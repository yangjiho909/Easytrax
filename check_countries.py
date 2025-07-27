#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pickle
import pandas as pd
from collections import Counter

def check_available_countries():
    print("🌍 조사 가능한 국가 확인 중...")
    
    try:
        # 모델 로딩
        with open("model/raw_data.pkl", "rb") as f:
            raw_data = pickle.load(f)
        
        print(f"📊 총 데이터 수: {len(raw_data)}")
        print(f"📋 사용 가능한 컬럼: {list(raw_data.columns)}")
        
        # 수입국 확인
        if "수입국" in raw_data.columns:
            countries = raw_data["수입국"].dropna()
            country_counts = Counter(countries)
            
            print(f"\n🌍 조사 가능한 수입국 ({len(country_counts)}개):")
            print("=" * 50)
            
            # 상위 20개 국가 출력
            for i, (country, count) in enumerate(country_counts.most_common(20), 1):
                print(f"{i:2d}. {country:<15} ({count:4d}건)")
            
            if len(country_counts) > 20:
                print(f"... 외 {len(country_counts) - 20}개 국가")
        
        # 원산지 확인
        if "원산지" in raw_data.columns:
            origins = raw_data["원산지"].dropna()
            origin_counts = Counter(origins)
            
            print(f"\n🏭 조사 가능한 원산지 ({len(origin_counts)}개):")
            print("=" * 50)
            
            # 상위 20개 원산지 출력
            for i, (origin, count) in enumerate(origin_counts.most_common(20), 1):
                print(f"{i:2d}. {origin:<15} ({count:4d}건)")
            
            if len(origin_counts) > 20:
                print(f"... 외 {len(origin_counts) - 20}개 원산지")
        
        # 품목 확인
        if "품목" in raw_data.columns:
            items = raw_data["품목"].dropna()
            item_counts = Counter(items)
            
            print(f"\n📦 주요 품목 분류 ({len(item_counts)}개):")
            print("=" * 50)
            
            # 상위 15개 품목 출력
            for i, (item, count) in enumerate(item_counts.most_common(15), 1):
                print(f"{i:2d}. {item:<20} ({count:4d}건)")
            
            if len(item_counts) > 15:
                print(f"... 외 {len(item_counts) - 15}개 품목")
        
        return True
        
    except Exception as e:
        print(f"❌ 데이터 확인 실패: {e}")
        return False

if __name__ == "__main__":
    check_available_countries() 