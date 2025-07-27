#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌐 KATI MVP 통합 수출 지원 시스템 - 웹 버전
- Flask 기반 웹 애플리케이션
- 중국, 미국 라면 수출 지원
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
import pickle
import os
from datetime import datetime
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from soynlp.tokenizer import RegexTokenizer
from typing import Dict
import json

# MVP 모듈들 import
try:
    from mvp_regulations import get_mvp_regulations, get_mvp_countries, get_mvp_products, display_mvp_regulation_info
    from nutrition_label_generator import NutritionLabelGenerator, APIImageGenerator
    from dashboard_analyzer import DashboardAnalyzer
    from document_generator import DocumentGenerator
    from integrated_nlg_engine import IntegratedNLGEngine
    from advanced_label_generator import AdvancedLabelGenerator
    from real_time_regulation_system import RealTimeRegulationCrawler
    from action_plan_generator import ActionPlanGenerator
except ImportError as e:
    print(f"⚠️ 일부 모듈을 찾을 수 없습니다: {e}")

app = Flask(__name__)
app.secret_key = 'kati_mvp_secret_key_2024'

class WebMVPCustomsAnalyzer:
    """웹용 MVP 통관 거부사례 분석기"""
    
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
            print("✅ 웹 MVP 모델 로드 완료")
        except Exception as e:
            print(f"❌ 모델 로드 실패: {e}")
    
    def analyze_customs_failures(self, user_input, threshold=0.3):
        """통관 거부사례 분석 (웹 버전)"""
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
        """입력 전처리 (웹 버전)"""
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

class WebMVPSystem:
    """웹용 MVP 통합 시스템"""
    
    def __init__(self):
        self.customs_analyzer = WebMVPCustomsAnalyzer()
        self.supported_countries = ['중국', '미국']
        self.supported_products = ['라면']
        
        # 실시간 규제 크롤러 초기화
        try:
            self.real_time_crawler = RealTimeRegulationCrawler()
        except:
            self.real_time_crawler = None
    
    def analyze_compliance(self, country, product, company_info, product_info, prepared_documents, labeling_info):
        """규제 준수성 분석 (웹 버전)"""
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
                regulations = self.real_time_crawler.get_real_time_regulations("중국", "라면") if self.real_time_crawler else None
            elif country == "미국":
                regulations = self.real_time_crawler.get_real_time_regulations("미국", "라면") if self.real_time_crawler else None
            else:
                regulations = None
        except:
            # 폴백: MVP 규제 정보 사용
            mvp_regs = get_mvp_regulations()
            if country == "중국":
                regulations = mvp_regs.get("중국", {}).get("라면", {})
            elif country == "미국":
                regulations = mvp_regs.get("미국", {}).get("라면", {})
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
            if not labeling_info.get("has_nutrition_label"):
                analysis["critical_issues"].append("중국 GB 7718-2025: 영양성분표 필수")
            if not labeling_info.get("has_allergy_info"):
                analysis["critical_issues"].append("중국 GB 7718-2025: 8대 알레르기 정보 필수")
            if not labeling_info.get("has_expiry_date"):
                analysis["critical_issues"].append("중국 GB 7718-2025: 유통기한 필수")
            if not labeling_info.get("has_ingredients"):
                analysis["critical_issues"].append("중국 GB 7718-2025: 성분표 필수")
            if not labeling_info.get("has_storage_info"):
                analysis["minor_issues"].append("중국 GB 7718-2025: 보관방법 권장")
            if not labeling_info.get("has_manufacturer_info"):
                analysis["critical_issues"].append("중국 GB 7718-2025: 제조사 정보 필수")
        
        elif country == "미국":
            if not labeling_info.get("has_nutrition_label"):
                analysis["critical_issues"].append("미국 FDA: 영양성분표 필수")
            if not labeling_info.get("has_allergy_info"):
                analysis["critical_issues"].append("미국 FDA: 9대 알레르기 정보 필수")
            if not labeling_info.get("has_expiry_date"):
                analysis["minor_issues"].append("미국 FDA: 유통기한 권장")
            if not labeling_info.get("has_ingredients"):
                analysis["critical_issues"].append("미국 FDA: 성분표 필수")
            if not labeling_info.get("has_storage_info"):
                analysis["minor_issues"].append("미국 FDA: 보관방법 권장")
            if not labeling_info.get("has_manufacturer_info"):
                analysis["critical_issues"].append("미국 FDA: 제조사 정보 필수")
        
        # 3. 점수 계산
        total_checks = len(required_documents) + 6
        passed_checks = len(required_documents) - len(missing_docs)
        
        # 라벨링 체크
        for key, value in labeling_info.items():
            if value:
                passed_checks += 1
        
        analysis["overall_score"] = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
        
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
        """개선 제안 생성 (웹 버전)"""
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

