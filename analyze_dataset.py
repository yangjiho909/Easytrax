#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
전체 데이터셋 분석
"""

import pandas as pd
import pickle
import os

def analyze_dataset():
    """전체 데이터셋 분석"""
    
    print("🔍 전체 데이터셋 분석")
    print("=" * 50)
    
    # 1. 모델 데이터 분석
    print("\n📊 모델 데이터 분석 (model/raw_data.pkl)")
    print("-" * 40)
    
    try:
        with open('model/raw_data.pkl', 'rb') as f:
            df = pickle.load(f)
        
        print(f"전체 데이터 수: {len(df):,}개")
        print(f"총 수입국 수: {df['수입국'].nunique()}개")
        
        # 수입국별 데이터 분포
        country_counts = df['수입국'].value_counts()
        print(f"\n📈 상위 20개 수입국:")
        for i, (country, count) in enumerate(country_counts.head(20).items(), 1):
            print(f"  {i:2d}. {country}: {count:,}개")
        
        # 중국, 미국 데이터 확인
        china_us_data = df[df['수입국'].isin(['중국', '미국'])]
        print(f"\n🇨🇳🇺🇸 중국, 미국 데이터:")
        print(f"  중국: {len(df[df['수입국'] == '중국']):,}개")
        print(f"  미국: {len(df[df['수입국'] == '미국']):,}개")
        print(f"  합계: {len(china_us_data):,}개")
        
        # 중국, 미국 데이터 비율
        total_ratio = len(china_us_data) / len(df) * 100
        print(f"  전체 대비 비율: {total_ratio:.1f}%")
        
    except Exception as e:
        print(f"❌ 모델 데이터 로드 실패: {e}")
    
    # 2. 원본 Excel 파일 분석
    print(f"\n📁 원본 Excel 파일 분석")
    print("-" * 40)
    
    data_dir = "data"
    excel_files = [f for f in os.listdir(data_dir) if f.startswith('customsExcel') and f.endswith('.xlsx')]
    
    print(f"발견된 Excel 파일: {len(excel_files)}개")
    
    all_countries = set()
    total_records = 0
    
    for file in excel_files:
        try:
            file_path = os.path.join(data_dir, file)
            df_excel = pd.read_excel(file_path)
            
            if '수입국' in df_excel.columns:
                countries = df_excel['수입국'].dropna().unique()
                all_countries.update(countries)
                total_records += len(df_excel)
                
                print(f"  {file}: {len(df_excel):,}개 레코드, {len(countries)}개 국가")
                
        except Exception as e:
            print(f"  ❌ {file} 로드 실패: {e}")
    
    print(f"\n📊 전체 국가 목록 ({len(all_countries)}개):")
    sorted_countries = sorted(all_countries)
    for i, country in enumerate(sorted_countries, 1):
        print(f"  {i:2d}. {country}")
    
    # 3. 중국, 미국 외 주요 국가들
    print(f"\n🌍 중국, 미국 외 주요 국가들:")
    major_countries = ['러시아', '일본', '베트남', '태국', '인도네시아', '말레이시아', '필리핀', '싱가포르']
    
    for country in major_countries:
        if country in all_countries:
            print(f"  ✅ {country}: 포함됨")
        else:
            print(f"  ❌ {country}: 없음")
    
    # 4. 데이터 품질 분석
    print(f"\n🔍 데이터 품질 분석")
    print("-" * 40)
    
    try:
        with open('model/raw_data.pkl', 'rb') as f:
            df = pickle.load(f)
        
        # 컬럼별 결측값 확인
        print("컬럼별 결측값:")
        for col in df.columns:
            missing = df[col].isnull().sum()
            if missing > 0:
                print(f"  {col}: {missing:,}개 ({missing/len(df)*100:.1f}%)")
        
        # 문제사유 길이 분석
        if '문제사유' in df.columns:
            reason_lengths = df['문제사유'].str.len()
            print(f"\n문제사유 길이 분석:")
            print(f"  평균 길이: {reason_lengths.mean():.1f}자")
            print(f"  최대 길이: {reason_lengths.max()}자")
            print(f"  최소 길이: {reason_lengths.min()}자")
            
            # 빈 문제사유 확인
            empty_reasons = (df['문제사유'].str.strip() == '').sum()
            print(f"  빈 문제사유: {empty_reasons:,}개 ({empty_reasons/len(df)*100:.1f}%)")
        
    except Exception as e:
        print(f"❌ 데이터 품질 분석 실패: {e}")

if __name__ == "__main__":
    analyze_dataset() 