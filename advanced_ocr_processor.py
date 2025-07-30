#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 고급 OCR 및 이미지 전처리 시스템
- 다중 OCR 엔진 병렬 처리
- 이미지 전처리 (해상도 향상, 잡음제거, 회전 보정)
- 표 구조 데이터화 및 아이콘/직인 추출
- 신뢰도 기반 결과 검증
"""

import os
import cv2
import numpy as np
import json
import base64
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from datetime import datetime
import logging

# 이미지 전처리 라이브러리
try:
    from skimage import filters, restoration, transform, exposure
    from skimage.util import img_as_ubyte
    SKIMAGE_AVAILABLE = True
except ImportError:
    SKIMAGE_AVAILABLE = False
    print("⚠️ scikit-image을 사용할 수 없습니다.")

# OCR 엔진들
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False
    print("⚠️ EasyOCR을 사용할 수 없습니다.")

try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False
    print("⚠️ PaddleOCR을 사용할 수 없습니다.")

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("⚠️ Tesseract를 사용할 수 없습니다.")

# Google Cloud Vision
try:
    from google.cloud import vision
    GOOGLE_VISION_AVAILABLE = True
except ImportError:
    GOOGLE_VISION_AVAILABLE = False
    print("⚠️ Google Cloud Vision을 사용할 수 없습니다.")

# Azure Computer Vision
try:
    from azure.cognitiveservices.vision.computervision import ComputerVisionClient
    from msrest.authentication import CognitiveServicesCredentials
    AZURE_VISION_AVAILABLE = True
except ImportError:
    AZURE_VISION_AVAILABLE = False
    print("⚠️ Azure Computer Vision을 사용할 수 없습니다.")

@dataclass
class OCRResult:
    """OCR 결과 데이터 클래스"""
    text: str
    confidence: float
    bbox: List[Tuple[int, int]]
    engine: str
    page: int = 1

@dataclass
class TableData:
    """테이블 데이터 클래스"""
    data: List[List[str]]
    bbox: List[Tuple[int, int]]
    confidence: float
    engine: str
    page: int = 1

@dataclass
class IconData:
    """아이콘/직인 데이터 클래스"""
    type: str  # 'icon', 'stamp', 'logo', 'signature'
    bbox: List[Tuple[int, int]]
    confidence: float
    engine: str
    image_data: Optional[bytes] = None
    page: int = 1

@dataclass
class LayoutData:
    """레이아웃 데이터 클래스"""
    regions: List[Dict[str, Any]]
    confidence: float
    engine: str
    page: int = 1

class AdvancedImagePreprocessor:
    """고급 이미지 전처리기 (문서별 맞춤 설정)"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 문서별 최적화 설정
        self.document_settings = {
            'nutrition_label': {
                'enhance_resolution': True,
                'scale_factor': 2.5,
                'noise_reduction': 'strong',
                'contrast_enhancement': 'aggressive',
                'rotation_correction': True,
                'binarization': 'adaptive',
                'morphology': 'text_sharpening'
            },
            'customs_document': {
                'enhance_resolution': True,
                'scale_factor': 2.0,
                'noise_reduction': 'moderate',
                'contrast_enhancement': 'balanced',
                'rotation_correction': True,
                'binarization': 'otsu',
                'morphology': 'table_enhancement'
            },
            'general_document': {
                'enhance_resolution': False,
                'scale_factor': 1.5,
                'noise_reduction': 'light',
                'contrast_enhancement': 'conservative',
                'rotation_correction': True,
                'binarization': 'adaptive',
                'morphology': 'basic_cleaning'
            }
        }
    
    def preprocess_for_document_type(self, image: np.ndarray, document_type: str = 'general_document') -> Dict[str, Any]:
        """문서 유형별 맞춤 전처리"""
        if document_type not in self.document_settings:
            document_type = 'general_document'
        
        settings = self.document_settings[document_type]
        self.logger.info(f"🔧 {document_type} 전처리 시작")
        
        processed_image = image.copy()
        preprocessing_info = {
            'document_type': document_type,
            'original_size': image.shape,
            'applied_settings': settings,
            'processing_steps': []
        }
        
        # 1. 해상도 향상
        if settings['enhance_resolution']:
            processed_image = self.enhance_resolution(processed_image, settings['scale_factor'])
            preprocessing_info['processing_steps'].append('resolution_enhancement')
        
        # 2. 잡음제거
        if settings['noise_reduction'] != 'none':
            processed_image = self.remove_noise_optimized(processed_image, settings['noise_reduction'])
            preprocessing_info['processing_steps'].append('noise_reduction')
        
        # 3. 대비 향상
        if settings['contrast_enhancement'] != 'none':
            processed_image = self.enhance_contrast_optimized(processed_image, settings['contrast_enhancement'])
            preprocessing_info['processing_steps'].append('contrast_enhancement')
        
        # 4. 회전 보정
        if settings['rotation_correction']:
            processed_image, rotation_angle = self.correct_rotation(processed_image)
            preprocessing_info['rotation_angle'] = rotation_angle
            preprocessing_info['processing_steps'].append('rotation_correction')
        
        # 5. 이진화
        if settings['binarization'] != 'none':
            processed_image = self.binarize_optimized(processed_image, settings['binarization'])
            preprocessing_info['processing_steps'].append('binarization')
        
        # 6. 모폴로지 연산
        if settings['morphology'] != 'none':
            processed_image = self.apply_morphology(processed_image, settings['morphology'])
            preprocessing_info['processing_steps'].append('morphology')
        
        preprocessing_info['final_size'] = processed_image.shape
        self.logger.info(f"✅ {document_type} 전처리 완료: {len(preprocessing_info['processing_steps'])}단계")
        
        return {
            'processed_image': processed_image,
            'preprocessing_info': preprocessing_info
        }
    
    def enhance_resolution(self, image: np.ndarray, scale_factor: float = 2.0) -> np.ndarray:
        """해상도 향상"""
        try:
            if SKIMAGE_AVAILABLE:
                # Lanczos 보간법 사용
                enhanced = transform.rescale(image, scale_factor, order=3, anti_aliasing=True)
                return img_as_ubyte(enhanced)
            else:
                # OpenCV 사용
                height, width = image.shape[:2]
                new_height, new_width = int(height * scale_factor), int(width * scale_factor)
                enhanced = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
                return enhanced
        except Exception as e:
            self.logger.error(f"해상도 향상 실패: {e}")
            return image
    
    def remove_noise(self, image: np.ndarray) -> np.ndarray:
        """잡음 제거"""
        try:
            if SKIMAGE_AVAILABLE:
                # Non-local means denoising
                if len(image.shape) == 3:
                    denoised = restoration.denoise_nl_means(image, h=0.1, fast_mode=True)
                else:
                    denoised = restoration.denoise_nl_means(image, h=0.1, fast_mode=True)
                return img_as_ubyte(denoised)
            else:
                # OpenCV bilateral filter
                denoised = cv2.bilateralFilter(image, 9, 75, 75)
                return denoised
        except Exception as e:
            self.logger.error(f"잡음 제거 실패: {e}")
            return image
    
    def correct_rotation(self, image: np.ndarray) -> Tuple[np.ndarray, float]:
        """회전 보정"""
        try:
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # 이진화
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            # 텍스트 라인 검출
            lines = cv2.HoughLines(binary, 1, np.pi/180, threshold=100)
            
            if lines is not None:
                angles = []
                for rho, theta in lines[:10]:  # 상위 10개 라인만 사용
                    angle = theta * 180 / np.pi
                    if angle < 45:
                        angles.append(angle)
                    elif angle > 135:
                        angles.append(angle - 180)
                
                if angles:
                    median_angle = np.median(angles)
                    if abs(median_angle) > 0.5:  # 0.5도 이상일 때만 회전
                        height, width = image.shape[:2]
                        center = (width // 2, height // 2)
                        rotation_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
                        corrected = cv2.warpAffine(image, rotation_matrix, (width, height))
                        return corrected, median_angle
            
            return image, 0.0
            
        except Exception as e:
            self.logger.error(f"회전 보정 실패: {e}")
            return image, 0.0
    
    def standardize_image(self, image: np.ndarray) -> np.ndarray:
        """이미지 표준화"""
        try:
            # 그레이스케일 변환
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # 히스토그램 평활화
            if SKIMAGE_AVAILABLE:
                equalized = exposure.equalize_hist(gray)
                return img_as_ubyte(equalized)
            else:
                equalized = cv2.equalizeHist(gray)
                return equalized
                
        except Exception as e:
            self.logger.error(f"이미지 표준화 실패: {e}")
            return image
    
    def remove_noise_optimized(self, image: np.ndarray, intensity: str = 'moderate') -> np.ndarray:
        """강도별 잡음제거"""
        if not SKIMAGE_AVAILABLE:
            return image
        
        try:
            if intensity == 'strong':
                # 강한 잡음제거 (영양정보 라벨용)
                denoised = restoration.denoise_bilateral(image, sigma_color=0.1, sigma_spatial=15)
            elif intensity == 'moderate':
                # 중간 잡음제거 (통관 서류용)
                denoised = restoration.denoise_bilateral(image, sigma_color=0.05, sigma_spatial=10)
            else:  # light
                # 가벼운 잡음제거 (일반 문서용)
                denoised = restoration.denoise_bilateral(image, sigma_color=0.02, sigma_spatial=5)
            
            return img_as_ubyte(denoised)
        except Exception as e:
            self.logger.warning(f"❌ 잡음제거 실패: {e}")
            return image
    
    def enhance_contrast_optimized(self, image: np.ndarray, intensity: str = 'balanced') -> np.ndarray:
        """강도별 대비 향상"""
        try:
            if intensity == 'aggressive':
                # 공격적 대비 향상 (영양정보 라벨용)
                clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
                enhanced = clahe.apply(image)
            elif intensity == 'balanced':
                # 균형잡힌 대비 향상 (통관 서류용)
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                enhanced = clahe.apply(image)
            else:  # conservative
                # 보수적 대비 향상 (일반 문서용)
                clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8,8))
                enhanced = clahe.apply(image)
            
            return enhanced
        except Exception as e:
            self.logger.warning(f"❌ 대비 향상 실패: {e}")
            return image
    
    def binarize_optimized(self, image: np.ndarray, method: str = 'adaptive') -> np.ndarray:
        """방법별 이진화"""
        try:
            if method == 'adaptive':
                # 적응형 이진화 (대부분의 문서에 적합)
                binary = cv2.adaptiveThreshold(
                    image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                    cv2.THRESH_BINARY, 11, 2
                )
            elif method == 'otsu':
                # Otsu 이진화 (명확한 대비가 있는 문서에 적합)
                _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            else:  # simple
                # 단순 이진화
                _, binary = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
            
            return binary
        except Exception as e:
            self.logger.warning(f"❌ 이진화 실패: {e}")
            return image
    
    def apply_morphology(self, image: np.ndarray, operation: str = 'basic_cleaning') -> np.ndarray:
        """모폴로지 연산 적용"""
        try:
            if operation == 'text_sharpening':
                # 텍스트 선명화 (영양정보 라벨용)
                kernel = np.ones((1,1), np.uint8)
                sharpened = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
                kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
                sharpened = cv2.filter2D(sharpened, -1, kernel)
            elif operation == 'table_enhancement':
                # 테이블 강화 (통관 서류용)
                kernel = np.ones((2,2), np.uint8)
                enhanced = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
                kernel = np.ones((1,1), np.uint8)
                enhanced = cv2.morphologyEx(enhanced, cv2.MORPH_OPEN, kernel)
            else:  # basic_cleaning
                # 기본 정리 (일반 문서용)
                kernel = np.ones((1,1), np.uint8)
                cleaned = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
            
            return enhanced if operation == 'table_enhancement' else (sharpened if operation == 'text_sharpening' else cleaned)
        except Exception as e:
            self.logger.warning(f"❌ 모폴로지 연산 실패: {e}")
            return image
    
    def detect_document_type(self, image: np.ndarray) -> str:
        """이미지에서 문서 유형 자동 감지"""
        try:
            # 이미지 특성 분석
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
            
            # 1. 텍스트 밀도 분석
            edges = cv2.Canny(gray, 50, 150)
            text_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            
            # 2. 대비 분석
            contrast = np.std(gray)
            
            # 3. 구조적 복잡도 분석
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # 4. 색상 분석 (영양정보 라벨은 보통 색상이 있음)
            if len(image.shape) == 3:
                color_variance = np.std(image, axis=(0,1))
                has_color = np.any(color_variance > 30)
            else:
                has_color = False
            
            # 문서 유형 판단
            if has_color and text_density > 0.1 and contrast > 50:
                return 'nutrition_label'
            elif text_density > 0.15 and laplacian_var > 100:
                return 'customs_document'
            else:
                return 'general_document'
                
        except Exception as e:
            self.logger.warning(f"❌ 문서 유형 감지 실패: {e}")
            return 'general_document'
    
    def preprocess_image(self, image: np.ndarray, enhance_resolution: bool = True) -> Dict[str, Any]:
        """전체 이미지 전처리 파이프라인"""
        original = image.copy()
        processing_steps = []
        
        try:
            # 1. 회전 보정
            corrected, rotation_angle = self.correct_rotation(image)
            if abs(rotation_angle) > 0.5:
                processing_steps.append(f"회전 보정: {rotation_angle:.2f}도")
                image = corrected
            
            # 2. 잡음 제거
            denoised = self.remove_noise(image)
            processing_steps.append("잡음 제거")
            image = denoised
            
            # 3. 해상도 향상 (선택적)
            if enhance_resolution:
                enhanced = self.enhance_resolution(image, scale_factor=1.5)
                processing_steps.append("해상도 향상 (1.5배)")
                image = enhanced
            
            # 4. 표준화
            standardized = self.standardize_image(image)
            processing_steps.append("이미지 표준화")
            image = standardized
            
            return {
                'processed_image': image,
                'original_image': original,
                'processing_steps': processing_steps,
                'rotation_angle': rotation_angle
            }
            
        except Exception as e:
            self.logger.error(f"이미지 전처리 실패: {e}")
            return {
                'processed_image': original,
                'original_image': original,
                'processing_steps': ["전처리 실패"],
                'rotation_angle': 0.0,
                'error': str(e)
            }

