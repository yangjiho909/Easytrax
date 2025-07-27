#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import warnings
import pickle
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from soynlp.tokenizer import RegexTokenizer
warnings.filterwarnings("ignore", category=FutureWarning, module="soynlp")

# 상세한 규제정보 모듈 임포트
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 자연어 생성 엔진 임포트
try:
    from integrated_nlg_engine import IntegratedNLGEngine
    NLG_AVAILABLE = True
    print("✅ 자연어 생성 엔진이 로드되었습니다.")
except ImportError:
    print("⚠️ 자연어 생성 엔진을 찾을 수 없습니다.")
    NLG_AVAILABLE = False

try:
    from detailed_regulations import (
        get_detailed_regulations, 
        search_detailed_regulations, 
        get_all_countries, 
        get_all_products,
        display_detailed_regulation_info
    )
    REGULATION_AVAILABLE = True
    print("✅ 상세한 규제정보 모듈이 로드되었습니다.")
except ImportError:
    print("⚠️ 상세 규제정보 모듈을 찾을 수 없습니다. 기본 규제정보를 사용합니다.")
    try:
        from __pycache__.country_regulations import (
            get_country_regulations, 
            search_regulations_by_keyword, 
            get_all_countries, 
            get_all_products
        )
        def get_detailed_regulations(country, product): return get_country_regulations(country, product)
        def search_detailed_regulations(keyword): return search_regulations_by_keyword(keyword)
        def display_detailed_regulation_info(country, product): 
            reg = get_country_regulations(country, product)
            if not reg: return f"❌ {country}의 {product}에 대한 규제정보가 없습니다."
            result = f"\n📋 {country} - {product} 규제정보\n"
            result += "=" * 50 + "\n"
            for key, value in reg.items():
                if key in ["원본언어", "번역출처"]: continue
                result += f"\n🔸 {key}:\n"
                if isinstance(value, list):
                    for i, item in enumerate(value, 1):
                        result += f"   {i}. {item}\n"
                else:
                    result += f"   {value}\n"
            return result
        REGULATION_AVAILABLE = True
    except ImportError:
        print("⚠️ 규제정보 모듈을 찾을 수 없습니다. 규제정보 기능을 사용할 수 없습니다.")
        REGULATION_AVAILABLE = False

