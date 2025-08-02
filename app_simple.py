#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌐 KATI 간단한 서류 생성 API - 배포 환경용
- 최소한의 의존성으로 서류 생성 기능 제공
- 배포 환경에서 안정적으로 작동
"""

from flask import Flask, request, jsonify
from datetime import datetime
import os

app = Flask(__name__)

class SimpleDocumentGenerator:
    """간단한 서류 생성기"""
    
    def __init__(self):
        print("✅ SimpleDocumentGenerator 초기화 완료")
    
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
            
            # 문서 생성
            lines = []
            lines.append("=== 상업송장 (Commercial Invoice) ===")
            lines.append("")
            lines.append("📋 기본 정보")
            lines.append(f"- 국가: {safe_str(country)}")
            lines.append(f"- 제품명: {safe_str(product)}")
            lines.append(f"- 발행일: {datetime.now().strftime('%Y-%m-%d')}")
            lines.append("")
            lines.append("🏢 판매자 정보")
            lines.append(f"- 회사명: {safe_str(company_info.get('name'))}")
            lines.append(f"- 주소: {safe_str(company_info.get('address'))}")
            lines.append(f"- 연락처: {safe_str(company_info.get('phone'))}")
            lines.append(f"- 이메일: {safe_str(company_info.get('email'))}")
            lines.append("")
            lines.append("👤 구매자 정보")
            lines.append(f"- 회사명: {safe_str(buyer_info.get('name'))}")
            lines.append(f"- 주소: {safe_str(buyer_info.get('address'))}")
            lines.append(f"- 연락처: {safe_str(buyer_info.get('phone'))}")
            lines.append("")
            lines.append("📦 제품 정보")
            lines.append(f"- 제품명: {safe_str(product_info.get('name', product))}")
            lines.append(f"- 수량: {safe_str(product_info.get('quantity'))}")
            lines.append(f"- 단가: {safe_str(product_info.get('unit_price'))}")
            lines.append(f"- 총액: {safe_str(total_amount)}")
            lines.append("")
            lines.append("🚢 운송 정보")
            lines.append(f"- 운송방법: {safe_str(transport_info.get('method'))}")
            lines.append(f"- 출발지: {safe_str(transport_info.get('origin'))}")
            lines.append(f"- 도착지: {safe_str(transport_info.get('destination'))}")
            lines.append("")
            lines.append("💳 결제 정보")
            lines.append(f"- 결제방법: {safe_str(payment_info.get('method'))}")
            lines.append(f"- 통화: {safe_str(payment_info.get('currency', 'USD'))}")
            lines.append("")
            lines.append("---")
            lines.append("KATI 수출 지원 시스템에서 생성된 상업송장입니다.")
            
            return "\n".join(lines)
            
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
            
            # 문서 생성
            lines = []
            lines.append("=== 포장명세서 (Packing List) ===")
            lines.append("")
            lines.append("📋 기본 정보")
            lines.append(f"- 국가: {safe_str(country)}")
            lines.append(f"- 제품명: {safe_str(product)}")
            lines.append(f"- 발행일: {datetime.now().strftime('%Y-%m-%d')}")
            lines.append("")
            lines.append("🏢 발송자 정보")
            lines.append(f"- 회사명: {safe_str(company_info.get('name'))}")
            lines.append(f"- 주소: {safe_str(company_info.get('address'))}")
            lines.append(f"- 연락처: {safe_str(company_info.get('phone'))}")
            lines.append("")
            lines.append("📦 포장 정보")
            lines.append(f"- 포장 방법: {safe_str(packing_details.get('method'))}")
            lines.append(f"- 포장 재질: {safe_str(packing_details.get('material', 'Carton'))}")
            lines.append(f"- 포장 크기: {safe_str(packing_details.get('size', 'Standard'))}")
            lines.append(f"- 포장 무게: {safe_str(packing_details.get('weight'))}")
            lines.append("")
            lines.append("📋 상세 명세")
            lines.append(f"- 제품명: {safe_str(product_info.get('name', product))}")
            lines.append(f"- 수량: {safe_str(product_info.get('quantity'))}")
            lines.append(f"- 단위: {safe_str(product_info.get('unit', '개'))}")
            lines.append(f"- 총 포장 수: {safe_str(packing_details.get('total_packages'))}")
            lines.append("")
            lines.append("📝 특이사항")
            lines.append(f"- 취급 주의: {safe_str(packing_details.get('handling_notes'))}")
            lines.append(f"- 보관 조건: {safe_str(packing_details.get('storage_conditions'))}")
            lines.append("")
            lines.append("---")
            lines.append("KATI 수출 지원 시스템에서 생성된 포장명세서입니다.")
            
            return "\n".join(lines)
            
        except Exception as e:
            print(f"❌ 포장명세서 생성 오류: {str(e)}")
            return f"포장명세서 생성 중 오류가 발생했습니다: {str(e)}"

# 전역 변수로 생성기 인스턴스 생성
doc_generator = SimpleDocumentGenerator()

@app.route('/')
def index():
    """메인 페이지"""
    return jsonify({
        'message': 'KATI 수출 지원 시스템 - 간단한 서류 생성 API',
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
    """간단한 서류 생성 API"""
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
                
                content = doc_generator.generate_document(
                    doc_type=doc_type,
                    country=country,
                    product=product_info.get('name', '라면'),
                    company_info=company_info,
                    **doc_data
                )
                documents[doc_type] = content
                print(f"✅ {doc_type} 생성 완료")
            except Exception as e:
                print(f"❌ {doc_type} 생성 실패: {str(e)}")
                documents[doc_type] = f"❌ 서류 생성 실패: {str(e)}"
        
        print(f"✅ 서류 생성 완료: {len(documents)}개")
        print(f"📄 생성된 서류: {list(documents.keys())}")
        
        return jsonify({
            'success': True,
            'message': '서류 생성 완료',
            'documents': documents,
            'generated_count': len(documents),
            'generated_documents': list(documents.keys()),
            'note': '배포 환경에서는 텍스트 형태로만 제공됩니다. PDF 변환은 로컬 환경에서 가능합니다.'
        })
        
    except Exception as e:
        print(f"❌ 서류 생성 API 전체 오류: {str(e)}")
        import traceback
        print(f"📋 상세 오류: {traceback.format_exc()}")
        return jsonify({'error': f'서류 생성 실패: {str(e)}'})

@app.route('/api/system-status')
def api_system_status():
    """시스템 상태 확인"""
    return jsonify({
        'status': 'operational',
        'service': 'KATI Simple Document Generator',
        'version': '1.0.0',
        'environment': 'production',
        'features': {
            'document_generation': True,
            'pdf_generation': False,  # 배포 환경에서는 비활성화
            'ocr_processing': False,
            'ai_services': False
        },
        'supported_documents': ['상업송장', '포장명세서'],
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 KATI 간단한 서류 생성 API 시작")
    print("📋 지원 기능:")
    print("  - 상업송장 생성")
    print("  - 포장명세서 생성")
    print("  - 텍스트 형태 출력")
    print("  - 배포 환경 최적화")
    
    # 포트 설정 (환경 변수에서 가져오거나 기본값 사용)
    port = int(os.environ.get('PORT', 5000))
    
    app.run(host='0.0.0.0', port=port, debug=False) 