#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
배포된 서버 API 테스트 스크립트
- 실제 배포된 서버의 API 엔드포인트 테스트
- 규제 준수성 분석 기능 확인
"""

import requests
import json
import time
from datetime import datetime

# 배포된 서버 URL
BASE_URL = "https://kati-export-helper.onrender.com"

def test_health_check():
    """서버 상태 확인"""
    print("🔍 서버 상태 확인")
    
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        print(f"✅ 상태 코드: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 서버 응답: {data}")
        else:
            print(f"❌ 서버 오류: {response.text}")
    except Exception as e:
        print(f"❌ 연결 실패: {str(e)}")

def test_regulation_status():
    """규제 상태 확인"""
    print("\n🔍 규제 상태 확인")
    
    try:
        response = requests.get(f"{BASE_URL}/api/regulation-status", 
                              params={'country': '중국', 'product_type': '식품'}, 
                              timeout=10)
        print(f"✅ 상태 코드: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 규제 상태: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 오류: {response.text}")
    except Exception as e:
        print(f"❌ 요청 실패: {str(e)}")

def test_compliance_analysis():
    """규제 준수성 분석 테스트"""
    print("\n🤖 규제 준수성 분석 테스트")
    
    test_data = {
        'country': '중국',
        'product_type': '식품',
        'product_name': '테스트 라면',
        'ingredients': '면, 스프, 조미료',
        'allergens': '대두, 밀',
        'nutrition_info': {
            'calories': '350',
            'protein': '12',
            'fat': '15',
            'carbs': '45'
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/compliance-analysis", 
                               json=test_data, 
                               timeout=30)
        print(f"✅ 상태 코드: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 분석 결과: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 오류: {response.text}")
    except Exception as e:
        print(f"❌ 요청 실패: {str(e)}")

def test_dynamic_compliance_analysis():
    """동적 준수성 분석 테스트"""
    print("\n⚡ 동적 준수성 분석 테스트")
    
    test_data = {
        'country': '중국',
        'product_type': '식품',
        'structured_data': {
            '라벨': {
                'product_name': '테스트 라면',
                'ingredients': '면, 스프, 조미료',
                'allergens': '대두, 밀',
                'text': '중국어 라벨 텍스트'
            },
            '영양성분표': {
                'calories': '350',
                'protein': '12',
                'fat': '15',
                'carbs': '45',
                'text': '영양성분 정보'
            }
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/dynamic-compliance-analysis", 
                               json=test_data, 
                               timeout=30)
        print(f"✅ 상태 코드: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 동적 분석 결과: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 오류: {response.text}")
    except Exception as e:
        print(f"❌ 요청 실패: {str(e)}")

def test_dashboard_stats():
    """대시보드 통계 테스트"""
    print("\n📊 대시보드 통계 테스트")
    
    try:
        response = requests.get(f"{BASE_URL}/api/dashboard-stats", timeout=10)
        print(f"✅ 상태 코드: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 대시보드 통계: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 오류: {response.text}")
    except Exception as e:
        print(f"❌ 요청 실패: {str(e)}")

def main():
    """메인 테스트 함수"""
    print("🚀 배포된 서버 API 테스트 시작")
    print("=" * 50)
    print(f"📡 서버 URL: {BASE_URL}")
    print(f"⏰ 테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 1. 서버 상태 확인
    test_health_check()
    
    # 2. 대시보드 통계
    test_dashboard_stats()
    
    # 3. 규제 상태 확인
    test_regulation_status()
    
    # 4. 규제 준수성 분석
    test_compliance_analysis()
    
    # 5. 동적 준수성 분석
    test_dynamic_compliance_analysis()
    
    print("\n" + "=" * 50)
    print("✅ 모든 테스트 완료")

if __name__ == "__main__":
    main() 