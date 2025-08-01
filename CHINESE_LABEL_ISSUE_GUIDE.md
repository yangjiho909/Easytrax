# 🇨🇳 중국어 라벨 생성 문제 해결 가이드

## 🔍 문제 현상

### 🏠 로컬호스트 (정상)
- ✅ 중국어 라벨 이미지 정상 생성
- ✅ 중국어 텍스트 정상 표시
- ✅ Microsoft YaHei, SimSun 폰트 사용

### 🌐 배포 환경 (문제)
- ❌ 중국어 라벨 이미지 생성 실패
- ❌ 중국어 텍스트 깨짐 또는 표시 안됨
- ⚠️ 폰트 로드 실패로 텍스트만 반환

## 🎯 문제 원인

### 1. **폰트 파일 부재**
- 배포 환경(Linux)에 중국어 폰트 설치 안됨
- Windows 전용 폰트 경로 사용 불가
- 시스템 폰트에 중국어 지원 폰트 없음

### 2. **환경별 폰트 경로 차이**
```python
# 로컬 환경 (Windows)
"C:/Windows/Fonts/msyh.ttc"  # ✅ 접근 가능

# 배포 환경 (Linux)
"C:/Windows/Fonts/msyh.ttc"  # ❌ 접근 불가
"/usr/share/fonts/..."       # ⚠️ 중국어 폰트 없음
```

### 3. **PIL/Pillow 폰트 로드 실패**
- 중국어 폰트 파일 없음
- 폰트 로드 실패 시 기본 폰트 사용
- 기본 폰트는 중국어 지원 안함

## 🛠️ 해결 방안

### 1. **폰트 파일 프로젝트 포함** (권장)

#### 단계별 해결 과정:
1. **폰트 파일 복사**
   ```bash
   # Windows 폰트 폴더에서 복사
   copy "C:\Windows\Fonts\msyh.ttc" "fonts\msyh.ttc"
   copy "C:\Windows\Fonts\simsun.ttc" "fonts\simsun.ttc"
   copy "C:\Windows\Fonts\simhei.ttf" "fonts\simhei.ttf"
   copy "C:\Windows\Fonts\malgun.ttf" "fonts\malgun.ttf"
   ```

2. **Git에 추가**
   ```bash
   git add fonts/
   git commit -m "Add Chinese fonts for deployment"
   git push
   ```

3. **폰트 로드 우선순위 변경**
   ```python
   # 프로젝트 내 폰트 폴더를 최우선으로
   font_paths = [
       "fonts/msyh.ttc",        # 최우선
       "fonts/simsun.ttc",      # 대체
       # ... 기타 경로
   ]
   ```

### 2. **폰트 로드 로직 개선**

#### 개선된 폰트 로드 순서:
1. `fonts/msyh.ttc` (Microsoft YaHei)
2. `fonts/simsun.ttc` (SimSun)
3. `fonts/simhei.ttf` (SimHei)
4. Linux 시스템 폰트
5. 기본 폰트 (폴백)

#### 폰트 로드 실패 시 개선된 폴백:
```python
if font is None:
    # 중국어 텍스트로 라벨 내용 생성
    label_text = f"""중국어 영양성분표 (폰트 로드 실패)
    
    제품명: {product_name}
    영양성분표 (每100g):
    - 能量: {calories} kcal
    - 蛋白质: {protein}g
    ...
    """
```

### 3. **대안 방안**

#### A. 오픈소스 폰트 사용
```python
# Noto Sans CJK (Google)
"/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"

# Source Han Sans (Adobe)
"/usr/share/fonts/truetype/source-han-sans/SourceHanSans-Regular.ttc"
```

#### B. 웹폰트 사용
```html
<!-- Google Fonts -->
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC&display=swap" rel="stylesheet">
```

#### C. 폰트 서브셋 생성
```bash
# 필요한 문자만 포함한 경량 폰트 생성
pyftsubset msyh.ttc --text="营养成分表每100g能量蛋白质脂肪碳水化合物钠" --output-file=msyh-subset.ttc
```

## 📋 구현 체크리스트

### ✅ 완료된 항목
- [x] 폰트 로드 우선순위 개선
- [x] 폰트 로드 실패 시 폴백 처리
- [x] 중국어 텍스트 폴백 생성
- [x] 폰트 설정 가이드 문서화

### ⏳ 대기 중인 항목
- [ ] 폰트 파일 프로젝트에 추가
- [ ] Git에 폰트 파일 커밋
- [ ] 배포 환경에서 테스트
- [ ] 중국어 라벨 생성 확인

## 🔧 테스트 방법

### 로컬 테스트
```bash
# 폰트 파일 존재 확인
ls fonts/

# 중국어 라벨 생성 테스트
curl -X POST http://localhost:5000/api/nutrition-label \
  -H "Content-Type: application/json" \
  -d '{"country": "중국", "product_name": "라면"}'
```

### 배포 환경 테스트
```bash
# 배포 후 폰트 로드 확인
# 로그에서 폰트 로드 성공/실패 확인
# 중국어 라벨 이미지 생성 확인
```

## 📊 예상 결과

### 폰트 파일 추가 후
| 환경 | 중국어 라벨 | 영어 라벨 | 한글 라벨 |
|------|-------------|-----------|-----------|
| 로컬호스트 | ✅ 정상 | ✅ 정상 | ✅ 정상 |
| 배포 환경 | ✅ 정상 | ✅ 정상 | ✅ 정상 |

### 폰트 파일 없이
| 환경 | 중국어 라벨 | 영어 라벨 | 한글 라벨 |
|------|-------------|-----------|-----------|
| 로컬호스트 | ✅ 정상 | ✅ 정상 | ✅ 정상 |
| 배포 환경 | ⚠️ 텍스트만 | ✅ 정상 | ⚠️ 텍스트만 |

## 🚨 주의사항

### 폰트 라이선스
- Microsoft YaHei, SimSun은 Microsoft 라이선스 적용
- 상업적 사용 시 라이선스 확인 필요
- 오픈소스 폰트 사용 권장

### 파일 크기
- 폰트 파일은 수 MB 크기
- Git 저장소 크기 증가
- 배포 시간 증가 가능

### 대안 고려
1. **웹폰트 사용**: Google Fonts, Adobe Fonts
2. **오픈소스 폰트**: Noto Sans CJK, Source Han Sans
3. **폰트 서브셋**: 필요한 문자만 포함

---

**마지막 업데이트**: 2024년 12월 19일
**문제 상태**: 해결 방안 구현 완료, 폰트 파일 추가 대기 