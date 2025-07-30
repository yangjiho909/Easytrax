#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 외부 AI 서비스 연동 시스템
- Google Cloud Vision API
- Azure Computer Vision API
- OpenAI API
- 로컬 AI 모델과 동일한 기능 제공
"""

import requests
import json
import base64
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import time

class ExternalAIServices:
    """외부 AI 서비스 연동 시스템"""
    
    def __init__(self):
        # API 키 설정 (환경변수에서 로드)
        self.google_api_key = os.environ.get('GOOGLE_CLOUD_API_KEY', '')
        self.azure_key = os.environ.get('AZURE_VISION_KEY', '')
        self.azure_endpoint = os.environ.get('AZURE_VISION_ENDPOINT', '')
        self.openai_api_key = os.environ.get('OPENAI_API_KEY', '')
        
        # 기본 설정
        self.timeout = 30
        self.max_retries = 3
    
    def extract_text_from_image(self, image_path: str) -> Dict[str, Any]:
        """이미지에서 텍스트 추출 (Google Cloud Vision API)"""
        try:
            if not self.google_api_key:
                return self._fallback_ocr(image_path)
            
            # 이미지를 base64로 인코딩
            with open(image_path, 'rb') as image_file:
                image_content = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Google Cloud Vision API 요청
            url = f"https://vision.googleapis.com/v1/images:annotate?key={self.google_api_key}"
            
            request_data = {
                "requests": [
                    {
                        "image": {
                            "content": image_content
                        },
                        "features": [
                            {
                                "type": "TEXT_DETECTION",
                                "maxResults": 10
                            },
                            {
                                "type": "LABEL_DETECTION",
                                "maxResults": 10
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(url, json=request_data, timeout=self.timeout)
            
            if response.status_code == 200:
                result = response.json()
                return self._parse_google_vision_result(result)
            else:
                print(f"⚠️ Google Vision API 실패: {response.status_code}")
                return self._fallback_ocr(image_path)
                
        except Exception as e:
            print(f"❌ Google Vision API 오류: {e}")
            return self._fallback_ocr(image_path)
    
    def analyze_nutrition_label(self, image_path: str) -> Dict[str, Any]:
        """영양 라벨 분석 (Azure Computer Vision + OpenAI)"""
        try:
            # Azure Computer Vision으로 텍스트 추출
            text_result = self._azure_ocr(image_path)
            
            if not text_result.get('text'):
                return self._fallback_nutrition_analysis()
            
            # OpenAI로 영양 정보 구조화
            if self.openai_api_key:
                return self._openai_nutrition_analysis(text_result['text'])
            else:
                return self._fallback_nutrition_analysis()
                
        except Exception as e:
            print(f"❌ 영양 라벨 분석 오류: {e}")
            return self._fallback_nutrition_analysis()
    
    def _azure_ocr(self, image_path: str) -> Dict[str, Any]:
        """Azure Computer Vision OCR"""
        try:
            if not self.azure_key or not self.azure_endpoint:
                return {'text': '', 'confidence': 0.0}
            
            # 이미지를 base64로 인코딩
            with open(image_path, 'rb') as image_file:
                image_content = image_file.read()
            
            url = f"{self.azure_endpoint}/vision/v3.2/read/analyze"
            headers = {
                'Ocp-Apim-Subscription-Key': self.azure_key,
                'Content-Type': 'application/octet-stream'
            }
            
            response = requests.post(url, headers=headers, data=image_content, timeout=self.timeout)
            
            if response.status_code == 202:
                # 비동기 처리 대기
                operation_url = response.headers['Operation-Location']
                time.sleep(2)
                
                headers = {'Ocp-Apim-Subscription-Key': self.azure_key}
                result_response = requests.get(operation_url, headers=headers, timeout=self.timeout)
                
                if result_response.status_code == 200:
                    result = result_response.json()
                    return self._parse_azure_result(result)
            
            return {'text': '', 'confidence': 0.0}
            
        except Exception as e:
            print(f"❌ Azure OCR 오류: {e}")
            return {'text': '', 'confidence': 0.0}
    
    def _openai_nutrition_analysis(self, text: str) -> Dict[str, Any]:
        """OpenAI로 영양 정보 구조화"""
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            prompt = f"""
            다음은 영양 라벨에서 추출한 텍스트입니다. JSON 형태로 구조화해주세요:
            
            {text}
            
            다음 형식으로 응답해주세요:
            {{
                "calories": "칼로리",
                "protein": "단백질",
                "fat": "지방",
                "carbohydrates": "탄수화물",
                "sodium": "나트륨",
                "sugar": "당류",
                "fiber": "식이섬유",
                "ingredients": ["성분1", "성분2"],
                "allergens": ["알레르기1", "알레르기2"]
            }}
            """
            
            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "영양 라벨 분석 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=self.timeout)
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # JSON 파싱
                try:
                    nutrition_data = json.loads(content)
                    return {
                        'success': True,
                        'nutrition_data': nutrition_data,
                        'raw_text': text,
                        'source': 'OpenAI GPT-3.5'
                    }
                except json.JSONDecodeError:
                    return self._fallback_nutrition_analysis()
            
            return self._fallback_nutrition_analysis()
            
        except Exception as e:
            print(f"❌ OpenAI 분석 오류: {e}")
            return self._fallback_nutrition_analysis()
    
    def _parse_google_vision_result(self, result: Dict) -> Dict[str, Any]:
        """Google Vision API 결과 파싱"""
        try:
            text_annotations = result.get('responses', [{}])[0].get('textAnnotations', [])
            label_annotations = result.get('responses', [{}])[0].get('labelAnnotations', [])
            
            # 텍스트 추출
            full_text = ""
            if text_annotations:
                full_text = text_annotations[0].get('description', '')
            
            # 라벨 추출
            labels = [label.get('description', '') for label in label_annotations]
            
            return {
                'success': True,
                'text': full_text,
                'labels': labels,
                'confidence': 0.9,
                'source': 'Google Cloud Vision'
            }
            
        except Exception as e:
            print(f"❌ Google Vision 결과 파싱 오류: {e}")
            return {'success': False, 'text': '', 'confidence': 0.0}
    
    def _parse_azure_result(self, result: Dict) -> Dict[str, Any]:
        """Azure OCR 결과 파싱"""
        try:
            text = ""
            if 'analyzeResult' in result and 'readResults' in result['analyzeResult']:
                for read_result in result['analyzeResult']['readResults']:
                    for line in read_result.get('lines', []):
                        text += line.get('text', '') + '\n'
            
            return {
                'text': text.strip(),
                'confidence': 0.8,
                'source': 'Azure Computer Vision'
            }
            
        except Exception as e:
            print(f"❌ Azure 결과 파싱 오류: {e}")
            return {'text': '', 'confidence': 0.0}
    
    def _fallback_ocr(self, image_path: str) -> Dict[str, Any]:
        """폴백 OCR (기본 텍스트 추출)"""
        return {
            'success': True,
            'text': 'OCR 서비스를 사용할 수 없습니다. 기본 텍스트를 사용합니다.',
            'labels': ['food', 'label'],
            'confidence': 0.5,
            'source': 'Fallback OCR'
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
            'raw_text': 'AI 서비스를 사용할 수 없습니다.',
            'source': 'Fallback Analysis'
        }

# 전역 인스턴스
external_ai = ExternalAIServices() 