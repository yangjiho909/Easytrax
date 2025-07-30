#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
새로운 데이터셋 통합 (중국, 미국 위주)
"""

import pandas as pd
import pickle
import os
import warnings
from glob import glob
from soynlp.tokenizer import RegexTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")
warnings.filterwarnings("ignore", category=FutureWarning, module="soynlp")

def integrate_new_data():
    """새로운 데이터셋 통합"""
    
    print("🚀 새로운 데이터셋 통합 시작")
    print("=" * 60)
    
    # 1. 기존 데이터 로드
    print("\n📁 기존 데이터 로드 중...")
    try:
        with open('model/raw_data.pkl', 'rb') as f:
            existing_df = pickle.load(f)
        print(f"✅ 기존 데이터 로드 완료: {len(existing_df):,}개")
    except Exception as e:
        print(f"❌ 기존 데이터 로드 실패: {e}")
        return
    
    # 2. 새로운 데이터셋 파일들
    new_files = [
        "미국으로 수출 2.xlsx",
        "미국으로 수출.xlsx", 
        "중국 으로 수출.xlsx"
    ]
    
    all_new_data = []
    
    for file in new_files:
        file_path = os.path.join("data", file)
        
        if os.path.exists(file_path):
            try:
                print(f"\n📁 처리 중: {file}")
                
                # 데이터 로드
                df = pd.read_excel(file_path)
                print(f"  레코드 수: {len(df):,}개")
                
                # 문제사유 병합 처리 (기존 방식과 동일)
                sa_yu_cols = [col for col in df.columns if "문제사유" in col]
                df["문제사유"] = df[sa_yu_cols].fillna("").astype(str).agg(" ".join, axis=1)
                
                # 필요한 컬럼만 선택
                required_cols = ["품목", "원산지", "수입국", "조치사항", "문제사유", "HS CODE"]
                df = df[required_cols].dropna()
                
                # 출처 파일 정보 추가
                df["출처파일"] = file
                
                all_new_data.append(df)
                print(f"  ✅ 처리 완료: {len(df):,}개")
                
            except Exception as e:
                print(f"  ❌ 처리 실패: {e}")
        else:
            print(f"❌ 파일 없음: {file}")
    
    # 3. 새로운 데이터 병합
    if all_new_data:
        print(f"\n🔗 새로운 데이터 병합 중...")
        new_df = pd.concat(all_new_data, ignore_index=True)
        print(f"✅ 새로운 데이터 병합 완료: {len(new_df):,}개")
        
        # 4. 기존 데이터와 병합
        print(f"\n🔗 전체 데이터 병합 중...")
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        print(f"✅ 전체 데이터 병합 완료: {len(combined_df):,}개")
        
        # 5. 중복 제거 (필요한 경우)
        print(f"\n🧹 중복 데이터 제거 중...")
        initial_count = len(combined_df)
        combined_df = combined_df.drop_duplicates(subset=['품목', '원산지', '수입국', '문제사유'], keep='first')
        final_count = len(combined_df)
        removed_count = initial_count - final_count
        print(f"✅ 중복 제거 완료: {removed_count:,}개 제거됨")
        
        # 6. 텍스트 전처리
        print(f"\n📝 텍스트 전처리 중...")
        tokenizer = RegexTokenizer()
        
        # 텍스트 결합: 품목 + 원산지 + 수입국 + 문제사유
        combined_df["텍스트"] = (
            combined_df["품목"].astype(str) + " " +
            combined_df["원산지"].astype(str) + " " +
            combined_df["수입국"].astype(str) + " " +
            combined_df["문제사유"].astype(str) + " " +
            combined_df["HS CODE"].astype(str)
        )
        
        # 토큰화 적용
        combined_df["텍스트"] = combined_df["텍스트"].apply(lambda x: " ".join(tokenizer.tokenize(x, flatten=True)))
        
        # 7. TF-IDF 모델 재학습
        print(f"\n🤖 TF-IDF 모델 재학습 중...")
        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(combined_df["텍스트"])
        
        # 8. 모델 저장
        print(f"\n💾 모델 저장 중...")
        os.makedirs("model", exist_ok=True)
        
        with open("model/vectorizer.pkl", "wb") as f:
            pickle.dump(vectorizer, f)
        with open("model/indexed_matrix.pkl", "wb") as f:
            pickle.dump(X, f)
        with open("model/raw_data.pkl", "wb") as f:
            pickle.dump(combined_df, f)
        
        print(f"✅ 모델 저장 완료")
        
        # 9. 통합 결과 분석
        print(f"\n📊 통합 결과 분석")
        print("=" * 40)
        
        # 국가별 데이터 분포
        country_counts = combined_df['수입국'].value_counts()
        print(f"국가별 데이터 분포:")
        for country, count in country_counts.head(10).items():
            print(f"  {country}: {count:,}개")
        
        # 중국, 미국 데이터 확인
        china_data = combined_df[combined_df['수입국'] == '중국']
        us_data = combined_df[combined_df['수입국'] == '미국']
        
        print(f"\n🇨🇳🇺🇸 중국, 미국 데이터:")
        print(f"  중국: {len(china_data):,}개 (기존: 27,249개 → +{len(china_data)-27249:,}개)")
        print(f"  미국: {len(us_data):,}개 (기존: 73,870개 → +{len(us_data)-73870:,}개)")
        print(f"  중국+미국: {len(china_data) + len(us_data):,}개")
        
        # 데이터 품질 확인
        print(f"\n📈 데이터 품질:")
        print(f"  전체 데이터: {len(combined_df):,}개")
        print(f"  고유 품목: {combined_df['품목'].nunique():,}개")
        print(f"  고유 국가: {combined_df['수입국'].nunique()}개")
        
        # 문제사유 길이 분석
        reason_lengths = combined_df['문제사유'].str.len()
        print(f"  문제사유 평균 길이: {reason_lengths.mean():.1f}자")
        print(f"  빈 문제사유: {(combined_df['문제사유'].str.strip() == '').sum():,}개")
        
        return combined_df
        
    else:
        print("❌ 새로운 데이터가 없습니다.")
        return None

def test_integrated_system():
    """통합된 시스템 테스트"""
    
    print(f"\n🧪 통합된 시스템 테스트")
    print("=" * 40)
    
    try:
        # 새로운 모델 로드
        with open('model/raw_data.pkl', 'rb') as f:
            df = pickle.load(f)
        with open('model/vectorizer.pkl', 'rb') as f:
            vectorizer = pickle.load(f)
        with open('model/indexed_matrix.pkl', 'rb') as f:
            X = pickle.load(f)
        
        print(f"✅ 모델 로드 성공")
        print(f"  데이터: {len(df):,}개")
        print(f"  벡터 크기: {X.shape}")
        
        # 간단한 검색 테스트
        test_queries = ["중국 라면", "미국 과자", "중국 채소", "미국 수산물"]
        
        for query in test_queries:
            # 쿼리 전처리
            query_vector = vectorizer.transform([query])
            
            # 유사도 계산
            from sklearn.metrics.pairwise import cosine_similarity
            similarities = cosine_similarity(query_vector, X).flatten()
            
            # 상위 결과 찾기
            top_indices = similarities.argsort()[-5:][::-1]
            
            print(f"\n🔍 '{query}' 검색 결과:")
            for i, idx in enumerate(top_indices, 1):
                if similarities[idx] > 0.1:  # 임계값
                    result = df.iloc[idx]
                    print(f"  {i}. {result['품목']} ({result['수입국']}) - 유사도: {similarities[idx]:.3f}")
        
        print(f"\n✅ 시스템 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 시스템 테스트 실패: {e}")

if __name__ == "__main__":
    # 1. 새로운 데이터 통합
    integrated_df = integrate_new_data()
    
    if integrated_df is not None:
        # 2. 통합된 시스템 테스트
        test_integrated_system()
        
        print(f"\n🎉 새로운 데이터셋 통합 완료!")
        print(f"📊 최종 데이터: {len(integrated_df):,}개")
    else:
        print(f"\n❌ 데이터 통합 실패") 