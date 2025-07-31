# 통합 무역 데이터베이스 시스템 종합 보고서

## 📋 프로젝트 개요

### 목표
중국 또는 미국의 통관·무역·수출입·시장동향·전략 등 어떤 질문이든 자연어로 입력받아 AI가 통합 데이터베이스를 참조하여 답변하는 시스템을 구축합니다.

### 핵심 기능
- **자연어 질의 처리**: 사용자가 자연어로 질문하면 AI가 의도를 파악하고 적절한 답변 생성
- **통합 데이터베이스**: 규제정보, 무역통계, 시장분석, 전략보고서를 하나의 DB로 통합
- **신뢰도 기반 답변**: 데이터 소스별 신뢰도 점수를 반영한 답변 생성
- **후속 질문 제안**: 사용자의 추가 질문을 제안하여 대화형 경험 제공
- **시각화 제안**: 데이터에 적합한 차트/그래프 제안

## 🏗️ 시스템 아키텍처

### 1. 데이터 소스 통합
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   KOTRA API     │    │ KOTRA BigData   │    │ Public Data     │
│   (규제정보)     │    │ (무역통계)       │    │ (수출입실적)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Market Entry    │
                    │ Strategy Parser │
                    │ (전략보고서)     │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Integrated      │
                    │ Trade Database  │
                    │ (통합 DB)       │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │ Natural Language│
                    │ Query Engine    │
                    │ (자연어 처리)    │
                    └─────────────────┘
```

### 2. 데이터베이스 스키마

#### 규제 정보 테이블 (regulations)
```sql
CREATE TABLE regulations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    country TEXT NOT NULL,           -- 국가 (중국/미국)
    product TEXT NOT NULL,           -- 품목 (라면/마스크 등)
    category TEXT NOT NULL,          -- 카테고리 (식품안전/인증 등)
    title TEXT NOT NULL,             -- 규제 제목
    description TEXT,                -- 규제 설명
    requirements TEXT,               -- 요구사항
    source TEXT NOT NULL,            -- 데이터 소스
    last_updated TEXT,               -- 최종 업데이트
    reliability_score REAL DEFAULT 0.8, -- 신뢰도 점수
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

#### 무역 통계 테이블 (trade_statistics)
```sql
CREATE TABLE trade_statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    country TEXT NOT NULL,           -- 국가
    hs_code TEXT,                    -- HS코드
    product TEXT,                    -- 품목
    period TEXT NOT NULL,            -- 기간
    export_amount REAL,              -- 수출액
    import_amount REAL,              -- 수입액
    trade_balance REAL,              -- 무역수지
    growth_rate REAL,                -- 성장률
    market_share REAL,               -- 시장점유율
    source TEXT NOT NULL,            -- 데이터 소스
    data_date TEXT,                  -- 데이터 날짜
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

#### 시장 분석 테이블 (market_analysis)
```sql
CREATE TABLE market_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    country TEXT NOT NULL,           -- 국가
    product TEXT NOT NULL,           -- 품목
    analysis_type TEXT NOT NULL,     -- 분석 유형
    title TEXT NOT NULL,             -- 분석 제목
    content TEXT,                    -- 분석 내용
    trend_type TEXT,                 -- 트렌드 유형
    period TEXT,                     -- 분석 기간
    data_support TEXT,               -- 데이터 근거
    source TEXT NOT NULL,            -- 데이터 소스
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

