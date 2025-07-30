#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
중국, 미국 데이터 상세 분석 및 추가 데이터 필요성 평가
"""

import pandas as pd
import pickle
import os
from collections import Counter

def analyze_china_us_data():
    """중국, 미국 데이터 상세 분석"""
    
    print("🔍 중국, 미국 데이터 상세 분석")
    print("=" * 60)
    
    try:
        with open('model/raw_data.pkl', 'rb') as f:
            df = pickle.load(f)
        
        # 중국, 미국 데이터 분리
        china_data = df[df['수입국'] == '중국']
        us_data = df[df['수입국'] == '미국']
        
        print(f"📊 현재 데이터 현황:")
        print(f"  전체 데이터: {len(df):,}개")
        print(f"  중국 데이터: {len(china_data):,}개 ({len(china_data)/len(df)*100:.1f}%)")
        print(f"  미국 데이터: {len(us_data):,}개 ({len(us_data)/len(df)*100:.1f}%)")
        print(f"  중국+미국: {len(china_data) + len(us_data):,}개 ({(len(china_data) + len(us_data))/len(df)*100:.1f}%)")
        
        # 1. 품목별 분석
        print(f"\n🏷️ 품목별 분석 (상위 10개)")
        print("-" * 40)
        
        # 중국 품목별
        china_items = china_data['품목'].value_counts().head(10)
        print(f"🇨🇳 중국 상위 품목:")
        for i, (item, count) in enumerate(china_items.items(), 1):
            print(f"  {i:2d}. {item}: {count:,}개")
        
        # 미국 품목별
        us_items = us_data['품목'].value_counts().head(10)
        print(f"\n🇺🇸 미국 상위 품목:")
        for i, (item, count) in enumerate(us_items.items(), 1):
            print(f"  {i:2d}. {item}: {count:,}개")
        
        # 2. 문제사유별 분석
        print(f"\n⚠️ 문제사유별 분석 (상위 10개)")
        print("-" * 40)
        
        # 중국 문제사유
        china_reasons = china_data['문제사유'].value_counts().head(10)
        print(f"🇨🇳 중국 주요 문제사유:")
        for i, (reason, count) in enumerate(china_reasons.items(), 1):
            print(f"  {i:2d}. {reason[:50]}{'...' if len(reason) > 50 else ''}: {count:,}개")
        
        # 미국 문제사유
        us_reasons = us_data['문제사유'].value_counts().head(10)
        print(f"\n🇺🇸 미국 주요 문제사유:")
        for i, (reason, count) in enumerate(us_reasons.items(), 1):
            print(f"  {i:2d}. {reason[:50]}{'...' if len(reason) > 50 else ''}: {count:,}개")
        
        # 3. HS 코드별 분석
        print(f"\n📋 HS 코드별 분석 (상위 10개)")
        print("-" * 40)
        
        # 중국 HS 코드
        china_hs = china_data['HS CODE'].value_counts().head(10)
        print(f"🇨🇳 중국 상위 HS 코드:")
        for i, (hs, count) in enumerate(china_hs.items(), 1):
            print(f"  {i:2d}. {hs}: {count:,}개")
        
        # 미국 HS 코드
        us_hs = us_data['HS CODE'].value_counts().head(10)
        print(f"\n🇺🇸 미국 상위 HS 코드:")
        for i, (hs, count) in enumerate(us_hs.items(), 1):
            print(f"  {i:2d}. {hs}: {count:,}개")
        
        # 4. 조치사항별 분석
        print(f"\n🔧 조치사항별 분석")
        print("-" * 40)
        
        # 중국 조치사항
        china_actions = china_data['조치사항'].value_counts()
        print(f"🇨🇳 중국 조치사항:")
        for action, count in china_actions.items():
            print(f"  {action}: {count:,}개")
        
        # 미국 조치사항
        us_actions = us_data['조치사항'].value_counts()
        print(f"\n🇺🇸 미국 조치사항:")
        for action, count in us_actions.items():
            print(f"  {action}: {count:,}개")
        
        # 5. 데이터 품질 평가
        print(f"\n📈 데이터 품질 평가")
        print("-" * 40)
        
        # 문제사유 길이 분석
        china_reason_lengths = china_data['문제사유'].str.len()
        us_reason_lengths = us_data['문제사유'].str.len()
        
        print(f"🇨🇳 중국 문제사유:")
        print(f"  평균 길이: {china_reason_lengths.mean():.1f}자")
        print(f"  최대 길이: {china_reason_lengths.max()}자")
        print(f"  최소 길이: {china_reason_lengths.min()}자")
        
        print(f"\n🇺🇸 미국 문제사유:")
        print(f"  평균 길이: {us_reason_lengths.mean():.1f}자")
        print(f"  최대 길이: {us_reason_lengths.max()}자")
        print(f"  최소 길이: {us_reason_lengths.min()}자")
        
        # 6. 추가 데이터 필요성 평가
        print(f"\n🎯 추가 데이터 필요성 평가")
        print("-" * 40)
        
        # 현재 데이터의 다양성 평가
        china_unique_items = china_data['품목'].nunique()
        us_unique_items = us_data['품목'].nunique()
        
        print(f"🇨🇳 중국 품목 다양성: {china_unique_items}개 고유 품목")
        print(f"🇺🇸 미국 품목 다양성: {us_unique_items}개 고유 품목")
        
        # 데이터 밀도 계산 (품목당 평균 사례 수)
        china_density = len(china_data) / china_unique_items
        us_density = len(us_data) / us_unique_items
        
        print(f"🇨🇳 중국 데이터 밀도: 품목당 {china_density:.1f}개 사례")
        print(f"🇺🇸 미국 데이터 밀도: 품목당 {us_density:.1f}개 사례")
        
        # 권장 추가 데이터량
        print(f"\n📊 권장 추가 데이터량:")
        print(f"  중국: 현재 {len(china_data):,}개 → 목표 {len(china_data)*1.5:,.0f}개 (+{len(china_data)*0.5:,.0f}개)")
        print(f"  미국: 현재 {len(us_data):,}개 → 목표 {len(us_data)*1.5:,.0f}개 (+{len(us_data)*0.5:,.0f}개)")
        
        # 7. 우선순위 제안
        print(f"\n🚀 우선순위 제안")
        print("-" * 40)
        
        # 중국에서 부족한 품목 찾기
        all_items = df['품목'].value_counts()
        china_items_set = set(china_data['품목'].unique())
        
        missing_in_china = []
        for item, count in all_items.head(20).items():
            if item not in china_items_set:
                missing_in_china.append((item, count))
        
        print(f"🇨🇳 중국에 부족한 주요 품목 (상위 10개):")
        for i, (item, count) in enumerate(missing_in_china[:10], 1):
            print(f"  {i:2d}. {item}: 전체 {count:,}개")
        
        # 미국에서 부족한 품목 찾기
        us_items_set = set(us_data['품목'].unique())
        
        missing_in_us = []
        for item, count in all_items.head(20).items():
            if item not in us_items_set:
                missing_in_us.append((item, count))
        
        print(f"\n🇺🇸 미국에 부족한 주요 품목 (상위 10개):")
        for i, (item, count) in enumerate(missing_in_us[:10], 1):
            print(f"  {i:2d}. {item}: 전체 {count:,}개")
        
    except Exception as e:
        print(f"❌ 데이터 분석 실패: {e}")

def suggest_data_sources():
    """추가 데이터 소스 제안"""
    
    print(f"\n📚 추가 데이터 소스 제안")
    print("=" * 60)
    
    sources = [
        {
            "name": "관세청 통관정보포털",
            "url": "https://unipass.customs.go.kr",
            "description": "실시간 통관 거부사례 데이터",
            "priority": "높음"
        },
        {
            "name": "식품의약품안전처",
            "url": "https://www.mfds.go.kr",
            "description": "식품 관련 통관 거부사례",
            "priority": "높음"
        },
        {
            "name": "농림축산식품부",
            "url": "https://www.mafra.go.kr",
            "description": "농축산물 관련 통관 거부사례",
            "priority": "중간"
        },
        {
            "name": "해양수산부",
            "url": "https://www.mof.go.kr",
            "description": "수산물 관련 통관 거부사례",
            "priority": "중간"
        },
        {
            "name": "공공데이터포털",
            "url": "https://www.data.go.kr",
            "description": "정부 공개 데이터",
            "priority": "높음"
        }
    ]
    
    for i, source in enumerate(sources, 1):
        print(f"{i}. {source['name']} ({source['priority']} 우선순위)")
        print(f"   URL: {source['url']}")
        print(f"   설명: {source['description']}")
        print()

if __name__ == "__main__":
    analyze_china_us_data()
    suggest_data_sources() 