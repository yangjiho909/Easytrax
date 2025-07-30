#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 AI API 기반 고성능 OCR 시스템
- OpenAI GPT-4 Vision
- Azure Computer Vision
- Google Cloud Vision
- 다중 AI 엔진 통합 및 앙상블
- 한글 특화 최적화
"""

import os
import re
import json
import base64
import requests
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime
import cv2
import numpy as np
from PIL import Image
import io

# AI API 라이브러리들
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ OpenAI를 사용할 수 없습니다.")

try:
    from azure.cognitiveservices.vision.computervision import ComputerVisionClient
    from msrest.authentication import CognitiveServicesCredentials
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    print("⚠️ Azure Computer Vision을 사용할 수 없습니다.")

try:
    from google.cloud import vision
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("⚠️ Google Cloud Vision을 사용할 수 없습니다.")

class AIEnhancedOCR:
    """AI API 기반 고성능 OCR 시스템"""
    
    def __init__(self):
        # 로깅 설정
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # AI API 클라이언트 초기화
        self.openai_client = self._initialize_openai()
        self.azure_client = self._initialize_azure()
        self.google_client = self._initialize_google()
        
        # OCR 결과 캐시
        self.result_cache = {}
        
        # 한글 특화 프롬프트
        self.korean_prompts = {
            "nutrition_label": """
다음은 한국 식품의 영양정보 라벨입니다. 다음 정보를 정확히 추출해주세요:

1. 제품명 (Product Name)
2. 제조사 (Manufacturer)
3. 원산지 (Origin)
4. 유통기한 (Expiry Date)
5. 영양성분 (Nutrition Facts):
   - 칼로리 (Calories)
   - 단백질 (Protein)
   - 지방 (Fat)
   - 탄수화물 (Carbohydrates)
   - 나트륨 (Sodium)
   - 당류 (Sugar)
   - 식이섬유 (Fiber)
6. 알레르기 정보 (Allergy Information)
7. 성분 목록 (Ingredients)

JSON 형식으로 응답해주세요:
{
    "product_name": "제품명",
    "manufacturer": "제조사",
    "origin": "원산지",
    "expiry_date": "YYYY-MM-DD",
    "nutrition": {
        "calories": 숫자,
        "protein": 숫자,
        "fat": 숫자,
        "carbs": 숫자,
        "sodium": 숫자,
        "sugar": 숫자,
        "fiber": 숫자
    },
    "allergies": ["알레르기1", "알레르기2"],
    "ingredients": "성분 목록"
}
""",
            "general_text": """
이 이미지에서 한국어 텍스트를 정확히 추출해주세요. 
특히 다음 정보들을 주의깊게 확인해주세요:
- 제품명, 브랜드명
- 영양성분 정보
- 날짜 정보
- 숫자와 단위
- 알레르기 정보

