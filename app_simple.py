#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌐 KATI 간단한 서류 생성 API - 배포 환경용 (PDF 생성 포함)
- 좌표 매핑된 PDF 템플릿 활용
- 배포 환경에서 안정적으로 작동
"""

from flask import Flask, request, jsonify, send_file
from datetime import datetime
import os
import json
import fitz  # PyMuPDF

app = Flask(__name__)

class SimpleDocumentGenerator:
    """간단한 서류 생성기 (PDF 포함)"""
    
    def __init__(self):
        print("✅ SimpleDocumentGenerator 초기화 완료")
        self.template_files = {
            "상업송장": {
                "pdf": "uploaded_templates/상업송장 빈 템플릿.pdf",
                "coordinates": "uploaded_templates/상업송장 좌표 반영.json"
            },
            "포장명세서": {
                "pdf": "uploaded_templates/포장명세서 빈 템플릿.pdf", 
                "coordinates": "uploaded_templates/포장명세서 좌표 반영.json"
            }
        }
    
    def generate_document(self, doc_type, country, product, company_info, **kwargs):
        """문서 생성 메인 함수"""
        try:
            if doc_type == "상업송장":
                return self._generate_commercial_invoice(country, product, company_info, **kwargs)
            elif doc_type == "포장명세서":
                return self._generate_packing_list(country, product, company_info, **kwargs)
            else:
                return f"지원하지 않는 문서 유형: {doc_type}"
        except Exception as e:
            print(f"❌ 문서 생성 오류: {str(e)}")
            return f"문서 생성 중 오류가 발생했습니다: {str(e)}"
    
    def generate_pdf_with_coordinates(self, doc_type, data, output_path):
        """좌표 기반 PDF 생성"""
        try:
            print(f"📄 PDF 생성 시작: {doc_type}")
            
            # 템플릿 파일 경로 확인
            template_info = self.template_files.get(doc_type)
            if not template_info:
                raise ValueError(f"템플릿 정보를 찾을 수 없습니다: {doc_type}")
            
            pdf_template = template_info["pdf"]
            coord_file = template_info["coordinates"]
            
            print(f"📁 PDF 템플릿: {pdf_template}")
            print(f"📁 좌표 파일: {coord_file}")
            
            # 파일 존재 확인
            if not os.path.exists(pdf_template):
                raise FileNotFoundError(f"PDF 템플릿 파일이 없습니다: {pdf_template}")
            if not os.path.exists(coord_file):
                raise FileNotFoundError(f"좌표 파일이 없습니다: {coord_file}")
            
            # 좌표 정보 로드
            with open(coord_file, 'r', encoding='utf-8') as f:
                coordinates = json.load(f)
            
            print(f"✅ 좌표 정보 로드됨: {len(coordinates)}개 필드")
            
            # PDF 템플릿 열기
            doc = fitz.open(pdf_template)
            page = doc[0]  # 첫 번째 페이지
            
            # 데이터를 좌표에 맞춰 삽입
            for field_name, field_data in coordinates.items():
                if field_name in data and data[field_name]:
                    x = field_data["x"]
                    y = field_data["y"]
                    font_size = field_data.get("font_size", 9)
                    text = str(data[field_name])
                    
                    print(f"📝 텍스트 삽입: {field_name} = '{text}' at ({x}, {y})")
                    
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
            
            # 출력 디렉토리 생성
            output_dir = os.path.dirname(output_path)
            os.makedirs(output_dir, exist_ok=True)
            
            # PDF 저장
            doc.save(output_path)
            doc.close()
            
            print(f"✅ PDF 생성 완료: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ PDF 생성 오류: {str(e)}")
            raise e
    
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
        'version': '1.0.0'
    })

@app.route('/api/health')
def health_check():
    """헬스 체크"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'KATI Document Generator'
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
                
                # PDF 파일 생성
                safe_name = doc_type.replace("/", "_").replace(" ", "_")
                pdf_filename = f"{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                pdf_path = os.path.join("generated_documents", pdf_filename)
                
                # PDF 생성
                doc_generator.generate_pdf_with_coordinates(doc_type, pdf_data, pdf_path)
                
                documents[doc_type] = pdf_data
                pdf_files[doc_type] = pdf_filename
                print(f"✅ {doc_type} 생성 완료")
                
            except Exception as e:
                print(f"❌ {doc_type} 생성 실패: {str(e)}")
                documents[doc_type] = f"❌ 서류 생성 실패: {str(e)}"
        
        print(f"✅ 서류 생성 완료: {len(documents)}개")
        print(f"📄 생성된 서류: {list(documents.keys())}")
        
        # PDF 다운로드 URL 생성
        pdf_download_urls = {}
        for doc_name, filename in pdf_files.items():
            pdf_download_urls[doc_name] = f"/api/download-document/{filename}"
        
        return jsonify({
            'success': True,
            'message': '서류 생성 완료',
            'documents': documents,
            'pdf_files': pdf_files,
            'download_urls': pdf_download_urls,
            'generated_count': len(pdf_files),
            'download_instructions': {
                'method': 'GET',
                'urls': pdf_download_urls,
                'note': '각 URL을 브라우저에서 직접 접속하거나 JavaScript로 window.open() 사용'
            }
        })
        
    except Exception as e:
        print(f"❌ 서류 생성 API 전체 오류: {str(e)}")
        import traceback
        print(f"📋 상세 오류: {traceback.format_exc()}")
        return jsonify({'error': f'서류 생성 실패: {str(e)}'})

@app.route('/api/download-document/<filename>')
def download_document(filename):
    """PDF 파일 다운로드"""
    try:
        file_path = os.path.join("generated_documents", filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True, download_name=filename)
        else:
            return jsonify({'error': '파일을 찾을 수 없습니다.'}), 404
    except Exception as e:
        return jsonify({'error': f'파일 다운로드 실패: {str(e)}'}), 500

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
            'pdf_generation': True,  # PDF 생성 활성화
            'ocr_processing': False,
            'ai_services': False
        },
        'supported_documents': ['상업송장', '포장명세서'],
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 KATI 서류 생성 API 시작 (PDF 포함)")
    print("📋 지원 기능:")
    print("  - 상업송장 생성 (PDF)")
    print("  - 포장명세서 생성 (PDF)")
    print("  - 좌표 기반 PDF 생성")
    print("  - 배포 환경 최적화")
    
    # 포트 설정 (환경 변수에서 가져오거나 기본값 사용)
    port = int(os.environ.get('PORT', 5000))
    
    app.run(host='0.0.0.0', port=port, debug=False) 