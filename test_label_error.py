#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
라벨 생성 오류 진단 테스트 스크립트
"""

import sys
import os
import traceback
from datetime import datetime

def test_pil_import():
    """PIL 라이브러리 임포트 테스트"""
    print("🔍 PIL 라이브러리 임포트 테스트...")
    try:
        from PIL import Image, ImageDraw, ImageFont
        print("✅ PIL 라이브러리 임포트 성공")
        return True
    except Exception as e:
        print(f"❌ PIL 라이브러리 임포트 실패: {e}")
        return False

def test_font_loading():
    """폰트 로딩 테스트"""
    print("\n🔍 폰트 로딩 테스트...")
    try:
        from PIL import ImageFont
        
        font_paths = [
            "fonts/msyh.ttc",
            "fonts/simsun.ttc", 
            "fonts/malgun.ttf",
            "fonts/arial.ttf"
        ]
        
        for font_path in font_paths:
            try:
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, 20)
                    print(f"✅ 폰트 로드 성공: {font_path}")
                    return True
                else:
                    print(f"❌ 폰트 파일 없음: {font_path}")
            except Exception as e:
                print(f"❌ 폰트 로드 실패: {font_path} - {e}")
        
        return False
    except Exception as e:
        print(f"❌ 폰트 테스트 실패: {e}")
        return False

def test_simple_label_creation():
    """간단한 라벨 생성 테스트"""
    print("\n🔍 간단한 라벨 생성 테스트...")
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # 테스트 제품 정보
        product_info = {
            'name': '테스트 제품',
            'nutrition': {
                'calories': '400',
                'protein': '12',
                'fat': '15',
                'carbs': '60',
                'sodium': '800'
            },
            'allergies': ['우유', '계란']
        }
        
        # 이미지 생성
        width, height = 800, 1000
        image = Image.new('RGB', (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # 폰트 로드
        font = None
        font_paths = ["fonts/msyh.ttc", "fonts/simsun.ttc", "fonts/malgun.ttf"]
        
        for font_path in font_paths:
            try:
                font = ImageFont.truetype(font_path, 20)
                print(f"✅ 폰트 로드 성공: {font_path}")
                break
            except Exception as e:
                print(f"❌ 폰트 로드 실패: {font_path} - {e}")
                continue
        
        if font is None:
            print("⚠️ 모든 폰트 로드 실패, 기본 폰트 사용")
            font = ImageFont.load_default()
        
        # 텍스트 그리기
        draw.text((30, 30), f"테스트 라벨 - {datetime.now().strftime('%Y-%m-%d')}", fill=(0, 0, 0), font=font)
        draw.text((30, 60), f"제품명: {product_info['name']}", fill=(0, 0, 0), font=font)
        
        # 이미지 저장
        test_filename = f"test_label_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        image.save(test_filename)
        print(f"✅ 테스트 라벨 생성 성공: {test_filename}")
        
        # 파일 삭제
        os.remove(test_filename)
        print("✅ 테스트 파일 정리 완료")
        
        return True
        
    except Exception as e:
        print(f"❌ 라벨 생성 테스트 실패: {e}")
        traceback.print_exc()
        return False

def test_chinese_label_creation():
    """중국어 라벨 생성 테스트"""
    print("\n🔍 중국어 라벨 생성 테스트...")
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # 테스트 제품 정보
        product_info = {
            'name': '测试产品',
            'nutrition': {
                'calories': '400',
                'protein': '12',
                'fat': '15',
                'carbs': '60',
                'sodium': '800'
            },
            'allergies': ['牛奶', '鸡蛋']
        }
        
        # 이미지 생성
        width, height = 800, 1000
        image = Image.new('RGB', (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # 중국어 폰트 로드
        font = None
        font_paths = ["fonts/msyh.ttc", "fonts/simsun.ttc"]
        
        for font_path in font_paths:
            try:
                font = ImageFont.truetype(font_path, 20)
                print(f"✅ 중국어 폰트 로드 성공: {font_path}")
                break
            except Exception as e:
                print(f"❌ 중국어 폰트 로드 실패: {font_path} - {e}")
                continue
        
        if font is None:
            print("⚠️ 중국어 폰트 로드 실패")
            return False
        
        # 중국어 텍스트 그리기
        draw.text((30, 30), "营养标签", fill=(0, 0, 0), font=font)
        draw.text((30, 60), f"产品名称: {product_info['name']}", fill=(0, 0, 0), font=font)
        
        # 이미지 저장
        test_filename = f"test_chinese_label_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        image.save(test_filename)
        print(f"✅ 중국어 테스트 라벨 생성 성공: {test_filename}")
        
        # 파일 삭제
        os.remove(test_filename)
        print("✅ 중국어 테스트 파일 정리 완료")
        
        return True
        
    except Exception as e:
        print(f"❌ 중국어 라벨 생성 테스트 실패: {e}")
        traceback.print_exc()
        return False

def test_directory_permissions():
    """디렉토리 권한 테스트"""
    print("\n🔍 디렉토리 권한 테스트...")
    try:
        # advanced_labels 디렉토리 생성 테스트
        test_dir = "advanced_labels"
        if not os.path.exists(test_dir):
            os.makedirs(test_dir)
            print(f"✅ 디렉토리 생성 성공: {test_dir}")
        else:
            print(f"✅ 디렉토리 존재: {test_dir}")
        
        # 파일 쓰기 테스트
        test_file = os.path.join(test_dir, "test_permission.txt")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("권한 테스트")
        print(f"✅ 파일 쓰기 성공: {test_file}")
        
        # 파일 삭제
        os.remove(test_file)
        print("✅ 테스트 파일 정리 완료")
        
        return True
        
    except Exception as e:
        print(f"❌ 디렉토리 권한 테스트 실패: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("🚀 라벨 생성 오류 진단 테스트 시작")
    print("=" * 50)
    
    tests = [
        ("PIL 라이브러리 임포트", test_pil_import),
        ("폰트 로딩", test_font_loading),
        ("간단한 라벨 생성", test_simple_label_creation),
        ("중국어 라벨 생성", test_chinese_label_creation),
        ("디렉토리 권한", test_directory_permissions)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name} 테스트 시작...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 테스트 중 예외 발생: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 테스트 결과 요약")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 모든 테스트 통과! 라벨 생성 시스템이 정상 작동합니다.")
    else:
        print("⚠️ 일부 테스트 실패. 라벨 생성에 문제가 있을 수 있습니다.")
        print("\n🔧 해결 방법:")
        print("1. PIL 라이브러리 재설치: pip install --upgrade Pillow")
        print("2. 폰트 파일 확인: fonts/ 폴더의 폰트 파일들이 정상인지 확인")
        print("3. 디렉토리 권한 확인: advanced_labels/ 폴더 쓰기 권한 확인")
        print("4. 메모리 부족 확인: 시스템 메모리 사용량 확인")

if __name__ == "__main__":
    main() 