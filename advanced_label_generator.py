#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🏷️ 고도화된 영양정보 라벨 생성 시스템
- 2027년 중국 GB 7718-2025 규정 반영
- 2025년 미국 FDA 새로운 라벨링 규정 반영
- QR코드 디지털 라벨, FOP 라벨 등 최신 기능 포함
"""

import os
import qrcode
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta
import json
import requests
from typing import Dict, List, Optional, Tuple
import base64

class AdvancedLabelGenerator:
    """2027년 중국, 2025년 미국 규정을 반영한 고도화된 라벨 생성기"""
    
    def __init__(self):
        # OCR 인식도 향상을 위한 고해상도 설정
        self.label_width = 800  # 해상도 증가
        self.label_height = 1000  # 해상도 증가
        self.background_color = (255, 255, 255)  # 흰색
        self.text_color = (0, 0, 0)  # 검은색 (OCR 최적화)
        self.accent_color = (0, 100, 200)  # 파란색
        self.warning_color = (255, 0, 0)  # 빨간색
        self.allergy_color = (255, 140, 0)  # 주황색  # 주황색 (알레르기 강조)
        
        # 폰트 설정 (다국어 지원 폰트 우선 사용)
        try:
            # 다국어 지원 폰트 우선 시도 (중국어, 영어, 한글 모두 지원)
            multilingual_fonts = [
                "C:/Windows/Fonts/msyh.ttc",      # Microsoft YaHei (중국어, 영어, 한글)
                "C:/Windows/Fonts/simsun.ttc",    # SimSun (중국어, 영어)
                "C:/Windows/Fonts/simhei.ttf",    # SimHei (중국어, 영어)
                "C:/Windows/Fonts/arial.ttf",     # Arial (영어, 기본)
                "C:/Windows/Fonts/calibri.ttf",   # Calibri (영어, 기본)
                "C:/Windows/Fonts/tahoma.ttf",    # Tahoma (영어, 기본)
                "msyh.ttc",                       # Microsoft YaHei
                "simsun.ttc",                     # SimSun
                "simhei.ttf",                     # SimHei
                "arial.ttf",                      # Arial
                "calibri.ttf",                    # Calibri
                "tahoma.ttf",                     # Tahoma
                "malgun.ttf",                     # 맑은 고딕 (한글)
                "gulim.ttc",                      # 굴림 (한글)
            ]
            
            font_found = False
            for font_path in multilingual_fonts:
                try:
                    # OCR 인식도 향상을 위한 폰트 크기 증가
                    self.title_font = ImageFont.truetype(font_path, 36)  # 제목 폰트 크기 증가
                    self.header_font = ImageFont.truetype(font_path, 28)  # 헤더 폰트 크기 증가
                    self.body_font = ImageFont.truetype(font_path, 22)    # 본문 폰트 크기 증가
                    self.small_font = ImageFont.truetype(font_path, 20)   # 작은 폰트 크기 증가
                    self.allergy_font = ImageFont.truetype(font_path, 22) # 알레르기 폰트 크기 증가
                    print(f"✅ 다국어 폰트 로드 성공: {font_path}")
                    font_found = True
                    break
                except:
                    continue
            
            if not font_found:
                # 폰트를 찾을 수 없는 경우 기본 폰트 사용
                self.title_font = ImageFont.load_default()
                self.header_font = ImageFont.load_default()
                self.body_font = ImageFont.load_default()
                self.small_font = ImageFont.load_default()
                self.allergy_font = ImageFont.load_default()
                print("⚠️ 다국어 폰트를 찾을 수 없어 기본 폰트를 사용합니다.")
                
        except Exception as e:
            # 폰트를 찾을 수 없는 경우 기본 폰트 사용
            self.title_font = ImageFont.load_default()
            self.header_font = ImageFont.load_default()
            self.body_font = ImageFont.load_default()
            self.small_font = ImageFont.load_default()
            self.allergy_font = ImageFont.load_default()
            print(f"⚠️ 폰트 로드 실패: {e}")
        
        # 2027년 중국 알레르기 성분 (8대)
        self.china_allergens = [
            "글루텐 함유 곡물", "갑각류", "생선", "달걀", 
            "땅콩", "대두", "젖", "견과류"
        ]
        
        # 2025년 미국 알레르기 성분 (9대)
        self.us_allergens = [
            "우유", "달걀", "생선", "갑각류", "견과류", 
            "밀", "땅콩", "콩", "참깨"
        ]
    
    def generate_china_2027_label(self, product_info: Dict) -> Image.Image:
        """2027년 중국 GB 7718-2025 규정 라벨 생성 (개선된 버전)"""
        
        try:
            print("🇨🇳 중국어 고급 라벨 생성 시작")
            
            # 중국어 전용 폰트 로딩 시도
            self._load_chinese_fonts()
            
            # 이미지 생성
            image = Image.new('RGB', (self.label_width, self.label_height), self.background_color)
            draw = ImageDraw.Draw(image)
            
            y_position = 20
            
            # 안전한 텍스트 그리기 함수
            def safe_draw_text(draw, position, text, font, fill):
                try:
                    if text is None:
                        text = ""
                    elif not isinstance(text, str):
                        text = str(text)
                    
                    if not text.strip():
                        text = "N/A"
                    
                    draw.text(position, text, fill=fill, font=font)
                except Exception as e:
                    print(f"⚠️ 텍스트 그리기 실패: {text} - {e}")
                    try:
                        draw.text(position, "N/A", fill=fill, font=font)
                    except:
                        pass
            
            # 1. 제품명 (사용자 입력 우선, 중국어 변환)
            product_name = product_info.get("product_name", product_info.get("name", "라면"))
            # 간단한 중국어 변환 (실제로는 번역 API 사용 권장)
            chinese_name_map = {
                "라면": "拉面", "김치": "泡菜", "된장": "大酱", "고추장": "辣椒酱"
            }
            product_name_chinese = chinese_name_map.get(product_name, f"{product_name}")
            safe_draw_text(draw, (20, y_position), product_name_chinese, self.title_font, self.accent_color)
            y_position += 40
            
            # 2. 원산지 (사용자 입력 우선)
            origin = product_info.get("origin", "대한민국")
            origin_chinese = "原产国：韩国" if origin == "대한민국" else f"原产国：{origin}"
            safe_draw_text(draw, (20, y_position), origin_chinese, self.body_font, self.text_color)
            y_position += 30
            
            # 3. 제조사 정보 (사용자 입력 우선)
            manufacturer = product_info.get("manufacturer", "한국식품(주)")
            manufacturer_chinese = "韩国食品公司" if manufacturer == "한국식품(주)" else f"{manufacturer}"
            safe_draw_text(draw, (20, y_position), f"制造商：{manufacturer_chinese}", self.body_font, self.text_color)
            y_position += 30
            
            # 4. 유통기한 (사용자 입력 우선)
            expiry_date = product_info.get("expiry_date", "2026-12-31")
            expiry_chinese = f"到期日：{expiry_date}"
            safe_draw_text(draw, (20, y_position), expiry_chinese, self.body_font, self.text_color)
            y_position += 40
            
            # 구분선
            draw.line([(20, y_position), (self.label_width-20, y_position)], fill=self.accent_color, width=2)
            y_position += 20
            
            # 5. 영양성분표 (1+6 체계)
            y_position = self._draw_china_nutrition_table(draw, product_info, y_position)
            
            # 6. 성분표 (알레르기 성분 강조)
            y_position = self._draw_china_ingredients(draw, product_info, y_position)
            
            # 7. 알레르기 정보 (8대 알레르기)
            y_position = self._draw_china_allergy_info(draw, product_info, y_position)
            
            # 8. 경고 문구 (2027년 의무)
            y_position = self._draw_china_warning(draw, y_position)
            
            # 9. 디지털 라벨 QR코드
            y_position = self._draw_digital_label_qr(draw, product_info, y_position)
            
            # 10. 보관 방법
            y_position = self._draw_storage_info(draw, product_info, y_position)
            
            # 11. 제조사 상세 정보
            self._draw_manufacturer_details(draw, product_info, y_position)
            
            print("✅ 중국어 고급 라벨 생성 완료")
            return image
            
        except Exception as e:
            print(f"❌ 중국어 고급 라벨 생성 실패: {e}")
            # 폴백: 기본 중국어 라벨 생성
            try:
                from nutrition_label_generator import NutritionLabelGenerator
                basic_generator = NutritionLabelGenerator()
                return basic_generator.generate_chinese_nutrition_label(product_info)
            except Exception as e2:
                print(f"❌ 기본 중국어 라벨 생성도 실패: {e2}")
                # 최종 폴백: 기본 이미지 생성
                fallback_image = Image.new('RGB', (self.label_width, self.label_height), self.background_color)
                fallback_draw = ImageDraw.Draw(fallback_image)
                fallback_draw.text((50, 50), "Chinese Label Generation Failed", fill=self.text_color)
                fallback_draw.text((50, 100), f"Error: {str(e)}", fill=self.warning_color)
                return fallback_image
    
    def _load_chinese_fonts(self):
        """중국어 전용 폰트 로딩"""
        try:
            chinese_fonts = [
                "C:/Windows/Fonts/msyh.ttc",      # Microsoft YaHei
                "C:/Windows/Fonts/simsun.ttc",    # SimSun
                "C:/Windows/Fonts/simhei.ttf",    # SimHei
                "msyh.ttc",
                "simsun.ttc",
                "simhei.ttf"
            ]
            
            for font_path in chinese_fonts:
                try:
                    self.title_font = ImageFont.truetype(font_path, 36)
                    self.header_font = ImageFont.truetype(font_path, 28)
                    self.body_font = ImageFont.truetype(font_path, 22)
                    self.small_font = ImageFont.truetype(font_path, 20)
                    self.allergy_font = ImageFont.truetype(font_path, 22)
                    print(f"✅ 중국어 폰트 로드 성공: {font_path}")
                    return
                except:
                    continue
            
            print("⚠️ 중국어 폰트를 찾을 수 없어 기본 폰트를 사용합니다.")
            
        except Exception as e:
            print(f"⚠️ 중국어 폰트 로드 실패: {e}")
    
    def generate_us_2025_label(self, product_info: Dict) -> Image.Image:
        """2025년 미국 FDA 새로운 라벨링 규정 라벨 생성"""
        
        # 이미지 생성
        image = Image.new('RGB', (self.label_width, self.label_height), self.background_color)
        draw = ImageDraw.Draw(image)
        
        y_position = 20
        
        # 1. 제품명 (사용자 입력 우선, 영어 변환)
        product_name = product_info.get("product_name", product_info.get("name", "라면"))
        # 간단한 영어 변환 (실제로는 번역 API 사용 권장)
        english_name_map = {
            "라면": "Korean Ramen", "김치": "Korean Kimchi", "된장": "Korean Doenjang", "고추장": "Korean Gochujang"
        }
        product_name_english = english_name_map.get(product_name, f"Korean {product_name}")
        draw.text((20, y_position), product_name_english, fill=self.accent_color, font=self.title_font)
        y_position += 40
        
        # 2. 원산지 (사용자 입력 우선)
        origin = product_info.get("origin", "대한민국")
        origin_english = "Republic of Korea" if origin == "대한민국" else origin
        draw.text((20, y_position), f"Country of Origin: {origin_english}", fill=self.text_color, font=self.body_font)
        y_position += 30
        
        # 3. 제조사 정보 (사용자 입력 우선)
        manufacturer = product_info.get("manufacturer", "한국식품(주)")
        manufacturer_english = "Korean Food Co., Ltd." if manufacturer == "한국식품(주)" else f"{manufacturer}"
        draw.text((20, y_position), f"Manufacturer: {manufacturer_english}", fill=self.text_color, font=self.body_font)
        y_position += 30
        
        # 4. 유통기한 (사용자 입력 우선)
        expiry_date = product_info.get("expiry_date", "2026-12-31")
        draw.text((20, y_position), f"Best Before: {expiry_date}", fill=self.text_color, font=self.body_font)
        y_position += 40
        
        # 구분선
        draw.line([(20, y_position), (self.label_width-20, y_position)], fill=self.accent_color, width=2)
        y_position += 20
        
        # 5. 영양성분표 (2025년 FDA 규정)
        y_position = self._draw_us_nutrition_table(draw, product_info, y_position)
        
        # 6. 성분표 (알레르기 성분 강조)
        y_position = self._draw_us_ingredients(draw, product_info, y_position)
        
        # 7. 알레르기 정보 (9대 알레르기)
        y_position = self._draw_us_allergy_info(draw, product_info, y_position)
        
        # 8. FOP 라벨 (2025년 제안)
        y_position = self._draw_fop_label(draw, product_info, y_position)
        
        # 9. 보관 방법
        y_position = self._draw_storage_info_english(draw, product_info, y_position)
        
        # 10. 제조사 상세 정보
        self._draw_manufacturer_details_english(draw, product_info, y_position)
        
        return image
    
    def _draw_china_nutrition_table(self, draw: ImageDraw.Draw, product_info: Dict, y_position: int) -> int:
        """중국 1+6 영양성분표 그리기 (안전한 버전)"""
        
        def safe_draw_text(draw, position, text, font, fill):
            try:
                if text is None:
                    text = ""
                elif not isinstance(text, str):
                    text = str(text)
                
                if not text.strip():
                    text = "N/A"
                
                draw.text(position, text, fill=fill, font=font)
            except Exception as e:
                print(f"⚠️ 텍스트 그리기 실패: {text} - {e}")
                try:
                    draw.text(position, "N/A", fill=fill, font=font)
                except:
                    pass
        
        # 제목
        safe_draw_text(draw, (20, y_position), "营养成分表 (每100g)", self.header_font, self.accent_color)
        y_position += 30
        
        # 표 헤더
        safe_draw_text(draw, (20, y_position), "项目", self.body_font, self.text_color)
        safe_draw_text(draw, (200, y_position), "含量", self.body_font, self.text_color)
        safe_draw_text(draw, (300, y_position), "营养素参考值%", self.body_font, self.text_color)
        y_position += 25
        
        # 구분선
        draw.line([(20, y_position), (self.label_width-20, y_position)], fill=self.text_color, width=1)
        y_position += 10
        
        # 1+6 필수 영양성분 (사용자 입력 우선)
        nutrition_data = product_info.get("nutrition", {})
        china_nutrition = {
            "能量": f"{nutrition_data.get('calories', '400')} kcal",
            "蛋白质": f"{nutrition_data.get('protein', '12')}g",
            "脂肪": f"{nutrition_data.get('fat', '15')}g",
            "饱和脂肪": f"{nutrition_data.get('saturated_fat', '5')}g",
            "碳水化合物": f"{nutrition_data.get('carbs', '60')}g",
            "糖": f"{nutrition_data.get('sugar', '5')}g",
            "钠": f"{nutrition_data.get('sodium', '800')}mg"
        }
        
        for nutrient, value in china_nutrition.items():
            safe_draw_text(draw, (20, y_position), nutrient, self.body_font, self.text_color)
            safe_draw_text(draw, (200, y_position), value, self.body_font, self.text_color)
            
            # NRV% 계산 (예시)
            if "kcal" in value:
                nrv = "20%"
            elif "g" in value:
                nrv = "15%"
            elif "mg" in value:
                nrv = "35%"
            else:
                nrv = "10%"
            
            safe_draw_text(draw, (300, y_position), nrv, self.body_font, self.text_color)
            y_position += 20
        
        y_position += 20
        
        # 구분선
        draw.line([(20, y_position), (self.label_width-20, y_position)], fill=self.accent_color, width=1)
        y_position += 15
        
        return y_position
    
    def _draw_us_nutrition_table(self, draw: ImageDraw.Draw, product_info: Dict, y_position: int) -> int:
        """미국 2025년 FDA 영양성분표 그리기"""
        
        # 제목
        draw.text((20, y_position), "Nutrition Facts", fill=self.accent_color, font=self.header_font)
        y_position += 30
        
        # 1회 제공량
        serving_size = "1 package (85g)"
        draw.text((20, y_position), f"Serving Size: {serving_size}", fill=self.text_color, font=self.body_font)
        y_position += 25
        
        # 칼로리 (강조)
        calories = product_info.get("nutrition", {}).get("열량", "400 kcal").split()[0]
        draw.text((20, y_position), f"Calories: {calories}", fill=self.text_color, font=self.header_font)
        y_position += 30
        
        # 구분선
        draw.line([(20, y_position), (self.label_width-20, y_position)], fill=self.text_color, width=2)
        y_position += 10
        
        # 영양성분 (13개 필수, 사용자 입력 우선)
        nutrition_data = product_info.get("nutrition", {})
        us_nutrition = [
            ("Total Fat", f"{nutrition_data.get('fat', '15')}g", "25%"),
            ("Saturated Fat", f"{nutrition_data.get('saturated_fat', '5')}g", "25%"),
            ("Trans Fat", "0g", "0%"),
            ("Cholesterol", "0mg", "0%"),
            ("Sodium", f"{nutrition_data.get('sodium', '800')}mg", "35%"),
            ("Total Carbohydrate", f"{nutrition_data.get('carbs', '60')}g", "20%"),
            ("Dietary Fiber", f"{nutrition_data.get('fiber', '2')}g", "8%"),
            ("Total Sugars", f"{nutrition_data.get('sugar', '5')}g", ""),
            ("Added Sugars", "0g", "0%"),
            ("Protein", f"{nutrition_data.get('protein', '12')}g", ""),
            ("Vitamin D", "0mcg", "0%"),
            ("Calcium", "20mg", "2%"),
            ("Iron", "2mg", "10%"),
            ("Potassium", "200mg", "4%")
        ]
        
        for nutrient, value, dv in us_nutrition:
            draw.text((20, y_position), nutrient, fill=self.text_color, font=self.body_font)
            draw.text((200, y_position), value, fill=self.text_color, font=self.body_font)
            if dv:
                draw.text((300, y_position), f"{dv} DV", fill=self.text_color, font=self.body_font)
            y_position += 18
        
        y_position += 20
        
        # 구분선
        draw.line([(20, y_position), (self.label_width-20, y_position)], fill=self.accent_color, width=1)
        y_position += 15
        
        return y_position
    
    def _draw_china_ingredients(self, draw: ImageDraw.Draw, product_info: Dict, y_position: int) -> int:
        """중국 성분표 (알레르기 성분 강조) - 안전한 버전"""
        
        def safe_draw_text(draw, position, text, font, fill):
            try:
                if text is None:
                    text = ""
                elif not isinstance(text, str):
                    text = str(text)
                
                if not text.strip():
                    text = "N/A"
                
                draw.text(position, text, fill=fill, font=font)
            except Exception as e:
                print(f"⚠️ 텍스트 그리기 실패: {text} - {e}")
                try:
                    draw.text(position, "N/A", fill=fill, font=font)
                except:
                    pass
        
        # 제목
        safe_draw_text(draw, (20, y_position), "配料表", self.header_font, self.accent_color)
        y_position += 25
        
        # 성분 목록
        ingredients = product_info.get("ingredients", [
            "面条(小麦粉, 盐)", "调味粉", "脱水蔬菜", "调味料", "香料"
        ])
        
        for ingredient in ingredients:
            # 알레르기 성분 강조 표시
            is_allergy = any(allergen in ingredient for allergen in self.china_allergens)
            color = self.allergy_color if is_allergy else self.text_color
            font = self.allergy_font if is_allergy else self.body_font
            
            prefix = "• " if not is_allergy else "⚠ "
            safe_draw_text(draw, (20, y_position), f"{prefix}{ingredient}", font, color)
            y_position += 18
        
        y_position += 10
        
        # 구분선
        draw.line([(20, y_position), (self.label_width-20, y_position)], fill=self.accent_color, width=1)
        y_position += 15
        
        return y_position
    
    def _draw_us_ingredients(self, draw: ImageDraw.Draw, product_info: Dict, y_position: int) -> int:
        """미국 성분표 (알레르기 성분 강조)"""
        
        # 제목
        draw.text((20, y_position), "Ingredients", fill=self.accent_color, font=self.header_font)
        y_position += 25
        
        # 성분 목록
        ingredients = product_info.get("ingredients_english", [
            "Noodles (Wheat Flour, Salt)", "Seasoning Powder", "Dehydrated Vegetables", 
            "Seasoning", "Spices"
        ])
        
        for ingredient in ingredients:
            # 알레르기 성분 강조 표시
            is_allergy = any(allergen.lower() in ingredient.lower() for allergen in self.us_allergens)
            color = self.allergy_color if is_allergy else self.text_color
            font = self.allergy_font if is_allergy else self.body_font
            
            prefix = "• " if not is_allergy else "⚠ "
            draw.text((20, y_position), f"{prefix}{ingredient}", fill=color, font=font)
            y_position += 18
        
        y_position += 10
        
        # 구분선
        draw.line([(20, y_position), (self.label_width-20, y_position)], fill=self.accent_color, width=1)
        y_position += 15
        
        return y_position
    
    def _draw_china_allergy_info(self, draw: ImageDraw.Draw, product_info: Dict, y_position: int) -> int:
        """중국 알레르기 정보 (8대 알레르기) - 안전한 버전"""
        
        def safe_draw_text(draw, position, text, font, fill):
            try:
                if text is None:
                    text = ""
                elif not isinstance(text, str):
                    text = str(text)
                
                if not text.strip():
                    text = "N/A"
                
                draw.text(position, text, fill=fill, font=font)
            except Exception as e:
                print(f"⚠️ 텍스트 그리기 실패: {text} - {e}")
                try:
                    draw.text(position, "N/A", fill=fill, font=font)
                except:
                    pass
        
        # 제목
        safe_draw_text(draw, (20, y_position), "过敏原信息", self.header_font, self.warning_color)
        y_position += 25
        
        # 사용자 입력 알레르기 정보
        allergies = product_info.get("allergies", [])
        if allergies:
            # 알레르기 성분을 중국어로 변환
            allergy_map = {
                "밀": "小麦", "대두": "大豆", "계란": "鸡蛋", "우유": "牛奶",
                "땅콩": "花生", "견과류": "坚果", "조개류": "贝类", "어류": "鱼类"
            }
            allergy_ingredients = [allergy_map.get(allergy, allergy) for allergy in allergies]
            allergy_text = "含有: " + ", ".join(allergy_ingredients)
            safe_draw_text(draw, (20, y_position), allergy_text, self.body_font, self.warning_color)
        else:
            safe_draw_text(draw, (20, y_position), "含有: 无", self.body_font, self.text_color)
        
        y_position += 25
        
        # 주의사항
        safe_draw_text(draw, (20, y_position), "※ 本产品含有过敏原成分，请过敏体质者注意。", 
                     self.small_font, self.warning_color)
        y_position += 20
        
        return y_position
    
    def _draw_us_allergy_info(self, draw: ImageDraw.Draw, product_info: Dict, y_position: int) -> int:
        """미국 알레르기 정보 (9대 알레르기)"""
        
        # 제목
        draw.text((20, y_position), "Allergen Information", fill=self.warning_color, font=self.header_font)
        y_position += 25
        
        # 사용자 입력 알레르기 정보
        allergies = product_info.get("allergies", [])
        if allergies:
            # 알레르기 성분을 영어로 변환
            allergy_map = {
                "밀": "Wheat", "대두": "Soy", "계란": "Egg", "우유": "Milk",
                "땅콩": "Peanut", "견과류": "Tree Nuts", "조개류": "Shellfish", "어류": "Fish"
            }
            allergy_ingredients = [allergy_map.get(allergy, allergy) for allergy in allergies]
            draw.text((20, y_position), "Contains: " + ", ".join(allergy_ingredients), 
                     fill=self.warning_color, font=self.body_font)
        else:
            draw.text((20, y_position), "Contains: None", fill=self.text_color, font=self.body_font)
        
        y_position += 25
        
        # 주의사항
        draw.text((20, y_position), "※ This product contains allergens. Please check ingredients if you have allergies.", 
                 fill=self.warning_color, font=self.small_font)
        y_position += 20
        
        return y_position
    
    def _draw_china_warning(self, draw: ImageDraw.Draw, y_position: int) -> int:
        """중국 2027년 의무 경고 문구 - 안전한 버전"""
        
        def safe_draw_text(draw, position, text, font, fill):
            try:
                if text is None:
                    text = ""
                elif not isinstance(text, str):
                    text = str(text)
                
                if not text.strip():
                    text = "N/A"
                
                draw.text(position, text, fill=fill, font=font)
            except Exception as e:
                print(f"⚠️ 텍스트 그리기 실패: {text} - {e}")
                try:
                    draw.text(position, "N/A", fill=fill, font=font)
                except:
                    pass
        
        # 경고 문구
        warning_text = "儿童及青少年应避免过量摄入钠、脂肪、糖"
        safe_draw_text(draw, (20, y_position), warning_text, self.body_font, self.warning_color)
        y_position += 25
        
        return y_position
    
    def _draw_digital_label_qr(self, draw: ImageDraw.Draw, product_info: Dict, y_position: int) -> int:
        """중국 디지털 라벨 QR코드"""
        
        # 디지털 라벨 문구
        draw.text((20, y_position), "数字标签", fill=self.accent_color, font=self.header_font)
        y_position += 25
        
        # QR코드 생성
        qr_data = {
            "product_name": product_info.get("product_name_chinese", "拉面"),
            "manufacturer": product_info.get("manufacturer_chinese", "韩国食品公司"),
            "nutrition": product_info.get("nutrition", {}),
            "ingredients": product_info.get("ingredients", []),
            "allergy_info": product_info.get("allergy_ingredients", []),
            "digital_label": True
        }
        
        # QR코드 이미지 생성
        qr = qrcode.QRCode(version=1, box_size=3, border=2)
        qr.add_data(json.dumps(qr_data, ensure_ascii=False))
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img = qr_img.resize((80, 80))
        
        # QR코드를 메인 이미지에 붙이기
        image = draw._image
        image.paste(qr_img, (20, y_position))
        
        y_position += 90
        
        return y_position
    
    def _draw_fop_label(self, draw: ImageDraw.Draw, product_info: Dict, y_position: int) -> int:
        """미국 FOP 라벨 (2025년 제안)"""
        
        # FOP 라벨 제목
        draw.text((20, y_position), "Front of Package Label", fill=self.accent_color, font=self.header_font)
        y_position += 25
        
        # FOP 정보 박스
        nutrition_data = product_info.get("nutrition", {})
        
        # 포화지방 평가
        sat_fat = float(nutrition_data.get("포화지방", "5g").replace("g", ""))
        sat_fat_level = "High" if sat_fat > 5 else "Med" if sat_fat > 2 else "Low"
        
        # 나트륨 평가
        sodium = float(nutrition_data.get("나트륨", "800mg").replace("mg", ""))
        sodium_level = "High" if sodium > 600 else "Med" if sodium > 300 else "Low"
        
        # 첨가당 평가
        added_sugar = float(nutrition_data.get("당류", "5g").replace("g", ""))
        sugar_level = "High" if added_sugar > 10 else "Med" if added_sugar > 5 else "Low"
        
        # FOP 표시
        fop_items = [
            f"Saturated Fat: {sat_fat_level}",
            f"Sodium: {sodium_level}",
            f"Added Sugars: {sugar_level}"
        ]
        
        for item in fop_items:
            draw.text((20, y_position), item, fill=self.text_color, font=self.body_font)
            y_position += 20
        
        y_position += 10
        
        return y_position
    
    def _draw_storage_info(self, draw: ImageDraw.Draw, product_info: Dict, y_position: int) -> int:
        """보관 방법 (중국어) - 안전한 버전"""
        
        def safe_draw_text(draw, position, text, font, fill):
            try:
                if text is None:
                    text = ""
                elif not isinstance(text, str):
                    text = str(text)
                
                if not text.strip():
                    text = "N/A"
                
                draw.text(position, text, fill=fill, font=font)
            except Exception as e:
                print(f"⚠️ 텍스트 그리기 실패: {text} - {e}")
                try:
                    draw.text(position, "N/A", fill=fill, font=font)
                except:
                    pass
        
        # 제목
        safe_draw_text(draw, (20, y_position), "储存方法", self.header_font, self.accent_color)
        y_position += 25
        
        # 보관 방법
        storage_method = product_info.get("storage_method_chinese", "常温保存，避免阳光直射")
        safe_draw_text(draw, (20, y_position), storage_method, self.body_font, self.text_color)
        y_position += 25
        
        return y_position
    
    def _draw_storage_info_english(self, draw: ImageDraw.Draw, product_info: Dict, y_position: int) -> int:
        """보관 방법 (영어)"""
        
        # 제목
        draw.text((20, y_position), "Storage Instructions", fill=self.accent_color, font=self.header_font)
        y_position += 25
        
        # 보관 방법
        storage_method = product_info.get("storage_method_english", "Store at room temperature, avoid direct sunlight")
        draw.text((20, y_position), storage_method, fill=self.text_color, font=self.body_font)
        y_position += 25
        
        return y_position
    
    def _draw_manufacturer_details(self, draw: ImageDraw.Draw, product_info: Dict, y_position: int) -> int:
        """제조사 상세 정보 (중국어) - 안전한 버전"""
        
        def safe_draw_text(draw, position, text, font, fill):
            try:
                if text is None:
                    text = ""
                elif not isinstance(text, str):
                    text = str(text)
                
                if not text.strip():
                    text = "N/A"
                
                draw.text(position, text, fill=fill, font=font)
            except Exception as e:
                print(f"⚠️ 텍스트 그리기 실패: {text} - {e}")
                try:
                    draw.text(position, "N/A", fill=fill, font=font)
                except:
                    pass
        
        # 제조사 정보
        address = product_info.get("address_chinese", "韩国首尔江南区")
        phone = product_info.get("phone", "02-1234-5678")
        
        safe_draw_text(draw, (20, y_position), f"地址: {address}", self.small_font, self.text_color)
        y_position += 15
        safe_draw_text(draw, (20, y_position), f"电话: {phone}", self.small_font, self.text_color)
        y_position += 15
        
        return y_position
    
    def _draw_manufacturer_details_english(self, draw: ImageDraw.Draw, product_info: Dict, y_position: int) -> int:
        """제조사 상세 정보 (영어)"""
        
        # 제조사 정보
        address = product_info.get("address_english", "Seoul, South Korea")
        phone = product_info.get("phone", "02-1234-5678")
        
        draw.text((20, y_position), f"Address: {address}", fill=self.text_color, font=self.small_font)
        y_position += 15
        draw.text((20, y_position), f"Phone: {phone}", fill=self.text_color, font=self.small_font)
        y_position += 15
        
        return y_position
    
    def save_label(self, image: Image.Image, filename: str, output_dir: str = "advanced_labels"):
        """라벨 이미지 저장"""
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        image.save(filepath, "PNG")
        return filepath

def main():
    """고도화된 라벨 생성 테스트"""
    
    # 제품 정보 설정 (2027년 중국, 2025년 미국 규정 반영)
    product_info = {
        # 기본 정보
        "product_name": "한국 라면",
        "product_name_chinese": "韩国拉面",
        "product_name_english": "Korean Ramen",
        "manufacturer": "한국식품(주)",
        "manufacturer_chinese": "韩国食品有限公司",
        "manufacturer_english": "Korean Food Co., Ltd.",
        "origin": "대한민국",
        "expiry_date": "2026-12-31",
        
        # 영양성분 (1+6 체계)
        "nutrition": {
            "열량": "400 kcal",
            "단백질": "12g",
            "지방": "15g",
            "포화지방": "5g",
            "탄수화물": "60g",
            "당류": "5g",
            "나트륨": "800mg"
        },
        
        # 성분 정보
        "ingredients": [
            "面条(小麦粉, 盐)",
            "调味粉",
            "脱水蔬菜",
            "调味料",
            "香料"
        ],
        "ingredients_english": [
            "Noodles (Wheat Flour, Salt)",
            "Seasoning Powder",
            "Dehydrated Vegetables",
            "Seasoning",
            "Spices"
        ],
        
        # 알레르기 정보 (8대/9대)
        "allergy_ingredients": ["小麦", "大豆"],
        "allergy_ingredients_english": ["Wheat", "Soy"],
        
        # 보관 방법
        "storage_method_chinese": "常温保存，避免阳光直射",
        "storage_method_english": "Store at room temperature, avoid direct sunlight",
        
        # 제조사 정보
        "address_chinese": "韩国首尔江南区",
        "address_english": "Seoul, South Korea",
        "phone": "02-1234-5678"
    }
    
    print("🏷️ 고도화된 영양정보 라벨 생성 시스템")
    print("=" * 60)
    print("📋 2027년 중국 GB 7718-2025 규정 반영")
    print("📋 2025년 미국 FDA 새로운 라벨링 규정 반영")
    print("=" * 60)
    
    generator = AdvancedLabelGenerator()
    
    # 중국 2027년 라벨 생성
    print("\n🔧 중국 2027년 라벨 생성 중...")
    china_label = generator.generate_china_2027_label(product_info)
    china_filename = f"china_2027_label_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    china_path = generator.save_label(china_label, china_filename)
    print(f"✅ 중국 2027년 라벨 생성 완료: {china_path}")
    
    # 미국 2025년 라벨 생성
    print("\n🔧 미국 2025년 라벨 생성 중...")
    us_label = generator.generate_us_2025_label(product_info)
    us_filename = f"us_2025_label_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    us_path = generator.save_label(us_label, us_filename)
    print(f"✅ 미국 2025년 라벨 생성 완료: {us_path}")
    
    print(f"\n✅ 총 2개 라벨이 생성되었습니다:")
    print(f"   📁 {china_path}")
    print(f"   📁 {us_path}")
    
    print(f"\n🎯 주요 특징:")
    print(f"   🇨🇳 중국: 1+6 영양성분, 8대 알레르기, QR코드 디지털 라벨")
    print(f"   🇺🇸 미국: 13개 영양성분, 9대 알레르기, FOP 라벨")

if __name__ == "__main__":
    main() 