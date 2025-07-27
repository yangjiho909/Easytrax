#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import os
from glob import glob

def check_data_structure():
    print("🔍 데이터 파일 구조 확인 중...")
    
    # 엑셀 파일들 찾기
    excel_files = glob("data/*.xlsx")
    print(f"📁 발견된 엑셀 파일: {len(excel_files)}개")
    
    for i, file in enumerate(excel_files):
        print(f"\n📊 파일 {i+1}: {os.path.basename(file)}")
        try:
            df = pd.read_excel(file)
            print(f"   - 행 수: {len(df)}")
            print(f"   - 컬럼: {list(df.columns)}")
            print(f"   - 샘플 데이터:")
            print(df.head(1).to_string())
        except Exception as e:
            print(f"   ❌ 읽기 실패: {e}")

if __name__ == "__main__":
    check_data_structure() 