# 전역 시스템 인스턴스
mvp_system = WebMVPSystem()

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/customs-analysis')
def customs_analysis():
    """통관 거부사례 분석 페이지"""
    return render_template('customs_analysis.html')

@app.route('/api/customs-analysis', methods=['POST'])
def api_customs_analysis():
    """통관 거부사례 분석 API"""
    data = request.get_json()
    user_input = data.get('user_input', data.get('query', ''))
    
    if not user_input:
        return jsonify({'error': '검색어를 입력해주세요.'})
    
    # 유사도 임계값 조정으로 결과 찾기
    thresholds = [0.3, 0.2, 0.1]
    results = []
    
    for threshold in thresholds:
        results = mvp_system.customs_analyzer.analyze_customs_failures(user_input, threshold)
        if results:
            break
    
    if not results:
        return jsonify({'error': '관련 통관 거부사례를 찾을 수 없습니다.'})
    
    # 결과 포맷팅
    formatted_results = []
    for result in results:
        data = result['data']
        similarity = result['similarity']
        
        # 유사도 등급 분류
        if similarity >= 0.5:
            grade = "높음"
            grade_icon = "🔴"
        elif similarity >= 0.3:
            grade = "보통"
            grade_icon = "🟡"
        else:
            grade = "낮음"
            grade_icon = "🟢"
        
        formatted_results.append({
            'similarity': round(similarity, 2),
            'grade': grade,
            'grade_icon': grade_icon,
            'country': data.get('수입국', '정보 없음'),
            'item': data.get('품목', '정보 없음'),
            'reason': data.get('거부사유', '정보 없음'),
            'action': data.get('조치사항', '정보 없음')
        })
    
    return jsonify({
        'success': True,
        'results': formatted_results,
        'count': len(formatted_results)
    })

@app.route('/regulation-info')
def regulation_info():
    """규제 정보 페이지"""
    return render_template('regulation_info.html')

@app.route('/api/regulation-info', methods=['POST'])
def api_regulation_info():
    """규제 정보 API"""
    data = request.get_json()
    country = data.get('country', '')
    
    if not country:
        return jsonify({'error': '국가를 선택해주세요.'})
    
    try:
        # 실시간 규제 정보 가져오기
        if mvp_system.real_time_crawler:
            regulation_info = mvp_system.real_time_crawler.get_real_time_regulations(country, "라면")
            print(f"✅ 실시간 규제정보 로드 성공: {country}")
        else:
            # 폴백: MVP 규제 정보 사용
            regulation_info = display_mvp_regulation_info(country, "라면")
            print(f"⚠️ 실시간 크롤러 없음, MVP 규제정보 사용: {country}")
        
        return jsonify({
            'success': True,
            'regulation_info': regulation_info
        })
    except Exception as e:
        print(f"❌ 규제정보 API 오류: {str(e)}")
        return jsonify({'error': f'규제 정보 조회 중 오류가 발생했습니다: {str(e)}'})

@app.route('/compliance-analysis')
def compliance_analysis():
    """규제 준수성 분석 페이지"""
    return render_template('compliance_analysis.html')

@app.route('/api/compliance-analysis', methods=['POST'])
def api_compliance_analysis():
    """규제 준수성 분석 API"""
    data = request.get_json()
    
    country = data.get('country', '')
    company_info = data.get('company_info', {})
    product_info = data.get('product_info', {})
    prepared_documents = data.get('prepared_documents', [])
    labeling_info = data.get('labeling_info', {})
    
    if not country:
        return jsonify({'error': '국가를 선택해주세요.'})
    
    try:
        analysis_result = mvp_system.analyze_compliance(
            country, "라면", company_info, product_info, prepared_documents, labeling_info
        )
        
        return jsonify({
            'success': True,
            'analysis': analysis_result
        })
    except Exception as e:
        return jsonify({'error': f'분석 중 오류가 발생했습니다: {str(e)}'})

