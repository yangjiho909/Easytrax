# 🚀 Render 배포 가이드

## 📋 배포 준비 완료 사항

### ✅ 완료된 설정 파일들
- `render.yaml` - Render 서비스 설정
- `Procfile` - 프로세스 관리
- `runtime.txt` - Python 버전 명시
- `requirements.txt` - 의존성 패키지 (최적화됨)
- `.gitignore` - Git 제외 파일 설정
- `README.md` - 프로젝트 문서 업데이트

### 🔧 기술 스택
- **Backend**: Flask 3.0+
- **Python**: 3.11.0
- **Process Manager**: Gunicorn
- **Platform**: Render (Free Plan)

## 🚀 배포 단계

### 1. GitHub 저장소 준비
```bash
# 현재 변경사항 커밋
git add .
git commit -m "Render 배포 준비 완료"
git push origin main
```

### 2. Render 계정 설정
1. [Render.com](https://render.com) 방문
2. GitHub 계정으로 가입/로그인
3. GitHub 저장소 연결

### 3. 웹 서비스 생성
1. Dashboard에서 "New Web Service" 클릭
2. GitHub 저장소 선택: `KATI2`
3. 서비스 설정:
   - **Name**: `kati-export-helper`
   - **Environment**: `Python 3`
   - **Region**: `Oregon (US West)` (가장 빠름)
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

### 4. 환경 변수 설정
- `FLASK_ENV`: `production`
- `PORT`: `10000`

### 5. 배포 실행
- "Create Web Service" 클릭
- 빌드 과정 모니터링 (약 5-10분 소요)
- 배포 완료 후 URL 확인

## 🌐 배포 후 확인사항

### URL 접속 테스트
- 메인 페이지: `https://kati-export-helper.onrender.com`
- 대시보드: `https://kati-export-helper.onrender.com/dashboard`
- 통관 분석: `https://kati-export-helper.onrender.com/customs-analysis`

### 기능 테스트
1. **메인 페이지 로딩**
2. **대시보드 통계 조회**
3. **통관 분석 기능**
4. **문서 생성 기능**
5. **영양성분표 생성**

## 📊 성능 최적화

### 메모리 사용량 최적화
- 불필요한 AI 모듈 비활성화
- 정적 파일 캐싱 설정
- 데이터베이스 연결 풀링

### 무료 플랜 제한사항
- **메모리**: 512MB
- **CPU**: 공유 리소스
- **스토리지**: 1GB
- **월 사용량**: 750시간

## 🔧 문제 해결

### 빌드 실패 시
1. `requirements.txt` 버전 호환성 확인
2. Python 버전 확인 (3.11.0)
3. 로그 확인 및 수정

### 런타임 오류 시
1. 환경 변수 설정 확인
2. 포트 설정 확인
3. 메모리 사용량 모니터링

### 성능 이슈 시
1. 정적 파일 최적화
2. 데이터베이스 쿼리 최적화
3. 캐싱 전략 적용

## 📈 모니터링

### Render Dashboard
- 실시간 로그 확인
- 성능 메트릭 모니터링
- 오류 알림 설정

### 애플리케이션 로그
- Flask 로그 확인
- Gunicorn 로그 확인
- 사용자 접속 통계

## 🔄 업데이트 배포

### 자동 배포
- GitHub main 브랜치 푸시 시 자동 배포
- 빌드 및 배포 과정 자동화

### 수동 배포
1. Render Dashboard에서 "Manual Deploy" 클릭
2. 특정 커밋 선택 가능
3. 배포 상태 모니터링

## 💰 비용 관리

### 무료 플랜 한계
- 월 750시간 사용 제한
- 15분 비활성 시 슬립 모드
- 제한된 리소스 할당

### 유료 플랜 고려사항
- 월 $7부터 시작
- 24/7 가동
- 더 많은 리소스 할당

---
*배포 준비 완료: 2024년 12월 19일* 