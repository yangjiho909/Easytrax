#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 OCR이 포함된 준수성 분석 테스트
"""

import requests
import os
import json

def test_compliance_with_ocr():
    """OCR이 포함된 준수성 분석 테스트"""
    print("🧪 OCR이 포함된 준수성 분석 테스트")
    print("=" * 50)
    
    # 테스트 이미지 경로
    test_image = "mvp_nutrition_labels/mvp_nutrition_label_korean_20250727_134704.png"
    
    if not os.path.exists(test_image):
        print(f"❌ 테스트 이미지가 없습니다: {test_image}")
        return False
    
    try:
        url = "http://localhost:5000/api/compliance-analysis"
        
        # Form-data로 파일 업로드와 함께 요청
        with open(test_image, 'rb') as f:
            files = {
                'labelFile': ('test_label.png', f, 'image/png')
            }
            
            data = {
                'country': '중국',
                'product_type': '라면',
                'use_ocr': 'true',
                'company_info': json.dumps({
                    'name': '테스트회사',
                    'address': '서울시 강남구'
                }),
                'product_info': json.dumps({
                    'name': '테스트라면',
                    'weight': '120g'
                }),
                'uploaded_documents': json.dumps([]),
                'prepared_documents': json.dumps([]),
                'labeling_info': json.dumps({})
            }
            
            print("📤 OCR 포함 준수성 분석 요청 전송 중...")
            response = requests.post(url, files=files, data=data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ OCR 포함 준수성 분석 성공!")
                
                # 분석 결과 확인
                analysis_summary = result.get('analysis_summary', {})
                print(f"📊 분석된 문서: {analysis_summary.get('analyzed_documents', [])}")
                print(f"📊 준수성 점수: {analysis_summary.get('compliance_score', 0)}점")
                print(f"📊 총 문서 수: {analysis_summary.get('total_documents', 0)}개")
                
                # OCR 결과 확인
                ocr_results = result.get('ocr_results', {})
                if ocr_results:
                    print("🔍 OCR 분석 결과:")
                    for doc_type, ocr_result in ocr_results.items():
                        if 'error' not in ocr_result:
                            text_content = ocr_result.get('text_content', [])
                            if text_content:
                                print(f"  - {doc_type}: {len(text_content)}개 텍스트 블록")
                            else:
                                print(f"  - {doc_type}: 텍스트 추출 실패")
                        else:
                            print(f"  - {doc_type}: OCR 오류 - {ocr_result['error']}")
                
                # 구조화된 데이터 확인
                structured_data = result.get('structured_data', {})
                if structured_data:
                    print("📋 구조화된 데이터:")
                    for doc_type, data in structured_data.items():
                        extracted_text = data.get('extracted_text', [])
                        print(f"  - {doc_type}: {len(extracted_text)}개 텍스트")
                
                # 규제 매칭 확인
                regulation_matching = result.get('regulation_matching', {})
                if regulation_matching:
                    print("📋 규제 매칭 결과:")
                    for category, info in regulation_matching.items():
                        if isinstance(info, dict) and 'regulation' in info:
                            print(f"  - {category}: {info['regulation']}")
                
                return True
            else:
                print(f"❌ 준수성 분석 실패: {result.get('error', '알 수 없는 오류')}")
                return False
        else:
            print(f"❌ API 오류: {response.status_code}")
            print(f"응답: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        return False

def test_compliance_without_ocr():
    """OCR 없이 기본 준수성 분석 테스트"""
    print("\n🧪 OCR 없이 기본 준수성 분석 테스트")
    print("=" * 50)
    
    try:
        url = "http://localhost:5000/api/compliance-analysis"
        
        data = {
            'country': '중국',
            'product_type': '라면',
            'use_ocr': 'false',
            'company_info': json.dumps({
                'name': '테스트회사',
                'address': '서울시 강남구'
            }),
            'product_info': json.dumps({
                'name': '테스트라면',
                'weight': '120g'
            }),
            'uploaded_documents': json.dumps([]),
            'prepared_documents': json.dumps([]),
            'labeling_info': json.dumps({})
        }
        
        print("📤 기본 준수성 분석 요청 전송 중...")
        response = requests.post(url, data=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 기본 준수성 분석 성공!")
                
                analysis_summary = result.get('analysis_summary', {})
                print(f"📊 준수성 점수: {analysis_summary.get('compliance_score', 0)}점")
                print(f"📊 총 문서 수: {analysis_summary.get('total_documents', 0)}개")
                
                return True
            else:
                print(f"❌ 기본 분석 실패: {result.get('error', '알 수 없는 오류')}")
                return False
        else:
            print(f"❌ API 오류: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("🚀 준수성 분석 OCR 통합 테스트 시작")
    print("=" * 60)
    
    # 1. OCR 없이 기본 분석
    basic_success = test_compliance_without_ocr()
    
    # 2. OCR 포함 분석
    ocr_success = test_compliance_with_ocr()
    
    print("\n" + "=" * 60)
    print("🏁 테스트 완료")
    
    if basic_success and ocr_success:
        print("✅ OCR이 준수성 분석에 정상적으로 통합되어 작동합니다!")
        print("📋 OCR 기능:")
        print("  - 이미지 파일 업로드 및 텍스트 추출")
        print("  - 구조화된 데이터 변환")
        print("  - 규제 정보와 매칭")
        print("  - 준수성 점수 계산")
    elif basic_success:
        print("⚠️ 기본 분석은 작동하지만 OCR 통합에 문제가 있습니다.")
    else:
        print("❌ 준수성 분석에 문제가 있습니다.")

if __name__ == "__main__":
    main() 