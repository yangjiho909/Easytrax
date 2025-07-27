# natural_language_generator.py
# KATI2 자연어 출력 시스템 핵심 모듈

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import re
from collections import Counter
from datetime import datetime

class OutputType(Enum):
    CUSTOMS_ANALYSIS = "customs_analysis"
    REGULATION_INFO = "regulation_info"
    SYSTEM_PROCESS = "system_process"

@dataclass
class NLGContext:
    user_query: str
    analysis_type: OutputType
    data: Dict[str, Any]
    threshold_info: Optional[Dict[str, Any]] = None

class BaseNLG:
    """자연어 생성 기본 클래스"""
    
    def __init__(self):
        self.product_patterns = ['라면', '김치', '소주', '화장품', '전자제품', '의류', '신발', '가공식품']
        self.country_patterns = ['중국', '미국', '일본', 'EU', '동남아시아', '러시아', '캐나다', '호주']
    
    def extract_user_intent(self, query: str) -> tuple:
        """사용자 입력에서 제품과 국가 추출"""
        found_product = None
        found_country = None
        
        for product in self.product_patterns:
            if product in query:
                found_product = product
                break
        
        for country in self.country_patterns:
            if country in query:
                found_country = country
                break
        
        return found_product, found_country
    
    def clean_text(self, text: str) -> str:
        """텍스트 정리"""
        if not text or text == "정보 없음":
            return ""
        return str(text).strip()
    
    def format_percentage(self, value: float) -> str:
        """퍼센트 형식으로 변환"""
        return f"{value * 100:.1f}%" 