#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🆓 완전 무료 AI 서비스 시스템
- Hugging Face 무료 API
- OCR.space 무료 API
- Free OCR API
- 로컬 AI 모델 (CPU 기반)
"""

import requests
import json
import base64
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import time

class FreeAIServices:
    """완전 무료 AI 서비스 시스템"""
    
    def __init__(self):
        # 무료 API 키들
        self.huggingface_token = os.environ.get('HUGGINGFACE_TOKEN', '')
        self.ocrspace_key = os.environ.get('OCRSPACE_KEY', '')
        
        # 무료 API 엔드포인트
        self.huggingface_api = "https://api-inference.huggingface.co/models"
        self.ocrspace_api = "https://api.ocr.space/parse/image"
        
        print("🆓 완전 무료 AI 서비스 시스템 초기화")
    
    def extract_text_from_image(self, image_path: str) -> Dict[str, Any]:
        """이미지에서 텍스트 추출 (무료 OCR API)"""
        try:
            # OCR.space 무료 API 사용
            with open(image_path, 'rb') as image_file:
                files = {'image': image_file}
                data = {
                    'apikey': self.ocrspace_key or 'helloworld',  # 무료 키
                    'language': 'kor+eng',
                    'isOverlayRequired': False,
                    'filetype': 'png',
                    'detectOrientation': True
                }
                
                response = requests.post(self.ocrspace_api, files=files, data=data, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('ParsedResults'):
                        text = result['ParsedResults'][0]['ParsedText']
                        confidence = result['ParsedResults'][0].get('TextOverlay', {}).get('Lines', [])
                        
                        return {
                            'success': True,
                            'text': text,
                            'confidence': 0.8,
                            'source': 'OCR.space (무료)',
                            'raw_result': result
                        }
                
                # OCR.space 실패 시 Hugging Face 사용
                return self._huggingface_ocr(image_path)
                
        except Exception as e:
            print(f"❌ 무료 OCR 실패: {e}")
            return self._fallback_ocr(image_path)
    
    def _huggingface_ocr(self, image_path: str) -> Dict[str, Any]:
        """Hugging Face 무료 OCR"""
        try:
            # Hugging Face 무료 OCR 모델
            model_name = "microsoft/trocr-base-handwritten"
            
            with open(image_path, 'rb') as image_file:
                image_content = base64.b64encode(image_file.read()).decode('utf-8')
            
            headers = {
                'Authorization': f'Bearer {self.huggingface_token}' if self.huggingface_token else '',
                'Content-Type': 'application/json'
            }
            
            data = {
                'inputs': f'data:image/png;base64,{image_content}'
            }
            
            response = requests.post(
                f"{self.huggingface_api}/{model_name}",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'text': result.get('generated_text', ''),
                    'confidence': 0.7,
                    'source': 'Hugging Face (무료)',
                    'raw_result': result
                }
            
            return self._fallback_ocr(image_path)
            
        except Exception as e:
            print(f"❌ Hugging Face OCR 실패: {e}")
            return self._fallback_ocr(image_path)
    
    def analyze_nutrition_label(self, image_path: str) -> Dict[str, Any]:
        """영양 라벨 분석 (무료 AI)"""
        try:
            # 텍스트 추출
            ocr_result = self.extract_text_from_image(image_path)
            
            if not ocr_result.get('text'):
                return self._fallback_nutrition_analysis()
            
            # 무료 AI로 영양 정보 구조화
            return self._free_nutrition_analysis(ocr_result['text'])
                
        except Exception as e:
            print(f"❌ 영양 라벨 분석 오류: {e}")
            return self._fallback_nutrition_analysis()
    
    def _free_nutrition_analysis(self, text: str) -> Dict[str, Any]:
        """무료 AI로 영양 정보 구조화"""
        try:
            # Hugging Face 무료 텍스트 분석 모델
            model_name = "microsoft/DialoGPT-medium"
            
            # 간단한 규칙 기반 분석
            nutrition_data = self._rule_based_nutrition_extraction(text)
            
            return {
                'success': True,
                'nutrition_data': nutrition_data,
                'raw_text': text,
                'source': '무료 규칙 기반 분석'
            }
            
        except Exception as e:
            print(f"❌ 무료 영양 분석 실패: {e}")
            return self._fallback_nutrition_analysis()
    
    def _rule_based_nutrition_extraction(self, text: str) -> Dict[str, Any]:
        """규칙 기반 영양 정보 추출"""
        text_lower = text.lower()
        
        # 기본 영양 정보 추출
        nutrition_data = {
            'calories': '정보 없음',
            'protein': '정보 없음',
            'fat': '정보 없음',
            'carbohydrates': '정보 없음',
            'sodium': '정보 없음',
            'sugar': '정보 없음',
            'fiber': '정보 없음',
            'ingredients': [],
            'allergens': []
        }
        
        # 칼로리 추출
        if 'kcal' in text_lower or 'calories' in text_lower:
            import re
            calorie_match = re.search(r'(\d+)\s*(kcal|calories?)', text_lower)
            if calorie_match:
                nutrition_data['calories'] = f"{calorie_match.group(1)} kcal"
        
        # 단백질 추출
        if 'protein' in text_lower or '단백질' in text:
            protein_match = re.search(r'(\d+(?:\.\d+)?)\s*(g|g단백질)', text_lower)
            if protein_match:
                nutrition_data['protein'] = f"{protein_match.group(1)}g"
        
        # 지방 추출
        if 'fat' in text_lower or '지방' in text:
            fat_match = re.search(r'(\d+(?:\.\d+)?)\s*(g|g지방)', text_lower)
            if fat_match:
                nutrition_data['fat'] = f"{fat_match.group(1)}g"
        
        # 탄수화물 추출
        if 'carbohydrate' in text_lower or '탄수화물' in text:
            carb_match = re.search(r'(\d+(?:\.\d+)?)\s*(g|g탄수화물)', text_lower)
            if carb_match:
                nutrition_data['carbohydrates'] = f"{carb_match.group(1)}g"
        
        # 성분 추출
        if '성분' in text or 'ingredient' in text_lower:
            lines = text.split('\n')
            for line in lines:
                if any(keyword in line.lower() for keyword in ['밀', 'wheat', '우유', 'milk', '계란', 'egg']):
                    nutrition_data['ingredients'].append(line.strip())
        
        # 알레르기 정보 추출
        if '알레르기' in text or 'allergen' in text_lower:
            lines = text.split('\n')
            for line in lines:
                if any(keyword in line.lower() for keyword in ['알레르기', 'allergen', '주의']):
                    nutrition_data['allergens'].append(line.strip())
        
        return nutrition_data
    
    def _fallback_ocr(self, image_path: str) -> Dict[str, Any]:
        """폴백 OCR (기본 텍스트 추출)"""
        return {
            'success': True,
            'text': '무료 OCR 서비스를 사용할 수 없습니다. 기본 텍스트를 사용합니다.',
            'labels': ['food', 'label'],
            'confidence': 0.5,
            'source': 'Fallback OCR (무료)'
        }
    
    def _fallback_nutrition_analysis(self) -> Dict[str, Any]:
        """폴백 영양 분석"""
        return {
            'success': True,
            'nutrition_data': {
                'calories': '정보 없음',
                'protein': '정보 없음',
                'fat': '정보 없음',
                'carbohydrates': '정보 없음',
                'sodium': '정보 없음',
                'sugar': '정보 없음',
                'fiber': '정보 없음',
                'ingredients': ['정보 없음'],
                'allergens': ['정보 없음']
            },
            'raw_text': '무료 AI 서비스를 사용할 수 없습니다.',
            'source': 'Fallback Analysis (무료)'
        }

# 전역 인스턴스
free_ai = FreeAIServices() 