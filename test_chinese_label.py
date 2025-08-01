#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
중국어 라벨 생성 테스트 스크립트
"""

import sys
import os
from PIL import Image, ImageDraw, ImageFont

def test_font_loading():
    """폰트 로딩 테스트"""
    print("🔤 폰트 로딩 테스트")
    
    # 폰트 경로들
    font_paths = [
        "fonts/msyh.ttc",      # Microsoft YaHei (중국어, 영어, 한글)
        "fonts/simsun.ttc",    # SimSun (중국어, 영어)
        "fonts/malgun.ttf",    # 맑은 고딕 (한글)
        "fonts/arial.ttf",     # Arial (영어)
    ]
    
    for font_path in font_paths:
        try:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, 20)
                print(f"✅ {font_path} - 로딩 성공")
                
                # 중국어 텍스트 테스트
                test_text = "营养标签"
                try:
                    # 텍스트 크기 측정
                    bbox = font.getbbox(test_text)
                    print(f"   📏 중국어 텍스트 크기: {bbox}")
                except Exception as e:
                    print(f"   ❌ 중국어 텍스트 렌더링 실패: {e}")
            else:
                print(f"❌ {font_path} - 파일 없음")
        except Exception as e:
            print(f"❌ {font_path} - 로딩 실패: {e}")

def test_chinese_label_generation():
    """중국어 라벨 생성 테스트"""
    print("\n🏷️ 중국어 라벨 생성 테스트")
    
    try:
        # 폰트 로드
        font_path = "fonts/msyh.ttc"
        if not os.path.exists(font_path):
            print(f"❌ 폰트 파일 없음: {font_path}")
            return
        
        # 폰트 생성
        title_font = ImageFont.truetype(font_path, 36)
        header_font = ImageFont.truetype(font_path, 28)
        body_font = ImageFont.truetype(font_path, 22)
        small_font = ImageFont.truetype(font_path, 20)
        
        # 이미지 생성
        width, height = 800, 1200
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)
        
        # 테스트 텍스트들
        texts = [
            ("营养标签", title_font, (50, 50), 'black'),
            ("营养成分表", header_font, (50, 120), 'black'),
            ("每100克含量", body_font, (50, 180), 'black'),
            ("能量: 350千卡", body_font, (50, 220), 'black'),
            ("蛋白质: 12克", body_font, (50, 260), 'black'),
            ("脂肪: 15克", body_font, (50, 300), 'black'),
            ("碳水化合物: 45克", body_font, (50, 340), 'black'),
            ("钠: 800毫克", body_font, (50, 380), 'black'),
            ("过敏原信息", header_font, (50, 450), 'red'),
            ("含有: 大豆, 小麦", body_font, (50, 490), 'red'),
            ("配料表", header_font, (50, 560), 'black'),
            ("面条, 调味包, 蔬菜包", body_font, (50, 600), 'black'),
            ("净含量: 120克", body_font, (50, 680), 'black'),
            ("保质期: 12个月", body_font, (50, 720), 'black'),
            ("生产日期: 2024年12月", body_font, (50, 760), 'black'),
            ("制造商: 韩国食品公司", body_font, (50, 800), 'black'),
        ]
        
        # 텍스트 그리기
        for text, font, position, color in texts:
            try:
                draw.text(position, text, font=font, fill=color)
                print(f"✅ 텍스트 그리기 성공: {text}")
            except Exception as e:
                print(f"❌ 텍스트 그리기 실패: {text} - {e}")
        
        # 이미지 저장
        output_path = "test_chinese_label.png"
        image.save(output_path)
        print(f"✅ 중국어 라벨 저장 완료: {output_path}")
        
        return output_path
        
    except Exception as e:
        print(f"❌ 중국어 라벨 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_font_fallback():
    """폰트 폴백 테스트"""
    print("\n🔄 폰트 폴백 테스트")
    
    # 폰트 우선순위
    font_paths = [
        "fonts/msyh.ttc",      # Microsoft YaHei
        "fonts/simsun.ttc",    # SimSun
        "fonts/malgun.ttf",    # 맑은 고딕
        "fonts/arial.ttf",     # Arial
    ]
    
    font_path = None
    for path in font_paths:
        if os.path.exists(path):
            font_path = path
            break
    
    if font_path:
        print(f"✅ 사용할 폰트: {font_path}")
        return font_path
    else:
        print("❌ 사용 가능한 폰트 없음")
        return None

def main():
    """메인 테스트 함수"""
    print("🚀 중국어 라벨 테스트 시작")
    print("=" * 50)
    
    # 1. 폰트 로딩 테스트
    test_font_loading()
    
    # 2. 폰트 폴백 테스트
    test_font_fallback()
    
    # 3. 중국어 라벨 생성 테스트
    test_chinese_label_generation()
    
    print("\n" + "=" * 50)
    print("✅ 모든 테스트 완료")

if __name__ == "__main__":
    main() 