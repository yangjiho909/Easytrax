# 🧪 폰트 테스트 Postman 가이드

## 📋 테스트 개요

중국어 폰트 깨짐 현상 해결을 위한 Postman 테스트 가이드입니다.

## 🔧 환경 설정

### 1. Postman 환경 변수 설정
```
BASE_URL: https://your-app.onrender.com
LOCAL_URL: http://localhost:5000
```

### 2. 테스트 컬렉션 생성
- **컬렉션명**: `KATI 폰트 테스트`
- **설명**: 중국어 폰트 깨짐 현상 해결 테스트

## 📊 API 테스트 목록

### 1. 폰트 상태 확인 API

#### 요청 정보
```
Method: GET
URL: {{BASE_URL}}/api/test-fonts
Headers: 
  Content-Type: application/json
```

#### 예상 응답
```json
{
  "font_status": {
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc": {
      "exists": true,
      "readable": true,
      "loadable": true,
      "font_name": "Noto Sans CJK"
    },
    "fonts/msyh.ttc": {
      "exists": true,
      "readable": true,
      "loadable": true,
      "font_name": "Microsoft YaHei"
    }
  },
  "environment": "production",
  "timestamp": "2024-12-19T10:30:00"
}
```

#### 테스트 스크립트
```javascript
// 폰트 상태 확인 테스트
pm.test("폰트 상태 확인", function () {
    const response = pm.response.json();
    
    // 응답 구조 확인
    pm.expect(response).to.have.property('font_status');
    pm.expect(response).to.have.property('environment');
    pm.expect(response).to.have.property('timestamp');
    
    // 폰트 상태 확인
    const fontStatus = response.font_status;
    let availableFonts = 0;
    
    for (const fontPath in fontStatus) {
        if (fontStatus[fontPath].loadable) {
            availableFonts++;
        }
    }
    
    // 최소 1개 이상의 폰트가 로드 가능해야 함
    pm.expect(availableFonts).to.be.at.least(1);
    
    console.log(`✅ 사용 가능한 폰트: ${availableFonts}개`);
});

// 환경 확인
pm.test("배포 환경 확인", function () {
    const response = pm.response.json();
    pm.expect(response.environment).to.be.oneOf(['production', 'development']);
});
```

### 2. 중국어 렌더링 테스트 API

#### 요청 정보
```
Method: GET
URL: {{BASE_URL}}/api/test-chinese-rendering
Headers: 
  Content-Type: application/json
```

#### 예상 응답
```json
{
  "success": true,
  "image_path": "test_chinese_rendering.png",
  "font_used": "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
  "test_text": "营养标签 营养成分表 过敏原信息"
}
```

#### 테스트 스크립트
```javascript
// 중국어 렌더링 테스트
pm.test("중국어 렌더링 성공", function () {
    const response = pm.response.json();
    
    // 성공 여부 확인
    pm.expect(response.success).to.be.true;
    
    // 이미지 생성 확인
    pm.expect(response).to.have.property('image_path');
    pm.expect(response.image_path).to.include('.png');
    
    // 폰트 사용 확인
    pm.expect(response).to.have.property('font_used');
    pm.expect(response.font_used).to.not.be.empty;
    
    // 테스트 텍스트 확인
    pm.expect(response).to.have.property('test_text');
    pm.expect(response.test_text).to.include('营养');
    
    console.log(`✅ 사용된 폰트: ${response.font_used}`);
    console.log(`✅ 생성된 이미지: ${response.image_path}`);
});

// 오류 처리 테스트
pm.test("오류 처리 확인", function () {
    const response = pm.response.json();
    
    if (!response.success) {
        pm.expect(response).to.have.property('error');
        pm.expect(response.error).to.be.a('string');
        console.log(`❌ 렌더링 실패: ${response.error}`);
    }
});
```

### 3. 헬스 체크 API

#### 요청 정보
```
Method: GET
URL: {{BASE_URL}}/api/health
Headers: 
  Content-Type: application/json
```

#### 테스트 스크립트
```javascript
// 헬스 체크 테스트
pm.test("서버 상태 확인", function () {
    const response = pm.response.json();
    
    pm.expect(response.status).to.equal('healthy');
    pm.expect(response).to.have.property('timestamp');
    pm.expect(response).to.have.property('service');
    
    console.log(`✅ 서버 상태: ${response.status}`);
    console.log(`✅ 서비스: ${response.service}`);
});
```

## 🧪 통합 테스트

### 1. 폰트 설치 확인 테스트

#### 요청 정보
```
Method: GET
URL: {{BASE_URL}}/api/test-fonts
```

