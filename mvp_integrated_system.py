#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 KATI MVP 통합 수출 지원 시스템
- 중국, 미국만 지원
- 라면 제품에 집중
- 핵심 기능만 포함
"""

import pickle
import os
from datetime import datetime
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from soynlp.tokenizer import RegexTokenizer
from typing import Dict

# MVP 모듈들 import
try:
    from mvp_regulations import get_mvp_regulations, get_mvp_countries, get_mvp_products, display_mvp_regulation_info
    from nutrition_label_generator import NutritionLabelGenerator, APIImageGenerator
    from dashboard_analyzer import DashboardAnalyzer
    from document_generator import DocumentGenerator
    from integrated_nlg_engine import IntegratedNLGEngine
    from advanced_label_generator import AdvancedLabelGenerator
    from real_time_regulation_system import RealTimeRegulationCrawler
    from regulation_data_exporter import RegulationDataExporter
    from action_plan_generator import ActionPlanGenerator
except ImportError as e:
    print(f"⚠️ 일부 모듈을 찾을 수 없습니다: {e}")
    print("💡 필요한 파일들이 같은 폴더에 있는지 확인해주세요.")

class MVPCustomsAnalyzer:
    """MVP 통관 거부사례 분석기"""
    
    def __init__(self):
        self.vectorizer = None
        self.indexed_matrix = None
        self.raw_data = None
        self.tokenizer = RegexTokenizer()
        self.load_model()
    
    def load_model(self):
        """학습된 모델 로드"""
        try:
            with open('model/vectorizer.pkl', 'rb') as f:
                self.vectorizer = pickle.load(f)
            with open('model/indexed_matrix.pkl', 'rb') as f:
                self.indexed_matrix = pickle.load(f)
            with open('model/raw_data.pkl', 'rb') as f:
                self.raw_data = pickle.load(f)
            print("✅ MVP 모델 로드 완료")
        except Exception as e:
            print(f"❌ 모델 로드 실패: {e}")
            print("💡 model/ 폴더에 필요한 파일들이 있는지 확인해주세요.")
    
    def analyze_customs_failures(self, user_input, threshold=0.3):
        """통관 거부사례 분석 (MVP 버전)"""
        if self.vectorizer is None or self.indexed_matrix is None or self.raw_data is None:
            return []
        
        # 입력 전처리
        processed_input = self._preprocess_input(user_input)
        
        # TF-IDF 벡터화
        input_vector = self.vectorizer.transform([processed_input])
        
        # 유사도 계산
        similarities = cosine_similarity(input_vector, self.indexed_matrix).flatten()
        
        # 결과 필터링 (MVP: 중국, 미국만)
        results = []
        for i, sim in enumerate(similarities):
            if sim >= threshold:
                row = self.raw_data.iloc[i]
                country = row.get('수입국', '정보 없음')
                
                # MVP 국가만 필터링
                if country in ['중국', '미국']:
                    results.append({
                        'index': i,
                        'similarity': sim,
                        'data': row.to_dict()
                    })
        
        # 유사도 순으로 정렬
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        return results[:10]  # 상위 10개만 반환
    
    def _preprocess_input(self, user_input):
        """입력 전처리 (MVP 버전)"""
        # 간단한 키워드 확장
        keywords = {
            '라면': ['라면', '면류', '인스턴트', '즉석'],
            '중국': ['중국', '차이나', '중화'],
            '미국': ['미국', 'USA', 'US', '아메리카']
        }
        
        expanded_input = user_input
        for key, values in keywords.items():
            if key in user_input:
                expanded_input += ' ' + ' '.join(values)
        
        return expanded_input

class MVPSystem:
    """MVP 통합 시스템"""
    
    def __init__(self):
        self.customs_analyzer = MVPCustomsAnalyzer()
        self.nlg_engine = IntegratedNLGEngine()
        self.dashboard_analyzer = DashboardAnalyzer()
        self.document_generator = DocumentGenerator()
        
        # MVP 설정
        self.supported_countries = ['중국', '미국']
        self.supported_products = ['라면']
        
        # 실시간 규제 크롤러 초기화
        self.real_time_crawler = RealTimeRegulationCrawler()
        
        # NLG 엔진 초기화
        self.nlg_engine = IntegratedNLGEngine()
        
        # 규제 데이터 내보내기 시스템 초기화
        self.regulation_exporter = RegulationDataExporter()
        
        # 액션 플랜 생성기 초기화
        self.action_plan_generator = ActionPlanGenerator()
    
    def run(self):
        """MVP 시스템 실행"""
        print("🎯 KATI MVP 통합 수출 지원 시스템")
        print("=" * 60)
        print("📋 지원 범위:")
        print(f"   🌍 국가: {', '.join(self.supported_countries)}")
        print(f"   📦 제품: {', '.join(self.supported_products)}")
        print("=" * 60)
        
        while True:
            print("\n📋 MVP 메뉴 선택:")
            print("1. 🚨 통관 거부사례 분석 (중국/미국)")
            print("2. 📋 규제정보 조회 (중국/미국)")
            print("3. 📊 대시보드 분석")
            print("4. 📄 자동 서류 생성")
            print("5. 🏷️ 영양정보 라벨 생성")
            print("6. 🔍 규제 준수성 분석 (입력정보 vs 규제정보)")
            print("7. 종료")
            print("=" * 50)
            
            choice = input("선택 (1-7): ").strip()
            
            if choice == "1":
                self.customs_analysis_menu()
            elif choice == "2":
                self.regulation_menu()
            elif choice == "3":
                self.dashboard_menu()
            elif choice == "4":
                self.document_generation_menu()
            elif choice == "5":
                self.nutrition_label_menu()
            elif choice == "6":
                self.compliance_analysis_menu()
            elif choice == "7":
                print("\n👋 MVP 시스템을 종료합니다.")
                break
            else:
                print("❌ 잘못된 선택입니다. 1-7 중에서 선택해주세요.")
    
    def customs_analysis_menu(self):
        """통관 거부사례 분석 메뉴"""
        print("\n🚨 통관 거부사례 분석 (MVP)")
        print("-" * 40)
        print("💡 예시: '중국으로 라면 수출하고싶어', '미국 라면 통관 거부'")
        print(f"📊 분석 가능 국가: {', '.join(self.supported_countries)}")
        
        user_input = input("\n🔍 검색어를 입력하세요: ").strip()
        if not user_input:
            print("❌ 검색어를 입력해주세요.")
            return
        
        print(f"\n🔍 '{user_input}' 관련 통관 거부사례를 분석 중...")
        
        # 유사도 임계값 조정으로 결과 찾기
        thresholds = [0.3, 0.2, 0.1]
        results = []
        
        for threshold in thresholds:
            results = self.customs_analyzer.analyze_customs_failures(user_input, threshold)
            if results:
                break
        
        if not results:
            print("❌ 관련 통관 거부사례를 찾을 수 없습니다.")
            print("💡 다른 키워드로 검색해보세요.")
            return
        
        # 결과 표시
        print(f"\n✅ {len(results)}개의 관련 사례를 찾았습니다:")
        print("=" * 60)
        
        for i, result in enumerate(results, 1):
            data = result['data']
            similarity = result['similarity']
            
            # 유사도 등급 분류
            if similarity >= 0.5:
                grade = "🔴 높음"
            elif similarity >= 0.3:
                grade = "🟡 보통"
            else:
                grade = "🟢 낮음"
            
            print(f"\n{i}. {grade} (유사도: {similarity:.2f})")
            print(f"   국가: {data.get('수입국', '정보 없음')}")
            print(f"   품목: {data.get('품목', '정보 없음')}")
            print(f"   거부사유: {data.get('거부사유', '정보 없음')}")
            print(f"   조치사항: {data.get('조치사항', '정보 없음')}")
    
    def regulation_menu(self):
        """규제정보 조회 메뉴"""
        print("\n📋 규제정보 조회 (중국/미국)")
        print("-" * 40)
        print("1. 🇨🇳 중국 규제정보 조회")
        print("2. 🇺🇸 미국 규제정보 조회")
        print("3. 🔙 메인 메뉴로")
        
        choice = input("선택 (1-3): ").strip()
        
        if choice == "1":
            display_mvp_regulation_info("중국", "라면")
        elif choice == "2":
            display_mvp_regulation_info("미국", "라면")
        elif choice == "3":
            return
        else:
            print("❌ 잘못된 선택입니다.")
    
    def dashboard_menu(self):
        """대시보드 분석 메뉴"""
        print("\n📊 대시보드 분석 (MVP)")
        print("-" * 40)
        print("💡 중국, 미국 통관 거부사례 통계 분석")
        
        try:
            # 중국, 미국 데이터만 필터링
            if self.customs_analyzer.raw_data is not None:
                mvp_data = self.customs_analyzer.raw_data[
                    self.customs_analyzer.raw_data['수입국'].isin(self.supported_countries)
                ]
                
                if not mvp_data.empty:
                    print(f"\n📈 MVP 국가 통계:")
                    print(f"   총 사례 수: {len(mvp_data)}건")
                    print(f"   중국: {len(mvp_data[mvp_data['수입국'] == '중국'])}건")
                    print(f"   미국: {len(mvp_data[mvp_data['수입국'] == '미국'])}건")
                    
                    # 상위 거부사유
                    if '거부사유' in mvp_data.columns:
                        top_reasons = mvp_data['거부사유'].value_counts().head(5)
                        print(f"\n🔴 상위 거부사유 (MVP):")
                        for reason, count in top_reasons.items():
                            if pd.notna(reason) and reason != '정보 없음':
                                print(f"   • {reason}: {count}건")
                else:
                    print("❌ MVP 국가 데이터가 없습니다.")
            else:
                print("❌ 데이터를 로드할 수 없습니다.")
        except Exception as e:
            print(f"❌ 대시보드 분석 중 오류: {e}")
    
    def document_generation_menu(self):
        """자동 서류 생성 메뉴"""
        print("\n📄 자동 서류 생성 (MVP)")
        print("-" * 40)
        print("💡 중국, 미국 수출용 서류 자동 생성")
        print("⚠️ 이 기능은 아직 구현 중입니다.")
    
    def nutrition_label_menu(self):
        """영양정보 라벨 생성 메뉴"""
        print("\n🏷️ 영양정보 라벨 생성 (MVP)")
        print("-" * 40)
        print("💡 2027년 중국, 2025년 미국 규정 반영")
        print("⚠️ 이 기능은 아직 구현 중입니다.")
    
    def compliance_analysis_menu(self):
        """규제 준수성 분석 메뉴"""
        print("\n🔍 규제 준수성 분석 (입력정보 vs 규제정보)")
        print("-" * 50)
        print("💡 사용자가 입력한 정보와 규제 정보를 비교하여 준수 여부를 분석합니다.")
        print("💡 부족한 부분을 찾아서 구체적인 개선 방안을 제시합니다.")
        
        # 국가 선택
        print("\n🌍 분석할 국가를 선택하세요:")
        print("1. 중국")
        print("2. 미국")
        country_choice = input("선택 (1-2): ").strip()
        
        country = None
        if country_choice == "1":
            country = "중국"
        elif country_choice == "2":
            country = "미국"
        else:
            print("❌ 잘못된 선택입니다.")
            return
        
        product = "라면"  # MVP는 라면만 지원
        
        print(f"\n📋 {country} {product} 수출 준비 현황을 입력해주세요:")
        
        # 회사 기본 정보 입력
        print("\n🏢 회사 기본 정보:")
        company_info = {
            "company_name": input("회사명: ").strip() or "한국식품(주)",
            "address": input("주소: ").strip() or "서울특별시 강남구 테헤란로 123",
            "phone": input("연락처: ").strip() or "02-1234-5678",
            "email": input("이메일: ").strip() or "export@koreafood.com",
            "representative": input("대표자명: ").strip() or "홍길동"
        }
        
        # 제품 정보 입력
        print(f"\n📦 {product} 제품 정보:")
        product_info = {
            "product_name": input("제품명: ").strip() or "한국 라면",
            "manufacturer": input("제조사: ").strip() or "한국식품(주)",
            "origin": input("원산지: ").strip() or "대한민국",
            "expiry_date": input("유통기한 (YYYY-MM-DD): ").strip() or "2026-12-31"
        }
        
        # 영양성분 정보
        print(f"\n🍽️ 영양성분 정보:")
        nutrition = {
            "열량": input("열량 (kcal): ").strip() or "400 kcal",
            "단백질": input("단백질 (g): ").strip() or "12g",
            "지방": input("지방 (g): ").strip() or "15g",
            "탄수화물": input("탄수화물 (g): ").strip() or "60g",
            "나트륨": input("나트륨 (mg): ").strip() or "800mg",
            "당류": input("당류 (g): ").strip() or "5g"
        }
        product_info["nutrition"] = nutrition
        
        # 성분 정보
        ingredients_input = input("성분 (쉼표로 구분): ").strip() or "면류(밀가루, 소금), 분말스프, 건조야채, 조미료, 향신료"
        product_info["ingredients"] = [ing.strip() for ing in ingredients_input.split(",")]
        
        # 알레르기 정보
        allergy_input = input("알레르기 성분 (쉼표로 구분, 없으면 '없음'): ").strip() or "밀, 대두"
        if allergy_input.lower() == "없음":
            product_info["allergy_ingredients"] = []
        else:
            product_info["allergy_ingredients"] = [allergy.strip() for allergy in allergy_input.split(",")]
        
        # 보관 방법
        product_info["storage_method"] = input("보관방법: ").strip() or "직사광선을 피해 서늘한 곳에 보관"
        
        # 준비된 서류 정보
        print(f"\n📄 준비된 서류 현황:")
        prepared_documents = []
        document_options = {
            "1": "상업송장 (Commercial Invoice)",
            "2": "포장명세서 (Packing List)",
            "3": "원산지증명서 (Certificate of Origin)",
            "4": "위생증명서 (Health Certificate)",
            "5": "FDA 등록 (미국용)",
            "6": "중국 라벨링 승인서 (중국용)",
            "7": "방사선 검사증명서",
            "8": "EORI 번호 (EU용)"
        }
        
        print("준비된 서류를 선택하세요 (번호로 선택, 완료시 'done' 입력):")
        for key, value in document_options.items():
            print(f"   {key}. {value}")
        
        while True:
            doc_choice = input("서류 번호 (또는 'done'): ").strip()
            if doc_choice.lower() == 'done':
                break
            if doc_choice in document_options:
                prepared_documents.append(document_options[doc_choice])
                print(f"✅ {document_options[doc_choice]} 추가됨")
            else:
                print("❌ 잘못된 번호입니다.")
        
        # 라벨링 정보
        print(f"\n🏷️ 라벨링 현황:")
        labeling_info = {
            "has_nutrition_label": input("영양성분표 있음? (y/n): ").strip().lower() == 'y',
            "has_allergy_info": input("알레르기 정보 표기? (y/n): ").strip().lower() == 'y',
            "has_expiry_date": input("유통기한 표기? (y/n): ").strip().lower() == 'y',
            "has_ingredients": input("성분표 있음? (y/n): ").strip().lower() == 'y',
            "has_storage_info": input("보관방법 표기? (y/n): ").strip().lower() == 'y',
            "has_manufacturer_info": input("제조사 정보 표기? (y/n): ").strip().lower() == 'y'
        }
        
        # 분석 실행
        print(f"\n🔍 {country} {product} 규제 준수성 분석 중...")
        analysis_result = self._analyze_compliance(country, product, company_info, product_info, prepared_documents, labeling_info)
        
        # 결과 표시
        self._display_compliance_result(analysis_result)
    
    def _analyze_compliance(self, country, product, company_info, product_info, prepared_documents, labeling_info):
        """규제 준수성 분석"""
        analysis = {
            "country": country,
            "product": product,
            "overall_score": 0,
            "compliance_status": "미준수",
            "missing_requirements": [],
            "improvement_suggestions": [],
            "critical_issues": [],
            "minor_issues": []
        }
        
        # 국가별 규제 정보 가져오기
        try:
            if country == "중국":
                regulations = self.real_time_crawler.get_real_time_regulations("중국", "라면")
            elif country == "미국":
                regulations = self.real_time_crawler.get_real_time_regulations("미국", "라면")
            else:
                regulations = None
        except:
            # 폴백: MVP 규제 정보 사용
            if country == "중국":
                regulations = get_mvp_regulations().get("중국", {}).get("라면", {})
            elif country == "미국":
                regulations = get_mvp_regulations().get("미국", {}).get("라면", {})
            else:
                regulations = {}
        
        if not regulations:
            analysis["critical_issues"].append("규제 정보를 찾을 수 없습니다.")
            return analysis
        
        # 1. 필수 서류 검사
        required_documents = regulations.get("필요서류", [])
        missing_docs = []
        for doc in required_documents:
            if doc not in prepared_documents:
                missing_docs.append(doc)
        
        if missing_docs:
            analysis["missing_requirements"].extend(missing_docs)
            analysis["critical_issues"].append(f"필수 서류 부족: {', '.join(missing_docs)}")
        
        # 2. 라벨링 요구사항 검사
        if country == "중국":
            # 중국 라벨링 규정 (GB 7718-2025)
            if not labeling_info["has_nutrition_label"]:
                analysis["critical_issues"].append("중국 GB 7718-2025: 영양성분표 필수")
            if not labeling_info["has_allergy_info"]:
                analysis["critical_issues"].append("중국 GB 7718-2025: 8대 알레르기 정보 필수")
            if not labeling_info["has_expiry_date"]:
                analysis["critical_issues"].append("중국 GB 7718-2025: 유통기한 필수")
            if not labeling_info["has_ingredients"]:
                analysis["critical_issues"].append("중국 GB 7718-2025: 성분표 필수")
            if not labeling_info["has_storage_info"]:
                analysis["minor_issues"].append("중국 GB 7718-2025: 보관방법 권장")
            if not labeling_info["has_manufacturer_info"]:
                analysis["critical_issues"].append("중국 GB 7718-2025: 제조사 정보 필수")
        
        elif country == "미국":
            # 미국 라벨링 규정 (FDA)
            if not labeling_info["has_nutrition_label"]:
                analysis["critical_issues"].append("미국 FDA: 영양성분표 필수")
            if not labeling_info["has_allergy_info"]:
                analysis["critical_issues"].append("미국 FDA: 9대 알레르기 정보 필수")
            if not labeling_info["has_expiry_date"]:
                analysis["minor_issues"].append("미국 FDA: 유통기한 권장")
            if not labeling_info["has_ingredients"]:
                analysis["critical_issues"].append("미국 FDA: 성분표 필수")
            if not labeling_info["has_storage_info"]:
                analysis["minor_issues"].append("미국 FDA: 보관방법 권장")
            if not labeling_info["has_manufacturer_info"]:
                analysis["critical_issues"].append("미국 FDA: 제조사 정보 필수")
        
        # 3. 제한사항 검사
        restrictions = regulations.get("제한사항", [])
        for restriction in restrictions:
            if "나트륨" in restriction and "나트륨" in product_info["nutrition"]:
                sodium_value = product_info["nutrition"]["나트륨"]
                if "mg" in sodium_value:
                    try:
                        sodium_amount = int(sodium_value.replace("mg", "").strip())
                        if sodium_amount > 800:  # 예시 임계값
                            analysis["critical_issues"].append(f"나트륨 함량 초과: {sodium_amount}mg (권장: 800mg 이하)")
                    except:
                        pass
        
        # 4. 점수 계산
        total_checks = len(required_documents) + 6  # 서류 + 라벨링 체크
        passed_checks = len(required_documents) - len(missing_docs)
        
        # 라벨링 체크
        for key, value in labeling_info.items():
            if value:
                passed_checks += 1
        
        analysis["overall_score"] = (passed_checks / total_checks) * 100
        
        # 준수 상태 결정
        if analysis["overall_score"] >= 90:
            analysis["compliance_status"] = "준수"
        elif analysis["overall_score"] >= 70:
            analysis["compliance_status"] = "부분 준수"
        else:
            analysis["compliance_status"] = "미준수"
        
        # 개선 제안 생성
        analysis["improvement_suggestions"] = self._generate_improvement_suggestions(analysis, country)
        
        return analysis
    
    def _generate_improvement_suggestions(self, analysis, country):
        """개선 제안 생성"""
        suggestions = []
        
        if analysis["missing_requirements"]:
            suggestions.append("📄 필수 서류 준비:")
            for doc in analysis["missing_requirements"]:
                suggestions.append(f"   • {doc} 서류를 즉시 준비하세요.")
        
        if analysis["critical_issues"]:
            suggestions.append("🚨 긴급 개선사항:")
            for issue in analysis["critical_issues"]:
                suggestions.append(f"   • {issue}")
        
        if analysis["minor_issues"]:
            suggestions.append("⚠️ 권장 개선사항:")
            for issue in analysis["minor_issues"]:
                suggestions.append(f"   • {issue}")
        
        # 국가별 특별 제안
        if country == "중국":
            suggestions.append("🇨🇳 중국 특별 권장사항:")
            suggestions.append("   • GB 7718-2025 규정에 맞는 라벨 디자인")
            suggestions.append("   • QR코드 디지털 라벨 준비")
            suggestions.append("   • 중국어 표기 정확성 검토")
        
        elif country == "미국":
            suggestions.append("🇺🇸 미국 특별 권장사항:")
            suggestions.append("   • FDA 등록 완료")
            suggestions.append("   • 9대 알레르기 정보 표기")
            suggestions.append("   • 영양성분표 FDA 형식 준수")
        
        return suggestions
    
    def _display_compliance_result(self, analysis):
        """준수성 분석 결과 표시"""
        print("\n" + "="*60)
        print("🔍 규제 준수성 분석 결과")
        print("="*60)
        
        print(f"🌍 분석 국가: {analysis['country']}")
        print(f"📦 분석 제품: {analysis['product']}")
        print(f"📊 전체 준수도: {analysis['overall_score']:.1f}%")
        
        # 준수 상태 표시
        status_icon = "✅" if analysis['compliance_status'] == "준수" else "⚠️" if analysis['compliance_status'] == "부분 준수" else "❌"
        print(f"📋 준수 상태: {status_icon} {analysis['compliance_status']}")
        
        print("\n" + "-"*60)
        
        # 부족한 요구사항
        if analysis["missing_requirements"]:
            print("📄 부족한 필수 요구사항:")
            for req in analysis["missing_requirements"]:
                print(f"   ❌ {req}")
        
        # 긴급 이슈
        if analysis["critical_issues"]:
            print("\n🚨 긴급 개선 필요:")
            for issue in analysis["critical_issues"]:
                print(f"   🔴 {issue}")
        
        # 경미한 이슈
        if analysis["minor_issues"]:
            print("\n⚠️ 권장 개선사항:")
            for issue in analysis["minor_issues"]:
                print(f"   🟡 {issue}")
        
        # 개선 제안
        if analysis["improvement_suggestions"]:
            print("\n💡 구체적 개선 방안:")
            for suggestion in analysis["improvement_suggestions"]:
                print(f"   {suggestion}")
        
        print("\n" + "="*60)
        
        # 다음 단계 제안
        if analysis['compliance_status'] == "준수":
            print("🎉 축하합니다! 규제를 준수하고 있습니다.")
            print("💡 다음 단계: 수출 서류 제출 및 통관 절차 진행")
        elif analysis['compliance_status'] == "부분 준수":
            print("⚠️ 부분적으로 준수하고 있습니다.")
            print("💡 위 개선사항들을 해결한 후 수출을 진행하세요.")
        else:
            print("❌ 규제를 준수하지 않고 있습니다.")
            print("💡 위 긴급 개선사항들을 모두 해결한 후 수출을 진행하세요.")
        
        print("\n" + "="*60)

def main():
    """MVP 시스템 실행"""
    mvp_system = MVPSystem()
    mvp_system.run()

if __name__ == "__main__":
    main() 