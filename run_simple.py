#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import warnings
import pickle
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from soynlp.tokenizer import RegexTokenizer
warnings.filterwarnings("ignore")

def load_model():
    try:
        with open("model/vectorizer.pkl", "rb") as f:
            vectorizer = pickle.load(f)
        with open("model/indexed_matrix.pkl", "rb") as f:
            tfidf_matrix = pickle.load(f)
        with open("model/raw_data.pkl", "rb") as f:
            raw_data = pickle.load(f)
        return vectorizer, tfidf_matrix, raw_data
    except Exception as e:
        print(f"❌ 모델 로딩 실패: {e}")
        return None, None, None

def analyze_input(user_input, vectorizer, tfidf_matrix, raw_data, top_k=5):
    try:
        input_vec = vectorizer.transform([user_input])
        similarities = cosine_similarity(input_vec, tfidf_matrix).flatten()
        top_indices = similarities.argsort()[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            sim = similarities[idx]
            row = raw_data.iloc[idx]
            result = {
                "품목": row.get("품목", "정보 없음"),
                "원산지": row.get("원산지", "정보 없음"),
                "수입국": row.get("수입국", "정보 없음"),
                "조치사항": row.get("조치사항", "정보 없음"),
                "문제사유": row.get("문제사유", "정보 없음"),
                "유사도": round(float(sim), 3)
            }
            results.append(result)
        
        return results
    except Exception as e:
        print(f"❌ 분석 실패: {e}")
        return []

def main():
    print("✅ KATI 통관 실패 사례 검색 시스템")
    print("=" * 50)
    
    # 모델 로딩
    vectorizer, tfidf_matrix, raw_data = load_model()
    if vectorizer is None:
        print("❌ 모델을 로딩할 수 없습니다.")
        return
    
    print(f"✅ 모델 로딩 완료! (데이터: {len(raw_data)}개)")
    
    # 사용자 입력
    print("\n📝 수출하고자 하는 제품 정보를 입력해주세요.")
    user_input = input("제품 설명: ")
    
    if not user_input.strip():
        print("❌ 제품 설명을 입력해주세요.")
        return
    
    # 토크나이징
    tokenizer = RegexTokenizer()
    user_input = " ".join(tokenizer.tokenize(user_input, flatten=True))
    
    # 분석
    results = analyze_input(user_input, vectorizer, tfidf_matrix, raw_data)
    
    if not results:
        print("❌ 유사한 사례를 찾을 수 없습니다.")
        return
    
    # 결과 출력
    print(f"\n📌 유사 통관 실패 사례 ({len(results)}개):")
    print("=" * 50)
    
    for i, result in enumerate(results, 1):
        print(f"\n🧾 [사례 {i}] (유사도: {result['유사도']})")
        print(f"품목     : {result['품목']}")
        print(f"원산지   : {result['원산지']}")
        print(f"수입국   : {result['수입국']}")
        print(f"조치사항 : {result['조치사항']}")
        print(f"문제사유 : {result['문제사유']}")
    
    print("\n🔐 위 사례들을 참고하여 통관 리스크를 최소화하세요.")

if __name__ == "__main__":
    main() 