# 🧪 Postman API 테스트 가이드

## 🚀 효율적인 API 테스트 워크플로우

### 📋 권장 테스트 순서
1. **로컬 테스트** → 2. **Postman 검증** → 3. **GitHub 푸시** → 4. **Render 자동 배포**

### 🔧 1단계: 로컬 서버 실행 및 테스트
```bash
# 로컬 서버 실행
python app.py

# 서버 URL: http://localhost:5000
```

### 🌐 2단계: Postman 환경 설정
1. **로컬 환경 변수**:
   - `local_url`: `http://localhost:5000`
   - `render_url`: `https://kati-export-helper.onrender.com`

2. **테스트 순서**:
   - 로컬에서 API 수정사항 테스트
   - Postman으로 응답 검증
   - 문제 없으면 GitHub 푸시

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

### 4. 테스트 문서 생성 API
- **URL**: `POST /api/test-document-generation`
- **설명**: 테스트용 PDF 문서 생성
- **Headers**: 
  - `Content-Type: application/json`
- **Body**:
```json
{
  "country": "중국",
  "product_info": {"name": "테스트라면", "weight": "120g"},
  "company_info": {"name": "테스트회사", "address": "서울시"}
}
```

### 5. 실제 문서 생성 API
- **URL**: `POST /api/document-generation`
- **설명**: 실제 문서 생성 (상업송장, 포장명세서)
- **Headers**: 
  - `Content-Type: application/json`
- **Body**:
```json
{
  "country": "중국",
  "product_info": {"name": "테스트라면", "weight": "120g"},
  "company_info": {"name": "테스트회사", "address": "서울시"},
  "buyer_info": {"name": "중국수입업체", "address": "상하이"},
  "transport_info": {"method": "해운", "port": "인천항"},
  "payment_info": {"method": "신용장", "terms": "D/P"},
  "packing_details": {"packages": 100, "weight": "12kg"},
  "selected_documents": ["상업송장", "포장명세서"]
}
```

### 6. 문서 다운로드 API
- **URL**: `GET /api/download-document/{filename}`
- **설명**: 생성된 PDF 파일 다운로드
- **예시**: `GET /api/download-document/상업송장_20241219_143022.pdf`

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

## 🚀 Postman에서 직접 테스트하는 방법

### 📋 1단계: Postman 설정

#### A. 새 Collection 생성
1. Postman 열기
2. "New Collection" 클릭
3. 이름: "KATI API Tests"

#### B. 환경 변수 설정 (중요!)
1. **우측 상단의 "Environments" 탭 클릭**
2. **"New Environment" 클릭**
3. **환경 이름**: "KATI Local"
4. **변수 추가**:
   - `local_url`: `http://localhost:5000`
   - `render_url`: `https://kati-export-helper.onrender.com`
5. **"Save" 클릭**
6. **우측 상단 드롭다운에서 "KATI Local" 환경 선택** (중요!)

#### C. 환경 변수 확인 방법
- URL 입력란에 `{{local_url}}`을 입력하면 자동으로 `http://localhost:5000`으로 변환되어야 함
- 만약 `{{local_url}}`이 그대로 표시되면 환경이 선택되지 않은 것

### 🔧 2단계: 준수성 분석 API 테스트

#### A. JSON 방식 테스트 (권장)
```
Method: POST
URL: {{local_url}}/api/compliance-analysis
Headers: 
  - Content-Type: application/json

Body (raw JSON):
{
  "country": "중국",
  "product_type": "라면",
  "use_ocr": false,
  "company_info": {
    "name": "테스트회사",
    "address": "서울시 강남구"
  },
  "product_info": {
    "name": "테스트라면",
    "weight": "120g"
  },
  "uploaded_documents": [],
  "prepared_documents": [],
  "labeling_info": {}
}
```

#### B. Form-Data 방식 테스트
```
Method: POST
URL: {{local_url}}/api/compliance-analysis
Headers: 
  - Content-Type: multipart/form-data

Body (form-data):
- country: 중국
- product_type: 라면
- use_ocr: false
- company_info: {"name":"테스트회사","address":"서울시 강남구"}
- product_info: {"name":"테스트라면","weight":"120g"}
- uploaded_documents: []
- prepared_documents: []
- labeling_info: {}
```

### 🧪 3단계: 테스트 순서

#### 1. 헬스 체크 먼저
```
Method: GET
URL: {{local_url}}/api/health
```

#### 2. 준수성 분석 테스트
위의 JSON 또는 Form-Data 방식 중 하나 선택

#### 3. 응답 확인
- **성공**: JSON 형태의 분석 결과
- **실패**: 에러 메시지 확인

