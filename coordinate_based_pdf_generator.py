#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📄 좌표 기반 PDF 서류 생성기
- 사용자가 제공한 좌표에 따라 정확한 위치에 텍스트 배치
- 템플릿 PDF에 데이터를 정확한 좌표에 삽입
- 다양한 서류 유형 지원 (상업송장, 포장명세서 등)
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import fitz  # PyMuPDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class CoordinateBasedPDFGenerator:
    """좌표 기반 PDF 서류 생성기"""
    
    def __init__(self):
        self.coordinate_templates = self._load_coordinate_templates()
        self._register_fonts()
        
    def _register_fonts(self):
        """한글 폰트 등록"""
        try:
            # 한글 폰트 경로들
            korean_fonts = [
                "C:/Windows/Fonts/malgun.ttf",      # 맑은 고딕
                "C:/Windows/Fonts/gulim.ttc",       # 굴림
                "/System/Library/Fonts/AppleGothic.ttf",  # macOS
                "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"  # Linux
            ]
            
            for font_path in korean_fonts:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('KoreanFont', font_path))
                    print(f"✅ 한글 폰트 등록 성공: {font_path}")
                    break
            else:
                print("⚠️ 한글 폰트를 찾을 수 없습니다. 기본 폰트 사용")
        except Exception as e:
            print(f"⚠️ 폰트 등록 실패: {e}")
    
    def _load_coordinate_templates(self) -> Dict[str, Dict]:
        """좌표 템플릿 로드"""
        # 현재 작업 디렉토리 확인
        current_dir = os.getcwd()
        print(f"📁 현재 작업 디렉토리: {current_dir}")
        
        # 템플릿 파일 경로 확인
        commercial_template = "uploaded_templates/상업송장 빈 템플릿.pdf"
        packing_template = "uploaded_templates/포장명세서 빈 템플릿.pdf"
        
        # 절대 경로로 변환
        commercial_template_abs = os.path.abspath(commercial_template)
        packing_template_abs = os.path.abspath(packing_template)
        
        print(f"📄 상업송장 템플릿 경로: {commercial_template_abs}")
        print(f"📄 포장명세서 템플릿 경로: {packing_template_abs}")
        print(f"📄 상업송장 템플릿 존재: {os.path.exists(commercial_template_abs)}")
        print(f"📄 포장명세서 템플릿 존재: {os.path.exists(packing_template_abs)}")
        
        templates = {
            "상업송장": {
                "template_file": commercial_template_abs if os.path.exists(commercial_template_abs) else commercial_template,
                "coordinates": {}  # 사용자 정의 좌표 파일 사용
            },
            "포장명세서": {
                "template_file": packing_template_abs if os.path.exists(packing_template_abs) else packing_template,
                "coordinates": {}  # 사용자 정의 좌표 파일 사용
            }
        }
        return templates
    
    def load_custom_coordinates(self, coordinate_file: str) -> Dict[str, Dict]:
        """사용자 정의 좌표 파일 로드"""
        try:
            # 절대 경로로 변환 시도
            if not os.path.isabs(coordinate_file):
                coordinate_file_abs = os.path.abspath(coordinate_file)
                print(f"📁 좌표 파일 절대 경로: {coordinate_file_abs}")
                print(f"📁 좌표 파일 존재: {os.path.exists(coordinate_file_abs)}")
                
                if os.path.exists(coordinate_file_abs):
                    coordinate_file = coordinate_file_abs
                else:
                    print(f"⚠️ 절대 경로에서 파일을 찾을 수 없음, 상대 경로 시도")
            
            with open(coordinate_file, 'r', encoding='utf-8') as f:
                coordinates = json.load(f)
            print(f"✅ 사용자 정의 좌표 로드 성공: {coordinate_file}")
            return coordinates
        except Exception as e:
            print(f"❌ 사용자 정의 좌표 로드 실패: {e}")
            print(f"📁 시도한 파일 경로: {coordinate_file}")
            print(f"📁 현재 디렉토리: {os.getcwd()}")
            return {}
    
    def generate_pdf_with_coordinates(self, doc_type: str, data: Dict, 
                                    coordinate_file: str = None, 
                                    output_path: str = None) -> str:
        """좌표 기반 PDF 생성"""
        
        print(f"📄 좌표 기반 PDF 생성 시작: {doc_type}")
        print(f"📋 받은 데이터: {data}")
        print(f"📁 좌표 파일: {coordinate_file}")
        
        # 좌표 정보 로드
        if coordinate_file and os.path.exists(coordinate_file):
            coordinates = self.load_custom_coordinates(coordinate_file)
            print(f"✅ 사용자 정의 좌표 로드됨: {len(coordinates)}개 필드")
        else:
            coordinates = self.coordinate_templates.get(doc_type, {}).get("coordinates", {})
            print(f"⚠️ 기본 좌표 사용: {len(coordinates)}개 필드")
        
        if not coordinates:
            raise ValueError(f"좌표 정보를 찾을 수 없습니다: {doc_type}")
        
        # 데이터와 좌표 매칭 확인
        print(f"🔍 데이터-좌표 매칭 확인:")
        for field_name in coordinates.keys():
            if field_name in data:
                print(f"  ✅ {field_name}: {data[field_name]}")
            else:
                print(f"  ❌ {field_name}: 데이터 없음")
        
        # 출력 경로 설정
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = doc_type.replace("/", "_").replace(" ", "_")
            output_path = f"generated_documents/{safe_name}_{timestamp}.pdf"
        
        # 디렉토리 생성
        output_dir = os.path.dirname(output_path)
        try:
            os.makedirs(output_dir, exist_ok=True)
            print(f"✅ 출력 디렉토리 생성/확인: {output_dir}")
        except Exception as e:
            print(f"❌ 출력 디렉토리 생성 실패: {e}")
            # 현재 디렉토리에 생성
            output_path = os.path.basename(output_path)
            print(f"⚠️ 현재 디렉토리에 생성: {output_path}")
        
        # 템플릿 파일 경로
        template_file = self.coordinate_templates.get(doc_type, {}).get("template_file")
        
        print(f"🔍 템플릿 파일 확인: {template_file}")
        print(f"📁 템플릿 파일 존재: {os.path.exists(template_file) if template_file else False}")
        
        if template_file and os.path.exists(template_file):
            # 기존 템플릿에 데이터 추가
            print(f"✅ 기존 템플릿에 데이터 추가: {template_file}")
            self._fill_template_pdf(template_file, data, coordinates, output_path)
        else:
            # 새 PDF 생성
            print(f"⚠️ 새 PDF 생성 (템플릿 파일 없음)")
            self._create_new_pdf(data, coordinates, output_path)
        
        print(f"✅ 좌표 기반 PDF 생성 완료: {output_path}")
        return output_path
    
    def _fill_template_pdf(self, template_path: str, data: Dict, 
                          coordinates: Dict, output_path: str):
        """기존 템플릿 PDF에 데이터 채우기"""
        
        try:
            # 템플릿 PDF 열기
            doc = fitz.open(template_path)
            page = doc[0]  # 첫 번째 페이지
            
            # 데이터를 좌표에 맞춰 삽입
            for field_name, field_data in coordinates.items():
                if field_name in data and data[field_name]:
                    x = field_data["x"]
                    y = field_data["y"]
                    font_size = field_data.get("font_size", 9)
                    text = str(data[field_name])
                    
                    print(f"📝 텍스트 삽입: {field_name} = '{text}' at ({x}, {y})")
                    
                    # vessel_flight 필드 특별 처리 - 8글자씩 3행으로 구성
                    if field_name == "vessel_flight":
                        # 폰트 크기를 5로 설정
                        font_size = 5
                        # 텍스트를 8글자씩 3행으로 분할
                        lines = self._split_text_into_lines(text, 8, 3)
                        line_height = font_size * 1.2  # 줄 간격
                        
                        print(f"  📄 vessel_flight 분할: {lines}")
                        
                        for i, line in enumerate(lines):
                            current_y = y - (i * line_height)
                            page.insert_text(
                                point=(x, current_y),
                                text=line,
                                fontsize=font_size,
                                fontname="helv"
                            )
                    else:
                        # 일반 텍스트 삽입 - 한글 폰트 사용
                        try:
                            page.insert_text(
                                point=(x, y),
                                text=text,
                                fontsize=font_size,
                                fontname="KoreanFont"  # 한글 폰트 사용
                            )
                        except:
                            # 한글 폰트 실패 시 기본 폰트 사용
                            page.insert_text(
                                point=(x, y),
                                text=text,
                                fontsize=font_size,
                                fontname="helv"
                            )
                else:
                    print(f"⚠️ 데이터 없음: {field_name}")
            
            # 결과 저장
            doc.save(output_path)
            doc.close()
            
        except Exception as e:
            print(f"❌ 템플릿 PDF 채우기 실패: {e}")
            # 폴백: 새 PDF 생성
            self._create_new_pdf(data, coordinates, output_path)
    
    def _split_text_into_lines(self, text: str, chars_per_line: int, max_lines: int) -> List[str]:
        """텍스트를 지정된 글자 수와 최대 행 수로 분할"""
        if len(text) <= chars_per_line:
            return [text]
        
        lines = []
        remaining_text = text
        
        for i in range(max_lines):
            if len(remaining_text) <= chars_per_line:
                lines.append(remaining_text)
                break
            else:
                # 8글자씩 자르기
                line = remaining_text[:chars_per_line]
                lines.append(line)
                remaining_text = remaining_text[chars_per_line:]
        
        # 남은 텍스트가 있으면 마지막 줄에 추가 (8글자 초과해도)
        if remaining_text and len(lines) < max_lines:
            lines.append(remaining_text)
        
        return lines
    
    def _create_new_pdf(self, data: Dict, coordinates: Dict, output_path: str):
        """새 PDF 생성"""
        try:
            c = canvas.Canvas(output_path, pagesize=A4)
            
            # 데이터를 좌표에 맞춰 삽입
            for field_name, field_data in coordinates.items():
                if field_name in data and data[field_name]:
                    x = field_data["x"]
                    y = field_data["y"]
                    font_size = field_data.get("font_size", 12)
                    text = str(data[field_name])
                    
                    # 폰트 설정 - 한글 폰트 우선 사용
                    try:
                        if font_size > 14:
                            c.setFont("KoreanFont", font_size)
                        else:
                            c.setFont("KoreanFont", font_size)
                    except:
                        # 한글 폰트 실패 시 기본 폰트 사용
                        if font_size > 14:
                            c.setFont("Helvetica-Bold", font_size)
                        else:
                            c.setFont("Helvetica", font_size)
                    
                    # 텍스트 삽입
                    c.drawString(x, y, text)
            
            c.save()
            
        except Exception as e:
            print(f"❌ 새 PDF 생성 실패: {e}")
            raise
    
    def update_coordinates(self, doc_type: str, field_name: str, 
                          x: float, y: float, font_size: int = 12):
        """좌표 업데이트"""
        if doc_type in self.coordinate_templates:
            self.coordinate_templates[doc_type]["coordinates"][field_name] = {
                "x": x, "y": y, "font_size": font_size
            }
    
    def save_coordinates(self, doc_type: str, output_file: str):
        """좌표를 JSON 파일로 저장"""
        if doc_type in self.coordinate_templates:
            coordinates = self.coordinate_templates[doc_type]["coordinates"]
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(coordinates, f, ensure_ascii=False, indent=2)
    
    def get_available_fields(self, doc_type: str) -> List[str]:
        """사용 가능한 필드 목록 반환"""
        if doc_type in self.coordinate_templates:
            return list(self.coordinate_templates[doc_type]["coordinates"].keys())
        return []
    
    def preview_coordinates(self, doc_type: str) -> Dict:
        """좌표 미리보기"""
        if doc_type in self.coordinate_templates:
            return self.coordinate_templates[doc_type]["coordinates"]
        return {}

def main():
    """테스트 함수"""
    generator = CoordinateBasedPDFGenerator()
    
    # 테스트 데이터
    test_data = {
        "seller_name": "Korea Food Industry Co., Ltd.",
        "buyer_name": "China Food Trading Co., Ltd.",
        "invoice_number": "INV-20240115-001",
        "product_name": "Shin Ramyun",
        "quantity": "1000 boxes",
        "unit_price": "5.00 USD",
        "total_amount": "5000.00 USD"
    }
    
    # PDF 생성
    output_path = generator.generate_pdf_with_coordinates(
        "상업송장", 
        test_data, 
        coordinate_file="uploaded_templates/상품송장 좌표 반영.json"
    )
    
    print(f"✅ PDF 생성 완료: {output_path}")

if __name__ == "__main__":
    main() 