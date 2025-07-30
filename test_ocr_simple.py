#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 OCR 기능 간단 테스트
"""

import requests
import os
from PIL import Image, ImageDraw, ImageFont

def create_test_image():
    """테스트 이미지 생성"""
    print("📸 테스트 이미지 생성 중...")
    
    # 간단한 테스트 이미지 생성
    img = Image.new('RGB', (400, 300), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
    
    test_text = [
        "제품명: 테스트 라면",
        "제조사: 테스트 식품(주)",
        "중량: 120g",
        "열량: 400kcal",
        "단백질: 12g",
        "지방: 15g",
        "탄수화물: 60g",
        "나트륨: 1200mg"
    ]
    
    y = 20
    for text in test_text:
        draw.text((20, y), text, fill='black', font=font)
        y += 25
    
    test_image_path = "test_ocr_image.png"
    img.save(test_image_path)
    print(f"✅ 테스트 이미지 생성 완료: {test_image_path}")
    return test_image_path

def test_ocr_api(image_path):
    """OCR API 테스트"""
    print(f"🔍 OCR API 테스트 중... (이미지: {image_path})")
    
    try:
        url = "http://localhost:5000/api/ocr-extract"
        
        with open(image_path, 'rb') as f:
            files = {'image': f}
            response = requests.post(url, files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ OCR API 호출 성공!")
                print(f"📊 추출된 정보: {len(result.get('extracted_info', {}))}개")
                print(f"📝 원본 텍스트 길이: {len(result.get('raw_text', ''))}자")
                print(f"🤖 AI 강화: {result.get('ai_enhanced', False)}")
                return True
            else:
                print(f"❌ OCR 추출 실패: {result.get('error', '알 수 없는 오류')}")
                return False
        else:
            print(f"❌ OCR API 오류: {response.status_code}")
            print(f"응답: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ OCR 테스트 실패: {e}")
        return False

def test_existing_image():
    """기존 테스트 이미지로 테스트"""
    print("🖼️ 기존 테스트 이미지로 OCR 테스트...")
    
    test_images = [
        "mvp_nutrition_labels/mvp_nutrition_label_korean_20250727_134704.png",
        "mvp_nutrition_labels/mvp_nutrition_label_english_20250727_134704.png",
        "mvp_nutrition_labels/mvp_nutrition_label_chinese_20250727_134704.png"
    ]
    
    for image_path in test_images:
        if os.path.exists(image_path):
            print(f"\n📸 테스트 이미지: {image_path}")
            success = test_ocr_api(image_path)
            if success:
                print("✅ 이 이미지는 OCR이 정상 작동합니다!")
            else:
                print("❌ 이 이미지에서 OCR 오류 발생")
        else:
            print(f"⚠️ 이미지 파일이 없습니다: {image_path}")

def main():
    """메인 테스트 함수"""
    print("🧪 OCR 기능 테스트 시작")
    print("=" * 50)
    
    # 1. 기존 테스트 이미지로 테스트
    test_existing_image()
    
    print("\n" + "=" * 50)
    
    # 2. 새로 생성한 테스트 이미지로 테스트
    test_image_path = create_test_image()
    success = test_ocr_api(test_image_path)
    
    # 테스트 이미지 정리
    if os.path.exists(test_image_path):
        os.remove(test_image_path)
        print(f"🗑️ 테스트 이미지 정리: {test_image_path}")
    
    print("\n" + "=" * 50)
    print("🏁 OCR 테스트 완료")
    
    if success:
        print("✅ OCR 기능이 정상적으로 작동하고 있습니다!")
    else:
        print("❌ OCR 기능에 문제가 있습니다.")

if __name__ == "__main__":
    main() 