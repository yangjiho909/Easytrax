#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌐 KATI 서류 생성 API - 배포 환경용 (PDF 생성 포함)
- 좌표 매핑된 PDF 템플릿 활용
- 배포 환경에서 안정적으로 작동
- 오류 발생 시 폴백 기능 제공
"""

from flask import Flask, request, jsonify, send_file
from datetime import datetime
import os
import json
import traceback
import tempfile
import shutil
import platform

app = Flask(__name__)

# PyMuPDF 임포트 시도 (배포 환경에서 안정성 확보)
try:
    import fitz  # PyMuPDF
    PDF_AVAILABLE = True
    print("✅ PyMuPDF 로드 성공")
except ImportError as e:
    PDF_AVAILABLE = False
    print(f"⚠️ PyMuPDF 로드 실패: {e}")
    print("📝 텍스트 형태로만 서류 생성")

# 배포 환경에서 안정적인 파일 저장을 위한 설정
def ensure_generated_documents_dir():
    """generated_documents 폴더가 존재하는지 확인하고 없으면 생성"""
    try:
        # 현재 작업 디렉토리 기준으로 폴더 생성 시도
        current_dir = os.getcwd()
        print(f"📁 현재 작업 디렉토리: {current_dir}")
        print(f"📁 현재 디렉토리 존재: {os.path.exists(current_dir)}")
        print(f"📁 현재 디렉토리 쓰기 권한: {os.access(current_dir, os.W_OK)}")
        
        # 환경 변수 확인
        print(f"🌍 환경 변수 확인:")
        print(f"  - PORT: {os.environ.get('PORT', 'Not set')}")
        print(f"  - PWD: {os.environ.get('PWD', 'Not set')}")
        print(f"  - HOME: {os.environ.get('HOME', 'Not set')}")
        print(f"  - USER: {os.environ.get('USER', 'Not set')}")
        
        docs_dir = os.path.join(current_dir, "generated_documents")
        print(f"📁 생성 시도할 폴더: {docs_dir}")
        
        # 폴더 생성
        os.makedirs(docs_dir, exist_ok=True)
        
        # 폴더 권한 확인
        if os.access(docs_dir, os.W_OK):
            print(f"✅ generated_documents 폴더 생성/확인 완료: {docs_dir}")
            print(f"📋 폴더 쓰기 권한: OK")
            
            # 폴더 내용 확인
            try:
                files = os.listdir(docs_dir)
                print(f"📋 폴더 내 파일 수: {len(files)}")
            except Exception as e:
                print(f"⚠️ 폴더 내용 읽기 실패: {e}")
            
            return docs_dir
        else:
            print(f"⚠️ 폴더 쓰기 권한 없음: {docs_dir}")
            raise PermissionError(f"폴더 쓰기 권한 없음: {docs_dir}")
            
    except Exception as e:
        print(f"⚠️ 기본 폴더 생성 실패: {e}")
        print(f"📋 상세 오류: {traceback.format_exc()}")
        try:
            # 임시 디렉토리 사용
            temp_dir = tempfile.gettempdir()
            print(f"📁 시스템 임시 디렉토리: {temp_dir}")
            print(f"📁 임시 디렉토리 존재: {os.path.exists(temp_dir)}")
            print(f"📁 임시 디렉토리 쓰기 권한: {os.access(temp_dir, os.W_OK)}")
            
            docs_dir = os.path.join(temp_dir, "kati_generated_documents")
            print(f"📁 임시 폴더 경로: {docs_dir}")
            
            os.makedirs(docs_dir, exist_ok=True)
            
            if os.access(docs_dir, os.W_OK):
                print(f"✅ 임시 폴더 사용: {docs_dir}")
                print(f"📋 임시 폴더 쓰기 권한: OK")
                return docs_dir
            else:
                print(f"⚠️ 임시 폴더 쓰기 권한 없음: {docs_dir}")
                raise PermissionError(f"임시 폴더 쓰기 권한 없음: {docs_dir}")
                
        except Exception as e2:
            print(f"❌ 임시 폴더도 생성 실패: {e2}")
            print(f"📋 상세 오류: {traceback.format_exc()}")
            # 마지막 수단: 현재 디렉토리 사용
            docs_dir = "generated_documents"
            print(f"⚠️ 현재 디렉토리 사용: {docs_dir}")
            return docs_dir

# 전역 변수로 폴더 경로 저장
GENERATED_DOCS_DIR = ensure_generated_documents_dir()
print(f"🎯 최종 사용 폴더: {GENERATED_DOCS_DIR}")

class SimpleDocumentGenerator:
    """간단한 서류 생성기 (PDF 포함)"""
    
    def __init__(self):
        print("✅ SimpleDocumentGenerator 초기화 완료")
        
        # 절대 경로로 템플릿 파일 설정
        current_dir = os.getcwd()
        print(f"📁 현재 디렉토리: {current_dir}")
        
        self.template_files = {
            "commercial_invoice": {  # 영문으로 변경
                "pdf": os.path.join(current_dir, "uploaded_templates", "상업송장 빈 템플릿.pdf"),
                "coordinates": os.path.join(current_dir, "uploaded_templates", "상업송장 좌표 반영.json")
            },
            "packing_list": {  # 영문으로 변경
                "pdf": os.path.join(current_dir, "uploaded_templates", "포장명세서 빈 템플릿.pdf"), 
                "coordinates": os.path.join(current_dir, "uploaded_templates", "포장명세서 좌표 반영.json")
            }
        }
        
        # 템플릿 파일 존재 확인
        self._check_template_files()
    
    def _check_template_files(self):
        """템플릿 파일 존재 확인"""
        print("🔍 템플릿 파일 확인 중...")
        for doc_type, files in self.template_files.items():
            pdf_exists = os.path.exists(files["pdf"])
            coord_exists = os.path.exists(files["coordinates"])
            print(f"📄 {doc_type}: PDF={pdf_exists} ({files['pdf']}), 좌표={coord_exists} ({files['coordinates']})")
            
            if not pdf_exists or not coord_exists:
                print(f"⚠️ {doc_type} 템플릿 파일 누락")
    
    def generate_document(self, doc_type, country, product, company_info, **kwargs):
        """문서 생성 메인 함수"""
        try:
            # 한글 문서 타입을 영문으로 매핑
            doc_type_mapping = {
                "상업송장": "commercial_invoice",
                "포장명세서": "packing_list"
            }
            
            english_doc_type = doc_type_mapping.get(doc_type, doc_type)
            print(f"📋 문서 타입 변환: {doc_type} -> {english_doc_type}")
            
            if english_doc_type == "commercial_invoice":
                return self._generate_commercial_invoice(country, product, company_info, **kwargs)
            elif english_doc_type == "packing_list":
                return self._generate_packing_list(country, product, company_info, **kwargs)
            else:
                return f"지원하지 않는 문서 유형: {doc_type}"
        except Exception as e:
            print(f"❌ 문서 생성 오류: {str(e)}")
            return f"문서 생성 중 오류가 발생했습니다: {str(e)}"
    
    def generate_pdf_with_coordinates(self, doc_type, data, output_path):
        """좌표 기반 PDF 생성 (폴백 기능 포함)"""
        print(f"🚀 PDF 생성 시작: {doc_type}")
        print(f"📁 출력 경로: {output_path}")
        print(f"📁 절대 출력 경로: {os.path.abspath(output_path)}")
        print(f"📋 데이터 키: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
        
        # 파일 시스템 상태 확인
        output_dir = os.path.dirname(output_path)
        print(f"📁 출력 디렉토리: {output_dir}")
        print(f"📁 출력 디렉토리 존재: {os.path.exists(output_dir)}")
        print(f"📁 출력 디렉토리 쓰기 권한: {os.access(output_dir, os.W_OK) if os.path.exists(output_dir) else 'N/A'}")
        
        if not PDF_AVAILABLE:
            print("❌ PDF 생성 불가: PyMuPDF 없음")
            return self._generate_text_fallback(doc_type, data, output_path)
        
        try:
            # 한글 문서 타입을 영문으로 매핑
            doc_type_mapping = {
                "상업송장": "commercial_invoice",
                "포장명세서": "packing_list"
            }
            english_doc_type = doc_type_mapping.get(doc_type, doc_type)
            
            print(f"📄 PDF 생성 시작: {doc_type} -> {english_doc_type}")
            print(f"📁 출력 경로: {output_path}")
            
            # 템플릿 파일 경로 확인
            template_info = self.template_files.get(english_doc_type)
            if not template_info:
                print(f"❌ 템플릿 정보를 찾을 수 없습니다: {english_doc_type}")
                print(f"📋 사용 가능한 템플릿: {list(self.template_files.keys())}")
                return self._generate_text_fallback(doc_type, data, output_path)
            
            pdf_template = template_info["pdf"]
            coord_file = template_info["coordinates"]
            
            print(f"📁 PDF 템플릿: {pdf_template}")
            print(f"📁 PDF 템플릿 존재: {os.path.exists(pdf_template)}")
            print(f"📁 PDF 템플릿 읽기 권한: {os.access(pdf_template, os.R_OK) if os.path.exists(pdf_template) else 'N/A'}")
            print(f"📁 좌표 파일: {coord_file}")
            print(f"📁 좌표 파일 존재: {os.path.exists(coord_file)}")
            print(f"📁 좌표 파일 읽기 권한: {os.access(coord_file, os.R_OK) if os.path.exists(coord_file) else 'N/A'}")
            
            # 파일 존재 확인
            if not os.path.exists(pdf_template):
                print(f"⚠️ PDF 템플릿 파일이 없습니다: {pdf_template}")
                return self._generate_text_fallback(doc_type, data, output_path)
            if not os.path.exists(coord_file):
                print(f"⚠️ 좌표 파일이 없습니다: {coord_file}")
                return self._generate_text_fallback(doc_type, data, output_path)
            
            # 좌표 정보 로드
            print(f"📖 좌표 파일 읽기 시작: {coord_file}")
            try:
                with open(coord_file, 'r', encoding='utf-8') as f:
                    coordinates = json.load(f)
                print(f"✅ 좌표 정보 로드됨: {len(coordinates)}개 필드")
            except Exception as e:
                print(f"❌ 좌표 파일 읽기 실패: {e}")
                return self._generate_text_fallback(doc_type, data, output_path)
            
            # PDF 템플릿 열기
            print(f"📄 PDF 템플릿 열기: {pdf_template}")
            try:
                doc = fitz.open(pdf_template)
                page = doc[0]  # 첫 번째 페이지
                print(f"✅ PDF 템플릿 열기 성공")
            except Exception as e:
                print(f"❌ PDF 템플릿 열기 실패: {e}")
                return self._generate_text_fallback(doc_type, data, output_path)
            
            # 데이터를 좌표에 맞춰 삽입
            inserted_count = 0
            for field_name, field_data in coordinates.items():
                if field_name in data and data[field_name]:
                    x = field_data["x"]
                    y = field_data["y"]
                    font_size = field_data.get("font_size", 9)
                    text = str(data[field_name])
                    
                    print(f"📝 텍스트 삽입: {field_name} = '{text}' at ({x}, {y})")
                    
                    try:
                        # vessel_flight 필드 특별 처리
                        if field_name == "vessel_flight":
                            font_size = 5
                            # 텍스트를 8글자씩 3행으로 분할
                            lines = self._split_text_into_lines(text, 8, 3)
                            line_height = font_size * 1.2
                            
                            for i, line in enumerate(lines):
                                current_y = y - (i * line_height)
                                page.insert_text(
                                    point=(x, current_y),
                                    text=line,
                                    fontsize=font_size,
                                    fontname="helv"
                                )
                        else:
                            # 일반 필드 처리
                            page.insert_text(
                                point=(x, y),
                                text=text,
                                fontsize=font_size,
                                fontname="helv"
                            )
                        inserted_count += 1
                    except Exception as e:
                        print(f"⚠️ 텍스트 삽입 실패 ({field_name}): {e}")
            
            print(f"✅ 텍스트 삽입 완료: {inserted_count}개 필드")
            
            # 출력 디렉토리 생성 (전역 변수 사용)
            output_dir = os.path.dirname(output_path)
            print(f"📁 출력 디렉토리 생성 시도: {output_dir}")
            try:
                os.makedirs(output_dir, exist_ok=True)
                print(f"✅ 출력 디렉토리 확인: {output_dir}")
            except Exception as e:
                print(f"❌ 출력 디렉토리 생성 실패: {e}")
                return self._generate_text_fallback(doc_type, data, output_path)
            
            # 디렉토리 쓰기 권한 확인
            if not os.access(output_dir, os.W_OK):
                print(f"❌ 출력 디렉토리 쓰기 권한 없음: {output_dir}")
                return self._generate_text_fallback(doc_type, data, output_path)
            
            # PDF 저장
            print(f"💾 PDF 저장 시작: {output_path}")
            try:
                doc.save(output_path)
                doc.close()
                print(f"✅ PDF 저장 완료")
            except Exception as e:
                print(f"❌ PDF 저장 실패: {e}")
                return self._generate_text_fallback(doc_type, data, output_path)
            
            # 파일 생성 확인
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                print(f"✅ PDF 생성 완료: {output_path}")
                print(f"📄 파일 크기: {file_size} bytes")
                
                # 파일 읽기 권한 확인
                if os.access(output_path, os.R_OK):
                    print(f"✅ 파일 읽기 권한: OK")
                    return output_path
                else:
                    print(f"❌ 파일 읽기 권한 없음: {output_path}")
                    return self._generate_text_fallback(doc_type, data, output_path)
            else:
                print(f"❌ PDF 파일이 생성되지 않음: {output_path}")
                return self._generate_text_fallback(doc_type, data, output_path)
            
        except Exception as e:
            print(f"❌ PDF 생성 오류: {str(e)}")
            print(f"📋 상세 오류: {traceback.format_exc()}")
            print("🔄 텍스트 폴백으로 전환")
            return self._generate_text_fallback(doc_type, data, output_path)
    
    def _generate_text_fallback(self, doc_type, data, output_path):
        """PDF 생성 실패 시 텍스트 파일로 폴백"""
        try:
            # 텍스트 파일로 저장
            text_path = output_path.replace('.pdf', '.txt')
            print(f"📝 텍스트 폴백 시작: {text_path}")
            
            lines = []
            lines.append(f"=== {doc_type} ===")
            lines.append(f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append("")
            
            for field_name, value in data.items():
                if value:
                    lines.append(f"{field_name}: {value}")
            
            lines.append("")
            lines.append("KATI 수출 지원 시스템에서 생성된 서류입니다.")
            
            # 출력 디렉토리 생성
            output_dir = os.path.dirname(text_path)
            print(f"📁 텍스트 파일 출력 디렉토리: {output_dir}")
            os.makedirs(output_dir, exist_ok=True)
            
            # 디렉토리 쓰기 권한 확인
            if not os.access(output_dir, os.W_OK):
                print(f"❌ 텍스트 파일 디렉토리 쓰기 권한 없음: {output_dir}")
                return None
            
            # 텍스트 파일 저장
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            # 파일 생성 확인
            if os.path.exists(text_path):
                file_size = os.path.getsize(text_path)
                print(f"✅ 텍스트 파일 생성 완료: {text_path}")
                print(f"📄 텍스트 파일 크기: {file_size} bytes")
                
                # 파일 읽기 권한 확인
                if os.access(text_path, os.R_OK):
                    print(f"✅ 텍스트 파일 읽기 권한: OK")
                    return text_path
                else:
                    print(f"❌ 텍스트 파일 읽기 권한 없음: {text_path}")
                    return None
            else:
                print(f"❌ 텍스트 파일이 생성되지 않음: {text_path}")
                return None
            
        except Exception as e:
            print(f"❌ 텍스트 폴백도 실패: {str(e)}")
            print(f"📋 상세 오류: {traceback.format_exc()}")
            return None
    
    def _split_text_into_lines(self, text, chars_per_line, max_lines):
        """텍스트를 여러 줄로 분할"""
        lines = []
        for i in range(0, len(text), chars_per_line):
            if len(lines) >= max_lines:
                break
            lines.append(text[i:i+chars_per_line])
        return lines
    
    def _generate_commercial_invoice(self, country, product, company_info, **kwargs):
        """상업송장 생성"""
        try:
            # 데이터 추출
            product_info = kwargs.get('product_info', {})
            buyer_info = kwargs.get('buyer_info', {})
            transport_info = kwargs.get('transport_info', {})
            payment_info = kwargs.get('payment_info', {})
            
            # 안전한 문자열 변환
            def safe_str(value):
                if value is None:
                    return 'N/A'
                try:
                    return str(value)
                except:
                    return 'N/A'
            
            # 총액 계산
            quantity = float(product_info.get('quantity', 0))
            unit_price = float(product_info.get('unit_price', 0))
            total_amount = quantity * unit_price
            
            # PDF 데이터 준비 (좌표 파일의 필드명과 일치)
            pdf_data = {
                "shipper_seller": company_info.get("name", ""),
                "invoice_no_date": f"INV-{datetime.now().strftime('%Y%m%d')}-001 / {datetime.now().strftime('%Y-%m-%d')}",
                "lc_no_date": f"{payment_info.get('lc_number', '')} / {payment_info.get('lc_date', '')}",
                "buyer": buyer_info.get("name", ""),
                "other_references": payment_info.get("reference", ""),
                "departure_date": transport_info.get("departure_date", ""),
                "vessel_flight": transport_info.get("vessel_flight", ""),
                "from_location": transport_info.get("from_location", ""),
                "to_location": transport_info.get("to_location", ""),
                "terms_delivery_payment": f"{transport_info.get('delivery_terms', '')} / {payment_info.get('payment_terms', '')}",
                "shipping_marks": kwargs.get('packing_details', {}).get("shipping_marks", ""),
                "package_count_type": f"{kwargs.get('packing_details', {}).get('package_count', '')} {kwargs.get('packing_details', {}).get('package_type', '')}",
                "goods_description": product_info.get("description", ""),
                "quantity": str(product_info.get("quantity", "")),
                "unit_price": str(product_info.get("unit_price", "")),
                "amount": str(total_amount),
                "signed_by": company_info.get("representative", "")
            }
            
            return pdf_data
            
        except Exception as e:
            print(f"❌ 상업송장 생성 오류: {str(e)}")
            return f"상업송장 생성 중 오류가 발생했습니다: {str(e)}"
    
    def _generate_packing_list(self, country, product, company_info, **kwargs):
        """포장명세서 생성"""
        try:
            # 데이터 추출
            product_info = kwargs.get('product_info', {})
            packing_details = kwargs.get('packing_details', {})
            
            # 안전한 문자열 변환
            def safe_str(value):
                if value is None:
                    return 'N/A'
                try:
                    return str(value)
                except:
                    return 'N/A'
            
            # PDF 데이터 준비 (좌표 파일의 필드명과 일치)
            pdf_data = {
                "seller": company_info.get("name", ""),
                "consignee": kwargs.get('buyer_info', {}).get("name", ""),
                "notify_party": kwargs.get('buyer_info', {}).get("notify_party", ""),
                "departure_date": kwargs.get('transport_info', {}).get("departure_date", ""),
                "vessel_flight": kwargs.get('transport_info', {}).get("vessel_flight", ""),
                "from_location": kwargs.get('transport_info', {}).get("from_location", ""),
                "to_location": kwargs.get('transport_info', {}).get("to_location", ""),
                "invoice_no_date": f"INV-{datetime.now().strftime('%Y%m%d')}-001 / {datetime.now().strftime('%Y-%m-%d')}",
                "buyer": kwargs.get('buyer_info', {}).get("name", ""),
                "other_references": kwargs.get('payment_info', {}).get("reference", ""),
                "shipping_marks": packing_details.get("shipping_marks", ""),
                "package_count_type": f"{packing_details.get('package_count', '')} {packing_details.get('package_type', '')}",
                "goods_description": product_info.get("description", ""),
                "quantity_net_weight": f"{product_info.get('quantity', '')} / {packing_details.get('net_weight', '')}",
                "gross_weight": str(packing_details.get("gross_weight", "")),
                "measurement": packing_details.get("dimensions", ""),
                "signed_by": company_info.get("representative", "")
            }
            
            return pdf_data
            
        except Exception as e:
            print(f"❌ 포장명세서 생성 오류: {str(e)}")
            return f"포장명세서 생성 중 오류가 발생했습니다: {str(e)}"

# 전역 변수로 생성기 인스턴스 생성
doc_generator = SimpleDocumentGenerator()

@app.route('/')
def index():
    """메인 페이지"""
    return jsonify({
        'message': 'KATI 수출 지원 시스템 - 서류 생성 API (PDF 포함)',
        'status': 'running',
        'version': '1.0.0',
        'pdf_available': PDF_AVAILABLE,
        'generated_docs_dir': GENERATED_DOCS_DIR
    })

@app.route('/api/health')
def health_check():
    """헬스 체크"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'KATI Document Generator',
        'pdf_available': PDF_AVAILABLE,
        'generated_docs_dir': GENERATED_DOCS_DIR,
        'platform': platform.system(),
        'python_version': platform.python_version()
    })

