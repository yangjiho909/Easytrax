# 🧪 Postman API 테스트 가이드

## 📋 테스트할 API 엔드포인트

### 1. 헬스 체크 API
- **URL**: `GET /api/health`
- **설명**: 서버 상태 확인
- **예상 응답**: 
```json
{
  "status": "healthy",
  "timestamp": "2024-12-19T10:30:00",
  "service": "KATI Compliance Analysis API"
}
```

### 2. 테스트 준수성 분석 API
- **URL**: `POST /api/test-compliance`
- **설명**: 간단한 테스트용 준수성 분석
- **Headers**: 
  - `Content-Type: application/json`
- **Body**:
```json
{
  "country": "중국",
  "product_type": "라면"
}
```

### 3. 실제 준수성 분석 API
- **URL**: `POST /api/compliance-analysis`
- **설명**: 실제 문서 기반 준수성 분석
- **Headers**: 
  - `Content-Type: multipart/form-data`
- **Body** (Form-data):
  - `country`: 중국
  - `product_type`: 라면
  - `use_ocr`: true
  - `company_info`: `{"name": "테스트회사", "address": "서울시"}`
  - `product_info`: `{"name": "테스트라면", "weight": "120g"}`
  - `uploaded_documents`: `[]`
  - `prepared_documents`: `[]`
  - `labeling_info`: `{}`
  - `labelFile`: [파일 업로드]
  - `nutritionFile`: [파일 업로드]

## 🚀 Postman 설정 단계

### 1. 새 Collection 생성
1. Postman 열기
2. "New Collection" 클릭
3. 이름: "KATI API Tests"

### 2. 환경 변수 설정
1. "Environments" 탭 클릭
2. "New Environment" 클릭
3. 이름: "KATI Local"
4. 변수 추가:
   - `base_url`: `http://localhost:5000`
   - `render_url`: `https://kati-export-helper.onrender.com`

### 3. 테스트 요청 생성

#### 헬스 체크 요청
```
Method: GET
URL: {{base_url}}/api/health
```

#### 테스트 준수성 분석 요청
```
Method: POST
URL: {{base_url}}/api/test-compliance
Headers: Content-Type: application/json
Body (raw JSON):
{
  "country": "중국",
  "product_type": "라면"
}
```

#### 실제 준수성 분석 요청
```
Method: POST
URL: {{base_url}}/api/compliance-analysis
Body (form-data):
- country: 중국
- product_type: 라면
- use_ocr: true
- company_info: {"name": "테스트회사", "address": "서울시"}
- product_info: {"name": "테스트라면", "weight": "120g"}
- uploaded_documents: []
- prepared_documents: []
- labeling_info: {}
```

## 🔍 테스트 시나리오

### 시나리오 1: 기본 테스트
1. 헬스 체크 API 호출
2. 테스트 준수성 분석 API 호출
3. 응답 확인

### 시나리오 2: 문서 없는 분석
1. 실제 준수성 분석 API 호출 (문서 없이)
2. 기본 분석 결과 확인

### 시나리오 3: 문서 있는 분석
1. 테스트 이미지 파일 준비
2. 실제 준수성 분석 API 호출 (파일 포함)
3. OCR 분석 결과 확인

## 📊 예상 응답 형식

### 성공 응답
```json
{
  "success": true,
  "analysis_summary": {
    "total_documents": 1,
    "analyzed_documents": ["라벨"],
    "compliance_score": 75,
    "critical_issues": 1,
    "major_issues": 2,
    "minor_issues": 3
  },
  "compliance_analysis": {
    "overall_score": 75,
    "critical_issues": [...],
    "major_issues": [...],
    "minor_issues": [...],
    "suggestions": [...]
  },
  "checklist": [...],
  "correction_guide": {...},
  "message": "중국 라면 규제 준수성 분석이 완료되었습니다."
}
```

### 오류 응답
```json
{
  "error": "분석 중 오류가 발생했습니다: [오류 내용]",
  "success": false,
  "details": "[상세 오류 정보]"
}
```

## 🐛 디버깅 팁

### 1. 로그 확인
- 서버 콘솔에서 로그 메시지 확인
- `🔍 준수성 분석 API 호출됨` 메시지 확인

### 2. 일반적인 오류
- **500 Internal Server Error**: 서버 내부 오류
- **400 Bad Request**: 요청 데이터 형식 오류
- **404 Not Found**: API 엔드포인트 없음

### 3. 문제 해결
1. 헬스 체크 API로 서버 상태 확인
2. 테스트 API로 기본 기능 확인
3. 실제 API에서 단계별 테스트

## 📝 테스트 체크리스트

- [ ] 헬스 체크 API 응답 확인
- [ ] 테스트 준수성 분석 API 응답 확인
- [ ] 실제 준수성 분석 API (문서 없음) 응답 확인
- [ ] 실제 준수성 분석 API (문서 있음) 응답 확인
- [ ] 오류 처리 확인
- [ ] 응답 형식 검증

## 🔧 로컬 테스트 실행

```bash
# 서버 실행
python app.py

# Postman에서 테스트
# URL: http://localhost:5000/api/health
```

## 🌐 Render 배포 후 테스트

```bash
# Render 배포 후
# URL: https://kati-export-helper.onrender.com/api/health
```

---
*테스트 가이드 작성: 2024년 12월 19일* 