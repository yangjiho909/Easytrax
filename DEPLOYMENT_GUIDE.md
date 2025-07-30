# 🚀 KATI2 배포 가이드

## 📋 배포 전 확인사항

### ✅ 현재 구현된 기능들
- **웹 인터페이스**: 모든 HTML 페이지 및 API 엔드포인트
- **실시간 규제 크롤링**: 외부 API 연동으로 실시간 데이터 수집
- **AI 기반 분석**: Google Cloud Vision, Azure Computer Vision, OpenAI 연동
- **파일 업로드/다운로드**: 클라우드 스토리지 시스템
- **문서 생성**: PDF, Excel, Word 문서 생성
- **OCR 처리**: 이미지에서 텍스트 추출 및 분석
- **영양 라벨 생성**: AI 기반 영양 정보 분석

### 🔧 클라우드 최적화 완료
- **파일 시스템**: 임시 파일 시스템으로 대체
- **AI 모델**: 외부 API로 대체 (로컬 모델과 동일한 기능)
- **캐싱**: 메모리 기반 캐싱 시스템
- **실시간 크롤링**: 외부 API 연동

## 🌐 배포 플랫폼 선택

### 1. Railway (권장)
- **무료 티어**: 월 $5 크레딧
- **리소스**: 1GB RAM, 3GB 저장공간
- **장점**: GitHub 연동, 자동 배포, 관대한 제한

### 2. Heroku
- **무료 티어**: 없음 (유료만)
- **리소스**: 512MB RAM (무료 플랜 없음)
- **장점**: 안정적, 확장성 좋음

### 3. Render
- **무료 티어**: 512MB RAM
- **리소스**: 제한적이지만 무료
- **장점**: 간단한 배포

## 💰 비용 정보

### Railway
- **무료**: 월 $5 크레딧 (충분함)
- **유료**: $20/월부터 (대규모 사용시)

### 외부 AI API 비용
- **Google Cloud Vision**: $1.50/1000회 요청
- **Azure Computer Vision**: $1.00/1000회 요청  
- **OpenAI GPT-3.5**: $0.002/1000 토큰

### 예상 월 비용
- **소규모 사용**: $5-10/월
- **중규모 사용**: $20-50/월
- **대규모 사용**: $100+/월

## 🔑 환경변수 설정

### 필수 환경변수
```bash
SECRET_KEY=your_secret_key_here
IS_RAILWAY=true
```

### 선택적 AI API 키 (성능 향상)
```bash
GOOGLE_CLOUD_API_KEY=your_google_api_key
AZURE_VISION_KEY=your_azure_key
AZURE_VISION_ENDPOINT=your_azure_endpoint
OPENAI_API_KEY=your_openai_key
```

## 📦 배포 단계

### 1. GitHub 푸시
```bash
git add .
git commit -m "클라우드 배포 준비 완료"
git push origin main
```

### 2. Railway 배포
1. [Railway.app](https://railway.app) 가입
2. GitHub 저장소 연결
3. 자동 배포 시작

### 3. 환경변수 설정
- Railway 대시보드에서 환경변수 설정
- AI API 키 추가 (선택사항)

## 🎯 배포 후 확인사항

### ✅ 정상 작동 확인
- [ ] 웹사이트 접속 가능
- [ ] 모든 페이지 로딩
- [ ] 파일 업로드 기능
- [ ] OCR 처리 기능
- [ ] 규제 정보 조회
- [ ] 문서 생성 기능

### ⚠️ 문제 해결
- **메모리 부족**: Railway 유료 플랜으로 업그레이드
- **API 제한**: AI API 키 설정
- **파일 저장**: 클라우드 스토리지 연동

## 🔄 업데이트 방법

### 자동 배포
- GitHub에 푸시하면 자동 배포
- 환경변수 변경 시 수동 재배포 필요

### 수동 배포
```bash
git push origin main
# Railway에서 자동으로 배포됨
```

## 📞 지원

### 문제 발생 시
1. Railway 로그 확인
2. 환경변수 설정 확인
3. AI API 키 설정 확인
4. 메모리 사용량 확인

### 연락처
- 기술 지원: 개발팀
- 비용 문의: Railway 고객지원 