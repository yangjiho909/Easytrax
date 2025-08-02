# 🇨🇳 중국어 폰트 깨짐 현상 해결 가이드

## 🔍 문제 진단

### 현재 상황 분석
- **로컬 환경**: ✅ 중국어 폰트 정상 표시
- **배포 환경**: ❌ 중국어 문자가 □□ 또는 ? 로 깨짐
- **영향 범위**: 중국어 라벨 생성, 웹페이지 중국어 텍스트

### 원인 분석
1. **폰트 파일 누락**: 배포 환경(Render/Linux)에 중국어 폰트 미설치
2. **폰트 경로 문제**: Windows 경로를 Linux에서 사용
3. **라이선스 제한**: 상용 폰트의 배포 환경 사용 제한
4. **시스템 폰트 부재**: Linux 서버에 CJK 폰트 미설치

## 🛠️ 해결 방안

### 1. 즉시 해결책 (웹폰트)

#### A. HTML 템플릿 수정 ✅ 완료
```html
<!-- templates/nutrition_label.html에 이미 적용됨 -->
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700&family=Noto+Sans+KR:wght@400;700&display=swap" rel="stylesheet">

<style>
.chinese-text {
    font-family: 'Noto Sans SC', 'Noto Sans KR', sans-serif;
}
</style>
```

#### B. CSS 클래스 적용
```html
<!-- 중국어 텍스트에 클래스 적용 -->
<div class="chinese-text">营养标签 营养成分表</div>
```

### 2. 서버 폰트 설치 (근본적 해결)

#### A. Render 설정 수정 ✅ 완료
```yaml
# render.yaml
buildCommand: |
  # 폰트 설치 (중국어 지원)
  sudo apt-get update
  sudo apt-get install -y fonts-noto-cjk fonts-noto-cjk-extra
  sudo fc-cache -fv
  # Python 패키지 설치
  pip install -r requirements.txt
```

#### B. 빌드 스크립트 ✅ 완료
```bash
# build.sh
#!/bin/bash
sudo apt-get update
sudo apt-get install -y fonts-noto-cjk fonts-noto-cjk-extra
sudo fc-cache -fv
pip install -r requirements.txt
```

### 3. Python 코드 개선 ✅ 완료

#### A. 폰트 로드 우선순위 개선
```python
# app.py의 폰트 경로 수정
font_paths = [
    # 오픈소스 폰트 (배포 환경 우선)
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansSC-Regular.otf",
    # 프로젝트 폰트
    "fonts/msyh.ttc",
    "fonts/simsun.ttc",
]
```

#### B. 폰트 테스트 API 추가 ✅ 완료
```python
@app.route('/api/test-fonts')
def test_fonts():
    """폰트 로드 상태 테스트"""
    # 폰트 존재 여부, 읽기 권한, 로드 가능성 확인

@app.route('/api/test-chinese-rendering')
def test_chinese_rendering():
    """중국어 렌더링 테스트"""
    # 실제 중국어 텍스트 렌더링 테스트
```

## 📋 테스트 방법

### 1. 폰트 상태 확인
```bash
# API 호출
curl https://your-app.onrender.com/api/test-fonts
```

### 2. 중국어 렌더링 테스트
```bash
# API 호출
curl https://your-app.onrender.com/api/test-chinese-rendering
```

### 3. 웹페이지 테스트
```bash
# 브라우저에서 확인
https://your-app.onrender.com/nutrition-label
```

## 🔧 추가 최적화

### 1. 폰트 서브셋 생성 (선택사항)
```python
# 필요한 문자만 포함한 경량 폰트
from fonttools import subset

chinese_chars = "营养标签营养成分表过敏原信息"
subset.main([
    'fonts/msyh.ttc',
    '--text=' + chinese_chars,
    '--output-file=fonts/msyh_subset.ttf'
])
```

### 2. 폰트 캐싱 구현
```python
# 폰트 캐시 매니저
class FontCache:
    def __init__(self):
        self.fonts = {}
    
    def get_font(self, font_path, size):
        key = f"{font_path}_{size}"
        if key not in self.fonts:
            self.fonts[key] = ImageFont.truetype(font_path, size)
        return self.fonts[key]
```

