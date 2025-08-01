# 🎨 폰트 설정 가이드

## 📁 폰트 폴더 구조
```
fonts/
├── README.md                    # 이 파일
├── msyh.ttc                     # Microsoft YaHei (중국어, 영어, 한글)
├── simsun.ttc                   # SimSun (중국어, 영어)
├── simhei.ttf                   # SimHei (중국어)
├── malgun.ttf                   # 맑은 고딕 (한글)
└── arial.ttf                    # Arial (영어)
```

## 🌍 국가별 폰트 지원

### 🇨🇳 중국 (중국어)
- **주요 폰트**: Microsoft YaHei (msyh.ttc)
- **대체 폰트**: SimSun (simsun.ttc), SimHei (simhei.ttf)
- **지원 문자**: 중국어 간체, 영어, 숫자

### 🇺🇸 미국 (영어)
- **주요 폰트**: Arial (arial.ttf)
- **대체 폰트**: Microsoft YaHei (msyh.ttc)
- **지원 문자**: 영어, 숫자

### 🇰🇷 한국 (한글)
- **주요 폰트**: 맑은 고딕 (malgun.ttf)
- **대체 폰트**: Microsoft YaHei (msyh.ttc)
- **지원 문자**: 한글, 영어, 숫자

## 🔧 폰트 설치 방법

### 로컬 개발 환경 (Windows)
1. Windows 폰트 폴더에서 폰트 파일 복사
2. `fonts/` 폴더에 붙여넣기
3. Git에 추가하여 배포 환경에서 사용

### 배포 환경 (Linux/Render)
1. 폰트 파일을 `fonts/` 폴더에 포함
2. Git에 커밋하여 배포 시 자동 포함
3. 상대 경로로 폰트 로드

## 📋 필요한 폰트 파일 목록

### 필수 폰트 (배포용)
- [ ] `msyh.ttc` - Microsoft YaHei (다국어 지원)
- [ ] `simsun.ttc` - SimSun (중국어)
- [ ] `malgun.ttf` - 맑은 고딕 (한글)
- [ ] `arial.ttf` - Arial (영어)

### 선택 폰트 (고급 지원)
- [ ] `simhei.ttf` - SimHei (중국어 굵은체)
- [ ] `simkai.ttf` - SimKai (중국어 필기체)
- [ ] `simfang.ttf` - SimFang (중국어 장식체)

## 🚀 폰트 로드 우선순위

### 중국어 라벨 생성 시
1. `fonts/msyh.ttc` (Microsoft YaHei)
2. `fonts/simsun.ttc` (SimSun)
3. `fonts/simhei.ttf` (SimHei)
4. Linux 시스템 폰트
5. 기본 폰트 (폴백)

### 영어 라벨 생성 시
1. `fonts/arial.ttf` (Arial)
2. `fonts/msyh.ttc` (Microsoft YaHei)
3. Linux 시스템 폰트
4. 기본 폰트 (폴백)

## ⚠️ 주의사항

### 폰트 라이선스
- Microsoft YaHei, SimSun 등은 Microsoft 라이선스 적용
- 상업적 사용 시 라이선스 확인 필요
- 오픈소스 대안 폰트 고려 (Noto Sans CJK 등)

### 파일 크기
- 폰트 파일은 크기가 큼 (수 MB)
- Git 저장소 크기 증가
- 배포 시간 증가 가능

### 대안 방안
1. **웹폰트 사용**: Google Fonts, Adobe Fonts 등
2. **오픈소스 폰트**: Noto Sans CJK, Source Han Sans 등
3. **폰트 서브셋**: 필요한 문자만 포함한 경량 폰트

## 🔍 문제 해결

### 폰트 로드 실패 시
1. 폰트 파일 존재 여부 확인
2. 파일 경로 정확성 확인
3. 파일 권한 확인
4. 대체 폰트 시도
5. 기본 폰트로 폴백

### 중국어 표시 문제
1. UTF-8 인코딩 확인
2. 중국어 폰트 로드 확인
3. 텍스트 렌더링 로그 확인
4. 폰트 폴백 체인 확인

---

**마지막 업데이트**: 2024년 12월 19일
**폰트 버전**: 1.0 