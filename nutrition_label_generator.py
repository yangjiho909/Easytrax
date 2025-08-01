#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import requests
import json
from typing import Dict, List, Optional

class NutritionLabelGenerator:
    """제품 영양정보 라벨 이미지 생성 시스템"""
    
    def __init__(self):
        self.label_width = 400
        self.label_height = 600
        self.background_color = (255, 255, 255)  # 흰색
        self.text_color = (0, 0, 0)  # 검은색
        self.accent_color = (0, 100, 200)  # 파란색
        self.warning_color = (255, 0, 0)  # 빨간색
        
        # 폰트 설정 (다국어 지원 폰트 우선 사용)
        self._load_fonts()
    
    def _load_fonts(self):
        """폰트 로딩 (개선된 예외 처리)"""
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
                    self.title_font = ImageFont.truetype(font_path, 24)
                    self.header_font = ImageFont.truetype(font_path, 18)
                    self.body_font = ImageFont.truetype(font_path, 14)
                    self.small_font = ImageFont.truetype(font_path, 12)
                    print(f"✅ 다국어 폰트 로드 성공: {font_path}")
                    font_found = True
                    break
                except Exception as e:
                    print(f"❌ 폰트 로드 실패: {font_path} - {e}")
                    continue
            
            if not font_found:
                # 폰트를 찾을 수 없는 경우 기본 폰트 사용
                self.title_font = ImageFont.load_default()
                self.header_font = ImageFont.load_default()
                self.body_font = ImageFont.load_default()
                self.small_font = ImageFont.load_default()
                print("⚠️ 다국어 폰트를 찾을 수 없어 기본 폰트를 사용합니다.")
                
        except Exception as e:
            # 폰트를 찾을 수 없는 경우 기본 폰트 사용
            self.title_font = ImageFont.load_default()
            self.header_font = ImageFont.load_default()
            self.body_font = ImageFont.load_default()
            self.small_font = ImageFont.load_default()
            print(f"⚠️ 폰트 로드 실패: {e}")
    
    def _safe_draw_text(self, draw: ImageDraw.Draw, position: tuple, text: str, font: ImageFont.FreeTypeFont, fill: tuple):
        """안전한 텍스트 그리기 (중국어 지원)"""
        try:
            # 텍스트가 None이거나 빈 문자열인 경우 처리
            if text is None:
                text = ""
            elif not isinstance(text, str):
                text = str(text)
            
            # 중국어 텍스트가 비어있는 경우 기본값 사용
            if not text.strip():
                text = "N/A"
            
            draw.text(position, text, fill=fill, font=font)
        except Exception as e:
            print(f"⚠️ 텍스트 그리기 실패: {text} - {e}")
            # 실패한 경우 기본 텍스트로 대체
            try:
                draw.text(position, "N/A", fill=fill, font=font)
            except:
                pass
    
    def generate_nutrition_label(self, product_info: Dict, country: str = "한국") -> Image.Image:
        """영양정보 라벨 이미지 생성"""
        
        # 이미지 생성
        image = Image.new('RGB', (self.label_width, self.label_height), self.background_color)
        draw = ImageDraw.Draw(image)
        
        # 제목 영역
        self._draw_header(draw, product_info, country)
        
        # 영양성분표 영역
        self._draw_nutrition_table(draw, product_info)
        
        # 성분 정보 영역
        self._draw_ingredients(draw, product_info)
        
        # 알레르기 정보 영역
        self._draw_allergy_info(draw, product_info)
        
        # 보관 방법 영역
        self._draw_storage_info(draw, product_info)
        
        # 제조사 정보 영역
        self._draw_manufacturer_info(draw, product_info)
        
        return image
    
    def _draw_header(self, draw: ImageDraw.Draw, product_info: Dict, country: str):
        """헤더 영역 그리기"""
        y_position = 20
        
        # 제품명
        product_name = product_info.get("product_name", "제품명")
        self._safe_draw_text(draw, (20, y_position), product_name, self.title_font, self.accent_color)
        y_position += 40
        
        # 원산지
        origin = product_info.get("origin", "대한민국")
        self._safe_draw_text(draw, (20, y_position), f"원산지: {origin}", self.body_font, self.text_color)
        y_position += 25
        
        # 제조사
        manufacturer = product_info.get("manufacturer", "제조사")
        self._safe_draw_text(draw, (20, y_position), f"제조사: {manufacturer}", self.body_font, self.text_color)
        y_position += 25
        
        # 유통기한
        expiry_date = product_info.get("expiry_date", "유통기한")
        self._safe_draw_text(draw, (20, y_position), f"유통기한: {expiry_date}", self.body_font, self.text_color)
        y_position += 40
        
        # 구분선
        draw.line([(20, y_position), (self.label_width-20, y_position)], fill=self.accent_color, width=2)
        y_position += 20
    
    def _draw_nutrition_table(self, draw: ImageDraw.Draw, product_info: Dict):
        """영양성분표 그리기"""
        y_position = 150
        
        # 제목
        self._safe_draw_text(draw, (20, y_position), "영양성분표 (100g당)", self.header_font, self.accent_color)
        y_position += 30
        
        # 표 헤더
        self._safe_draw_text(draw, (20, y_position), "구분", self.body_font, self.text_color)
        self._safe_draw_text(draw, (200, y_position), "함량", self.body_font, self.text_color)
        y_position += 25
        
        # 구분선
        draw.line([(20, y_position), (self.label_width-20, y_position)], fill=self.text_color, width=1)
        y_position += 10
        
        # 영양성분 데이터
        nutrition_data = product_info.get("nutrition", {
            "열량": "400 kcal",
            "단백질": "12g",
            "지방": "15g",
            "탄수화물": "60g",
            "나트륨": "800mg",
            "당류": "5g"
        })
        
        for nutrient, value in nutrition_data.items():
            self._safe_draw_text(draw, (20, y_position), nutrient, self.body_font, self.text_color)
            self._safe_draw_text(draw, (200, y_position), value, self.body_font, self.text_color)
            y_position += 20
        
        y_position += 20
        
        # 구분선
        draw.line([(20, y_position), (self.label_width-20, y_position)], fill=self.accent_color, width=2)
        y_position += 20
        
        return y_position
    
    def _draw_ingredients(self, draw: ImageDraw.Draw, product_info: Dict):
        """성분 정보 그리기"""
        y_position = 350
        
        # 제목
        self._safe_draw_text(draw, (20, y_position), "성분", self.header_font, self.accent_color)
        y_position += 25
        
        # 성분 목록
        ingredients = product_info.get("ingredients", [
            "면류(밀가루, 소금)",
            "분말스프",
            "건조야채",
            "조미료",
            "향신료"
        ])
        
        for ingredient in ingredients:
            self._safe_draw_text(draw, (20, y_position), f"• {ingredient}", self.body_font, self.text_color)
            y_position += 18
        
        y_position += 10
        
        # 구분선
        draw.line([(20, y_position), (self.label_width-20, y_position)], fill=self.accent_color, width=1)
        y_position += 15
    
    def _draw_allergy_info(self, draw: ImageDraw.Draw, product_info: Dict):
        """알레르기 정보 그리기"""
        y_position = 450
        
        # 제목
        self._safe_draw_text(draw, (20, y_position), "알레르기 정보", self.header_font, self.warning_color)
        y_position += 25
        
        # 알레르기 성분
        allergy_ingredients = product_info.get("allergy_ingredients", ["밀", "대두"])
        
        if allergy_ingredients:
            allergy_text = "함유: " + ", ".join(allergy_ingredients)
            self._safe_draw_text(draw, (20, y_position), allergy_text, self.body_font, self.warning_color)
        else:
            self._safe_draw_text(draw, (20, y_position), "함유: 없음", self.body_font, self.text_color)
        
        y_position += 25
        
        # 주의사항
        self._safe_draw_text(draw, (20, y_position), "※ 알레르기 성분이 함유된 제품입니다.", self.small_font, self.warning_color)
        y_position += 20
    
    def _draw_storage_info(self, draw: ImageDraw.Draw, product_info: Dict):
        """보관 방법 그리기"""
        y_position = 520
        
        # 제목
        self._safe_draw_text(draw, (20, y_position), "보관방법", self.header_font, self.accent_color)
        y_position += 25
        
        # 보관 방법
        storage_method = product_info.get("storage_method", "직사광선을 피해 서늘한 곳에 보관")
        self._safe_draw_text(draw, (20, y_position), storage_method, self.body_font, self.text_color)
        y_position += 20
    
    def _draw_manufacturer_info(self, draw: ImageDraw.Draw, product_info: Dict):
        """제조사 정보 그리기"""
        y_position = 570
        
        # 제조사 정보
        manufacturer = product_info.get("manufacturer", "제조사")
        address = product_info.get("address", "주소")
        phone = product_info.get("phone", "연락처")
        
        self._safe_draw_text(draw, (20, y_position), f"제조사: {manufacturer}", self.small_font, self.text_color)
        y_position += 15
        self._safe_draw_text(draw, (20, y_position), f"주소: {address}", self.small_font, self.text_color)
        y_position += 15
        self._safe_draw_text(draw, (20, y_position), f"연락처: {phone}", self.small_font, self.text_color)
    
    def generate_chinese_nutrition_label(self, product_info: Dict) -> Image.Image:
        """중국어 영양정보 라벨 생성 (개선된 버전)"""
        
        try:
            print("🇨🇳 중국어 라벨 생성 시작")
            
            # 중국어 정보로 변환 (안전한 변환)
            chinese_info = self._convert_to_chinese_info(product_info)
            
            # 중국어 전용 폰트 로딩 시도
            self._load_chinese_fonts()
            
            # 라벨 생성
            image = self.generate_nutrition_label(chinese_info, "중국")
            
            print("✅ 중국어 라벨 생성 완료")
            return image
            
        except Exception as e:
            print(f"❌ 중국어 라벨 생성 실패: {e}")
            # 폴백: 영어로 생성
            print("🔄 영어로 폴백 라벨 생성")
            return self._generate_fallback_label(product_info)
    
    def _convert_to_chinese_info(self, product_info: Dict) -> Dict:
        """제품 정보를 중국어로 변환"""
        
        # 중국어 번역 매핑
        chinese_translations = {
            # 제품명
            "라면": "拉面", "김치": "泡菜", "된장": "大酱", "고추장": "辣椒酱",
            # 영양성분
            "열량": "热量", "단백질": "蛋白质", "지방": "脂肪", "탄수화물": "碳水化合物",
            "나트륨": "钠", "당류": "糖", "식이섬유": "膳食纤维",
            # 알레르기
            "밀": "小麦", "대두": "大豆", "우유": "牛奶", "계란": "鸡蛋",
            "땅콩": "花生", "견과류": "坚果", "생선": "鱼类", "조개류": "贝类",
            # 기타
            "성분": "成分", "알레르기 정보": "过敏信息", "보관방법": "储存方法",
            "제조사": "制造商", "원산지": "原产地", "유통기한": "保质期"
        }
        
        chinese_info = {}
        
        # 제품명 변환
        product_name = product_info.get("product_name", product_info.get("name", "라면"))
        chinese_info["product_name"] = chinese_translations.get(product_name, product_name)
        
        # 원산지
        origin = product_info.get("origin", "대한민국")
        chinese_info["origin"] = "韩国" if origin == "대한민국" else origin
        
        # 제조사
        manufacturer = product_info.get("manufacturer", "제조사")
        chinese_info["manufacturer"] = chinese_translations.get(manufacturer, manufacturer)
        
        # 유통기한
        expiry_date = product_info.get("expiry_date", "유통기한")
        chinese_info["expiry_date"] = expiry_date
        
        # 영양성분 변환
        nutrition = product_info.get("nutrition", {})
        chinese_nutrition = {}
        for key, value in nutrition.items():
            chinese_key = chinese_translations.get(key, key)
            chinese_nutrition[chinese_key] = value
        chinese_info["nutrition"] = chinese_nutrition
        
        # 성분 목록
        ingredients = product_info.get("ingredients", ["면류(밀가루, 소금)", "분말스프", "건조야채", "조미료", "향신료"])
        chinese_ingredients = []
        for ingredient in ingredients:
            # 간단한 중국어 변환
            if "면류" in ingredient:
                chinese_ingredients.append("面条(小麦粉, 盐)")
            elif "분말스프" in ingredient:
                chinese_ingredients.append("调味粉")
            elif "건조야채" in ingredient:
                chinese_ingredients.append("脱水蔬菜")
            elif "조미료" in ingredient:
                chinese_ingredients.append("调味料")
            elif "향신료" in ingredient:
                chinese_ingredients.append("香料")
            else:
                chinese_ingredients.append(ingredient)
        chinese_info["ingredients"] = chinese_ingredients
        
        # 알레르기 성분
        allergy_ingredients = product_info.get("allergy_ingredients", ["밀", "대두"])
        chinese_allergies = []
        for allergy in allergy_ingredients:
            chinese_allergy = chinese_translations.get(allergy, allergy)
            chinese_allergies.append(chinese_allergy)
        chinese_info["allergy_ingredients"] = chinese_allergies
        
        # 보관 방법
        storage_method = product_info.get("storage_method", "직사광선을 피해 서늘한 곳에 보관")
        chinese_info["storage_method"] = "常温保存，避免阳光直射"
        
        # 제조사 정보
        chinese_info["address"] = "韩国地址"
        chinese_info["phone"] = "韩国电话"
        
        return chinese_info
    
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
                    self.title_font = ImageFont.truetype(font_path, 24)
                    self.header_font = ImageFont.truetype(font_path, 18)
                    self.body_font = ImageFont.truetype(font_path, 14)
                    self.small_font = ImageFont.truetype(font_path, 12)
                    print(f"✅ 중국어 폰트 로드 성공: {font_path}")
                    return
                except:
                    continue
            
            print("⚠️ 중국어 폰트를 찾을 수 없어 기본 폰트를 사용합니다.")
            
        except Exception as e:
            print(f"⚠️ 중국어 폰트 로드 실패: {e}")
    
    def _generate_fallback_label(self, product_info: Dict) -> Image.Image:
        """폴백 라벨 생성 (영어)"""
        try:
            # 영어 정보로 변환
            english_info = {
                "product_name": product_info.get("product_name", "Korean Product"),
                "origin": "Republic of Korea",
                "manufacturer": product_info.get("manufacturer", "Korean Manufacturer"),
                "expiry_date": product_info.get("expiry_date", "2026-12-31"),
                "nutrition": product_info.get("nutrition", {}),
                "ingredients": product_info.get("ingredients", ["Ingredients"]),
                "allergy_ingredients": product_info.get("allergy_ingredients", ["Allergens"]),
                "storage_method": "Store in a cool, dry place",
                "address": "Korean Address",
                "phone": "Korean Phone"
            }
            
            return self.generate_nutrition_label(english_info, "미국")
            
        except Exception as e:
            print(f"❌ 폴백 라벨 생성도 실패: {e}")
            # 최종 폴백: 기본 이미지 생성
            image = Image.new('RGB', (self.label_width, self.label_height), self.background_color)
            draw = ImageDraw.Draw(image)
            self._safe_draw_text(draw, (20, 20), "Label Generation Failed", self.title_font, self.text_color)
            return image
    
    def save_label(self, image: Image.Image, filename: str, output_dir: str = "nutrition_labels"):
        """라벨 이미지 저장"""
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        image.save(filepath, "PNG")
        return filepath

