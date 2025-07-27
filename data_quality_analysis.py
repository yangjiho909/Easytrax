#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pickle
import pandas as pd
import numpy as np
from collections import Counter

def analyze_data_quality():
    """데이터 품질 및 목적 적합성 분석"""
    print("🔍 KATI 데이터 품질 및 목적 적합성 분석")
    print("=" * 70)
    
    try:
        # 데이터 로딩
        with open("model/raw_data.pkl", "rb") as f:
            raw_data = pickle.load(f)
        
        print(f"📊 총 데이터 수: {len(raw_data):,}건")
        print("=" * 70)
        
        # 1. 기본 데이터 구조 분석
        print("📋 1. 데이터 구조 분석")
        print("-" * 40)
        print(f"컬럼 수: {len(raw_data.columns)}")
        print(f"컬럼명: {list(raw_data.columns)}")
        
        # 2. 결측값 분석
        print(f"\n📋 2. 결측값 분석")
        print("-" * 40)
        for col in raw_data.columns:
            missing = raw_data[col].isnull().sum()
            missing_pct = (missing / len(raw_data)) * 100
            print(f"{col:<15}: {missing:>6}건 ({missing_pct:>5.1f}%)")
        
        # 3. 핵심 컬럼별 상세 분석
        print(f"\n📋 3. 핵심 컬럼별 상세 분석")
        print("-" * 40)
        
        # 수입국 분석
        if "수입국" in raw_data.columns:
            countries = raw_data["수입국"].dropna()
            print(f"🌍 수입국:")
            print(f"   - 고유값: {countries.nunique()}개")
            print(f"   - 상위 5개: {list(countries.value_counts().head().index)}")
            print(f"   - 한국 관련: {len(countries[countries.str.contains('한국|대한민국', na=False)])}건")
        
        # 원산지 분석
        if "원산지" in raw_data.columns:
            origins = raw_data["원산지"].dropna()
            print(f"\n🏭 원산지:")
            print(f"   - 고유값: {origins.nunique()}개")
            print(f"   - 상위 5개: {list(origins.value_counts().head().index)}")
            print(f"   - 한국 관련: {len(origins[origins.str.contains('한국|대한민국', na=False)])}건")
        
        # 품목 분석
        if "품목" in raw_data.columns:
            items = raw_data["품목"].dropna()
            print(f"\n📦 품목:")
            print(f"   - 고유값: {items.nunique()}개")
            print(f"   - 상위 5개: {list(items.value_counts().head().index)}")
            
            # 한국 수출 관련 품목 찾기
            korean_export_keywords = ["라면", "김치", "소주", "전자", "자동차", "반도체", "화장품"]
            korean_items = []
            for keyword in korean_export_keywords:
                count = len(items[items.str.contains(keyword, na=False)])
                if count > 0:
                    korean_items.append(f"{keyword}({count}건)")
            print(f"   - 한국 수출 관련: {', '.join(korean_items)}")
        
        # 조치사항 분석
        if "조치사항" in raw_data.columns:
            actions = raw_data["조치사항"].dropna()
            print(f"\n🛠️ 조치사항:")
            print(f"   - 고유값: {actions.nunique()}개")
            print(f"   - 상위 5개: {list(actions.value_counts().head().index)}")
        
        # 문제사유 분석
        if "문제사항" in raw_data.columns:
            reasons = raw_data["문제사유"].dropna()
            print(f"\n❌ 문제사유:")
            print(f"   - 고유값: {reasons.nunique()}개")
            print(f"   - 평균 길이: {reasons.str.len().mean():.1f}자")
            
            # 주요 문제 키워드 분석
            problem_keywords = ["서류", "인증", "라벨", "표시", "성분", "검역", "해충", "농약", "방사능"]
            for keyword in problem_keywords:
                count = len(reasons[reasons.str.contains(keyword, na=False)])
                if count > 0:
                    print(f"   - '{keyword}' 관련: {count}건")
        
        # 4. 한국 수출 관점에서의 데이터 적합성
        print(f"\n📋 4. 한국 수출 관점에서의 데이터 적합성")
        print("-" * 40)
        
        # 한국에서 수출하는 경우 (한국이 원산지인 경우)
        korean_origin = raw_data[raw_data["원산지"].str.contains("한국|대한민국", na=False)]
        print(f"🇰🇷 한국 원산지 데이터: {len(korean_origin)}건 ({len(korean_origin)/len(raw_data)*100:.1f}%)")
        
        if len(korean_origin) > 0:
            print(f"   - 주요 수입국: {list(korean_origin['수입국'].value_counts().head(5).index)}")
            print(f"   - 주요 품목: {list(korean_origin['품목'].value_counts().head(5).index)}")
        
        # 한국으로 수입하는 경우 (한국이 수입국인 경우)
        korean_import = raw_data[raw_data["수입국"].str.contains("한국|대한민국", na=False)]
        print(f"📥 한국 수입국 데이터: {len(korean_import)}건 ({len(korean_import)/len(raw_data)*100:.1f}%)")
        
        # 5. 데이터 품질 평가
        print(f"\n📋 5. 데이터 품질 평가")
        print("-" * 40)
        
        # 완성도 점수 계산
        completeness_scores = []
        for col in ["품목", "원산지", "수입국", "조치사항", "문제사유"]:
            if col in raw_data.columns:
                score = (len(raw_data) - raw_data[col].isnull().sum()) / len(raw_data)
                completeness_scores.append(score)
                print(f"   {col:<12}: {score:.1%}")
        
        avg_completeness = np.mean(completeness_scores) if completeness_scores else 0
        print(f"   평균 완성도: {avg_completeness:.1%}")
        
        # 6. 목적 적합성 평가
        print(f"\n📋 6. 목적 적합성 평가")
        print("-" * 40)
        
        # 한국 수출 지원 관점에서의 평가
        korean_export_relevance = len(korean_origin) / len(raw_data) * 100
        print(f"🇰🇷 한국 수출 관련성: {korean_export_relevance:.1f}%")
        
        if korean_export_relevance > 50:
            print("   ✅ 한국 수출 지원에 매우 적합한 데이터")
        elif korean_export_relevance > 20:
            print("   ⚠️ 한국 수출 지원에 부분적으로 적합한 데이터")
        else:
            print("   ❌ 한국 수출 지원에 부적합한 데이터")
        
        # 데이터 다양성 평가
        country_diversity = raw_data["수입국"].nunique() if "수입국" in raw_data.columns else 0
        item_diversity = raw_data["품목"].nunique() if "품목" in raw_data.columns else 0
        
        print(f"🌍 국가 다양성: {country_diversity}개 국가")
        print(f"📦 품목 다양성: {item_diversity}개 품목")
        
        # 7. 개선 제안
        print(f"\n📋 7. 개선 제안")
        print("-" * 40)
        
        if korean_export_relevance < 20:
            print("💡 한국 수출 관련 데이터가 부족합니다.")
            print("   - 한국 원산지 데이터 수집 필요")
            print("   - 한국 수출 실패 사례 추가 필요")
        
        if avg_completeness < 0.8:
            print("💡 데이터 완성도가 낮습니다.")
            print("   - 결측값 보완 필요")
            print("   - 데이터 정제 작업 필요")
        
        if country_diversity < 10:
            print("💡 국가 다양성이 부족합니다.")
            print("   - 더 많은 수출대상국 데이터 필요")
        
        print(f"\n🎯 종합 평가:")
        if korean_export_relevance > 30 and avg_completeness > 0.7 and country_diversity > 20:
            print("✅ 한국 수출 지원 목적에 적합한 데이터")
        elif korean_export_relevance > 10 and avg_completeness > 0.5:
            print("⚠️ 부분적으로 적합하나 개선 필요")
        else:
            print("❌ 목적에 부적합한 데이터")
        
    except Exception as e:
        print(f"❌ 데이터 분석 실패: {e}")

if __name__ == "__main__":
    analyze_data_quality() 