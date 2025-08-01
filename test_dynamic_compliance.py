#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
동적 준수성 분석 테스트 스크립트
- 실시간 규제 데이터 연동 테스트
- AI 기반 OCR 분석 테스트
- 동적 점수 계산 테스트
"""

import requests
import json
import time
from datetime import datetime

# 테스트 서버 URL
BASE_URL = "https://kati-export-helper.onrender.com"

def test_regulation_status():
    """규제 상태 확인 테스트"""
    print("🔍 규제 상태 확인 테스트")
    
    countries = ["중국", "미국"]
    
    for country in countries:
        try:
            response = requests.get(f"{BASE_URL}/api/regulation-status", params={
                'country': country,
                'product_type': '식품'
            })
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    status = data['status']
                    print(f"✅ {country}: {status['status']} - {status['regulation_count']}개 규제")
                else:
                    print(f"❌ {country}: {data['error']}")
            else:
                print(f"❌ {country}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {country}: {str(e)}")

def test_update_regulations():
    """규제 데이터 업데이트 테스트"""
    print("\n🔄 규제 데이터 업데이트 테스트")
    
    countries = ["중국", "미국"]
    
    for country in countries:
        try:
            response = requests.post(f"{BASE_URL}/api/update-regulations", json={
                'country': country,
                'product_type': '식품'
            })
            
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    print(f"✅ {country}: {data['message']}")
                else:
                    print(f"❌ {country}: {data['error']}")
            else:
                print(f"❌ {country}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {country}: {str(e)}")

def test_ai_ocr_analysis():
    """AI OCR 분석 테스트"""
    print("\n🤖 AI OCR 분석 테스트")
    
    # 테스트용 샘플 데이터
    test_data = {
        'country': '중국',
        'product_type': '식품',
        'structured_data': {
            '라벨': {
                'product_name': '테스트 라면',
                'ingredients': '면, 스프, 조미료',
                'allergens': '대두, 밀',
                'text': '중국어 라벨 텍스트'
            },
            '영양성분표': {
                'calories': '350',
                'protein': '12',
                'fat': '15',
                'carbs': '45',
                'text': '영양성분 정보'
            }
        }
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/dynamic-compliance-analysis", json=test_data)
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                analysis = data['analysis']
                print(f"✅ 분석 완료:")
                print(f"   - 점수: {analysis.get('overall_score', 0)}점")
                print(f"   - 주요 문제점: {len(analysis.get('critical_issues', []))}개")
                print(f"   - 개선 필요: {len(analysis.get('major_issues', []))}개")
                print(f"   - 권장사항: {len(analysis.get('minor_issues', []))}개")
                print(f"   - 제안: {len(analysis.get('suggestions', []))}개")
            else:
                print(f"❌ 분석 실패: {data['error']}")
        else:
            print(f"❌ HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ AI OCR 분석 테스트 실패: {str(e)}")

def test_compliance_analysis_with_files():
    """파일 업로드를 통한 준수성 분석 테스트"""
    print("\n📁 파일 업로드 준수성 분석 테스트")
    
    # 테스트용 파일 경로 (실제 파일이 있어야 함)
    test_files = [
        # "test_files/sample_label.jpg",
        # "test_files/sample_nutrition.pdf"
    ]
    
    for file_path in test_files:
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {
                    'document_type': '라벨',
                    'country': '중국',
                    'product_type': '식품'
                }
                
                response = requests.post(f"{BASE_URL}/api/ai-ocr-analysis", files=files, data=data)
                
                if response.status_code == 200:
                    result = response.json()
                    if result['success']:
                        print(f"✅ {file_path}: AI 분석 완료")
                        print(f"   - 신뢰도: {result.get('confidence', 0):.2f}")
                        print(f"   - 추출 데이터: {len(result.get('extracted_data', {}))}개 항목")
                    else:
                        print(f"❌ {file_path}: {result['error']}")
                else:
                    print(f"❌ {file_path}: HTTP {response.status_code}")
                    
        except FileNotFoundError:
            print(f"⚠️ {file_path}: 파일을 찾을 수 없습니다")
        except Exception as e:
            print(f"❌ {file_path}: {str(e)}")

def test_performance():
    """성능 테스트"""
    print("\n⚡ 성능 테스트")
    
    test_data = {
        'country': '중국',
        'product_type': '식품',
        'structured_data': {
            '라벨': {'text': '테스트 라벨'},
            '영양성분표': {'text': '테스트 영양성분'}
        }
    }
    
    start_time = time.time()
    
    try:
        response = requests.post(f"{BASE_URL}/api/dynamic-compliance-analysis", json=test_data)
        
        end_time = time.time()
        duration = end_time - start_time
        
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                print(f"✅ 분석 완료: {duration:.2f}초")
            else:
                print(f"❌ 분석 실패: {data['error']} ({duration:.2f}초)")
        else:
            print(f"❌ HTTP {response.status_code} ({duration:.2f}초)")
            
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        print(f"❌ 성능 테스트 실패: {str(e)} ({duration:.2f}초)")

def main():
    """메인 테스트 함수"""
    print("🚀 동적 준수성 분석 테스트 시작")
    print("=" * 50)
    
    # 1. 규제 상태 확인
    test_regulation_status()
    
    # 2. 규제 데이터 업데이트
    test_update_regulations()
    
    # 3. AI OCR 분석 테스트
    test_ai_ocr_analysis()
    
    # 4. 파일 업로드 테스트 (선택적)
    # test_compliance_analysis_with_files()
    
    # 5. 성능 테스트
    test_performance()
    
    print("\n" + "=" * 50)
    print("✅ 모든 테스트 완료")

if __name__ == "__main__":
    main() 