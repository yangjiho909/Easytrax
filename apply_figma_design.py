#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎨 피그마 디자인을 현재 웹 앱에 적용
- 기존 템플릿에 피그마 디자인 적용
- 디자인 토큰 통합
- 컴포넌트 스타일 업데이트
"""

import json
import shutil
from pathlib import Path
from figma_mcp_setup import FigmaMCPConnector

class FigmaDesignApplier:
    """피그마 디자인을 웹 앱에 적용하는 시스템"""
    
    def __init__(self):
        self.templates_dir = "templates"
        self.static_dir = "static"
        self.figma_design_dir = "figma_design"
        
    def apply_figma_design_to_templates(self, figma_file_key: str):
        """피그마 디자인을 템플릿에 적용"""
        
        print("🎨 피그마 디자인을 웹 앱에 적용 중...")
        
        # 1. 피그마 디자인 추출
        connector = FigmaMCPConnector()
        design_result = connector.apply_design_to_app(figma_file_key, self.figma_design_dir)
        
        # 2. 기존 템플릿 백업
        self.backup_templates()
        
        # 3. 디자인 토큰을 템플릿에 적용
        self.apply_design_tokens_to_templates(design_result['design_tokens'])
        
        # 4. CSS 파일을 static 디렉토리에 복사
        self.copy_css_to_static(design_result['css_file'])
        
        # 5. 템플릿에 CSS 링크 추가
        self.add_css_link_to_templates()
        
        # 6. 컴포넌트 스타일 업데이트
        self.update_component_styles(design_result['components'])
        
        print("✅ 피그마 디자인 적용 완료!")
        
    def backup_templates(self):
        """템플릿 백업"""
        
        backup_dir = Path("templates_backup")
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        
        shutil.copytree(self.templates_dir, backup_dir)
        print(f"✅ 템플릿 백업 완료: {backup_dir}")
    
    def apply_design_tokens_to_templates(self, design_tokens: dict):
        """디자인 토큰을 템플릿에 적용"""
        
        print("🎨 디자인 토큰을 템플릿에 적용 중...")
        
        # 메인 페이지 템플릿 업데이트
        self.update_index_template(design_tokens)
        
        # 통관 분석 페이지 템플릿 업데이트
        self.update_customs_analysis_template(design_tokens)
        
        # 기타 페이지들 업데이트
        self.update_other_templates(design_tokens)
    
    def update_index_template(self, design_tokens: dict):
        """메인 페이지 템플릿 업데이트"""
        
        index_file = Path(self.templates_dir) / "index.html"
        if not index_file.exists():
            return
        
        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 피그마 디자인 스타일 적용
        updated_content = self.apply_figma_styles_to_content(content, design_tokens)
        
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("✅ 메인 페이지 템플릿 업데이트 완료")
    
    def update_customs_analysis_template(self, design_tokens: dict):
        """통관 분석 페이지 템플릿 업데이트"""
        
        analysis_file = Path(self.templates_dir) / "customs_analysis.html"
        if not analysis_file.exists():
            return
        
        with open(analysis_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 피그마 디자인 스타일 적용
        updated_content = self.apply_figma_styles_to_content(content, design_tokens)
        
        with open(analysis_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("✅ 통관 분석 페이지 템플릿 업데이트 완료")
    
    def update_other_templates(self, design_tokens: dict):
        """기타 템플릿 업데이트"""
        
        template_files = [
            "regulation_info.html",
            "compliance_analysis.html",
            "document_generation.html",
            "nutrition_label.html"
        ]
        
        for template_name in template_files:
            template_file = Path(self.templates_dir) / template_name
            if template_file.exists():
                with open(template_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                updated_content = self.apply_figma_styles_to_content(content, design_tokens)
                
                with open(template_file, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                print(f"✅ {template_name} 템플릿 업데이트 완료")
    
    def apply_figma_styles_to_content(self, content: str, design_tokens: dict) -> str:
        """피그마 스타일을 HTML 콘텐츠에 적용"""
        
        # 기본 색상 적용
        primary_colors = list(design_tokens.get('colors', {}).keys())
        if primary_colors:
            primary_color = primary_colors[0]
            # Bootstrap 테마 색상 업데이트
            content = content.replace(
                '--bs-primary: #0d6efd;',
                f'--bs-primary: var(--color-{primary_color.lower().replace(" ", "-")});'
            )
        
        # 버튼 스타일 업데이트
        content = content.replace(
            'class="btn btn-primary"',
            'class="btn btn-primary figma-btn"'
        )
        
        # 카드 스타일 업데이트
        content = content.replace(
            'class="card"',
            'class="card figma-card"'
        )
        
        # 네비게이션 스타일 업데이트
        content = content.replace(
            'class="navbar navbar-expand-lg"',
            'class="navbar navbar-expand-lg figma-navbar"'
        )
        
        return content
    
    def copy_css_to_static(self, css_file_path: str):
        """CSS 파일을 static 디렉토리에 복사"""
        
        static_dir = Path(self.static_dir)
        static_dir.mkdir(exist_ok=True)
        
        css_file = Path(css_file_path)
        if css_file.exists():
            shutil.copy2(css_file, static_dir / "figma-design.css")
            print("✅ CSS 파일을 static 디렉토리에 복사 완료")
    
    def add_css_link_to_templates(self):
        """템플릿에 CSS 링크 추가"""
        
        css_link = '<link rel="stylesheet" href="{{ url_for(\'static\', filename=\'figma-design.css\') }}">'
        
        template_files = [
            "index.html",
            "customs_analysis.html",
            "regulation_info.html",
            "compliance_analysis.html",
            "document_generation.html",
            "nutrition_label.html"
        ]
        
        for template_name in template_files:
            template_file = Path(self.templates_dir) / template_name
            if template_file.exists():
                with open(template_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # CSS 링크가 이미 있는지 확인
                if 'figma-design.css' not in content:
                    # head 태그 안에 CSS 링크 추가
                    if '<head>' in content:
                        content = content.replace(
                            '<head>',
                            f'<head>\n    {css_link}'
                        )
                
                with open(template_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ {template_name}에 CSS 링크 추가 완료")
    
    def update_component_styles(self, components: list):
        """컴포넌트 스타일 업데이트"""
        
        print("🧩 컴포넌트 스타일 업데이트 중...")
        
        # 컴포넌트별 스타일 생성
        component_styles = self.generate_component_styles(components)
        
        # CSS 파일에 컴포넌트 스타일 추가
        css_file = Path(self.static_dir) / "figma-design.css"
        if css_file.exists():
            with open(css_file, 'a', encoding='utf-8') as f:
                f.write("\n\n/* 🧩 Component Styles */\n")
                f.write(component_styles)
        
        print("✅ 컴포넌트 스타일 업데이트 완료")
    
    def generate_component_styles(self, components: list) -> str:
        """컴포넌트 스타일 생성"""
        
        styles = ""
        
        for component in components:
            component_name = component['name'].lower().replace(' ', '-')
            styles += f"""