@app.route('/document-generation')
def document_generation():
    """자동 서류 생성 페이지"""
    return render_template('document_generation.html')

@app.route('/api/document-generation', methods=['POST'])
def api_document_generation():
    """자동 서류 생성 API"""
    data = request.get_json()
    
    country = data.get('country', '')
    product_info = data.get('product_info', {})
    company_info = data.get('company_info', {})
    
    if not country:
        return jsonify({'error': '국가를 선택해주세요.'})
    
    try:
        # DocumentGenerator 인스턴스 생성
        doc_generator = DocumentGenerator()
        
        # 서류 생성
        documents = doc_generator.generate_all_documents(
            country=country,
            product="라면",
            company_info=company_info,
            **product_info
        )
        
        return jsonify({
            'success': True,
            'documents': documents
        })
    except Exception as e:
        return jsonify({'error': f'서류 생성 중 오류가 발생했습니다: {str(e)}'})

@app.route('/nutrition-label')
def nutrition_label():
    """영양정보 라벨 생성 페이지"""
    return render_template('nutrition_label.html')

@app.route('/api/nutrition-label', methods=['POST'])
def api_nutrition_label():
    """영양정보 라벨 생성 API"""
    print("🔍 API 호출됨: /api/nutrition-label")  # 디버그 로그 추가
    
    data = request.get_json()
    print(f"📥 받은 데이터: {data}")  # 디버그 로그 추가
    
    country = data.get('country', '')
    product_info = data.get('product_info', {})
    
    if not country:
        return jsonify({'error': '국가를 선택해주세요.'})
    
    try:
        # AdvancedLabelGenerator 인스턴스 생성
        label_generator = AdvancedLabelGenerator()
        
        # 국가별로 적절한 메서드 호출
        if country == "중국":
            image = label_generator.generate_china_2027_label(product_info)
            label_type = "china_2027"
        elif country == "미국":
            image = label_generator.generate_us_2025_label(product_info)
            label_type = "us_2025"
        else:
            return jsonify({'error': f'지원하지 않는 국가입니다: {country}'})
        
        # 이미지 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"nutrition_label_{country}_{timestamp}.png"
        output_dir = "advanced_labels"
        
        # 디렉토리 생성
        os.makedirs(output_dir, exist_ok=True)
        
        # 이미지 저장
        image_path = os.path.join(output_dir, filename)
        image.save(image_path)
        
        # 텍스트 내용 생성
        text_content = f"""
영양정보 라벨 - {country}
제품명: {product_info.get('name', 'N/A')}
생성일시: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
규정: {label_type.upper()}

영양성분 (100g 기준):
- 칼로리: {product_info.get('nutrition', {}).get('calories', 'N/A')} kcal
- 단백질: {product_info.get('nutrition', {}).get('protein', 'N/A')} g
- 지방: {product_info.get('nutrition', {}).get('fat', 'N/A')} g
- 탄수화물: {product_info.get('nutrition', {}).get('carbs', 'N/A')} g
- 나트륨: {product_info.get('nutrition', {}).get('sodium', 'N/A')} mg
- 당류: {product_info.get('nutrition', {}).get('sugar', 'N/A')} g
- 식이섬유: {product_info.get('nutrition', {}).get('fiber', 'N/A')} g

알레르기 정보: {', '.join(product_info.get('allergies', []))}
        """.strip()
        
        print(f"✅ 라벨 생성 성공: {image_path}")  # 디버그 로그 추가
        
        return jsonify({
            'success': True,
            'label_data': {
                'text_content': text_content,
                'image_path': f"/{image_path.replace(os.sep, '/')}",
                'filename': filename,
                'country': country,
                'label_type': label_type
            }
        })
    except Exception as e:
        print(f"❌ 라벨 생성 오류: {str(e)}")  # 디버그 로그 추가
        return jsonify({'error': f'라벨 생성 중 오류가 발생했습니다: {str(e)}'})

@app.route('/advanced_labels/<filename>')
def serve_label_image(filename):
    """생성된 라벨 이미지 서빙"""
    try:
        return send_from_directory('advanced_labels', filename)
    except Exception as e:
        return jsonify({'error': f'이미지를 찾을 수 없습니다: {str(e)}'}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=port) 