#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 키 설정 스크립트
"""

import os
import sys

def set_api_key():
    """API 키 설정"""
    
    print("🔑 KOTRA API 키 설정")
    print("=" * 40)
    
    # 현재 환경변수 확인
    current_key = os.getenv('KOTRA_SERVICE_KEY')
    if current_key:
        print(f"현재 설정된 API 키: {current_key[:10]}...")
        choice = input("새로운 API 키로 변경하시겠습니까? (y/n): ")
        if choice.lower() != 'y':
            print("API 키 설정을 취소했습니다.")
            return
    
    # API 키 입력
    print("\n📝 API 키를 입력해주세요:")
    print("(공공데이터포털에서 받은 서비스키를 입력하세요)")
    
    api_key = input("API 키: ").strip()
    
    if not api_key:
        print("❌ API 키가 입력되지 않았습니다.")
        return
    
    # 환경변수 설정
    os.environ['KOTRA_SERVICE_KEY'] = api_key
    
    print(f"\n✅ API 키가 설정되었습니다: {api_key[:10]}...")
    print("\n🔍 API 키 테스트를 실행합니다...")
    
    # API 키 테스트 실행
    try:
        from test_kotra_api import test_kotra_api_key
        test_kotra_api_key()
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류: {e}")

if __name__ == "__main__":
    set_api_key() 