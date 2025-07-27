import warnings
import pickle
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from soynlp.tokenizer import RegexTokenizer
warnings.filterwarnings("ignore", category=FutureWarning, module="soynlp")

pd.set_option("display.max_colwidth", None)     # 각 셀 내용 전부 출력
pd.set_option("display.max_columns", None)      # 모든 열 출력
pd.set_option("display.width", 300)            # 전체 줄 폭 지정


tokenizer = RegexTokenizer()

def tokenize(text):
    return tokenizer.tokenize(text, flatten=True)  # 단어 단위 리스트 반환

def visualize_statistics(cases):
    df = pd.DataFrame(cases)
    
    if df.empty:
        print("⚠️ 시각화할 데이터가 없습니다.")
        return

    print("\n📊 유사 사례 통계 요약:")
    print("=" * 40)
    
    # 사용 가능한 컬럼들 확인
    available_columns = list(df.columns)
    print(f"📋 사용 가능한 정보: {available_columns}")
    
    # ✅ 1. 조치사항 분포 (컬럼이 존재하고 "정보 없음"이 아닐 때만)
    if "조치사항" in df.columns:
        action_counts = df["조치사항"].value_counts()
        valid_actions = action_counts[action_counts.index != "정보 없음"]
        
        if not valid_actions.empty:
            print(f"\n🛠️ 조치사항 분포:")
            for action, count in valid_actions.head(5).items():
                print(f"   - {action}: {count}건")
        else:
            print("\n⚠️ 조치사항 정보가 없습니다.")
    else:
        print("\n⚠️ 조치사항 컬럼이 없습니다.")

    # ✅ 2. 품목 상위 5개 (컬럼이 존재하고 "정보 없음"이 아닐 때만)
    if "품목" in df.columns:
        item_counts = df["품목"].value_counts()
        valid_items = item_counts[item_counts.index != "정보 없음"]
        
        if not valid_items.empty:
            print(f"\n📦 주요 품목:")
            for item, count in valid_items.head(5).items():
                print(f"   - {item}: {count}건")
        else:
            print("\n⚠️ 품목 정보가 없습니다.")
    else:
        print("\n⚠️ 품목 컬럼이 없습니다.")
    
    # ✅ 3. 수입국 분포
    if "수입국" in df.columns:
        country_counts = df["수입국"].value_counts()
        valid_countries = country_counts[country_counts.index != "정보 없음"]
        
        if not valid_countries.empty:
            print(f"\n🌍 주요 수입국:")
            for country, count in valid_countries.head(5).items():
                print(f"   - {country}: {count}건")
        else:
            print("\n⚠️ 수입국 정보가 없습니다.")
    else:
        print("\n⚠️ 수입국 컬럼이 없습니다.")




# -----------------------------
# 모델 로드
# -----------------------------
def load_model():
    with open("model/vectorizer.pkl", "rb") as f:
        vectorizer = pickle.load(f)
    with open("model/indexed_matrix.pkl", "rb") as f:
        tfidf_matrix = pickle.load(f)
    with open("model/raw_data.pkl", "rb") as f:
        raw_data = pickle.load(f)
    return vectorizer, tfidf_matrix, raw_data

# -----------------------------
# 유사도 분석
# -----------------------------
def analyze_input(user_input, vectorizer, tfidf_matrix, raw_data, top_k=15, threshold=0.1):
    input_vec = vectorizer.transform([user_input])
    similarities = cosine_similarity(input_vec, tfidf_matrix).flatten()
    top_indices = similarities.argsort()[::-1]

    results = []
    for idx in top_indices:
        sim = similarities[idx]
        if sim < threshold:
            break  # 유사도가 너무 낮으면 중단
        row = raw_data.iloc[idx]
        result = {
            "품목": row.get("품목", "정보 없음"),
            "원산지": row.get("원산지", "정보 없음"),
            "수입국": row.get("수입국", "정보 없음"),
            "조치사항": row.get("조치사항", "정보 없음"),
            "문제사유": row.get("문제사유", "정보 없음"),
            "출처파일": row.get("출처파일", "정보 없음"),
            "HS CODE": row.get("HS CODE", "정보 없음"),
            "유사도": round(float(sim), 3)
        }
        results.append(result)
        if len(results) >= top_k:
            break

    return results


# -----------------------------
# 개선 제안 생성
# -----------------------------
def suggest_improvement(cases):
    reasons = " ".join([case["문제사유"] for case in cases]).lower()
    suggestions = []

    if "서류" in reasons or "인증" in reasons:
        suggestions.append("- 관련 인증서류 및 시험성적서를 첨부하십시오.")
    if "라벨" in reasons or "표시" in reasons:
        suggestions.append("- 제품 라벨에 원산지, 수출자, 성분 정보를 명확히 표기하십시오.")
    if "성분" in reasons or "첨가물" in reasons:
        suggestions.append("- 식품첨가물 및 유해물질의 함량 기준을 확인하고 조정하십시오.")
    if "검역" in reasons or "해충" in reasons:
        suggestions.append("- 방역/검역 관련 사전 점검을 수행하십시오.")
    if not suggestions:
        suggestions.append("- 과거 유사 사례를 기반으로 제품 정보를 신중히 점검하십시오.")
    return suggestions

# -----------------------------
# 메인 로직
# -----------------------------
def main():
    print("✅ 수출하고자 하는 제품 정보를 입력해주세요.")
    user_input = input("제품 설명: ")

    vectorizer, tfidf_matrix, raw_data = load_model()
    
    user_input = " ".join(tokenize(user_input))
    

    top_cases = analyze_input(user_input, vectorizer, tfidf_matrix, raw_data, top_k=15, threshold=0.1)

    print("\n📌 유사 통관 실패 사례:")
    df = pd.DataFrame(top_cases)
    for i, row in df.iterrows():
        print(f"\n🧾 [사례 {i+1}]")
        print(f"품목     : {row.get('품목', '정보 없음')}")
        print(f"원산지   : {row.get('원산지', '정보 없음')}")
        print(f"수입국   : {row.get('수입국', '정보 없음')}")
        print(f"조치사항 : {row.get('조치사항', '정보 없음')}")
        문제사유 = row.get("문제사유", "정보 없음")
        # 세로 줄바꿈 적용 (임의 기준으로)
        if isinstance(문제사유, str) and len(문제사유) > 50:
            print("문제사유 :")
            for chunk in [문제사유[i:i+50] for i in range(0, len(문제사유), 50)]:
                print("          " + chunk)
        else:
            print(f"문제사유 : {문제사유}")
        print(f"유사도   : {row.get('유사도', 0):.3f}")
        hscode = row.get("HS CODE", "정보 없음")
        if isinstance(hscode, float):
            if hscode.is_integer():
                hscode = str(int(hscode))
            else:
                hscode = str(hscode)
        print(f"HS CODE : {hscode}")


    print("\n🛠️ 개선 제안:")
    for s in suggest_improvement(top_cases):
        print(s)

    # 시각화 실행
    print("\n📊 유사 사례 통계 요약:")
    visualize_statistics(top_cases)

    print("\n🔐 위 사례들을 참고하여 통관 리스크를 최소화하세요.")


# -----------------------------
# 실행
# -----------------------------
if __name__ == "__main__":
    from main import main
    main()  # 사용자 입력 반복
