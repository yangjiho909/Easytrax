#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pickle
import pandas as pd

def show_available_countries():
    """현재 비교분석 가능한 국가들 표시"""
    print("🌍 KATI 시스템 비교분석 가능한 국가 정보")
    print("=" * 60)
    
    try:
        # 통관 거부사례 데이터 로딩
        with open("model/raw_data.pkl", "rb") as f:
            raw_data = pickle.load(f)
        
        print(f"📊 총 데이터 수: {len(raw_data):,}건")
        print("=" * 60)
        
        # 수입국 정보
        countries = raw_data["수입국"].dropna().unique()
        top_countries = raw_data["수입국"].value_counts().head(15)
        
        print(f"🌍 통관 거부사례 분석 가능한 수입국: {len(countries)}개")
        print("📊 상위 15개 국가 (사례 수):")
        print("-" * 40)
        for i, (country, count) in enumerate(top_countries.items(), 1):
            print(f"{i:2d}. {country:<12} ({count:5d}건)")
        
        if len(countries) > 15:
            print(f"... 외 {len(countries) - 15}개 국가")
        
        # 원산지 정보
        origins = raw_data["원산지"].dropna().unique()
        top_origins = raw_data["원산지"].value_counts().head(10)
        
        print(f"\n🏭 원산지 분석 가능: {len(origins)}개")
        print("📊 상위 10개 원산지:")
        print("-" * 40)
        for i, (origin, count) in enumerate(top_origins.items(), 1):
            print(f"{i:2d}. {origin:<12} ({count:5d}건)")
        
        if len(origins) > 10:
            print(f"... 외 {len(origins) - 10}개 원산지")
        
        # 품목 정보
        items = raw_data["품목"].dropna().unique()
        top_items = raw_data["품목"].value_counts().head(10)
        
        print(f"\n📦 품목 분석 가능: {len(items)}개")
        print("📊 상위 10개 품목:")
        print("-" * 40)
        for i, (item, count) in enumerate(top_items.items(), 1):
            print(f"{i:2d}. {item:<25} ({count:5d}건)")
        
        if len(items) > 10:
            print(f"... 외 {len(items) - 10}개 품목")
        
        print("\n" + "=" * 60)
        print("💡 사용 팁:")
        print("- 제품 설명 입력 시 위 국가/원산지/품목명을 포함하면 더 정확한 분석이 가능합니다.")
        print("- 예시: '한국산 라면을 미국으로 수출하려고 합니다'")
        print("- 예시: '중국산 전자제품을 일본으로 수출하려고 합니다'")
        
    except Exception as e:
        print(f"❌ 데이터 로딩 실패: {e}")

if __name__ == "__main__":
    show_available_countries() 