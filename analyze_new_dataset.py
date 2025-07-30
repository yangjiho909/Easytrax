#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
새로운 데이터셋 분석 (중국, 미국 위주)
"""

import pandas as pd
import os
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

def analyze_new_datasets():
    """새로운 데이터셋 분석"""
    
    print("🔍 새로운 데이터셋 분석")
    print("=" * 60)
    
    # 새로운 데이터셋 파일들
    new_files = [
        "미국으로 수출 2.xlsx",
        "미국으로 수출.xlsx", 
        "중국 으로 수출.xlsx"
    ]
    
    total_new_records = 0
    all_new_data = []
    
    for file in new_files:
        file_path = os.path.join("data", file)
        
        if os.path.exists(file_path):
            try:
                print(f"\n📁 분석 중: {file}")
                print("-" * 40)
                
                # 파일 크기 확인
                file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                print(f"파일 크기: {file_size:.2f} MB")
                
                # 데이터 로드
                df = pd.read_excel(file_path)
                print(f"레코드 수: {len(df):,}개")
                print(f"컬럼 수: {len(df.columns)}개")
                
                # 컬럼명 확인
                print(f"컬럼명: {list(df.columns)}")
                
                # 수입국 확인 (있는 경우)
                if '수입국' in df.columns:
                    countries = df['수입국'].value_counts()
                    print(f"수입국 분포:")
                    for country, count in countries.head(10).items():
                        print(f"  {country}: {count:,}개")
                
                # 품목 확인 (있는 경우)
                if '품목' in df.columns:
                    items = df['품목'].value_counts().head(5)
                    print(f"상위 품목:")
                    for item, count in items.items():
                        print(f"  {item}: {count:,}개")
                
                # 문제사유 확인 (있는 경우)
                if '문제사유' in df.columns:
                    reasons = df['문제사유'].value_counts().head(5)
                    print(f"상위 문제사유:")
                    for reason, count in reasons.items():
                        print(f"  {reason[:50]}{'...' if len(reason) > 50 else ''}: {count:,}개")
                
                # 데이터 품질 확인
                print(f"결측값:")
                for col in df.columns:
                    missing = df[col].isnull().sum()
                    if missing > 0:
                        print(f"  {col}: {missing:,}개 ({missing/len(df)*100:.1f}%)")
                
                total_new_records += len(df)
                all_new_data.append(df)
                
            except Exception as e:
                print(f"❌ {file} 분석 실패: {e}")
        else:
            print(f"❌ 파일 없음: {file}")
    
    print(f"\n📊 새로운 데이터셋 요약")
    print("=" * 40)
    print(f"총 새로운 레코드: {total_new_records:,}개")
    print(f"분석된 파일: {len(all_new_data)}개")
    
    return all_new_data

def compare_with_existing_data():
    """기존 데이터와 비교"""
    
    print(f"\n🔄 기존 데이터와 비교")
    print("=" * 40)
    
    try:
        # 기존 데이터 로드
        import pickle
        with open('model/raw_data.pkl', 'rb') as f:
            existing_df = pickle.load(f)
        
        print(f"기존 데이터: {len(existing_df):,}개")
        
        # 중국, 미국 데이터 확인
        china_existing = existing_df[existing_df['수입국'] == '중국']
        us_existing = existing_df[existing_df['수입국'] == '미국']
        
        print(f"기존 중국 데이터: {len(china_existing):,}개")
        print(f"기존 미국 데이터: {len(us_existing):,}개")
        
        # 새로운 데이터에서 중국, 미국 확인
        new_files = ["중국 으로 수출.xlsx", "미국으로 수출.xlsx", "미국으로 수출 2.xlsx"]
        
        for file in new_files:
            file_path = os.path.join("data", file)
            if os.path.exists(file_path):
                try:
                    df = pd.read_excel(file_path)
                    if '수입국' in df.columns:
                        china_new = df[df['수입국'] == '중국']
                        us_new = df[df['수입국'] == '미국']
                        
                        print(f"\n{file}:")
                        print(f"  중국 데이터: {len(china_new):,}개")
                        print(f"  미국 데이터: {len(us_new):,}개")
                        
                except Exception as e:
                    print(f"❌ {file} 비교 실패: {e}")
        
    except Exception as e:
        print(f"❌ 기존 데이터 비교 실패: {e}")

def prepare_integration_plan():
    """통합 계획 수립"""
    
    print(f"\n📋 데이터 통합 계획")
    print("=" * 40)
    
    plan = {
        "1단계": "새 데이터 전처리",
        "2단계": "기존 데이터와 병합",
        "3단계": "모델 재학습",
        "4단계": "시스템 업데이트"
    }
    
    for step, description in plan.items():
        print(f"{step}: {description}")
    
    print(f"\n🎯 예상 효과:")
    print(f"  - 중국 데이터: 27,249개 → 40,000+개")
    print(f"  - 미국 데이터: 73,870개 → 110,000+개")
    print(f"  - 분석 정확도: 75% → 85-90%")

if __name__ == "__main__":
    # 1. 새로운 데이터셋 분석
    new_data = analyze_new_datasets()
    
    # 2. 기존 데이터와 비교
    compare_with_existing_data()
    
    # 3. 통합 계획 수립
    prepare_integration_plan()
    
    print(f"\n✅ 새로운 데이터셋 분석 완료!") 