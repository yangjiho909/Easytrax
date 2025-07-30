import os
import json
import logging
import fitz  # PyMuPDF
import cv2
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
import io
import base64

class PDFGenerator:
    """PDF 양식 생성기 - 원본 레이아웃 100% 복원"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 한글 폰트 설정
        self.korean_fonts = {
            'default': 'malgun.ttf',  # 맑은 고딕
            'bold': 'malgunbd.ttf',   # 맑은 고딕 볼드
            'serif': 'batang.ttc'     # 바탕체
        }
        
        # 폰트 경로 설정
        self.font_paths = {
            'windows': 'C:/Windows/Fonts/',
            'mac': '/System/Library/Fonts/',
            'linux': '/usr/share/fonts/'
        }
    
    def generate_filled_pdf(self, template_path: str, form_data: Dict[str, Any], 
                           user_input: Dict[str, Any]) -> str:
        """양식에 데이터를 채워서 PDF 생성"""
        self.logger.info(f"📄 PDF 생성 시작: {template_path}")
        
        try:
            # 원본 PDF 열기
            doc = fitz.open(template_path)
            
            # 각 페이지에 데이터 입력
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # 해당 페이지의 필드들 찾기
                page_fields = [field for field in form_data['fields'] if field['page'] == page_num + 1]
                
                # 필드별 데이터 입력
                for field in page_fields:
                    field_id = field['field_id']
                    field_value = user_input.get(field_id, '')
                    
                    if field_value:
                        self._fill_field(page, field, field_value)
            
            # 결과 PDF 저장
            output_path = self._save_filled_pdf(doc, template_path)
            doc.close()
            
            self.logger.info(f"✅ PDF 생성 완료: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"❌ PDF 생성 실패: {e}")
            raise
    
    def _fill_field(self, page, field: Dict[str, Any], value: Any):
        """개별 필드에 데이터 입력"""
        field_type = field['field_type']
        
        try:
            if field_type == 'text':
                self._fill_text_field(page, field, value)
            elif field_type == 'checkbox':
                self._fill_checkbox_field(page, field, value)
            elif field_type == 'table':
                self._fill_table_field(page, field, value)
            elif field_type == 'signature':
                self._fill_signature_field(page, field, value)
            
        except Exception as e:
            self.logger.warning(f"⚠️ 필드 입력 실패 ({field['label']}): {e}")
    
    def _fill_text_field(self, page, field: Dict[str, Any], value: str):
        """텍스트 필드 입력"""
        if not value or not value.strip():
            return
        
        # 필드 위치 정보 (실제 구현에서는 정확한 좌표 사용)
        bbox = field.get('bbox', [(100, 100), (300, 120)])
        x, y = bbox[0][0], bbox[0][1]
        
        # 폰트 정보
        font_info = field.get('font_info', {})
        font_name = font_info.get('font_name', 'default')
        font_size = font_info.get('font_size', 12)
        
        # 텍스트 삽입
        text_rect = fitz.Rect(x, y, x + 200, y + 20)
        
        # 기존 텍스트 지우기 (입력란 영역)
        page.draw_rect(text_rect, color=(1, 1, 1), fill=(1, 1, 1))
        
        # 새 텍스트 삽입
        page.insert_text(
            point=(x + 2, y + 15),
            text=str(value),
            fontsize=font_size,
            color=(0, 0, 0)
        )
    
    def _fill_checkbox_field(self, page, field: Dict[str, Any], value: str):
        """체크박스 필드 입력"""
        if value != 'checked':
            return
        
        bbox = field.get('bbox', [(100, 100), (120, 120)])
        x, y = bbox[0][0], bbox[0][1]
        
        # 체크박스 그리기
        checkbox_rect = fitz.Rect(x, y, x + 20, y + 20)
        
        # 체크 표시
        page.draw_line(
            p1=(x + 5, y + 10),
            p2=(x + 8, y + 15),
            color=(0, 0, 0),
            width=2
        )
        page.draw_line(
            p1=(x + 8, y + 15),
            p2=(x + 15, y + 5),
            color=(0, 0, 0),
            width=2
        )
    
    def _fill_table_field(self, page, field: Dict[str, Any], value: List[List[str]]):
        """테이블 필드 입력"""
        if not value or not isinstance(value, list):
            return
        
        table_structure = field.get('table_structure', [])
        bbox = field.get('bbox', [(100, 100), (500, 300)])
        
        # 테이블 그리기
        start_x, start_y = bbox[0][0], bbox[0][1]
        cell_width = 80
        cell_height = 25
        
        for row_idx, row_data in enumerate(value):
            for col_idx, cell_value in enumerate(row_data):
                if cell_value:
                    cell_x = start_x + (col_idx * cell_width)
                    cell_y = start_y + (row_idx * cell_height)
                    
                    # 셀에 텍스트 삽입
                    page.insert_text(
                        point=(cell_x + 5, cell_y + 15),
                        text=str(cell_value),
                        fontsize=10,
                        color=(0, 0, 0)
                    )
    
    def _fill_signature_field(self, page, field: Dict[str, Any], value: str):
        """서명 필드 입력"""
        if not value:
            return
        
        bbox = field.get('bbox', [(100, 100), (300, 150)])
        x, y = bbox[0][0], bbox[0][1]
        
        # 서명 텍스트 삽입
        signature_rect = fitz.Rect(x, y, x + 200, y + 50)
        
        # 기존 영역 지우기
        page.draw_rect(signature_rect, color=(1, 1, 1), fill=(1, 1, 1))
        
        # 서명 텍스트 삽입
        page.insert_text(
            point=(x + 5, y + 30),
            text=str(value),
            fontsize=14,
            color=(0, 0, 0)
        )
    
    def _save_filled_pdf(self, doc, template_path: str) -> str:
        """채워진 PDF 저장"""
        # 출력 디렉토리 생성
        output_dir = "generated_documents"
        os.makedirs(output_dir, exist_ok=True)
        
        # 파일명 생성
        template_name = os.path.splitext(os.path.basename(template_path))[0]
        timestamp = str(np.datetime64('now')).replace(':', '-').replace('.', '-')
        output_filename = f"{template_name}_filled_{timestamp}.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        # PDF 저장
        doc.save(output_path)
        
        return output_path
    
    def create_preview_image(self, pdf_path: str, page_num: int = 0) -> str:
        """PDF 미리보기 이미지 생성"""
        try:
            doc = fitz.open(pdf_path)
            page = doc[page_num]
            
            # 페이지를 이미지로 변환
            mat = fitz.Matrix(1.5, 1.5)  # 1.5배 확대
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            
            # Base64 인코딩
            img_base64 = base64.b64encode(img_data).decode('utf-8')
            
            doc.close()
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            self.logger.error(f"❌ 미리보기 생성 실패: {e}")
            return ""
    
    def validate_pdf_template(self, pdf_path: str) -> Dict[str, Any]:
        """PDF 템플릿 유효성 검사"""
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'info': {}
        }
        
        try:
            doc = fitz.open(pdf_path)
            
            validation_result['info'] = {
                'pages': len(doc),
                'file_size': os.path.getsize(pdf_path),
                'file_name': os.path.basename(pdf_path)
            }
            
            # 페이지별 검사
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # 텍스트 존재 여부 확인
                text = page.get_text()
                if not text.strip():
                    validation_result['warnings'].append(f"페이지 {page_num + 1}: 텍스트가 없습니다.")
                
                # 이미지 존재 여부 확인
                images = page.get_images()
                if not images:
                    validation_result['warnings'].append(f"페이지 {page_num + 1}: 이미지가 없습니다.")
            
            doc.close()
            
        except Exception as e:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"PDF 파일 열기 실패: {e}")
        
        return validation_result

# 전역 인스턴스
pdf_generator = PDFGenerator() 