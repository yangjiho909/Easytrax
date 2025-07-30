#!/bin/bash
set -e

echo "🚀 KATI 배포 빌드 시작..."

# Python 버전 확인
python --version

# pip 업그레이드
pip install --upgrade pip

# 기본 의존성 설치
echo "📦 기본 의존성 설치 중..."
pip install -r requirements.txt

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

echo "✅ 빌드 완료!" 