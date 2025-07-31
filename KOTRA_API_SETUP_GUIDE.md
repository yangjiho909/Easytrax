# 🌐 KOTRA 국가정보 API 설정 가이드

## 📋 개요

KATI 시스템에서 공공데이터포털 KOTRA 국가정보 API를 활용하여 중국, 미국의 무역·통관 규정을 실시간으로 조회할 수 있습니다.

## 🔑 API 키 발급 방법

### 1. 공공데이터포털 회원가입
- [공공데이터포털](https://www.data.go.kr/) 접속
- 회원가입 및 로그인

### 2. KOTRA 국가정보 API 신청
- [KOTRA 국가정보 API](https://www.data.go.kr/data/15034830/openapi.do?recommendDataYn=Y) 페이지 접속
- "활용신청" 버튼 클릭
- 신청서 작성 및 제출

### 3. API 키 확인
- 승인 후 "마이페이지 > 개발계정 > 일반 인증키"에서 서비스키 확인
- 예시: `abc123def456ghi789jkl012mno345pqr678stu901vwx234yz`

## ⚙️ 환경변수 설정

### Windows 환경
```cmd
set KOTRA_SERVICE_KEY=your_api_key_here
```

### Linux/Mac 환경
```bash
export KOTRA_SERVICE_KEY=your_api_key_here
```

### Python 코드에서 직접 설정
```python
import os
os.environ['KOTRA_SERVICE_KEY'] = 'your_api_key_here'
```

## 🔧 시스템 통합

### 1. KOTRA API 모듈 import 확인
```python
from kotra_regulation_api import KOTRARegulationAPI
```

### 2. 시스템 초기화 확인
```python
# WebMVPSystem 클래스에서 자동으로 초기화됨
self.kotra_api = KOTRARegulationAPI()
```

### 3. API 상태 확인
```bash
curl -X GET http://localhost:5000/api/kotra-status
```

## 📊 API 응답 구조

### 성공 응답 예시
```json
{
  "success": true,
  "kotra_api_status": {
    "service_key_configured": true,
    "supported_countries": ["중국", "미국"],
    "cache_directory": "regulation_cache",
    "last_update": "2024-01-15 14:30:00",
    "api_connection": "success"
  },
  "kotra_available": true
}
```

### 실패 응답 예시
```json
{
  "success": true,
  "kotra_api_status": {
    "service_key_configured": false,
    "supported_countries": [],
    "cache_directory": "regulation_cache",
    "last_update": "2024-01-15 14:30:00",
    "api_connection": "no_service_key"
  },
  "kotra_available": false
}
```

## 🔄 규제 정보 업데이트

### 수동 업데이트
```bash
curl -X POST http://localhost:5000/api/update-kotra-regulations
```

### 응답 예시
```json
{
  "success": true,
  "updated_countries": ["중국", "미국"],
  "total_countries": 2,
  "update_time": "2024-01-15 14:30:00",
  "message": "2개 국가의 규제 정보가 업데이트되었습니다."
}
```

## 📁 캐시 파일 구조

```
regulation_cache/
├── kotra_중국_20240115.json
├── kotra_미국_20240115.json
└── kotra_all_countries_20240115_143000.json
```

## 🚀 사용 방법

### 1. 규제 정보 조회
```python
# KOTRA API를 통한 규제 정보 조회
regulation_info = mvp_system.kotra_api.get_country_regulations("중국")
```

### 2. 전체 국가 업데이트
```python
# 모든 지원 국가의 규제 정보 업데이트
results = mvp_system.kotra_api.update_all_countries()
```

### 3. API 상태 확인
```python
# KOTRA API 상태 확인
status = mvp_system.kotra_api.get_api_status()
```

## 🔍 데이터 우선순위

1. **KOTRA API** (최신 공공데이터)
2. **실시간 크롤러** (기존 시스템)
3. **MVP 규제 정보** (기본 데이터)
4. **기본 규제 정보** (최후 수단)

## ⚠️ 주의사항

### API 사용 제한
- 일일 호출 제한: 1,000회
- 초당 호출 제한: 10회
- 캐시 유효기간: 24시간

### 오류 처리
- API 키 미설정 시 기본 데이터 사용
- 네트워크 오류 시 캐시된 데이터 사용
- API 응답 오류 시 폴백 데이터 사용

### 데이터 정확성
- KOTRA API 데이터는 공공데이터포털에서 제공하는 공식 정보
- 실시간 업데이트되지만 약간의 지연이 있을 수 있음
- 중요한 결정 시 공식 출처 재확인 권장

## 🛠️ 문제 해결

### 1. API 키 인증 오류
```bash
# 환경변수 확인
echo $KOTRA_SERVICE_KEY

# Python에서 확인
python -c "import os; print(os.getenv('KOTRA_SERVICE_KEY'))"
```

### 2. 네트워크 연결 오류
```bash
# API 엔드포인트 연결 테스트
curl -I "https://www.data.go.kr/data/15034830/openapi.do"
```

### 3. 캐시 파일 오류
```bash
# 캐시 디렉토리 권한 확인
ls -la regulation_cache/

# 캐시 파일 삭제 후 재시도
rm -rf regulation_cache/*
```

## 📞 지원

### 공공데이터포털 지원
- 이메일: data@data.go.kr
- 전화: 02-2100-2500

### KATI 시스템 지원
- GitHub Issues: [KATI Repository](https://github.com/your-repo/kati)
- 이메일: support@kati.com

## 📈 성능 모니터링

### API 호출 통계
```python
# API 호출 횟수 확인
status = mvp_system.kotra_api.get_api_status()
print(f"API 호출 상태: {status['api_connection']}")
```

### 캐시 효율성
```python
# 캐시 파일 크기 확인
import os
cache_size = sum(os.path.getsize(f) for f in os.listdir('regulation_cache'))
print(f"캐시 크기: {cache_size / 1024:.2f} KB")
```

---

**마지막 업데이트**: 2024-01-15
**버전**: 1.0.0
**작성자**: KATI 개발팀 