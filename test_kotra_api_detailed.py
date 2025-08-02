#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KOTRA API 상세 테스트 스크립트
"""

import os
import requests
import json
from datetime import datetime

def test_kotra_api_detailed():
    """KOTRA API 상세 테스트"""
    
    # 환경변수에서 API 키 확인
    api_key = os.getenv('KOTRA_SERVICE_KEY')
    
    if not api_key:
        print("❌ KOTRA_SERVICE_KEY 환경변수가 설정되지 않았습니다.")
        return False
    
    print(f"✅ API 키 확인됨: {api_key[:10]}...")
    
    # 1. 실제 엔드포인트로 테스트
    print("\n🔍 1. 실제 KOTRA API 엔드포인트 테스트")
    print("-" * 60)
    
    try:
        # 실제 엔드포인트 사용
        url = "https://apis.data.go.kr/B410001/kotra_nationalInformation/natnInfo"
        params = {
            'serviceKey': api_key,
            'isoWd2CntCd': 'CN',  # 중국
            'type': 'json'
        }
        
        print(f"📡 API 호출 URL: {url}")
        print(f"📋 파라미터: {params}")
        
        response = requests.get(url, params=params, timeout=30)
        
        print(f"📊 응답 상태 코드: {response.status_code}")
        print(f"📄 응답 헤더: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ API 호출 성공!")
            print(f"📏 응답 크기: {len(response.text)} 문자")
            
            # 응답 내용 확인
            print(f"\n📝 응답 내용 (처음 500자):")
            print("-" * 40)
            print(response.text[:500])
            print("-" * 40)
            
            # JSON 파싱 시도
            try:
                data = response.json()
                print("✅ JSON 파싱 성공!")
                print(f"📊 JSON 구조: {type(data)}")
                if isinstance(data, dict):
                    print(f"🔑 최상위 키: {list(data.keys())}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON 파싱 실패: {e}")
                print("📄 응답이 JSON 형식이 아닐 수 있습니다.")
                
        else:
            print(f"❌ API 호출 실패: {response.status_code}")
            print(f"📄 응답 내용: {response.text}")
            
    except Exception as e:
        print(f"❌ API 테스트 중 오류: {e}")
    
    # 2. 기존 URL로도 테스트
    print("\n🔍 2. 기존 URL 테스트")
    print("-" * 60)
    
    try:
        url = "https://www.data.go.kr/data/15034830/openapi.do"
        params = {
            'serviceKey': api_key,
            'isoWd2CntCd': 'CN',
            'type': 'json'
        }
        
        response = requests.get(url, params=params, timeout=30)
        
        print(f"📊 응답 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API 호출 성공!")
            print(f"📏 응답 크기: {len(response.text)} 문자")
            print(f"📝 응답 내용 (처음 300자):")
            print("-" * 40)
            print(response.text[:300])
            print("-" * 40)
        else:
            print(f"❌ API 호출 실패: {response.status_code}")
            
    except Exception as e:
        print(f"❌ API 테스트 중 오류: {e}")
    
    # 3. XML 형식으로 테스트
    print("\n🔍 3. XML 형식 테스트")
    print("-" * 60)
    
    try:
        url = "https://apis.data.go.kr/B410001/kotra_nationalInformation/natnInfo"
        params = {
            'serviceKey': api_key,
            'isoWd2CntCd': 'CN',
            'type': 'xml'
        }
        
        response = requests.get(url, params=params, timeout=30)
        
        print(f"📊 응답 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ XML API 호출 성공!")
            print(f"📏 응답 크기: {len(response.text)} 문자")
            print(f"📝 응답 내용 (처음 300자):")
            print("-" * 40)
            print(response.text[:300])
            print("-" * 40)
        else:
            print(f"❌ XML API 호출 실패: {response.status_code}")
            
    except Exception as e:
        print(f"❌ XML API 테스트 중 오류: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 상세 API 테스트 완료!")
    print("=" * 60)

if __name__ == "__main__":
    test_kotra_api_detailed() 