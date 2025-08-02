#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
엑셀 파일 구조 분석기
"""

import pandas as pd
import os

def analyze_excel_structure():
    """엑셀 파일 구조 분석"""
    
    data_dir = "data"
    
    print("🔍 엑셀 파일 구조 분석")
    print("=" * 60)
    
    # data 폴더의 엑셀 파일들 찾기
    excel_files = []
    for file in os.listdir(data_dir):
        if file.endswith('.xlsx') or file.endswith('.xls'):
            excel_files.append(file)
    
    for excel_file in excel_files:
        print(f"\n📊 파일: {excel_file}")
        print("-" * 40)
        
        try:
            filepath = os.path.join(data_dir, excel_file)
            
            # 엑셀 파일 읽기 (헤더 없이)
            df = pd.read_excel(filepath, header=None)
            
            print(f"📏 크기: {len(df)}행 x {len(df.columns)}열")
            
            # 처음 10행 출력
            print(f"\n📋 처음 10행 데이터:")
            print(df.head(10).to_string())
            
            # 컬럼별 고유값 확인
            print(f"\n🔍 각 컬럼별 고유값 (처음 5개):")
            for i, col in enumerate(df.columns):
                unique_values = df[col].dropna().unique()[:5]
                print(f"   컬럼 {i}: {list(unique_values)}")
            
            # 중국, 미국 관련 데이터 찾기
            print(f"\n🇨🇳🇺🇸 중국, 미국 관련 데이터:")
            for i, col in enumerate(df.columns):
                for j, value in enumerate(df[col]):
                    if pd.notna(value):
                        value_str = str(value).lower()
                        if any(keyword in value_str for keyword in ['중국', 'china', '미국', 'usa', 'united states']):
                            print(f"   행 {j}, 컬럼 {i}: {value}")
            
        except Exception as e:
            print(f"❌ 파일 분석 중 오류: {e}")

if __name__ == "__main__":
    analyze_excel_structure() 