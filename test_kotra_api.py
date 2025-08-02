#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KOTRA API 키 테스트 스크립트
"""

import os
import requests
import json
from datetime import datetime

def test_kotra_api_key():
    """KOTRA API 키 테스트"""
    
    # 환경변수에서 API 키 확인
    api_key = os.getenv('KOTRA_SERVICE_KEY')
    
    if not api_key:
        print("❌ KOTRA_SERVICE_KEY 환경변수가 설정되지 않았습니다.")
        print("\n🔧 환경변수 설정 방법:")
        print("Windows (PowerShell):")
        print("  $env:KOTRA_SERVICE_KEY = 'your_api_key_here'")
        print("\nWindows (CMD):")
        print("  set KOTRA_SERVICE_KEY=your_api_key_here")
        print("\nLinux/Mac:")
        print("  export KOTRA_SERVICE_KEY='your_api_key_here'")
        return False
    
    print(f"✅ API 키 확인됨: {api_key[:10]}...")
    
    # 1. 국가정보 API 테스트
    print("\n🔍 1. KOTRA 국가정보 API 테스트")
    print("-" * 50)
    
    try:
        # 중국 국가정보 조회
        url = "https://www.data.go.kr/data/15034830/openapi.do"
        params = {
            'serviceKey': api_key,
            'isoWd2CntCd': 'CN',  # 중국
            'type': 'json'
        }
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API 호출 성공!")
            print(f"   응답 데이터 크기: {len(str(data))} 문자")
            
            # 응답 구조 확인
            if 'response' in data:
                print("   응답 구조: response 객체 존재")
            else:
                print("   응답 구조: 직접 데이터")
                
        else:
            print(f"❌ API 호출 실패: {response.status_code}")
            print(f"   응답 내용: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ API 테스트 중 오류: {e}")
    
    # 2. 유망시장 수출입 통계 API 테스트
    print("\n🔍 2. 유망시장 수출입 통계 API 테스트")
    print("-" * 50)
    
    try:
        # 수출입 통계 조회
        url = "https://www.data.go.kr/data/15140440/fileData.do"
        params = {
            'serviceKey': api_key,
            'type': 'json'
        }
        
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API 호출 성공!")
            print(f"   응답 데이터 크기: {len(str(data))} 문자")
            
        else:
            print(f"❌ API 호출 실패: {response.status_code}")
            print(f"   응답 내용: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ API 테스트 중 오류: {e}")
    
    # 3. 기존 구현된 모듈 테스트
    print("\n🔍 3. 기존 구현 모듈 테스트")
    print("-" * 50)
    
    try:
        from kotra_regulation_api import KOTRARegulationAPI
        
        kotra_api = KOTRARegulationAPI()
        status = kotra_api.get_api_status()
        
        print("✅ KOTRA API 모듈 테스트 성공!")
        print(f"   API 상태: {status.get('status', 'unknown')}")
        
        # 중국 규정 조회 테스트
        china_reg = kotra_api.get_country_regulations("중국")
        if china_reg:
            print("✅ 중국 규정 조회 성공!")
        else:
            print("❌ 중국 규정 조회 실패")
            
    except Exception as e:
        print(f"❌ 기존 모듈 테스트 중 오류: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 API 키 테스트 완료!")
    print("=" * 60)

if __name__ == "__main__":
    test_kotra_api_key() 