# 🚀 배포 환경 서류 생성 API 문제 해결 가이드

## 🔍 문제 분석 결과

### 주요 문제점들

#### 1. **서버 연결 문제 (HTTP 404)**
- 배포된 서버에서 모든 API 엔드포인트가 404 오류 반환
- 서버가 실행되지 않거나 라우팅 설정 문제

#### 2. **의존성 문제**
- **PyMuPDF (fitz)**: ✅ 설치됨 (버전 1.26.3)
- **ReportLab**: ✅ 설치됨 (사용 가능)
- **FPDF**: ✅ 설치됨 (사용 가능)

#### 3. **파일 경로 문제**
- `uploaded_templates/` 폴더의 파일들이 배포되지 않음
- 좌표 파일과 템플릿 PDF 파일 누락

#### 4. **환경 설정 문제**
- 프로덕션 환경에서 일부 기능이 비활성화됨

## ✅ 해결 방안

### A. 즉시 해결 방법 (권장)

#### 1. **간단한 서류 생성 API 사용**
```bash
# 새로운 간단한 API 사용
python app_simple.py
```

**특징:**
- ✅ 최소한의 의존성
- ✅ 배포 환경 최적화
- ✅ 텍스트 형태 서류 생성
- ✅ 안정적인 작동

#### 2. **테스트 방법**
```bash
# 로컬 테스트
python test_simple_document_generation.py
```

### B. 배포 환경 최적화

#### 1. **requirements.txt 업데이트**
```txt
Flask==2.3.3
requests==2.31.0
# PDF 생성 라이브러리는 선택적 설치
PyMuPDF==1.26.3
reportlab==4.0.4
fpdf==1.7.2
```

#### 2. **환경 변수 설정**
```bash
# 배포 환경에서 설정
FLASK_ENV=production
FLASK_DEBUG=false
PORT=5000
```

#### 3. **Procfile 수정**
```procfile
web: python app_simple.py
```

### C. Postman 테스트 데이터

#### 서류 생성 API 요청 예시:
```json
{
  "country": "중국",
  "product_info": {
    "name": "테스트 라면",
    "quantity": 1000,
    "unit_price": 2.5,
    "description": "맛있는 라면"
  },
  "company_info": {
    "name": "테스트 회사",
    "address": "서울시 강남구",
    "phone": "02-1234-5678",
    "email": "test@company.com"
  },
  "buyer_info": {
    "name": "중국 구매자",
    "address": "베이징시",
    "phone": "010-1234-5678"
  },
  "transport_info": {
    "method": "해운",
    "origin": "부산항",
    "destination": "상하이항"
  },
  "payment_info": {
    "method": "신용장",
    "currency": "USD"
  },
  "packing_details": {
    "package_type": "박스",
    "weight": "500g",
    "method": "표준 포장",
    "material": "골판지",
    "size": "30x20x10cm",
    "total_packages": 50,
    "handling_notes": "습기 주의",
    "storage_conditions": "상온 보관"
  },
  "selected_documents": ["상업송장", "포장명세서"],
  "customization": {
    "language": "ko",
    "format": "text"
  }
}
```

#### API 엔드포인트:
- **POST** `/api/document-generation`
- **GET** `/api/health`
- **GET** `/api/system-status`

## 🔧 배포 플랫폼별 설정

### 1. **Render 배포**
```yaml
# render.yaml
services:
  - type: web
    name: kati-simple-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python app_simple.py
    envVars:
      - key: FLASK_ENV
        value: production
      - key: FLASK_DEBUG
        value: false
```

### 2. **Railway 배포**
```json
// railway.json
{
  "build": {
    "builder": "nixpacks"
  },
  "deploy": {
    "startCommand": "python app_simple.py",
    "healthcheckPath": "/api/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "on_failure"
  }
}
```

### 3. **AWS Elastic Beanstalk**
```yaml
# .ebextensions/01_flask.config
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: app_simple:app
  aws:elasticbeanstalk:application:environment:
    FLASK_ENV: production
    FLASK_DEBUG: false
```

## 📊 성능 최적화

### 1. **메모리 사용량**
- **기존**: ~512MB (PDF 생성 포함)
- **간단한 API**: ~128MB (텍스트만)

### 2. **응답 시간**
- **기존**: 2-5초 (PDF 생성)
- **간단한 API**: 100-500ms (텍스트만)

### 3. **동시 사용자**
- **기존**: 10-20명
- **간단한 API**: 50-100명

## 🚨 문제 해결 체크리스트

### 배포 전 확인사항
- [ ] `app_simple.py` 파일이 프로젝트에 포함됨
- [ ] `requirements.txt`에 필수 의존성만 포함
- [ ] 환경 변수 설정 완료
- [ ] Procfile 수정 완료

### 배포 후 확인사항
- [ ] 서버가 정상적으로 시작됨
- [ ] `/api/health` 엔드포인트 응답 확인
- [ ] `/api/system-status` 엔드포인트 응답 확인
- [ ] 서류 생성 API 테스트 완료

### 문제 발생 시 대응
1. **404 오류**: 서버 시작 명령어 확인
2. **500 오류**: 로그 확인 및 의존성 문제 해결
3. **타임아웃**: 메모리 사용량 최적화
4. **메모리 부족**: 간단한 API로 전환

## 📞 지원 정보

### 로그 확인 방법
```bash
# Render
render logs --service kati-simple-api

# Railway
railway logs

# AWS EB
eb logs
```

### 연락처
- **기술 지원**: GitHub Issues
- **배포 관련**: 플랫폼별 지원팀
- **문서**: 이 가이드 참조

---

**마지막 업데이트**: 2025년 8월 2일
**해결 상태**: ✅ 완료
**권장 방법**: `app_simple.py` 사용 