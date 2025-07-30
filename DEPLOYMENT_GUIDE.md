# 🚀 KATI 통관 수출 도우미 배포 가이드

## 📋 배포 개요
- **플랫폼**: Render.com
- **프레임워크**: Flask (Python 3.11.7)
- **웹서버**: Gunicorn
- **데이터베이스**: PostgreSQL (Render 제공)

## 🔧 배포 전 준비사항

### 1. 필수 파일 확인
```
✅ app.py - 메인 Flask 애플리케이션
✅ requirements.txt - Python 의존성
✅ render.yaml - Render 배포 설정
✅ Procfile - 프로세스 정의
✅ runtime.txt - Python 버전
✅ build.sh - 빌드 스크립트
```

### 2. 디렉토리 구조 확인
```
✅ model/ - 학습된 모델 파일들
✅ templates/ - HTML 템플릿
✅ static/ - CSS, JS, 이미지 파일
✅ data/ - 데이터 파일들
```

## 🚀 Render 배포 단계

### 1단계: Render 계정 설정
1. [Render.com](https://render.com) 가입
2. GitHub 저장소 연결
3. 새 Web Service 생성

### 2단계: 서비스 설정
```yaml
# render.yaml 설정
services:
  - type: web
    name: kati-customs-system
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

### 3단계: 환경 변수 설정
- `SECRET_KEY`: 자동 생성
- `IS_RENDER`: true
- `PORT`: 10000

### 4단계: 배포 실행
1. GitHub 저장소에 코드 푸시
2. Render에서 자동 배포 시작
3. 빌드 로그 모니터링

## 🔍 배포 문제 해결

### 일반적인 오류들

#### 1. 빌드 타임아웃
```bash
# 해결방법: requirements.txt 최적화
# 무거운 라이브러리들을 선택적으로 설치
```

#### 2. 메모리 부족
```bash
# 해결방법: gunicorn 워커 수 조정
startCommand: gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120
```

#### 3. 모듈 import 오류
```bash
# 해결방법: try-except 블록으로 안전한 import
try:
    import heavy_module
except ImportError:
    print("모듈을 찾을 수 없습니다")
```

### 빌드 로그 확인
```bash
# Render 대시보드에서 실시간 로그 확인
# 주요 체크포인트:
# 1. Python 버전 확인
# 2. pip 설치 성공
# 3. 모델 파일 로드
# 4. Flask 앱 시작
```

## 📊 성능 최적화

### 1. 메모리 사용량 최적화
- Gunicorn 워커 수: 1-2개
- 타임아웃: 120초
- 메모리 제한: 512MB

### 2. 빌드 시간 최적화
- 불필요한 파일 제외
- 캐시 활용
- 의존성 최소화

### 3. 런타임 최적화
- 모델 로딩 지연
- 이미지 처리 최적화
- 데이터베이스 연결 풀링

## 🔒 보안 설정

### 1. 환경 변수
```bash
SECRET_KEY=your_secret_key_here
IS_RENDER=true
DATABASE_URL=your_database_url
```

### 2. 파일 업로드 보안
```python
# app.py에서 설정
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB 제한
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
```

## 📈 모니터링

### 1. 헬스 체크
- 엔드포인트: `/`
- 응답 시간: < 5초
- 상태 코드: 200

### 2. 로그 모니터링
```bash
# 주요 로그 메시지
✅ 모든 MVP 모듈 import 성공
✅ 웹 MVP 모델 로드 완료
🚀 Flask 앱 시작
```

### 3. 성능 메트릭
- 응답 시간
- 메모리 사용량
- CPU 사용률
- 에러율

## 🛠️ 유지보수

### 1. 정기 업데이트
- 의존성 패키지 업데이트
- 보안 패치 적용
- 성능 최적화

### 2. 백업
- 코드 백업 (GitHub)
- 데이터 백업 (Render 제공)
- 설정 백업

### 3. 장애 대응
- 자동 재시작 설정
- 로그 분석
- 문제 해결 가이드

## 📞 지원

### 문제 발생 시
1. Render 로그 확인
2. GitHub Issues 등록
3. 개발팀 문의

### 유용한 링크
- [Render 문서](https://render.com/docs)
- [Flask 문서](https://flask.palletsprojects.com/)
- [Gunicorn 문서](https://gunicorn.org/)

---

**배포 완료 후 확인사항:**
- ✅ 웹사이트 접속 가능
- ✅ 모든 기능 정상 작동
- ✅ 파일 업로드/다운로드 정상
- ✅ 데이터베이스 연결 정상
- ✅ API 응답 정상 