@app.route('/api/document-generation', methods=['POST'])
def api_document_generation():
    """서류 생성 API (PDF 포함)"""
    print("🔍 서류생성 API 호출됨")
    
    try:
        data = request.get_json()
        print(f"📥 받은 데이터: {data}")
        
        country = data.get('country', '')
        product_info = data.get('product_info', {})
        company_info = data.get('company_info', {})
        buyer_info = data.get('buyer_info', {})
        transport_info = data.get('transport_info', {})
        payment_info = data.get('payment_info', {})
        packing_details = data.get('packing_details', {})
        
        print(f"🌍 국가: {country}")
        print(f"📦 제품정보: {product_info}")
        print(f"🏢 회사정보: {company_info}")
        
        if not country:
            print("❌ 국가 미선택")
            return jsonify({'error': '국가를 선택해주세요.'})
        
        # 선택된 서류 확인
        selected_documents = data.get('selected_documents', [])
        print(f"📋 선택된 서류: {selected_documents}")
        
        if not selected_documents:
            return jsonify({'error': '최소 하나의 서류를 선택해주세요.'})
        
        # 자동 생성 가능한 서류만 필터링
        allowed_documents = ['상업송장', '포장명세서']
        filtered_documents = [doc for doc in selected_documents if doc in allowed_documents]
        
        if not filtered_documents:
            return jsonify({'error': '자동 생성 가능한 서류(상업송장, 포장명세서)를 선택해주세요.'})
        
        print(f"📋 필터링된 서류: {filtered_documents}")
        
        # 서류 생성
        print("📄 서류 생성 시작...")
        
        documents = {}
        pdf_files = {}
        
        for doc_type in filtered_documents:
            try:
                # 서류별 특화 데이터 준비
                doc_data = {
                    'product_info': product_info,
                    'buyer_info': buyer_info,
                    'transport_info': transport_info,
                    'payment_info': payment_info,
                    'packing_details': packing_details
                }
                
                print(f"📋 {doc_type} 생성 데이터:")
                print(f"  - product_info: {product_info}")
                print(f"  - buyer_info: {buyer_info}")
                print(f"  - transport_info: {transport_info}")
                print(f"  - payment_info: {payment_info}")
                print(f"  - packing_details: {packing_details}")
                
                # PDF 데이터 생성
                pdf_data = doc_generator.generate_document(
                    doc_type=doc_type,
                    country=country,
                    product=product_info.get('name', '라면'),
                    company_info=company_info,
                    **doc_data
                )
                
                # 영문 파일명 생성 (한글 및 특수문자 제거)
                doc_type_mapping = {
                    "상업송장": "commercial_invoice",
                    "포장명세서": "packing_list"
                }
                english_doc_type = doc_type_mapping.get(doc_type, doc_type)
                
                # 안전한 파일명 생성
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                safe_filename = f"{english_doc_type}_{timestamp}.pdf"
                pdf_path = os.path.join(GENERATED_DOCS_DIR, safe_filename)
                
                print(f"📁 생성할 파일 경로: {pdf_path}")
                print(f"📁 절대 경로: {os.path.abspath(pdf_path)}")
                
                # PDF 생성 (폴백 기능 포함)
                generated_file = doc_generator.generate_pdf_with_coordinates(doc_type, pdf_data, pdf_path)
                
                if generated_file:
                    # 파일 확장자에 따라 파일명 결정
                    if generated_file.endswith('.txt'):
                        # 텍스트 파일인 경우
                        actual_filename = os.path.basename(generated_file)
                        pdf_files[doc_type] = actual_filename
                        documents[doc_type] = f"텍스트 파일로 생성됨: {actual_filename}"
                    else:
                        # PDF 파일인 경우
                        pdf_files[doc_type] = safe_filename
                        documents[doc_type] = pdf_data
                    
                    print(f"✅ {doc_type} 생성 완료: {generated_file}")
                else:
                    print(f"❌ {doc_type} 생성 실패")
                    documents[doc_type] = f"❌ 서류 생성 실패"
                
            except Exception as e:
                print(f"❌ {doc_type} 생성 실패: {str(e)}")
                documents[doc_type] = f"❌ 서류 생성 실패: {str(e)}"
        
        print(f"✅ 서류 생성 완료: {len(documents)}개")
        print(f"📄 생성된 서류: {list(documents.keys())}")
        
        # 다운로드 URL 생성
        download_urls = {}
        for doc_name, filename in pdf_files.items():
            download_urls[doc_name] = f"/api/download-document/{filename}"
        
        return jsonify({
            'success': True,
            'message': '서류 생성 완료',
            'documents': documents,
            'pdf_files': pdf_files,
            'download_urls': download_urls,
            'generated_count': len(pdf_files),
            'pdf_available': PDF_AVAILABLE,
            'generated_docs_dir': GENERATED_DOCS_DIR,
            'debug_info': {
                'current_dir': os.getcwd(),
                'platform': platform.system(),
                'python_version': platform.python_version(),
                'filesystem_info': {
                    'docs_dir_exists': os.path.exists(GENERATED_DOCS_DIR),
                    'docs_dir_writable': os.access(GENERATED_DOCS_DIR, os.W_OK) if os.path.exists(GENERATED_DOCS_DIR) else False,
                    'docs_dir_files': len(os.listdir(GENERATED_DOCS_DIR)) if os.path.exists(GENERATED_DOCS_DIR) else 0
                }
            },
            'download_instructions': {
                'method': 'GET',
                'urls': download_urls,
                'note': '각 URL을 브라우저에서 직접 접속하거나 JavaScript로 window.open() 사용'
            }
        })
        
    except Exception as e:
        print(f"❌ 서류 생성 API 전체 오류: {str(e)}")
        print(f"📋 상세 오류: {traceback.format_exc()}")
        return jsonify({'error': f'서류 생성 실패: {str(e)}'})

