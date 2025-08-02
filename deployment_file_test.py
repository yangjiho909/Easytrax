#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
배포 환경 파일 시스템 진단 도구
로컬과 배포 환경의 차이점을 분석하고 파일 생성/다운로드 문제를 진단합니다.
"""

import os
import sys
import tempfile
import shutil
import platform
from datetime import datetime
from pathlib import Path

def check_environment_info():
    """환경 정보 확인"""
    print("🔍 환경 정보 확인")
    print("=" * 50)
    
    # 기본 환경 정보
    print(f"Python 버전: {sys.version}")
    print(f"플랫폼: {platform.platform()}")
    print(f"현재 작업 디렉토리: {os.getcwd()}")
    print(f"사용자: {os.getenv('USER', 'Unknown')}")
    
    # 배포 환경 감지
    is_render = os.environ.get('RENDER') is not None
    is_heroku = os.environ.get('IS_HEROKU', False)
    is_railway = os.environ.get('IS_RAILWAY', False)
    is_cloud = is_render or is_heroku or is_railway
    
    print(f"Render 환경: {is_render}")
    print(f"Heroku 환경: {is_heroku}")
    print(f"Railway 환경: {is_railway}")
    print(f"클라우드 환경: {is_cloud}")
    
    # 환경 변수 확인
    print(f"FLASK_ENV: {os.environ.get('FLASK_ENV', 'Not set')}")
    print(f"PORT: {os.environ.get('PORT', 'Not set')}")
    print(f"PYTHON_VERSION: {os.environ.get('PYTHON_VERSION', 'Not set')}")
    
    return {
        'is_cloud': is_cloud,
        'is_render': is_render,
        'platform': platform.platform(),
        'python_version': sys.version
    }

def check_file_system_permissions():
    """파일 시스템 권한 확인"""
    print("\n🔐 파일 시스템 권한 확인")
    print("=" * 50)
    
    # 필요한 디렉토리 목록
    required_dirs = [
        'generated_documents',
        'uploaded_documents', 
        'uploaded_labels',
        'advanced_labels',
        'temp_uploads',
        'regulation_cache',
        'public_data_cache'
    ]
    
    permissions = {}
    
    for dir_name in required_dirs:
        try:
            # 디렉토리 생성 시도
            os.makedirs(dir_name, exist_ok=True)
            
            # 권한 확인
            if os.path.exists(dir_name):
                # 읽기 권한 확인
                can_read = os.access(dir_name, os.R_OK)
                # 쓰기 권한 확인
                can_write = os.access(dir_name, os.W_OK)
                # 실행 권한 확인
                can_execute = os.access(dir_name, os.X_OK)
                
                permissions[dir_name] = {
                    'exists': True,
                    'can_read': can_read,
                    'can_write': can_write,
                    'can_execute': can_execute,
                    'path': os.path.abspath(dir_name)
                }
                
                print(f"✅ {dir_name}: 읽기={can_read}, 쓰기={can_write}, 실행={can_execute}")
            else:
                permissions[dir_name] = {
                    'exists': False,
                    'error': '디렉토리 생성 실패'
                }
                print(f"❌ {dir_name}: 생성 실패")
                
        except Exception as e:
            permissions[dir_name] = {
                'exists': False,
                'error': str(e)
            }
            print(f"❌ {dir_name}: 오류 - {str(e)}")
    
    return permissions

def test_file_creation():
    """파일 생성 테스트"""
    print("\n📄 파일 생성 테스트")
    print("=" * 50)
    
    test_results = {}
    
    # 1. 텍스트 파일 생성 테스트
    try:
        test_file = "test_creation.txt"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("테스트 파일 생성 테스트\n")
            f.write(f"생성 시간: {datetime.now()}\n")
        
        if os.path.exists(test_file):
            size = os.path.getsize(test_file)
            test_results['text_file'] = {
                'success': True,
                'size': size,
                'path': os.path.abspath(test_file)
            }
            print(f"✅ 텍스트 파일 생성 성공: {test_file} ({size} bytes)")
            
            # 파일 삭제
            os.remove(test_file)
            print(f"✅ 테스트 파일 삭제 완료")
        else:
            test_results['text_file'] = {'success': False, 'error': '파일이 생성되지 않음'}
            print(f"❌ 텍스트 파일 생성 실패")
            
    except Exception as e:
        test_results['text_file'] = {'success': False, 'error': str(e)}
        print(f"❌ 텍스트 파일 생성 오류: {str(e)}")
    
    # 2. generated_documents 폴더에 파일 생성 테스트
    try:
        os.makedirs('generated_documents', exist_ok=True)
        test_pdf = os.path.join('generated_documents', 'test_document.pdf')
        
        # 간단한 PDF 생성 (텍스트로 대체)
        with open(test_pdf, 'w', encoding='utf-8') as f:
            f.write("%PDF-1.4\n")
            f.write("1 0 obj\n")
            f.write("<<\n")
            f.write("/Type /Catalog\n")
            f.write("/Pages 2 0 R\n")
            f.write(">>\n")
            f.write("endobj\n")
            f.write("2 0 obj\n")
            f.write("<<\n")
            f.write("/Type /Pages\n")
            f.write("/Kids [3 0 R]\n")
            f.write("/Count 1\n")
            f.write(">>\n")
            f.write("endobj\n")
            f.write("3 0 obj\n")
            f.write("<<\n")
            f.write("/Type /Page\n")
            f.write("/Parent 2 0 R\n")
            f.write("/MediaBox [0 0 612 792]\n")
            f.write("/Contents 4 0 R\n")
            f.write(">>\n")
            f.write("endobj\n")
            f.write("4 0 obj\n")
            f.write("<<\n")
            f.write("/Length 44\n")
            f.write(">>\n")
            f.write("stream\n")
            f.write("BT\n")
            f.write("/F1 12 Tf\n")
            f.write("72 720 Td\n")
            f.write("(Test Document) Tj\n")
            f.write("ET\n")
            f.write("endstream\n")
            f.write("endobj\n")
            f.write("xref\n")
            f.write("0 5\n")
            f.write("0000000000 65535 f \n")
            f.write("0000000009 00000 n \n")
            f.write("0000000058 00000 n \n")
            f.write("0000000115 00000 n \n")
            f.write("0000000204 00000 n \n")
            f.write("trailer\n")
            f.write("<<\n")
            f.write("/Size 5\n")
            f.write("/Root 1 0 R\n")
            f.write(">>\n")
            f.write("startxref\n")
            f.write("273\n")
            f.write("%%EOF\n")
        
        if os.path.exists(test_pdf):
            size = os.path.getsize(test_pdf)
            test_results['pdf_file'] = {
                'success': True,
                'size': size,
                'path': os.path.abspath(test_pdf)
            }
            print(f"✅ PDF 파일 생성 성공: {test_pdf} ({size} bytes)")
        else:
            test_results['pdf_file'] = {'success': False, 'error': 'PDF 파일이 생성되지 않음'}
            print(f"❌ PDF 파일 생성 실패")
            
    except Exception as e:
        test_results['pdf_file'] = {'success': False, 'error': str(e)}
        print(f"❌ PDF 파일 생성 오류: {str(e)}")
    
    # 3. 임시 파일 생성 테스트
    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("임시 파일 테스트\n")
            temp_path = f.name
        
        if os.path.exists(temp_path):
            size = os.path.getsize(temp_path)
            test_results['temp_file'] = {
                'success': True,
                'size': size,
                'path': temp_path
            }
            print(f"✅ 임시 파일 생성 성공: {temp_path} ({size} bytes)")
            
            # 임시 파일 삭제
            os.unlink(temp_path)
            print(f"✅ 임시 파일 삭제 완료")
        else:
            test_results['temp_file'] = {'success': False, 'error': '임시 파일이 생성되지 않음'}
            print(f"❌ 임시 파일 생성 실패")
            
    except Exception as e:
        test_results['temp_file'] = {'success': False, 'error': str(e)}
        print(f"❌ 임시 파일 생성 오류: {str(e)}")
    
    return test_results

def check_disk_space():
    """디스크 공간 확인"""
    print("\n💾 디스크 공간 확인")
    print("=" * 50)
    
    try:
        import shutil
        
        # 현재 디렉토리의 디스크 사용량 확인
        total, used, free = shutil.disk_usage('.')
        
        # 바이트를 MB로 변환
        total_mb = total // (1024 * 1024)
        used_mb = used // (1024 * 1024)
        free_mb = free // (1024 * 1024)
        
        print(f"전체 디스크: {total_mb} MB")
        print(f"사용 중: {used_mb} MB")
        print(f"사용 가능: {free_mb} MB")
        print(f"사용률: {(used / total) * 100:.1f}%")
        
        return {
            'total_mb': total_mb,
            'used_mb': used_mb,
            'free_mb': free_mb,
            'usage_percent': (used / total) * 100
        }
        
    except Exception as e:
        print(f"❌ 디스크 공간 확인 오류: {str(e)}")
        return {'error': str(e)}

def check_pdf_libraries():
    """PDF 라이브러리 확인"""
    print("\n📚 PDF 라이브러리 확인")
    print("=" * 50)
    
    libraries = {}
    
    # ReportLab 확인
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        libraries['reportlab'] = {'available': True, 'version': 'Available'}
        print("✅ ReportLab: 사용 가능")
    except ImportError as e:
        libraries['reportlab'] = {'available': False, 'error': str(e)}
        print(f"❌ ReportLab: {str(e)}")
    
    # PyMuPDF (fitz) 확인
    try:
        import fitz
        libraries['pymupdf'] = {'available': True, 'version': fitz.version}
        print(f"✅ PyMuPDF: {fitz.version}")
    except ImportError as e:
        libraries['pymupdf'] = {'available': False, 'error': str(e)}
        print(f"❌ PyMuPDF: {str(e)}")
    
    # PyPDF2 확인
    try:
        import PyPDF2
        libraries['pypdf2'] = {'available': True, 'version': PyPDF2.__version__}
        print(f"✅ PyPDF2: {PyPDF2.__version__}")
    except ImportError as e:
        libraries['pypdf2'] = {'available': False, 'error': str(e)}
        print(f"❌ PyPDF2: {str(e)}")
    
    # Pillow (이미지 처리) 확인
    try:
        from PIL import Image, ImageDraw, ImageFont
        libraries['pillow'] = {'available': True, 'version': 'Available'}
        print("✅ Pillow: 사용 가능")
    except ImportError as e:
        libraries['pillow'] = {'available': False, 'error': str(e)}
        print(f"❌ Pillow: {str(e)}")
    
    return libraries

def generate_diagnostic_report():
    """진단 보고서 생성"""
    print("\n📋 배포 환경 파일 시스템 진단 보고서")
    print("=" * 60)
    
    # 모든 진단 실행
    env_info = check_environment_info()
    permissions = check_file_system_permissions()
    file_tests = test_file_creation()
    disk_info = check_disk_space()
    pdf_libs = check_pdf_libraries()
    
    # 결과 요약
    print("\n🎯 진단 결과 요약")
    print("=" * 60)
    
    # 환경별 문제점 분석
    if env_info['is_cloud']:
        print("🌐 클라우드 환경 감지됨")
        print("⚠️  클라우드 환경에서는 파일 시스템이 임시적일 수 있습니다")
        print("⚠️  서버 재시작 시 생성된 파일이 삭제될 수 있습니다")
    
    # 권한 문제 확인
    permission_issues = []
    for dir_name, perm in permissions.items():
        if not perm.get('exists', False) or not perm.get('can_write', False):
            permission_issues.append(dir_name)
    
    if permission_issues:
        print(f"❌ 권한 문제 발견: {', '.join(permission_issues)}")
    else:
        print("✅ 모든 디렉토리 권한 정상")
    
    # 파일 생성 문제 확인
    file_creation_issues = []
    for test_name, result in file_tests.items():
        if not result.get('success', False):
            file_creation_issues.append(test_name)
    
    if file_creation_issues:
        print(f"❌ 파일 생성 문제 발견: {', '.join(file_creation_issues)}")
    else:
        print("✅ 모든 파일 생성 테스트 통과")
    
    # PDF 라이브러리 문제 확인
    pdf_lib_issues = []
    for lib_name, lib_info in pdf_libs.items():
        if not lib_info.get('available', False):
            pdf_lib_issues.append(lib_name)
    
    if pdf_lib_issues:
        print(f"❌ PDF 라이브러리 문제: {', '.join(pdf_lib_issues)}")
    else:
        print("✅ 모든 PDF 라이브러리 사용 가능")
    
    # 디스크 공간 확인
    if disk_info.get('free_mb', 0) < 100:
        print(f"⚠️  디스크 공간 부족: {disk_info.get('free_mb', 0)} MB")
    else:
        print(f"✅ 디스크 공간 충분: {disk_info.get('free_mb', 0)} MB")
    
    # 해결 방안 제시
    print("\n🔧 해결 방안")
    print("=" * 60)
    
    if env_info['is_cloud']:
        print("1. 클라우드 환경 대응:")
        print("   - 외부 저장소 (S3, Cloud Storage) 사용 고려")
        print("   - 파일을 데이터베이스에 저장하는 방식 고려")
        print("   - 임시 파일 생성 후 즉시 다운로드 제공")
    
    if permission_issues:
        print("2. 권한 문제 해결:")
        print("   - 애플리케이션 시작 시 필요한 디렉토리 생성")
        print("   - 파일 생성 전 디렉토리 존재 여부 확인")
        print("   - 오류 발생 시 대체 경로 사용")
    
    if pdf_lib_issues:
        print("3. PDF 라이브러리 문제 해결:")
        print("   - requirements.txt에 필요한 라이브러리 추가")
        print("   - 배포 환경에서 라이브러리 설치 확인")
        print("   - 대체 PDF 생성 방식 구현")
    
    # 상세 보고서를 파일로 저장
    report_file = f"deployment_diagnostic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("배포 환경 파일 시스템 진단 보고서\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("환경 정보:\n")
            for key, value in env_info.items():
                f.write(f"  {key}: {value}\n")
            f.write("\n")
            
            f.write("권한 정보:\n")
            for dir_name, perm in permissions.items():
                f.write(f"  {dir_name}: {perm}\n")
            f.write("\n")
            
            f.write("파일 생성 테스트:\n")
            for test_name, result in file_tests.items():
                f.write(f"  {test_name}: {result}\n")
            f.write("\n")
            
            f.write("디스크 정보:\n")
            f.write(f"  {disk_info}\n\n")
            
            f.write("PDF 라이브러리:\n")
            for lib_name, lib_info in pdf_libs.items():
                f.write(f"  {lib_name}: {lib_info}\n")
        
        print(f"📄 상세 보고서 저장됨: {report_file}")
        
    except Exception as e:
        print(f"❌ 보고서 저장 실패: {str(e)}")

if __name__ == "__main__":
    generate_diagnostic_report() 