#### 테스트 스크립트
```javascript
// 폰트 설치 종합 테스트
pm.test("폰트 설치 종합 확인", function () {
    const response = pm.response.json();
    const fontStatus = response.font_status;
    
    // 필수 폰트 확인
    const requiredFonts = [
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "fonts/msyh.ttc",
        "fonts/simsun.ttc"
    ];
    
    let installedCount = 0;
    let loadableCount = 0;
    
    for (const fontPath of requiredFonts) {
        if (fontStatus[fontPath] && fontStatus[fontPath].exists) {
            installedCount++;
        }
        if (fontStatus[fontPath] && fontStatus[fontPath].loadable) {
            loadableCount++;
        }
    }
    
    console.log(`📦 설치된 폰트: ${installedCount}/${requiredFonts.length}`);
    console.log(`✅ 로드 가능한 폰트: ${loadableCount}/${requiredFonts.length}`);
    
    // 최소 1개 이상의 폰트가 로드 가능해야 함
    pm.expect(loadableCount).to.be.at.least(1);
});
```

### 2. 중국어 라벨 생성 테스트

#### 요청 정보
```
Method: POST
URL: {{BASE_URL}}/api/ocr-extract
Headers: 
  Content-Type: application/json
Body:
{
  "country": "중국",
  "product_info": {
    "product_name": "테스트라면",
    "manufacturer": "테스트회사",
    "nutrition": {
      "calories": "400",
      "protein": "12",
      "fat": "15",
      "carbs": "60",
      "sodium": "800"
    },
    "allergies": ["대두", "밀"]
  }
}
```

#### 테스트 스크립트
```javascript
// 중국어 라벨 생성 테스트
pm.test("중국어 라벨 생성 확인", function () {
    const response = pm.response.json();
    
    // 성공 여부 확인
    pm.expect(response.success).to.be.true;
    
    // 라벨 이미지 생성 확인
    if (response.label_image) {
        pm.expect(response.label_image).to.include('.png');
        console.log(`✅ 라벨 이미지 생성: ${response.label_image}`);
    }
    
    // 중국어 텍스트 포함 확인
    if (response.label_text) {
        pm.expect(response.label_text).to.include('营养');
        console.log(`✅ 중국어 텍스트 포함: ${response.label_text.substring(0, 50)}...`);
    }
});
```

## 📊 테스트 결과 분석

### 1. 성공 기준
- ✅ 폰트 상태 API: 최소 1개 폰트 로드 가능
- ✅ 중국어 렌더링 API: 이미지 생성 성공
- ✅ 헬스 체크 API: 서버 상태 정상
- ✅ 중국어 라벨 생성: 중국어 텍스트 포함

### 2. 실패 시 대응
- ❌ 폰트 로드 실패: 서버 폰트 설치 확인
- ❌ 렌더링 실패: 폰트 경로 및 권한 확인
- ❌ 라벨 생성 실패: 폰트 폴백 체인 확인

## 🔄 자동화 테스트

### 1. Postman Runner 설정
```
Iterations: 3
Delay: 1000ms
Data File: test_data.json
```

### 2. 테스트 데이터 파일
```json
[
  {
    "country": "중국",
    "product_name": "테스트라면1",
    "expected_font": "NotoSansCJK"
  },
  {
    "country": "중국", 
    "product_name": "테스트라면2",
    "expected_font": "msyh"
  }
]
```

### 3. 자동화 스크립트
```javascript
// 자동화 테스트 스크립트
pm.test("자동화 테스트", function () {
    const testData = pm.iterationData.get("country");
    const response = pm.response.json();
    
    // 데이터 기반 테스트
    if (testData === "중국") {
        pm.expect(response.success).to.be.true;
        console.log(`✅ ${testData} 테스트 통과`);
    }
});
```

## 📈 성능 테스트

### 1. 응답 시간 테스트
```javascript
// 응답 시간 확인
pm.test("응답 시간 확인", function () {
    pm.expect(pm.response.responseTime).to.be.below(5000); // 5초 이하
    console.log(`⏱️ 응답 시간: ${pm.response.responseTime}ms`);
});
```

### 2. 메모리 사용량 확인
```javascript
// 메모리 사용량 확인 (서버 로그 기반)
pm.test("메모리 사용량 확인", function () {
    const response = pm.response.json();
    
    if (response.memory_usage) {
        pm.expect(response.memory_usage).to.be.below(500); // 500MB 이하
        console.log(`💾 메모리 사용량: ${response.memory_usage}MB`);
    }
});
```

## 🚀 배포 후 테스트

### 1. 배포 확인 체크리스트
- [ ] `/api/health` - 서버 상태 확인
- [ ] `/api/test-fonts` - 폰트 설치 확인
- [ ] `/api/test-chinese-rendering` - 렌더링 테스트
- [ ] 실제 라벨 생성 테스트

### 2. 모니터링 설정
```javascript
// 모니터링 스크립트
pm.test("모니터링", function () {
    const response = pm.response.json();
    
    // 성공률 계산
    if (response.success) {
        console.log("✅ 성공");
    } else {
        console.log("❌ 실패");
        // 알림 발송 로직
    }
});
```

---

**마지막 업데이트**: 2024년 12월 19일  
**테스트 환경**: Postman v10+  
**권장 브라우저**: Chrome, Firefox, Safari 