class MultiEngineOCRProcessor:
    """다중 OCR 엔진 병렬 처리 클래스"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.preprocessor = AdvancedImagePreprocessor()
        
        # OCR 엔진 초기화
        self.engines = {}
        self._initialize_engines()
    
    def _initialize_engines(self):
        """OCR 엔진 초기화"""
        # EasyOCR
        if EASYOCR_AVAILABLE:
            try:
                self.engines['easyocr'] = easyocr.Reader(['ko', 'en', 'zh'])
                self.logger.info("✅ EasyOCR 엔진 초기화 완료")
            except Exception as e:
                self.logger.error(f"❌ EasyOCR 초기화 실패: {e}")
        
        # PaddleOCR
        if PADDLEOCR_AVAILABLE:
            try:
                self.engines['paddleocr'] = PaddleOCR(use_angle_cls=True, lang='korean')
                self.logger.info("✅ PaddleOCR 엔진 초기화 완료")
            except Exception as e:
                self.logger.error(f"❌ PaddleOCR 초기화 실패: {e}")
        
        # Tesseract
        if TESSERACT_AVAILABLE:
            try:
                # Tesseract 설치 확인
                pytesseract.get_tesseract_version()
                self.engines['tesseract'] = 'tesseract'
                self.logger.info("✅ Tesseract 엔진 초기화 완료")
            except Exception as e:
                self.logger.error(f"❌ Tesseract 초기화 실패: {e}")
        
        # Google Cloud Vision
        if GOOGLE_VISION_AVAILABLE:
            try:
                self.engines['google_vision'] = vision.ImageAnnotatorClient()
                self.logger.info("✅ Google Cloud Vision 엔진 초기화 완료")
            except Exception as e:
                self.logger.error(f"❌ Google Cloud Vision 초기화 실패: {e}")
        
        # Azure Computer Vision
        if AZURE_VISION_AVAILABLE:
            try:
                endpoint = os.getenv('AZURE_VISION_ENDPOINT')
                key = os.getenv('AZURE_VISION_KEY')
                if endpoint and key:
                    self.engines['azure_vision'] = ComputerVisionClient(
                        endpoint, CognitiveServicesCredentials(key)
                    )
                    self.logger.info("✅ Azure Computer Vision 엔진 초기화 완료")
            except Exception as e:
                self.logger.error(f"❌ Azure Computer Vision 초기화 실패: {e}")
    
    def _process_with_easyocr(self, image: np.ndarray) -> List[OCRResult]:
        """EasyOCR로 처리"""
        try:
            results = self.engines['easyocr'].readtext(image)
            ocr_results = []
            
            for (bbox, text, confidence) in results:
                ocr_results.append(OCRResult(
                    text=text,
                    confidence=confidence,
                    bbox=bbox,
                    engine='easyocr'
                ))
            
            return ocr_results
        except Exception as e:
            self.logger.error(f"EasyOCR 처리 실패: {e}")
            return []
    
    def _process_with_paddleocr(self, image: np.ndarray) -> List[OCRResult]:
        """PaddleOCR로 처리"""
        try:
            results = self.engines['paddleocr'].ocr(image, cls=True)
            ocr_results = []
            
            if results and results[0]:
                for line in results[0]:
                    if line:
                        bbox, (text, confidence) = line
                        ocr_results.append(OCRResult(
                            text=text,
                            confidence=confidence,
                            bbox=bbox,
                            engine='paddleocr'
                        ))
            
            return ocr_results
        except Exception as e:
            self.logger.error(f"PaddleOCR 처리 실패: {e}")
            return []
    
    def _process_with_tesseract(self, image: np.ndarray) -> List[OCRResult]:
        """Tesseract로 처리"""
        try:
            # Tesseract 설정
            custom_config = r'--oem 3 --psm 6 -l kor+eng+chi_sim'
            
            # 텍스트 추출
            text = pytesseract.image_to_string(image, config=custom_config)
            
            # 바운딩 박스 추출
            data = pytesseract.image_to_data(image, config=custom_config, output_type=pytesseract.Output.DICT)
            
            ocr_results = []
            for i in range(len(data['text'])):
                if data['conf'][i] > 0:  # 신뢰도가 0보다 큰 경우만
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    bbox = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
                    
                    ocr_results.append(OCRResult(
                        text=data['text'][i],
                        confidence=data['conf'][i] / 100.0,
                        bbox=bbox,
                        engine='tesseract'
                    ))
            
            return ocr_results
        except Exception as e:
            self.logger.error(f"Tesseract 처리 실패: {e}")
            return []
    
    def _process_with_google_vision(self, image: np.ndarray) -> List[OCRResult]:
        """Google Cloud Vision으로 처리"""
        try:
            # 이미지를 base64로 인코딩
            _, buffer = cv2.imencode('.jpg', image)
            image_bytes = buffer.tobytes()
            
            # Vision API 요청
            image_vision = vision.Image(content=image_bytes)
            response = self.engines['google_vision'].text_detection(image=image_vision)
            
            ocr_results = []
            if response.text_annotations:
                for annotation in response.text_annotations[1:]:  # 첫 번째는 전체 텍스트
                    vertices = [(vertex.x, vertex.y) for vertex in annotation.bounding_poly.vertices]
                    ocr_results.append(OCRResult(
                        text=annotation.description,
                        confidence=1.0,  # Google Vision은 신뢰도를 제공하지 않음
                        bbox=vertices,
                        engine='google_vision'
                    ))
            
            return ocr_results
        except Exception as e:
            self.logger.error(f"Google Cloud Vision 처리 실패: {e}")
            return []
    
    def _process_with_azure_vision(self, image: np.ndarray) -> List[OCRResult]:
        """Azure Computer Vision으로 처리"""
        try:
            # 이미지를 base64로 인코딩
            _, buffer = cv2.imencode('.jpg', image)
            image_bytes = buffer.tobytes()
            
            # Azure Vision API 요청
            response = self.engines['azure_vision'].read_in_stream(image_bytes, raw=True)
            operation_location = response.headers["Operation-Location"]
            operation_id = operation_location.split("/")[-1]
            
            # 결과 대기
            import time
            while True:
                read_result = self.engines['azure_vision'].get_read_result(operation_id)
                if read_result.status not in ['notStarted', 'running']:
                    break
                time.sleep(1)
            
            ocr_results = []
            if read_result.status == "succeeded":
                for text_result in read_result.analyze_result.read_results:
                    for line in text_result.lines:
                        bbox = [(word.bounding_box[0], word.bounding_box[1]) for word in line.words]
                        text = ' '.join([word.text for word in line.words])
                        ocr_results.append(OCRResult(
                            text=text,
                            confidence=1.0,  # Azure Vision은 신뢰도를 제공하지 않음
                            bbox=bbox,
                            engine='azure_vision'
                        ))
            
            return ocr_results
        except Exception as e:
            self.logger.error(f"Azure Computer Vision 처리 실패: {e}")
            return []
    
    def process_image_parallel(self, image: np.ndarray, document_type: str = None) -> Dict[str, Any]:
        """이미지를 다중 OCR 엔진으로 병렬 처리 (문서별 맞춤 전처리)"""
        self.logger.info("🚀 다중 OCR 엔진 병렬 처리 시작")
        
        # 문서 유형 자동 감지 (지정되지 않은 경우)
        if document_type is None:
            document_type = self.preprocessor.detect_document_type(image)
            self.logger.info(f"🔍 자동 감지된 문서 유형: {document_type}")
        
        # 문서별 맞춤 전처리 적용
        preprocess_result = self.preprocessor.preprocess_for_document_type(image, document_type)
        processed_image = preprocess_result['processed_image']
        
        # 병렬 OCR 처리
        results = {}
        with ThreadPoolExecutor(max_workers=len(self.engines)) as executor:
            future_to_engine = {}
            
            for engine_name in self.engines.keys():
                if engine_name == 'easyocr':
                    future = executor.submit(self._process_with_easyocr, processed_image)
                elif engine_name == 'paddleocr':
                    future = executor.submit(self._process_with_paddleocr, processed_image)
                elif engine_name == 'tesseract':
                    future = executor.submit(self._process_with_tesseract, processed_image)
                elif engine_name == 'google_vision':
                    future = executor.submit(self._process_with_google_vision, processed_image)
                elif engine_name == 'azure_vision':
                    future = executor.submit(self._process_with_azure_vision, processed_image)
                
                future_to_engine[future] = engine_name
            
            # 결과 수집
            for future in as_completed(future_to_engine):
                engine_name = future_to_engine[future]
                try:
                    results[engine_name] = future.result()
                    self.logger.info(f"✅ {engine_name} 처리 완료: {len(results[engine_name])}개 결과")
                except Exception as e:
                    self.logger.error(f"❌ {engine_name} 처리 실패: {e}")
                    results[engine_name] = []
        
        # 결과 통합 및 신뢰도 기반 필터링
        integrated_results = self._integrate_results(results)
        
        # 테이블, 아이콘, 레이아웃 추출
        tables = self._extract_tables(integrated_results)
        icons = self._extract_icons(processed_image, integrated_results)
        layout = self._analyze_layout(integrated_results)
        
        self.logger.info(f"✅ 병렬 처리 완료: {len(integrated_results)}개 텍스트, {len(tables)}개 테이블, {len(icons)}개 아이콘")
        
        return {
            'text': [{'text': r.text, 'confidence': r.confidence, 'bbox': r.bbox, 'engine': r.engine} for r in integrated_results],
            'tables': [{'data': t.data, 'bbox': t.bbox, 'confidence': t.confidence, 'engine': t.engine} for t in tables],
            'icons': [{'type': i.type, 'bbox': i.bbox, 'confidence': i.confidence, 'engine': i.engine} for i in icons],
            'layout': {'regions': layout.regions, 'confidence': layout.confidence, 'engine': layout.engine},
            'preprocessing_info': preprocess_result['preprocessing_info'],
            'engine_performance': {name: len(results[name]) for name in results.keys()},
            'document_type': document_type
        }
    
    def _integrate_results(self, engine_results: Dict[str, List[OCRResult]]) -> List[OCRResult]:
        """다중 엔진 결과 통합"""
        all_results = []
        
        for engine_name, results in engine_results.items():
            for result in results:
                all_results.append(result)
        
        # 신뢰도 기반 필터링 (0.3 이상)
        filtered_results = [r for r in all_results if r.confidence >= 0.3]
        
        # 중복 제거 (텍스트 유사도 기반)
        unique_results = self._remove_duplicates(filtered_results)
        
        return unique_results
    
    def _remove_duplicates(self, results: List[OCRResult]) -> List[OCRResult]:
        """중복 결과 제거"""
        unique_results = []
        
        for result in results:
            is_duplicate = False
            for existing in unique_results:
                # 텍스트 유사도 계산
                similarity = self._calculate_text_similarity(result.text, existing.text)
                if similarity > 0.8:  # 80% 이상 유사하면 중복으로 간주
                    # 더 높은 신뢰도를 가진 결과 선택
                    if result.confidence > existing.confidence:
                        unique_results.remove(existing)
                        unique_results.append(result)
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_results.append(result)
        
        return unique_results
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """텍스트 유사도 계산"""
        if not text1 or not text2:
            return 0.0
        
        # 간단한 Jaccard 유사도
        set1 = set(text1.lower())
        set2 = set(text2.lower())
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def _extract_tables(self, ocr_results: List[OCRResult]) -> List[TableData]:
        """테이블 구조 추출"""
        tables = []
        
        # 텍스트를 좌표 기반으로 정렬
        sorted_results = sorted(ocr_results, key=lambda x: (x.bbox[0][1], x.bbox[0][0]))
        
        # 테이블 패턴 검출
        table_regions = self._detect_table_regions(sorted_results)
        
        for region in table_regions:
            table_data = self._structure_table_data(region)
            if table_data:
                tables.append(table_data)
        
        return tables
    
    def _detect_table_regions(self, ocr_results: List[OCRResult]) -> List[List[OCRResult]]:
        """테이블 영역 검출"""
        # 간단한 테이블 검출 로직
        # 실제로는 더 정교한 알고리즘이 필요
        regions = []
        current_region = []
        
        for result in ocr_results:
            if len(current_region) == 0:
                current_region.append(result)
            else:
                # 같은 행에 있는지 확인
                last_result = current_region[-1]
                y_diff = abs(result.bbox[0][1] - last_result.bbox[0][1])
                
                if y_diff < 20:  # 같은 행
                    current_region.append(result)
                else:
                    # 새로운 행 시작
                    if len(current_region) >= 3:  # 최소 3개 이상의 텍스트가 있으면 테이블로 간주
                        regions.append(current_region)
                    current_region = [result]
        
        if len(current_region) >= 3:
            regions.append(current_region)
        
        return regions
    
    def _structure_table_data(self, region: List[OCRResult]) -> Optional[TableData]:
        """테이블 데이터 구조화"""
        try:
            # 행별로 그룹화
            rows = {}
            for result in region:
                y = result.bbox[0][1]
                row_key = y // 20  # 20픽셀 단위로 행 그룹화
                
                if row_key not in rows:
                    rows[row_key] = []
                rows[row_key].append(result)
            
            # 각 행을 x좌표로 정렬
            table_data = []
            for row_key in sorted(rows.keys()):
                row_results = sorted(rows[row_key], key=lambda x: x.bbox[0][0])
                row_data = [result.text for result in row_results]
                table_data.append(row_data)
            
            if table_data:
                # 전체 바운딩 박스 계산
                all_bboxes = [result.bbox for result in region]
                min_x = min([bbox[0][0] for bbox in all_bboxes])
                min_y = min([bbox[0][1] for bbox in all_bboxes])
                max_x = max([bbox[2][0] for bbox in all_bboxes])
                max_y = max([bbox[2][1] for bbox in all_bboxes])
                
                bbox = [(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)]
                
                return TableData(
                    data=table_data,
                    bbox=bbox,
                    confidence=np.mean([result.confidence for result in region]),
                    engine='integrated'
                )
            
            return None
            
        except Exception as e:
            self.logger.error(f"테이블 구조화 실패: {e}")
            return None
    
    def _extract_icons(self, image: np.ndarray, ocr_results: List[OCRResult]) -> List[IconData]:
        """아이콘/직인 추출"""
        icons = []
        
        try:
            # 텍스트 영역을 제외한 영역에서 아이콘 검출
            text_mask = np.zeros(image.shape[:2], dtype=np.uint8)
            
            for result in ocr_results:
                bbox = result.bbox
                pts = np.array(bbox, np.int32)
                cv2.fillPoly(text_mask, [pts], 255)
            
            # 텍스트가 아닌 영역
            non_text_mask = cv2.bitwise_not(text_mask)
            
            # 윤곽선 검출
            contours, _ = cv2.findContours(non_text_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 100:  # 최소 크기 필터
                    x, y, w, h = cv2.boundingRect(contour)
                    bbox = [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
                    
                    # 아이콘 타입 분류
                    icon_type = self._classify_icon_type(image[y:y+h, x:x+w])
                    
                    # 아이콘 이미지 추출
                    icon_image = image[y:y+h, x:x+w]
                    _, icon_bytes = cv2.imencode('.png', icon_image)
                    
                    icons.append(IconData(
                        type=icon_type,
                        bbox=bbox,
                        confidence=0.8,  # 기본 신뢰도
                        engine='opencv',
                        image_data=icon_bytes.tobytes()
                    ))
        
        except Exception as e:
            self.logger.error(f"아이콘 추출 실패: {e}")
        
        return icons
    
    def _classify_icon_type(self, icon_image: np.ndarray) -> str:
        """아이콘 타입 분류"""
        try:
            # 간단한 분류 로직
            # 실제로는 머신러닝 모델을 사용해야 함
            
            # 원형 검출 (직인)
            gray = cv2.cvtColor(icon_image, cv2.COLOR_BGR2GRAY)
            circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=30, minRadius=0, maxRadius=0)
            
            if circles is not None:
                return 'stamp'
            
            # 사각형 검출 (로고)
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 50:
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h
                    if 0.8 < aspect_ratio < 1.2:  # 정사각형에 가까우면 로고
                        return 'logo'
            
            return 'icon'
            
        except Exception as e:
            self.logger.error(f"아이콘 분류 실패: {e}")
            return 'icon'
    
    def _analyze_layout(self, ocr_results: List[OCRResult]) -> LayoutData:
        """레이아웃 분석"""
        try:
            regions = []
            
            # 텍스트 블록 그룹화
            text_blocks = self._group_text_blocks(ocr_results)
            
            for block in text_blocks:
                region = {
                    'type': 'text',
                    'bbox': self._calculate_block_bbox(block),
                    'text': ' '.join([result.text for result in block]),
                    'confidence': np.mean([result.confidence for result in block])
                }
                regions.append(region)
            
            return LayoutData(
                regions=regions,
                confidence=0.9,
                engine='integrated'
            )
            
        except Exception as e:
            self.logger.error(f"레이아웃 분석 실패: {e}")
            return LayoutData(regions=[], confidence=0.0, engine='integrated')
    
    def _group_text_blocks(self, ocr_results: List[OCRResult]) -> List[List[OCRResult]]:
        """텍스트 블록 그룹화"""
        blocks = []
        current_block = []
        
        for result in ocr_results:
            if not current_block:
                current_block.append(result)
            else:
                # 같은 블록에 속하는지 확인
                last_result = current_block[-1]
                distance = self._calculate_distance(result.bbox, last_result.bbox)
                
                if distance < 50:  # 50픽셀 이내면 같은 블록
                    current_block.append(result)
                else:
                    if current_block:
                        blocks.append(current_block)
                    current_block = [result]
        
        if current_block:
            blocks.append(current_block)
        
        return blocks
    
    def _calculate_distance(self, bbox1: List[Tuple[int, int]], bbox2: List[Tuple[int, int]]) -> float:
        """두 바운딩 박스 간의 거리 계산"""
        center1 = ((bbox1[0][0] + bbox1[2][0]) / 2, (bbox1[0][1] + bbox1[2][1]) / 2)
        center2 = ((bbox2[0][0] + bbox2[2][0]) / 2, (bbox2[0][1] + bbox2[2][1]) / 2)
        
        return np.sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)
    
    def _calculate_block_bbox(self, block: List[OCRResult]) -> List[Tuple[int, int]]:
        """블록의 바운딩 박스 계산"""
        all_bboxes = [result.bbox for result in block]
        min_x = min([bbox[0][0] for bbox in all_bboxes])
        min_y = min([bbox[0][1] for bbox in all_bboxes])
        max_x = max([bbox[2][0] for bbox in all_bboxes])
        max_y = max([bbox[2][1] for bbox in all_bboxes])
        
        return [(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)]

class OCRResultValidator:
    """OCR 결과 검증 및 사용자 확인 인터페이스"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_results(self, ocr_results: List[OCRResult], confidence_threshold: float = 0.5) -> Dict[str, Any]:
        """OCR 결과 검증"""
        validated_results = []
        low_confidence_results = []
        missing_items = []
        
        for result in ocr_results:
            if result.confidence >= confidence_threshold:
                validated_results.append(result)
            else:
                low_confidence_results.append(result)
        
        # 누락된 항목 검출 (규제 준수성 관점에서)
        missing_items = self._detect_missing_items(validated_results)
        
        return {
            'validated_results': validated_results,
            'low_confidence_results': low_confidence_results,
            'missing_items': missing_items,
            'validation_summary': {
                'total_items': len(ocr_results),
                'validated_count': len(validated_results),
                'low_confidence_count': len(low_confidence_results),
                'missing_count': len(missing_items)
            }
        }
    
    def _detect_missing_items(self, validated_results: List[OCRResult]) -> List[str]:
        """누락된 항목 검출"""
        missing_items = []
        
        # 필수 라벨링 요소들
        required_elements = [
            '제품명', '성분', '영양성분', '유통기한', '보관방법',
            '제조사', '원산지', '알레르기', '용량', '가격'
        ]
        
        all_text = ' '.join([result.text for result in validated_results]).lower()
        
        for element in required_elements:
            if element.lower() not in all_text:
                missing_items.append(element)
        
        return missing_items
    
    def generate_user_interface_data(self, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """사용자 확인 인터페이스 데이터 생성"""
        return {
            'low_confidence_items': [
                {
                    'text': result.text,
                    'confidence': result.confidence,
                    'bbox': result.bbox,
                    'engine': result.engine,
                    'suggestions': self._generate_text_suggestions(result.text)
                }
                for result in validation_result['low_confidence_results']
            ],
            'missing_items': validation_result['missing_items'],
            'validation_summary': validation_result['validation_summary']
        }
    
    def _generate_text_suggestions(self, text: str) -> List[str]:
        """텍스트 수정 제안 생성"""
        suggestions = []
        
        # 일반적인 OCR 오류 패턴 수정
        common_errors = {
            '0': 'O',
            '1': 'l',
            '5': 'S',
            '8': 'B',
            'rn': 'm',
            'cl': 'd'
        }
        
        for error, correction in common_errors.items():
            if error in text:
                corrected = text.replace(error, correction)
                suggestions.append(corrected)
        
        return suggestions[:3]  # 최대 3개 제안

# 전역 인스턴스
advanced_ocr_processor = MultiEngineOCRProcessor()
ocr_validator = OCRResultValidator() 