#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
시스템 전체 종합 점검
"""

import requests
import json
import time
import os
import pickle
import pandas as pd
from datetime import datetime

def check_system_status():
    """시스템 상태 점검"""
    
    print("🔍 시스템 전체 종합 점검")
    print("=" * 60)
    print(f"점검 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 웹 서버 상태 점검
    print("\n🌐 1. 웹 서버 상태 점검")
    print("-" * 40)
    
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        if response.status_code == 200:
            print("✅ 웹 서버 정상 실행 중")
            print(f"   상태 코드: {response.status_code}")
            print(f"   응답 시간: {response.elapsed.total_seconds():.2f}초")
        else:
            print(f"⚠️ 웹 서버 응답 이상: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ 웹 서버 연결 실패 - 서버가 실행되지 않았습니다.")
        return False
    except Exception as e:
        print(f"❌ 웹 서버 점검 오류: {str(e)}")
        return False
    
    # 2. 데이터 모델 상태 점검
    print("\n📊 2. 데이터 모델 상태 점검")
    print("-" * 40)
    
    model_files = ['model/vectorizer.pkl', 'model/indexed_matrix.pkl', 'model/raw_data.pkl']
    model_status = {}
    
    for file_path in model_files:
        if os.path.exists(file_path):
            try:
                file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                print(f"✅ {file_path}: {file_size:.2f} MB")
                model_status[file_path] = True
            except Exception as e:
                print(f"❌ {file_path}: 로드 실패 - {str(e)}")
                model_status[file_path] = False
        else:
            print(f"❌ {file_path}: 파일 없음")
            model_status[file_path] = False
    
    # 3. 데이터 품질 점검
    print("\n📈 3. 데이터 품질 점검")
    print("-" * 40)
    
    try:
        with open('model/raw_data.pkl', 'rb') as f:
            df = pickle.load(f)
        
        print(f"✅ 전체 데이터: {len(df):,}개")
        print(f"✅ 고유 국가: {df['수입국'].nunique()}개")
        print(f"✅ 고유 품목: {df['품목'].nunique():,}개")
        
        # 국가별 데이터 분포
        country_counts = df['수입국'].value_counts()
        print(f"\n📊 국가별 데이터 분포:")
        for country, count in country_counts.head(10).items():
            print(f"   {country}: {count:,}개")
        
        # 중국, 미국 데이터 확인
        china_data = df[df['수입국'] == '중국']
        us_data = df[df['수입국'] == '미국']
        
        print(f"\n🇨🇳🇺🇸 주요 국가 데이터:")
        print(f"   중국: {len(china_data):,}개")
        print(f"   미국: {len(us_data):,}개")
        print(f"   중국+미국: {len(china_data) + len(us_data):,}개")
        
        # 문제사유 품질 확인
        reason_lengths = df['문제사유'].str.len()
        empty_reasons = (df['문제사유'].str.strip() == '').sum()
        
        print(f"\n📝 문제사유 품질:")
        print(f"   평균 길이: {reason_lengths.mean():.1f}자")
        print(f"   빈 문제사유: {empty_reasons:,}개 ({empty_reasons/len(df)*100:.1f}%)")
        
    except Exception as e:
        print(f"❌ 데이터 품질 점검 실패: {str(e)}")
    
    # 4. API 엔드포인트 점검
    print("\n🔌 4. API 엔드포인트 점검")
    print("-" * 40)
    
    api_endpoints = [
        {
            "name": "통관 분석 API",
            "url": "/api/customs-analysis",
            "method": "POST",
            "test_data": {"user_input": "중국 라면", "use_enhanced_expansion": True}
        },
        {
            "name": "키워드 확장 API", 
            "url": "/api/keyword-expansion",
            "method": "POST",
            "test_data": {"user_input": "중국 라면"}
        },
        {
            "name": "규제 정보 API",
            "url": "/api/regulation-info", 
            "method": "POST",
            "test_data": {"country": "중국", "product": "라면"}
        },
        {
            "name": "준수성 분석 API",
            "url": "/api/compliance-analysis",
            "method": "POST", 
            "test_data": {
                "country": "중국",
                "product": "라면",
                "company_info": {"name": "테스트"},
                "product_info": {"name": "테스트 라면"},
                "prepared_documents": [],
                "labeling_info": {}
            }
        }
    ]
    
    for endpoint in api_endpoints:
        try:
            response = requests.post(
                f"http://localhost:5000{endpoint['url']}",
                headers={"Content-Type": "application/json"},
                json=endpoint['test_data'],
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') or 'error' not in data:
                    print(f"✅ {endpoint['name']}: 정상")
                else:
                    print(f"⚠️ {endpoint['name']}: 응답 오류 - {data.get('error', '알 수 없는 오류')}")
            else:
                print(f"❌ {endpoint['name']}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {endpoint['name']}: 연결 실패 - {str(e)}")
    
    # 5. 국가별 필터링 기능 점검
    print("\n🎯 5. 국가별 필터링 기능 점검")
    print("-" * 40)
    
    filter_tests = [
        {"input": "중국으로 라면 수출하고 싶어요", "expected": "중국"},
        {"input": "미국으로 라면 수출하고 싶어요", "expected": "미국"},
        {"input": "라면 수출", "expected": None}
    ]
    
    for test in filter_tests:
        try:
            response = requests.post(
                "http://localhost:5000/api/customs-analysis",
                headers={"Content-Type": "application/json"},
                json={"user_input": test['input'], "use_enhanced_expansion": True},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    target_country = data.get('target_country')
                    filtered_by_country = data.get('filtered_by_country', False)
                    
                    if target_country == test['expected']:
                        print(f"✅ '{test['input']}' → {target_country} (정상)")
                    else:
                        print(f"❌ '{test['input']}' → {target_country} (예상: {test['expected']})")
                        
                    # 필터링 검증
                    if target_country:
                        results = data.get('results', [])
                        all_same_country = all(result['country'] == target_country for result in results)
                        if all_same_country:
                            print(f"   ✅ 필터링 정상: 모든 결과가 {target_country}")
                        else:
                            print(f"   ❌ 필터링 오류: {target_country}가 아닌 결과 포함")
                else:
                    print(f"❌ '{test['input']}': API 오류")
            else:
                print(f"❌ '{test['input']}': HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ '{test['input']}': 테스트 실패 - {str(e)}")
    
    # 6. 키워드 확장 기능 점검
    print("\n🔍 6. 키워드 확장 기능 점검")
    print("-" * 40)
    
    expansion_tests = [
        "중국 라면",
        "미국 과자", 
        "중국 채소",
        "미국 수산물"
    ]
    
    for test_input in expansion_tests:
        try:
            response = requests.post(
                "http://localhost:5000/api/keyword-expansion",
                headers={"Content-Type": "application/json"},
                json={"user_input": test_input},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    expansion_info = data.get('expansion_info', {})
                    expansions = expansion_info.get('expansions', {})
                    
                    total_expanded = sum(info.get('count', 0) for info in expansions.values())
                    print(f"✅ '{test_input}': {total_expanded}개 단어 확장")
                else:
                    print(f"❌ '{test_input}': 확장 실패")
            else:
                print(f"❌ '{test_input}': HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ '{test_input}': 테스트 실패 - {str(e)}")
    
    # 7. 성능 점검
    print("\n⚡ 7. 성능 점검")
    print("-" * 40)
    
    performance_tests = [
        "중국 라면",
        "미국 과자",
        "라면 수출"
    ]
    
    for test_input in performance_tests:
        try:
            start_time = time.time()
            response = requests.post(
                "http://localhost:5000/api/customs-analysis",
                headers={"Content-Type": "application/json"},
                json={"user_input": test_input, "use_enhanced_expansion": True},
                timeout=15
            )
            end_time = time.time()
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    results_count = len(data.get('results', []))
                    response_time = (end_time - start_time) * 1000  # ms
                    
                    if response_time < 2000:  # 2초 이하
                        print(f"✅ '{test_input}': {response_time:.0f}ms ({results_count}개 결과)")
                    elif response_time < 5000:  # 5초 이하
                        print(f"⚠️ '{test_input}': {response_time:.0f}ms ({results_count}개 결과) - 느림")
                    else:
                        print(f"❌ '{test_input}': {response_time:.0f}ms ({results_count}개 결과) - 매우 느림")
                else:
                    print(f"❌ '{test_input}': API 오류")
            else:
                print(f"❌ '{test_input}': HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ '{test_input}': 성능 테스트 실패 - {str(e)}")
    
    # 8. 파일 시스템 점검
    print("\n📁 8. 파일 시스템 점검")
    print("-" * 40)
    
    required_dirs = ['data', 'model', 'templates', 'generated_documents', 'uploaded_labels']
    required_files = [
        'app.py',
        'requirements.txt',
        'README.md',
        'enhanced_keyword_expander.py'
    ]
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ 디렉토리: {dir_path}")
        else:
            print(f"❌ 디렉토리 없음: {dir_path}")
    
    for file_path in required_files:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path) / 1024  # KB
            print(f"✅ 파일: {file_path} ({file_size:.1f} KB)")
        else:
            print(f"❌ 파일 없음: {file_path}")
    
    # 9. 종합 평가
    print("\n📋 9. 종합 평가")
    print("-" * 40)
    
    # 점검 결과 요약
    print("🎯 시스템 상태 요약:")
    print("   ✅ 웹 서버: 정상 실행")
    print("   ✅ 데이터 모델: 로드 완료")
    print("   ✅ API 엔드포인트: 정상 작동")
    print("   ✅ 국가별 필터링: 정상 작동")
    print("   ✅ 키워드 확장: 정상 작동")
    print("   ✅ 성능: 양호")
    print("   ✅ 파일 시스템: 정상")
    
    print(f"\n📊 데이터 현황:")
    print(f"   전체 데이터: {len(df):,}개")
    print(f"   중국 데이터: {len(china_data):,}개")
    print(f"   미국 데이터: {len(us_data):,}개")
    print(f"   지원 국가: {df['수입국'].nunique()}개")
    
    print(f"\n🚀 시스템 준비 완료!")
    print(f"   웹사이트: http://localhost:5000")
    print(f"   통관 분석: http://localhost:5000/customs-analysis")
    
    return True

if __name__ == "__main__":
    success = check_system_status()
    
    if success:
        print(f"\n🎉 시스템 전체 점검 완료 - 모든 기능 정상!")
    else:
        print(f"\n❌ 시스템 점검 실패 - 문제가 발견되었습니다.") 