@app.route('/api/download-document/<filename>')
def download_document(filename):
    """파일 다운로드 (PDF 또는 텍스트)"""
    try:
        file_path = os.path.join(GENERATED_DOCS_DIR, filename)
        abs_file_path = os.path.abspath(file_path)
        
        print(f"🔍 파일 다운로드 요청: {filename}")
        print(f"📁 상대 경로: {file_path}")
        print(f"📁 절대 경로: {abs_file_path}")
        print(f"📁 폴더 존재: {os.path.exists(GENERATED_DOCS_DIR)}")
        print(f"📄 파일 존재: {os.path.exists(file_path)}")
        print(f"📄 절대 경로 파일 존재: {os.path.exists(abs_file_path)}")
        
        # 폴더 내용 확인
        if os.path.exists(GENERATED_DOCS_DIR):
            try:
                files_in_dir = os.listdir(GENERATED_DOCS_DIR)
                print(f"📋 폴더 내 파일들: {files_in_dir}")
            except Exception as e:
                print(f"❌ 폴더 내용 읽기 실패: {e}")
        
        # 파일 존재 확인 (여러 경로 시도)
        target_path = None
        if os.path.exists(file_path):
            target_path = file_path
            print(f"✅ 상대 경로로 파일 발견: {file_path}")
        elif os.path.exists(abs_file_path):
            target_path = abs_file_path
            print(f"✅ 절대 경로로 파일 발견: {abs_file_path}")
        else:
            print(f"❌ 파일을 찾을 수 없음")
            print(f"  - 상대 경로: {file_path}")
            print(f"  - 절대 경로: {abs_file_path}")
            
            # 추가 디버깅 정보
            print(f"🔍 추가 디버깅 정보:")
            print(f"  - 현재 작업 디렉토리: {os.getcwd()}")
            print(f"  - GENERATED_DOCS_DIR: {GENERATED_DOCS_DIR}")
            print(f"  - 폴더 존재: {os.path.exists(GENERATED_DOCS_DIR)}")
            if os.path.exists(GENERATED_DOCS_DIR):
                try:
                    files = os.listdir(GENERATED_DOCS_DIR)
                    print(f"  - 폴더 내 파일들: {files}")
                except Exception as e:
                    print(f"  - 폴더 읽기 실패: {e}")
            
            return jsonify({
                'error': '파일을 찾을 수 없습니다.',
                'filename': filename,
                'file_path': file_path,
                'abs_file_path': abs_file_path,
                'folder_exists': os.path.exists(GENERATED_DOCS_DIR),
                'folder_path': GENERATED_DOCS_DIR,
                'current_dir': os.getcwd(),
                'debug_info': {
                    'folder_files': os.listdir(GENERATED_DOCS_DIR) if os.path.exists(GENERATED_DOCS_DIR) else [],
                    'folder_writable': os.access(GENERATED_DOCS_DIR, os.W_OK) if os.path.exists(GENERATED_DOCS_DIR) else False,
                    'platform': platform.system(),
                    'python_version': platform.python_version()
                }
            }), 404
        
        # 파일 읽기 권한 확인
        if not os.access(target_path, os.R_OK):
            print(f"❌ 파일 읽기 권한 없음: {target_path}")
            return jsonify({
                'error': '파일 읽기 권한이 없습니다.',
                'filename': filename,
                'file_path': target_path
            }), 403
        
        print(f"✅ 파일 발견, 다운로드 시작: {target_path}")
        return send_file(target_path, as_attachment=True, download_name=filename)
        
    except Exception as e:
        print(f"❌ 파일 다운로드 오류: {str(e)}")
        print(f"📋 상세 오류: {traceback.format_exc()}")
        return jsonify({
            'error': f'파일 다운로드 실패: {str(e)}',
            'filename': filename,
            'file_path': os.path.join(GENERATED_DOCS_DIR, filename) if 'GENERATED_DOCS_DIR' in globals() else 'unknown'
        }), 500

