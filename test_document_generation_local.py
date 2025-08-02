#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time

def test_document_generation():
    """로컬 서버의 서류생성 API 테스트"""
    
    # 서버 시작 대기
    print("🔄 서버 시작 대기 중...")
    time.sleep(5)
    
    # 테스트 데이터
    test_data = {
        "country": "중국",
        "product_info": {
            "name": "라면",
            "quantity": "1000개",
            "unit_price": "1.5달러"
        },
        "company_info": {
            "name": "테스트회사",
            "address": "서울시 강남구",
            "phone": "02-1234-5678"
        },
        "buyer_info": {
            "name": "중국구매자",
            "address": "베이징시",
            "phone": "010-1234-5678"
        },
        "transport_info": {
            "method": "해운",
            "port": "인천항"
        },
        "payment_info": {
            "method": "신용장",
            "terms": "D/P"
        },
        "packing_details": {
            "weight": "1kg",
            "dimensions": "10x10x5cm"
        },
        "selected_documents": ["상업송장", "포장명세서"]
    }
    
    try:
        print("📡 서류생성 API 호출 중...")
        print(f"📋 요청 데이터: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
        
        response = requests.post(
            "http://localhost:5000/api/document-generation",
            headers={"Content-Type": "application/json"},
            json=test_data,
            timeout=30
        )
        
        print(f"📊 응답 상태 코드: {response.status_code}")
        print(f"📄 응답 헤더: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 서류생성 성공!")
            print(f"📋 응답 데이터: {json.dumps(result, ensure_ascii=False, indent=2)}")
        else:
            print(f"❌ 서류생성 실패: {response.status_code}")
            print(f"📄 응답 내용: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.")
    except requests.exceptions.Timeout:
        print("❌ 요청 시간 초과")
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

if __name__ == "__main__":
    test_document_generation() 