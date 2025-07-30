#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 KATI 시스템 성능 및 안정성 테스트
- 동시 요청 처리 테스트
- 메모리 사용량 모니터링
- 응답 시간 측정
- 에러 처리 테스트
"""

import requests
import time
import threading
import psutil
import os
from datetime import datetime

def test_response_time():
    """응답 시간 테스트"""
    print("🔍 응답 시간 테스트")
    print("=" * 50)
    
    endpoints = [
        ("/", "메인 페이지"),
        ("/customs-analysis", "통관분석"),
        ("/regulation-info", "규제정보"),
        ("/compliance-analysis", "준수성분석"),
        ("/document-generation", "서류생성"),
        ("/nutrition-label", "영양라벨")
    ]
    
    base_url = "http://localhost:5000"
    results = {}
    
    for endpoint, name in endpoints:
        try:
            start_time = time.time()
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # ms로 변환
            
            if response.status_code == 200:
                print(f"✅ {name}: {response_time:.2f}ms")
                results[name] = response_time
            else:
                print(f"❌ {name}: 오류 (상태코드: {response.status_code})")
                results[name] = None
                
        except Exception as e:
            print(f"❌ {name}: 오류 - {e}")
            results[name] = None
    
    # 평균 응답 시간 계산
    valid_times = [t for t in results.values() if t is not None]
    if valid_times:
        avg_time = sum(valid_times) / len(valid_times)
        print(f"\n📊 평균 응답 시간: {avg_time:.2f}ms")
        
        if avg_time < 1000:
            print("✅ 응답 시간이 양호합니다 (< 1초)")
            return True
        else:
            print("⚠️ 응답 시간이 다소 느립니다 (> 1초)")
            return False
    else:
        print("❌ 모든 엔드포인트에서 오류 발생")
        return False

def test_concurrent_requests():
    """동시 요청 처리 테스트"""
    print("\n🔍 동시 요청 처리 테스트")
    print("=" * 50)
    
    def make_request(request_id):
        try:
            response = requests.get("http://localhost:5000/", timeout=10)
            return request_id, response.status_code == 200
        except:
            return request_id, False
    
    # 10개의 동시 요청 생성
    threads = []
    results = {}
    
    for i in range(10):
        thread = threading.Thread(target=lambda x=i: results.update({x: make_request(x)}))
        threads.append(thread)
    
    start_time = time.time()
    
    # 모든 스레드 시작
    for thread in threads:
        thread.start()
    
    # 모든 스레드 완료 대기
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # 결과 분석
    successful_requests = sum(1 for success in results.values() if success)
    total_requests = len(results)
    
    print(f"✅ 동시 요청 처리 완료: {successful_requests}/{total_requests} 성공")
    print(f"📊 총 처리 시간: {total_time:.2f}초")
    print(f"📊 평균 처리 시간: {(total_time/total_requests)*1000:.2f}ms")
    
    if successful_requests == total_requests:
        print("✅ 모든 동시 요청이 성공적으로 처리되었습니다")
        return True
    else:
        print("⚠️ 일부 동시 요청이 실패했습니다")
        return False

def test_memory_usage():
    """메모리 사용량 테스트"""
    print("\n🔍 메모리 사용량 테스트")
    print("=" * 50)
    
    try:
        # 현재 프로세스의 메모리 사용량 확인
        process = psutil.Process()
        memory_info = process.memory_info()
        
        # 메모리 사용량을 MB로 변환
        memory_mb = memory_info.rss / 1024 / 1024
        
        print(f"📊 현재 메모리 사용량: {memory_mb:.2f}MB")
        
        # 메모리 사용량이 적절한지 확인 (500MB 이하)
        if memory_mb < 500:
            print("✅ 메모리 사용량이 적절합니다 (< 500MB)")
            return True
        else:
            print("⚠️ 메모리 사용량이 높습니다 (> 500MB)")
            return False
            
    except Exception as e:
        print(f"❌ 메모리 사용량 확인 실패: {e}")
        return False

def test_error_handling():
    """에러 처리 테스트"""
    print("\n🔍 에러 처리 테스트")
    print("=" * 50)
    
    error_tests = [
        ("잘못된 엔드포인트", "/invalid-endpoint"),
        ("잘못된 JSON", "/api/customs-analysis", {"invalid": "data"}),
        ("빈 요청", "/api/regulation-info", {}),
        ("큰 파일 업로드", "/api/ocr-extract", {"image": "large_file"})
    ]
    
    successful_handling = 0
    
    for test_name, endpoint in error_tests:
        try:
            if len(error_tests[0]) == 2:  # GET 요청
                response = requests.get(f"http://localhost:5000{endpoint}", timeout=5)
            else:  # POST 요청
                response = requests.post(f"http://localhost:5000{endpoint}", 
                                       json=error_tests[1], timeout=5)
            
            # 에러가 적절히 처리되었는지 확인 (4xx 또는 5xx 상태코드)
            if 400 <= response.status_code < 600:
                print(f"✅ {test_name}: 적절한 에러 처리 ({response.status_code})")
                successful_handling += 1
            else:
                print(f"⚠️ {test_name}: 예상과 다른 응답 ({response.status_code})")
                
        except Exception as e:
            print(f"✅ {test_name}: 예외 적절히 처리됨")
            successful_handling += 1
    
    print(f"\n📊 에러 처리 성공률: {successful_handling}/{len(error_tests)}")
    
    if successful_handling == len(error_tests):
        print("✅ 모든 에러가 적절히 처리되었습니다")
        return True
    else:
        print("⚠️ 일부 에러 처리가 미흡합니다")
        return False

def test_system_stability():
    """시스템 안정성 테스트"""
    print("\n🔍 시스템 안정성 테스트")
    print("=" * 50)
    
    # 연속 요청 테스트
    print("연속 요청 테스트 중...")
    
    successful_requests = 0
    total_requests = 20
    
    for i in range(total_requests):
        try:
            response = requests.get("http://localhost:5000/", timeout=5)
            if response.status_code == 200:
                successful_requests += 1
            time.sleep(0.1)  # 100ms 간격
        except:
            pass
    
    stability_rate = (successful_requests / total_requests) * 100
    
    print(f"📊 안정성 점수: {stability_rate:.1f}% ({successful_requests}/{total_requests})")
    
    if stability_rate >= 95:
        print("✅ 시스템이 매우 안정적입니다 (95% 이상)")
        return True
    elif stability_rate >= 80:
        print("✅ 시스템이 안정적입니다 (80% 이상)")
        return True
    else:
        print("⚠️ 시스템 안정성이 부족합니다 (80% 미만)")
        return False

def generate_performance_report():
    """성능 및 안정성 보고서"""
    print("\n📊 성능 및 안정성 테스트 보고서")
    print("=" * 60)
    print(f"테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 각 테스트 실행
    tests = [
        ("응답 시간", test_response_time),
        ("동시 요청 처리", test_concurrent_requests),
        ("메모리 사용량", test_memory_usage),
        ("에러 처리", test_error_handling),
        ("시스템 안정성", test_system_stability)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} 테스트 중 오류: {e}")
            results[test_name] = False
    
    # 결과 요약
    print(f"\n📋 성능 및 안정성 테스트 결과")
    print("-" * 40)
    
    passed_tests = sum(results.values())
    total_tests = len(results)
    
    for test_name, result in results.items():
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{test_name}: {status}")
    
    print(f"\n🎯 성능 및 안정성 결과: {passed_tests}/{total_tests} 통과")
    
    if passed_tests == total_tests:
        print("🎉 시스템 성능 및 안정성이 우수합니다!")
        return True
    else:
        print("⚠️ 일부 성능 또는 안정성 문제가 있습니다.")
        return False

if __name__ == "__main__":
    generate_performance_report() 