### 3. 폰트 폴백 체인 최적화
```python
def load_optimal_font(country, size=20):
    """국가별 최적 폰트 로드"""
    if country == "중국":
        return load_chinese_font(size)
    elif country == "일본":
        return load_japanese_font(size)
    else:
        return load_default_font(size)
```

## 📊 모니터링

### 1. 폰트 로드 통계
```python
font_stats = {
    'total_requests': 0,
    'successful_loads': 0,
    'failed_loads': 0,
    'fallback_usage': 0
}
```

### 2. 사용자 피드백 수집
```python
@app.route('/api/font-feedback', methods=['POST'])
def collect_font_feedback():
    """폰트 표시 문제 피드백 수집"""
    feedback = request.json
    # 피드백 저장 및 분석
    return jsonify({'status': 'received'})
```

## ⚠️ 주의사항

### 폰트 라이선스
- **Microsoft YaHei, SimSun**: 상용 폰트, 배포 환경 사용 시 라이선스 확인 필요
- **Noto Sans CJK**: 오픈소스, 상업적 사용 가능
- **권장사항**: 오픈소스 폰트 사용

### 성능 고려사항
- **폰트 파일 크기**: 수 MB로 큰 용량
- **로딩 시간**: 초기 로딩 시 지연 가능
- **메모리 사용**: 폰트 캐싱으로 최적화

### 호환성
- **브라우저 지원**: 모든 최신 브라우저 지원
- **모바일 환경**: 반응형 폰트 크기 적용
- **접근성**: 고대비 모드 지원

## 🚀 배포 체크리스트

### 배포 전 확인사항
- [ ] `render.yaml` 폰트 설치 명령 추가
- [ ] `build.sh` 스크립트 실행 권한 확인
- [ ] 폰트 테스트 API 동작 확인
- [ ] 웹폰트 로드 확인

### 배포 후 확인사항
- [ ] `/api/test-fonts` API 호출하여 폰트 설치 확인
- [ ] `/api/test-chinese-rendering` API로 렌더링 테스트
- [ ] 실제 중국어 라벨 생성 테스트
- [ ] 웹페이지 중국어 텍스트 표시 확인

## 📈 성능 최적화

### 1. 폰트 로딩 최적화
```html
<!-- 폰트 프리로드 -->
<link rel="preload" href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC" as="style">
```

### 2. 폰트 서브셋 최적화
```css
/* 필요한 문자만 포함 */
@font-face {
    font-family: 'Noto Sans SC Subset';
    src: url('fonts/noto-sans-sc-subset.woff2') format('woff2');
    unicode-range: U+4E00-9FFF; /* 중국어 범위 */
}
```

### 3. 폰트 캐싱 전략
```python
# 서버 사이드 폰트 캐싱
FONT_CACHE = {}
FONT_CACHE_TTL = 3600  # 1시간

def get_cached_font(font_path, size):
    cache_key = f"{font_path}_{size}"
    if cache_key in FONT_CACHE:
        return FONT_CACHE[cache_key]
    
    font = ImageFont.truetype(font_path, size)
    FONT_CACHE[cache_key] = font
    return font
```

## 🔍 문제 해결 가이드

### 폰트 로드 실패 시
1. **폰트 파일 존재 확인**: `ls -la /usr/share/fonts/truetype/noto/`
2. **폰트 권한 확인**: `ls -la fonts/`
3. **폰트 캐시 업데이트**: `sudo fc-cache -fv`
4. **대체 폰트 시도**: 프로젝트 내 폰트 사용
5. **기본 폰트 폴백**: `ImageFont.load_default()`

### 중국어 표시 문제 시
1. **UTF-8 인코딩 확인**: 파일 인코딩 확인
2. **폰트 로드 로그 확인**: 콘솔 로그 분석
3. **브라우저 개발자 도구**: 네트워크 탭에서 폰트 로드 확인
4. **폰트 폴백 체인 확인**: CSS 폰트 스택 검증

---

**마지막 업데이트**: 2024년 12월 19일  
**해결 우선순위**: 높음 (사용자 경험에 직접적 영향)  
**예상 소요 시간**: 1-3일  
**상태**: ✅ 구현 완료, 테스트 필요 