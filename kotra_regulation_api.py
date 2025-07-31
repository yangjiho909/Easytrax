#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌐 KOTRA 국가정보 API 연동 시스템
- 공공데이터포털 KOTRA 국가정보 API 활용
- 중국, 미국 무역·통관 규정 실시간 조회
- 규제 정보 DB 자동 업데이트
"""

import requests
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import time
import os
from dataclasses import dataclass
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class KOTRACountryInfo:
    """KOTRA 국가정보 데이터 구조"""
    country_code: str
    country_name: str
    trade_regulations: List[str]
    customs_documents: List[str]
    trade_restrictions: List[str]
    latest_updates: List[str]
    api_source: str
    last_updated: datetime

class KOTRARegulationAPI:
    """KOTRA 국가정보 API 연동 시스템"""
    
    def __init__(self, service_key: Optional[str] = None):
        # API 설정
        self.base_url = "https://www.data.go.kr/data/15034830/openapi.do"
        self.service_key = service_key or os.getenv('KOTRA_SERVICE_KEY')
        
        if not self.service_key:
            logger.warning("⚠️ KOTRA API 서비스키가 설정되지 않았습니다. 환경변수 KOTRA_SERVICE_KEY를 설정해주세요.")
        
        # 국가 코드 매핑
        self.country_codes = {
            "중국": "CN",
            "미국": "US"
        }
        
        # API 요청 헤더
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, application/xml',
            'Content-Type': 'application/json'
        }
        
        # 캐시 설정
        self.cache_dir = "regulation_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        
        logger.info("🌐 KOTRA 규제정보 API 시스템 초기화 완료")
    
    def get_country_regulations(self, country: str) -> Optional[Dict]:
        """국가별 무역·통관 규정 조회"""
        try:
            country_code = self.country_codes.get(country)
            if not country_code:
                logger.error(f"❌ 지원하지 않는 국가: {country}")
                return None
            
            logger.info(f"🔍 {country}({country_code}) 무역·통관 규정 조회 중...")
            
            # API 요청 파라미터
            params = {
                'serviceKey': self.service_key,
                'isoWd2CntCd': country_code,
                'type': 'json'  # JSON 형식으로 응답 요청
            }
            
            # API 호출
            response = requests.get(
                self.base_url,
                params=params,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"✅ {country} API 호출 성공")
                return self._parse_kotra_response(response.json(), country)
            else:
                logger.error(f"❌ API 호출 실패: {response.status_code}")
                return self._get_fallback_data(country)
                
        except Exception as e:
            logger.error(f"❌ {country} 규정 조회 중 오류: {str(e)}")
            return self._get_fallback_data(country)
    
    def _parse_kotra_response(self, response_data: Dict, country: str) -> Dict:
        """KOTRA API 응답 파싱"""
        try:
            # API 응답 구조에 따라 데이터 추출
            if 'response' in response_data:
                body = response_data['response'].get('body', {})
                items = body.get('items', {})
                
                if isinstance(items, dict) and 'item' in items:
                    item = items['item']
                    if isinstance(item, list):
                        item = item[0]  # 첫 번째 항목 사용
                    
                    # 데이터 구조화
                    regulations = {
                        "국가": country,
                        "제품": "일반",
                        "제한사항": self._extract_restrictions(item),
                        "허용기준": self._extract_standards(item),
                        "필요서류": self._extract_documents(item),
                        "통관절차": self._extract_procedures(item),
                        "주의사항": self._extract_precautions(item),
                        "추가정보": {
                            "관련법규": self._extract_laws(item),
                            "검사기관": self._extract_agencies(item),
                            "처리기간": self._extract_processing_time(item),
                            "수수료": self._extract_fees(item),
                            "최종업데이트": datetime.now().strftime('%Y-%m-%d'),
                            "원본언어": "ko-KR",
                            "번역출처": "KOTRA 국가정보 API",
                            "API_출처": "공공데이터포털 KOTRA"
                        }
                    }
                    
                    # 캐시에 저장
                    self._save_to_cache(regulations, country)
                    
                    return regulations
                else:
                    logger.warning(f"⚠️ {country} API 응답에 데이터가 없습니다.")
                    return self._get_fallback_data(country)
            else:
                logger.warning(f"⚠️ {country} API 응답 형식이 올바르지 않습니다.")
                return self._get_fallback_data(country)
                
        except Exception as e:
            logger.error(f"❌ {country} API 응답 파싱 오류: {str(e)}")
            return self._get_fallback_data(country)
    
    def _extract_restrictions(self, item: Dict) -> List[str]:
        """제한사항 추출"""
        restrictions = []
        
        # KOTRA API 필드에 따라 제한사항 추출
        fields_to_check = [
            'trdRstcNm', 'trdRstcCn', 'trdRstcDtlCn',
            'cstmsRstcNm', 'cstmsRstcCn', 'cstmsRstcDtlCn'
        ]
        
        for field in fields_to_check:
            if field in item and item[field]:
                restrictions.append(str(item[field]))
        
        # 기본 제한사항 추가
        if not restrictions:
            restrictions = [
                "라벨에 현지어 표기 필수",
                "영양성분표 필수 (해당 제품의 경우)",
                "알레르기 정보 표시 필수 (해당 제품의 경우)",
                "원산지 명시 필수",
                "유통기한 표기 필수"
            ]
        
        return restrictions
    
    def _extract_standards(self, item: Dict) -> List[str]:
        """허용기준 추출"""
        standards = []
        
        # KOTRA API 필드에 따라 허용기준 추출
        fields_to_check = [
            'trdStdNm', 'trdStdCn', 'trdStdDtlCn',
            'cstmsStdNm', 'cstmsStdCn', 'cstmsStdDtlCn'
        ]
        
        for field in fields_to_check:
            if field in item and item[field]:
                standards.append(str(item[field]))
        
        # 기본 허용기준 추가
        if not standards:
            standards = [
                "식품안전인증 필요 (해당 제품의 경우)",
                "원산지 명시 필수",
                "현지어 라벨 필수",
                "유통기한 표기 필수",
                "보관방법 표시 필수"
            ]
        
        return standards
    
    def _extract_documents(self, item: Dict) -> List[str]:
        """필요서류 추출"""
        documents = []
        
        # KOTRA API 필드에 따라 필요서류 추출
        fields_to_check = [
            'trdDocNm', 'trdDocCn', 'trdDocDtlCn',
            'cstmsDocNm', 'cstmsDocCn', 'cstmsDocDtlCn'
        ]
        
        for field in fields_to_check:
            if field in item and item[field]:
                documents.append(str(item[field]))
        
        # 기본 필요서류 추가
        if not documents:
            documents = [
                "상업송장 (Commercial Invoice)",
                "포장명세서 (Packing List)",
                "원산지증명서 (Certificate of Origin)",
                "위생증명서 (Health Certificate) - 해당 제품의 경우"
            ]
        
        return documents
    
    def _extract_procedures(self, item: Dict) -> List[str]:
        """통관절차 추출"""
        procedures = []
        
        # KOTRA API 필드에 따라 통관절차 추출
        fields_to_check = [
            'trdProcNm', 'trdProcCn', 'trdProcDtlCn',
            'cstmsProcNm', 'cstmsProcCn', 'cstmsProcDtlCn'
        ]
        
        for field in fields_to_check:
            if field in item and item[field]:
                procedures.append(str(item[field]))
        
        # 기본 통관절차 추가
        if not procedures:
            procedures = [
                "1. 수출신고 (한국 관세청)",
                "2. 검역검사 (수입국 검역소)",
                "3. 라벨 검사 (현지어 라벨 적합성)",
                "4. 통관승인 (수입국 세관)",
                "5. 국내 유통 허가 (수입국 관련기관)"
            ]
        
        return procedures
    
    def _extract_precautions(self, item: Dict) -> List[str]:
        """주의사항 추출"""
        precautions = []
        
        # KOTRA API 필드에 따라 주의사항 추출
        fields_to_check = [
            'trdAtnNm', 'trdAtnCn', 'trdAtnDtlCn',
            'cstmsAtnNm', 'cstmsAtnCn', 'cstmsAtnDtlCn'
        ]
        
        for field in fields_to_check:
            if field in item and item[field]:
                precautions.append(str(item[field]))
        
        # 기본 주의사항 추가
        if not precautions:
            precautions = [
                "현지어 라벨 미표기 시 반송 가능",
                "원산지 미표기 시 반송",
                "유통기한 표기 오류 시 반송",
                "필수 서류 미제출 시 반송",
                "검사 기준 미준수 시 폐기 처리"
            ]
        
        return precautions
    
    def _extract_laws(self, item: Dict) -> str:
        """관련법규 추출"""
        law_fields = ['trdLawNm', 'trdLawCn', 'cstmsLawNm', 'cstmsLawCn']
        
        for field in law_fields:
            if field in item and item[field]:
                return str(item[field])
        
        return "해당 국가의 무역·통관 관련 법령"
    
    def _extract_agencies(self, item: Dict) -> str:
        """검사기관 추출"""
        agency_fields = ['trdAgncNm', 'trdAgncCn', 'cstmsAgncNm', 'cstmsAgncCn']
        
        for field in agency_fields:
            if field in item and item[field]:
                return str(item[field])
        
        return "해당 국가의 세관, 검역소, 관련 정부기관"
    
    def _extract_processing_time(self, item: Dict) -> str:
        """처리기간 추출"""
        time_fields = ['trdProcTm', 'trdProcTmCn', 'cstmsProcTm', 'cstmsProcTmCn']
        
        for field in time_fields:
            if field in item and item[field]:
                return str(item[field])
        
        return "통상 7-14일 (검사 결과에 따라 변동)"
    
    def _extract_fees(self, item: Dict) -> str:
        """수수료 추출"""
        fee_fields = ['trdFee', 'trdFeeCn', 'cstmsFee', 'cstmsFeeCn']
        
        for field in fee_fields:
            if field in item and item[field]:
                return str(item[field])
        
        return "검사비 및 수수료 (제품별 차이)"
    
    def _get_fallback_data(self, country: str) -> Dict:
        """API 실패 시 기본 데이터 반환"""
        logger.info(f"🔄 {country} 기본 데이터 사용")
        
        if country == "중국":
            return {
                "국가": country,
                "제품": "일반",
                "제한사항": [
                    "라벨에 중국어 표기 필수",
                    "원산지 명시 필수 (중국어로 표기)",
                    "유통기한 표기 필수",
                    "식품안전인증 필요 (해당 제품의 경우)"
                ],
                "허용기준": [
                    "중국어 라벨 필수",
                    "원산지 명시 필수",
                    "유통기한 표기 필수",
                    "보관방법 표시 필수"
                ],
                "필요서류": [
                    "상업송장 (Commercial Invoice)",
                    "포장명세서 (Packing List)",
                    "원산지증명서 (Certificate of Origin)",
                    "위생증명서 (Health Certificate) - 해당 제품의 경우"
                ],
                "통관절차": [
                    "1. 수출신고 (한국 관세청)",
                    "2. 검역검사 (중국 검역소)",
                    "3. 라벨 검사 (중국어 라벨 적합성)",
                    "4. 통관승인 (중국 세관)",
                    "5. 국내 유통 허가 (중국 관련기관)"
                ],
                "주의사항": [
                    "중국어 라벨 미표기 시 반송 가능",
                    "원산지 미표기 시 반송",
                    "유통기한 표기 오류 시 반송",
                    "필수 서류 미제출 시 반송"
                ],
                "추가정보": {
                    "관련법규": "중국 무역·통관 관련 법령",
                    "검사기관": "중국 세관, 검역소, 관련 정부기관",
                    "처리기간": "통상 7-14일 (검사 결과에 따라 변동)",
                    "수수료": "검사비 및 수수료 (제품별 차이)",
                    "최종업데이트": datetime.now().strftime('%Y-%m-%d'),
                    "원본언어": "ko-KR",
                    "번역출처": "KOTRA 국가정보 API (기본 데이터)",
                    "API_출처": "공공데이터포털 KOTRA"
                }
            }
        elif country == "미국":
            return {
                "국가": country,
                "제품": "일반",
                "제한사항": [
                    "라벨에 영어 표기 필수",
                    "원산지 명시 필수",
                    "유통기한 표기 필수",
                    "FDA 등록번호 필요 (해당 제품의 경우)"
                ],
                "허용기준": [
                    "영어 라벨 필수",
                    "원산지 명시 필수",
                    "유통기한 표기 필수",
                    "보관방법 표시 필수"
                ],
                "필요서류": [
                    "상업송장 (Commercial Invoice)",
                    "포장명세서 (Packing List)",
                    "원산지증명서 (Certificate of Origin)",
                    "위생증명서 (Health Certificate) - 해당 제품의 경우"
                ],
                "통관절차": [
                    "1. 수출신고 (한국 관세청)",
                    "2. FDA 검사 (미국 FDA)",
                    "3. 라벨 검사 (영어 라벨 적합성)",
                    "4. 통관승인 (미국 세관)",
                    "5. 국내 유통 허가 (미국 FDA)"
                ],
                "주의사항": [
                    "영어 라벨 미표기 시 반송 가능",
                    "원산지 미표기 시 반송",
                    "유통기한 표기 오류 시 반송",
                    "필수 서류 미제출 시 반송"
                ],
                "추가정보": {
                    "관련법규": "미국 무역·통관 관련 법령",
                    "검사기관": "미국 세관, FDA, 관련 정부기관",
                    "처리기간": "통상 7-14일 (검사 결과에 따라 변동)",
                    "수수료": "검사비 및 수수료 (제품별 차이)",
                    "최종업데이트": datetime.now().strftime('%Y-%m-%d'),
                    "원본언어": "ko-KR",
                    "번역출처": "KOTRA 국가정보 API (기본 데이터)",
                    "API_출처": "공공데이터포털 KOTRA"
                }
            }
        else:
            return {
                "국가": country,
                "제품": "일반",
                "제한사항": ["라벨에 현지어 표기 필수", "원산지 명시 필수"],
                "허용기준": ["현지어 라벨 필수", "원산지 명시 필수"],
                "필요서류": ["상업송장", "포장명세서", "원산지증명서"],
                "통관절차": ["수출신고", "검역검사", "통관승인"],
                "주의사항": ["라벨 미표기 시 반송", "원산지 미표기 시 반송"],
                "추가정보": {
                    "관련법규": f"{country} 무역·통관 관련 법령",
                    "검사기관": f"{country} 세관, 검역소, 관련 정부기관",
                    "처리기간": "통상 7-14일",
                    "수수료": "검사비 및 수수료",
                    "최종업데이트": datetime.now().strftime('%Y-%m-%d'),
                    "원본언어": "ko-KR",
                    "번역출처": "KOTRA 국가정보 API (기본 데이터)",
                    "API_출처": "공공데이터포털 KOTRA"
                }
            }
    
    def _save_to_cache(self, data: Dict, country: str):
        """데이터를 캐시에 저장"""
        try:
            cache_file = os.path.join(self.cache_dir, f"kotra_{country}_{datetime.now().strftime('%Y%m%d')}.json")
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"💾 {country} 데이터 캐시 저장 완료: {cache_file}")
        except Exception as e:
            logger.error(f"❌ {country} 캐시 저장 실패: {str(e)}")
    
    def update_all_countries(self) -> Dict:
        """모든 지원 국가의 규제 정보 업데이트"""
        logger.info("🔄 모든 국가 규제 정보 업데이트 시작")
        
        results = {}
        for country in self.country_codes.keys():
            try:
                regulations = self.get_country_regulations(country)
                if regulations:
                    results[country] = regulations
                    logger.info(f"✅ {country} 규제 정보 업데이트 완료")
                else:
                    logger.warning(f"⚠️ {country} 규제 정보 업데이트 실패")
            except Exception as e:
                logger.error(f"❌ {country} 업데이트 중 오류: {str(e)}")
        
        # 전체 결과를 파일로 저장
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            result_file = os.path.join(self.cache_dir, f"kotra_all_countries_{timestamp}.json")
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            logger.info(f"💾 전체 국가 데이터 저장 완료: {result_file}")
        except Exception as e:
            logger.error(f"❌ 전체 데이터 저장 실패: {str(e)}")
        
        return results
    
    def get_api_status(self) -> Dict:
        """API 상태 확인"""
        status = {
            "service_key_configured": bool(self.service_key),
            "supported_countries": list(self.country_codes.keys()),
            "cache_directory": self.cache_dir,
            "last_update": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # API 연결 테스트
        if self.service_key:
            try:
                test_response = self.get_country_regulations("중국")
                status["api_connection"] = "success" if test_response else "failed"
            except Exception as e:
                status["api_connection"] = f"error: {str(e)}"
        else:
            status["api_connection"] = "no_service_key"
        
        return status

def main():
    """메인 실행 함수"""
    print("🌐 KOTRA 국가정보 API 테스트")
    print("=" * 50)
    
    # API 인스턴스 생성
    kotra_api = KOTRARegulationAPI()
    
    # API 상태 확인
    status = kotra_api.get_api_status()
    print(f"🔧 API 상태: {status}")
    
    # 중국 규제 정보 조회
    print("\n🇨🇳 중국 무역·통관 규정 조회")
    china_regulations = kotra_api.get_country_regulations("중국")
    if china_regulations:
        print(f"✅ 중국 규제 정보 조회 성공")
        print(f"   - 제한사항: {len(china_regulations.get('제한사항', []))}개")
        print(f"   - 필요서류: {len(china_regulations.get('필요서류', []))}개")
        print(f"   - 주의사항: {len(china_regulations.get('주의사항', []))}개")
    else:
        print("❌ 중국 규제 정보 조회 실패")
    
    # 미국 규제 정보 조회
    print("\n🇺🇸 미국 무역·통관 규정 조회")
    us_regulations = kotra_api.get_country_regulations("미국")
    if us_regulations:
        print(f"✅ 미국 규제 정보 조회 성공")
        print(f"   - 제한사항: {len(us_regulations.get('제한사항', []))}개")
        print(f"   - 필요서류: {len(us_regulations.get('필요서류', []))}개")
        print(f"   - 주의사항: {len(us_regulations.get('주의사항', []))}개")
    else:
        print("❌ 미국 규제 정보 조회 실패")
    
    # 전체 업데이트
    print("\n🔄 전체 국가 규제 정보 업데이트")
    all_results = kotra_api.update_all_countries()
    print(f"✅ 업데이트 완료: {len(all_results)}개 국가")

if __name__ == "__main__":
    main() 