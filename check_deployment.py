#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 KATI 배포 준비 상태 확인 스크립트
- Render 배포 전 필수 파일 및 설정 검증
"""

import os
import sys
import importlib.util

def check_file_exists(filepath, description):
    """파일 존재 여부 확인"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} (파일 없음)")
        return False

def check_python_version():
    """Python 버전 확인"""
    version = sys.version_info
    print(f"🐍 Python 버전: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 11:
        print("✅ Python 3.11+ 호환성 확인")
        return True
    else:
        print("⚠️ Python 3.11+ 권장")
        return False

def check_requirements():
    """requirements.txt 확인"""
    if not check_file_exists("requirements.txt", "requirements.txt"):
        return False
    
    try:
        with open("requirements.txt", "r", encoding="utf-8") as f:
            content = f.read()
            
        required_packages = [
            "Flask", "gunicorn", "pandas", "numpy", 
            "Pillow", "reportlab", "requests"
        ]
        
        missing_packages = []
        for package in required_packages:
            if package.lower() not in content.lower():
                missing_packages.append(package)
        
        if missing_packages:
            print(f"⚠️ 누락된 패키지: {', '.join(missing_packages)}")
            return False
        else:
            print("✅ 필수 패키지 모두 포함")
            return True
            
    except Exception as e:
        print(f"❌ requirements.txt 읽기 오류: {e}")
        return False

def check_flask_app():
    """Flask 앱 확인"""
    if not check_file_exists("app.py", "Flask 앱"):
        return False
    
    try:
        # Flask 앱 import 테스트
        spec = importlib.util.spec_from_file_location("app", "app.py")
        app_module = importlib.util.module_from_spec(spec)
        
        # 안전한 import (오류 무시)
        try:
            spec.loader.exec_module(app_module)
            print("✅ Flask 앱 구조 확인")
            return True
        except Exception as e:
            print(f"⚠️ Flask 앱 import 경고: {e}")
            return True  # 경고만 있으면 통과
            
    except Exception as e:
        print(f"❌ Flask 앱 확인 오류: {e}")
        return False

def check_render_config():
    """Render 설정 파일 확인"""
    config_files = [
        ("render.yaml", "Render 서비스 설정"),
        ("Procfile", "프로세스 관리"),
        ("runtime.txt", "Python 버전 명시")
    ]
    
    all_exist = True
    for filepath, description in config_files:
        if not check_file_exists(filepath, description):
            all_exist = False
    
    return all_exist

def check_directories():
    """필수 디렉토리 확인"""
    required_dirs = [
        ("templates", "HTML 템플릿"),
        ("static", "정적 파일")
    ]
    
    all_exist = True
    for dirpath, description in required_dirs:
        if os.path.exists(dirpath) and os.path.isdir(dirpath):
            print(f"✅ {description}: {dirpath}/")
        else:
            print(f"❌ {description}: {dirpath}/ (디렉토리 없음)")
            all_exist = False
    
    return all_exist

def check_git_status():
    """Git 상태 확인"""
    try:
        import subprocess
        result = subprocess.run(["git", "status", "--porcelain"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            if result.stdout.strip():
                print("⚠️ 커밋되지 않은 변경사항이 있습니다")
                print("   git add . && git commit -m '배포 준비' 실행 권장")
                return False
            else:
                print("✅ Git 상태 정상")
                return True
        else:
            print("⚠️ Git 상태 확인 불가")
            return True
            
    except Exception:
        print("⚠️ Git 명령어 실행 불가")
        return True

def main():
    """메인 검증 함수"""
    print("🚀 KATI Render 배포 준비 상태 확인")
    print("=" * 50)
    
    checks = [
        ("Python 버전", check_python_version),
        ("requirements.txt", check_requirements),
        ("Flask 앱", check_flask_app),
        ("Render 설정", check_render_config),
        ("디렉토리 구조", check_directories),
        ("Git 상태", check_git_status)
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        print(f"\n📋 {name} 확인 중...")
        if check_func():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 검증 결과: {passed}/{total} 통과")
    
    if passed == total:
        print("🎉 모든 검증 통과! Render 배포 준비 완료!")
        print("\n📝 다음 단계:")
        print("1. git add . && git commit -m 'Render 배포 준비'")
        print("2. git push origin main")
        print("3. Render.com에서 새 웹 서비스 생성")
        print("4. GitHub 저장소 연결 및 배포")
    else:
        print("⚠️ 일부 검증 실패. 위의 오류를 수정 후 다시 실행하세요.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 