#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
서류생성 API 테스트 스크립트
"""

import requests
import json

# 테스트 서버 URL
BASE_URL = "https://kati-export-helper.onrender.com"

def test_document_generation():
    """서류생성 API 테스트"""
    print("📄 서류생성 API 테스트")
    
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
            "weight": "500g"
        },
        "selected_documents": ["상업송장", "포장명세서"],
        "customization": {
            "language": "ko",
            "format": "pdf"
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
            print(f"📋 결과: {result}")
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
            print("✅ 서버 정상 작동")
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
            print("✅ 메인 페이지 접근 가능")
        else:
            print(f"❌ 메인 페이지 오류: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ 메인 페이지 테스트 실패: {str(e)}")

def main():
    """메인 테스트 함수"""
    print("🚀 서류생성 테스트 시작")
    print("=" * 50)
    
    # 1. 헬스 체크
    test_health_check()
    
    # 2. 메인 페이지 테스트
    test_main_page()
    
    # 3. 서류생성 테스트
    test_document_generation()
    
    print("\n" + "=" * 50)
    print("✅ 모든 테스트 완료")

if __name__ == "__main__":
    main() 