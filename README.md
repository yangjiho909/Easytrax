# 🚀 KATI 수출 지원 시스템

## 🌐 배포 상태
- **Render**: ✅ 배포 준비 완료
- **GitHub**: 자동 배포 파이프라인 구성 완료
- **배포 URL**: 배포 후 `https://kati-export-helper.onrender.com`

## 📋 주요 기능
- 통관 규정 분석 및 조회
- 영양성분표 자동 생성
- 문서 생성 (상업송장, 포장명세서)
- OCR 기반 문서 분석
- 실시간 규제 업데이트 모니터링
- 대시보드 분석 및 리포트

## 🚀 Render 배포 방법

### 1. GitHub 저장소 준비
```bash
# 현재 프로젝트를 GitHub에 푸시
git add .
git commit -m "Render 배포 준비 완료"
git push origin main
```

### 2. Render 계정 생성 및 연결
1. [Render.com](https://render.com)에 가입
2. GitHub 계정 연결
3. "New Web Service" 선택
4. GitHub 저장소 연결

### 3. 서비스 설정
- **Name**: `kati-export-helper`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`
- **Plan**: Free (무료 플랜)

### 4. 환경 변수 설정
- `FLASK_ENV`: `production`
- `PORT`: `10000`

## 🔧 기술 스택
- **Backend**: Flask, Python 3.11
- **Deployment**: Render
- **Process Manager**: Gunicorn
- **Monitoring**: Render Dashboard

## 📁 프로젝트 구조
```
KATI2/
├── app.py                 # 메인 Flask 애플리케이션
├── requirements.txt       # Python 의존성
├── render.yaml           # Render 배포 설정
├── Procfile             # 프로세스 관리
├── runtime.txt          # Python 버전
├── templates/           # HTML 템플릿
├── static/             # 정적 파일
└── README.md           # 프로젝트 문서
```

## 🚀 로컬 실행
```bash
# 의존성 설치
pip install -r requirements.txt

# 애플리케이션 실행
python app.py
```

## 📊 성능 최적화
- 메모리 사용량 최적화
- 불필요한 AI 모듈 비활성화
- 정적 파일 캐싱
- 데이터베이스 연결 풀링

---
*마지막 업데이트: 2024년 12월 19일* 