추출된 텍스트를 깔끔하게 정리해서 반환해주세요.
"""
        }
    
    def _initialize_openai(self) -> Optional[Any]:
        """OpenAI 클라이언트 초기화"""
        if not OPENAI_AVAILABLE:
            return None
        
        try:
            # 환경변수에서 API 키 확인
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                self.logger.warning("⚠️ OPENAI_API_KEY 환경변수가 설정되지 않았습니다.")
                return None
            
            client = openai.OpenAI(api_key=api_key)
            self.logger.info("✅ OpenAI 클라이언트 초기화 성공")
            return client
        except Exception as e:
            self.logger.warning(f"❌ OpenAI 초기화 실패: {e}")
            return None
    
    def _initialize_azure(self) -> Optional[Any]:
        """Azure Computer Vision 클라이언트 초기화"""
        if not AZURE_AVAILABLE:
            return None
        
        try:
            # 환경변수에서 API 키와 엔드포인트 확인
            api_key = os.getenv('AZURE_VISION_KEY')
            endpoint = os.getenv('AZURE_VISION_ENDPOINT')
            
            if not api_key or not endpoint:
                self.logger.warning("⚠️ AZURE_VISION_KEY 또는 AZURE_VISION_ENDPOINT 환경변수가 설정되지 않았습니다.")
                return None
            
            client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(api_key))
            self.logger.info("✅ Azure Computer Vision 클라이언트 초기화 성공")
            return client
        except Exception as e:
            self.logger.warning(f"❌ Azure Computer Vision 초기화 실패: {e}")
            return None
    
    def _initialize_google(self) -> Optional[Any]:
        """Google Cloud Vision 클라이언트 초기화"""
        if not GOOGLE_AVAILABLE:
            return None
        
        try:
            # 환경변수에서 서비스 계정 키 확인
            credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            if not credentials_path or not os.path.exists(credentials_path):
                self.logger.warning("⚠️ GOOGLE_APPLICATION_CREDENTIALS 환경변수가 설정되지 않았습니다.")
                return None
            
            client = vision.ImageAnnotatorClient()
            self.logger.info("✅ Google Cloud Vision 클라이언트 초기화 성공")
            return client
        except Exception as e:
            self.logger.warning(f"❌ Google Cloud Vision 초기화 실패: {e}")
            return None
    
    def extract_with_openai(self, image_path: str, prompt_type: str = "nutrition_label") -> Dict:
        """OpenAI GPT-4 Vision을 사용한 텍스트 추출"""
        if not self.openai_client:
            return {}
        
        try:
            # 이미지를 base64로 인코딩
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # 프롬프트 선택
            prompt = self.korean_prompts.get(prompt_type, self.korean_prompts["general_text"])
            
            # GPT-4 Vision API 호출
            response = self.openai_client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.1
            )
            
            # 응답 파싱
            content = response.choices[0].message.content
            
            # JSON 응답인 경우 파싱
            try:
                if content.strip().startswith('{'):
                    return json.loads(content)
                else:
                    # 일반 텍스트인 경우 구조화
                    return self._parse_text_to_structure(content)
            except json.JSONDecodeError:
                return self._parse_text_to_structure(content)
                
        except Exception as e:
            self.logger.error(f"❌ OpenAI OCR 실패: {e}")
            return {}
    
    def extract_with_azure(self, image_path: str) -> Dict:
        """Azure Computer Vision을 사용한 텍스트 추출"""
        if not self.azure_client:
            return {}
        
        try:
            # 이미지 파일 열기
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
            
            # OCR 실행
            result = self.azure_client.recognize_printed_text_in_stream(image_data)
            
            # 텍스트 추출
            extracted_text = ""
            for region in result.regions:
                for line in region.lines:
                    for word in line.words:
                        extracted_text += word.text + " "
                    extracted_text += "\n"
            
            # 구조화된 정보 추출
            return self._extract_structured_info(extracted_text)
            
        except Exception as e:
            self.logger.error(f"❌ Azure OCR 실패: {e}")
            return {}
    
    def extract_with_google(self, image_path: str) -> Dict:
        """Google Cloud Vision을 사용한 텍스트 추출"""
        if not self.google_client:
            return {}
        
        try:
            # 이미지 파일 읽기
            with open(image_path, "rb") as image_file:
                content = image_file.read()
            
            # 이미지 객체 생성
            image = vision.Image(content=content)
            
            # OCR 실행
            response = self.google_client.text_detection(image=image)
            texts = response.text_annotations
            
            if not texts:
                return {}
            
            # 전체 텍스트 추출
            extracted_text = texts[0].description
            
            # 구조화된 정보 추출
            return self._extract_structured_info(extracted_text)
            
        except Exception as e:
            self.logger.error(f"❌ Google OCR 실패: {e}")
            return {}
    
    def _extract_structured_info(self, text: str) -> Dict:
        """텍스트에서 구조화된 정보 추출"""
        info = {}
        
        # 제품명 추출
        product_patterns = [
            r"제품명[:\s]*([^\n\r]+)",
            r"상품명[:\s]*([^\n\r]+)",
            r"Product[:\s]*([^\n\r]+)",
            r"Name[:\s]*([^\n\r]+)"
        ]
        
        for pattern in product_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info['product_name'] = match.group(1).strip()
                break
        
        # 영양성분 추출
        nutrition = {}
        nutrition_patterns = {
            'calories': [r"칼로리[:\s]*(\d+)", r"Calories[:\s]*(\d+)"],
            'protein': [r"단백질[:\s]*(\d+\.?\d*)", r"Protein[:\s]*(\d+\.?\d*)"],
            'fat': [r"지방[:\s]*(\d+\.?\d*)", r"Fat[:\s]*(\d+\.?\d*)"],
            'carbs': [r"탄수화물[:\s]*(\d+\.?\d*)", r"Carbohydrates[:\s]*(\d+\.?\d*)"],
            'sodium': [r"나트륨[:\s]*(\d+)", r"Sodium[:\s]*(\d+)"],
            'sugar': [r"당류[:\s]*(\d+\.?\d*)", r"Sugar[:\s]*(\d+\.?\d*)"],
            'fiber': [r"식이섬유[:\s]*(\d+\.?\d*)", r"Fiber[:\s]*(\d+\.?\d*)"]
        }
        
        for nutrient, patterns in nutrition_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        nutrition[nutrient] = float(match.group(1))
                    except ValueError:
                        nutrition[nutrient] = match.group(1)
                    break
        
        if nutrition:
            info['nutrition'] = nutrition
        
        # 알레르기 정보 추출
        allergy_patterns = [
            r"알레르기[:\s]*([^\n\r]+)",
            r"Allergy[:\s]*([^\n\r]+)",
            r"알레르기[:\s]*([가-힣\s,]+)"
        ]
        
        for pattern in allergy_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                allergies = [item.strip() for item in match.group(1).split(',')]
                info['allergies'] = allergies
                break
        
        # 성분 정보 추출
        ingredient_patterns = [
            r"성분[:\s]*([^\n\r]+)",
            r"Ingredients[:\s]*([^\n\r]+)",
            r"원료[:\s]*([^\n\r]+)"
        ]
        
        for pattern in ingredient_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                info['ingredients'] = match.group(1).strip()
                break
        
        return info
    
    def _parse_text_to_structure(self, text: str) -> Dict:
        """일반 텍스트를 구조화된 정보로 변환"""
        return self._extract_structured_info(text)
    
    def extract_label_info(self, image_path: str, use_ai_apis: bool = True) -> Dict:
        """AI API를 활용한 라벨 정보 추출"""
        self.logger.info(f"🤖 AI OCR 시작: {image_path}")
        
        results = {}
        
        # 1. OpenAI GPT-4 Vision (가장 정확)
        if use_ai_apis and self.openai_client:
            self.logger.info("🔍 OpenAI GPT-4 Vision 처리 중...")
            openai_result = self.extract_with_openai(image_path, "nutrition_label")
            if openai_result:
                results['openai'] = openai_result
                self.logger.info("✅ OpenAI OCR 완료")
        
        # 2. Azure Computer Vision
        if use_ai_apis and self.azure_client:
            self.logger.info("🔍 Azure Computer Vision 처리 중...")
            azure_result = self.extract_with_azure(image_path)
            if azure_result:
                results['azure'] = azure_result
                self.logger.info("✅ Azure OCR 완료")
        
        # 3. Google Cloud Vision
        if use_ai_apis and self.google_client:
            self.logger.info("🔍 Google Cloud Vision 처리 중...")
            google_result = self.extract_with_google(image_path)
            if google_result:
                results['google'] = google_result
                self.logger.info("✅ Google OCR 완료")
        
        # 결과 통합 및 앙상블
        if results:
            final_result = self._ensemble_results(results)
            self.logger.info(f"✅ AI OCR 완료: {len(results)}개 엔진 사용")
            return final_result
        else:
            self.logger.warning("⚠️ 사용 가능한 AI OCR 엔진이 없습니다.")
            return {}
    
    def _ensemble_results(self, results: Dict) -> Dict:
        """여러 AI 엔진의 결과를 앙상블하여 최적 결과 생성"""
        if not results:
            return {}
        
        # OpenAI 결과를 기본으로 사용
        if 'openai' in results:
            base_result = results['openai'].copy()
        else:
            # OpenAI가 없으면 첫 번째 결과 사용
            base_result = list(results.values())[0].copy()
        
        # 다른 엔진들의 결과로 보완
        for engine, result in results.items():
            if engine == 'openai':
                continue
            
            # 제품명이 없으면 추가
            if not base_result.get('product_name') and result.get('product_name'):
                base_result['product_name'] = result['product_name']
            
            # 영양성분 보완
            if 'nutrition' in result:
                if 'nutrition' not in base_result:
                    base_result['nutrition'] = {}
                
                for nutrient, value in result['nutrition'].items():
                    if nutrient not in base_result['nutrition']:
                        base_result['nutrition'][nutrient] = value
            
            # 알레르기 정보 보완
            if not base_result.get('allergies') and result.get('allergies'):
                base_result['allergies'] = result['allergies']
            
            # 성분 정보 보완
            if not base_result.get('ingredients') and result.get('ingredients'):
                base_result['ingredients'] = result['ingredients']
        
        return base_result

# 전역 인스턴스
ai_ocr = AIEnhancedOCR() 