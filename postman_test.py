#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📄 Postman 스타일 API 테스트
- 서류생성 API를 Postman과 동일한 방식으로 테스트
- 다양한 케이스별 테스트 수행
"""

import requests
import json
import time
from datetime import datetime

def test_document_generation_api():
    """서류생성 API Postman 스타일 테스트"""
    print("="*80)
    print("📄 Postman 스타일 서류생성 API 테스트")
    print("="*80)
    
    base_url = "http://localhost:5000"
    
    # 테스트 1: 기본 서류생성 요청
    print("\n🔍 테스트 1: 기본 서류생성 요청")
    print("-" * 50)
    
    test_data = {
        "country": "중국",
        "product_info": {
            "name": "테스트 라면",
            "description": "맛있는 테스트 라면",
            "quantity": "1000",
            "unit_price": "1.00",
            "total_amount": "1000.00"
        },
        "company_info": {
            "name": "테스트 회사",
            "address": "서울시 강남구 테스트로 123",
            "phone": "02-1234-5678",
            "email": "test@company.com",
            "representative": "홍길동"
        },
        "buyer_info": {
            "name": "중국 구매자",
            "address": "중국 상하이시 테스트구 456",
            "phone": "+86-123-4567-8900",
            "email": "buyer@china.com",
            "notify_party": "중국 통관업체"
        },
        "transport_info": {
            "departure_date": "2025-08-01",
            "vessel_flight": "VESSEL001",
            "from_location": "인천항",
            "to_location": "상하이항",
            "delivery_terms": "FOB"
        },
        "payment_info": {
            "payment_terms": "L/C",
            "lc_number": "LC2025001",
            "lc_date": "2025-07-15",
            "reference": "REF001"
        },
        "packing_details": {
            "package_count": "100",
            "package_type": "박스",
            "shipping_marks": "TEST/MARK",
            "net_weight": "500kg",
            "gross_weight": "550kg",
            "dimensions": "50x30x20cm"
        },
        "documents_to_generate": ["상업송장", "포장명세서"]
    }
    
    try:
        print("📤 요청 전송 중...")
        print(f"URL: {base_url}/api/document-generation")
        print(f"Method: POST")
        print(f"Content-Type: application/json")
        print(f"Request Body:")
        print(json.dumps(test_data, indent=2, ensure_ascii=False))
        
        response = requests.post(
            f"{base_url}/api/document-generation",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"\n📥 응답 수신:")
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body:")
        
        try:
            response_json = response.json()
            print(json.dumps(response_json, indent=2, ensure_ascii=False))
        except:
            print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
        
        if response.status_code == 200:
            print("✅ 테스트 1 성공!")
        else:
            print("❌ 테스트 1 실패!")
            
    except Exception as e:
        print(f"❌ 테스트 1 오류: {e}")
    
    # 테스트 2: 빈 국가 요청 (오류 케이스)
    print("\n🔍 테스트 2: 빈 국가 요청 (오류 케이스)")
    print("-" * 50)
    
    error_data = {
        "country": "",
        "product_info": {"name": "테스트 제품"},
        "documents_to_generate": ["상업송장"]
    }
    
    try:
        print("📤 요청 전송 중...")
        print(f"URL: {base_url}/api/document-generation")
        print(f"Method: POST")
        print(f"Content-Type: application/json")
        print(f"Request Body:")
        print(json.dumps(error_data, indent=2, ensure_ascii=False))
        
        response = requests.post(
            f"{base_url}/api/document-generation",
            json=error_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"\n📥 응답 수신:")
        print(f"Status Code: {response.status_code}")
        print(f"Response Body:")
        
        try:
            response_json = response.json()
            print(json.dumps(response_json, indent=2, ensure_ascii=False))
        except:
            print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
        
        if response.status_code == 400:
            print("✅ 테스트 2 성공! (예상된 오류 응답)")
        else:
            print("❌ 테스트 2 실패! (예상과 다른 응답)")
            
    except Exception as e:
        print(f"❌ 테스트 2 오류: {e}")
    
    # 테스트 3: 잘못된 JSON 형식 (오류 케이스)
    print("\n🔍 테스트 3: 잘못된 JSON 형식 (오류 케이스)")
    print("-" * 50)
    
    try:
        print("📤 요청 전송 중...")
        print(f"URL: {base_url}/api/document-generation")
        print(f"Method: POST")
        print(f"Content-Type: application/json")
        print(f"Request Body: invalid json")
        
        response = requests.post(
            f"{base_url}/api/document-generation",
            data="invalid json",
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"\n📥 응답 수신:")
        print(f"Status Code: {response.status_code}")
        print(f"Response Body:")
        
        try:
            response_json = response.json()
            print(json.dumps(response_json, indent=2, ensure_ascii=False))
        except:
            print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
        
        if response.status_code == 400:
            print("✅ 테스트 3 성공! (예상된 오류 응답)")
        else:
            print("❌ 테스트 3 실패! (예상과 다른 응답)")
            
    except Exception as e:
        print(f"❌ 테스트 3 오류: {e}")
    
    # 테스트 4: 준수성 분석 API 테스트
    print("\n🔍 테스트 4: 준수성 분석 API 테스트")
    print("-" * 50)
    
    compliance_data = {
        "country": "중국",
        "product_type": "식품",
        "use_ocr": True,
        "company_info": {
            "name": "테스트 회사",
            "address": "서울시 강남구"
        },
        "product_info": {
            "name": "테스트 라면",
            "description": "맛있는 라면"
        },
        "uploaded_documents": [],
        "prepared_documents": [],
        "labeling_info": {}
    }
    
    try:
        print("📤 요청 전송 중...")
        print(f"URL: {base_url}/api/compliance-analysis")
        print(f"Method: POST")
        print(f"Content-Type: application/json")
        print(f"Request Body:")
        print(json.dumps(compliance_data, indent=2, ensure_ascii=False))
        
        response = requests.post(
            f"{base_url}/api/compliance-analysis",
            json=compliance_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"\n📥 응답 수신:")
        print(f"Status Code: {response.status_code}")
        print(f"Response Body:")
        
        try:
            response_json = response.json()
            print(json.dumps(response_json, indent=2, ensure_ascii=False))
        except:
            print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
        
        if response.status_code == 200:
            print("✅ 테스트 4 성공!")
        else:
            print("❌ 테스트 4 실패!")
            
    except Exception as e:
        print(f"❌ 테스트 4 오류: {e}")
    
    print("\n" + "="*80)
    print("📄 Postman 스타일 테스트 완료")
    print("="*80)

if __name__ == "__main__":
    # 서버 시작 대기
    print("⏳ 서버 시작 대기 중... (5초)")
    time.sleep(5)
    
    test_document_generation_api() 