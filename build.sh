#!/bin/bash
set -e

echo "🚀 KATI 배포 빌드 시작 (안정적 빌드)"

# Python 버전 확인
python --version

# pip 업그레이드
echo "📦 pip 업그레이드 중..."
pip install --upgrade pip

# 기본 패키지들 먼저 설치
echo "📦 기본 패키지 설치 중..."
pip install Flask==2.3.3 gunicorn==21.2.0 flask-cors==4.0.0

# 데이터 처리 패키지 설치
echo "📦 데이터 처리 패키지 설치 중..."
pip install pandas==2.0.3 numpy==1.24.3 openpyxl==3.1.2

# 웹 크롤링 패키지 설치
echo "📦 웹 크롤링 패키지 설치 중..."
pip install beautifulsoup4==4.12.2 requests==2.31.0

# 이미지 처리 패키지 설치
echo "📦 이미지 처리 패키지 설치 중..."
pip install Pillow==10.0.0 qrcode==7.4.2

# PDF 처리 패키지 설치
echo "📦 PDF 처리 패키지 설치 중..."
pip install reportlab==4.0.4 PyPDF2==3.0.1 fpdf2==2.7.6

# OCR 패키지 설치
echo "📦 OCR 패키지 설치 중..."
pip install pytesseract==0.3.10 opencv-python-headless==4.8.1.78

# 머신러닝 패키지 설치
echo "📦 머신러닝 패키지 설치 중..."
pip install scikit-learn==1.3.0

# 한국어 처리 패키지 설치
echo "📦 한국어 처리 패키지 설치 중..."
pip install soynlp==0.0.493

# 문서 처리 패키지 설치
echo "📦 문서 처리 패키지 설치 중..."
pip install python-docx==0.8.11 PyMuPDF==1.23.8

# 데이터베이스 패키지 설치
echo "📦 데이터베이스 패키지 설치 중..."
pip install psycopg2-binary==2.9.7

# 스케줄링 패키지 설치
echo "📦 스케줄링 패키지 설치 중..."
pip install schedule==1.2.0

# AI 라이브러리들 설치 (단계별)
echo "📦 AI 라이브러리 설치 중..."
pip install transformers==4.35.2
pip install torch==2.1.1+cpu
pip install spacy==3.7.2
pip install easyocr==1.7.0

# PaddlePaddle 설치
echo "📦 PaddlePaddle 설치 중..."
pip install paddlepaddle==2.5.2
pip install paddleocr==2.7.0.3

# 클라우드 서비스 설치
echo "📦 클라우드 서비스 설치 중..."
pip install google-cloud-vision==3.4.4
pip install google-cloud-storage==2.10.0
pip install azure-cognitiveservices-vision-computervision==0.9.0
pip install azure-storage-blob==12.19.0

# 이미지 전처리 설치
echo "📦 이미지 전처리 설치 중..."
pip install scikit-image==0.21.0
pip install imgaug==0.4.0
pip install albumentations==1.3.1

# 과학 계산 설치
echo "📦 과학 계산 설치 중..."
pip install scipy==1.11.1

# 무료 AI API 설치
echo "📦 무료 AI API 설치 중..."
pip install huggingface-hub==0.19.4

# 디렉토리 확인
echo "📁 디렉토리 확인 중..."
if [ -d "model" ]; then
    echo "✅ 모델 디렉토리 확인됨"
else
    echo "⚠️ 모델 디렉토리가 없습니다"
fi

if [ -d "templates" ]; then
    echo "✅ 템플릿 디렉토리 확인됨"
else
    echo "⚠️ 템플릿 디렉토리가 없습니다"
fi

if [ -d "static" ]; then
    echo "✅ 정적 파일 디렉토리 확인됨"
else
    echo "⚠️ 정적 파일 디렉토리가 없습니다"
fi

echo "✅ 모든 패키지 설치 완료!"
echo "📋 설치된 패키지 목록:"
pip list

echo "🎉 빌드 완료! 모든 기능 준비됨" 