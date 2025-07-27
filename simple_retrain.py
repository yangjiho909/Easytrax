#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pickle
from glob import glob
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import warnings
warnings.filterwarnings("ignore")

def train_and_save_model(data_dir="data", model_dir="model"):
    print("🧼 통관 실패 데이터 정제 및 모델 재학습...")
    excel_files = glob(os.path.join(data_dir, "*.xlsx"))
    
    if not excel_files:
        print("❌ 엑셀 파일을 찾을 수 없습니다.")
        return
    
    print(f"📁 발견된 엑셀 파일: {len(excel_files)}개")
    all_df = []

    for i, file in enumerate(excel_files):
        print(f"📊 처리 중: {os.path.basename(file)}")
        try:
            df = pd.read_excel(file)
            print(f"   - 행 수: {len(df)}")
            print(f"   - 컬럼: {list(df.columns)}")
            
            # 문제사유 컬럼 찾기
            sa_yu_cols = [col for col in df.columns if "문제사유" in col or "사유" in col]
            if sa_yu_cols:
                df["문제사유"] = df[sa_yu_cols].fillna("").astype(str).agg(" ".join, axis=1)
            else:
                df["문제사유"] = "정보 없음"
            
            # 필요한 컬럼들 확인
            required_cols = ["품목", "원산지", "수입국", "조치사항"]
            available_cols = [col for col in required_cols if col in df.columns]
            
            if len(available_cols) >= 3:  # 최소 3개 컬럼은 있어야 함
                df = df[available_cols + ["문제사유"]].dropna()
                df["출처파일"] = os.path.basename(file)
                all_df.append(df)
                print(f"   ✅ 처리 완료: {len(df)}행")
            else:
                print(f"   ⚠️ 필요한 컬럼 부족. 사용 가능: {available_cols}")
                
        except Exception as e:
            print(f"   ❌ 처리 실패: {e}")

    if not all_df:
        print("❌ 유효한 데이터가 없습니다.")
        return

    full_df = pd.concat(all_df, ignore_index=True)
    print(f"\n✅ 총 {len(full_df)}개의 데이터를 처리했습니다.")
    
    # 한국 관련 데이터 확인
    korean_data = full_df[full_df["원산지"].str.contains("한국|대한민국", na=False)]
    print(f"🇰🇷 한국 원산지 데이터: {len(korean_data)}건 ({len(korean_data)/len(full_df)*100:.1f}%)")
    
    if len(korean_data) > 0:
        print(f"   - 주요 수입국: {list(korean_data['수입국'].value_counts().head(5).index)}")
        print(f"   - 주요 품목: {list(korean_data['품목'].value_counts().head(5).index)}")
    
    # 텍스트 결합
    text_cols = [col for col in ["품목", "원산지", "수입국", "문제사유"] if col in full_df.columns]
    full_df["텍스트"] = full_df[text_cols].astype(str).agg(" ".join, axis=1)

    # TF-IDF 벡터화
    print("🔧 TF-IDF 벡터화 중...")
    vectorizer = TfidfVectorizer(max_features=5000, stop_words=None)
    X = vectorizer.fit_transform(full_df["텍스트"])

    # 모델 저장
    os.makedirs(model_dir, exist_ok=True)
    with open(os.path.join(model_dir, "vectorizer.pkl"), "wb") as f:
        pickle.dump(vectorizer, f)
    with open(os.path.join(model_dir, "indexed_matrix.pkl"), "wb") as f:
        pickle.dump(X, f)
    with open(os.path.join(model_dir, "raw_data.pkl"), "wb") as f:
        pickle.dump(full_df, f)

    print(f"✅ 모델 저장 완료!")
    print(f"📁 저장 위치: {model_dir}/")
    print(f"📊 최종 데이터 수: {len(full_df)}건")

if __name__ == "__main__":
    train_and_save_model() 