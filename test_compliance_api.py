#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import os
from datetime import datetime

def test_compliance_api():
    """준수성 분석 API 테스트"""
    
    # 테스트용 서버 URL (로컬 테스트)
    base_url = "http://localhost:5000"
    
    # 테스트 케이스들
    test_cases = [
        {
            "name": "기본 분석 (문서 없음)",
            "data": {
                "country": "중국",
                "product_type": "식품",
                "use_ocr": False,
                "company_info": {"name": "테스트 회사"},
                "product_info": {"name": "테스트 라면"}
            },
            "expected_status": 200
        },
        {
            "name": "JSON 형식 테스트",
            "data": {
                "country": "미국",
                "product_type": "식품",
                "use_ocr": True,
                "company_info": {"name": "Test Company"},
                "product_info": {"name": "Test Noodles"}
            },
            "expected_status": 200
        },
        {
            "name": "빈 국가 테스트",
            "data": {
                "country": "",
                "product_type": "식품",
                "use_ocr": False
            },
            "expected_status": 400  # 국가가 없으면 오류
        },
        {
            "name": "잘못된 JSON 테스트",
            "data": "invalid json",
            "expected_status": 400
        }
    ]
    
    print("=" * 80)
    print("준수성 분석 API 테스트 결과")
    print("=" * 80)
    
    success_count = 0
    total_count = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. 테스트: {test_case['name']}")
        print(f"   기대 상태: {test_case['expected_status']}")
        
        try:
            # API 호출
            if isinstance(test_case['data'], dict):
                response = requests.post(
                    f"{base_url}/api/compliance-analysis",
                    json=test_case['data'],
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
            else:
                response = requests.post(
                    f"{base_url}/api/compliance-analysis",
                    data=test_case['data'],
                    timeout=30
                )
            
            # 결과 확인
            if response.status_code == test_case['expected_status']:
                print(f"   결과: ✅ 성공 (상태 코드: {response.status_code})")
                success_count += 1
                
                # 응답 내용 확인
                try:
                    response_data = response.json()
                    if 'success' in response_data:
                        print(f"   성공 여부: {response_data['success']}")
                    if 'message' in response_data:
                        print(f"   메시지: {response_data['message'][:50]}...")
                    if 'analysis_summary' in response_data:
                        summary = response_data['analysis_summary']
                        print(f"   준수성 점수: {summary.get('compliance_score', 'N/A')}")
                except:
                    print(f"   응답 파싱 실패: {response.text[:100]}...")
            else:
                print(f"   결과: ❌ 실패 (상태 코드: {response.status_code}, 기대: {test_case['expected_status']})")
                print(f"   응답: {response.text[:100]}...")
                
        except requests.exceptions.ConnectionError:
            print(f"   결과: ❌ 연결 실패 (서버가 실행 중인지 확인하세요)")
        except requests.exceptions.Timeout:
            print(f"   결과: ❌ 타임아웃 (30초 초과)")
        except Exception as e:
            print(f"   결과: ❌ 오류 발생: {str(e)}")
    
    print("\n" + "=" * 80)
    print(f"테스트 결과: {success_count}/{total_count} 성공 ({success_count/total_count*100:.1f}%)")
    print("=" * 80)
    
    # 성공률 분석
    if success_count/total_count >= 0.75:
        print("🎉 준수성 분석 API가 안정적으로 작동합니다!")
    elif success_count/total_count >= 0.5:
        print("⚠️ 준수성 분석 API가 부분적으로 작동합니다. 일부 기능을 확인해주세요.")
    else:
        print("❌ 준수성 분석 API에 문제가 있습니다. 수정이 필요합니다.")

def test_file_upload():
    """파일 업로드 테스트 (실제 파일이 있는 경우)"""
    print("\n" + "=" * 80)
    print("파일 업로드 테스트")
    print("=" * 80)
    
    # 테스트용 이미지 파일 경로들
    test_files = [
        "test_label.jpg",
        "test_nutrition.png",
        "test_ingredient.pdf"
    ]
    
    base_url = "http://localhost:5000"
    
    for file_name in test_files:
        if os.path.exists(file_name):
            print(f"\n📁 파일 업로드 테스트: {file_name}")
            
            try:
                with open(file_name, 'rb') as f:
                    files = {
                        'labelFile': (file_name, f, 'image/jpeg')
                    }
                    
                    data = {
                        'country': '중국',
                        'product_type': '식품',
                        'use_ocr': 'true'
                    }
                    
                    response = requests.post(
                        f"{base_url}/api/compliance-analysis",
                        data=data,
                        files=files,
                        timeout=60
                    )
                
                if response.status_code == 200:
                    print(f"   결과: ✅ 성공 (파일 업로드 및 분석 완료)")
                    try:
                        response_data = response.json()
                        if 'analysis_summary' in response_data:
                            summary = response_data['analysis_summary']
                            print(f"   분석된 문서 수: {summary.get('total_documents', 0)}")
                            print(f"   준수성 점수: {summary.get('compliance_score', 'N/A')}")
                    except:
                        pass
                else:
                    print(f"   결과: ❌ 실패 (상태 코드: {response.status_code})")
                    
            except Exception as e:
                print(f"   결과: ❌ 오류: {str(e)}")
        else:
            print(f"\n📁 파일 없음: {file_name} (테스트 스킵)")

def test_error_handling():
    """오류 처리 테스트"""
    print("\n" + "=" * 80)
    print("오류 처리 테스트")
    print("=" * 80)
    
    base_url = "http://localhost:5000"
    
    # 잘못된 요청 테스트
    error_tests = [
        {
            "name": "잘못된 Content-Type",
            "headers": {"Content-Type": "text/plain"},
            "data": "invalid data"
        },
        {
            "name": "빈 요청",
            "headers": {},
            "data": {}
        }
    ]
    
    for test in error_tests:
        print(f"\n🔍 {test['name']}")
        
        try:
            response = requests.post(
                f"{base_url}/api/compliance-analysis",
                headers=test.get('headers', {}),
                data=test['data'],
                timeout=10
            )
            
            print(f"   상태 코드: {response.status_code}")
            print(f"   응답: {response.text[:100]}...")
            
        except Exception as e:
            print(f"   오류: {str(e)}")

if __name__ == "__main__":
    print("준수성 분석 API 테스트 시작...")
    print("서버가 실행 중인지 확인하세요: python app.py")
    print()
    
    # 기본 API 테스트
    test_compliance_api()
    
    # 파일 업로드 테스트
    test_file_upload()
    
    # 오류 처리 테스트
    test_error_handling()
    
    print("\n" + "=" * 80)
    print("테스트 완료!")
    print("=" * 80) 