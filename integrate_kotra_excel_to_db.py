#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KOTRA 엑셀 데이터를 통합 무역 데이터베이스에 삽입하는 스크립트
"""

import json
import os
import glob
from datetime import datetime
from integrated_trade_database import IntegratedTradeDatabase

def integrate_kotra_excel_data():
    """KOTRA 엑셀 데이터를 DB에 통합"""
    
    print("🚀 KOTRA 엑셀 데이터 DB 통합 시작")
    print("=" * 60)
    
    try:
        # 통합 데이터베이스 초기화
        db = IntegratedTradeDatabase()
        print("✅ 통합 데이터베이스 초기화 완료")
        
        # regulation_cache 폴더에서 KOTRA 엑셀 데이터 JSON 파일들 찾기
        cache_dir = "regulation_cache"
        kotra_files = []
        
        # 글로벌 무역현황 파일들
        global_trade_files = glob.glob(os.path.join(cache_dir, "kotra_global_trade_data_*.json"))
        kotra_files.extend(global_trade_files)
        
        # 해외유망시장추천 파일들
        market_recommendation_files = glob.glob(os.path.join(cache_dir, "kotra_market_recommendation_data_*.json"))
        kotra_files.extend(market_recommendation_files)
        
        print(f"🔍 발견된 KOTRA 엑셀 데이터 파일: {len(kotra_files)}개")
        
        total_inserted = 0
        
        for file_path in kotra_files:
            try:
                print(f"\n📁 파일 처리 중: {os.path.basename(file_path)}")
                
                # JSON 파일 읽기
                with open(file_path, 'r', encoding='utf-8') as f:
                    excel_data = json.load(f)
                
                # 데이터베이스에 삽입
                db.insert_kotra_excel_data(excel_data)
                
                total_inserted += excel_data.get('total_records', 0)
                print(f"✅ 삽입 완료: {excel_data.get('total_records', 0)}개 레코드")
                
            except Exception as e:
                print(f"❌ 파일 처리 실패: {os.path.basename(file_path)} - {e}")
                continue
        
        print(f"\n📊 통합 완료 요약:")
        print(f"   - 처리된 파일: {len(kotra_files)}개")
        print(f"   - 총 삽입된 레코드: {total_inserted}개")
        
        # 데이터베이스 상태 확인
        status = db.get_database_status()
        print(f"\n📈 데이터베이스 상태:")
        print(f"   - 총 규제정보: {status.get('regulations_count', 0)}개")
        print(f"   - 총 무역통계: {status.get('trade_statistics_count', 0)}개")
        print(f"   - 총 시장분석: {status.get('market_analysis_count', 0)}개")
        print(f"   - 총 전략보고서: {status.get('strategy_reports_count', 0)}개")
        print(f"   - 총 KOTRA 글로벌무역: {status.get('kotra_global_trade_count', 0)}개")
        print(f"   - 총 KOTRA 시장추천: {status.get('kotra_market_recommendation_count', 0)}개")
        
        print(f"\n🎉 KOTRA 엑셀 데이터 DB 통합 완료!")
        
        # 테스트 질의 실행
        print(f"\n🧪 테스트 질의 실행:")
        test_queries = [
            "중국 무역 현황 알려줘",
            "미국 시장 추천 정보 보여줘",
            "중국 미국 무역 통계 비교"
        ]
        
        for query in test_queries:
            print(f"\n❓ 질의: {query}")
            result = db.natural_language_query(query)
            print(f"📝 답변: {result.answer[:200]}...")
            print(f"📊 신뢰도: {result.confidence_score:.2f}")
            print(f"🔗 데이터소스: {', '.join(result.data_sources)}")
        
    except Exception as e:
        print(f"❌ KOTRA 엑셀 데이터 통합 실패: {e}")
        raise

if __name__ == "__main__":
    integrate_kotra_excel_data() 