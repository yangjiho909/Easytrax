#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 KATI 시스템 종합 검증 스크립트
- 모든 핵심 모듈 로드 테스트
- 각 기능별 동작 검증
- API 엔드포인트 테스트
- 데이터베이스 연결 확인
"""

import sys
import os
import json
import requests
from datetime import datetime

def test_module_imports():
    """핵심 모듈 로드 테스트"""
    print("🔍 핵심 모듈 로드 테스트")
    print("=" * 50)
    
    modules_to_test = [
        ("Flask", "flask"),
        ("Pandas", "pandas"),
        ("Scikit-learn", "sklearn"),
        ("BeautifulSoup", "bs4"),
        ("Requests", "requests"),
        ("Pillow", "PIL"),
        ("QRCode", "qrcode"),
        ("ReportLab", "reportlab"),
        ("PyPDF2", "PyPDF2"),
        ("FPDF2", "fpdf"),
        ("OpenCV", "cv2"),
        ("EasyOCR", "easyocr"),
        ("Transformers", "transformers"),
        ("Torch", "torch")
    ]
    
    failed_modules = []
    
    for module_name, import_name in modules_to_test:
        try:
            __import__(import_name)
            print(f"✅ {module_name}: 로드 성공")
        except ImportError as e:
            print(f"❌ {module_name}: 로드 실패 - {e}")
            failed_modules.append(module_name)
    
    if failed_modules:
        print(f"\n⚠️ 실패한 모듈: {', '.join(failed_modules)}")
    else:
        print(f"\n🎉 모든 핵심 모듈 로드 성공!")
    
    return len(failed_modules) == 0

def test_custom_modules():
    """커스텀 모듈 로드 테스트"""
    print(f"\n🔍 커스텀 모듈 로드 테스트")
    print("=" * 50)
    
    custom_modules = [
        ("mvp_regulations", "mvp_regulations"),
        ("nutrition_label_generator", "nutrition_label_generator"),
        ("dashboard_analyzer", "dashboard_analyzer"),
        ("document_generator", "document_generator"),
        ("integrated_nlg_engine", "integrated_nlg_engine"),
        ("advanced_label_generator", "advanced_label_generator"),
        ("real_time_regulation_system", "real_time_regulation_system"),
        ("action_plan_generator", "action_plan_generator"),
        ("advanced_pdf_generator", "advanced_pdf_generator"),
        ("label_ocr_extractor", "label_ocr_extractor"),
        ("label_compliance_checker", "label_compliance_checker")
    ]
    
    failed_custom = []
    
    for module_name, import_name in custom_modules:
        try:
            __import__(import_name)
            print(f"✅ {module_name}: 로드 성공")
        except ImportError as e:
            print(f"❌ {module_name}: 로드 실패 - {e}")
            failed_custom.append(module_name)
    
    if failed_custom:
        print(f"\n⚠️ 실패한 커스텀 모듈: {', '.join(failed_custom)}")
    else:
        print(f"\n🎉 모든 커스텀 모듈 로드 성공!")
    
    return len(failed_custom) == 0

def test_ocr_functionality():
    """OCR 기능 테스트"""
    print(f"\n🔍 OCR 기능 테스트")
    print("=" * 50)
    
    try:
        from label_ocr_extractor import LabelOCRExtractor
        extractor = LabelOCRExtractor()
        
        # OCR 엔진 상태 확인
        available_engines = [name for name, config in extractor.ocr_engines.items() 
                           if config.get('available', False)]
        
        if available_engines:
            print(f"✅ OCR 엔진 사용 가능: {', '.join(available_engines)}")
            return True
        else:
            print("❌ 사용 가능한 OCR 엔진이 없습니다")
            return False
            
    except Exception as e:
        print(f"❌ OCR 기능 테스트 실패: {e}")
        return False

def test_pdf_generation():
    """PDF 생성 기능 테스트"""
    print(f"\n🔍 PDF 생성 기능 테스트")
    print("=" * 50)
    
    try:
        from advanced_pdf_generator import AdvancedPDFGenerator
        pdf_generator = AdvancedPDFGenerator()
        
        # 템플릿 확인
        template_count = len(pdf_generator.templates)
        print(f"✅ PDF 템플릿 {template_count}개 로드 완료")
        
        # 테스트 데이터
        test_data = {
            "product_name": "테스트 라면",
            "manufacturer": "테스트 식품",
            "content": "테스트 내용"
        }
        
        # 출력 디렉토리 생성
        os.makedirs("test_output", exist_ok=True)
        
        # PDF 생성 테스트
        output_path = "test_output/test_document.pdf"
        result_path = pdf_generator.generate_pdf_document(
            "상업송장", test_data, {}, output_path
        )
        
        if os.path.exists(result_path):
            file_size = os.path.getsize(result_path)
            print(f"✅ PDF 생성 성공: {result_path} ({file_size} bytes)")
            return True
        else:
            print("❌ PDF 생성 실패")
            return False
            
    except Exception as e:
        print(f"❌ PDF 생성 테스트 실패: {e}")
        return False

def test_web_api_endpoints():
    """웹 API 엔드포인트 테스트"""
    print(f"\n🔍 웹 API 엔드포인트 테스트")
    print("=" * 50)
    
    base_url = "http://localhost:5000"
    endpoints = [
        ("/", "메인 페이지"),
        ("/customs-analysis", "통관분석 페이지"),
        ("/regulation-info", "규제정보 페이지"),
        ("/compliance-analysis", "준수성분석 페이지"),
        ("/document-generation", "서류생성 페이지"),
        ("/nutrition-label", "영양라벨 페이지")
    ]
    
    failed_endpoints = []
    
    for endpoint, name in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: 접속 성공")
            else:
                print(f"❌ {name}: 접속 실패 (상태코드: {response.status_code})")
                failed_endpoints.append(name)
        except Exception as e:
            print(f"❌ {name}: 접속 실패 - {e}")
            failed_endpoints.append(name)
    
    if failed_endpoints:
        print(f"\n⚠️ 실패한 엔드포인트: {', '.join(failed_endpoints)}")
    else:
        print(f"\n🎉 모든 웹 페이지 접속 성공!")
    
    return len(failed_endpoints) == 0

def test_data_files():
    """데이터 파일 존재 확인"""
    print(f"\n🔍 데이터 파일 확인")
    print("=" * 50)
    
    required_files = [
        "model/vectorizer.pkl",
        "model/indexed_matrix.pkl", 
        "model/raw_data.pkl",
        "requirements.txt",
        "app.py"
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"✅ {file_path}: 존재 ({file_size} bytes)")
        else:
            print(f"❌ {file_path}: 없음")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️ 누락된 파일: {', '.join(missing_files)}")
    else:
        print(f"\n🎉 모든 필수 파일 존재!")
    
    return len(missing_files) == 0

def test_directory_structure():
    """디렉토리 구조 확인"""
    print(f"\n🔍 디렉토리 구조 확인")
    print("=" * 50)
    
    required_dirs = [
        "templates",
        "model",
        "data",
        "advanced_labels",
        "generated_documents",
        "uploaded_labels"
    ]
    
    missing_dirs = []
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            file_count = len(os.listdir(dir_path))
            print(f"✅ {dir_path}/: 존재 ({file_count}개 파일)")
        else:
            print(f"❌ {dir_path}/: 없음")
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"\n⚠️ 누락된 디렉토리: {', '.join(missing_dirs)}")
    else:
        print(f"\n🎉 모든 필수 디렉토리 존재!")
    
    return len(missing_dirs) == 0

def test_ai_model_loading():
    """AI 모델 로드 테스트"""
    print(f"\n🔍 AI 모델 로드 테스트")
    print("=" * 50)
    
    try:
        # 통관분석 모델 로드 테스트
        import pickle
        with open('model/vectorizer.pkl', 'rb') as f:
            vectorizer = pickle.load(f)
        print("✅ TF-IDF 벡터라이저 로드 성공")
        
        with open('model/indexed_matrix.pkl', 'rb') as f:
            indexed_matrix = pickle.load(f)
        print("✅ 인덱스 매트릭스 로드 성공")
        
        with open('model/raw_data.pkl', 'rb') as f:
            raw_data = pickle.load(f)
        print(f"✅ 원본 데이터 로드 성공 ({len(raw_data)}개 레코드)")
        
        return True
        
    except Exception as e:
        print(f"❌ AI 모델 로드 실패: {e}")
        return False

def generate_comprehensive_report():
    """종합 보고서 생성"""
    print(f"\n📊 시스템 종합 검증 보고서")
    print("=" * 60)
    print(f"검증 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 각 테스트 실행
    tests = [
        ("핵심 모듈 로드", test_module_imports),
        ("커스텀 모듈 로드", test_custom_modules),
        ("OCR 기능", test_ocr_functionality),
        ("PDF 생성", test_pdf_generation),
        ("웹 API 엔드포인트", test_web_api_endpoints),
        ("데이터 파일", test_data_files),
        ("디렉토리 구조", test_directory_structure),
        ("AI 모델 로드", test_ai_model_loading)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} 테스트 중 오류: {e}")
            results[test_name] = False
    
    # 결과 요약
    print(f"\n📋 검증 결과 요약")
    print("-" * 40)
    
    passed_tests = sum(results.values())
    total_tests = len(results)
    
    for test_name, result in results.items():
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{test_name}: {status}")
    
    print(f"\n🎯 전체 결과: {passed_tests}/{total_tests} 통과")
    
    if passed_tests == total_tests:
        print("🎉 모든 테스트 통과! 시스템이 정상적으로 작동합니다.")
        return True
    else:
        print("⚠️ 일부 테스트 실패. 시스템 점검이 필요합니다.")
        return False

if __name__ == "__main__":
    generate_comprehensive_report() 