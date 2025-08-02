#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KOTRA API 수정된 테스트 스크립트
"""

import os
import requests
import json
import urllib3
from datetime import datetime

# SSL 경고 무시 (개발 환경에서만 사용)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_kotra_api_fixed():
    """KOTRA API 수정된 테스트"""
    
    # 환경변수에서 API 키 확인
    api_key = os.getenv('KOTRA_SERVICE_KEY')
    
    if not api_key:
        print("❌ KOTRA_SERVICE_KEY 환경변수가 설정되지 않았습니다.")
        return False
    
    print(f"✅ API 키 확인됨: {api_key[:10]}...")
    
    # 1. 공공데이터포털 표준 API 엔드포인트 테스트
    print("\n🔍 1. 공공데이터포털 표준 API 테스트")
    print("-" * 60)
    
    try:
        # 공공데이터포털 표준 엔드포인트
        url = "https://apis.data.go.kr/B410001/kotra_nationalInformation/natnInfo"
        params = {
            'serviceKey': api_key,
            'isoWd2CntCd': 'CN',  # 중국
            'type': 'json'
        }
        
        print(f"📡 API 호출 URL: {url}")
        
        # SSL 검증 비활성화로 테스트
        response = requests.get(url, params=params, timeout=30, verify=False)
        
        print(f"📊 응답 상태 코드: {response.status_code}")
        
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
                    # 데이터 구조 출력
                    print(f"📋 데이터 구조:")
                    for key, value in data.items():
                        if isinstance(value, dict):
                            print(f"   {key}: {list(value.keys())}")
                        elif isinstance(value, list):
                            print(f"   {key}: 리스트 ({len(value)}개 항목)")
                        else:
                            print(f"   {key}: {type(value)}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON 파싱 실패: {e}")
                
        else:
            print(f"❌ API 호출 실패: {response.status_code}")
            print(f"📄 응답 내용: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ API 테스트 중 오류: {e}")
    
    # 2. 다른 가능한 엔드포인트 테스트
    print("\n🔍 2. 대체 엔드포인트 테스트")
    print("-" * 60)
    
    alternative_urls = [
        "https://apis.data.go.kr/B410001/kotra_nationalInformation/natnInfo",
        "https://www.data.go.kr/data/15034830/openapi.do",
        "https://apis.data.go.kr/B410001/kotra_nationalInformation",
        "https://www.data.go.kr/data/15034830/openapi"
    ]
    
    for i, url in enumerate(alternative_urls, 1):
        try:
            print(f"\n📡 테스트 {i}: {url}")
            
            params = {
                'serviceKey': api_key,
                'isoWd2CntCd': 'CN',
                'type': 'json'
            }
            
            response = requests.get(url, params=params, timeout=30, verify=False)
            
            print(f"   📊 상태 코드: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ 성공! 응답 크기: {len(response.text)} 문자")
                
                # JSON인지 확인
                try:
                    data = response.json()
                    print(f"   ✅ JSON 형식 확인됨")
                    if isinstance(data, dict):
                        print(f"   🔑 키: {list(data.keys())}")
                except:
                    print(f"   ❌ JSON 형식 아님 (HTML 또는 다른 형식)")
                    
            else:
                print(f"   ❌ 실패: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 오류: {e}")
    
    # 3. XML 형식 테스트
    print("\n🔍 3. XML 형식 테스트")
    print("-" * 60)
    
    try:
        url = "https://apis.data.go.kr/B410001/kotra_nationalInformation/natnInfo"
        params = {
            'serviceKey': api_key,
            'isoWd2CntCd': 'CN',
            'type': 'xml'
        }
        
        response = requests.get(url, params=params, timeout=30, verify=False)
        
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
    print("🎯 수정된 API 테스트 완료!")
    print("=" * 60)

if __name__ == "__main__":
    test_kotra_api_fixed() 