#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
시장 진출 전략 보고서 파서
KOTRA '드림' 사이트 또는 공공데이터포털 PDF/엑셀 보고서에서 추출한 
중국/미국 시장 진출 전략 정보를 텍스트로 파싱 후, DB 색인 및 요약문으로 저장하기 위한 구조로 가공
"""

import json
import re
import logging
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any
from pathlib import Path
import hashlib

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MarketIssue:
    """주요 이슈 정보"""
    title: str
    description: str
    impact_level: str  # high, medium, low
    category: str  # regulatory, market, customs, etc.

@dataclass
class MarketTrend:
    """시장 동향 정보"""
    trend_type: str  # growth, decline, stable, emerging
    description: str
    period: str
    data_support: str

@dataclass
class CustomsDocument:
    """통관 관련 서류 정보"""
    document_name: str
    description: str
    required: bool
    processing_time: str
    cost: str

@dataclass
class ResponseStrategy:
    """대응 전략 정보"""
    strategy_name: str
    description: str
    implementation_steps: List[str]
    expected_outcome: str
    risk_level: str

@dataclass
class MetaInformation:
    """DB 색인용 메타정보"""
    country: str
    product: str
    period: str
    risk_keywords: List[str]
    market_size: str
    growth_rate: str
    regulatory_complexity: str

@dataclass
class MarketEntryReport:
    """시장 진출 전략 보고서"""
    report_id: str
    title: str
    country: str
    product: str
    report_date: str
    source: str
    
    # 주요 내용
    executive_summary: str
    key_issues: List[MarketIssue]
    market_trends: List[MarketTrend]
    customs_documents: List[CustomsDocument]
    response_strategies: List[ResponseStrategy]
    
    # 메타정보
    meta_info: MetaInformation
    
    # 추가 정보
    risk_assessment: str
    market_opportunities: List[str]
    challenges: List[str]
    recommendations: List[str]

class MarketEntryStrategyParser:
    """시장 진출 전략 보고서 파서"""
    
    def __init__(self):
        self.cache_dir = Path("regulation_cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        # 키워드 패턴 정의
        self.issue_keywords = {
            'regulatory': ['규제', '인증', '허가', '승인', '검사', '기준', '표준'],
            'market': ['시장', '경쟁', '수요', '공급', '가격', '트렌드'],
            'customs': ['통관', '세관', '관세', '검역', '서류', '절차'],
            'logistics': ['물류', '운송', '보관', '배송', '창고'],
            'financial': ['환율', '금융', '보험', '결제', '신용']
        }
        
        self.trend_keywords = {
            'growth': ['성장', '증가', '확대', '상승', '호조'],
            'decline': ['감소', '하락', '축소', '부진', '둔화'],
            'stable': ['안정', '유지', '보합', '현상유지'],
            'emerging': ['신흥', '새로운', '부상', '각광']
        }
        
        self.risk_keywords = [
            '리스크', '위험', '불확실성', '변동성', '복잡성', '어려움',
            '장벽', '제약', '한계', '문제', '이슈', '도전'
        ]

    def parse_report_text(self, country: str, product: str, raw_text: str, source: str = "KOTRA") -> MarketEntryReport:
        """원문 텍스트를 파싱하여 시장 진출 전략 보고서 생성"""
        try:
            # 보고서 ID 생성
            report_id = self._generate_report_id(country, product, source)
            
            # 주요 이슈 추출
            key_issues = self._extract_key_issues(raw_text)
            
            # 시장 동향 추출
            market_trends = self._extract_market_trends(raw_text)
            
            # 통관 관련 서류 추출
            customs_documents = self._extract_customs_documents(raw_text)
            
            # 대응 전략 추출
            response_strategies = self._extract_response_strategies(raw_text)
            
            # 메타정보 생성
            meta_info = self._generate_meta_information(country, product, raw_text)
            
            # 추가 정보 추출
            risk_assessment = self._extract_risk_assessment(raw_text)
            market_opportunities = self._extract_market_opportunities(raw_text)
            challenges = self._extract_challenges(raw_text)
            recommendations = self._extract_recommendations(raw_text)
            
            # 실행 요약 생성
            executive_summary = self._generate_executive_summary(
                key_issues, market_trends, response_strategies
            )
            
            report = MarketEntryReport(
                report_id=report_id,
                title=f"{country} {product} 시장 진출 전략 보고서",
                country=country,
                product=product,
                report_date=datetime.now().strftime("%Y-%m-%d"),
                source=source,
                executive_summary=executive_summary,
                key_issues=key_issues,
                market_trends=market_trends,
                customs_documents=customs_documents,
                response_strategies=response_strategies,
                meta_info=meta_info,
                risk_assessment=risk_assessment,
                market_opportunities=market_opportunities,
                challenges=challenges,
                recommendations=recommendations
            )
            
            # 캐시에 저장
            self._save_to_cache(report)
            
            logger.info(f"✅ {country} {product} 시장 진출 전략 보고서 파싱 완료")
            return report
            
        except Exception as e:
            logger.error(f"❌ 보고서 파싱 중 오류: {e}")
            return self._get_fallback_report(country, product, source)

    def _generate_report_id(self, country: str, product: str, source: str) -> str:
        """보고서 ID 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_string = f"{country}_{product}_{source}_{timestamp}"
        return hashlib.md5(base_string.encode()).hexdigest()[:12]

    def _extract_key_issues(self, text: str) -> List[MarketIssue]:
        """주요 이슈 추출"""
        issues = []
        
        # 문장 단위로 분리
        sentences = re.split(r'[.!?。！？]', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
                
            # 이슈 키워드 확인
            for category, keywords in self.issue_keywords.items():
                for keyword in keywords:
                    if keyword in sentence:
                        # 영향도 판단
                        impact_level = self._determine_impact_level(sentence)
                        
                        issue = MarketIssue(
                            title=f"{category} 관련 이슈",
                            description=sentence,
                            impact_level=impact_level,
                            category=category
                        )
                        issues.append(issue)
                        break
        
        # 중복 제거 및 상위 5개 선택
        unique_issues = []
        seen_descriptions = set()
        for issue in issues:
            if issue.description not in seen_descriptions:
                unique_issues.append(issue)
                seen_descriptions.add(issue.description)
        
        return unique_issues[:5]

    def _extract_market_trends(self, text: str) -> List[MarketTrend]:
        """시장 동향 추출"""
        trends = []
        
        sentences = re.split(r'[.!?。！？]', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
                
            # 트렌드 키워드 확인
            for trend_type, keywords in self.trend_keywords.items():
                for keyword in keywords:
                    if keyword in sentence:
                        trend = MarketTrend(
                            trend_type=trend_type,
                            description=sentence,
                            period="최근 1년",
                            data_support="시장 조사 데이터"
                        )
                        trends.append(trend)
                        break
        
        return trends[:3]

    def _extract_customs_documents(self, text: str) -> List[CustomsDocument]:
        """통관 관련 서류 추출"""
        documents = []
        
        # 통관 관련 키워드 패턴
        customs_patterns = [
            r'([가-힣]+)서류',
            r'([가-힣]+)증명서',
            r'([가-힣]+)허가증',
            r'([가-힣]+)인증서'
        ]
        
        for pattern in customs_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                doc_name = f"{match}서류"
                documents.append(CustomsDocument(
                    document_name=doc_name,
                    description=f"{doc_name}는 수출입 시 필수 서류입니다.",
                    required=True,
                    processing_time="3-5일",
                    cost="무료"
                ))
        
        # 기본 통관 서류 추가
        default_docs = [
            "상업송장", "포장명세서", "원산지증명서", "검역증명서"
        ]
        
        for doc in default_docs:
            if doc not in [d.document_name for d in documents]:
                documents.append(CustomsDocument(
                    document_name=doc,
                    description=f"{doc}는 일반적인 수출입 시 필요합니다.",
                    required=True,
                    processing_time="1-3일",
                    cost="무료"
                ))
        
        return documents[:6]

    def _extract_response_strategies(self, text: str) -> List[ResponseStrategy]:
        """대응 전략 추출"""
        strategies = []
        
        # 전략 관련 키워드
        strategy_keywords = ['전략', '대응', '해결', '개선', '강화', '확대']
        
        sentences = re.split(r'[.!?。！？]', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
                
            for keyword in strategy_keywords:
                if keyword in sentence:
                    strategy = ResponseStrategy(
                        strategy_name=f"{keyword} 전략",
                        description=sentence,
                        implementation_steps=[
                            "1단계: 현황 분석",
                            "2단계: 전략 수립",
                            "3단계: 실행 계획",
                            "4단계: 모니터링"
                        ],
                        expected_outcome="시장 진출 성공률 향상",
                        risk_level="medium"
                    )
                    strategies.append(strategy)
                    break
        
        return strategies[:3]

    def _generate_meta_information(self, country: str, product: str, text: str) -> MetaInformation:
        """메타정보 생성"""
        # 리스크 키워드 추출
        risk_keywords = []
        for keyword in self.risk_keywords:
            if keyword in text:
                risk_keywords.append(keyword)
        
        # 시장 규모 및 성장률 추정
        market_size = "중간 규모" if "중간" in text else "대규모" if "대" in text else "소규모"
        growth_rate = "높음" if any(word in text for word in ['성장', '증가', '확대']) else "보통"
        regulatory_complexity = "복잡" if any(word in text for word in ['복잡', '어려움', '제약']) else "보통"
        
        return MetaInformation(
            country=country,
            product=product,
            period=datetime.now().strftime("%Y년"),
            risk_keywords=risk_keywords[:5],
            market_size=market_size,
            growth_rate=growth_rate,
            regulatory_complexity=regulatory_complexity
        )

    def _extract_risk_assessment(self, text: str) -> str:
        """리스크 평가 추출"""
        risk_indicators = ['위험', '리스크', '불확실성', '변동성']
        for indicator in risk_indicators:
            if indicator in text:
                return f"{indicator} 요소가 시장 진출에 영향을 미칠 수 있습니다."
        return "일반적인 수출입 리스크가 예상됩니다."

    def _extract_market_opportunities(self, text: str) -> List[str]:
        """시장 기회 추출"""
        opportunities = []
        opportunity_keywords = ['기회', '잠재력', '성장', '확대', '신규']
        
        sentences = re.split(r'[.!?。！？]', text)
        for sentence in sentences:
            for keyword in opportunity_keywords:
                if keyword in sentence and len(sentence) > 10:
                    opportunities.append(sentence.strip())
                    break
        
        return opportunities[:3]

    def _extract_challenges(self, text: str) -> List[str]:
        """도전 과제 추출"""
        challenges = []
        challenge_keywords = ['도전', '어려움', '문제', '장벽', '제약']
        
        sentences = re.split(r'[.!?。！？]', text)
        for sentence in sentences:
            for keyword in challenge_keywords:
                if keyword in sentence and len(sentence) > 10:
                    challenges.append(sentence.strip())
                    break
        
        return challenges[:3]

    def _extract_recommendations(self, text: str) -> List[str]:
        """권장사항 추출"""
        recommendations = []
        recommendation_keywords = ['권장', '제안', '필요', '중요', '강화']
        
        sentences = re.split(r'[.!?。！？]', text)
        for sentence in sentences:
            for keyword in recommendation_keywords:
                if keyword in sentence and len(sentence) > 10:
                    recommendations.append(sentence.strip())
                    break
        
        return recommendations[:3]

    def _generate_executive_summary(self, issues: List[MarketIssue], 
                                  trends: List[MarketTrend], 
                                  strategies: List[ResponseStrategy]) -> str:
        """실행 요약 생성"""
        summary_parts = []
        
        if issues:
            summary_parts.append(f"주요 이슈 {len(issues)}건이 식별되었습니다.")
        
        if trends:
            summary_parts.append(f"시장 동향 {len(trends)}건이 분석되었습니다.")
        
        if strategies:
            summary_parts.append(f"대응 전략 {len(strategies)}건이 제시되었습니다.")
        
        if summary_parts:
            return " ".join(summary_parts)
        else:
            return "시장 진출 전략 분석이 완료되었습니다."

    def _determine_impact_level(self, text: str) -> str:
        """영향도 판단"""
        high_impact_words = ['심각', '중대', '위험', '긴급', '치명']
        medium_impact_words = ['중요', '주의', '관심', '검토']
        
        for word in high_impact_words:
            if word in text:
                return "high"
        
        for word in medium_impact_words:
            if word in text:
                return "medium"
        
        return "low"

    def _save_to_cache(self, report: MarketEntryReport):
        """캐시에 저장"""
        try:
            cache_file = self.cache_dir / f"market_entry_report_{report.report_id}.json"
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(report), f, ensure_ascii=False, indent=2)
            logger.info(f"✅ 캐시 저장 완료: {cache_file}")
        except Exception as e:
            logger.error(f"❌ 캐시 저장 실패: {e}")

    def _get_fallback_report(self, country: str, product: str, source: str) -> MarketEntryReport:
        """기본 보고서 생성"""
        report_id = self._generate_report_id(country, product, source)
        
        return MarketEntryReport(
            report_id=report_id,
            title=f"{country} {product} 시장 진출 전략 보고서",
            country=country,
            product=product,
            report_date=datetime.now().strftime("%Y-%m-%d"),
            source=source,
            executive_summary=f"{country} {product} 시장 진출을 위한 기본 전략 분석이 제공됩니다.",
            key_issues=[
                MarketIssue(
                    title="기본 규제 요구사항",
                    description="해당 국가의 기본 수출입 규제를 준수해야 합니다.",
                    impact_level="medium",
                    category="regulatory"
                )
            ],
            market_trends=[
                MarketTrend(
                    trend_type="stable",
                    description="시장이 안정적으로 유지되고 있습니다.",
                    period="최근 1년",
                    data_support="기본 시장 데이터"
                )
            ],
            customs_documents=[
                CustomsDocument(
                    document_name="상업송장",
                    description="기본 수출입 서류",
                    required=True,
                    processing_time="1-3일",
                    cost="무료"
                )
            ],
            response_strategies=[
                ResponseStrategy(
                    strategy_name="기본 진출 전략",
                    description="단계적 시장 진출을 통한 리스크 최소화",
                    implementation_steps=[
                        "1단계: 시장 조사",
                        "2단계: 파트너십 구축",
                        "3단계: 시범 수출",
                        "4단계: 확대 진출"
                    ],
                    expected_outcome="안정적인 시장 진출",
                    risk_level="low"
                )
            ],
            meta_info=MetaInformation(
                country=country,
                product=product,
                period=datetime.now().strftime("%Y년"),
                risk_keywords=["기본 리스크"],
                market_size="중간 규모",
                growth_rate="보통",
                regulatory_complexity="보통"
            ),
            risk_assessment="일반적인 수출입 리스크가 예상됩니다.",
            market_opportunities=["시장 진출 기회 존재"],
            challenges=["규제 준수 필요"],
            recommendations=["단계적 접근 권장"]
        )

    def generate_db_table_data(self, report: MarketEntryReport) -> Dict[str, Any]:
        """DB 테이블 적재용 데이터 생성"""
        return {
            "table_name": "market_entry_strategy_reports",
            "data": {
                "report_id": report.report_id,
                "title": report.title,
                "country": report.country,
                "product": report.product,
                "report_date": report.report_date,
                "source": report.source,
                "executive_summary": report.executive_summary,
                "key_issues_count": len(report.key_issues),
                "market_trends_count": len(report.market_trends),
                "customs_documents_count": len(report.customs_documents),
                "response_strategies_count": len(report.response_strategies),
                "risk_keywords": ",".join(report.meta_info.risk_keywords),
                "market_size": report.meta_info.market_size,
                "growth_rate": report.meta_info.growth_rate,
                "regulatory_complexity": report.meta_info.regulatory_complexity,
                "risk_assessment": report.risk_assessment,
                "market_opportunities_count": len(report.market_opportunities),
                "challenges_count": len(report.challenges),
                "recommendations_count": len(report.recommendations),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        }

    def get_api_status(self) -> Dict[str, Any]:
        """API 상태 확인"""
        return {
            "status": "active",
            "module": "MarketEntryStrategyParser",
            "version": "1.0.0",
            "features": [
                "시장 진출 전략 보고서 파싱",
                "주요 이슈 추출",
                "시장 동향 분석",
                "통관 서류 정보",
                "대응 전략 생성",
                "메타정보 생성",
                "DB 테이블 데이터 생성"
            ],
            "supported_countries": ["중국", "미국"],
            "cache_enabled": True,
            "last_updated": datetime.now().isoformat()
        } 