/* 🧩 {component['name']} Component */
.{component_name} {{
    /* Figma Component: {component['name']} */
    /* ID: {component['id']} */
}}
"""
        
        return styles
    
    def create_design_system_documentation(self, design_tokens: dict, components: list):
        """디자인 시스템 문서 생성"""
        
        doc_content = f"""
# 🎨 Figma Design System Documentation

## 📋 Design Tokens

### 🎨 Colors
"""
        
        for color_name, color_data in design_tokens.get('colors', {}).items():
            doc_content += f"- **{color_name}**: `{color_data['value']}`\n"
        
        doc_content += f"""
### 🧩 Components
"""
        
        for component in components:
            doc_content += f"- **{component['name']}**: {component.get('description', 'No description')}\n"
        
        doc_content += f"""
## 🚀 Usage

1. CSS 변수 사용: `var(--color-{list(design_tokens.get('colors', {}).keys())[0].lower().replace(' ', '-')})`
2. 컴포넌트 클래스 사용: `class="{components[0]['name'].lower().replace(' ', '-')}"`
3. 피그마 디자인 토큰 참조: `design-tokens.json`

## 📁 Files

- `figma-design.css`: 메인 디자인 스타일
- `design-tokens.json`: 디자인 토큰 데이터
- `components.json`: 컴포넌트 정보
"""
        
        with open("FIGMA_DESIGN_SYSTEM.md", 'w', encoding='utf-8') as f:
            f.write(doc_content)
        
        print("✅ 디자인 시스템 문서 생성 완료: FIGMA_DESIGN_SYSTEM.md")

def main():
    """피그마 디자인 적용 테스트"""
    
    print("🎨 피그마 디자인을 웹 앱에 적용")
    print("=" * 60)
    
    # 피그마 파일 키 입력
    figma_file_key = input("📋 피그마 파일 키를 입력하세요: ").strip()
    
    if not figma_file_key:
        print("❌ 파일 키가 입력되지 않았습니다.")
        return
    
    # 피그마 디자인 적용
    applier = FigmaDesignApplier()
    applier.apply_figma_design_to_templates(figma_file_key)
    
    print("\n🎉 피그마 디자인 적용 완료!")
    print("📝 다음 단계:")
    print("   1. 웹 서버 재시작")
    print("   2. 브라우저에서 디자인 확인")
    print("   3. FIGMA_DESIGN_SYSTEM.md 문서 참조")

if __name__ == "__main__":
    main() 