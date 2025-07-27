import os
import pandas as pd
import pickle
from glob import glob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")
from soynlp.tokenizer import RegexTokenizer
warnings.filterwarnings("ignore", category=FutureWarning, module="soynlp")
tokenizer = RegexTokenizer()

def tokenize(text):
    return tokenizer.tokenize(text, flatten=True)

# 📁 데이터 폴더 경로
data_dir = "data"

# 🔍 data/ 폴더 내 모든 .xlsx 파일 검색
excel_files = glob(os.path.join(data_dir, "customsExcel*.xlsx"))
all_dataframes = []

for file in excel_files:
    try:
        df = pd.read_excel(file)

        # ✅ 문제사유 병합 처리
        sa_yu_cols = [col for col in df.columns if "문제사유" in col]
        df["문제사유"] = df[sa_yu_cols].fillna("").astype(str).agg(" ".join, axis=1)

        # ✅ 주요 열 필터링 및 정리
        df = df[["품목", "원산지", "수입국", "조치사항", "문제사유", "HS CODE"]].dropna()
        df["출처파일"] = os.path.basename(file)

        all_dataframes.append(df)
        print(f"[✓] Loaded: {os.path.basename(file)}")
    except Exception as e:
        print(f"[!] Failed to load {file}: {e}")

# 🔗 모든 데이터 합치기
if all_dataframes:
    full_df = pd.concat(all_dataframes, ignore_index=True)
    print(f"✅ 총 데이터 수: {len(full_df)}")

else:
    raise ValueError("❌ 유효한 데이터를 가진 엑셀 파일이 없습니다.")



# 텍스트 결합: 품목 + 원산지 + 수입국 + 문제사유
full_df["텍스트"] = (
    full_df["품목"].astype(str) + " " +
    full_df["원산지"].astype(str) + " " +
    full_df["수입국"].astype(str) + " " +
    full_df["문제사유"].astype(str) + " " +
    full_df["HS CODE"].astype(str)
)

# 토큰화 적용
full_df["텍스트"] = full_df["텍스트"].apply(lambda x: " ".join(tokenize(x)))

# TF-IDF 벡터화
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(full_df["텍스트"])

os.makedirs("model", exist_ok=True)
with open("model/vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)
with open("model/indexed_matrix.pkl", "wb") as f:
    pickle.dump(X, f)
with open("model/raw_data.pkl", "wb") as f:
    pickle.dump(full_df, f)

print("✅ 모델 저장 완료 (model/ 폴더)")