#### 전략 보고서 테이블 (strategy_reports)
```sql
CREATE TABLE strategy_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id TEXT UNIQUE NOT NULL,  -- 보고서 ID
    country TEXT NOT NULL,           -- 국가
    product TEXT NOT NULL,           -- 품목
    title TEXT NOT NULL,             -- 보고서 제목
    executive_summary TEXT,          -- 실행 요약
    key_issues_count INTEGER,        -- 주요 이슈 수
    market_trends_count INTEGER,     -- 시장 동향 수
    customs_documents_count INTEGER, -- 통관 서류 수
    response_strategies_count INTEGER, -- 대응 전략 수
    risk_keywords TEXT,              -- 리스크 키워드
    market_size TEXT,                -- 시장 규모
    growth_rate TEXT,                -- 성장률
    regulatory_complexity TEXT,      -- 규제 복잡성
    risk_assessment TEXT,            -- 리스크 평가
    source TEXT NOT NULL,            -- 데이터 소스
    report_date TEXT,                -- 보고서 날짜
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

## 🤖 자연어 질의 처리 시스템

### 1. 질의 타입 분석
```python
query_patterns = {
    "regulation": [
        r"규제|규정|인증|허가|승인|검사|기준|표준",
        r"서류|문서|증명서|허가증|인증서",
        r"필요|요구|준수|의무"
    ],
    "trade_statistics": [
        r"통계|수치|데이터|금액|수량|비율",
        r"수출|수입|무역|거래|교역",
        r"HS코드|품목|상품|제품"
    ],
    "market_analysis": [
        r"시장|동향|트렌드|전망|예측",
        r"경쟁|수요|공급|가격|성장",
        r"유망|기회|잠재력|성장률"
    ],
    "risk_assessment": [
        r"리스크|위험|불확실성|변동성",
        r"문제|이슈|장벽|제약|어려움",
        r"도전|과제|복잡성"
    ],
    "strategy": [
        r"전략|대응|해결|개선|강화",
        r"방안|방법|접근|절차|단계",
        r"권장|제안|필요|중요"
    ]
}
```

### 2. 엔티티 추출
- **국가 추출**: 중국, 미국, China, USA 등
- **HS코드 추출**: HS코드 190230, 190230 HS코드 등
- **품목 추출**: 라면, 마스크, 전자제품, 의류, 식품, 화학제품 등

### 3. 신뢰도 점수 시스템
```python
reliability_scores = {
    "KOTRA_API": 0.95,           # KOTRA 공식 API (최고 신뢰도)
    "KOTRA_BIGDATA": 0.90,       # KOTRA 빅데이터 (높은 신뢰도)
    "PUBLIC_DATA_PORTAL": 0.85,  # 공공데이터포털 (높은 신뢰도)
    "REAL_TIME_CRAWLER": 0.80,   # 실시간 크롤러 (중간 신뢰도)
    "MVP_DATA": 0.70,            # MVP 기본 데이터 (기본 신뢰도)
    "MARKET_ENTRY_PARSER": 0.75  # 시장 진출 파서 (중간 신뢰도)
}
```

## 📊 API 엔드포인트

### 1. 자연어 질의 API
```http
POST /api/natural-language-query
Content-Type: application/json

{
    "query": "중국 라면 수출 규제 알려줘"
}
```

**응답 예시:**
```json
{
    "success": true,
    "message": "자연어 질의 처리 완료",
    "data": {
        "answer": "📋 **규제 정보**\n• 중국 라면 수출 식품안전 규제 (출처: KOTRA_API)\n• 미국 라면 수출 FDA 규제 (출처: KOTRA_API)\n\n📊 **무역 통계**\n• 2024년 4분기: 수출 1,500,000만원, 수입 500,000만원 (출처: KOTRA_BIGDATA)",
        "data_sources": ["KOTRA_API", "KOTRA_BIGDATA"],
        "confidence_score": 0.87,
        "suggested_followup": [
            "해당 규제의 최신 변경사항을 확인하시겠습니까?",
            "관련 인증 절차에 대해 더 자세히 알고 싶으신가요?"
        ],
        "visualizations": [
            {
                "type": "line_chart",
                "title": "무역 추이 그래프",
                "description": "월별/분기별 수출입 추이를 시각화"
            }
        ],
        "timestamp": "2025-01-15T10:30:00"
    }
}
```

### 2. 데이터베이스 상태 확인 API
```http
GET /api/integrated-db-status
```

### 3. 샘플 데이터 로드 API
```http
POST /api/load-sample-data
```

## 🎯 사용 예시

### 예시 질의 1: 규제 정보
**질의**: "올해 미국 마스크 수출 서류 뭐가 필요하지?"

**답변**:
```
📋 **규제 정보**
• 미국 마스크 수출 FDA 규제 (출처: KOTRA_API)
• FDA 등록, 식품안전계획, 라벨링 규정 준수

