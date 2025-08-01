#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
간단한 서류생성 테스트 앱
"""

from flask import Flask, request, jsonify
from new_document_generator import NewDocumentGenerator
import os

app = Flask(__name__)

@app.route('/api/health', methods=['GET'])
def health_check():
    """헬스 체크"""
    return jsonify({
        'status': 'healthy',
        'message': '서류생성 테스트 서버 정상 작동'
    })

@app.route('/api/document-generation', methods=['POST'])
def api_document_generation():
    """서류생성 API"""
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
        
        # DocumentGenerator 생성
        print("📋 DocumentGenerator 생성 중...")
        try:
            doc_generator = NewDocumentGenerator()
            print("✅ DocumentGenerator 생성 성공")
        except Exception as e:
            print(f"❌ DocumentGenerator 생성 실패: {str(e)}")
            return jsonify({'error': f'서류 생성기 초기화 실패: {str(e)}'})
        
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
            'generated_count': len(documents)
        })
        
    except Exception as e:
        print(f"❌ 서류생성 API 오류: {str(e)}")
        import traceback
        print(f"📋 상세 오류: {traceback.format_exc()}")
        return jsonify({'error': f'서류생성 중 오류가 발생했습니다: {str(e)}'})

@app.route('/')
def index():
    """메인 페이지"""
    return jsonify({
        'message': '서류생성 테스트 서버',
        'endpoints': {
            'health': '/api/health',
            'document_generation': '/api/document-generation'
        }
    })

if __name__ == '__main__':
    print("🚀 서류생성 테스트 서버 시작")
    app.run(debug=True, host='0.0.0.0', port=5000) 