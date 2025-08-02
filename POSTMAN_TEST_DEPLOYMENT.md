# 📮 배포 환경 Postman 테스트 가이드

## 🎯 테스트 목표
배포된 환경에서 서류 생성 API가 정상적으로 작동하는지 확인

## 🔗 API 엔드포인트

### 기본 URL
```
https://kati-export-helper.onrender.com
```

### 테스트할 엔드포인트
1. **헬스 체크**: `GET /api/health`
2. **시스템 상태**: `GET /api/system-status`
3. **서류 생성**: `POST /api/document-generation`

## 📋 Postman 테스트 순서

### 1. 헬스 체크 테스트

**요청 정보:**
- **Method**: GET
- **URL**: `https://kati-export-helper.onrender.com/api/health`

**예상 응답:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-02T10:30:00.000Z",
  "service": "KATI Document Generator"
}
```

### 2. 시스템 상태 테스트

**요청 정보:**
- **Method**: GET
- **URL**: `https://kati-export-helper.onrender.com/api/system-status`

**예상 응답:**
```json
{
  "status": "operational",
  "service": "KATI Simple Document Generator",
  "version": "1.0.0",
  "environment": "production",
  "features": {
    "document_generation": true,
    "pdf_generation": false,
    "ocr_processing": false,
    "ai_services": false
  },
  "supported_documents": ["상업송장", "포장명세서"],
  "timestamp": "2025-08-02T10:30:00.000Z"
}
```

### 3. 서류 생성 API 테스트

**요청 정보:**
- **Method**: POST
- **URL**: `https://kati-export-helper.onrender.com/api/document-generation`
- **Headers**: 
  - `Content-Type: application/json`

**요청 Body:**
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

**예상 응답:**
```json
{
  "success": true,
  "message": "서류 생성 완료",
  "documents": {
    "상업송장": "=== 상업송장 (Commercial Invoice) ===\n\n📋 기본 정보\n- 국가: 중국\n- 제품명: 테스트 라면\n...",
    "포장명세서": "=== 포장명세서 (Packing List) ===\n\n📋 기본 정보\n- 국가: 중국\n- 제품명: 테스트 라면\n..."
  },
  "generated_count": 2,
  "generated_documents": ["상업송장", "포장명세서"],
  "note": "배포 환경에서는 텍스트 형태로만 제공됩니다. PDF 변환은 로컬 환경에서 가능합니다."
}
```

## 🚨 오류 응답 예시

### 404 오류 (서버 미실행)
```json
{
  "error": "Not Found"
}
```

### 500 오류 (서버 내부 오류)
```json
{
  "error": "서류 생성 실패: [오류 메시지]"
}
```

### 400 오류 (잘못된 요청)
```json
{
  "error": "국가를 선택해주세요."
}
```

## ✅ 성공 판단 기준

### 1. 헬스 체크 성공
- ✅ HTTP 상태 코드: 200
- ✅ 응답에 `"status": "healthy"` 포함

### 2. 시스템 상태 성공
- ✅ HTTP 상태 코드: 200
- ✅ `"document_generation": true` 확인
- ✅ 지원 서류 목록 확인

### 3. 서류 생성 성공
- ✅ HTTP 상태 코드: 200
- ✅ `"success": true` 확인
- ✅ `"generated_count": 2` 확인
- ✅ 두 개의 서류 내용이 텍스트로 생성됨

## 🔧 문제 해결

### 1. 404 오류 발생 시
- 서버가 실행되지 않음
- 배포가 완료되지 않음
- URL이 잘못됨

### 2. 500 오류 발생 시
- 서버 내부 오류
- 의존성 문제
- 메모리 부족

### 3. 타임아웃 발생 시
- 서버 응답 지연
- 네트워크 문제
- 서버 과부하

## 📊 테스트 결과 기록

| 테스트 항목 | 상태 | 응답 시간 | 메모 |
|------------|------|----------|------|
| 헬스 체크 | ⭕ | - | - |
| 시스템 상태 | ⭕ | - | - |
| 서류 생성 | ⭕ | - | - |

**상태 표시:**
- ✅ 성공
- ❌ 실패
- ⭕ 미테스트

---

**테스트 날짜**: 2025년 8월 2일
**배포 환경**: Render
**API 버전**: 1.0.0 