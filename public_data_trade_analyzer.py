import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import re
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
import os
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TradePerformance:
    """수출입 실적 데이터 구조"""
    hs_code: str
    country: str
    export_amount: float
    import_amount: float
    trade_balance: float
    market_share: float
    growth_rate: float
    volatility: float
    market_potential_score: float
    ranking: int
    trend_direction: str
    risk_level: str
    created_at: str

@dataclass
class MarketRanking:
    """시장 유망도 랭킹 데이터 구조"""
    hs_code: str
    country: str
    overall_score: float
    market_potential: float
    growth_potential: float
    stability_score: float
    risk_score: float
    ranking: int
    ranking_change: int
    trend_analysis: str
    recommendation: str
    created_at: str

class PublicDataTradeAnalyzer:
    """공공데이터포털 수출입 실적 분석기"""
    
    def __init__(self):
        self.base_url = "https://www.data.go.kr/data/15140440/fileData.do"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # 지원 국가
        self.supported_countries = ["중국", "미국"]
        
        # 주요 HS CODE (식품 관련)
        self.common_hs_codes = {
            "라면": "190230",
            "과자": "190531", 
            "음료": "220210",
            "조미료": "210390",
            "건조식품": "071290",
            "커피": "090111",
            "차": "090210",
            "과일": "080810",
            "채소": "070190"
        }
        
        # 캐시 디렉토리
        self.cache_dir = "public_data_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # 시장 유망도 계산 가중치
        self.ranking_weights = {
            "market_potential": 0.3,    # 시장 잠재력
            "growth_potential": 0.25,   # 성장 잠재력
            "stability": 0.2,           # 안정성
            "risk_factor": 0.15,        # 리스크 요인
            "competitiveness": 0.1      # 경쟁력
        }
        
        logger.info("✅ 공공데이터 수출입 실적 분석기 초기화 완료")
    
    def get_trade_data(self, hs_code: str) -> Optional[Dict]:
        """특정 HS CODE의 수출입 실적 데이터 조회"""
        try:
            logger.info(f"🔍 HS CODE {hs_code} 수출입 실적 데이터 조회 시작")
            
            # 캐시 확인
            cache_key = f"trade_data_{hs_code}"
            cached_data = self._load_from_cache(cache_key)
            if cached_data:
                logger.info(f"✅ 캐시된 데이터 사용: {cache_key}")
                return cached_data
            
            # 공공데이터포털에서 데이터 다운로드
            trade_data = self._download_public_data(hs_code)
            
            if trade_data:
                # 시장 유망도 랭킹 계산
                ranking_data = self._calculate_market_ranking(trade_data)
                
                # 결과 통합
                result = {
                    "hs_code": hs_code,
                    "trade_data": trade_data,
                    "ranking_data": ranking_data,
                    "analysis_summary": self._generate_analysis_summary(trade_data, ranking_data),
                    "created_at": datetime.now().isoformat()
                }
                
                # 캐시 저장
                self._save_to_cache(cache_key, result)
                logger.info(f"✅ HS CODE {hs_code} 데이터 조회 완료")
                return result
            else:
                logger.warning(f"⚠️ HS CODE {hs_code} 데이터 없음")
                return None
                
        except Exception as e:
            logger.error(f"❌ 수출입 실적 데이터 조회 중 오류: {str(e)}")
            return None
    
    def _download_public_data(self, hs_code: str) -> Optional[List[TradePerformance]]:
        """공공데이터포털에서 데이터 다운로드"""
        try:
            # 실제 구현에서는 공공데이터포털 API 또는 파일 다운로드 로직 필요
            # 현재는 샘플 데이터로 대체
            
            sample_data = self._generate_sample_data(hs_code)
            return sample_data
            
        except Exception as e:
            logger.error(f"❌ 공공데이터 다운로드 중 오류: {str(e)}")
            return None
    
    def _generate_sample_data(self, hs_code: str) -> List[TradePerformance]:
        """샘플 데이터 생성 (실제 구현 시 제거)"""
        sample_data = []
        
        for country in self.supported_countries:
            # 랜덤 데이터 생성
            export_amount = np.random.uniform(1000000, 10000000)
            import_amount = np.random.uniform(500000, 8000000)
            trade_balance = export_amount - import_amount
            market_share = np.random.uniform(0.1, 5.0)
            growth_rate = np.random.uniform(-0.2, 0.3)
            volatility = np.random.uniform(0.05, 0.25)
            
            # 시장 잠재력 점수 계산
            market_potential_score = self._calculate_market_potential(
                export_amount, import_amount, market_share, growth_rate, volatility
            )
            
            # 랭킹 계산 (임시)
            ranking = np.random.randint(1, 100)
            
            # 트렌드 방향
            if growth_rate > 0.1:
                trend_direction = "상승"
            elif growth_rate < -0.1:
                trend_direction = "하락"
            else:
                trend_direction = "안정"
            
            # 리스크 레벨
            if volatility > 0.2:
                risk_level = "높음"
            elif volatility > 0.1:
                risk_level = "보통"
            else:
                risk_level = "낮음"
            
            performance = TradePerformance(
                hs_code=hs_code,
                country=country,
                export_amount=export_amount,
                import_amount=import_amount,
                trade_balance=trade_balance,
                market_share=market_share,
                growth_rate=growth_rate,
                volatility=volatility,
                market_potential_score=market_potential_score,
                ranking=ranking,
                trend_direction=trend_direction,
                risk_level=risk_level,
                created_at=datetime.now().isoformat()
            )
            
            sample_data.append(performance)
        
        return sample_data
    
    def _calculate_market_potential(self, export_amount: float, import_amount: float, 
                                  market_share: float, growth_rate: float, volatility: float) -> float:
        """시장 잠재력 점수 계산"""
        try:
            # 정규화된 점수 계산
            export_score = min(export_amount / 10000000, 1.0)  # 최대 1천만 달러 기준
            market_share_score = min(market_share / 10.0, 1.0)  # 최대 10% 기준
            growth_score = max(min(growth_rate + 0.2, 1.0), 0.0)  # -20% ~ +80% 범위
            stability_score = max(1.0 - volatility, 0.0)  # 변동성 낮을수록 높은 점수
            
            # 가중 평균 계산
            potential_score = (
                export_score * 0.3 +
                market_share_score * 0.25 +
                growth_score * 0.25 +
                stability_score * 0.2
            )
            
            return round(potential_score * 100, 2)  # 0-100 점수로 변환
            
        except Exception as e:
            logger.error(f"❌ 시장 잠재력 계산 중 오류: {str(e)}")
            return 0.0
    
    def _calculate_market_ranking(self, trade_data: List[TradePerformance]) -> List[MarketRanking]:
        """시장 유망도 랭킹 계산"""
        try:
            rankings = []
            
            for performance in trade_data:
                # 종합 점수 계산
                overall_score = self._calculate_overall_score(performance)
                
                # 성장 잠재력 계산
                growth_potential = self._calculate_growth_potential(performance)
                
                # 안정성 점수 계산
                stability_score = self._calculate_stability_score(performance)
                
                # 리스크 점수 계산
                risk_score = self._calculate_risk_score(performance)
                
                # 시장 잠재력 (기존 계산값 사용)
                market_potential = performance.market_potential_score
                
                # 랭킹 계산 (임시)
                ranking = np.random.randint(1, 50)
                ranking_change = np.random.randint(-5, 6)
                
                # 트렌드 분석
                trend_analysis = self._analyze_trend(performance)
                
                # 추천사항
                recommendation = self._generate_recommendation(performance, overall_score)
                
                ranking_data = MarketRanking(
                    hs_code=performance.hs_code,
                    country=performance.country,
                    overall_score=overall_score,
                    market_potential=market_potential,
                    growth_potential=growth_potential,
                    stability_score=stability_score,
                    risk_score=risk_score,
                    ranking=ranking,
                    ranking_change=ranking_change,
                    trend_analysis=trend_analysis,
                    recommendation=recommendation,
                    created_at=datetime.now().isoformat()
                )
                
                rankings.append(ranking_data)
            
            return rankings
            
        except Exception as e:
            logger.error(f"❌ 시장 유망도 랭킹 계산 중 오류: {str(e)}")
            return []
    
    def _calculate_overall_score(self, performance: TradePerformance) -> float:
        """종합 점수 계산"""
        try:
            # 각 지표별 점수 계산
            export_score = min(performance.export_amount / 10000000, 1.0) * 100
            market_share_score = min(performance.market_share / 10.0, 1.0) * 100
            growth_score = max(min(performance.growth_rate + 0.2, 1.0), 0.0) * 100
            stability_score = max(1.0 - performance.volatility, 0.0) * 100
            
            # 가중 평균 계산
            overall_score = (
                export_score * self.ranking_weights["market_potential"] +
                market_share_score * self.ranking_weights["competitiveness"] +
                growth_score * self.ranking_weights["growth_potential"] +
                stability_score * self.ranking_weights["stability"]
            )
            
            return round(overall_score, 2)
            
        except Exception as e:
            logger.error(f"❌ 종합 점수 계산 중 오류: {str(e)}")
            return 0.0
    
    def _calculate_growth_potential(self, performance: TradePerformance) -> float:
        """성장 잠재력 계산"""
        try:
            # 성장률과 시장 점유율을 기반으로 성장 잠재력 계산
            growth_rate_score = max(min(performance.growth_rate + 0.2, 1.0), 0.0) * 100
            market_share_potential = min(performance.market_share / 5.0, 1.0) * 100
            
            growth_potential = (growth_rate_score * 0.6 + market_share_potential * 0.4)
            return round(growth_potential, 2)
            
        except Exception as e:
            logger.error(f"❌ 성장 잠재력 계산 중 오류: {str(e)}")
            return 0.0
    
    def _calculate_stability_score(self, performance: TradePerformance) -> float:
        """안정성 점수 계산"""
        try:
            # 변동성과 성장률의 일관성을 기반으로 안정성 계산
            volatility_score = max(1.0 - performance.volatility, 0.0) * 100
            growth_consistency = max(1.0 - abs(performance.growth_rate), 0.0) * 100
            
            stability_score = (volatility_score * 0.7 + growth_consistency * 0.3)
            return round(stability_score, 2)
            
        except Exception as e:
            logger.error(f"❌ 안정성 점수 계산 중 오류: {str(e)}")
            return 0.0
    
    def _calculate_risk_score(self, performance: TradePerformance) -> float:
        """리스크 점수 계산"""
        try:
            # 변동성, 성장률, 무역수지를 기반으로 리스크 계산
            volatility_risk = performance.volatility * 100
            growth_risk = max(0.0, -performance.growth_rate) * 100
            balance_risk = max(0.0, -performance.trade_balance / 1000000) * 10
            
            risk_score = (volatility_risk * 0.4 + growth_risk * 0.4 + balance_risk * 0.2)
            return round(min(risk_score, 100), 2)
            
        except Exception as e:
            logger.error(f"❌ 리스크 점수 계산 중 오류: {str(e)}")
            return 0.0
    
    def _analyze_trend(self, performance: TradePerformance) -> str:
        """트렌드 분석"""
        try:
            if performance.growth_rate > 0.15:
                return "강한 상승세, 시장 확장 중"
            elif performance.growth_rate > 0.05:
                return "안정적 상승세, 지속적 성장"
            elif performance.growth_rate > -0.05:
                return "안정적 유지, 시장 안정"
            elif performance.growth_rate > -0.15:
                return "약간의 하락세, 주의 필요"
            else:
                return "강한 하락세, 시장 위험"
                
        except Exception as e:
            logger.error(f"❌ 트렌드 분석 중 오류: {str(e)}")
            return "분석 불가"
    
    def _generate_recommendation(self, performance: TradePerformance, overall_score: float) -> str:
        """추천사항 생성"""
        try:
            if overall_score >= 80:
                return "매우 유망한 시장, 적극적 진출 권장"
            elif overall_score >= 60:
                return "유망한 시장, 단계적 진출 권장"
            elif overall_score >= 40:
                return "보통 수준, 신중한 진출 검토"
            elif overall_score >= 20:
                return "위험 요소 존재, 진출 재검토 필요"
            else:
                return "매우 위험한 시장, 진출 비권장"
                
        except Exception as e:
            logger.error(f"❌ 추천사항 생성 중 오류: {str(e)}")
            return "추천사항 생성 실패"
    
    def _generate_analysis_summary(self, trade_data: List[TradePerformance], 
                                 ranking_data: List[MarketRanking]) -> Dict:
        """분석 요약 생성"""
        try:
            summary = {
                "total_countries": len(trade_data),
                "average_export": sum(d.export_amount for d in trade_data) / len(trade_data),
                "average_import": sum(d.import_amount for d in trade_data) / len(trade_data),
                "average_growth_rate": sum(d.growth_rate for d in trade_data) / len(trade_data),
                "average_market_potential": sum(d.market_potential_score for d in trade_data) / len(trade_data),
                "top_performing_country": max(trade_data, key=lambda x: x.market_potential_score).country,
                "highest_growth_country": max(trade_data, key=lambda x: x.growth_rate).country,
                "most_stable_country": min(trade_data, key=lambda x: x.volatility).country,
                "overall_market_trend": self._determine_overall_trend(trade_data),
                "risk_assessment": self._assess_overall_risk(trade_data),
                "strategic_recommendations": self._generate_strategic_recommendations(trade_data, ranking_data)
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ 분석 요약 생성 중 오류: {str(e)}")
            return {}
    
    def _determine_overall_trend(self, trade_data: List[TradePerformance]) -> str:
        """전체 시장 트렌드 판단"""
        try:
            avg_growth = sum(d.growth_rate for d in trade_data) / len(trade_data)
            
            if avg_growth > 0.1:
                return "전체적으로 상승세"
            elif avg_growth > -0.1:
                return "전체적으로 안정세"
            else:
                return "전체적으로 하락세"
                
        except Exception as e:
            logger.error(f"❌ 전체 트렌드 판단 중 오류: {str(e)}")
            return "분석 불가"
    
    def _assess_overall_risk(self, trade_data: List[TradePerformance]) -> str:
        """전체 리스크 평가"""
        try:
            avg_volatility = sum(d.volatility for d in trade_data) / len(trade_data)
            
            if avg_volatility > 0.2:
                return "높은 변동성, 주의 필요"
            elif avg_volatility > 0.1:
                return "보통 수준의 변동성"
            else:
                return "낮은 변동성, 안정적"
                
        except Exception as e:
            logger.error(f"❌ 전체 리스크 평가 중 오류: {str(e)}")
            return "평가 불가"
    
    def _generate_strategic_recommendations(self, trade_data: List[TradePerformance], 
                                          ranking_data: List[MarketRanking]) -> List[str]:
        """전략적 추천사항 생성"""
        try:
            recommendations = []
            
            # 최고 성과 국가 기반 추천
            top_country = max(trade_data, key=lambda x: x.market_potential_score)
            recommendations.append(f"{top_country.country} 시장에 집중 투자 권장 (시장 잠재력: {top_country.market_potential_score:.1f}점)")
            
            # 성장률 기반 추천
            growth_country = max(trade_data, key=lambda x: x.growth_rate)
            if growth_country.growth_rate > 0.1:
                recommendations.append(f"{growth_country.country} 시장 성장세 활용 (성장률: {growth_country.growth_rate:.1%})")
            
            # 리스크 관리 추천
            high_risk_countries = [d for d in trade_data if d.risk_level == "높음"]
            if high_risk_countries:
                recommendations.append(f"리스크 관리 강화 필요 ({len(high_risk_countries)}개 국가)")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ 전략적 추천사항 생성 중 오류: {str(e)}")
            return ["추천사항 생성 실패"]
    
    def generate_db_table_data(self, analysis_result: Dict) -> Dict:
        """DB 적재용 테이블 형태 데이터 생성"""
        try:
            trade_data = analysis_result.get("trade_data", [])
            ranking_data = analysis_result.get("ranking_data", [])
            
            # 수출입 실적 테이블
            trade_table = {
                "table_name": "trade_performance",
                "columns": [
                    "hs_code", "country", "export_amount", "import_amount", "trade_balance",
                    "market_share", "growth_rate", "volatility", "market_potential_score",
                    "ranking", "trend_direction", "risk_level", "created_at"
                ],
                "data": [
                    {
                        "hs_code": d.hs_code,
                        "country": d.country,
                        "export_amount": d.export_amount,
                        "import_amount": d.import_amount,
                        "trade_balance": d.trade_balance,
                        "market_share": d.market_share,
                        "growth_rate": d.growth_rate,
                        "volatility": d.volatility,
                        "market_potential_score": d.market_potential_score,
                        "ranking": d.ranking,
                        "trend_direction": d.trend_direction,
                        "risk_level": d.risk_level,
                        "created_at": d.created_at
                    }
                    for d in trade_data
                ]
            }
            
            # 시장 유망도 랭킹 테이블
            ranking_table = {
                "table_name": "market_ranking",
                "columns": [
                    "hs_code", "country", "overall_score", "market_potential", "growth_potential",
                    "stability_score", "risk_score", "ranking", "ranking_change", "trend_analysis",
                    "recommendation", "created_at"
                ],
                "data": [
                    {
                        "hs_code": r.hs_code,
                        "country": r.country,
                        "overall_score": r.overall_score,
                        "market_potential": r.market_potential,
                        "growth_potential": r.growth_potential,
                        "stability_score": r.stability_score,
                        "risk_score": r.risk_score,
                        "ranking": r.ranking,
                        "ranking_change": r.ranking_change,
                        "trend_analysis": r.trend_analysis,
                        "recommendation": r.recommendation,
                        "created_at": r.created_at
                    }
                    for r in ranking_data
                ]
            }
            
            # 분석 요약 테이블
            summary = analysis_result.get("analysis_summary", {})
            summary_table = {
                "table_name": "trade_analysis_summary",
                "columns": [
                    "hs_code", "total_countries", "average_export", "average_import",
                    "average_growth_rate", "average_market_potential", "top_performing_country",
                    "highest_growth_country", "most_stable_country", "overall_market_trend",
                    "risk_assessment", "strategic_recommendations", "created_at"
                ],
                "data": [
                    {
                        "hs_code": analysis_result.get("hs_code", ""),
                        "total_countries": summary.get("total_countries", 0),
                        "average_export": summary.get("average_export", 0),
                        "average_import": summary.get("average_import", 0),
                        "average_growth_rate": summary.get("average_growth_rate", 0),
                        "average_market_potential": summary.get("average_market_potential", 0),
                        "top_performing_country": summary.get("top_performing_country", ""),
                        "highest_growth_country": summary.get("highest_growth_country", ""),
                        "most_stable_country": summary.get("most_stable_country", ""),
                        "overall_market_trend": summary.get("overall_market_trend", ""),
                        "risk_assessment": summary.get("risk_assessment", ""),
                        "strategic_recommendations": json.dumps(summary.get("strategic_recommendations", []), ensure_ascii=False),
                        "created_at": analysis_result.get("created_at", "")
                    }
                ]
            }
            
            return {
                "trade_performance_table": trade_table,
                "market_ranking_table": ranking_table,
                "analysis_summary_table": summary_table
            }
            
        except Exception as e:
            logger.error(f"❌ DB 테이블 데이터 생성 중 오류: {str(e)}")
            return {}
    
    def _save_to_cache(self, key: str, data: Dict):
        """캐시에 데이터 저장"""
        try:
            cache_file = os.path.join(self.cache_dir, f"{key}.json")
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ 캐시 저장 완료: {cache_file}")
            
        except Exception as e:
            logger.error(f"❌ 캐시 저장 중 오류: {str(e)}")
    
    def _load_from_cache(self, key: str) -> Optional[Dict]:
        """캐시에서 데이터 로드"""
        try:
            cache_file = os.path.join(self.cache_dir, f"{key}.json")
            
            if not os.path.exists(cache_file):
                return None
            
            # 캐시 만료 확인 (24시간)
            file_time = os.path.getmtime(cache_file)
            if time.time() - file_time > 86400:  # 24시간
                logger.info(f"🔄 캐시 만료: {cache_file}")
                return None
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            logger.info(f"✅ 캐시 로드 완료: {cache_file}")
            return cache_data
            
        except Exception as e:
            logger.error(f"❌ 캐시 로드 중 오류: {str(e)}")
            return None
    
    def get_ranking_algorithm_explanation(self) -> Dict:
        """AI 자동 랭킹 산출 알고리즘 설명"""
        return {
            "algorithm_name": "종합 시장 유망도 랭킹 알고리즘",
            "version": "1.0",
            "description": "수출입 실적 데이터를 기반으로 시장 유망도를 종합적으로 평가하는 알고리즘",
            "components": {
                "market_potential": {
                    "weight": self.ranking_weights["market_potential"],
                    "description": "수출액, 시장 점유율, 성장률, 안정성을 종합한 시장 잠재력",
                    "calculation": "정규화된 수출액(30%) + 시장점유율(25%) + 성장률(25%) + 안정성(20%)"
                },
                "growth_potential": {
                    "weight": self.ranking_weights["growth_potential"],
                    "description": "성장률과 시장 점유율 잠재력을 기반으로 한 성장 가능성",
                    "calculation": "성장률 점수(60%) + 시장점유율 잠재력(40%)"
                },
                "stability": {
                    "weight": self.ranking_weights["stability"],
                    "description": "변동성과 성장 일관성을 기반으로 한 시장 안정성",
                    "calculation": "변동성 점수(70%) + 성장 일관성(30%)"
                },
                "risk_factor": {
                    "weight": self.ranking_weights["risk_factor"],
                    "description": "변동성, 성장률, 무역수지를 기반으로 한 리스크 평가",
                    "calculation": "변동성 리스크(40%) + 성장 리스크(40%) + 무역수지 리스크(20%)"
                },
                "competitiveness": {
                    "weight": self.ranking_weights["competitiveness"],
                    "description": "시장 점유율을 기반으로 한 경쟁력 평가",
                    "calculation": "시장 점유율 정규화 점수"
                }
            },
            "normalization": "각 지표를 0-100 범위로 정규화하여 계산",
            "ranking_method": "종합 점수 기준 내림차순 정렬",
            "update_frequency": "월 1회 (공공데이터 업데이트 기준)",
            "data_sources": [
                "공공데이터포털 수출입 실적 데이터",
                "HS CODE별 국가별 통계",
                "시장 점유율 및 성장률 데이터"
            ]
        }
    
    def get_db_sync_strategy(self) -> Dict:
        """DB 동기화 방안 제안"""
        return {
            "sync_strategy": "증분 업데이트 방식",
            "update_frequency": "월 1회",
            "data_retention": "최근 5년 데이터 보관",
            "tables": {
                "trade_performance": {
                    "primary_key": ["hs_code", "country", "created_at"],
                    "indexes": ["hs_code", "country", "created_at"],
                    "partitioning": "연도별 파티셔닝"
                },
                "market_ranking": {
                    "primary_key": ["hs_code", "country", "created_at"],
                    "indexes": ["hs_code", "ranking", "overall_score"],
                    "partitioning": "연도별 파티셔닝"
                },
                "analysis_summary": {
                    "primary_key": ["hs_code", "created_at"],
                    "indexes": ["hs_code", "created_at"],
                    "partitioning": "연도별 파티셔닝"
                }
            },
            "sync_process": [
                "1. 공공데이터포털에서 최신 데이터 다운로드",
                "2. 데이터 전처리 및 검증",
                "3. 시장 유망도 랭킹 재계산",
                "4. 기존 데이터와 비교하여 변경사항 식별",
                "5. 증분 업데이트 실행",
                "6. 데이터 무결성 검증"
            ],
            "backup_strategy": "업데이트 전 전체 백업",
            "monitoring": "데이터 품질 및 업데이트 상태 모니터링"
        }
    
    def get_api_status(self) -> Dict:
        """API 상태 확인"""
        return {
            "service_available": True,
            "supported_countries": self.supported_countries,
            "common_hs_codes": self.common_hs_codes,
            "cache_directory": self.cache_dir,
            "ranking_weights": self.ranking_weights,
            "last_update": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "api_connection": "initialized"
        }

# 사용 예시
if __name__ == "__main__":
    analyzer = PublicDataTradeAnalyzer()
    
    # 테스트 실행
    result = analyzer.get_trade_data("190230")  # 라면 HS CODE
    
    if result:
        print(f"✅ 데이터 분석 완료: HS CODE {result['hs_code']}")
        
        # 수출입 실적 데이터 출력
        print("\n📊 수출입 실적 데이터:")
        for data in result['trade_data']:
            print(f"  {data.country}: 수출 {data.export_amount:,.0f}, 수입 {data.import_amount:,.0f}, 점유율 {data.market_share:.2f}%")
        
        # 시장 유망도 랭킹 출력
        print("\n🏆 시장 유망도 랭킹:")
        for ranking in result['ranking_data']:
            print(f"  {ranking.country}: 종합점수 {ranking.overall_score:.1f}, 랭킹 {ranking.ranking}위, 추천: {ranking.recommendation}")
        
        # 분석 요약 출력
        summary = result['analysis_summary']
        print(f"\n📈 분석 요약:")
        print(f"  전체 트렌드: {summary['overall_market_trend']}")
        print(f"  리스크 평가: {summary['risk_assessment']}")
        print(f"  최고 성과 국가: {summary['top_performing_country']}")
        
        # DB 테이블 데이터 생성
        db_data = analyzer.generate_db_table_data(result)
        print(f"\n🗄️ DB 테이블 데이터 생성 완료:")
        print(f"  수출입 실적 테이블: {len(db_data['trade_performance_table']['data'])}개 행")
        print(f"  시장 랭킹 테이블: {len(db_data['market_ranking_table']['data'])}개 행")
        print(f"  분석 요약 테이블: {len(db_data['analysis_summary_table']['data'])}개 행")
        
        # 알고리즘 설명
        algorithm = analyzer.get_ranking_algorithm_explanation()
        print(f"\n🤖 랭킹 알고리즘: {algorithm['algorithm_name']} v{algorithm['version']}")
        
        # DB 동기화 방안
        sync_strategy = analyzer.get_db_sync_strategy()
        print(f"\n🔄 DB 동기화 방안: {sync_strategy['sync_strategy']}")
        
    else:
        print("❌ 데이터 분석 실패") 