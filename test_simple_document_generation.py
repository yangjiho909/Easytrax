#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
간단한 서류 생성 API 테스트 스크립트
"""

import requests
import json

# 테스트 서버 URL (로컬 테스트용)
BASE_URL = "http://localhost:5000"

def test_simple_document_generation():
    """간단한 서류 생성 API 테스트"""
    print("📄 간단한 서류 생성 API 테스트")
    
    # 테스트 데이터
    test_data = {
        "country": "중국",
        "product_info": {
            "name": "테스트 라면",
            "quantity": 1000,
            "unit_price": 2.5,
            "description": "맛있는 라면"
        },
        "company_info": {
            "name": "테스트 회사",
            "address": "서울시 강남구",
            "phone": "02-1234-5678",
            "email": "test@company.com"
        },
        "buyer_info": {
            "name": "중국 구매자",
            "address": "베이징시",
            "phone": "010-1234-5678"
        },
        "transport_info": {
            "method": "해운",
            "origin": "부산항",
            "destination": "상하이항"
        },
        "payment_info": {
            "method": "신용장",
            "currency": "USD"
        },
        "packing_details": {
            "package_type": "박스",
            "weight": "500g",
            "method": "표준 포장",
            "material": "골판지",
            "size": "30x20x10cm",
            "total_packages": 50,
            "handling_notes": "습기 주의",
            "storage_conditions": "상온 보관"
        },
        "selected_documents": ["상업송장", "포장명세서"],
        "customization": {
            "language": "ko",
            "format": "text"
        }
    }
    
    try:
        print("📤 서류생성 요청 전송 중...")
        response = requests.post(f"{BASE_URL}/api/document-generation", 
                               json=test_data,
                               headers={'Content-Type': 'application/json'})
        
        print(f"📥 응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 서류생성 성공!")
            print(f"📋 생성된 서류 수: {result.get('generated_count', 0)}")
            print(f"📄 생성된 서류: {result.get('generated_documents', [])}")
            
            # 생성된 서류 내용 출력
            documents = result.get('documents', {})
            for doc_name, content in documents.items():
                print(f"\n📋 {doc_name}:")
                print("=" * 50)
                print(content)
                print("=" * 50)
        else:
            print(f"❌ 서류생성 실패: HTTP {response.status_code}")
            print(f"📋 응답 내용: {response.text}")
            
    except Exception as e:
        print(f"❌ 서류생성 테스트 실패: {str(e)}")

def test_health_check():
    """헬스 체크 테스트"""
    print("\n🏥 헬스 체크 테스트")
    
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"📥 응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 서버 정상 작동")
            print(f"📋 상태: {result.get('status')}")
            print(f"📋 서비스: {result.get('service')}")
        else:
            print(f"❌ 서버 오류: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ 헬스 체크 실패: {str(e)}")

def test_main_page():
    """메인 페이지 테스트"""
    print("\n🏠 메인 페이지 테스트")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"📥 응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 메인 페이지 정상")
            print(f"📋 메시지: {result.get('message')}")
            print(f"📋 상태: {result.get('status')}")
            print(f"📋 버전: {result.get('version')}")
        else:
            print(f"❌ 메인 페이지 오류: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ 메인 페이지 테스트 실패: {str(e)}")

def test_system_status():
    """시스템 상태 테스트"""
    print("\n🔧 시스템 상태 테스트")
    
    try:
        response = requests.get(f"{BASE_URL}/api/system-status")
        print(f"📥 응답 상태: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 시스템 상태 확인 성공")
            print(f"📋 상태: {result.get('status')}")
            print(f"📋 서비스: {result.get('service')}")
            print(f"📋 환경: {result.get('environment')}")
            print(f"📋 지원 서류: {result.get('supported_documents')}")
            
            features = result.get('features', {})
            print("📋 기능 상태:")
            for feature, enabled in features.items():
                status = "✅ 활성화" if enabled else "❌ 비활성화"
                print(f"  - {feature}: {status}")
        else:
            print(f"❌ 시스템 상태 확인 실패: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ 시스템 상태 테스트 실패: {str(e)}")

def main():
    """메인 테스트 함수"""
    print("🚀 간단한 서류 생성 API 테스트 시작")
    print("=" * 50)
    
    # 1. 헬스 체크
    test_health_check()
    
    # 2. 메인 페이지
    test_main_page()
    
    # 3. 시스템 상태
    test_system_status()
    
    # 4. 서류 생성
    test_simple_document_generation()
    
    print("\n" + "=" * 50)
    print("✅ 모든 테스트 완료")

if __name__ == "__main__":
    main() 