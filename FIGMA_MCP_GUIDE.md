# 🎨 피그마 MCP 연동 가이드

## 📋 개요

이 가이드는 피그마 디자인을 현재 웹 앱에 MCP(Model Context Protocol) 기능을 활용하여 적용하는 방법을 설명합니다.

## 🚀 시작하기

### 1. 피그마 액세스 토큰 설정

#### **1.1 피그마에서 토큰 생성**
1. 피그마 계정에 로그인
2. Settings → Account → Personal access tokens
3. "Create new token" 클릭
4. 토큰 이름 입력 (예: "MCP Integration")
5. 토큰 복사

#### **1.2 환경변수 설정**

**Windows (PowerShell):**
```powershell
$env:FIGMA_ACCESS_TOKEN="your_figma_token_here"
```

**Windows (Command Prompt):**
```cmd
set FIGMA_ACCESS_TOKEN=your_figma_token_here
```

**macOS/Linux:**
```bash
export FIGMA_ACCESS_TOKEN="your_figma_token_here"
```

### 2. 피그마 파일 키 확인

피그마 파일 URL에서 파일 키를 추출:
```
https://www.figma.com/file/XXXXXXXXXXXXXXX/Design-Name
                    ↑
                파일 키
```

## 🎨 디자인 적용 방법

### **방법 1: 자동 적용 (권장)**

```bash
python apply_figma_design.py
```

**단계:**
1. 피그마 파일 키 입력
2. 자동으로 디자인 토큰 추출
3. CSS 파일 생성
4. 템플릿 업데이트
5. 컴포넌트 스타일 적용

### **방법 2: 수동 설정**

```bash
python figma_mcp_setup.py
```

**단계:**
1. 피그마 파일 키 입력
2. 디자인 토큰 추출
3. CSS 파일 생성
4. 수동으로 템플릿에 적용

## 📁 생성되는 파일들

### **디자인 파일**
- `figma_design/figma-design-tokens.css` - 메인 CSS 파일
- `figma_design/design-tokens.json` - 디자인 토큰 데이터
- `figma_design/components.json` - 컴포넌트 정보

### **적용된 파일**
- `static/figma-design.css` - 웹 앱에 적용된 CSS
- `templates/*.html` - 업데이트된 템플릿
- `FIGMA_DESIGN_SYSTEM.md` - 디자인 시스템 문서

### **백업 파일**
- `templates_backup/` - 원본 템플릿 백업

## 🎨 디자인 토큰 사용법

### **CSS 변수 사용**
```css
/* 피그마에서 추출된 색상 사용 */
.my-component {
    background-color: var(--color-primary);
    color: var(--color-text);
}
```

### **컴포넌트 클래스 사용**
```html
<!-- 피그마 컴포넌트 적용 -->
<div class="figma-card">
    <h2 class="figma-heading">제목</h2>
    <button class="figma-btn">버튼</button>
</div>
```

## 🔧 커스터마이징

### **디자인 토큰 수정**
`figma_design/design-tokens.json` 파일을 직접 수정하여 색상, 폰트, 간격 등을 조정할 수 있습니다.

### **컴포넌트 스타일 수정**
`static/figma-design.css` 파일에서 컴포넌트별 스타일을 수정할 수 있습니다.

### **새로운 컴포넌트 추가**
```css
/* 새로운 피그마 컴포넌트 스타일 */
.my-custom-component {
    /* 피그마 디자인 토큰 사용 */
    background-color: var(--color-primary);
    border-radius: var(--spacing-sm);
    box-shadow: var(--shadow-medium);
}
```

## 🔄 업데이트 프로세스

### **피그마 디자인 변경 시**
1. 피그마에서 디자인 수정
2. 다시 스크립트 실행
3. 자동으로 새로운 디자인 적용

### **수동 업데이트**
```bash
# 기존 디자인 제거
rm -rf figma_design/
rm -rf static/figma-design.css

# 새로운 디자인 적용
python apply_figma_design.py
```

## 🐛 문제 해결

### **토큰 오류**
```
❌ FIGMA_ACCESS_TOKEN 환경변수가 설정되지 않았습니다.
```
**해결:** 환경변수를 올바르게 설정했는지 확인

### **파일 키 오류**
```
❌ 피그마 파일 연결 실패: 404
```
**해결:** 파일 키가 올바른지, 파일에 접근 권한이 있는지 확인

### **CSS 적용 안됨**
**해결:**
1. 웹 서버 재시작
2. 브라우저 캐시 삭제
3. CSS 파일 경로 확인

## 📊 MCP 기능

### **지원하는 기능**
- ✅ 디자인 토큰 추출
- ✅ 컴포넌트 추출
- ✅ CSS 코드 생성
- ✅ 스타일 동기화
- ✅ 자동 템플릿 업데이트

### **향후 확장 예정**
- 🔄 실시간 디자인 동기화
- 🔄 피그마 플러그인 연동
- 🔄 디자인 버전 관리
- 🔄 팀 협업 기능

## 📞 지원

### **문서**
- `FIGMA_DESIGN_SYSTEM.md` - 디자인 시스템 문서
- `figma_design/design-tokens.json` - 토큰 참조
- `figma_design/components.json` - 컴포넌트 참조

### **로그 확인**
```bash
# 피그마 연결 테스트
python figma_mcp_setup.py

# 디자인 적용 상태 확인
python apply_figma_design.py
```

## 🎉 완료!

피그마 디자인이 성공적으로 웹 앱에 적용되었습니다!

**확인 방법:**
1. 웹 서버 재시작: `python app.py`
2. 브라우저에서 확인: `http://localhost:5000`
3. 디자인 변경사항 확인

---

**💡 팁:** 피그마에서 디자인을 수정할 때마다 이 프로세스를 반복하면 항상 최신 디자인을 유지할 수 있습니다! 