### 🔍 4단계: 문제 해결

#### 환경 변수 문제
- `{{local_url}}`이 변환되지 않으면:
  1. 우측 상단에서 "KATI Local" 환경이 선택되었는지 확인
  2. 환경 변수에 `local_url`이 정확히 입력되었는지 확인

#### 서버 연결 문제
- `ENOTFOUND` 오류 발생 시:
  1. 로컬 서버가 실행 중인지 확인: `python app.py`
  2. URL을 직접 입력: `http://localhost:5000/api/compliance-analysis`

### 📄 5단계: 서류생성 API 테스트

#### A. 기본 서류생성 테스트
```
Method: POST
URL: {{local_url}}/api/document-generation
Headers: 
  - Content-Type: application/json

Body (raw JSON):
{
  "country": "중국",
  "product_info": {
    "name": "라면",
    "code": "1902.30.0000",
    "quantity": 1000,
    "unit": "개",
    "unit_price": 2.5,
    "weight": 500,
    "volume": 0.5,
    "origin": "KOREA"
  },
  "company_info": {
    "name": "한국식품공사",
    "address": "서울시 강남구 테헤란로 123",
    "phone": "02-1234-5678",
    "email": "info@koreafood.com"
  },
  "buyer_info": {
    "name": "중국식품무역공사",
    "address": "상해시 황포구 난징로 456",
    "phone": "021-8765-4321",
    "email": "contact@chinafood.com"
  },
  "transport_info": {
    "port_of_departure": "BUSAN, KOREA",
    "port_of_arrival": "SHANGHAI, CHINA",
    "mode": "SEA",
    "package_type": "Carton"
  },
  "payment_info": {
    "method": "L/C",
    "terms": "CIF"
  },
  "packing_details": {
    "package_type": "Carton",
    "total_packages": 50
  },
  "selected_documents": ["상업송장", "포장명세서"],
  "customization": {
    "style": "professional"
  }
}
```

#### B. 예상 응답
```json
{
  "success": true,
  "message": "서류 생성 완료",
  "documents": {
    "상업송장": "상업송장 (Commercial Invoice)\n=====================================\n\n송장번호: INV-20250731-1000\n...",
    "포장명세서": "포장명세서 (Packing List)\n=====================================\n\n명세서번호: PKG-20250731-1000\n..."
  },
  "pdf_files": {
    "상업송장": "상업송장_20250731_004651.pdf",
    "포장명세서": "포장명세서_20250731_004651.pdf"
  },
  "download_urls": {
    "상업송장": "/api/download-document/상업송장_20250731_004651.pdf",
    "포장명세서": "/api/download-document/포장명세서_20250731_004651.pdf"
  },
  "generated_count": 2,
  "download_instructions": {
    "method": "GET",
    "urls": {
      "상업송장": "/api/download-document/상업송장_20250731_004651.pdf",
      "포장명세서": "/api/download-document/포장명세서_20250731_004651.pdf"
    },
    "note": "각 URL을 브라우저에서 직접 접속하거나 JavaScript로 window.open() 사용"
  }
}
```

#### C. PDF 다운로드 테스트
생성된 PDF 파일을 다운로드하려면:

1. **브라우저에서 직접 접속:**
   - `{{local_url}}/api/download-document/상업송장_20250731_004651.pdf`
   - `{{local_url}}/api/download-document/포장명세서_20250731_004651.pdf`

2. **Postman에서 GET 요청:**
   - `GET {{local_url}}/api/download-document/상업송장_20250731_004651.pdf`
   - `GET {{local_url}}/api/download-document/포장명세서_20250731_004651.pdf`

#### D. 지원되는 서류 유형
현재 자동 생성 가능한 서류:
- `상업송장` (Commercial Invoice)
- `포장명세서` (Packing List)

#### E. 주의사항
- **필수 필드:** `country`, `selected_documents`는 반드시 포함해야 합니다.
- **PDF 생성:** 서류 생성과 동시에 PDF 파일이 자동으로 생성됩니다.
- **파일 저장:** 생성된 PDF 파일은 `generated_documents/` 디렉토리에 저장됩니다.
- **다운로드:** 응답에 포함된 `download_urls`를 통해 PDF 파일을 다운로드할 수 있습니다.

### 📝 6단계: 테스트 결과 기록

각 테스트 후 결과를 기록:
- ✅ 성공한 요청
- ❌ 실패한 요청과 에러 메시지
- 🔧 수정이 필요한 부분
- 📄 PDF 파일 생성 및 다운로드 상태

---
*테스트 가이드 작성: 2024년 12월 19일* 