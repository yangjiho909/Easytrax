#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
실제 라벨 생성 기능 테스트 스크립트
"""

import sys
import os
from datetime import datetime

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_nutrition_label_generator():
    """영양성분표 라벨 생성기 테스트"""
    print("🏷️ 영양성분표 라벨 생성기 테스트")
    
    try:
        from nutrition_label_generator import NutritionLabelGenerator
        
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
        
        # 중국어 라벨 생성
        generator = NutritionLabelGenerator()
        chinese_label = generator.generate_chinese_nutrition_label(product_info)
        
        # 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_chinese_label_nutrition_{timestamp}.png"
        filepath = generator.save_label(chinese_label, filename)
        print(f"✅ 중국어 영양성분표 라벨 생성 완료: {filepath}")
        
        return filepath
        
    except Exception as e:
        print(f"❌ 영양성분표 라벨 생성기 실패: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_advanced_label_generator():
    """고급 라벨 생성기 테스트"""
    print("\n🏷️ 고급 라벨 생성기 테스트")
    
    try:
        from advanced_label_generator import AdvancedLabelGenerator
        
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
        
        # 중국어 라벨 생성
        generator = AdvancedLabelGenerator()
        chinese_label = generator.generate_china_2027_label(product_info)
        
        # 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_chinese_label_advanced_{timestamp}.png"
        filepath = generator.save_label(chinese_label, filename)
        print(f"✅ 고급 중국어 라벨 생성 완료: {filepath}")
        
        return filepath
        
    except Exception as e:
        print(f"❌ 고급 라벨 생성기 실패: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_app_label_generation():
    """앱의 라벨 생성 기능 테스트"""
    print("\n🏷️ 앱 라벨 생성 기능 테스트")
    
    try:
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
        
        # app.py의 create_simple_test_label 함수 사용
        from app import create_simple_test_label
        
        # 중국어 라벨 생성
        chinese_label = create_simple_test_label("중국", product_info)
        
        # 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_chinese_label_app_{timestamp}.png"
        filepath = os.path.join("advanced_labels", filename)
        os.makedirs("advanced_labels", exist_ok=True)
        chinese_label.save(filepath)
        print(f"✅ 앱 중국어 라벨 생성 완료: {filepath}")
        
        return filepath
        
    except Exception as e:
        print(f"❌ 앱 라벨 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """메인 테스트 함수"""
    print("🚀 라벨 생성 기능 테스트 시작")
    print("=" * 50)
    
    # 1. 영양성분표 라벨 생성기 테스트
    test_nutrition_label_generator()
    
    # 2. 고급 라벨 생성기 테스트
    test_advanced_label_generator()
    
    # 3. 앱 라벨 생성 기능 테스트
    test_app_label_generation()
    
    print("\n" + "=" * 50)
    print("✅ 모든 라벨 생성 테스트 완료")
    print("📁 생성된 파일들은 다음 폴더에서 확인할 수 있습니다:")
    print("   - nutrition_labels/ (영양성분표 라벨)")
    print("   - advanced_labels/ (고급 라벨, 앱 라벨)")

if __name__ == "__main__":
    main() 