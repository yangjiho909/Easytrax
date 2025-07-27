# 🚀 KATI MVP 시스템 배포 가이드

## 📋 배포 단계별 가이드

### 1단계: GitHub 저장소 생성

1. **GitHub.com에 로그인**
2. **새 저장소 생성**
   - Repository name: `kati-mvp-system`
   - Description: `KATI MVP 통합 수출 지원 시스템`
   - Public 선택
   - README 파일 생성 체크 해제 (이미 있음)

### 2단계: 로컬 저장소를 GitHub에 연결

```bash
# 원격 저장소 추가 (YOUR_USERNAME을 실제 GitHub 사용자명으로 변경)
git remote add origin https://github.com/YOUR_USERNAME/kati-mvp-system.git

# 메인 브랜치를 main으로 변경
git branch -M main

# GitHub에 푸시
git push -u origin main
```

### 3단계: Render 배포

1. **Render.com에 로그인**
2. **새 Web Service 생성**
3. **GitHub 저장소 연결**
   - Connect to: GitHub
   - Repository: `kati-mvp-system` 선택

4. **서비스 설정**
   - Name: `kati-customs-helper`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

5. **환경 변수 설정**
   - `FLASK_ENV`: `production`
   - `PYTHON_VERSION`: `3.9.16`

6. **배포 시작**
   - Create Web Service 클릭

### 4단계: 배포 확인

배포가 완료되면 다음 URL로 접속 가능:
```
https://kati-customs-helper.onrender.com
```

## 🔧 배포 후 확인사항

### 1. 웹사이트 접속 테스트
- 메인 페이지 로딩 확인
- 모든 메뉴 페이지 접속 확인
- API 호출 테스트

### 2. 기능 테스트
- 실시간 규제정보 조회
- 통관 거부사례 분석
- 규제 준수성 분석
- 자동 서류 생성
- 영양정보 라벨 생성

### 3. 성능 확인
- 페이지 로딩 속도
- API 응답 시간
- 동시 접속자 처리

## 📊 배포 상태 모니터링

### Render 대시보드에서 확인할 수 있는 정보:
- 서비스 상태 (Live/Deploying/Failed)
- 로그 확인
- 리소스 사용량
- 응답 시간

### 문제 해결:
- 로그 확인: Render 대시보드 → Logs
- 환경 변수 확인: Settings → Environment Variables
- 빌드 오류 확인: Build Logs

## 🌐 공개 URL

배포 완료 후 다음 URL로 전 세계 누구나 접속 가능:
```
https://kati-customs-helper.onrender.com
```

## 📞 지원

배포 중 문제가 발생하면:
1. Render 로그 확인
2. GitHub Issues 생성
3. 개발팀 문의

---

**배포 완료 예상 시간**: 5-10분  
**서비스 유형**: Web Service  
**플랫폼**: Render  
**도메인**: kati-customs-helper.onrender.com 