import os
import pickle
from glob import glob
import pandas as pd
from tqdm import tqdm
from sklearn.feature_extraction.text import TfidfVectorizer
from playwright.sync_api import sync_playwright
import time

def crawl_kati_with_playwright(save_dir="data"):
    print("🌐 Playwright로 KATI에서 동적으로 검색 후 엑셀 다운로드 중...")
    os.makedirs(save_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.kati.net/customs/customsList.do")
        time.sleep(2)  # JS 로딩 대기

        # 🔧 발생기간 선택
        page.select_option("select[name='fromYy']", value="2021")
        page.select_option("select[name='fromMm']", value="01")
        page.select_option("select[name='toYy']", value="2025")
        page.select_option("select[name='toMm']", value="12")

        # ✅ 검색 버튼 클릭
        page.click("button:has-text('검색')")
        time.sleep(3)  # 결과 로딩 대기

        # 📥 엑셀 다운로드 버튼 클릭 (표 하단에 있음)
        links = page.query_selector_all("a[href$='.xlsx']")
        if not links:
            print("❌ 엑셀 링크를 찾지 못했습니다.")
            return

        for i, link in enumerate(links[:10]):
            url = link.get_attribute("href")
            full_url = "https://www.kati.net" + url
            filename = f"customs_excel_{i}.xlsx"
            path = os.path.join(save_dir, filename)

            response = page.request.get(full_url)
            with open(path, "wb") as f:
                f.write(response.body())

            print(f"[✓] 다운로드 완료: {filename}")

        browser.close()


# 🧼 정제 + 벡터화 + 모델 저장
def train_and_save_model(data_dir="data", model_dir="model"):
    print("🧼 통관 실패 데이터 정제 및 모델 학습...")
    excel_files = glob(os.path.join(data_dir, "customs_excel_*.xlsx"))
    all_df = []

    for file in tqdm(excel_files):
        try:
            df = pd.read_excel(file)
            sa_yu_cols = [col for col in df.columns if "문제사유" in col]
            df["문제사유"] = df[sa_yu_cols].fillna("").astype(str).agg(" ".join, axis=1)

            df = df[["품목", "원산지", "수입국", "조치사항", "문제사유"]].dropna()
            df["출처파일"] = os.path.basename(file)
            all_df.append(df)
        except Exception as e:
            print(f"[!] {file} 처리 실패: {e}")

    if not all_df:
        raise ValueError("❌ 유효한 데이터 없음")

    full_df = pd.concat(all_df, ignore_index=True)
    full_df["텍스트"] = (
        full_df["품목"].astype(str) + " " +
        full_df["원산지"].astype(str) + " " +
        full_df["수입국"].astype(str) + " " +
        full_df["문제사유"].astype(str)
    )

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(full_df["텍스트"])

    os.makedirs(model_dir, exist_ok=True)
    with open(os.path.join(model_dir, "vectorizer.pkl"), "wb") as f:
        pickle.dump(vectorizer, f)
    with open(os.path.join(model_dir, "indexed_matrix.pkl"), "wb") as f:
        pickle.dump(X, f)
    with open(os.path.join(model_dir, "raw_data.pkl"), "wb") as f:
        pickle.dump(full_df, f)

    print(f"✅ 모델 저장 완료! 총 데이터 수: {len(full_df)}")

# ------------------------------
# 🔁 외부 호출용 함수
# ------------------------------
def run_training():
    crawl_kati_with_playwright()
    train_and_save_model()
