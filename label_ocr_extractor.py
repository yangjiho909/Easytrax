#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🏷️ OCR 기반 라벨 정보 추출 시스템
- 다중 OCR 엔진 지원 (Tesseract, EasyOCR)
- 정규표현식 기반 정보 추출
- AI 기반 NER 모델 통합
- 데이터 정규화 및 검증
- 한글 우선 인식 및 다국어 번역 지원
"""

import os
import re
import cv2
import numpy as np
from PIL import Image
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import logging

# OCR 라이브러리들
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("⚠️ Tesseract를 사용할 수 없습니다.")

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    print("⚠️ EasyOCR을 사용할 수 없습니다.")

# 번역 라이브러리
try:
    from deep_translator import GoogleTranslator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False
    print("⚠️ Deep Translator를 사용할 수 없습니다.")

# AI/ML 라이브러리들
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    print("⚠️ spaCy를 사용할 수 없습니다.")

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️ Transformers를 사용할 수 없습니다.")

# AI API 통합
try:
    from ai_enhanced_ocr import ai_ocr
    AI_API_AVAILABLE = True
except ImportError:
    AI_API_AVAILABLE = False
    print("⚠️ AI API를 사용할 수 없습니다.")

class LabelOCRExtractor:
    """OCR 기반 라벨 정보 추출기 (한글 우선 + 번역 지원)"""
    
    def __init__(self):
        # 로깅 설정 (먼저 설정)
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # OCR 엔진 초기화
        self.ocr_engines = self._initialize_ocr_engines()
        self.ner_model = self._initialize_ner_model()
        self.extraction_patterns = self._load_extraction_patterns()
        self.data_normalizer = DataNormalizer()
        
        # 번역기 초기화
        self.translator = self._initialize_translator()
        
        # AI API 사용 여부
        self.use_ai_apis = AI_API_AVAILABLE
    
    def _initialize_translator(self) -> Optional[Any]:
        """번역기 초기화"""
        if TRANSLATOR_AVAILABLE:
            try:
                # Deep Translator는 인스턴스 생성이 필요 없음
                self.logger.info("✅ Deep Translator 초기화 성공")
                return True
            except Exception as e:
                self.logger.warning(f"❌ Deep Translator 초기화 실패: {e}")
        return None
    
    def _initialize_ocr_engines(self) -> Dict:
        """OCR 엔진 초기화 (한글 우선)"""
        engines = {}
        
        # Tesseract 초기화
        if TESSERACT_AVAILABLE:
            try:
                # Tesseract 경로 설정 (Windows)
                if os.name == 'nt':
                    # 여러 가능한 경로 시도
                    possible_paths = [
                        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                        r'C:\Users\양지호\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
                    ]
                    
                    tesseract_found = False
                    for path in possible_paths:
                        if os.path.exists(path):
                            pytesseract.pytesseract.tesseract_cmd = path
                            tesseract_found = True
                            break
                    
                    if not tesseract_found:
                        raise FileNotFoundError("Tesseract 실행 파일을 찾을 수 없습니다.")
                
                # 테스트 실행
                test_result = pytesseract.get_tesseract_version()
                engines['tesseract'] = {
                    'available': True,
                    'version': str(test_result),
                    'languages': ['kor', 'eng', 'chi_sim']  # 한국어 우선
                }
                self.logger.info(f"✅ Tesseract 초기화 성공: {test_result}")
            except Exception as e:
                engines['tesseract'] = {'available': False, 'error': str(e)}
                self.logger.warning(f"❌ Tesseract 초기화 실패: {e}")
        
        # EasyOCR 초기화 (한국어 우선)
        if EASYOCR_AVAILABLE:
            try:
                # 한국어를 첫 번째 언어로 설정
                engines['easyocr'] = {
                    'available': True,
                    'languages': ['ko', 'en', 'ch_sim'],
                    'reader': easyocr.Reader(['ko', 'en', 'ch_sim'])  # 한국어 우선
                }
                self.logger.info("✅ EasyOCR 초기화 성공 (한국어 우선)")
            except Exception as e:
                # 실패 시 한국어와 영어만 사용
                try:
                    engines['easyocr'] = {
                        'available': True,
                        'languages': ['ko', 'en'],
                        'reader': easyocr.Reader(['ko', 'en'])
                    }
                    self.logger.info("✅ EasyOCR 초기화 성공 (한국어+영어)")
                except Exception as e2:
                    engines['easyocr'] = {'available': False, 'error': str(e2)}
                    self.logger.warning(f"❌ EasyOCR 초기화 실패: {e2}")
        
        # 최소 하나의 OCR 엔진이 사용 가능한지 확인
        available_engines = [name for name, config in engines.items() if config.get('available', False)]
        if not available_engines:
            self.logger.error("❌ 사용 가능한 OCR 엔진이 없습니다.")
        else:
            self.logger.info(f"✅ 사용 가능한 OCR 엔진: {', '.join(available_engines)}")
        
        return engines
    
    def _initialize_ner_model(self) -> Optional[Any]:
        """NER 모델 초기화"""
        if SPACY_AVAILABLE:
            try:
                # 한국어 모델 로드 시도
                try:
                    nlp = spacy.load("ko_core_news_sm")
                except OSError:
                    # 한국어 모델이 없으면 영어 모델 사용
                    nlp = spacy.load("en_core_web_sm")
                
                self.logger.info("✅ spaCy NER 모델 초기화 성공")
                return nlp
            except Exception as e:
                self.logger.warning(f"❌ spaCy NER 모델 초기화 실패: {e}")
        
        if TRANSFORMERS_AVAILABLE:
            try:
                # Transformers 기반 NER 파이프라인
                ner_pipeline = pipeline("ner", model="dslim/bert-base-NER")
                self.logger.info("✅ Transformers NER 모델 초기화 성공")
                return ner_pipeline
            except Exception as e:
                self.logger.warning(f"❌ Transformers NER 모델 초기화 실패: {e}")
        
        return None
    
    def _load_extraction_patterns(self) -> Dict:
        """정보 추출 패턴 로딩"""
        return {
            # 제품명 패턴
            "product_name": [
                r"제품명[:\s]*([^\n\r]+)",
                r"상품명[:\s]*([^\n\r]+)",
                r"Product[:\s]*([^\n\r]+)",
                r"Name[:\s]*([^\n\r]+)"
            ],
            
            # 제조사 패턴
            "manufacturer": [
                r"제조사[:\s]*([^\n\r]+)",
                r"제조원[:\s]*([^\n\r]+)",
                r"Manufacturer[:\s]*([^\n\r]+)",
                r"Made by[:\s]*([^\n\r]+)",
                r"Producer[:\s]*([^\n\r]+)"
            ],
            
            # 원산지 패턴
            "origin": [
                r"원산지[:\s]*([^\n\r]+)",
                r"원산국[:\s]*([^\n\r]+)",
                r"Origin[:\s]*([^\n\r]+)",
                r"Made in[:\s]*([^\n\r]+)"
            ],
            
            # 유통기한 패턴
            "expiry_date": [
                r"유통기한[:\s]*(\d{4}[-\/]\d{1,2}[-\/]\d{1,2})",
                r"사용기한[:\s]*(\d{4}[-\/]\d{1,2}[-\/]\d{1,2})",
                r"Expiry[:\s]*(\d{4}[-\/]\d{1,2}[-\/]\d{1,2})",
                r"Best before[:\s]*(\d{4}[-\/]\d{1,2}[-\/]\d{1,2})",
                r"(\d{4}[-\/]\d{1,2}[-\/]\d{1,2})까지"
            ],
            
            # 영양성분 패턴
            "nutrition": {
                "calories": [
                    r"열량[:\s]*(\d+(?:\.\d+)?)\s*(?:kcal|칼로리)",
                    r"Calories[:\s]*(\d+(?:\.\d+)?)\s*(?:kcal|cal)",
                    r"에너지[:\s]*(\d+(?:\.\d+)?)\s*(?:kcal|칼로리)"
                ],
                "protein": [
                    r"단백질[:\s]*(\d+(?:\.\d+)?)\s*(?:g|그램)",
                    r"Protein[:\s]*(\d+(?:\.\d+)?)\s*(?:g|gram)"
                ],
                "fat": [
                    r"지방[:\s]*(\d+(?:\.\d+)?)\s*(?:g|그램)",
                    r"Fat[:\s]*(\d+(?:\.\d+)?)\s*(?:g|gram)"
                ],
                "carbohydrates": [
                    r"탄수화물[:\s]*(\d+(?:\.\d+)?)\s*(?:g|그램)",
                    r"Carbohydrate[:\s]*(\d+(?:\.\d+)?)\s*(?:g|gram)"
                ],
                "sodium": [
                    r"나트륨[:\s]*(\d+(?:\.\d+)?)\s*(?:mg|밀리그램)",
                    r"Sodium[:\s]*(\d+(?:\.\d+)?)\s*(?:mg|milligram)"
                ],
                "sugar": [
                    r"당류[:\s]*(\d+(?:\.\d+)?)\s*(?:g|그램)",
                    r"Sugar[:\s]*(\d+(?:\.\d+)?)\s*(?:g|gram)"
                ]
            },
            
            # 성분 패턴
            "ingredients": [
                r"성분[:\s]*([^\n\r]+)",
                r"원료[:\s]*([^\n\r]+)",
                r"Ingredients[:\s]*([^\n\r]+)",
                r"Contains[:\s]*([^\n\r]+)"
            ],
            
            # 알레르기 정보 패턴
            "allergies": [
                r"알레르기[:\s]*([^\n\r]+)",
                r"알레르기성분[:\s]*([^\n\r]+)",
                r"Allergy[:\s]*([^\n\r]+)",
                r"Contains[:\s]*([^\n\r]+)"
            ],
            
            # 바코드 패턴
            "barcode": [
                r"바코드[:\s]*(\d{13})",
                r"Barcode[:\s]*(\d{13})",
                r"(\d{13})",
                r"(\d{12})"
            ],
            
            # 중량 패턴
            "weight": [
                r"중량[:\s]*(\d+(?:\.\d+)?)\s*(?:g|ml|kg|L)",
                r"Weight[:\s]*(\d+(?:\.\d+)?)\s*(?:g|ml|kg|L)",
                r"(\d+(?:\.\d+)?)\s*(?:g|ml|kg|L)"
            ]
        }
    
    def extract_label_info(self, image_path: str, use_advanced_ocr: bool = True, translate_to: str = None, use_ai_apis: bool = True) -> Dict:
        """라벨 이미지에서 정보 추출 (한글 우선 + 번역 지원 + AI API)"""
        
        self.logger.info(f"🔍 라벨 정보 추출 시작: {image_path}")
        
        # AI API 우선 사용 (가장 정확)
        if use_ai_apis and self.use_ai_apis:
            self.logger.info("🤖 AI API OCR 시작...")
            ai_result = ai_ocr.extract_label_info(image_path, use_ai_apis=True)
            
            if ai_result:
                # AI API 결과가 있으면 번역 처리
                if translate_to and self.translator:
                    self.logger.info(f"🌐 AI 결과 번역 시작: {translate_to}")
                    translated_info = self.translate_extracted_info(ai_result, translate_to)
                    ai_result = translated_info
                
                # 신뢰도 평가 (AI API는 높은 신뢰도)
                confidence_scores = {key: 0.95 for key in ai_result.keys()}
                
                result = {
                    "extracted_info": ai_result,
                    "confidence_scores": confidence_scores,
                    "raw_text": "AI API 추출 결과",
                    "extraction_timestamp": datetime.now().isoformat(),
                    "image_path": image_path,
                    "translated": translate_to is not None,
                    "ai_enhanced": True
                }
                
                self.logger.info(f"✅ AI API OCR 완료: {len(ai_result)}개 항목")
                return result
        
        # AI API가 없거나 실패한 경우 기존 OCR 사용
        self.logger.info("📷 기존 OCR 엔진 사용...")
        
        # 이미지 전처리
        processed_image = self._preprocess_image(image_path)
        
        # OCR 텍스트 추출 (한글 우선)
        extracted_text = self._extract_text(processed_image, use_advanced_ocr)
        
        # 정보 추출
        label_info = self._extract_information(extracted_text)
        
        # 데이터 정규화
        normalized_info = self.data_normalizer.normalize_data(label_info)
        
        # 번역 처리 (요청된 경우)
        if translate_to and self.translator:
            self.logger.info(f"🌐 번역 시작: {translate_to}")
            translated_info = self.translate_extracted_info(normalized_info, translate_to)
            normalized_info = translated_info
        
        # 신뢰도 평가
        confidence_scores = self._calculate_confidence(extracted_text, normalized_info)
        
        result = {
            "extracted_info": normalized_info,
            "confidence_scores": confidence_scores,
            "raw_text": extracted_text,
            "extraction_timestamp": datetime.now().isoformat(),
            "image_path": image_path,
            "translated": translate_to is not None,
            "ai_enhanced": False
        }
        
        self.logger.info(f"✅ 기존 OCR 완료: {len(normalized_info)}개 항목")
        return result
    
    def _preprocess_image(self, image_path: str) -> np.ndarray:
        """이미지 전처리 강화"""
        try:
            # 이미지 로드
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"이미지를 로드할 수 없습니다: {image_path}")
            
            # 그레이스케일 변환
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 노이즈 제거
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # 대비 향상
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(denoised)
            
            # 이진화 (적응형)
            binary = cv2.adaptiveThreshold(
                enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # 모폴로지 연산으로 텍스트 선명화
            kernel = np.ones((1,1), np.uint8)
            processed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
            
            self.logger.info("✅ 이미지 전처리 완료")
            return processed
            
        except Exception as e:
            self.logger.error(f"❌ 이미지 전처리 실패: {e}")
            return cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    def _extract_text(self, image: np.ndarray, use_advanced_ocr: bool = True) -> str:
        """OCR을 사용한 텍스트 추출 (한글 우선)"""
        extracted_texts = []
        
        # Tesseract OCR (한국어 우선)
        if self.ocr_engines.get('tesseract', {}).get('available', False):
            try:
                # 한국어 우선 설정
                tesseract_config = '--oem 3 --psm 6 -l kor+eng+chi_sim'
                tesseract_text = pytesseract.image_to_string(image, config=tesseract_config)
                extracted_texts.append(('tesseract', tesseract_text))
                self.logger.info("✅ Tesseract 텍스트 추출 완료 (한국어 우선)")
            except Exception as e:
                self.logger.warning(f"❌ Tesseract 텍스트 추출 실패: {e}")
        
        # EasyOCR (한국어 우선)
        if self.ocr_engines.get('easyocr', {}).get('available', False):
            try:
                reader = self.ocr_engines['easyocr']['reader']
                easyocr_results = reader.readtext(image)
                easyocr_text = '\n'.join([text[1] for text in easyocr_results])
                extracted_texts.append(('easyocr', easyocr_text))
                self.logger.info("✅ EasyOCR 텍스트 추출 완료 (한국어 우선)")
            except Exception as e:
                self.logger.warning(f"❌ EasyOCR 텍스트 추출 실패: {e}")
        
        # OCR 엔진이 없는 경우 기본 텍스트 반환
        if not extracted_texts:
            self.logger.warning("⚠️ 사용 가능한 OCR 엔진이 없습니다. 기본 텍스트를 반환합니다.")
            return "OCR 엔진을 사용할 수 없습니다. 이미지를 확인해주세요."
        
        # 텍스트 결합 및 정리
        combined_text = self._combine_ocr_results(extracted_texts)
        
        # 한글 텍스트 정리 및 번역 준비
        cleaned_text = self._clean_korean_text(combined_text)
        
        return cleaned_text
    
    def _clean_korean_text(self, text: str) -> str:
        """한글 텍스트 정리 및 교정 강화"""
        if not text:
            return ""
        
        # 기본 정리
        cleaned = text.strip()
        
        # 일반적인 OCR 오류 교정
        corrections = {
            '준히어': '영양성분',
            '나트톱': '나트륨',
            'ODrig': '100g',
            'OOus': 'mg',
            'CCa': '탄수화물',
            'GDa': '당류',
            'J0us': '지방',
            'GDg': '트랜스지방',
            'OICa': '포화지방',
            '콜레스데감': '콜레스테롤',
            'D079': '0.79',
            'OOu': 'mg',
            'ODE': '단백질',
            '1맥': '1회',
            '염l심문': '섭취량',
            '기준치머': '기준치에',
            '바닥': '비율',
            '꼬:': '대한',
            'LJ(i': '비율',
            '힘:': '대한',
            'S 5Jg': '5g'
        }
        
        for wrong, correct in corrections.items():
            cleaned = cleaned.replace(wrong, correct)
        
        # 숫자 패턴 정리
        cleaned = re.sub(r'(\d+)\s*([a-zA-Z가-힣]+)', r'\1\2', cleaned)
        
        # 불필요한 공백 제거
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        self.logger.info(f"🔧 텍스트 교정: {text[:50]}... → {cleaned[:50]}...")
        return cleaned
    
    def translate_text(self, text: str, target_lang: str = 'en') -> str:
        """텍스트 번역"""
        if not self.translator or not text.strip():
            return text
        
        try:
            # 언어 코드 매핑
            lang_mapping = {
                'en': 'en',
                'zh-cn': 'zh-cn',
                'ko': 'ko'
            }
            
            target_lang_code = lang_mapping.get(target_lang, 'en')
            
            # 번역 실행
            translator = GoogleTranslator(source='ko', target=target_lang_code)
            translated = translator.translate(text)
            self.logger.info(f"✅ 번역 완료: {target_lang}")
            return translated
        except Exception as e:
            self.logger.warning(f"❌ 번역 실패: {e}")
            return text
    
    def translate_extracted_info(self, extracted_info: Dict, target_lang: str = 'en') -> Dict:
        """추출된 정보 번역"""
        if not self.translator:
            return extracted_info
        
        translated_info = extracted_info.copy()
        
        try:
            # 제품명 번역
            if 'product_name' in translated_info and translated_info['product_name']:
                translated_info['product_name'] = self.translate_text(
                    translated_info['product_name'], target_lang
                )
            
            # 제조사 번역
            if 'manufacturer' in translated_info and translated_info['manufacturer']:
                translated_info['manufacturer'] = self.translate_text(
                    translated_info['manufacturer'], target_lang
                )
            
            # 원산지 번역
            if 'origin' in translated_info and translated_info['origin']:
                translated_info['origin'] = self.translate_text(
                    translated_info['origin'], target_lang
                )
            
            # 성분 정보 번역
            if 'ingredients' in translated_info and translated_info['ingredients']:
                translated_info['ingredients'] = self.translate_text(
                    translated_info['ingredients'], target_lang
                )
            
            # 알레르기 정보 번역
            if 'allergies' in translated_info and translated_info['allergies']:
                if isinstance(translated_info['allergies'], list):
                    translated_allergies = []
                    for allergy in translated_info['allergies']:
                        translated_allergies.append(self.translate_text(allergy, target_lang))
                    translated_info['allergies'] = translated_allergies
                else:
                    translated_info['allergies'] = self.translate_text(
                        translated_info['allergies'], target_lang
                    )
            
            self.logger.info(f"✅ 추출 정보 번역 완료: {target_lang}")
            
        except Exception as e:
            self.logger.warning(f"❌ 추출 정보 번역 실패: {e}")
        
        return translated_info
    
    def _combine_ocr_results(self, ocr_results: List[Tuple[str, str]]) -> str:
        """OCR 결과 결합 및 정리"""
        if not ocr_results:
            return ""
        
        # 모든 텍스트 결합
        all_texts = [text for _, text in ocr_results]
        combined = '\n'.join(all_texts)
        
        # 텍스트 정리
        cleaned_text = self._clean_text(combined)
        
        return cleaned_text
    
    def _clean_text(self, text: str) -> str:
        """텍스트 정리"""
        # 불필요한 공백 제거
        text = re.sub(r'\s+', ' ', text)
        
        # 특수문자 정리
        text = re.sub(r'[^\w\s가-힣\-\.\,\:\/\(\)]', '', text)
        
        # 줄바꿈 정리
        text = re.sub(r'\n+', '\n', text)
        
        return text.strip()
    
    def _extract_information(self, text: str) -> Dict:
        """정규표현식을 사용한 정보 추출"""
        extracted_info = {}
        
        # 기본 정보 추출
        for field, patterns in self.extraction_patterns.items():
            if field == "nutrition":
                # 영양성분은 별도 처리
                extracted_info[field] = self._extract_nutrition_info(text)
            else:
                # 일반 필드 추출
                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        extracted_info[field] = match.group(1).strip()
                        break
        
        # NER 모델을 사용한 추가 정보 추출
        if self.ner_model:
            ner_info = self._extract_with_ner(text)
            extracted_info.update(ner_info)
        
        return extracted_info
    
    def _extract_nutrition_info(self, text: str) -> Dict:
        """영양성분 정보 추출"""
        nutrition_info = {}
        
        for nutrient, patterns in self.extraction_patterns["nutrition"].items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    nutrition_info[nutrient] = match.group(1).strip()
                    break
        
        return nutrition_info
    
    def _extract_with_ner(self, text: str) -> Dict:
        """NER 모델을 사용한 정보 추출"""
        ner_info = {}
        
        try:
            if hasattr(self.ner_model, 'pipe'):  # spaCy
                doc = self.ner_model(text)
                for ent in doc.ents:
                    if ent.label_ in ['ORG', 'PRODUCT', 'DATE', 'QUANTITY']:
                        ner_info[f"ner_{ent.label_.lower()}"] = ent.text
            elif hasattr(self.ner_model, '__call__'):  # Transformers
                ner_results = self.ner_model(text)
                for result in ner_results:
                    if result['score'] > 0.8:  # 신뢰도 임계값
                        ner_info[f"ner_{result['entity_group'].lower()}"] = result['word']
        except Exception as e:
            self.logger.warning(f"NER 정보 추출 실패: {e}")
        
        return ner_info
    
    def _calculate_confidence(self, text: str, extracted_info: Dict) -> Dict:
        """추출 정보의 신뢰도 계산"""
        confidence_scores = {}
        
        # 텍스트 길이 기반 기본 신뢰도
        base_confidence = min(len(text) / 1000, 1.0)  # 최대 1.0
        
        for field, value in extracted_info.items():
            if isinstance(value, dict):
                # 영양성분 등 중첩된 정보
                confidence_scores[field] = {
                    k: self._calculate_field_confidence(v, text) 
                    for k, v in value.items()
                }
            else:
                # 일반 필드
                confidence_scores[field] = self._calculate_field_confidence(value, text)
        
        # 전체 신뢰도
        confidence_scores['overall'] = base_confidence
        
        return confidence_scores
    
    def _calculate_field_confidence(self, value: str, text: str) -> float:
        """개별 필드 신뢰도 계산"""
        if not value:
            return 0.0
        
        # 값의 길이와 복잡성 기반 신뢰도
        length_confidence = min(len(value) / 50, 1.0)
        
        # 텍스트에서의 매칭 빈도 기반 신뢰도
        match_count = text.lower().count(value.lower())
        frequency_confidence = min(match_count / 3, 1.0)
        
        # 숫자 포함 여부 (영양성분 등)
        number_confidence = 1.0 if re.search(r'\d', value) else 0.5
        
        # 종합 신뢰도
        confidence = (length_confidence + frequency_confidence + number_confidence) / 3
        
        return round(confidence, 2)

class DataNormalizer:
    """데이터 정규화 클래스"""
    
    def __init__(self):
        self.unit_mappings = {
            'g': 'g', '그램': 'g', 'gram': 'g', 'grams': 'g',
            'ml': 'ml', '밀리리터': 'ml', 'milliliter': 'ml', 'milliliters': 'ml',
            'kg': 'kg', '킬로그램': 'kg', 'kilogram': 'kg', 'kilograms': 'kg',
            'kcal': 'kcal', '칼로리': 'kcal', 'calorie': 'kcal', 'calories': 'kcal',
            'mg': 'mg', '밀리그램': 'mg', 'milligram': 'mg', 'milligrams': 'mg'
        }
        
        self.date_patterns = [
            r'(\d{4})[-\/](\d{1,2})[-\/](\d{1,2})',
            r'(\d{1,2})[-\/](\d{1,2})[-\/](\d{4})',
            r'(\d{4})년(\d{1,2})월(\d{1,2})일',
            r'(\d{1,2})월(\d{1,2})일(\d{4})년'
        ]
    
    def normalize_data(self, data: Dict) -> Dict:
        """데이터 정규화"""
        normalized = {}
        
        for key, value in data.items():
            if isinstance(value, dict):
                normalized[key] = self.normalize_data(value)
            else:
                normalized[key] = self.normalize_field(key, value)
        
        return normalized
    
    def normalize_field(self, field: str, value: str) -> str:
        """개별 필드 정규화"""
        if not value:
            return value
        
        # 단위 정규화
        if field in ['weight', 'nutrition'] or any(unit in value.lower() for unit in self.unit_mappings):
            value = self.normalize_units(value)
        
        # 날짜 정규화
        if field in ['expiry_date', 'manufacture_date']:
            value = self.normalize_date(value)
        
        # 숫자 정규화
        if field in ['calories', 'protein', 'fat', 'carbohydrates', 'sodium', 'sugar']:
            value = self.normalize_number(value)
        
        return value
    
    def normalize_units(self, text: str) -> str:
        """단위 정규화"""
        for old_unit, new_unit in self.unit_mappings.items():
            text = re.sub(rf'\b{old_unit}\b', new_unit, text, flags=re.IGNORECASE)
        return text
    
    def normalize_date(self, date_str: str) -> str:
        """날짜 정규화"""
        for pattern in self.date_patterns:
            match = re.search(pattern, date_str)
            if match:
                groups = match.groups()
                if len(groups) == 3:
                    if len(groups[0]) == 4:  # YYYY-MM-DD
                        return f"{groups[0]}-{groups[1].zfill(2)}-{groups[2].zfill(2)}"
                    else:  # MM-DD-YYYY
                        return f"{groups[2]}-{groups[0].zfill(2)}-{groups[1].zfill(2)}"
        return date_str
    
    def normalize_number(self, text: str) -> str:
        """숫자 정규화"""
        # 숫자만 추출
        numbers = re.findall(r'\d+(?:\.\d+)?', text)
        if numbers:
            return numbers[0]
        return text

def main():
    """OCR 라벨 추출 시스템 테스트"""
    
    print("🏷️ OCR 기반 라벨 정보 추출 시스템")
    print("=" * 50)
    
    extractor = LabelOCRExtractor()
    
    # OCR 엔진 상태 확인
    print("\n📋 OCR 엔진 상태:")
    for engine_name, status in extractor.ocr_engines.items():
        if status.get('available', False):
            print(f"   ✅ {engine_name}: 사용 가능")
            if 'version' in status:
                print(f"      버전: {status['version']}")
        else:
            print(f"   ❌ {engine_name}: 사용 불가")
            if 'error' in status:
                print(f"      오류: {status['error']}")
    
    # NER 모델 상태 확인
    if extractor.ner_model:
        print(f"   ✅ NER 모델: 사용 가능")
    else:
        print(f"   ❌ NER 모델: 사용 불가")
    
    # 테스트 이미지가 있는 경우 추출 테스트
    test_image_path = "test_label.png"
    if os.path.exists(test_image_path):
        print(f"\n🔍 테스트 이미지 추출: {test_image_path}")
        try:
            result = extractor.extract_label_info(test_image_path)
            
            print(f"\n📄 추출된 정보:")
            for field, value in result['extracted_info'].items():
                if isinstance(value, dict):
                    print(f"   {field}:")
                    for sub_field, sub_value in value.items():
                        confidence = result['confidence_scores'][field].get(sub_field, 0)
                        print(f"     {sub_field}: {sub_value} (신뢰도: {confidence})")
                else:
                    confidence = result['confidence_scores'].get(field, 0)
                    print(f"   {field}: {value} (신뢰도: {confidence})")
            
            print(f"\n📊 전체 신뢰도: {result['confidence_scores']['overall']}")
            
        except Exception as e:
            print(f"❌ 추출 실패: {e}")
    else:
        print(f"\n💡 테스트 이미지를 업로드하여 추출 기능을 테스트해보세요.")

if __name__ == "__main__":
    main() 