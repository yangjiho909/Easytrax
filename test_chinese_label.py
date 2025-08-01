#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
중국어 라벨 생성 테스트 스크립트
"""

import sys
import os
from datetime import datetime

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_chinese_label_generation():
    """중국어 라벨 생성 테스트"""
    
    print("🇨🇳 중국어 라벨 생성 테스트 시작")
    print("=" * 50)
    
    # 테스트용 제품 정보
    product_info = {
        "name": "라면",
        "product_name": "라면",
        "origin": "대한민국",
        "manufacturer": "한국식품(주)",
        "expiry_date": "2026-12-31",
        "nutrition": {
            "calories": "400",
            "protein": "12",
            "fat": "15",
            "carbs": "60",
            "sodium": "800",
            "sugar": "5",
            "fiber": "2",
            "serving_size": "85"
        },
        "ingredients": ["면류(밀가루, 소금)", "분말스프", "건조야채", "조미료", "향신료"],
        "allergies": ["밀", "대두"],
        "storage_method": "직사광선을 피해 서늘한 곳에 보관"
    }
    
    try:
        # 1. 기본 라벨 생성기 테스트
        print("1️⃣ 기본 라벨 생성기 테스트")
        from nutrition_label_generator import NutritionLabelGenerator
        
        basic_generator = NutritionLabelGenerator()
        chinese_label = basic_generator.generate_chinese_nutrition_label(product_info)
        
        # 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_chinese_label_basic_{timestamp}.png"
        filepath = basic_generator.save_label(chinese_label, filename)
        print(f"✅ 기본 중국어 라벨 생성 완료: {filepath}")
        
    except Exception as e:
        print(f"❌ 기본 라벨 생성기 실패: {e}")
    
    try:
        # 2. 고급 라벨 생성기 테스트
        print("\n2️⃣ 고급 라벨 생성기 테스트")
        from advanced_label_generator import AdvancedLabelGenerator
        
        advanced_generator = AdvancedLabelGenerator()
        advanced_chinese_label = advanced_generator.generate_china_2027_label(product_info)
        
        # 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_chinese_label_advanced_{timestamp}.png"
        filepath = advanced_generator.save_label(advanced_chinese_label, filename)
        print(f"✅ 고급 중국어 라벨 생성 완료: {filepath}")
        
    except Exception as e:
        print(f"❌ 고급 라벨 생성기 실패: {e}")
    
    try:
        # 3. 간단한 테스트 라벨 생성
        print("\n3️⃣ 간단한 테스트 라벨 생성")
        from app import create_simple_test_label
        
        simple_chinese_label = create_simple_test_label("중국", product_info)
        
        # 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_chinese_label_simple_{timestamp}.png"
        filepath = os.path.join("advanced_labels", filename)
        os.makedirs("advanced_labels", exist_ok=True)
        simple_chinese_label.save(filepath)
        print(f"✅ 간단한 중국어 라벨 생성 완료: {filepath}")
        
    except Exception as e:
        print(f"❌ 간단한 라벨 생성 실패: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 중국어 라벨 생성 테스트 완료")
    print("📁 생성된 파일들은 다음 폴더에서 확인할 수 있습니다:")
    print("   - nutrition_labels/ (기본 라벨)")
    print("   - advanced_labels/ (고급 라벨, 간단한 라벨)")

if __name__ == "__main__":
    test_chinese_label_generation() 