pd.set_option("display.max_colwidth", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", 300)

tokenizer = RegexTokenizer()

def tokenize(text):
    return tokenizer.tokenize(text, flatten=True)

# -----------------------------
# 1. 통관 거부사례 분석 및 매칭
# -----------------------------
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

def analyze_customs_failures(user_input, vectorizer, tfidf_matrix, raw_data, top_k=10, threshold=0.3):
    """통관 거부사례 유사도 분석 (임계값 적용)"""
    try:
        input_vec = vectorizer.transform([user_input])
        similarities = cosine_similarity(input_vec, tfidf_matrix).flatten()
        top_indices = similarities.argsort()[::-1]
        
        results = []
        for idx in top_indices:
            sim = similarities[idx]
            
            # 유사도가 임계값보다 낮으면 중단
            if sim < threshold:
                break
                
            row = raw_data.iloc[idx]
            result = {
                "품목": row.get("품목", "정보 없음"),
                "원산지": row.get("원산지", "정보 없음"),
                "수입국": row.get("수입국", "정보 없음"),
                "조치사항": row.get("조치사항", "정보 없음"),
                "문제사유": row.get("문제사유", "정보 없음"),
                "HS_CODE": row.get("HS CODE", "정보 없음"),
                "유사도": round(float(sim), 3)
            }
            results.append(result)
            
            # 최대 개수 제한
            if len(results) >= top_k:
                break
        
        return results
    except Exception as e:
        print(f"❌ 통관 거부사례 분석 실패: {e}")
        return []

def display_customs_failures(results, user_query=None, threshold_info=None):
    """통관 거부사례 결과 출력 (자연어 요약 포함)"""
    if not results:
        print("❌ 유사한 통관 거부사례를 찾을 수 없습니다.")
        print("💡 더 구체적인 제품명이나 국가명을 포함해보세요.")
        print("   예시: '한국산 라면을 미국으로 수출하려고 합니다'")
        return
    
    # 자연어 요약 출력 (NLG 엔진 사용 가능한 경우)
    if NLG_AVAILABLE and user_query:
        nlg_engine = IntegratedNLGEngine()
        summary = nlg_engine.generate_customs_analysis_response(results, user_query, threshold_info)
        print(f"\n📊 분석 요약:")
        print("=" * 60)
        print(summary)
        print("=" * 60)
    
    # 상세 결과 출력
    print(f"\n📌 상세 유사 통관 거부사례 ({len(results)}개):")
    print("=" * 60)
    
    # 유사도별로 결과 분류
    high_similarity = [r for r in results if r['유사도'] >= 0.5]
    medium_similarity = [r for r in results if 0.3 <= r['유사도'] < 0.5]
    low_similarity = [r for r in results if r['유사도'] < 0.3]
    
    if high_similarity:
        print(f"🎯 높은 유사도 (0.5 이상): {len(high_similarity)}개")
        print("-" * 40)
        for i, result in enumerate(high_similarity, 1):
            print_result(result, i, "🎯")
    
    if medium_similarity:
        print(f"📊 중간 유사도 (0.3-0.5): {len(medium_similarity)}개")
        print("-" * 40)
        for i, result in enumerate(medium_similarity, 1):
            print_result(result, i, "📊")
    
    if low_similarity:
        print(f"⚠️ 낮은 유사도 (0.3 미만): {len(low_similarity)}개")
        print("   (참고용으로만 사용하세요)")
        print("-" * 40)
        for i, result in enumerate(low_similarity, 1):
            print_result(result, i, "⚠️")

def print_result(result, index, icon):
    """개별 결과 출력"""
    print(f"\n{icon} [사례 {index}] (유사도: {result['유사도']})")
    print(f"품목     : {result['품목']}")
    print(f"원산지   : {result['원산지']}")
    print(f"수입국   : {result['수입국']}")
    print(f"조치사항 : {result['조치사항']}")
    print(f"HS CODE  : {result['HS_CODE']}")
    
    # 문제사유가 길면 줄바꿈 처리
    문제사유 = result['문제사유']
    if isinstance(문제사유, str) and len(문제사유) > 50:
        print("문제사유 :")
        for chunk in [문제사유[i:i+50] for i in range(0, len(문제사유), 50)]:
            print("          " + chunk)
    else:
        print(f"문제사유 : {문제사유}")

# -----------------------------
# 2. 수출대상국가 규제정보 조회
# -----------------------------
def display_regulation_info(country, product):
    """특정 국가의 특정 제품 상세 규제정보 조회 (자연어 요약 포함)"""
    if not REGULATION_AVAILABLE:
        print("❌ 규제정보 모듈을 사용할 수 없습니다.")
        return
    
    regulations = get_detailed_regulations(country, product)
    if not regulations:
        print(f"❌ {country}의 {product}에 대한 규제정보가 없습니다.")
        return
    
    # 자연어 요약 출력 (NLG 엔진 사용 가능한 경우)
    if NLG_AVAILABLE:
        nlg_engine = IntegratedNLGEngine()
        summary = nlg_engine.generate_regulation_info_response(country, product, regulations, show_detail=False)
        print(f"\n📋 {country} - {product} 규제정보 요약:")
        print("=" * 60)
        print(summary)
        
        # 상세 정보 표시 여부 확인
        show_detail = input("\n상세 정보를 보시겠습니까? (y/n): ").strip().lower()
        if show_detail == 'y':
            detailed_info = nlg_engine.generate_regulation_info_response(country, product, regulations, show_detail=True)
            print(detailed_info)
    else:
        # 기존 방식 (NLG 엔진이 없는 경우)
        detailed_info = display_detailed_regulation_info(country, product)
        print(detailed_info)

def search_regulations(keyword):
    """키워드로 상세 규제정보 검색"""
    if not REGULATION_AVAILABLE:
        print("❌ 규제정보 모듈을 사용할 수 없습니다.")
        return
    
    results = search_detailed_regulations(keyword)
    if not results:
        print(f"❌ '{keyword}'와 관련된 규제정보를 찾을 수 없습니다.")
        return
    
    print(f"\n🔍 '{keyword}' 관련 상세 규제정보 ({len(results)}개):")
    print("=" * 60)
    
    for i, result in enumerate(results, 1):
        print(f"\n📋 {i}. {result['국가']} - {result['제품']}")
        regulations = result['규정']
        
        # 주요 정보만 미리보기로 표시
        for key, value in regulations.items():
            if key in ["원본언어", "번역출처", "추가정보"]:
                continue
            if isinstance(value, list) and value:
                print(f"   🔸 {key}: {value[0]}{'...' if len(value) > 1 else ''}")
        
        # 상세정보 보기 옵션 제공
        print(f"   📖 상세정보 보기: {result['국가']}의 {result['제품']} 규제정보")
    
    # 상세정보 보기 선택
    try:
        choice = input(f"\n상세정보를 보시겠습니까? (1-{len(results)}, 엔터로 취소): ").strip()
        if choice and choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(results):
                selected = results[idx]
                detailed_info = display_detailed_regulation_info(selected['국가'], selected['제품'])
                print(detailed_info)
    except (ValueError, KeyboardInterrupt):
        print("\n상세정보 보기를 취소했습니다.")

def show_available_countries():
    """사용 가능한 국가 목록 표시"""
    if not REGULATION_AVAILABLE:
        print("❌ 규제정보 모듈을 사용할 수 없습니다.")
        return
    
    countries = get_all_countries()
    products = get_all_products()
    
    print(f"\n🌍 규제정보 조회 가능한 국가 ({len(countries)}개):")
    print("=" * 40)
    for i, country in enumerate(countries, 1):
        print(f"{i:2d}. {country}")
    
    print(f"\n📦 규제정보 조회 가능한 제품 ({len(products)}개):")
    print("=" * 40)
    for i, product in enumerate(products, 1):
        print(f"{i:2d}. {product}")

# -----------------------------
# 통합 메인 시스템
# -----------------------------
def main():
    print("🚀 KATI 통합 수출 지원 시스템")
    print("=" * 50)
    print("1. 과거 통관 거부사례 분석 및 매칭")
    print("2. 수출대상국가의 규제정보 법령보기")
    print("=" * 50)
    
    # 모델 로딩
    vectorizer, tfidf_matrix, raw_data = load_model()
    if vectorizer is None:
        print("❌ 통관 거부사례 분석 기능을 사용할 수 없습니다.")
        return
    
    print(f"✅ 통관 거부사례 데이터 로딩 완료! (총 {len(raw_data)}건)")
    
    if REGULATION_AVAILABLE:
        print("✅ 규제정보 시스템 로딩 완료!")
    else:
        print("⚠️ 규제정보 시스템을 사용할 수 없습니다.")
    
    while True:
        print("\n" + "=" * 50)
        print("📋 메뉴 선택:")
        print("1. 제품 정보 입력 (통관 거부사례 검색)")
        print("2. 규제정보 조회")
        print("3. 사용 가능한 국가/제품 목록")
        print("4. 📊 대시보드 분석 (통계 및 전략 인사이트)")
        print("5. 📄 자동 서류 생성 (규제정보 기반)")
        print("6. 🏷️ 영양정보 라벨 이미지 생성")
        print("7. 종료")
        print("=" * 50)
        
        choice = input("선택 (1-7): ").strip()
        
        if choice == "1":
            # 통관 거부사례 분석
            print("\n📝 수출하고자 하는 제품 정보를 입력해주세요.")
            
            # 입력 대기 중에 비교분석 가능한 국가 정보 표시
            print("\n💡 입력 대기 중... 현재 비교분석 가능한 국가 정보:")
            print("=" * 50)
            
            # 통관 거부사례 데이터에서 국가 정보 추출
            countries = raw_data["수입국"].dropna().unique()
            top_countries = raw_data["수입국"].value_counts().head(10)
            
            print(f"🌍 통관 거부사례 분석 가능한 국가: {len(countries)}개")
            print("📊 상위 10개 국가 (사례 수):")
            for i, (country, count) in enumerate(top_countries.items(), 1):
                print(f"   {i:2d}. {country:<12} ({count:5d}건)")
            
            if len(countries) > 10:
                print(f"   ... 외 {len(countries) - 10}개 국가")
            
            # 원산지 정보도 표시
            origins = raw_data["원산지"].dropna().unique()
            top_origins = raw_data["원산지"].value_counts().head(5)
            
            print(f"\n🏭 원산지 분석 가능: {len(origins)}개")
            print("📊 상위 5개 원산지:")
            for i, (origin, count) in enumerate(top_origins.items(), 1):
                print(f"   {i}. {origin:<12} ({count:5d}건)")
            
            print("\n" + "=" * 50)
            print("💡 입력 예시:")
            print("   • 한국산 라면을 미국으로 수출하려고 합니다")
            print("   • 중국으로 김치를 수출할 때 주의사항이 궁금해요")
            print("   • 일본 수출 시 라벨 표기 문제가 있었습니다")
            print("   • EU로 화장품을 수출하려고 하는데 인증서가 필요할까요?")
            print("   • 미국에서 식품 첨가물 기준으로 통관이 거부되었습니다")
            print("   • 미국으로 라면수출하고싶어 (간단한 입력도 가능)")
            print("   • 중국 라면 (제품명만 입력해도 분석 가능)")
            print("=" * 50)
            user_input = input("제품 설명: ").strip()
            
            if not user_input:
                print("❌ 제품 설명을 입력해주세요.")
                continue
            
            # 토크나이징 및 검색어 개선
            original_input = user_input
            
            # 간단한 입력에 대한 개선
            if len(user_input.strip()) < 15:
                # 제품과 국가가 명확하지 않은 경우 기본 키워드 추가
                products = ['라면', '김치', '소주', '화장품', '전자제품', '의류', '신발', '가공식품']
                countries = ['미국', '중국', '일본', 'EU', '동남아시아', '러시아', '캐나다', '호주']
                
                found_product = None
                found_country = None
                
                # 제품과 국가 찾기
                for product in products:
                    if product in user_input:
                        found_product = product
                        break
                
                for country in countries:
                    if country in user_input:
                        found_country = country
                        break
                
                # 조합에 따른 개선
                if found_product and found_country:
                    user_input = f"한국산 {found_product}을(를) {found_country}로 수출"
                elif found_product:
                    user_input = f"{found_product} 수출 통관 거부사례"
                elif found_country:
                    user_input = f"{found_country} 수출 통관 거부사례"
                else:
                    user_input = "수출 통관 거부사례"
            
            # 토크나이징
            tokenized_input = " ".join(tokenize(user_input))
            
            print(f"🔍 검색어: '{original_input}'")
            print(f"🔧 개선된 검색어: '{user_input}'")
            print(f"🔧 토크나이징: '{tokenized_input}'")
            
            # 토크나이징된 결과를 실제 검색에 사용
            user_input = tokenized_input
            
            # 분석 실행 (임계값 0.3으로 설정)
            initial_threshold = 0.3
            results = analyze_customs_failures(user_input, vectorizer, tfidf_matrix, raw_data, threshold=initial_threshold)
            final_threshold = initial_threshold
            retry_count = 0
            
            # 결과가 없으면 임계값을 낮춰서 재시도
            if not results:
                print("⚠️ 유사도가 높은 결과가 없습니다. 임계값을 낮춰서 재검색합니다...")
                results = analyze_customs_failures(user_input, vectorizer, tfidf_matrix, raw_data, threshold=0.2)
                final_threshold = 0.2
                retry_count = 1
            
            if not results:
                print("⚠️ 여전히 유사한 결과가 없습니다. 임계값을 더 낮춰서 재검색합니다...")
                results = analyze_customs_failures(user_input, vectorizer, tfidf_matrix, raw_data, threshold=0.1)
                final_threshold = 0.1
                retry_count = 2
            
            # 임계값 정보 구성
            threshold_info = {
                'initial_threshold': initial_threshold,
                'final_threshold': final_threshold,
                'retry_count': retry_count
            }
            
            display_customs_failures(results, original_input, threshold_info)
            
            # 개선 제안 (자연어 엔진에서 이미 처리됨)
            pass
        
        elif choice == "2":
            # 규제정보 조회
            if not REGULATION_AVAILABLE:
                print("❌ 규제정보 기능을 사용할 수 없습니다.")
                continue
            
            # 규제정보 조회 가능한 국가/제품 정보 표시
            print("\n💡 규제정보 조회 가능한 국가 및 제품:")
            print("=" * 50)
            
            try:
                countries = get_all_countries()
                products = get_all_products()
                
                print(f"🌍 규제정보 조회 가능한 국가: {len(countries)}개")
                for i, country in enumerate(countries, 1):
                    print(f"   {i}. {country}")
                
                print(f"\n📦 규제정보 조회 가능한 제품: {len(products)}개")
                for i, product in enumerate(products, 1):
                    print(f"   {i}. {product}")
                
                print("\n" + "=" * 50)
            except:
                print("⚠️ 규제정보 목록을 불러올 수 없습니다.")
            
            print("\n📋 상세 규제정보 조회 방법:")
            print("1. 특정 국가/제품 상세 규제정보 조회")
            print("2. 키워드로 상세 규제정보 검색")
            print("   (제한사항, 허용기준, 필요서류, 통관절차, 주의사항, 추가정보 포함)")
            
            sub_choice = input("선택 (1-2): ").strip()
            
            if sub_choice == "1":
                country = input("국가명 (예: 중국, 미국, 일본): ").strip()
                product = input("제품명 (예: 라면, 과일): ").strip()
                display_regulation_info(country, product)
            
            elif sub_choice == "2":
                keyword = input("검색 키워드: ").strip()
                search_regulations(keyword)
            
            else:
                print("❌ 잘못된 선택입니다.")
        
        elif choice == "3":
            # 사용 가능한 목록 표시
            show_available_countries()
        
        elif choice == "4":
            # 대시보드 분석
            print("\n📊 대시보드 분석을 시작합니다...")
            try:
                from dashboard_analyzer import DashboardAnalyzer
                analyzer = DashboardAnalyzer()
                analyzer.generate_dashboard_report()
            except ImportError:
                print("❌ 대시보드 분석 모듈을 찾을 수 없습니다.")
                print("💡 dashboard_analyzer.py 파일이 필요합니다.")
            except Exception as e:
                print(f"❌ 대시보드 분석 중 오류 발생: {e}")
        
        elif choice == "5":
            # 자동 서류 생성
            print("\n📄 자동 서류 생성을 시작합니다...")
            try:
                from document_generator import DocumentGenerator
                generator = DocumentGenerator()
                
                # 회사 정보 입력
                print("\n💼 회사 정보를 입력해주세요:")
                company_info = {}
                company_info["manufacturer"] = input("제조사명: ").strip() or "한국식품(주)"
                company_info["exporter_name"] = input("수출자명: ").strip() or company_info["manufacturer"]
                company_info["business_number"] = input("사업자등록번호: ").strip() or "123-45-67890"
                company_info["exporter_address"] = input("수출자주소: ").strip() or "서울특별시 강남구 테헤란로 123"
                company_info["exporter_contact"] = input("수출자연락처: ").strip() or "02-1234-5678"
                company_info["contact_person"] = input("담당자명: ").strip() or "김수출"
                company_info["contact_info"] = input("담당자연락처: ").strip() or "02-1234-5678"
                
                # 제품 정보 입력
                print("\n📦 제품 정보를 입력해주세요:")
                country = input("수출국가 (예: 중국, 미국, 일본): ").strip()
                product = input("제품명 (예: 라면, 김치): ").strip()
                
                if not country or not product:
                    print("❌ 국가와 제품명을 모두 입력해주세요.")
                    continue
                
                # 체크리스트 표시
                checklist = generator.get_document_checklist(country, product)
                if "error" not in checklist:
                    print(f"\n📋 {country} - {product} 서류 체크리스트:")
                    print("=" * 50)
                    for i, doc in enumerate(checklist["필요서류"], 1):
                        print(f"{i}. {doc}")
                    
                    if checklist["통관절차"]:
                        print(f"\n🔄 통관절차:")
                        for i, step in enumerate(checklist["통관절차"], 1):
                            print(f"{i}. {step}")
                    
                    if checklist["주의사항"]:
                        print(f"\n⚠️ 주의사항:")
                        for i, caution in enumerate(checklist["주의사항"][:5], 1):
                            print(f"{i}. {caution}")
                    
                    print(f"\n⏱️ 처리기간: {checklist['처리기간']}")
                    print(f"💰 수수료: {checklist['수수료']}")
                else:
                    print(f"❌ {checklist['error']}")
                    continue
                
                # 서류 생성 여부 확인
                generate_choice = input(f"\n📄 위 서류들을 자동으로 생성하시겠습니까? (y/n): ").strip().lower()
                if generate_choice == 'y':
                    print("\n🔧 서류 생성 중...")
                    documents = generator.generate_all_documents(country, product, company_info)
                    
                    if "error" not in documents:
                        print(f"✅ {len(documents)}개 서류가 생성되었습니다:")
                        for doc_name in documents.keys():
                            print(f"   📄 {doc_name}")
                        
                        # 파일 저장 여부 확인
                        save_choice = input(f"\n💾 생성된 서류를 파일로 저장하시겠습니까? (y/n): ").strip().lower()
                        if save_choice == 'y':
                            saved_files = generator.save_documents(documents)
                            print(f"✅ {len(saved_files)}개 파일이 저장되었습니다:")
                            for filepath in saved_files:
                                print(f"   📁 {filepath}")
                        
                        # 서류 내용 미리보기
                        preview_choice = input(f"\n👀 서류 내용을 미리보기 하시겠습니까? (y/n): ").strip().lower()
                        if preview_choice == 'y':
                            for doc_name, content in documents.items():
                                print(f"\n📄 {doc_name}")
                                print("=" * 50)
                                print(content[:500] + "..." if len(content) > 500 else content)
                                print("=" * 50)
                    else:
                        print(f"❌ {documents['error']}")
                
            except ImportError:
                print("❌ 자동 서류 생성 모듈을 찾을 수 없습니다.")
                print("💡 document_generator.py 파일이 필요합니다.")
            except Exception as e:
                print(f"❌ 자동 서류 생성 중 오류 발생: {e}")
        
        elif choice == "6":
            # 영양정보 라벨 이미지 생성
            print("\n🏷️ 영양정보 라벨 이미지 생성을 시작합니다...")
            try:
                from nutrition_label_generator import NutritionLabelGenerator, APIImageGenerator
                generator = NutritionLabelGenerator()
                
                # 제품 정보 입력
                print("\n📦 제품 정보를 입력해주세요:")
                product_info = {}
                product_info["product_name"] = input("제품명: ").strip() or "한국 라면"
                product_info["manufacturer"] = input("제조사: ").strip() or "한국식품(주)"
                product_info["origin"] = input("원산지: ").strip() or "대한민국"
                product_info["expiry_date"] = input("유통기한 (YYYY-MM-DD): ").strip() or "2026-12-31"
                
                # 영양성분 정보 입력
                print("\n🍽️ 영양성분 정보를 입력해주세요:")
                nutrition = {}
                nutrition["열량"] = input("열량 (kcal): ").strip() or "400 kcal"
                nutrition["단백질"] = input("단백질 (g): ").strip() or "12g"
                nutrition["지방"] = input("지방 (g): ").strip() or "15g"
                nutrition["탄수화물"] = input("탄수화물 (g): ").strip() or "60g"
                nutrition["나트륨"] = input("나트륨 (mg): ").strip() or "800mg"
                nutrition["당류"] = input("당류 (g): ").strip() or "5g"
                product_info["nutrition"] = nutrition
                
                # 성분 정보 입력
                print("\n🥘 성분 정보를 입력해주세요 (쉼표로 구분):")
                ingredients_input = input("성분: ").strip() or "면류(밀가루, 소금), 분말스프, 건조야채, 조미료, 향신료"
                product_info["ingredients"] = [ing.strip() for ing in ingredients_input.split(",")]
                
                # 알레르기 정보 입력
                print("\n⚠️ 알레르기 성분을 입력해주세요 (쉼표로 구분, 없으면 '없음' 입력):")
                allergy_input = input("알레르기 성분: ").strip() or "밀, 대두"
                if allergy_input.lower() == "없음":
                    product_info["allergy_ingredients"] = []
                else:
                    product_info["allergy_ingredients"] = [allergy.strip() for allergy in allergy_input.split(",")]
                
                # 보관 방법 입력
                product_info["storage_method"] = input("보관방법: ").strip() or "직사광선을 피해 서늘한 곳에 보관"
                
                # 제조사 정보 입력
                product_info["address"] = input("제조사 주소: ").strip() or "서울특별시 강남구 테헤란로 123"
                product_info["phone"] = input("제조사 연락처: ").strip() or "02-1234-5678"
                
                # 라벨 생성 옵션 선택
                print("\n🎨 라벨 생성 옵션을 선택해주세요:")
                print("1. 한국어 라벨 생성")
                print("2. 중국어 라벨 생성")
                print("3. 한국어 + 중국어 모두 생성")
                print("4. API를 사용한 고품질 이미지 생성 (API 키 필요)")
                
                label_choice = input("선택 (1-4): ").strip()
                
                generated_files = []
                
                if label_choice in ["1", "3"]:
                    # 한국어 라벨 생성
                    print("\n🔧 한국어 라벨 생성 중...")
                    korean_label = generator.generate_nutrition_label(product_info, "한국")
                    korean_filename = f"nutrition_label_korean_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    korean_path = generator.save_label(korean_label, korean_filename)
                    generated_files.append(korean_path)
                    print(f"✅ 한국어 라벨 생성 완료: {korean_path}")
                
                if label_choice in ["2", "3"]:
                    # 중국어 라벨 생성
                    print("\n🔧 중국어 라벨 생성 중...")
                    chinese_label = generator.generate_chinese_nutrition_label(product_info)
                    chinese_filename = f"nutrition_label_chinese_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    chinese_path = generator.save_label(chinese_label, chinese_filename)
                    generated_files.append(chinese_path)
                    print(f"✅ 중국어 라벨 생성 완료: {chinese_path}")
                
                if label_choice == "4":
                    # API 이미지 생성
                    print("\n🤖 API 이미지 생성 옵션:")
                    print("1. DALL-E API (OpenAI)")
                    print("2. Stable Diffusion API")
                    
                    api_choice = input("API 선택 (1-2): ").strip()
                    
                    if api_choice == "1":
                        api_key = input("OpenAI API 키를 입력하세요: ").strip()
                        if api_key:
                            api_generator = APIImageGenerator(api_key)
                            prompt = f"""
                            Create a professional nutrition facts label for {product_info['product_name']}. 
                            Include: product name "{product_info['product_name']}", nutrition facts table with 
                            calories {nutrition['열량']}, protein {nutrition['단백질']}, fat {nutrition['지방']}, 
                            carbohydrates {nutrition['탄수화물']}, sodium {nutrition['나트륨']}, sugar {nutrition['당류']}, 
                            ingredients list, allergy information, storage instructions. 
                            Use clean, modern design with white background, black text, and blue accents. 
                            Make it look like an official food label that would be printed on packaging.
                            """
                            result = api_generator.generate_with_dalle(prompt)
                            print(result)
                        else:
                            print("❌ API 키가 필요합니다.")
                    
                    elif api_choice == "2":
                        api_url = input("Stable Diffusion API URL (기본: http://localhost:7860): ").strip() or "http://localhost:7860"
                        api_generator = APIImageGenerator()
                        prompt = f"professional nutrition facts label for {product_info['product_name']}, clean design, white background, official food packaging label"
                        result = api_generator.generate_with_stable_diffusion(prompt, api_url)
                        print(result)
                
                if generated_files:
                    print(f"\n✅ 총 {len(generated_files)}개 라벨이 생성되었습니다:")
                    for filepath in generated_files:
                        print(f"   📁 {filepath}")
                    
                    # 라벨 미리보기 옵션
                    preview_choice = input(f"\n👀 생성된 라벨을 확인하시겠습니까? (y/n): ").strip().lower()
                    if preview_choice == 'y':
                        print("\n💡 생성된 라벨 파일을 이미지 뷰어로 열어서 확인하세요.")
                        print("   📁 파일 위치: nutrition_labels/ 폴더")
                
            except ImportError:
                print("❌ 영양정보 라벨 생성 모듈을 찾을 수 없습니다.")
                print("💡 nutrition_label_generator.py 파일이 필요합니다.")
                print("💡 PIL(Pillow) 라이브러리 설치가 필요합니다: pip install Pillow")
            except Exception as e:
                print(f"❌ 영양정보 라벨 생성 중 오류 발생: {e}")
        
        elif choice == "7":
            print("\n👋 KATI 통합 수출 지원 시스템을 종료합니다.")
            break
        
        else:
            print("❌ 잘못된 선택입니다. 1-7 중에서 선택해주세요.")

if __name__ == "__main__":
    main() 