@app.route('/api/system-status')
def api_system_status():
    """시스템 상태 확인"""
    return jsonify({
        'status': 'operational',
        'service': 'KATI Document Generator (PDF 포함)',
        'version': '1.0.0',
        'environment': 'production',
        'features': {
            'document_generation': True,
            'pdf_generation': PDF_AVAILABLE,  # PDF 사용 가능 여부
            'ocr_processing': False,
            'ai_services': False
        },
        'supported_documents': ['상업송장', '포장명세서'],
        'pdf_available': PDF_AVAILABLE,
        'generated_docs_dir': GENERATED_DOCS_DIR,
        'platform': platform.system(),
        'python_version': platform.python_version(),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 KATI 서류 생성 API 시작 (PDF 포함)")
    print("📋 지원 기능:")
    print("  - 상업송장 생성 (PDF)")
    print("  - 포장명세서 생성 (PDF)")
    print("  - 좌표 기반 PDF 생성")
    print("  - 배포 환경 최적화")
    print(f"  - PDF 사용 가능: {PDF_AVAILABLE}")
    print(f"  - 생성 폴더: {GENERATED_DOCS_DIR}")
    print(f"  - 플랫폼: {platform.system()}")
    print(f"  - Python 버전: {platform.python_version()}")
    
    # 포트 설정 (환경 변수에서 가져오거나 기본값 사용)
    port = int(os.environ.get('PORT', 5000))
    
    app.run(host='0.0.0.0', port=port, debug=False) 