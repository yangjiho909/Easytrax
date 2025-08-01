#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
배포된 서버 메인 페이지 테스트
- 실제 배포된 서버의 메인 페이지 확인
- 어떤 애플리케이션이 실행되고 있는지 확인
"""

import requests
import json
from datetime import datetime

# 배포된 서버 URL
BASE_URL = "https://kati-export-helper.onrender.com"

def test_main_page():
    """메인 페이지 확인"""
    print("🔍 메인 페이지 확인")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        print(f"✅ 상태 코드: {response.status_code}")
        print(f"✅ 응답 헤더: {dict(response.headers)}")
        
        if response.status_code == 200:
            content = response.text
            print(f"✅ 페이지 내용 (처음 500자):")
            print(content[:500])
            
            # HTML에서 제목이나 키워드 찾기
            if "KATI" in content:
                print("✅ KATI 애플리케이션 확인됨")
            elif "Flask" in content:
                print("✅ Flask 애플리케이션 확인됨")
            else:
                print("⚠️ 알 수 없는 애플리케이션")
        else:
            print(f"❌ 오류: {response.text}")
    except Exception as e:
        print(f"❌ 연결 실패: {str(e)}")

def test_dashboard_page():
    """대시보드 페이지 확인"""
    print("\n📊 대시보드 페이지 확인")
    
    try:
        response = requests.get(f"{BASE_URL}/dashboard", timeout=10)
        print(f"✅ 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            print(f"✅ 대시보드 내용 (처음 300자):")
            print(content[:300])
        else:
            print(f"❌ 오류: {response.text}")
    except Exception as e:
        print(f"❌ 연결 실패: {str(e)}")

def test_compliance_page():
    """준수성 분석 페이지 확인"""
    print("\n🤖 준수성 분석 페이지 확인")
    
    try:
        response = requests.get(f"{BASE_URL}/compliance-analysis", timeout=10)
        print(f"✅ 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            print(f"✅ 준수성 분석 페이지 내용 (처음 300자):")
            print(content[:300])
        else:
            print(f"❌ 오류: {response.text}")
    except Exception as e:
        print(f"❌ 연결 실패: {str(e)}")

def main():
    """메인 테스트 함수"""
    print("🚀 배포된 서버 메인 페이지 테스트")
    print("=" * 50)
    print(f"📡 서버 URL: {BASE_URL}")
    print(f"⏰ 테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # 1. 메인 페이지 확인
    test_main_page()
    
    # 2. 대시보드 페이지 확인
    test_dashboard_page()
    
    # 3. 준수성 분석 페이지 확인
    test_compliance_page()
    
    print("\n" + "=" * 50)
    print("✅ 모든 테스트 완료")

if __name__ == "__main__":
    main() 