import os
import json
import logging
import fitz  # PyMuPDF
import cv2
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from PIL import Image
import re

@dataclass
class FormField:
    """PDF 양식 필드 정보"""
    field_id: str
    field_type: str  # 'text', 'table', 'checkbox', 'signature', 'image'
    bbox: List[Tuple[float, float]]  # 좌표 (x1, y1, x2, y2)
    page: int
    label: str
    required: bool = False
    default_value: str = ""
    validation_rules: Dict[str, Any] = None
    font_info: Dict[str, Any] = None
    table_structure: List[List[str]] = None

@dataclass
class FormTemplate:
    """PDF 양식 템플릿 정보"""
    template_id: str
    template_name: str
    fields: List[FormField]
    pages: int
    metadata: Dict[str, Any]

class PDFFormAnalyzer:
    """PDF 양식 자동 분석기"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 입력란 패턴 정의
        self.input_patterns = {
            'text_field': [
                r'[가-힣\w\s]*[□_]{3,}',  # 언더라인 또는 박스
                r'[가-힣\w\s]*\s*\([^)]*\)',  # 괄호 안 설명
                r'[가-힣\w\s]*\s*:',  # 콜론 뒤 입력란
                r'[가-힣\w\s]*\s*입력',  # "입력" 키워드
            ],
            'checkbox': [
                r'□\s*[가-힣\w\s]+',  # 체크박스
                r'☐\s*[가-힣\w\s]+',  # 빈 체크박스
                r'☑\s*[가-힣\w\s]+',  # 체크된 박스
            ],
            'signature': [
                r'서명[가-힣\w\s]*',
                r'인[가-힣\w\s]*',
                r'날인[가-힣\w\s]*',
                r'직인[가-힣\w\s]*',
            ],
            'table': [
                r'표\s*\d+',
                r'[가-힣\w\s]*목록',
                r'[가-힣\w\s]*리스트',
            ]
        }
        
        # 필수 필드 키워드
        self.required_keywords = [
            '필수', '필요', '반드시', '꼭', 'required', 'mandatory',
            '기업명', '회사명', '상호', '업체명',
            '주소', '소재지', '사업장',
            '대표자', '대표', '사장',
            '연락처', '전화', '팩스', '이메일',
            '사업자등록번호', '법인번호',
            '제품명', '상품명', '품목',
            '수량', '단가', '금액', '총액',
            '제조일', '유통기한', '보관기한',
            '원산지', '제조국', '생산지'
        ]
    
    def analyze_pdf_form(self, pdf_path: str) -> FormTemplate:
        """PDF 양식 파일 분석"""
        self.logger.info(f"🔍 PDF 양식 분석 시작: {pdf_path}")
        
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF 파일을 찾을 수 없습니다: {pdf_path}")
        
        doc = None
        try:
            doc = fitz.open(pdf_path)
            template_id = os.path.splitext(os.path.basename(pdf_path))[0]
            template_name = template_id.replace('_', ' ').title()
            
            all_fields = []
            page_count = len(doc)
            
            for page_num in range(page_count):
                page = doc[page_num]
                
                # 1. 텍스트 기반 필드 분석
                text_fields = self._analyze_text_fields(page, page_num)
                all_fields.extend(text_fields)
                
                # 2. 이미지 기반 필드 분석 (OCR) - 선택적
                try:
                    image_fields = self._analyze_image_fields(page, page_num)
                    all_fields.extend(image_fields)
                except Exception as e:
                    self.logger.warning(f"⚠️ 이미지 필드 분석 실패 (페이지 {page_num + 1}): {e}")
                
                # 3. 표 구조 분석 - 선택적
                try:
                    table_fields = self._analyze_table_fields(page, page_num)
                    all_fields.extend(table_fields)
                except Exception as e:
                    self.logger.warning(f"⚠️ 표 분석 실패 (페이지 {page_num + 1}): {e}")
                
                # 4. 체크박스 분석
                checkbox_fields = self._analyze_checkbox_fields(page, page_num)
                all_fields.extend(checkbox_fields)
            
            # 필드 정리 및 중복 제거
            unique_fields = self._deduplicate_fields(all_fields)
            
            # 필수 필드 표시
            for field in unique_fields:
                field.required = self._is_required_field(field.label)
            
            template = FormTemplate(
                template_id=template_id,
                template_name=template_name,
                fields=unique_fields,
                pages=page_count,
                metadata={
                    'file_path': pdf_path,
                    'file_size': os.path.getsize(pdf_path),
                    'analysis_date': str(np.datetime64('now'))
                }
            )
            
            self.logger.info(f"✅ PDF 양식 분석 완료: {len(unique_fields)}개 필드 발견")
            return template
            
        except Exception as e:
            self.logger.error(f"❌ PDF 양식 분석 실패: {e}")
            raise
        finally:
            if doc:
                doc.close()
    
    def _analyze_text_fields(self, page, page_num: int) -> List[FormField]:
        """텍스트 기반 입력 필드 분석"""
        fields = []
        
        # 페이지 텍스트 추출
        text_dict = page.get_text("dict")
        
        for block in text_dict["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if not text:
                            continue
                        
                        # 입력란 패턴 매칭
                        field_type = self._detect_field_type(text)
                        if field_type:
                            bbox = [
                                (span["bbox"][0], span["bbox"][1]),
                                (span["bbox"][2], span["bbox"][3])
                            ]
                            
                            field = FormField(
                                field_id=f"field_{len(fields)}_{page_num}",
                                field_type=field_type,
                                bbox=bbox,
                                page=page_num + 1,
                                label=text,
                                font_info={
                                    'font_name': span.get('font', ''),
                                    'font_size': span.get('size', 12),
                                    'color': span.get('color', 0)
                                }
                            )
                            fields.append(field)
        
        return fields
    
    def _analyze_image_fields(self, page, page_num: int) -> List[FormField]:
        """이미지 기반 필드 분석 (OCR 사용)"""
        fields = []
        
        try:
            # 페이지를 이미지로 변환
            mat = fitz.Matrix(1.5, 1.5)  # 해상도 낮춤
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            
            # OpenCV로 이미지 로드
            nparr = np.frombuffer(img_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                self.logger.warning(f"⚠️ 이미지 로드 실패 (페이지 {page_num + 1})")
                return fields
            
            # 이미지 채널 수 확인 및 변환
            if len(image.shape) == 3 and image.shape[2] > 3:
                # 6채널 이미지인 경우 3채널로 변환
                image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
            
            # 고급 OCR 처리 시도
            try:
                from advanced_ocr_processor import advanced_ocr_processor
                ocr_result = advanced_ocr_processor.process_image_parallel(image, 'customs_document')
                
                # OCR 결과에서 입력란 감지
                for text_item in ocr_result.get('text', []):
                    text = text_item.get('text', '').strip()
                    if not text:
                        continue
                    
                    field_type = self._detect_field_type(text)
                    if field_type:
                        bbox = text_item.get('bbox', [])
                        if bbox:
                            field = FormField(
                                field_id=f"ocr_field_{len(fields)}_{page_num}",
                                field_type=field_type,
                                bbox=bbox,
                                page=page_num + 1,
                                label=text
                            )
                            fields.append(field)
                            
            except ImportError:
                self.logger.warning("⚠️ 고급 OCR 모듈 없음, 이미지 분석 건너뜀")
            except Exception as ocr_error:
                self.logger.warning(f"⚠️ OCR 처리 실패: {ocr_error}")
            
        except Exception as e:
            self.logger.warning(f"⚠️ 이미지 필드 분석 실패: {e}")
        
        return fields
    
    def _analyze_table_fields(self, page, page_num: int) -> List[FormField]:
        """표 구조 분석"""
        fields = []
        
        try:
            # PyMuPDF의 테이블 추출 기능 사용 (버전에 따라 다름)
            if hasattr(page, 'get_tables'):
                tables = page.get_tables()
                
                for table_idx, table in enumerate(tables):
                    # 표가 입력란인지 확인
                    if self._is_input_table(table):
                        bbox = self._get_table_bbox(table)
                        
                        field = FormField(
                            field_id=f"table_{table_idx}_{page_num}",
                            field_type='table',
                            bbox=bbox,
                            page=page_num + 1,
                            label=f"입력 표 {table_idx + 1}",
                            table_structure=table
                        )
                        fields.append(field)
            else:
                # 테이블 추출 기능이 없는 경우 텍스트에서 표 패턴 찾기
                text = page.get_text()
                table_patterns = [
                    r'표\s*\d+',
                    r'[가-힣\w\s]*목록',
                    r'[가-힣\w\s]*리스트',
                ]
                
                for pattern in table_patterns:
                    import re
                    matches = re.finditer(pattern, text)
                    for match in matches:
                        field = FormField(
                            field_id=f"table_text_{len(fields)}_{page_num}",
                            field_type='table',
                            bbox=[(0, 0), (100, 100)],  # 기본값
                            page=page_num + 1,
                            label=match.group(),
                            table_structure=[[]]
                        )
                        fields.append(field)
            
        except Exception as e:
            self.logger.warning(f"⚠️ 표 분석 실패: {e}")
        
        return fields
    
    def _analyze_checkbox_fields(self, page, page_num: int) -> List[FormField]:
        """체크박스 필드 분석"""
        fields = []
        
        try:
            # 체크박스 패턴 검색
            text_dict = page.get_text("dict")
            
            for block in text_dict["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"].strip()
                            
                            # 체크박스 패턴 매칭
                            if any(re.search(pattern, text) for pattern in self.input_patterns['checkbox']):
                                bbox = [
                                    (span["bbox"][0], span["bbox"][1]),
                                    (span["bbox"][2], span["bbox"][3])
                                ]
                                
                                field = FormField(
                                    field_id=f"checkbox_{len(fields)}_{page_num}",
                                    field_type='checkbox',
                                    bbox=bbox,
                                    page=page_num + 1,
                                    label=text,
                                    default_value="unchecked"
                                )
                                fields.append(field)
            
        except Exception as e:
            self.logger.warning(f"⚠️ 체크박스 분석 실패: {e}")
        
        return fields
    
    def _detect_field_type(self, text: str) -> Optional[str]:
        """텍스트에서 필드 유형 감지"""
        text_lower = text.lower()
        
        # 체크박스
        if any(re.search(pattern, text) for pattern in self.input_patterns['checkbox']):
            return 'checkbox'
        
        # 서명 필드
        if any(re.search(pattern, text) for pattern in self.input_patterns['signature']):
            return 'signature'
        
        # 표
        if any(re.search(pattern, text) for pattern in self.input_patterns['table']):
            return 'table'
        
        # 텍스트 입력란
        if any(re.search(pattern, text) for pattern in self.input_patterns['text_field']):
            return 'text'
        
        return None
    
    def _is_input_table(self, table: List[List[str]]) -> bool:
        """표가 입력란인지 확인"""
        if not table or len(table) < 2:
            return False
        
        # 빈 셀이 많은지 확인
        empty_cells = 0
        total_cells = 0
        
        for row in table:
            for cell in row:
                total_cells += 1
                if not cell or cell.strip() == '':
                    empty_cells += 1
        
        # 30% 이상이 빈 셀이면 입력 표로 간주
        return empty_cells / total_cells > 0.3
    
    def _get_table_bbox(self, table: List[List[str]]) -> List[Tuple[float, float]]:
        """표의 경계 상자 계산"""
        # 실제 구현에서는 표의 실제 좌표를 계산해야 함
        # 여기서는 기본값 반환
        return [(0, 0), (100, 100)]
    
    def _is_required_field(self, label: str) -> bool:
        """필수 필드인지 확인"""
        label_lower = label.lower()
        
        # 필수 키워드 포함 여부 확인
        for keyword in self.required_keywords:
            if keyword in label_lower:
                return True
        
        return False
    
    def _deduplicate_fields(self, fields: List[FormField]) -> List[FormField]:
        """중복 필드 제거"""
        unique_fields = []
        seen_labels = set()
        
        for field in fields:
            # 레이블 정규화
            normalized_label = re.sub(r'\s+', ' ', field.label.strip())
            
            if normalized_label not in seen_labels:
                seen_labels.add(normalized_label)
                unique_fields.append(field)
        
        return unique_fields
    
    def generate_input_form(self, template: FormTemplate) -> Dict[str, Any]:
        """입력폼 생성"""
        form_data = {
            'template_id': template.template_id,
            'template_name': template.template_name,
            'pages': template.pages,
            'fields': []
        }
        
        for field in template.fields:
            field_data = {
                'field_id': field.field_id,
                'field_type': field.field_type,
                'label': field.label,
                'required': field.required,
                'default_value': field.default_value,
                'page': field.page,
                'validation_rules': field.validation_rules or {}
            }
            
            # 필드 유형별 추가 설정
            if field.field_type == 'text':
                field_data.update({
                    'input_type': 'text',
                    'placeholder': f'{field.label}을(를) 입력하세요',
                    'max_length': 100
                })
            elif field.field_type == 'checkbox':
                field_data.update({
                    'input_type': 'checkbox',
                    'options': ['checked', 'unchecked']
                })
            elif field.field_type == 'table':
                field_data.update({
                    'input_type': 'table',
                    'table_structure': field.table_structure
                })
            elif field.field_type == 'signature':
                field_data.update({
                    'input_type': 'signature',
                    'placeholder': '서명을 입력하세요'
                })
            
            form_data['fields'].append(field_data)
        
        return form_data
    
    def validate_form_data(self, form_data: Dict[str, Any], user_input: Dict[str, Any]) -> Dict[str, Any]:
        """입력 데이터 검증"""
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'missing_fields': []
        }
        
        for field in form_data['fields']:
            field_id = field['field_id']
            field_value = user_input.get(field_id, '')
            
            # 필수 필드 검증
            if field['required'] and not field_value:
                validation_result['missing_fields'].append({
                    'field_id': field_id,
                    'label': field['label'],
                    'message': f"{field['label']}은(는) 필수 입력 항목입니다."
                })
                validation_result['is_valid'] = False
            
            # 필드 유형별 검증
            if field_value:
                field_errors = self._validate_field_value(field, field_value)
                validation_result['errors'].extend(field_errors)
                
                if field_errors:
                    validation_result['is_valid'] = False
        
        return validation_result
    
    def _validate_field_value(self, field: Dict[str, Any], value: Any) -> List[str]:
        """개별 필드 값 검증"""
        errors = []
        
        if field['field_type'] == 'text':
            if len(str(value)) > field.get('max_length', 100):
                errors.append(f"{field['label']}은(는) {field.get('max_length', 100)}자 이하여야 합니다.")
        
        elif field['field_type'] == 'checkbox':
            if value not in ['checked', 'unchecked']:
                errors.append(f"{field['label']}은(는) 체크 또는 미체크 상태여야 합니다.")
        
        return errors

# 전역 인스턴스
pdf_form_analyzer = PDFFormAnalyzer() 