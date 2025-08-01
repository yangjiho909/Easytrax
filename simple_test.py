#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time

def test_compliance_api():
    """간단한 준수성 분석 API 테스트"""
    
    print("준수성 분석 API 테스트 시작...")
    
    # 테스트 데이터
    test_data = {
        "country": "중국",
        "product_type": "식품",
        "use_ocr": False,
        "company_info": {"name": "테스트 회사"},
        "product_info": {"name": "테스트 라면"}
    }
    
    try:
        print("API 호출 중...")
        response = requests.post(
            "http://localhost:5000/api/compliance-analysis",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API 호출 성공!")
            
            try:
                data = response.json()
                print(f"응답 키: {list(data.keys())}")
                
                if 'success' in data:
                    print(f"성공 여부: {data['success']}")
                
                if 'message' in data:
                    print(f"메시지: {data['message']}")
                
                if 'analysis_summary' in data:
                    summary = data['analysis_summary']
                    print(f"준수성 점수: {summary.get('compliance_score', 'N/A')}")
                    print(f"분석된 문서 수: {summary.get('total_documents', 0)}")
                
                if 'compliance_analysis' in data:
                    analysis = data['compliance_analysis']
                    print(f"전체 점수: {analysis.get('overall_score', 'N/A')}")
                    print(f"중요 이슈: {len(analysis.get('critical_issues', []))}개")
                    print(f"주요 이슈: {len(analysis.get('major_issues', []))}개")
                
                print("🎉 준수성 분석 API가 정상적으로 작동합니다!")
                return True
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON 파싱 오류: {e}")
                print(f"응답 내용: {response.text[:200]}...")
                return False
                
        else:
            print(f"❌ API 호출 실패 (상태 코드: {response.status_code})")
            print(f"응답 내용: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 연결 실패 - 서버가 실행 중인지 확인하세요")
        print("서버 실행 명령어: python app.py")
        return False
        
    except requests.exceptions.Timeout:
        print("❌ 타임아웃 - 서버 응답이 너무 느립니다")
        return False
        
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {str(e)}")
        return False

def test_error_cases():
    """오류 케이스 테스트"""
    print("\n" + "="*50)
    print("오류 케이스 테스트")
    print("="*50)
    
    # 빈 국가 테스트
    print("\n1. 빈 국가 테스트")
    try:
        response = requests.post(
            "http://localhost:5000/api/compliance-analysis",
            json={"country": "", "product_type": "식품"},
            timeout=10
        )
        print(f"상태 코드: {response.status_code}")
        print(f"응답 내용: {response.text[:200]}...")
        if response.status_code == 400:
            print("✅ 올바른 오류 응답")
        else:
            print("❌ 예상과 다른 응답")
    except Exception as e:
        print(f"❌ 오류: {e}")
    
    # 잘못된 JSON 테스트
    print("\n2. 잘못된 JSON 테스트")
    try:
        response = requests.post(
            "http://localhost:5000/api/compliance-analysis",
            data="invalid json",
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        print(f"상태 코드: {response.status_code}")
        print(f"응답 내용: {response.text[:200]}...")
        if response.status_code == 400:
            print("✅ 올바른 오류 응답")
        else:
            print("❌ 예상과 다른 응답")
    except Exception as e:
        print(f"❌ 오류: {e}")

if __name__ == "__main__":
    print("="*60)
    print("준수성 분석 API 자동 테스트")
    print("="*60)
    
    # 기본 테스트
    success = test_compliance_api()
    
    # 오류 케이스 테스트
    if success:
        test_error_cases()
    
    print("\n" + "="*60)
    print("테스트 완료!")
    print("="*60) 