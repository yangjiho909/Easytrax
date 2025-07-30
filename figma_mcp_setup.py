#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎨 피그마 MCP 연동 설정
- 피그마 디자인을 웹 앱에 적용
- 디자인 토큰 추출
- 컴포넌트 변환
"""

import requests
import json
import os
from typing import Dict, List, Optional
from pathlib import Path

class FigmaMCPConnector:
    """피그마 MCP 연동 시스템"""
    
    def __init__(self):
        self.figma_token = os.getenv('FIGMA_ACCESS_TOKEN')
        self.figma_api_base = "https://api.figma.com/v1"
        
        # MCP 설정
        self.mcp_config = {
            "server_name": "figma-mcp-server",
            "version": "1.0.0",
            "capabilities": {
                "design_tokens": True,
                "component_extraction": True,
                "code_generation": True,
                "style_sync": True
            }
        }
    
    def setup_figma_connection(self, file_key: str):
        """피그마 파일 연결 설정"""
        
        if not self.figma_token:
            print("❌ FIGMA_ACCESS_TOKEN 환경변수가 설정되지 않았습니다.")
            print("📝 설정 방법:")
            print("   1. 피그마 계정 설정 → Personal access tokens")
            print("   2. 새 토큰 생성")
            print("   3. 환경변수 설정: export FIGMA_ACCESS_TOKEN='your_token'")
            return False
        
        try:
            # 피그마 파일 정보 조회
            url = f"{self.figma_api_base}/files/{file_key}"
            headers = {"X-Figma-Token": self.figma_token}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                file_data = response.json()
                print(f"✅ 피그마 파일 연결 성공: {file_data['name']}")
                return True
            else:
                print(f"❌ 피그마 파일 연결 실패: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 피그마 연결 오류: {str(e)}")
            return False
    
    def extract_design_tokens(self, file_key: str) -> Dict:
        """디자인 토큰 추출"""
        
        print("🎨 디자인 토큰 추출 중...")
        
        try:
            # 스타일 정보 조회
            url = f"{self.figma_api_base}/files/{file_key}/styles"
            headers = {"X-Figma-Token": self.figma_token}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                styles_data = response.json()
                
                # 디자인 토큰 구성
                design_tokens = {
                    "colors": {},
                    "typography": {},
                    "spacing": {},
                    "shadows": {},
                    "borders": {},
                    "breakpoints": {}
                }
                
                # 색상 토큰 추출
                for style in styles_data.get('meta', {}).get('styles', {}).values():
                    if style.get('style_type') == 'FILL':
                        design_tokens['colors'][style['name']] = {
                            'value': style.get('description', ''),
                            'type': 'color'
                        }
                
                print(f"✅ 디자인 토큰 추출 완료: {len(design_tokens['colors'])}개 색상")
                return design_tokens
            else:
                print(f"❌ 디자인 토큰 추출 실패: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"❌ 디자인 토큰 추출 오류: {str(e)}")
            return {}
    
    def extract_components(self, file_key: str) -> List[Dict]:
        """컴포넌트 추출"""
        
        print("🧩 컴포넌트 추출 중...")
        
        try:
            # 컴포넌트 정보 조회
            url = f"{self.figma_api_base}/files/{file_key}/components"
            headers = {"X-Figma-Token": self.figma_token}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                components_data = response.json()
                
                components = []
                for component in components_data.get('meta', {}).get('components', {}).values():
                    components.append({
                        'id': component['node_id'],
                        'name': component['name'],
                        'description': component.get('description', ''),
                        'key': component['key']
                    })
                
                print(f"✅ 컴포넌트 추출 완료: {len(components)}개")
                return components
            else:
                print(f"❌ 컴포넌트 추출 실패: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ 컴포넌트 추출 오류: {str(e)}")
            return []
    
    def generate_css_from_tokens(self, design_tokens: Dict) -> str:
        """디자인 토큰을 CSS로 변환"""
        
        print("🎨 CSS 생성 중...")
        
        css_code = """
