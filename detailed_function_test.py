#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 KATI 시스템 세부 기능 테스트
- 통관분석 기능 테스트
- 규제정보 조회 테스트
- 서류생성 기능 테스트
- 라벨생성 기능 테스트
- OCR 기능 테스트
"""

import requests
import json
import os
from datetime import datetime

def test_customs_analysis():
    """통관분석 기능 테스트"""
    print("🔍 통관분석 기능 테스트")
    print("=" * 50)
    
    try:
        url = "http://localhost:5000/api/customs-analysis"
        data = {
            "user_input": "라면 수출 시 통관 거부사례",
            "country": "중국"
        }
        
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                analysis_count = len(result.get('analysis', []))
                print(f"✅ 통관분석 성공: {analysis_count}개 결과")
                return True
            else:
                print(f"❌ 통관분석 실패: {result.get('error', '알 수 없는 오류')}")
                return False
        else:
            print(f"❌ 통관분석 API 오류: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 통관분석 테스트 실패: {e}")
        return False

def test_regulation_info():
    """규제정보 조회 테스트"""
    print("\n🔍 규제정보 조회 테스트")
    print("=" * 50)
    
    try:
        url = "http://localhost:5000/api/regulation-info"
        data = {
            "country": "중국",
            "product": "라면"
        }
        
        response = requests.post(url, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                regulations = result.get('regulations', {})
                regulation_count = len(regulations)
                print(f"✅ 규제정보 조회 성공: {regulation_count}개 규정")
                return True
            else:
                print(f"❌ 규제정보 조회 실패: {result.get('error', '알 수 없는 오류')}")
                return False
        else:
            print(f"❌ 규제정보 API 오류: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 규제정보 테스트 실패: {e}")
        return False

def test_document_generation():
    """서류생성 기능 테스트"""
    print("\n🔍 서류생성 기능 테스트")
    print("=" * 50)
    
    try:
        url = "http://localhost:5000/api/document-generation"
        data = {
            "country": "중국",
            "company_info": {
                "name": "테스트 식품(주)",
                "address": "서울시 강남구",
                "contact": "02-1234-5678"
            },
            "product_info": {
                "name": "테스트 라면",
                "quantity": 1000,
                "unit_price": 10.0
            },
            "generate_pdf": True
        }
        
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                documents = result.get('documents', {})
                doc_count = len(documents)
                pdf_files = result.get('pdf_files', {})
                pdf_count = len(pdf_files)
                print(f"✅ 서류생성 성공: {doc_count}개 서류, {pdf_count}개 PDF")
                return True
            else:
                print(f"❌ 서류생성 실패: {result.get('error', '알 수 없는 오류')}")
                return False
        else:
            print(f"❌ 서류생성 API 오류: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 서류생성 테스트 실패: {e}")
        return False

def test_nutrition_label():
    """영양라벨 생성 테스트"""
    print("\n🔍 영양라벨 생성 테스트")
    print("=" * 50)
    
    try:
        url = "http://localhost:5000/api/nutrition-label"
        data = {
            "country": "중국",
            "product_info": {
                "product_name": "테스트 라면",
                "manufacturer": "테스트 식품",
                "origin": "대한민국",
                "expiry_date": "2026-12-31",
                "nutrition": {
                    "calories": "400",
                    "protein": "12",
                    "fat": "15",
                    "carbohydrates": "60",
                    "sodium": "1200",
                    "sugar": "5"
                },
                "ingredients": "면, 분말스프, 건조야채",
                "allergies": "대두, 밀"
            }
        }
        
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                filename = result.get('filename', '')
                print(f"✅ 영양라벨 생성 성공: {filename}")
                return True
            else:
                print(f"❌ 영양라벨 생성 실패: {result.get('error', '알 수 없는 오류')}")
                return False
        else:
            print(f"❌ 영양라벨 API 오류: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 영양라벨 테스트 실패: {e}")
        return False

def test_ocr_functionality():
    """OCR 기능 테스트"""
    print("\n🔍 OCR 기능 테스트")
    print("=" * 50)
    
    try:
        # 테스트 이미지 생성
        from PIL import Image, ImageDraw, ImageFont
        
        # 간단한 테스트 이미지 생성
        img = Image.new('RGB', (300, 200), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        test_text = [
            "제품명: 테스트 라면",
            "제조사: 테스트 식품",
            "중량: 120g",
            "열량: 400kcal"
        ]
        
        y = 20
        for text in test_text:
            draw.text((20, y), text, fill='black', font=font)
            y += 25
        
        test_image_path = "test_ocr_image.png"
        img.save(test_image_path)
        
        # OCR API 테스트
        url = "http://localhost:5000/api/ocr-extract"
        
        with open(test_image_path, 'rb') as f:
            files = {'image': f}
            response = requests.post(url, files=files, timeout=30)
        
        # 테스트 이미지 정리
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                extracted_info = result.get('extracted_info', {})
                info_count = len(extracted_info)
                print(f"✅ OCR 추출 성공: {info_count}개 정보 추출")
                return True
            else:
                print(f"❌ OCR 추출 실패: {result.get('error', '알 수 없는 오류')}")
                return False
        else:
            print(f"❌ OCR API 오류: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ OCR 테스트 실패: {e}")
        return False

def test_compliance_analysis():
    """준수성분석 기능 테스트"""
    print("\n🔍 준수성분석 기능 테스트")
    print("=" * 50)
    
    try:
        url = "http://localhost:5000/api/compliance-analysis"
        data = {
            "country": "중국",
            "company_info": {
                "name": "테스트 식품(주)",
                "address": "서울시 강남구"
            },
            "product_info": {
                "name": "테스트 라면",
                "type": "즉석면류"
            },
            "prepared_documents": ["상업송장", "원산지증명서"],
            "labeling_info": {
                "has_chinese_label": True,
                "has_nutrition_facts": True
            }
        }
        
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                analysis = result.get('analysis', {})
                score = analysis.get('overall_score', 0)
                print(f"✅ 준수성분석 성공: 종합점수 {score}점")
                return True
            else:
                print(f"❌ 준수성분석 실패: {result.get('error', '알 수 없는 오류')}")
                return False
        else:
            print(f"❌ 준수성분석 API 오류: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 준수성분석 테스트 실패: {e}")
        return False

def generate_detailed_report():
    """세부 기능 테스트 보고서"""
    print("\n📊 세부 기능 테스트 보고서")
    print("=" * 60)
    print(f"테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 각 기능 테스트 실행
    tests = [
        ("통관분석", test_customs_analysis),
        ("규제정보 조회", test_regulation_info),
        ("서류생성", test_document_generation),
        ("영양라벨 생성", test_nutrition_label),
        ("OCR 기능", test_ocr_functionality),
        ("준수성분석", test_compliance_analysis)
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
    print(f"\n📋 세부 기능 테스트 결과")
    print("-" * 40)
    
    passed_tests = sum(results.values())
    total_tests = len(results)
    
    for test_name, result in results.items():
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{test_name}: {status}")
    
    print(f"\n🎯 세부 기능 결과: {passed_tests}/{total_tests} 통과")
    
    if passed_tests == total_tests:
        print("🎉 모든 세부 기능이 정상 작동합니다!")
        return True
    else:
        print("⚠️ 일부 기능에 문제가 있습니다. 점검이 필요합니다.")
        return False

if __name__ == "__main__":
    generate_detailed_report() 