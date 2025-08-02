#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KOTRA 엑셀 데이터 처리기 (중국, 미국 대상) - 수정된 버전
글로벌 무역현황 및 해외유망시장추천 엑셀 파일을 파싱하여 구조화된 데이터로 변환
"""

import pandas as pd
import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging
from dataclasses import dataclass

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TradeData:
    """무역 데이터 구조"""
    country: str
    hs_code: str
    product_name: str
    export_amount: float
    import_amount: float
    trade_balance: float
    growth_rate: float
    market_share: float
    period: str
    source: str
    created_at: str

@dataclass
class MarketRecommendation:
    """시장 추천 데이터 구조"""
    country: str
    hs_code: str
    product_name: str
    recommendation_score: float
    market_potential: float
    growth_potential: float
    risk_level: str
    recommendation_reason: str
    period: str
    source: str
    created_at: str

class KOTRAExcelDataProcessor:
    """KOTRA 엑셀 데이터 처리기 (중국, 미국 대상)"""
    
    def __init__(self):
        self.data_dir = "data"
        self.cache_dir = "regulation_cache"
        
        # MVP 대상 국가
        self.target_countries = ["중국", "미국"]
        
        # 디렉토리 생성
        os.makedirs(self.cache_dir, exist_ok=True)
        
        logger.info("✅ KOTRA 엑셀 데이터 처리기 초기화 완료 (중국, 미국 대상)")
    
    def process_global_trade_data(self, filename: str) -> Dict[str, Any]:
        """글로벌 무역현황 엑셀 파일 처리"""
        try:
            filepath = os.path.join(self.data_dir, filename)
            logger.info(f"🔍 글로벌 무역현황 파일 처리 시작: {filename}")
            
            # 엑셀 파일 읽기
            df = pd.read_excel(filepath)
            
            logger.info(f"✅ 엑셀 파일 로드 완료: {len(df)}행, {len(df.columns)}열")
            logger.info(f"📊 컬럼 정보: {list(df.columns)}")
            
            # 중국, 미국 데이터만 필터링
            filtered_data = self._filter_target_countries(df, "글로벌 무역현황")
            
            # 데이터 구조화
            trade_data_list = self._extract_trade_data(filtered_data, "글로벌 무역현황")
            
            # 결과 저장
            result = {
                "source": "글로벌 무역현황",
                "filename": filename,
                "total_records": len(trade_data_list),
                "countries": self.target_countries,
                "data": [trade.__dict__ for trade in trade_data_list],
                "processed_at": datetime.now().isoformat()
            }
            
            # 캐시에 저장
            self._save_to_cache(result, "global_trade_data")
            
            logger.info(f"✅ 글로벌 무역현황 처리 완료: {len(trade_data_list)}개 레코드")
            return result
            
        except Exception as e:
            logger.error(f"❌ 글로벌 무역현황 처리 중 오류: {e}")
            return {"error": str(e)}
    
    def process_market_recommendation_data(self, filename: str) -> Dict[str, Any]:
        """해외유망시장추천 엑셀 파일 처리"""
        try:
            filepath = os.path.join(self.data_dir, filename)
            logger.info(f"🔍 해외유망시장추천 파일 처리 시작: {filename}")
            
            # 엑셀 파일 읽기
            df = pd.read_excel(filepath)
            
            logger.info(f"✅ 엑셀 파일 로드 완료: {len(df)}행, {len(df.columns)}열")
            logger.info(f"📊 컬럼 정보: {list(df.columns)}")
            
            # 중국, 미국 데이터만 필터링
            filtered_data = self._filter_target_countries(df, "해외유망시장추천")
            
            # 데이터 구조화
            recommendation_list = self._extract_recommendation_data(filtered_data, "해외유망시장추천")
            
            # 결과 저장
            result = {
                "source": "해외유망시장추천",
                "filename": filename,
                "total_records": len(recommendation_list),
                "countries": self.target_countries,
                "data": [rec.__dict__ for rec in recommendation_list],
                "processed_at": datetime.now().isoformat()
            }
            
            # 캐시에 저장
            self._save_to_cache(result, "market_recommendation_data")
            
            logger.info(f"✅ 해외유망시장추천 처리 완료: {len(recommendation_list)}개 레코드")
            return result
            
        except Exception as e:
            logger.error(f"❌ 해외유망시장추천 처리 중 오류: {e}")
            return {"error": str(e)}
    
    def _filter_target_countries(self, df: pd.DataFrame, source_type: str) -> pd.DataFrame:
        """중국, 미국 데이터만 필터링"""
        try:
            if source_type == "글로벌 무역현황":
                # 글로벌 무역현황: 컬럼 2에 국가 정보
                country_col = df.columns[2]
                logger.info(f"📍 글로벌 무역현황 국가 컬럼: {country_col}")
                
            elif source_type == "해외유망시장추천":
                # 해외유망시장추천: 컬럼 1에 국가 정보
                country_col = df.columns[1]
                logger.info(f"📍 해외유망시장추천 국가 컬럼: {country_col}")
                
            else:
                logger.warning("⚠️ 알 수 없는 소스 타입입니다.")
                return df
            
            # 중국, 미국 데이터만 필터링 (미국령사모아 제외)
            filtered_df = df[
                (df[country_col] == '중국') | 
                (df[country_col] == '미국') |
                (df[country_col] == 'China') | 
                (df[country_col] == 'USA') |
                (df[country_col] == 'United States')
            ]
            
            logger.info(f"✅ 필터링 완료: {len(filtered_df)}개 레코드 (중국, 미국)")
            return filtered_df
            
        except Exception as e:
            logger.error(f"❌ 국가 필터링 중 오류: {e}")
            return df
    
    def _extract_trade_data(self, df: pd.DataFrame, source: str) -> List[TradeData]:
        """무역 데이터 추출"""
        trade_data_list = []
        
        try:
            for _, row in df.iterrows():
                # 국가 정보 추출
                country = self._extract_country(row, source)
                if country not in self.target_countries:
                    continue
                
                # HS 코드 추출
                hs_code = self._extract_hs_code(row, source)
                
                # 제품명 추출
                product_name = self._extract_product_name(row, source)
                
                # 수출입 금액 추출
                export_amount = self._extract_amount(row, source, '수출', 'export', 'Export')
                import_amount = self._extract_amount(row, source, '수입', 'import', 'Import')
                trade_balance = export_amount - import_amount
                
                # 성장률 추출
                growth_rate = self._extract_growth_rate(row, source)
                
                # 시장점유율 추출
                market_share = self._extract_market_share(row, source)
                
                trade_data = TradeData(
                    country=country,
                    hs_code=hs_code,
                    product_name=product_name,
                    export_amount=export_amount,
                    import_amount=import_amount,
                    trade_balance=trade_balance,
                    growth_rate=growth_rate,
                    market_share=market_share,
                    period=datetime.now().strftime("%Y-%m"),
                    source=source,
                    created_at=datetime.now().isoformat()
                )
                
                trade_data_list.append(trade_data)
                
        except Exception as e:
            logger.error(f"❌ 무역 데이터 추출 중 오류: {e}")
        
        return trade_data_list
    
    def _extract_recommendation_data(self, df: pd.DataFrame, source: str) -> List[MarketRecommendation]:
        """시장 추천 데이터 추출"""
        recommendation_list = []
        
        try:
            for _, row in df.iterrows():
                # 국가 정보 추출
                country = self._extract_country(row, source)
                if country not in self.target_countries:
                    continue
                
                # HS 코드 추출
                hs_code = self._extract_hs_code(row, source)
                
                # 제품명 추출
                product_name = self._extract_product_name(row, source)
                
                # 추천 점수 추출
                recommendation_score = self._extract_recommendation_score(row, source)
                
                # 시장 잠재력 추출
                market_potential = self._extract_market_potential(row, source)
                
                # 성장 잠재력 추출
                growth_potential = self._extract_growth_potential(row, source)
                
                # 리스크 레벨 추출
                risk_level = self._extract_risk_level(row, source)
                
                # 추천 이유 추출
                recommendation_reason = self._extract_recommendation_reason(row, source)
                
                recommendation = MarketRecommendation(
                    country=country,
                    hs_code=hs_code,
                    product_name=product_name,
                    recommendation_score=recommendation_score,
                    market_potential=market_potential,
                    growth_potential=growth_potential,
                    risk_level=risk_level,
                    recommendation_reason=recommendation_reason,
                    period=datetime.now().strftime("%Y-%m"),
                    source=source,
                    created_at=datetime.now().isoformat()
                )
                
                recommendation_list.append(recommendation)
                
        except Exception as e:
            logger.error(f"❌ 시장 추천 데이터 추출 중 오류: {e}")
        
        return recommendation_list
    
    def _extract_country(self, row, source: str) -> str:
        """국가 정보 추출"""
        try:
            if source == "글로벌 무역현황":
                # 컬럼 2에서 국가 정보 추출
                value = str(row.iloc[2]).strip()
            elif source == "해외유망시장추천":
                # 컬럼 1에서 국가 정보 추출
                value = str(row.iloc[1]).strip()
            else:
                return '미분류'
            
            if '중국' in value or 'China' in value:
                return '중국'
            elif '미국' in value or 'USA' in value or 'United States' in value:
                return '미국'
            return '미분류'
            
        except Exception as e:
            logger.error(f"❌ 국가 정보 추출 중 오류: {e}")
            return '미분류'
    
    def _extract_hs_code(self, row, source: str) -> str:
        """HS 코드 추출"""
        try:
            # HS 코드는 보통 6자리 숫자
            for i, value in enumerate(row):
                if pd.notna(value):
                    value_str = str(value).strip()
                    if re.match(r'^\d{6}$', value_str):
                        return value_str
            return '000000'
        except Exception as e:
            logger.error(f"❌ HS 코드 추출 중 오류: {e}")
            return '000000'
    
    def _extract_product_name(self, row, source: str) -> str:
        """제품명 추출"""
        try:
            # 제품명은 보통 텍스트 형태
            for i, value in enumerate(row):
                if pd.notna(value):
                    value_str = str(value).strip()
                    if value_str and value_str != 'nan' and len(value_str) > 2:
                        # 숫자나 특수문자만 있는 경우 제외
                        if not re.match(r'^[\d\s\-\.\,]+$', value_str):
                            return value_str
            return '미분류'
        except Exception as e:
            logger.error(f"❌ 제품명 추출 중 오류: {e}")
            return '미분류'
    
    def _extract_amount(self, row, source: str, *keywords) -> float:
        """금액 추출"""
        try:
            for i, value in enumerate(row):
                if pd.notna(value):
                    value_str = str(value).strip()
                    # 쉼표 제거 후 숫자 변환 시도
                    if ',' in value_str:
                        value_str = value_str.replace(',', '')
                    try:
                        return float(value_str)
                    except:
                        continue
            return 0.0
        except Exception as e:
            logger.error(f"❌ 금액 추출 중 오류: {e}")
            return 0.0
    
    def _extract_growth_rate(self, row, source: str) -> float:
        """성장률 추출"""
        try:
            for i, value in enumerate(row):
                if pd.notna(value):
                    value_str = str(value).strip()
                    if '%' in value_str:
                        value_str = value_str.replace('%', '')
                    try:
                        return float(value_str)
                    except:
                        continue
            return 0.0
        except Exception as e:
            logger.error(f"❌ 성장률 추출 중 오류: {e}")
            return 0.0
    
    def _extract_market_share(self, row, source: str) -> float:
        """시장점유율 추출"""
        try:
            for i, value in enumerate(row):
                if pd.notna(value):
                    value_str = str(value).strip()
                    if '%' in value_str:
                        value_str = value_str.replace('%', '')
                    try:
                        return float(value_str)
                    except:
                        continue
            return 0.0
        except Exception as e:
            logger.error(f"❌ 시장점유율 추출 중 오류: {e}")
            return 0.0
    
    def _extract_recommendation_score(self, row, source: str) -> float:
        """추천 점수 추출"""
        try:
            for i, value in enumerate(row):
                if pd.notna(value):
                    try:
                        return float(value)
                    except:
                        continue
            return 0.0
        except Exception as e:
            logger.error(f"❌ 추천 점수 추출 중 오류: {e}")
            return 0.0
    
    def _extract_market_potential(self, row, source: str) -> float:
        """시장 잠재력 추출"""
        try:
            for i, value in enumerate(row):
                if pd.notna(value):
                    try:
                        return float(value)
                    except:
                        continue
            return 0.0
        except Exception as e:
            logger.error(f"❌ 시장 잠재력 추출 중 오류: {e}")
            return 0.0
    
    def _extract_growth_potential(self, row, source: str) -> float:
        """성장 잠재력 추출"""
        try:
            for i, value in enumerate(row):
                if pd.notna(value):
                    try:
                        return float(value)
                    except:
                        continue
            return 0.0
        except Exception as e:
            logger.error(f"❌ 성장 잠재력 추출 중 오류: {e}")
            return 0.0
    
    def _extract_risk_level(self, row, source: str) -> str:
        """리스크 레벨 추출"""
        try:
            for i, value in enumerate(row):
                if pd.notna(value):
                    value_str = str(value).strip()
                    if value_str and value_str != 'nan':
                        return value_str
            return '보통'
        except Exception as e:
            logger.error(f"❌ 리스크 레벨 추출 중 오류: {e}")
            return '보통'
    
    def _extract_recommendation_reason(self, row, source: str) -> str:
        """추천 이유 추출"""
        try:
            for i, value in enumerate(row):
                if pd.notna(value):
                    value_str = str(value).strip()
                    if value_str and value_str != 'nan' and len(value_str) > 5:
                        return value_str
            return '시장 잠재력이 높음'
        except Exception as e:
            logger.error(f"❌ 추천 이유 추출 중 오류: {e}")
            return '시장 잠재력이 높음'
    
    def _save_to_cache(self, data: Dict, cache_key: str):
        """캐시에 저장"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"kotra_{cache_key}_{timestamp}.json"
            filepath = os.path.join(self.cache_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ 캐시 저장 완료: {filepath}")
            
        except Exception as e:
            logger.error(f"❌ 캐시 저장 오류: {e}")
    
    def process_all_excel_files(self) -> Dict[str, Any]:
        """모든 엑셀 파일 처리"""
        results = {
            "success": True,
            "processed_files": [],
            "errors": [],
            "total_records": 0
        }
        
        try:
            # data 폴더의 엑셀 파일들 찾기
            excel_files = []
            for file in os.listdir(self.data_dir):
                if file.endswith('.xlsx') or file.endswith('.xls'):
                    excel_files.append(file)
            
            logger.info(f"🔍 발견된 엑셀 파일: {len(excel_files)}개")
            
            for excel_file in excel_files:
                try:
                    if '글로벌 무역현황' in excel_file:
                        result = self.process_global_trade_data(excel_file)
                        results["processed_files"].append({
                            "filename": excel_file,
                            "type": "글로벌 무역현황",
                            "records": result.get("total_records", 0)
                        })
                        results["total_records"] += result.get("total_records", 0)
                        
                    elif '해외유망시장추천' in excel_file:
                        result = self.process_market_recommendation_data(excel_file)
                        results["processed_files"].append({
                            "filename": excel_file,
                            "type": "해외유망시장추천",
                            "records": result.get("total_records", 0)
                        })
                        results["total_records"] += result.get("total_records", 0)
                        
                except Exception as e:
                    results["errors"].append({
                        "filename": excel_file,
                        "error": str(e)
                    })
            
            logger.info(f"✅ 모든 엑셀 파일 처리 완료: {results['total_records']}개 레코드")
            return results
            
        except Exception as e:
            results["success"] = False
            results["errors"].append({"error": str(e)})
            logger.error(f"❌ 전체 엑셀 파일 처리 중 오류: {e}")
            return results

def main():
    """메인 실행 함수"""
    processor = KOTRAExcelDataProcessor()
    
    print("🚀 KOTRA 엑셀 데이터 처리 시작 (중국, 미국 대상)")
    print("=" * 60)
    
    # 모든 엑셀 파일 처리
    results = processor.process_all_excel_files()
    
    print(f"📊 처리 결과:")
    print(f"   - 성공: {results['success']}")
    print(f"   - 처리된 파일: {len(results['processed_files'])}개")
    print(f"   - 총 레코드: {results['total_records']}개")
    print(f"   - 오류: {len(results['errors'])}개")
    
    if results['processed_files']:
        print(f"\n✅ 성공적으로 처리된 파일:")
        for file_info in results['processed_files']:
            print(f"   - {file_info['filename']} ({file_info['type']}): {file_info['records']}개 레코드")
    
    if results['errors']:
        print(f"\n❌ 처리 실패한 파일:")
        for error_info in results['errors']:
            print(f"   - {error_info['filename']}: {error_info['error']}")

if __name__ == "__main__":
    main() 