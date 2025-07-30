#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF 양식 분석 및 생성 시스템 전체 프로세스 테스트
"""

import os
import sys
import json
from datetime import datetime

def test_system_components():
    """시스템 컴포넌트 테스트"""
    print("🔍 시스템 컴포넌트 테스트 시작...")
    
    # 1. 필수 라이브러리 확인
    print("\n1️⃣ 필수 라이브러리 확인:")
    try:
        import fitz
        print(f"   ✅ PyMuPDF: {fitz.version}")
    except ImportError as e:
        print(f"   ❌ PyMuPDF: {e}")
        return False
    
    try:
        import cv2
        print(f"   ✅ OpenCV: {cv2.__version__}")
    except ImportError as e:
        print(f"   ❌ OpenCV: {e}")
    
    try:
        import numpy as np
        print(f"   ✅ NumPy: {np.__version__}")
    except ImportError as e:
        print(f"   ❌ NumPy: {e}")
    
    # 2. 커스텀 모듈 확인
    print("\n2️⃣ 커스텀 모듈 확인:")
    try:
        from pdf_form_analyzer import pdf_form_analyzer
        print("   ✅ PDF 양식 분석기 로드 성공")
    except ImportError as e:
        print(f"   ❌ PDF 양식 분석기: {e}")
        return False
    
    try:
        from pdf_generator import pdf_generator
        print("   ✅ PDF 생성기 로드 성공")
    except ImportError as e:
        print(f"   ❌ PDF 생성기: {e}")
        return False
    
    return True

def test_template_files():
    """템플릿 파일 확인"""
    print("\n3️⃣ 템플릿 파일 확인:")
    
    template_dir = "uploaded_templates"
    if not os.path.exists(template_dir):
        print(f"   ❌ 템플릿 디렉토리 없음: {template_dir}")
        return []
    
    templates = []
    for filename in os.listdir(template_dir):
        if filename.lower().endswith('.pdf'):
            file_path = os.path.join(template_dir, filename)
            file_size = os.path.getsize(file_path)
            templates.append({
                'filename': filename,
                'path': file_path,
                'size': file_size,
                'size_mb': round(file_size / (1024 * 1024), 2)
            })
            print(f"   ✅ {filename} ({file_size} bytes, {round(file_size / (1024 * 1024), 2)} MB)")
    
    if not templates:
        print("   ❌ PDF 템플릿 파일 없음")
    
    return templates

def test_pdf_analysis(template_path):
    """PDF 양식 분석 테스트"""
    print(f"\n4️⃣ PDF 양식 분석 테스트: {os.path.basename(template_path)}")
    
    try:
        from pdf_form_analyzer import pdf_form_analyzer
        
        # PDF 양식 분석
        print("   🔍 PDF 양식 분석 중...")
        template = pdf_form_analyzer.analyze_pdf_form(template_path)
        
        print(f"   ✅ 분석 완료:")
        print(f"      - 템플릿 ID: {template.template_id}")
        print(f"      - 템플릿명: {template.template_name}")
        print(f"      - 페이지 수: {template.pages}")
        print(f"      - 필드 수: {len(template.fields)}")
        
        # 필드 유형별 분포
        field_types = {}
        for field in template.fields:
            field_types[field.field_type] = field_types.get(field.field_type, 0) + 1
        
        print("      - 필드 유형별 분포:")
        for field_type, count in field_types.items():
            print(f"        * {field_type}: {count}개")
        
        # 입력폼 생성
        print("   📝 입력폼 생성 중...")
        form_data = pdf_form_analyzer.generate_input_form(template)
        
        print(f"   ✅ 입력폼 생성 완료:")
        print(f"      - 총 필드: {len(form_data['fields'])}개")
        
        return template, form_data
        
    except Exception as e:
        print(f"   ❌ PDF 분석 실패: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def test_pdf_generation(template_path, form_data, test_input):
    """PDF 생성 테스트"""
    print(f"\n5️⃣ PDF 생성 테스트: {os.path.basename(template_path)}")
    
    try:
        from pdf_generator import pdf_generator
        
        # 입력 데이터 검증
        print("   🔍 입력 데이터 검증 중...")
        from pdf_form_analyzer import pdf_form_analyzer
        validation_result = pdf_form_analyzer.validate_form_data(form_data, test_input)
        
        print(f"   ✅ 검증 결과:")
        print(f"      - 유효성: {validation_result['is_valid']}")
        print(f"      - 오류 수: {len(validation_result['errors'])}")
        print(f"      - 누락 필드: {len(validation_result['missing_fields'])}")
        
        if not validation_result['is_valid']:
            print("   ⚠️ 검증 실패, 테스트 입력 수정...")
            # 테스트 입력을 유효하게 수정
            for field in form_data['fields']:
                if field['required'] and field['field_id'] not in test_input:
                    if field['field_type'] == 'text':
                        test_input[field['field_id']] = f"테스트_{field['label']}"
                    elif field['field_type'] == 'checkbox':
                        test_input[field['field_id']] = 'checked'
                    elif field['field_type'] == 'signature':
                        test_input[field['field_id']] = '테스트 서명'
        
        # PDF 생성
        print("   📄 PDF 생성 중...")
        output_path = pdf_generator.generate_filled_pdf(template_path, form_data, test_input)
        
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"   ✅ PDF 생성 완료:")
            print(f"      - 출력 파일: {output_path}")
            print(f"      - 파일 크기: {file_size} bytes ({round(file_size / (1024 * 1024), 2)} MB)")
            
            # 미리보기 생성 테스트
            print("   🖼️ 미리보기 생성 중...")
            preview_image = pdf_generator.create_preview_image(output_path)
            if preview_image:
                print("   ✅ 미리보기 생성 완료")
            else:
                print("   ⚠️ 미리보기 생성 실패")
            
            return output_path
        else:
            print("   ❌ PDF 파일 생성 실패")
            return None
            
    except Exception as e:
        print(f"   ❌ PDF 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_complete_workflow():
    """전체 워크플로우 테스트"""
    print("\n🎯 전체 워크플로우 테스트 시작...")
    
    # 1. 시스템 컴포넌트 테스트
    if not test_system_components():
        print("❌ 시스템 컴포넌트 테스트 실패")
        return False
    
    # 2. 템플릿 파일 확인
    templates = test_template_files()
    if not templates:
        print("❌ 템플릿 파일 없음")
        return False
    
    # 3. 첫 번째 템플릿으로 전체 프로세스 테스트
    template = templates[0]
    print(f"\n📋 선택된 템플릿: {template['filename']}")
    
    # 4. PDF 양식 분석
    template_obj, form_data = test_pdf_analysis(template['path'])
    if not template_obj or not form_data:
        print("❌ PDF 양식 분석 실패")
        return False
    
    # 5. 테스트 입력 데이터 생성
    test_input = {}
    for field in form_data['fields'][:5]:  # 처음 5개 필드만 테스트
        if field['field_type'] == 'text':
            test_input[field['field_id']] = f"테스트_{field['label']}"
        elif field['field_type'] == 'checkbox':
            test_input[field['field_id']] = 'checked'
        elif field['field_type'] == 'signature':
            test_input[field['field_id']] = '테스트 서명'
        elif field['field_type'] == 'table':
            test_input[field['field_id']] = [['테스트 데이터']]
    
    print(f"   📝 테스트 입력 데이터: {len(test_input)}개 필드")
    
    # 6. PDF 생성
    output_path = test_pdf_generation(template['path'], form_data, test_input)
    
    if output_path:
        print(f"\n✅ 전체 워크플로우 테스트 성공!")
        print(f"   📄 생성된 PDF: {output_path}")
        return True
    else:
        print(f"\n❌ 전체 워크플로우 테스트 실패")
        return False

def main():
    """메인 함수"""
    print("🚀 PDF 양식 분석 및 생성 시스템 전체 프로세스 테스트")
    print("=" * 60)
    
    start_time = datetime.now()
    
    try:
        success = test_complete_workflow()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print("\n" + "=" * 60)
        print(f"⏱️ 테스트 완료 시간: {duration}")
        
        if success:
            print("🎉 모든 테스트가 성공적으로 완료되었습니다!")
            return 0
        else:
            print("❌ 일부 테스트가 실패했습니다.")
            return 1
            
    except Exception as e:
        print(f"\n💥 테스트 중 예상치 못한 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 