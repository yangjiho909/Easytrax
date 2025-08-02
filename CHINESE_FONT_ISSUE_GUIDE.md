# 🇨🇳 중국어 폰트 깨짐 현상 해결 가이드

## 🔍 문제 분석

### 현재 상황
- **로컬 환경**: 중국어 폰트가 정상적으로 표시됨
- **배포 환경**: 중국어 문자가 □□ 또는 ? 로 깨져서 출력됨
- **원인**: 배포 환경(Render/Linux)에서 중국어 폰트가 설치되지 않거나 로드되지 않음

### 기술적 원인
1. **폰트 파일 누락**: 배포 환경에 중국어 폰트 파일이 없음
2. **폰트 경로 문제**: Linux 환경에서 Windows 폰트 경로 사용
3. **폰트 라이선스**: 상용 폰트의 배포 환경 사용 제한
4. **시스템 폰트 부재**: Linux 서버에 중국어 폰트 미설치

## 🛠️ 해결 방안

### 1. 즉시 해결책 (임시)

#### A. 웹폰트 사용
```html
<!-- HTML 템플릿에 추가 -->
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700&display=swap" rel="stylesheet">
<style>
.chinese-text {
    font-family: 'Noto Sans SC', 'Microsoft YaHei', sans-serif;
}
</style>
```

#### B. 폰트 폴백 체인 개선
```python
# app.py의 폰트 로드 부분 수정
font_paths = [
    # 오픈소스 폰트 우선
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansSC-Regular.otf",
    # 프로젝트 내 폰트
    "fonts/msyh.ttc",
    "fonts/simsun.ttc",
    # 시스템 기본 폰트
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]
```

### 2. 근본적 해결책

#### A. 오픈소스 폰트 설치 (권장)
```bash
# Render 배포 환경에서 실행
sudo apt-get update
sudo apt-get install fonts-noto-cjk fonts-noto-cjk-extra
```

#### B. 폰트 파일 직접 포함
```python
# requirements.txt에 추가
# 폰트 설치 스크립트 포함
```

#### C. 폰트 서브셋 사용
```python
# 필요한 문자만 포함한 경량 폰트 생성
from fonttools import subset
subset.main([
    'fonts/msyh.ttc',
    '--text-file=chinese_chars.txt',
    '--output-file=fonts/msyh_subset.ttf'
])
```

## 📋 구현 단계

### 단계 1: 웹폰트 적용 (즉시)
1. HTML 템플릿에 Google Fonts 추가
2. CSS에서 폰트 패밀리 설정
3. 중국어 텍스트에 클래스 적용

### 단계 2: 서버 폰트 설치 (1-2일)
1. Render 빌드 스크립트에 폰트 설치 명령 추가
2. 오픈소스 폰트 다운로드 및 설치
3. 폰트 경로 업데이트

### 단계 3: 폰트 최적화 (3-5일)
1. 폰트 서브셋 생성
2. 폰트 캐싱 구현
3. 성능 최적화

## 🔧 코드 수정 예시

### HTML 템플릿 수정
```html
<!-- templates/nutrition_label.html -->
<head>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700&family=Noto+Sans+KR:wght@400;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --font-family: 'Noto Sans KR', sans-serif;
            --chinese-font-family: 'Noto Sans SC', 'Noto Sans KR', sans-serif;
        }
        
        .chinese-text {
            font-family: var(--chinese-font-family);
        }
    </style>
</head>
```

### Python 폰트 로드 개선
```python
def load_chinese_font():
    """중국어 폰트 로드 (개선된 버전)"""
    font_paths = [
        # 오픈소스 폰트 (우선)
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansSC-Regular.otf",
        # 프로젝트 폰트
        "fonts/msyh.ttc",
        "fonts/simsun.ttc",
        # 시스템 폰트
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    
    for font_path in font_paths:
        try:
            if os.path.exists(font_path):
                font = ImageFont.truetype(font_path, 20)
                print(f"✅ 폰트 로드 성공: {font_path}")
                return font
        except Exception as e:
            print(f"❌ 폰트 로드 실패: {font_path} - {e}")
    
    # 최종 폴백
    return ImageFont.load_default()
```

## 🚀 배포 환경 설정

### Render 설정 파일 수정
```yaml
# render.yaml
services:
  - type: web
    name: kati-export-helper
    env: python
    plan: free
    buildCommand: |
      pip install -r requirements.txt
      # 폰트 설치
      sudo apt-get update
      sudo apt-get install -y fonts-noto-cjk fonts-noto-cjk-extra
    startCommand: gunicorn app:app
```

### 빌드 스크립트 추가
```bash
# build.sh
#!/bin/bash
# 폰트 설치
sudo apt-get update
sudo apt-get install -y fonts-noto-cjk fonts-noto-cjk-extra

# 폰트 캐시 업데이트
sudo fc-cache -fv

# Python 패키지 설치
pip install -r requirements.txt
```

## 📊 테스트 방법

### 1. 폰트 로드 테스트
```python
@app.route('/api/test-fonts')
def test_fonts():
    """폰트 로드 상태 테스트"""
    font_status = {}
    
    test_paths = [
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "fonts/msyh.ttc",
        "fonts/simsun.ttc"
    ]
    
    for path in test_paths:
        font_status[path] = {
            'exists': os.path.exists(path),
            'readable': os.access(path, os.R_OK) if os.path.exists(path) else False
        }
    
    return jsonify(font_status)
```

### 2. 중국어 렌더링 테스트
```python
@app.route('/api/test-chinese-rendering')
def test_chinese_rendering():
    """중국어 렌더링 테스트"""
    test_text = "营养标签 营养成分表 过敏原信息"
    
    # 폰트 로드 테스트
    font = load_chinese_font()
    
    # 이미지 생성 테스트
    image = Image.new('RGB', (400, 100), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    try:
        draw.text((10, 10), test_text, fill=(0, 0, 0), font=font)
        # 이미지 저장
        image_path = "test_chinese_rendering.png"
        image.save(image_path)
        return jsonify({'success': True, 'image_path': image_path})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
```

## ⚠️ 주의사항

### 폰트 라이선스
- Microsoft YaHei, SimSun은 상용 폰트
- 배포 환경에서 사용 시 라이선스 확인 필요
- 오픈소스 폰트(Noto Sans CJK) 사용 권장

### 성능 고려사항
- 폰트 파일 크기가 큼 (수 MB)
- 로딩 시간 증가 가능
- 폰트 서브셋 사용으로 최적화

### 호환성
- 다양한 브라우저 지원 확인
- 모바일 환경 테스트 필요
- 폰트 폴백 체인 검증

## 📈 모니터링

### 폰트 로드 상태 모니터링
```python
def monitor_font_loading():
    """폰트 로드 상태 모니터링"""
    font_stats = {
        'total_requests': 0,
        'successful_loads': 0,
        'failed_loads': 0,
        'fallback_usage': 0
    }
    return font_stats
```

### 사용자 피드백 수집
```python
@app.route('/api/font-feedback', methods=['POST'])
def collect_font_feedback():
    """폰트 표시 문제 피드백 수집"""
    feedback = request.json
    # 피드백 저장 및 분석
    return jsonify({'status': 'received'})
```

---

**마지막 업데이트**: 2024년 12월 19일  
**해결 우선순위**: 높음 (사용자 경험에 직접적 영향)  
**예상 소요 시간**: 1-3일 