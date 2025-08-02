#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
로컬 다운로드 테스트 스크립트
"""

import requests
import json
import time

def test_document_generation():
    """서류 생성 API 테스트"""
    
    # 테스트 데이터
    test_data = {
        "country": "중국",
        "product_info": {
            "name": "라면",
            "description": "신라면",
            "quantity": 1000,
            "unit_price": 2.5
        },
        "company_info": {
            "name": "농심",
            "representative": "신춘수"
        },
        "buyer_info": {
            "name": "중국수입상",
            "notify_party": "중국통관업체"
        },
        "transport_info": {
            "departure_date": "2024-08-02",
            "vessel_flight": "COSCO SHIPPING UNIVERSE",
            "from_location": "부산",
            "to_location": "상해",
            "delivery_terms": "FOB"
        },
        "payment_info": {
            "lc_number": "LC123456",
            "lc_date": "2024-08-01",
            "reference": "REF001",
            "payment_terms": "L/C"
        },
        "packing_details": {
            "shipping_marks": "NONG SHIM",
            "package_count": 100,
            "package_type": "CARTONS",
            "net_weight": "500KG",
            "gross_weight": "550KG",
            "dimensions": "100x50x30cm"
        },
        "selected_documents": ["상업송장", "포장명세서"]
    }
    
    print("🚀 서류 생성 API 테스트 시작")
    print(f"📥 전송 데이터: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
    
    try:
        # API 호출
        response = requests.post(
            "http://localhost:5000/api/document-generation",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📤 응답 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 서류 생성 성공!")
            print(f"📄 생성된 서류: {result.get('generated_count', 0)}개")
            print(f"📁 파일 목록: {result.get('pdf_files', {})}")
            print(f"🔗 다운로드 URL: {result.get('download_urls', {})}")
            
            # 다운로드 테스트
            download_urls = result.get('download_urls', {})
            for doc_name, url in download_urls.items():
                print(f"\n🔍 {doc_name} 다운로드 테스트:")
                print(f"   URL: {url}")
                
                try:
                    download_response = requests.get(f"http://localhost:5000{url}")
                    print(f"   상태 코드: {download_response.status_code}")
                    
                    if download_response.status_code == 200:
                        # 파일 저장
                        filename = f"test_{doc_name}_{int(time.time())}.pdf"
                        with open(filename, 'wb') as f:
                            f.write(download_response.content)
                        print(f"   ✅ 다운로드 성공: {filename}")
                        print(f"   📄 파일 크기: {len(download_response.content)} bytes")
                    else:
                        print(f"   ❌ 다운로드 실패: {download_response.text}")
                        
                except Exception as e:
                    print(f"   ❌ 다운로드 오류: {str(e)}")
        else:
            print(f"❌ 서류 생성 실패: {response.text}")
            
    except Exception as e:
        print(f"❌ API 호출 오류: {str(e)}")

if __name__ == "__main__":
    test_document_generation() 