💡 추가 질문 제안:
1. 해당 규제의 최신 변경사항을 확인하시겠습니까?
2. 관련 인증 절차에 대해 더 자세히 알고 싶으신가요?
```

### 예시 질의 2: 무역 통계
**질의**: "HS코드 190230의 미중 유망시장 통계 비교해줘"

**답변**:
```
📊 **무역 통계**
• 중국 2024년 4분기: 수출 1,500,000만원, 수입 500,000만원 (출처: KOTRA_BIGDATA)
• 미국 2024년 4분기: 수출 2,000,000만원, 수입 800,000만원 (출처: KOTRA_BIGDATA)

📈 시각화 제안:
• 무역 추이 그래프: 월별/분기별 수출입 추이를 시각화
```

### 예시 질의 3: 시장 분석
**질의**: "중국 수출 주요 리스크 알려줘"

**답변**:
```
📈 **시장 동향**
• 중국 라면 시장 성장 전망: 중국 라면 시장은 연평균 8% 성장률을 보이며, 프리미엄 라면 수요가 증가하고 있습니다. (출처: KOTRA_BIGDATA)

📋 **전략 보고서**
• 중국 라면 시장 진출 전략 보고서: 중국 라면 시장 진출을 위한 종합 전략 분석 (출처: MARKET_ENTRY_PARSER)

💡 추가 질문 제안:
1. 향후 시장 전망을 확인하시겠습니까?
2. 관련 리스크 분석을 원하시나요?
```

## 🔧 기술 스택

### 백엔드
- **Flask**: 웹 프레임워크
- **SQLite**: 통합 데이터베이스
- **Python**: 메인 프로그래밍 언어

### 데이터 처리
- **정규표현식**: 패턴 매칭 및 엔티티 추출
- **JSON**: 데이터 직렬화
- **Dataclasses**: 데이터 구조 정의

### 외부 연동
- **KOTRA API**: 공식 무역 정보
- **KOTRA BigData**: 무역 통계 데이터
- **Public Data Portal**: 공공데이터
- **실시간 크롤러**: 동적 데이터 수집

## 📈 성능 및 확장성

### 1. 성능 최적화
- **인덱스 생성**: 국가, 품목, HS코드별 인덱스
- **캐싱 시스템**: 자주 조회되는 데이터 캐싱
- **비동기 처리**: 대용량 데이터 처리 시 비동기 방식

### 2. 확장성
- **모듈화 설계**: 각 기능별 독립적 모듈
- **플러그인 구조**: 새로운 데이터 소스 쉽게 추가 가능
- **API 기반**: RESTful API로 다양한 클라이언트 지원

### 3. 데이터 품질
- **신뢰도 점수**: 데이터 소스별 신뢰도 평가
- **데이터 검증**: 입력 데이터 유효성 검사
- **백업 시스템**: 데이터 손실 방지

## 🚀 향후 발전 방향

### 1. AI/ML 강화
- **자연어 처리**: 더 정교한 NLP 모델 적용
- **추천 시스템**: 사용자 맞춤형 정보 추천
- **예측 분석**: 시장 전망 예측 기능

### 2. 데이터 확장
- **다국가 지원**: 중국, 미국 외 추가 국가
- **다품목 지원**: 라면 외 다양한 품목
- **실시간 데이터**: 실시간 무역 정보 업데이트

### 3. 사용자 경험
- **대화형 인터페이스**: 챗봇 형태의 자연스러운 대화
- **시각화 강화**: 인터랙티브 차트 및 그래프
- **모바일 지원**: 모바일 앱 개발

## 📝 결론

통합 무역 데이터베이스 시스템은 다음과 같은 핵심 가치를 제공합니다:

1. **통합된 정보 접근**: 분산된 무역 정보를 하나의 인터페이스로 통합
2. **자연스러운 상호작용**: 자연어로 복잡한 무역 정보 조회 가능
3. **신뢰성 있는 답변**: 데이터 소스별 신뢰도를 반영한 정확한 정보 제공
4. **확장 가능한 구조**: 새로운 데이터 소스와 기능을 쉽게 추가 가능

이 시스템을 통해 수출업체들은 복잡한 무역 정보를 쉽게 조회하고, 시장 진출 전략을 수립하는 데 도움을 받을 수 있습니다. 