/* 🎨 Figma Design Tokens - Auto Generated */
:root {
"""
        
        # 색상 변수
        for color_name, color_data in design_tokens.get('colors', {}).items():
            css_code += f"  --color-{color_name.lower().replace(' ', '-')}: {color_data['value']};\n"
        
        # 타이포그래피 변수
        for typo_name, typo_data in design_tokens.get('typography', {}).items():
            css_code += f"  --font-{typo_name.lower().replace(' ', '-')}: {typo_data['value']};\n"
        
        # 간격 변수
        for spacing_name, spacing_data in design_tokens.get('spacing', {}).items():
            css_code += f"  --spacing-{spacing_name.lower().replace(' ', '-')}: {spacing_data['value']};\n"
        
        css_code += "}\n\n"
        
        # 유틸리티 클래스
        css_code += "/* 🎨 Utility Classes */\n"
        
        # 색상 유틸리티
        for color_name in design_tokens.get('colors', {}).keys():
            css_class = color_name.lower().replace(' ', '-')
            css_code += f".bg-{css_class} {{ background-color: var(--color-{css_class}); }}\n"
            css_code += f".text-{css_class} {{ color: var(--color-{css_class}); }}\n"
        
        css_code += "\n/* 🎨 Component Styles */\n"
        
        print("✅ CSS 생성 완료")
        return css_code
    
    def apply_design_to_app(self, file_key: str, output_dir: str = "figma_design"):
        """피그마 디자인을 앱에 적용"""
        
        print("🚀 피그마 디자인을 앱에 적용 중...")
        
        # 출력 디렉토리 생성
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # 1. 디자인 토큰 추출
        design_tokens = self.extract_design_tokens(file_key)
        
        # 2. 컴포넌트 추출
        components = self.extract_components(file_key)
        
        # 3. CSS 생성
        css_code = self.generate_css_from_tokens(design_tokens)
        
        # 4. 파일 저장
        css_file = output_path / "figma-design-tokens.css"
        with open(css_file, 'w', encoding='utf-8') as f:
            f.write(css_code)
        
        # 5. 디자인 토큰 JSON 저장
        tokens_file = output_path / "design-tokens.json"
        with open(tokens_file, 'w', encoding='utf-8') as f:
            json.dump(design_tokens, f, ensure_ascii=False, indent=2)
        
        # 6. 컴포넌트 정보 저장
        components_file = output_path / "components.json"
        with open(components_file, 'w', encoding='utf-8') as f:
            json.dump(components, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 디자인 적용 완료!")
        print(f"   📁 출력 디렉토리: {output_dir}")
        print(f"   🎨 CSS 파일: {css_file}")
        print(f"   📋 토큰 파일: {tokens_file}")
        print(f"   🧩 컴포넌트 파일: {components_file}")
        
        return {
            'css_file': str(css_file),
            'tokens_file': str(tokens_file),
            'components_file': str(components_file),
            'design_tokens': design_tokens,
            'components': components
        }

def main():
    """피그마 MCP 연동 테스트"""
    
    print("🎨 피그마 MCP 연동 시스템")
    print("=" * 60)
    
    # 피그마 MCP 커넥터 초기화
    connector = FigmaMCPConnector()
    
    # 피그마 파일 키 입력 (예시)
    file_key = input("📋 피그마 파일 키를 입력하세요: ").strip()
    
    if not file_key:
        print("❌ 파일 키가 입력되지 않았습니다.")
        return
    
    # 피그마 연결 설정
    if connector.setup_figma_connection(file_key):
        # 디자인을 앱에 적용
        result = connector.apply_design_to_app(file_key)
        
        print(f"\n🎉 피그마 MCP 연동 완료!")
        print(f"📝 다음 단계:")
        print(f"   1. {result['css_file']} 파일을 HTML에 포함")
        print(f"   2. 디자인 토큰을 사용하여 스타일 적용")
        print(f"   3. 컴포넌트 정보를 참고하여 개발")
    else:
        print("❌ 피그마 연결에 실패했습니다.")

if __name__ == "__main__":
    main() 