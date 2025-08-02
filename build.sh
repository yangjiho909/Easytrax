#!/bin/bash

# 🚀 KATI 배포 빌드 스크립트 (중국어 폰트 지원)

echo "🔧 KATI 배포 환경 설정 시작..."

# 시스템 업데이트
echo "📦 시스템 패키지 업데이트..."
sudo apt-get update

# 중국어 폰트 설치
echo "🇨🇳 중국어 폰트 설치..."
sudo apt-get install -y fonts-noto-cjk fonts-noto-cjk-extra

# 폰트 캐시 업데이트
echo "🔄 폰트 캐시 업데이트..."
sudo fc-cache -fv

# Python 패키지 설치
echo "🐍 Python 패키지 설치..."
pip install -r requirements.txt

# 폰트 설치 확인
echo "✅ 폰트 설치 확인..."
fc-list | grep -i "noto.*cjk" | head -5

echo "🎉 빌드 완료!"
echo "📋 설치된 폰트:"
echo "   - Noto Sans CJK (중국어, 일본어, 한국어)"
echo "   - Noto Sans SC (중국어 간체)"
echo "   - 프로젝트 내 폰트 (msyh.ttc, simsun.ttc)" 