class APIImageGenerator:
    """API 기반 이미지 생성 시스템"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
    
    def generate_with_dalle(self, prompt: str, size: str = "1024x1024") -> str:
        """DALL-E API를 사용한 이미지 생성"""
        
        if not self.api_key:
            return "❌ API 키가 필요합니다."
        
        url = "https://api.openai.com/v1/images/generations"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "dall-e-3",
            "prompt": prompt,
            "size": size,
            "quality": "standard",
            "n": 1
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            image_url = result["data"][0]["url"]
            
            # 이미지 다운로드
            img_response = requests.get(image_url)
            img_response.raise_for_status()
            
            # 파일로 저장
            filename = f"dalle_nutrition_label_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            with open(filename, "wb") as f:
                f.write(img_response.content)
            
            return f"✅ DALL-E 이미지 생성 완료: {filename}"
            
        except Exception as e:
            return f"❌ DALL-E API 오류: {e}"
    
    def generate_with_stable_diffusion(self, prompt: str, api_url: str = "http://localhost:7860") -> str:
        """Stable Diffusion API를 사용한 이미지 생성"""
        
        url = f"{api_url}/sdapi/v1/txt2img"
        
        data = {
            "prompt": prompt,
            "negative_prompt": "blurry, low quality, distorted",
            "steps": 20,
            "width": 512,
            "height": 768,
            "cfg_scale": 7.5
        }
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            
            result = response.json()
            image_data = result["images"][0]
            
            # base64 디코딩
            import base64
            image_bytes = base64.b64decode(image_data)
            
            # 파일로 저장
            filename = f"sd_nutrition_label_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            with open(filename, "wb") as f:
                f.write(image_bytes)
            
            return f"✅ Stable Diffusion 이미지 생성 완료: {filename}"
            
        except Exception as e:
            return f"❌ Stable Diffusion API 오류: {e}"

def main():
    """영양정보 라벨 생성 테스트"""
    
    # 제품 정보 설정
    product_info = {
        "product_name": "한국 라면",
        "origin": "대한민국",
        "manufacturer": "한국식품(주)",
        "expiry_date": "2026-12-31",
        "nutrition": {
            "열량": "400 kcal",
            "단백질": "12g",
            "지방": "15g",
            "탄수화물": "60g",
            "나트륨": "800mg",
            "당류": "5g"
        },
        "ingredients": [
            "면류(밀가루, 소금)",
            "분말스프",
            "건조야채",
            "조미료",
            "향신료"
        ],
        "allergy_ingredients": ["밀", "대두"],
        "storage_method": "직사광선을 피해 서늘한 곳에 보관",
        "address": "서울특별시 강남구 테헤란로 123",
        "phone": "02-1234-5678",
        # 중국어 정보
        "product_name_chinese": "拉面",
        "manufacturer_chinese": "韩国食品公司",
        "expiry_date_chinese": "2026年12月31日"
    }
    
    print("📋 영양정보 라벨 생성 시스템")
    print("=" * 50)
    
    # 로컬 이미지 생성
    generator = NutritionLabelGenerator()
    
    # 한국어 라벨 생성
    korean_label = generator.generate_nutrition_label(product_info, "한국")
    korean_filename = f"nutrition_label_korean_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    korean_path = generator.save_label(korean_label, korean_filename)
    print(f"✅ 한국어 라벨 생성: {korean_path}")
    
    # 중국어 라벨 생성
    chinese_label = generator.generate_chinese_nutrition_label(product_info)
    chinese_filename = f"nutrition_label_chinese_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    chinese_path = generator.save_label(chinese_label, chinese_filename)
    print(f"✅ 중국어 라벨 생성: {chinese_path}")
    
    # API 이미지 생성 예시 (API 키가 있는 경우)
    api_generator = APIImageGenerator()
    
    # DALL-E 프롬프트 예시
    dalle_prompt = """
    Create a professional nutrition facts label for Korean ramen noodles. 
    Include: product name "Korean Ramen", nutrition facts table, ingredients list, 
    allergy information, storage instructions. Use clean, modern design with 
    white background, black text, and blue accents. Make it look like an official 
    food label that would be printed on packaging.
    """
    
    print(f"\n🤖 API 이미지 생성 예시:")
    print(f"DALL-E 프롬프트: {dalle_prompt[:100]}...")
    print("💡 API 키를 설정하면 실제 이미지 생성이 가능합니다.")

if __name__ == "__main__":
    main() 