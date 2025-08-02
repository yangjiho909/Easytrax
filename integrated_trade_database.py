#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
통합 무역 데이터베이스 시스템
모든 무역 관련 데이터(규제, 통계, 시장분석, 전략보고서)를 통합하여
자연어 질의로 답변할 수 있는 시스템
"""

import json
import sqlite3
import logging
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
import re
import pandas as pd
from collections import defaultdict

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AI 자연어 처리기 import
try:
    from ai_natural_language_processor import FreeAINaturalLanguageProcessor, AIProcessedQuery
    AI_PROCESSOR_AVAILABLE = True
    logger.info("✅ AI 자연어 처리기 import 성공")
except ImportError:
    AI_PROCESSOR_AVAILABLE = False
    logger.warning("⚠️ AI 자연어 처리기 import 실패 - 기본 규칙 기반 처리 사용")

@dataclass
class QueryResult:
    """질의 결과"""
    answer: str
    data_sources: List[str]
    confidence_score: float
    suggested_followup: List[str]
    visualizations: List[Dict[str, Any]]
    timestamp: str

@dataclass
class DataSource:
    """데이터 소스 정보"""
    source_name: str
    data_type: str
    last_updated: str
    reliability_score: float
    description: str

class IntegratedTradeDatabase:
    """통합 무역 데이터베이스"""
    
    def __init__(self, db_path: str = "integrated_trade.db"):
        self.db_path = db_path
        self.init_database()
        
        # AI 자연어 처리기 초기화
        if AI_PROCESSOR_AVAILABLE:
            try:
                self.ai_processor = FreeAINaturalLanguageProcessor()
                logger.info("✅ AI 자연어 처리기 초기화 완료")
            except Exception as e:
                logger.error(f"❌ AI 자연어 처리기 초기화 실패: {e}")
                self.ai_processor = None
        else:
            self.ai_processor = None
        
        # 데이터 소스별 신뢰도 점수
        self.reliability_scores = {
            "KOTRA_API": 0.95,
            "KOTRA_BIGDATA": 0.90,
            "KOTRA_EXCEL_DATA": 0.88,  # KOTRA 엑셀 데이터 추가
            "PUBLIC_DATA_PORTAL": 0.85,
            "REAL_TIME_CRAWLER": 0.80,
            "MVP_DATA": 0.70,
            "MARKET_ENTRY_PARSER": 0.75
        }
        
        # 질의 패턴 정의
        self.query_patterns = {
            "regulation": [
                r"규제|규정|인증|허가|승인|검사|기준|표준",
                r"서류|문서|증명서|허가증|인증서",
                r"필요|요구|준수|의무"
            ],
            "trade_statistics": [
                r"통계|수치|데이터|금액|수량|비율",
                r"수출|수입|무역|거래|교역",
                r"HS코드|품목|상품|제품"
            ],
            "market_analysis": [
                r"시장|동향|트렌드|전망|예측",
                r"경쟁|수요|공급|가격|성장",
                r"유망|기회|잠재력|성장률"
            ],
            "risk_assessment": [
                r"리스크|위험|불확실성|변동성",
                r"문제|이슈|장벽|제약|어려움",
                r"도전|과제|복잡성"
            ],
            "strategy": [
                r"전략|대응|해결|개선|강화",
                r"방안|방법|접근|절차|단계",
                r"권장|제안|필요|중요"
            ]
        }

    def init_database(self):
        """데이터베이스 초기화 및 테이블 생성"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 규제 정보 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS regulations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        country TEXT NOT NULL,
                        product TEXT NOT NULL,
                        category TEXT NOT NULL,
                        title TEXT NOT NULL,
                        description TEXT,
                        requirements TEXT,
                        source TEXT NOT NULL,
                        last_updated TEXT,
                        reliability_score REAL DEFAULT 0.8,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 무역 통계 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS trade_statistics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        country TEXT NOT NULL,
                        hs_code TEXT,
                        product TEXT,
                        period TEXT NOT NULL,
                        export_amount REAL,
                        import_amount REAL,
                        trade_balance REAL,
                        growth_rate REAL,
                        market_share REAL,
                        source TEXT NOT NULL,
                        data_date TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # KOTRA 엑셀 데이터 테이블 (글로벌 무역현황)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS kotra_global_trade (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        country TEXT NOT NULL,
                        hs_code TEXT,
                        product_name TEXT,
                        export_amount REAL,
                        import_amount REAL,
                        trade_balance REAL,
                        growth_rate REAL,
                        market_share REAL,
                        period TEXT,
                        source TEXT DEFAULT 'KOTRA_EXCEL_DATA',
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # KOTRA 엑셀 데이터 테이블 (해외유망시장추천)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS kotra_market_recommendation (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        country TEXT NOT NULL,
                        hs_code TEXT,
                        product_name TEXT,
                        recommendation_score REAL,
                        market_potential REAL,
                        growth_potential REAL,
                        risk_level TEXT,
                        recommendation_reason TEXT,
                        period TEXT,
                        source TEXT DEFAULT 'KOTRA_EXCEL_DATA',
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 시장 분석 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS market_analysis (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        country TEXT NOT NULL,
                        product TEXT NOT NULL,
                        analysis_type TEXT NOT NULL,
                        title TEXT NOT NULL,
                        content TEXT,
                        trend_type TEXT,
                        period TEXT,
                        data_support TEXT,
                        source TEXT NOT NULL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 전략 보고서 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS strategy_reports (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        report_id TEXT UNIQUE NOT NULL,
                        country TEXT NOT NULL,
                        product TEXT NOT NULL,
                        title TEXT NOT NULL,
                        executive_summary TEXT,
                        key_issues_count INTEGER,
                        market_trends_count INTEGER,
                        customs_documents_count INTEGER,
                        response_strategies_count INTEGER,
                        risk_keywords TEXT,
                        market_size TEXT,
                        growth_rate TEXT,
                        regulatory_complexity TEXT,
                        risk_assessment TEXT,
                        source TEXT NOT NULL,
                        report_date TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 질의 로그 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS query_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        query_text TEXT NOT NULL,
                        query_type TEXT,
                        answer TEXT,
                        data_sources TEXT,
                        confidence_score REAL,
                        response_time REAL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 인덱스 생성
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_regulations_country_product ON regulations(country, product)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_trade_stats_country_hs ON trade_statistics(country, hs_code)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_market_analysis_country_product ON market_analysis(country, product)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_strategy_reports_country_product ON strategy_reports(country, product)')
                
                conn.commit()
                logger.info("✅ 통합 무역 데이터베이스 초기화 완료")
                
        except Exception as e:
            logger.error(f"❌ 데이터베이스 초기화 실패: {e}")

    def insert_regulation_data(self, regulation_data: Dict[str, Any]):
        """규제 데이터 삽입"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO regulations 
                    (country, product, category, title, description, requirements, source, last_updated, reliability_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    regulation_data.get('country'),
                    regulation_data.get('product'),
                    regulation_data.get('category'),
                    regulation_data.get('title'),
                    regulation_data.get('description'),
                    regulation_data.get('requirements'),
                    regulation_data.get('source'),
                    regulation_data.get('last_updated'),
                    self.reliability_scores.get(regulation_data.get('source'), 0.7)
                ))
                
                conn.commit()
                logger.info(f"✅ 규제 데이터 삽입 완료: {regulation_data.get('title')}")
                
        except Exception as e:
            logger.error(f"❌ 규제 데이터 삽입 실패: {e}")

    def insert_trade_statistics(self, trade_data: Dict[str, Any]):
        """무역 통계 데이터 삽입"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO trade_statistics 
                    (country, hs_code, product, period, export_amount, import_amount, trade_balance, growth_rate, market_share, source, data_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    trade_data.get('country'),
                    trade_data.get('hs_code'),
                    trade_data.get('product'),
                    trade_data.get('period'),
                    trade_data.get('export_amount'),
                    trade_data.get('import_amount'),
                    trade_data.get('trade_balance'),
                    trade_data.get('growth_rate'),
                    trade_data.get('market_share'),
                    trade_data.get('source'),
                    trade_data.get('data_date')
                ))
                
                conn.commit()
                logger.info(f"✅ 무역 통계 데이터 삽입 완료: {trade_data.get('country')} {trade_data.get('product')}")
                
        except Exception as e:
            logger.error(f"❌ 무역 통계 데이터 삽입 실패: {e}")

    def insert_market_analysis(self, market_data: Dict[str, Any]):
        """시장 분석 데이터 삽입"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO market_analysis 
                    (country, product, analysis_type, title, content, trend_type, period, data_support, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    market_data.get('country'),
                    market_data.get('product'),
                    market_data.get('analysis_type'),
                    market_data.get('title'),
                    market_data.get('content'),
                    market_data.get('trend_type'),
                    market_data.get('period'),
                    market_data.get('data_support'),
                    market_data.get('source')
                ))
                
                conn.commit()
                logger.info(f"✅ 시장 분석 데이터 삽입 완료: {market_data.get('title')}")
                
        except Exception as e:
            logger.error(f"❌ 시장 분석 데이터 삽입 실패: {e}")

    def insert_strategy_report(self, report_data: Dict[str, Any]):
        """전략 보고서 데이터 삽입"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO strategy_reports 
                    (report_id, country, product, title, executive_summary, key_issues_count, market_trends_count, 
                     customs_documents_count, response_strategies_count, risk_keywords, market_size, growth_rate, 
                     regulatory_complexity, risk_assessment, source, report_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    report_data.get('report_id'),
                    report_data.get('country'),
                    report_data.get('product'),
                    report_data.get('title'),
                    report_data.get('executive_summary'),
                    report_data.get('key_issues_count'),
                    report_data.get('market_trends_count'),
                    report_data.get('customs_documents_count'),
                    report_data.get('response_strategies_count'),
                    report_data.get('risk_keywords'),
                    report_data.get('market_size'),
                    report_data.get('growth_rate'),
                    report_data.get('regulatory_complexity'),
                    report_data.get('risk_assessment'),
                    report_data.get('source'),
                    report_data.get('report_date')
                ))
                
                conn.commit()
                logger.info(f"✅ 전략 보고서 데이터 삽입 완료: {report_data.get('title')}")
                
        except Exception as e:
            logger.error(f"❌ 전략 보고서 데이터 삽입 실패: {e}")

    def insert_kotra_excel_data(self, excel_data: Dict[str, Any]):
        """KOTRA 엑셀 데이터 삽입"""
        try:
            source = excel_data.get('source', 'KOTRA_EXCEL_DATA')
            
            if source == "글로벌 무역현황":
                self._insert_kotra_global_trade_data(excel_data)
            elif source == "해외유망시장추천":
                self._insert_kotra_market_recommendation_data(excel_data)
            else:
                logger.warning(f"⚠️ 알 수 없는 KOTRA 엑셀 데이터 소스: {source}")
                
        except Exception as e:
            logger.error(f"❌ KOTRA 엑셀 데이터 삽입 실패: {e}")
            raise
    
    def _insert_kotra_global_trade_data(self, excel_data: Dict[str, Any]):
        """글로벌 무역현황 데이터 삽입"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                data_list = excel_data.get('data', [])
                inserted_count = 0
                
                for item in data_list:
                    cursor.execute('''
                        INSERT INTO kotra_global_trade (
                            country, hs_code, product_name, export_amount,
                            import_amount, trade_balance, growth_rate,
                            market_share, period, source
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        item.get('country'),
                        item.get('hs_code'),
                        item.get('product_name'),
                        item.get('export_amount', 0.0),
                        item.get('import_amount', 0.0),
                        item.get('trade_balance', 0.0),
                        item.get('growth_rate', 0.0),
                        item.get('market_share', 0.0),
                        item.get('period'),
                        'KOTRA_EXCEL_DATA'
                    ))
                    inserted_count += 1
                
                conn.commit()
                logger.info(f"✅ 글로벌 무역현황 데이터 삽입 완료: {inserted_count}개 레코드")
                
        except Exception as e:
            logger.error(f"❌ 글로벌 무역현황 데이터 삽입 실패: {e}")
            raise
    
    def _insert_kotra_market_recommendation_data(self, excel_data: Dict[str, Any]):
        """해외유망시장추천 데이터 삽입"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                data_list = excel_data.get('data', [])
                inserted_count = 0
                
                for item in data_list:
                    cursor.execute('''
                        INSERT INTO kotra_market_recommendation (
                            country, hs_code, product_name, recommendation_score,
                            market_potential, growth_potential, risk_level,
                            recommendation_reason, period, source
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        item.get('country'),
                        item.get('hs_code'),
                        item.get('product_name'),
                        item.get('recommendation_score', 0.0),
                        item.get('market_potential', 0.0),
                        item.get('growth_potential', 0.0),
                        item.get('risk_level'),
                        item.get('recommendation_reason'),
                        item.get('period'),
                        'KOTRA_EXCEL_DATA'
                    ))
                    inserted_count += 1
                
                conn.commit()
                logger.info(f"✅ 해외유망시장추천 데이터 삽입 완료: {inserted_count}개 레코드")
                
        except Exception as e:
            logger.error(f"❌ 해외유망시장추천 데이터 삽입 실패: {e}")
            raise

    def natural_language_query(self, query: str) -> QueryResult:
        """자연어 질의 처리 (AI 강화)"""
        start_time = datetime.now()
        
        try:
            # 1. AI 자연어 처리 (가능한 경우)
            if self.ai_processor:
                try:
                    ai_processed = self.ai_processor.process_query(query)
                    logger.info(f"🤖 AI 처리 결과 - 의도: {ai_processed.intent}, 신뢰도: {ai_processed.confidence:.2f}")
                    
                    # AI 처리된 정보 활용
                    query_type = ai_processed.intent
                    entities = ai_processed.entities
                    country = entities.get('country', [''])[0] if entities.get('country') else ''
                    product = entities.get('product', [''])[0] if entities.get('product') else ''
                    hs_code = entities.get('hs_code', [''])[0] if entities.get('hs_code') else ''
                    
                    # AI가 향상시킨 질의 사용
                    enhanced_query = ai_processed.processed_query
                    
                except Exception as e:
                    logger.warning(f"AI 처리 실패, 기본 처리 사용: {e}")
                    query_type = self._analyze_query_type(query)
                    country, product, hs_code = self._extract_entities(query)
                    enhanced_query = query
            else:
                # 기본 처리
                query_type = self._analyze_query_type(query)
                country, product, hs_code = self._extract_entities(query)
                enhanced_query = query
            
            # 2. 데이터 검색
            results = self._search_data(query_type, country, product, hs_code, enhanced_query)
            
            # 3. AI를 통한 자연스러운 답변 생성
            if self.ai_processor and results:
                try:
                    answer = self.ai_processor.generate_natural_response(query, results)
                    logger.info("🤖 AI 생성 답변 사용")
                except Exception as e:
                    logger.warning(f"AI 답변 생성 실패, 기본 답변 사용: {e}")
                    answer = self._generate_answer(query, results, query_type)
            else:
                answer = self._generate_answer(query, results, query_type)
            
            # 4. 데이터 소스 수집
            data_sources = self._collect_data_sources(results)
            
            # 5. 신뢰도 점수 계산 (AI 처리 결과 반영)
            if self.ai_processor and hasattr(self.ai_processor, 'ai_processed'):
                confidence_score = max(
                    self._calculate_confidence_score(results),
                    getattr(self.ai_processor, 'ai_processed', AIProcessedQuery('', '', '', {}, 0.5, '')).confidence
                )
            else:
                confidence_score = self._calculate_confidence_score(results)
            
            # 6. 후속 질문 생성
            suggested_followup = self._generate_followup_questions(query, results)
            
            # 7. 시각화 제안
            visualizations = self._suggest_visualizations(query_type, results)
            
            # 8. 응답 시간 계산
            response_time = (datetime.now() - start_time).total_seconds()
            
            # 9. 질의 로그 저장
            self._log_query(query, query_type, answer, data_sources, confidence_score, response_time)
            
            return QueryResult(
                answer=answer,
                data_sources=data_sources,
                confidence_score=confidence_score,
                suggested_followup=suggested_followup,
                visualizations=visualizations,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"❌ 자연어 질의 처리 실패: {e}")
            return QueryResult(
                answer="죄송합니다. 질의 처리 중 오류가 발생했습니다.",
                data_sources=[],
                confidence_score=0.0,
                suggested_followup=["다른 방식으로 질문해 주세요."],
                visualizations=[],
                timestamp=datetime.now().isoformat()
            )

    def _analyze_query_type(self, query: str) -> str:
        """질의 타입 분석"""
        query_lower = query.lower()
        
        for query_type, patterns in self.query_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return query_type
        
        return "general"

    def _extract_entities(self, query: str) -> Tuple[str, str, str]:
        """국가, 품목, HS코드 추출"""
        country = None
        product = None
        hs_code = None
        
        # 국가 추출
        if "중국" in query or "china" in query.lower():
            country = "중국"
        elif "미국" in query or "usa" in query.lower() or "미국" in query:
            country = "미국"
        
        # HS코드 추출
        hs_pattern = r'HS코드\s*(\d{4,8})|(\d{4,8})\s*HS코드'
        hs_match = re.search(hs_pattern, query)
        if hs_match:
            hs_code = hs_match.group(1) or hs_match.group(2)
        
        # 품목 추출 (간단한 패턴 매칭)
        product_keywords = ["라면", "마스크", "전자제품", "의류", "식품", "화학제품"]
        for keyword in product_keywords:
            if keyword in query:
                product = keyword
                break
        
        return country, product, hs_code

    def _search_data(self, query_type: str, country: str, product: str, hs_code: str, query: str) -> Dict[str, Any]:
        """데이터 검색"""
        results = {
            "regulations": [],
            "trade_statistics": [],
            "market_analysis": [],
            "strategy_reports": [],
            "kotra_global_trade": [],
            "kotra_market_recommendation": []
        }
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 규제 정보 검색
                if query_type in ["regulation", "general"]:
                    regulation_query = '''
                        SELECT * FROM regulations 
                        WHERE (country = ? OR ? IS NULL)
                        AND (product = ? OR ? IS NULL)
                        ORDER BY reliability_score DESC, last_updated DESC
                        LIMIT 10
                    '''
                    cursor.execute(regulation_query, (country, country, product, product))
                    results["regulations"] = cursor.fetchall()
                
                # 무역 통계 검색
                if query_type in ["trade_statistics", "general"]:
                    trade_query = '''
                        SELECT * FROM trade_statistics 
                        WHERE (country = ? OR ? IS NULL)
                        AND (hs_code = ? OR ? IS NULL)
                        AND (product = ? OR ? IS NULL)
                        ORDER BY data_date DESC
                        LIMIT 10
                    '''
                    cursor.execute(trade_query, (country, country, hs_code, hs_code, product, product))
                    results["trade_statistics"] = cursor.fetchall()
                
                # 시장 분석 검색
                if query_type in ["market_analysis", "general"]:
                    market_query = '''
                        SELECT * FROM market_analysis 
                        WHERE (country = ? OR ? IS NULL)
                        AND (product = ? OR ? IS NULL)
                        ORDER BY created_at DESC
                        LIMIT 10
                    '''
                    cursor.execute(market_query, (country, country, product, product))
                    results["market_analysis"] = cursor.fetchall()
                
                # 전략 보고서 검색
                if query_type in ["strategy", "general"]:
                    strategy_query = '''
                        SELECT * FROM strategy_reports 
                        WHERE (country = ? OR ? IS NULL)
                        AND (product = ? OR ? IS NULL)
                        ORDER BY report_date DESC
                        LIMIT 5
                    '''
                    cursor.execute(strategy_query, (country, country, product, product))
                    results["strategy_reports"] = cursor.fetchall()
                
                # KOTRA 글로벌 무역현황 검색
                if query_type in ["trade_statistics", "general"]:
                    kotra_global_query = '''
                        SELECT * FROM kotra_global_trade 
                        WHERE (country = ? OR ? IS NULL)
                        AND (hs_code = ? OR ? IS NULL)
                        AND (product_name = ? OR ? IS NULL)
                        ORDER BY created_at DESC
                        LIMIT 10
                    '''
                    cursor.execute(kotra_global_query, (country, country, hs_code, hs_code, product, product))
                    results["kotra_global_trade"] = cursor.fetchall()
                
                # KOTRA 해외유망시장추천 검색
                if query_type in ["market_analysis", "general"]:
                    kotra_recommendation_query = '''
                        SELECT * FROM kotra_market_recommendation 
                        WHERE (country = ? OR ? IS NULL)
                        AND (hs_code = ? OR ? IS NULL)
                        AND (product_name = ? OR ? IS NULL)
                        ORDER BY recommendation_score DESC, created_at DESC
                        LIMIT 10
                    '''
                    cursor.execute(kotra_recommendation_query, (country, country, hs_code, hs_code, product, product))
                    results["kotra_market_recommendation"] = cursor.fetchall()
                
        except Exception as e:
            logger.error(f"❌ 데이터 검색 실패: {e}")
        
        return results

    def _generate_answer(self, query: str, results: Dict[str, Any], query_type: str) -> str:
        """답변 생성"""
        answer_parts = []
        
        # 중복 제거를 위한 set 사용
        seen_regulations = set()
        seen_statistics = set()
        seen_analysis = set()
        seen_reports = set()
        seen_kotra_global = set()
        seen_kotra_recommendation = set()
        
        # 규제 정보 답변
        if results["regulations"]:
            answer_parts.append("📋 **규제 정보**")
            for reg in results["regulations"][:3]:
                reg_key = f"{reg[1]}_{reg[2]}_{reg[4]}"  # country_product_title
                if reg_key not in seen_regulations:
                    seen_regulations.add(reg_key)
                    requirements = reg[5] if reg[5] else "상세 정보는 별도 문의"
                    answer_parts.append(f"• **{reg[1]} {reg[2]}**: {reg[4]}")
                    answer_parts.append(f"  - 필요 서류: {requirements}")
                    answer_parts.append(f"  - 출처: {reg[7]}")
        
        # 무역 통계 답변
        if results["trade_statistics"]:
            answer_parts.append("\n📊 **무역 통계**")
            for stat in results["trade_statistics"][:3]:
                stat_key = f"{stat[0]}_{stat[2]}_{stat[3]}"  # country_product_period
                if stat_key not in seen_statistics:
                    seen_statistics.add(stat_key)
                    answer_parts.append(f"• **{stat[0]} {stat[2]}** ({stat[3]}):")
                    answer_parts.append(f"  - 수출: {stat[5]:,.0f}만원, 수입: {stat[6]:,.0f}만원")
                    answer_parts.append(f"  - 성장률: {stat[8]:.1f}%, 시장점유율: {stat[9]:.1f}%")
                    answer_parts.append(f"  - 출처: {stat[10]}")
        
        # 시장 분석 답변
        if results["market_analysis"]:
            answer_parts.append("\n📈 **시장 동향**")
            for analysis in results["market_analysis"][:2]:
                analysis_key = f"{analysis[0]}_{analysis[1]}_{analysis[4]}"  # country_product_title
                if analysis_key not in seen_analysis:
                    seen_analysis.add(analysis_key)
                    answer_parts.append(f"• **{analysis[0]} {analysis[1]}**: {analysis[4]}")
                    answer_parts.append(f"  - 내용: {analysis[5][:150]}...")
                    answer_parts.append(f"  - 출처: {analysis[8]}")
        
        # 전략 보고서 답변
        if results["strategy_reports"]:
            answer_parts.append("\n📋 **전략 보고서**")
            for report in results["strategy_reports"][:2]:
                report_key = f"{report[1]}_{report[2]}_{report[3]}"  # country_product_title
                if report_key not in seen_reports:
                    seen_reports.add(report_key)
                    answer_parts.append(f"• **{report[1]} {report[2]}**: {report[3]}")
                    answer_parts.append(f"  - 요약: {report[4][:150]}...")
                    answer_parts.append(f"  - 리스크: {report[9]}")
                    answer_parts.append(f"  - 출처: {report[14]}")
        
        # KOTRA 글로벌 무역현황 답변
        if results["kotra_global_trade"]:
            answer_parts.append("\n🌍 **KOTRA 글로벌 무역현황**")
            for trade in results["kotra_global_trade"][:3]:
                trade_key = f"{trade[1]}_{trade[2]}_{trade[3]}"  # country_hs_code_product_name
                if trade_key not in seen_kotra_global:
                    seen_kotra_global.add(trade_key)
                    answer_parts.append(f"• **{trade[1]} {trade[3]}** (HS: {trade[2]}):")
                    answer_parts.append(f"  - 수출: {trade[4]:,.0f}, 수입: {trade[5]:,.0f}")
                    answer_parts.append(f"  - 무역수지: {trade[6]:,.0f}, 성장률: {trade[7]:.1f}%")
                    answer_parts.append(f"  - 시장점유율: {trade[8]:.1f}%")
                    answer_parts.append(f"  - 출처: {trade[10]}")
        
        # KOTRA 해외유망시장추천 답변
        if results["kotra_market_recommendation"]:
            answer_parts.append("\n⭐ **KOTRA 해외유망시장추천**")
            for rec in results["kotra_market_recommendation"][:3]:
                rec_key = f"{rec[1]}_{rec[2]}_{rec[3]}"  # country_hs_code_product_name
                if rec_key not in seen_kotra_recommendation:
                    seen_kotra_recommendation.add(rec_key)
                    answer_parts.append(f"• **{rec[1]} {rec[3]}** (HS: {rec[2]}):")
                    answer_parts.append(f"  - 추천점수: {rec[4]:.1f}, 시장잠재력: {rec[5]:.1f}")
                    answer_parts.append(f"  - 성장잠재력: {rec[6]:.1f}, 리스크: {rec[7]}")
                    answer_parts.append(f"  - 추천이유: {rec[8]}")
                    answer_parts.append(f"  - 출처: {rec[10]}")
        
        if not answer_parts:
            return "해당 정보를 찾을 수 없습니다. 다른 키워드로 검색해 보세요."
        
        return "\n".join(answer_parts)

    def _collect_data_sources(self, results: Dict[str, Any]) -> List[str]:
        """데이터 소스 수집"""
        sources = set()
        
        for reg in results["regulations"]:
            sources.add(reg[7])  # source column
        
        for stat in results["trade_statistics"]:
            sources.add(stat[10])  # source column
        
        for analysis in results["market_analysis"]:
            sources.add(analysis[8])  # source column
        
        for report in results["strategy_reports"]:
            sources.add(report[14])  # source column
        
        # KOTRA 엑셀 데이터 소스 추가
        for trade in results["kotra_global_trade"]:
            sources.add(trade[10])  # source column
        
        for rec in results["kotra_market_recommendation"]:
            sources.add(rec[10])  # source column
        
        return list(sources)

    def _calculate_confidence_score(self, results: Dict[str, Any]) -> float:
        """신뢰도 점수 계산"""
        total_score = 0
        total_weight = 0
        
        # 각 데이터 타입별 가중치
        weights = {
            "regulations": 0.3,
            "trade_statistics": 0.25,
            "market_analysis": 0.25,
            "strategy_reports": 0.2
        }
        
        for data_type, data_list in results.items():
            if data_list:
                weight = weights.get(data_type, 0.1)
                total_weight += weight
                
                # 데이터 소스별 신뢰도 평균
                source_scores = []
                for item in data_list:
                    source = item[7] if data_type == "regulations" else item[10] if data_type == "trade_statistics" else item[8] if data_type == "market_analysis" else item[14]
                    source_scores.append(self.reliability_scores.get(source, 0.7))
                
                avg_score = sum(source_scores) / len(source_scores) if source_scores else 0.7
                total_score += avg_score * weight
        
        return total_score / total_weight if total_weight > 0 else 0.7

    def _generate_followup_questions(self, query: str, results: Dict[str, Any]) -> List[str]:
        """후속 질문 생성"""
        followup = []
        
        if "규제" in query or "서류" in query:
            followup.extend([
                "해당 규제의 최신 변경사항을 확인하시겠습니까?",
                "관련 인증 절차에 대해 더 자세히 알고 싶으신가요?"
            ])
        
        if "통계" in query or "수출" in query or "수입" in query:
            followup.extend([
                "월별/분기별 추이 그래프를 보시겠습니까?",
                "경쟁국과의 비교 분석을 원하시나요?"
            ])
        
        if "시장" in query or "동향" in query:
            followup.extend([
                "향후 시장 전망을 확인하시겠습니까?",
                "관련 리스크 분석을 원하시나요?"
            ])
        
        return followup[:3]

    def _suggest_visualizations(self, query_type: str, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """시각화 제안"""
        visualizations = []
        
        if query_type == "trade_statistics" and results["trade_statistics"]:
            visualizations.append({
                "type": "line_chart",
                "title": "무역 추이 그래프",
                "description": "월별/분기별 수출입 추이를 시각화"
            })
        
        if query_type == "market_analysis" and results["market_analysis"]:
            visualizations.append({
                "type": "bar_chart",
                "title": "시장 동향 분석",
                "description": "주요 시장 지표 비교"
            })
        
        return visualizations

    def _log_query(self, query: str, query_type: str, answer: str, data_sources: List[str], confidence_score: float, response_time: float):
        """질의 로그 저장"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO query_logs 
                    (query_text, query_type, answer, data_sources, confidence_score, response_time)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    query,
                    query_type,
                    answer,
                    json.dumps(data_sources),
                    confidence_score,
                    response_time
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"❌ 질의 로그 저장 실패: {e}")

    def get_database_status(self) -> Dict[str, Any]:
        """데이터베이스 상태 확인"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 각 테이블의 레코드 수 확인
                tables = ["regulations", "trade_statistics", "market_analysis", "strategy_reports", "kotra_global_trade", "kotra_market_recommendation", "query_logs"]
                record_counts = {}
                
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    record_counts[table] = cursor.fetchone()[0]
                
                # 최근 업데이트 확인
                cursor.execute("SELECT MAX(created_at) FROM regulations")
                last_regulation_update = cursor.fetchone()[0]
                
                cursor.execute("SELECT MAX(data_date) FROM trade_statistics")
                last_trade_update = cursor.fetchone()[0]
                
                return {
                    "status": "active",
                    "database_path": self.db_path,
                    "record_counts": record_counts,
                    "regulations_count": record_counts.get("regulations", 0),
                    "trade_statistics_count": record_counts.get("trade_statistics", 0),
                    "market_analysis_count": record_counts.get("market_analysis", 0),
                    "strategy_reports_count": record_counts.get("strategy_reports", 0),
                    "kotra_global_trade_count": record_counts.get("kotra_global_trade", 0),
                    "kotra_market_recommendation_count": record_counts.get("kotra_market_recommendation", 0),
                    "query_logs_count": record_counts.get("query_logs", 0),
                    "last_regulation_update": last_regulation_update,
                    "last_trade_update": last_trade_update,
                    "reliability_scores": self.reliability_scores,
                    "supported_query_types": list(self.query_patterns.keys()),
                    "last_updated": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"❌ 데이터베이스 상태 확인 실패: {e}")
            return {"status": "error", "error": str(e)} 