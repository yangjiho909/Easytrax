#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
라벨 생성 API 직접 테스트 스크립트
"""

import requests
import json
import time

def test_nutrition_label_api():
    """영양성분표 라벨 생성 API 테스트"""
    print("🔍 영양성분표 라벨 생성 API 테스트...")
    
    # 테스트 데이터
    test_data = {
        "country": "중국",
        "product_info": {
            "name": "테스트 제품",
            "nutrition": {
                "calories": "400",
                "protein": "12",
                "fat": "15",
                "carbs": "60",
                "sodium": "800",
                "sugar": "10",
                "fiber": "5",
                "serving_size": "100"
            },
            "allergies": ["우유", "계란"],
            "manufacturer": "테스트 제조사",
            "ingredients": "밀가루, 설탕, 소금",
            "expiry_date": "2025-12-31",
            "storage_info": "서늘한 곳에 보관",
            "net_weight": "500g"
        }
    }
    
    try:
        # API 호출
        url = "http://localhost:5000/api/nutrition-label"
        headers = {"Content-Type": "application/json"}
        
        print(f"📡 API 요청 전송: {url}")
        print(f"📋 요청 데이터: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
        
        response = requests.post(url, json=test_data, headers=headers, timeout=30)
        
        print(f"📊 응답 상태 코드: {response.status_code}")
        print(f"📊 응답 헤더: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API 응답 성공:")
            print(f"   - 성공 여부: {result.get('success', False)}")
            print(f"   - 라벨 데이터: {result.get('label_data', {}).get('filename', 'N/A')}")
            print(f"   - 국가: {result.get('label_data', {}).get('country', 'N/A')}")
            print(f"   - 라벨 타입: {result.get('label_data', {}).get('label_type', 'N/A')}")
            
            if result.get('success'):
                print("🎉 라벨 생성 성공!")
                return True
            else:
                print(f"❌ 라벨 생성 실패: {result.get('error', '알 수 없는 오류')}")
                return False
        else:
            print(f"❌ HTTP 오류: {response.status_code}")
            print(f"❌ 응답 내용: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 서버 연결 실패. Flask 앱이 실행 중인지 확인하세요.")
        return False
    except requests.exceptions.Timeout:
        print("❌ 요청 시간 초과")
        return False
    except Exception as e:
        print(f"❌ API 테스트 중 오류 발생: {e}")
        return False

def test_us_label_api():
    """미국 라벨 생성 API 테스트"""
    print("\n🔍 미국 라벨 생성 API 테스트...")
    
    # 테스트 데이터
    test_data = {
        "country": "미국",
        "product_info": {
            "name": "Test Product",
            "nutrition": {
                "calories": "350",
                "protein": "10",
                "fat": "12",
                "carbs": "55",
                "sodium": "600",
                "sugar": "8",
                "fiber": "3",
                "serving_size": "100"
            },
            "allergies": ["Milk", "Eggs"],
            "manufacturer": "Test Manufacturer",
            "ingredients": "Flour, Sugar, Salt",
            "expiry_date": "2025-12-31",
            "storage_info": "Store in cool place",
            "net_weight": "500g"
        }
    }
    
    try:
        # API 호출
        url = "http://localhost:5000/api/nutrition-label"
        headers = {"Content-Type": "application/json"}
        
        print(f"📡 API 요청 전송: {url}")
        print(f"📋 요청 데이터: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
        
        response = requests.post(url, json=test_data, headers=headers, timeout=30)
        
        print(f"📊 응답 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API 응답 성공:")
            print(f"   - 성공 여부: {result.get('success', False)}")
            print(f"   - 라벨 데이터: {result.get('label_data', {}).get('filename', 'N/A')}")
            print(f"   - 국가: {result.get('label_data', {}).get('country', 'N/A')}")
            print(f"   - 라벨 타입: {result.get('label_data', {}).get('label_type', 'N/A')}")
            
            if result.get('success'):
                print("🎉 미국 라벨 생성 성공!")
                return True
            else:
                print(f"❌ 미국 라벨 생성 실패: {result.get('error', '알 수 없는 오류')}")
                return False
        else:
            print(f"❌ HTTP 오류: {response.status_code}")
            print(f"❌ 응답 내용: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 서버 연결 실패. Flask 앱이 실행 중인지 확인하세요.")
        return False
    except requests.exceptions.Timeout:
        print("❌ 요청 시간 초과")
        return False
    except Exception as e:
        print(f"❌ API 테스트 중 오류 발생: {e}")
        return False

def test_error_handling():
    """오류 처리 테스트"""
    print("\n🔍 오류 처리 테스트...")
    
    # 잘못된 데이터로 테스트
    invalid_data = {
        "country": "존재하지않는국가",
        "product_info": {}
    }
    
    try:
        url = "http://localhost:5000/api/nutrition-label"
        headers = {"Content-Type": "application/json"}
        
        print(f"📡 잘못된 데이터로 API 요청 전송...")
        
        response = requests.post(url, json=invalid_data, headers=headers, timeout=30)
        
        print(f"📊 응답 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 오류 처리 응답:")
            print(f"   - 성공 여부: {result.get('success', False)}")
            print(f"   - 오류 메시지: {result.get('error', 'N/A')}")
            
            if not result.get('success'):
                print("✅ 오류 처리 정상 작동!")
                return True
            else:
                print("⚠️ 오류 상황에서도 성공으로 처리됨")
                return False
        else:
            print(f"❌ HTTP 오류: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 오류 처리 테스트 중 예외 발생: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("🚀 라벨 생성 API 테스트 시작")
    print("=" * 60)
    
    # Flask 앱이 실행 중인지 확인
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        print("✅ Flask 앱이 실행 중입니다.")
    except:
        print("❌ Flask 앱이 실행되지 않았습니다.")
        print("🔧 Flask 앱을 먼저 실행하세요: python app.py")
        return
    
    tests = [
        ("중국 라벨 생성", test_nutrition_label_api),
        ("미국 라벨 생성", test_us_label_api),
        ("오류 처리", test_error_handling)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name} 테스트 시작...")
        try:
            result = test_func()
            results.append((test_name, result))
            time.sleep(1)  # API 호출 간격
        except Exception as e:
            print(f"❌ {test_name} 테스트 중 예외 발생: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 API 테스트 결과 요약")
    print("=" * 60)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 모든 API 테스트 통과! 라벨 생성 API가 정상 작동합니다.")
    else:
        print("⚠️ 일부 API 테스트 실패. 라벨 생성 API에 문제가 있을 수 있습니다.")
        print("\n🔧 해결 방법:")
        print("1. Flask 앱 로그 확인: 서버 콘솔에서 오류 메시지 확인")
        print("2. 라벨 생성 함수 디버깅: generate_label 함수 내부 오류 확인")
        print("3. 폰트 파일 경로 확인: fonts/ 폴더의 폰트 파일들 확인")
        print("4. 디렉토리 권한 확인: advanced_labels/ 폴더 쓰기 권한 확인")

if __name__ == "__main__":
    main() 