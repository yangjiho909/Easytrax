#!/bin/bash
set -e

echo "🚀 KATI 배포 빌드 시작 (모든 기능 유지)"

# Python 버전 확인
python --version

# pip 업그레이드
pip install --upgrade pip

# 캐시 클리어
pip cache purge

# 기본 의존성 설치 (캐시 없이)
echo "📦 모든 의존성 설치 중..."
pip install --no-cache-dir -r requirements.txt

# 모델 파일 확인
if [ -d "model" ]; then
    echo "✅ 모델 디렉토리 확인됨"
else
    echo "⚠️ 모델 디렉토리가 없습니다"
fi

# 템플릿 디렉토리 확인
if [ -d "templates" ]; then
    echo "✅ 템플릿 디렉토리 확인됨"
else
    echo "⚠️ 템플릿 디렉토리가 없습니다"
fi

# 정적 파일 디렉토리 확인
if [ -d "static" ]; then
    echo "✅ 정적 파일 디렉토리 확인됨"
else
    echo "⚠️ 정적 파일 디렉토리가 없습니다"
fi

# 설치된 패키지 확인
echo "📋 설치된 패키지 목록:"
pip list

echo "✅ 빌드 완료! 모든 기능 준비됨" 