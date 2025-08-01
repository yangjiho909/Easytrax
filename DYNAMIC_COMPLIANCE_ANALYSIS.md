# 동적 준수성 분석 시스템

## 🚀 개요

기존의 하드코딩된 준수성 분석을 실제 규제 데이터베이스와 연동하여 동적으로 분석하는 시스템으로 개선했습니다.

## 🔧 주요 개선사항

### 1. 실시간 규제 데이터 연동
- **KOTRA API 연동**: 최신 규제 정보 실시간 조회
- **통합 무역 데이터베이스**: 기존 규제 데이터 활용
- **실시간 크롤링**: 최신 규제 변경사항 반영
- **캐시 시스템**: 성능 최적화를 위한 규제 데이터 캐싱

### 2. AI 기반 OCR 분석
- **향상된 텍스트 추출**: AI 기반 텍스트 정제 및 구조화
- **테이블 구조 분석**: AI 기반 테이블 데이터 분석
- **신뢰도 계산**: OCR 결과의 정확도 평가
- **문서 타입별 특화 처리**: 라벨, 영양성분표, 원료리스트 등

### 3. 동적 점수 계산
- **실제 규제 기준**: 하드코딩된 점수 대신 실제 규제 위반 정도에 따른 가중치 적용
- **카테고리별 분석**: 라벨링, 영양성분, 알레르기, 원료 등 세부 분석
- **우선순위 분류**: Critical, Major, Minor 이슈 자동 분류

### 4. 국가별 특화 규제
- **중국**: GB 2760-2014, 8대 알레르기, 중국어 라벨 필수
- **미국**: FDA 규정, FSMA, 9대 알레르기, 영어 라벨 필수
- **확장 가능**: 다른 국가 규제 추가 용이

## 📊 시스템 아키텍처

```
사용자 업로드 → AI OCR 분석 → 규제 데이터 매칭 → 동적 점수 계산 → 결과 출력
     ↓              ↓              ↓              ↓           ↓
  파일 검증    텍스트 정제    실시간 규제 조회   가중치 적용   시각화
     ↓              ↓              ↓              ↓           ↓
  형식 검사    구조화 데이터    캐시 시스템    우선순위 분류   개선 제안
```

## 🔌 API 엔드포인트

### 1. 규제 상태 확인
```http
GET /api/regulation-status?country=중국&product_type=식품
```

### 2. 규제 데이터 업데이트
```http
POST /api/update-regulations
Content-Type: application/json

{
  "country": "중국",
  "product_type": "식품"
}
```

### 3. AI OCR 분석
```http
POST /api/ai-ocr-analysis
Content-Type: multipart/form-data

file: [업로드 파일]
document_type: "라벨"
```

### 4. 동적 준수성 분석
```http
POST /api/dynamic-compliance-analysis
Content-Type: application/json

{
  "country": "중국",
  "product_type": "식품",
  "structured_data": {
    "라벨": {...},
    "영양성분표": {...}
  }
}
```

## 🧪 테스트 방법

### 1. 테스트 스크립트 실행
```bash
python test_dynamic_compliance.py
```

### 2. 웹 인터페이스 테스트
1. `/compliance-analysis` 페이지 접속
2. AI 기반 분석 옵션 활성화
3. 실시간 규제 데이터 사용 체크
4. 파일 업로드 및 분석 실행

### 3. API 직접 테스트
```bash
# 규제 상태 확인
curl "http://localhost:5000/api/regulation-status?country=중국&product_type=식품"

# 규제 데이터 업데이트
curl -X POST "http://localhost:5000/api/update-regulations" \
  -H "Content-Type: application/json" \
  -d '{"country": "중국", "product_type": "식품"}'
```

## 📈 성능 개선

### 1. 캐시 시스템
- 규제 데이터 1시간 캐싱
- OCR 결과 임시 저장
- 메모리 사용량 최적화

### 2. 비동기 처리
- 파일 업로드 비동기 처리
- 규제 데이터 백그라운드 업데이트
- 사용자 경험 개선

### 3. 오류 처리
- 폴백 분석 시스템
- 단계별 오류 복구
- 상세한 오류 로깅

## 🔍 분석 결과 예시

```json
{
  "success": true,
  "country": "중국",
  "product_type": "식품",
  "analysis": {
    "overall_score": 75,
    "critical_issues": [
      "중국어 라벨 표기 필요",
      "식품안전인증서 누락"
    ],
    "major_issues": [
      "8대 알레르기 정보 표시 필요",
      "영양성분표 형식 불일치"
    ],
    "minor_issues": [
      "포장 정보 개선 권장"
    ],
    "suggestions": [
      "중국 현지 대리인과 상담",
      "식품안전인증서 발급",
      "중국어 라벨 작성"
    ],
    "regulation_source": "통합 실시간 데이터",
    "last_updated": "2025-01-15T10:30:00"
  }
}
```

## 🛠️ 설정 및 배포

### 1. 환경 변수
```bash
export KOTRA_API_KEY="your_kotra_api_key"
export DATABASE_URL="your_database_url"
export CACHE_TTL=3600
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 데이터베이스 초기화
```bash
python -c "from app import mvp_system; mvp_system.integrated_db.initialize()"
```

## 🔮 향후 개선 계획

### 1. 추가 국가 지원
- EU (CE 마킹, REACH 규정)
- 일본 (JAS 규정)
- 동남아시아 국가들

### 2. 고급 AI 기능
- 자연어 처리를 통한 규제 해석
- 이미지 인식을 통한 라벨 자동 검증
- 예측 분석을 통한 위험도 평가

### 3. 실시간 모니터링
- 규제 변경사항 실시간 알림
- 준수성 점수 변화 추적
- 시장 동향 분석

## 📞 지원 및 문의

기술적 문제나 개선 제안이 있으시면 이슈를 등록해주세요.

---

**개발팀**: 이지트랙스 개발팀  
**최종 업데이트**: 2025년 1월 15일  
**버전**: 2.0.0 