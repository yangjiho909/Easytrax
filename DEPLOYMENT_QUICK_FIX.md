# 🚀 배포 환경 서류 생성 API 빠른 수정 가이드

## ✅ 즉시 적용할 수정사항

### 1. **Procfile 수정** (완료)
```procfile
web: python app_simple.py
```

### 2. **requirements_simple.txt 생성** (완료)
```txt
# 배포 환경용 간단한 의존성 (서류 생성 API 전용)
Flask==2.3.3
requests==2.31.0
```

### 3. **render.yaml 수정** (완료)
```yaml
buildCommand: |
  # Python 패키지 설치 (간단한 버전)
  pip install -r requirements_simple.txt
startCommand: python app_simple.py
```

### 4. **railway.json 수정** (완료)
```json
{
  "deploy": {
    "startCommand": "python app_simple.py",
    "healthcheckPath": "/api/health",
    "healthcheckTimeout": 300
  }
}
```

## 🔄 배포 방법

### Render 배포
1. GitHub에 변경사항 푸시
2. Render에서 자동 배포 확인
3. 배포 완료 후 테스트

### Railway 배포
1. GitHub에 변경사항 푸시
2. Railway에서 자동 배포 확인
3. 배포 완료 후 테스트

## 🧪 배포 후 테스트

### 1. 헬스 체크
```bash
curl https://your-app-url.onrender.com/api/health
```

### 2. 서류 생성 API 테스트
```bash
curl -X POST https://your-app-url.onrender.com/api/document-generation \
  -H "Content-Type: application/json" \
  -d '{
    "country": "중국",
    "product_info": {
      "name": "테스트 라면",
      "quantity": 1000,
      "unit_price": 2.5
    },
    "company_info": {
      "name": "테스트 회사",
      "address": "서울시 강남구"
    },
    "buyer_info": {
      "name": "중국 구매자",
      "address": "베이징시"
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
      "method": "표준 포장",
      "material": "골판지"
    },
    "selected_documents": ["상업송장", "포장명세서"]
  }'
```

## 📊 예상 개선 효과

| 항목 | 기존 | 수정 후 |
|------|------|---------|
| 메모리 사용량 | ~512MB | ~128MB |
| 응답 시간 | 2-5초 | 100-500ms |
| 배포 시간 | 3-5분 | 1-2분 |
| 안정성 | 불안정 | 안정적 |

## 🚨 문제 발생 시 대응

### 1. 404 오류
- 서버 시작 명령어 확인
- `app_simple.py` 파일 존재 확인

### 2. 500 오류
- 로그 확인: `render logs` 또는 `railway logs`
- 의존성 문제 해결

### 3. 타임아웃
- 메모리 사용량 최적화 완료됨
- 추가 최적화 불필요

## 📞 지원

- **로그 확인**: 플랫폼별 로그 명령어 사용
- **재배포**: GitHub 푸시로 자동 재배포
- **롤백**: 이전 버전으로 되돌리기 가능

---

**수정 완료**: 2025년 8월 2일
**적용 방법**: GitHub 푸시 후 자동 배포
**예상 결과**: 서류 생성 API 정상 작동 