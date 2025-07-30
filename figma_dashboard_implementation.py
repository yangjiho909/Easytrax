#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎨 Figma 디자인 기반 대시보드 구현
- Figma API를 통한 디자인 토큰 추출
- 대시보드 컴포넌트 생성
- 반응형 레이아웃 적용
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path

class FigmaDashboardBuilder:
    """Figma 디자인 기반 대시보드 빌더"""
    
    def __init__(self):
        self.figma_token = os.getenv('FIGMA_ACCESS_TOKEN')
        self.figma_file_key = "5k7oBFQcrqQGrFrMzcpuVP"
        self.figma_api_base = "https://api.figma.com/v1"
        
    def get_figma_design_data(self):
        """Figma 디자인 데이터 가져오기"""
        if not self.figma_token:
            print("⚠️ FIGMA_ACCESS_TOKEN 환경변수가 설정되지 않았습니다.")
            return self.get_default_design_data()
        
        try:
            url = f"{self.figma_api_base}/files/{self.figma_file_key}"
            headers = {"X-Figma-Token": self.figma_token}
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            print("✅ Figma 디자인 데이터 로드 성공")
            return data
            
        except Exception as e:
            print(f"❌ Figma API 오류: {e}")
            return self.get_default_design_data()
    
    def get_default_design_data(self):
        """기본 디자인 데이터 (Figma API 실패 시)"""
        return {
            "name": "대시보드 디자인",
            "document": {
                "children": [
                    {
                        "name": "대시보드",
                        "type": "FRAME",
                        "fills": [{"type": "SOLID", "color": {"r": 0.98, "g": 0.98, "b": 0.98}}],
                        "children": [
                            {
                                "name": "헤더",
                                "type": "FRAME",
                                "fills": [{"type": "SOLID", "color": {"r": 1, "g": 1, "b": 1}}],
                                "children": []
                            },
                            {
                                "name": "사이드바",
                                "type": "FRAME",
                                "fills": [{"type": "SOLID", "color": {"r": 0.1, "g": 0.1, "b": 0.1}}],
                                "children": []
                            },
                            {
                                "name": "메인 콘텐츠",
                                "type": "FRAME",
                                "fills": [{"type": "SOLID", "color": {"r": 0.98, "g": 0.98, "b": 0.98}}],
                                "children": []
                            }
                        ]
                    }
                ]
            }
        }
    
    def extract_design_tokens(self, figma_data):
        """디자인 토큰 추출"""
        tokens = {
            "colors": {
                "primary": "#2c3e50",
                "secondary": "#3498db",
                "accent": "#e74c3c",
                "success": "#27ae60",
                "warning": "#f39c12",
                "background": "#f8f9fa",
                "surface": "#ffffff",
                "text": "#2c3e50",
                "text_secondary": "#6c757d"
            },
            "typography": {
                "font_family": "'Noto Sans KR', sans-serif",
                "font_size_small": "0.875rem",
                "font_size_base": "1rem",
                "font_size_large": "1.25rem",
                "font_size_xlarge": "1.5rem",
                "font_weight_normal": "400",
                "font_weight_bold": "700"
            },
            "spacing": {
                "xs": "0.25rem",
                "sm": "0.5rem",
                "md": "1rem",
                "lg": "1.5rem",
                "xl": "2rem",
                "xxl": "3rem"
            },
            "border_radius": {
                "sm": "0.25rem",
                "md": "0.5rem",
                "lg": "1rem",
                "xl": "1.5rem"
            },
            "shadows": {
                "sm": "0 2px 4px rgba(0,0,0,0.1)",
                "md": "0 4px 8px rgba(0,0,0,0.1)",
                "lg": "0 8px 16px rgba(0,0,0,0.1)",
                "xl": "0 16px 32px rgba(0,0,0,0.1)"
            }
        }
        
        # Figma 데이터에서 색상 추출 시도
        try:
            if "document" in figma_data:
                self._extract_colors_from_figma(figma_data["document"], tokens)
        except Exception as e:
            print(f"⚠️ 색상 추출 실패: {e}")
        
        return tokens
    
    def _extract_colors_from_figma(self, node, tokens):
        """Figma 노드에서 색상 추출"""
        if "fills" in node and node["fills"]:
            for fill in node["fills"]:
                if fill["type"] == "SOLID" and "color" in fill:
                    color = fill["color"]
                    hex_color = self._rgb_to_hex(color["r"], color["g"], color["b"])
                    
                    if "background" in node["name"].lower():
                        tokens["colors"]["background"] = hex_color
                    elif "primary" in node["name"].lower():
                        tokens["colors"]["primary"] = hex_color
                    elif "secondary" in node["name"].lower():
                        tokens["colors"]["secondary"] = hex_color
        
        if "children" in node:
            for child in node["children"]:
                self._extract_colors_from_figma(child, tokens)
    
    def _rgb_to_hex(self, r, g, b):
        """RGB를 HEX로 변환"""
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
    
    def generate_dashboard_html(self, design_tokens):
        """대시보드 HTML 생성"""
        html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>나만의 통관 수출 도우미 - 대시보드</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary-color: {design_tokens['colors']['primary']};
            --secondary-color: {design_tokens['colors']['secondary']};
            --accent-color: {design_tokens['colors']['accent']};
            --success-color: {design_tokens['colors']['success']};
            --warning-color: {design_tokens['colors']['warning']};
            --background-color: {design_tokens['colors']['background']};
            --surface-color: {design_tokens['colors']['surface']};
            --text-color: {design_tokens['colors']['text']};
            --text-secondary: {design_tokens['colors']['text_secondary']};
            
            --font-family: {design_tokens['typography']['font_family']};
            --font-size-small: {design_tokens['typography']['font_size_small']};
            --font-size-base: {design_tokens['typography']['font_size_base']};
            --font-size-large: {design_tokens['typography']['font_size_large']};
            --font-size-xlarge: {design_tokens['typography']['font_size_xlarge']};
            
            --spacing-xs: {design_tokens['spacing']['xs']};
            --spacing-sm: {design_tokens['spacing']['sm']};
            --spacing-md: {design_tokens['spacing']['md']};
            --spacing-lg: {design_tokens['spacing']['lg']};
            --spacing-xl: {design_tokens['spacing']['xl']};
            --spacing-xxl: {design_tokens['spacing']['xxl']};
            
            --border-radius-sm: {design_tokens['border_radius']['sm']};
            --border-radius-md: {design_tokens['border_radius']['md']};
            --border-radius-lg: {design_tokens['border_radius']['lg']};
            --border-radius-xl: {design_tokens['border_radius']['xl']};
            
            --shadow-sm: {design_tokens['shadows']['sm']};
            --shadow-md: {design_tokens['shadows']['md']};
            --shadow-lg: {design_tokens['shadows']['lg']};
            --shadow-xl: {design_tokens['shadows']['xl']};
        }}
        
        body {{
            font-family: var(--font-family);
            background-color: var(--background-color);
            color: var(--text-color);
            margin: 0;
            padding: 0;
        }}
        
        .dashboard-container {{
            display: flex;
            min-height: 100vh;
        }}
        
        .sidebar {{
            width: 280px;
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            padding: var(--spacing-lg);
            box-shadow: var(--shadow-lg);
            position: fixed;
            height: 100vh;
            overflow-y: auto;
        }}
        
        .main-content {{
            flex: 1;
            margin-left: 280px;
            padding: var(--spacing-lg);
        }}
        
        .header {{
            background: var(--surface-color);
            padding: var(--spacing-lg);
            border-radius: var(--border-radius-lg);
            box-shadow: var(--shadow-sm);
            margin-bottom: var(--spacing-lg);
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: var(--spacing-lg);
            margin-bottom: var(--spacing-xl);
        }}
        
        .stat-card {{
            background: var(--surface-color);
            padding: var(--spacing-lg);
            border-radius: var(--border-radius-lg);
            box-shadow: var(--shadow-md);
            border-left: 4px solid var(--primary-color);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-4px);
            box-shadow: var(--shadow-lg);
        }}
        
        .stat-card.success {{
            border-left-color: var(--success-color);
        }}
        
        .stat-card.warning {{
            border-left-color: var(--warning-color);
        }}
        
        .stat-card.accent {{
            border-left-color: var(--accent-color);
        }}
        
        .stat-number {{
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--primary-color);
            margin-bottom: var(--spacing-sm);
        }}
        
        .stat-label {{
            font-size: var(--font-size-small);
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .quick-actions {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: var(--spacing-md);
            margin-bottom: var(--spacing-xl);
        }}
        
        .action-card {{
            background: var(--surface-color);
            padding: var(--spacing-lg);
            border-radius: var(--border-radius-lg);
            box-shadow: var(--shadow-sm);
            text-align: center;
            text-decoration: none;
            color: var(--text-color);
            transition: all 0.3s ease;
            border: 2px solid transparent;
        }}
        
        .action-card:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
            border-color: var(--primary-color);
            color: var(--text-color);
            text-decoration: none;
        }}
        
        .action-icon {{
            font-size: 2rem;
            color: var(--primary-color);
            margin-bottom: var(--spacing-md);
        }}
        
        .recent-activity {{
            background: var(--surface-color);
            padding: var(--spacing-lg);
            border-radius: var(--border-radius-lg);
            box-shadow: var(--shadow-sm);
        }}
        
        .activity-item {{
            display: flex;
            align-items: center;
            padding: var(--spacing-md) 0;
            border-bottom: 1px solid #eee;
        }}
        
        .activity-item:last-child {{
            border-bottom: none;
        }}
        
        .activity-icon {{
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: var(--primary-color);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: var(--spacing-md);
        }}
        
        .nav-item {{
            margin-bottom: var(--spacing-sm);
        }}
        
        .nav-link {{
            color: rgba(255, 255, 255, 0.8);
            text-decoration: none;
            padding: var(--spacing-sm) var(--spacing-md);
            border-radius: var(--border-radius-md);
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
        }}
        
        .nav-link:hover {{
            color: white;
            background: rgba(255, 255, 255, 0.1);
            text-decoration: none;
        }}
        
        .nav-link.active {{
            background: rgba(255, 255, 255, 0.2);
            color: white;
        }}
        
        .nav-icon {{
            margin-right: var(--spacing-sm);
            width: 20px;
        }}
        
        @media (max-width: 768px) {{
            .sidebar {{
                width: 100%;
                height: auto;
                position: relative;
            }}
            
            .main-content {{
                margin-left: 0;
            }}
            
            .dashboard-container {{
                flex-direction: column;
            }}
        }}
    </style>
</head>
<body>
    <div class="dashboard-container">
        <!-- 사이드바 -->
        <div class="sidebar">
            <div class="mb-4">
                <h3 class="mb-0">
                    <i class="fas fa-globe-asia me-2"></i>
                    통관 도우미
                </h3>
                <small class="text-muted">수출 통관 관리 시스템</small>
            </div>
            
            <nav class="nav flex-column">
                <div class="nav-item">
                    <a href="/" class="nav-link active">
                        <i class="fas fa-tachometer-alt nav-icon"></i>
                        대시보드
                    </a>
                </div>
                <div class="nav-item">
                    <a href="/customs-analysis" class="nav-link">
                        <i class="fas fa-search nav-icon"></i>
                        통관 분석
                    </a>
                </div>
                <div class="nav-item">
                    <a href="/document-generation" class="nav-link">
                        <i class="fas fa-file-alt nav-icon"></i>
                        서류 생성
                    </a>
                </div>
                <div class="nav-item">
                    <a href="/regulation-info" class="nav-link">
                        <i class="fas fa-info-circle nav-icon"></i>
                        규제 정보
                    </a>
                </div>
                <div class="nav-item">
                    <a href="/compliance-analysis" class="nav-link">
                        <i class="fas fa-check-circle nav-icon"></i>
                        준수성 분석
                    </a>
                </div>
                <div class="nav-item">
                    <a href="/nutrition-label" class="nav-link">
                        <i class="fas fa-tags nav-icon"></i>
                        라벨 생성
                    </a>
                </div>
            </nav>
        </div>
        
        <!-- 메인 콘텐츠 -->
        <div class="main-content">
            <!-- 헤더 -->
            <div class="header">
                <div class="row align-items-center">
                    <div class="col">
                        <h1 class="mb-1">대시보드</h1>
                        <p class="text-muted mb-0">수출 통관 현황을 한눈에 확인하세요</p>
                    </div>
                    <div class="col-auto">
                        <span class="badge bg-success">시스템 정상</span>
                    </div>
                </div>
            </div>
            
            <!-- 통계 카드 -->
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">1,247</div>
                    <div class="stat-label">총 수출 건수</div>
                </div>
                <div class="stat-card success">
                    <div class="stat-number">98.5%</div>
                    <div class="stat-label">통관 성공률</div>
                </div>
                <div class="stat-card warning">
                    <div class="stat-number">23</div>
                    <div class="stat-label">대기 중인 서류</div>
                </div>
                <div class="stat-card accent">
                    <div class="stat-number">4</div>
                    <div class="stat-label">지원 국가</div>
                </div>
            </div>
            
            <!-- 빠른 액션 -->
            <div class="quick-actions">
                <a href="/customs-analysis" class="action-card">
                    <div class="action-icon">
                        <i class="fas fa-search"></i>
                    </div>
                    <h5>통관 분석</h5>
                    <p class="text-muted">거부 사례 분석 및 예방</p>
                </a>
                <a href="/document-generation" class="action-card">
                    <div class="action-icon">
                        <i class="fas fa-file-alt"></i>
                    </div>
                    <h5>서류 생성</h5>
                    <p class="text-muted">자동 서류 생성</p>
                </a>
                <a href="/regulation-info" class="action-card">
                    <div class="action-icon">
                        <i class="fas fa-info-circle"></i>
                    </div>
                    <h5>규제 정보</h5>
                    <p class="text-muted">실시간 규제 업데이트</p>
                </a>
                <a href="/compliance-analysis" class="action-card">
                    <div class="action-icon">
                        <i class="fas fa-check-circle"></i>
                    </div>
                    <h5>준수성 분석</h5>
                    <p class="text-muted">규제 준수성 검토</p>
                </a>
            </div>
            
            <!-- 최근 활동 -->
            <div class="recent-activity">
                <h4 class="mb-3">최근 활동</h4>
                <div class="activity-item">
                    <div class="activity-icon">
                        <i class="fas fa-file-alt"></i>
                    </div>
                    <div>
                        <div class="fw-bold">상업송장 생성 완료</div>
                        <small class="text-muted">중국 수출용 서류가 생성되었습니다.</small>
                    </div>
                    <div class="ms-auto">
                        <small class="text-muted">2분 전</small>
                    </div>
                </div>
                <div class="activity-item">
                    <div class="activity-icon">
                        <i class="fas fa-search"></i>
                    </div>
                    <div>
                        <div class="fw-bold">통관 분석 완료</div>
                        <small class="text-muted">라면 수출 거부 사례 분석이 완료되었습니다.</small>
                    </div>
                    <div class="ms-auto">
                        <small class="text-muted">15분 전</small>
                    </div>
                </div>
                <div class="activity-item">
                    <div class="activity-icon">
                        <i class="fas fa-info-circle"></i>
                    </div>
                    <div>
                        <div class="fw-bold">규제 정보 업데이트</div>
                        <small class="text-muted">중국 식품 규제 정보가 업데이트되었습니다.</small>
                    </div>
                    <div class="ms-auto">
                        <small class="text-muted">1시간 전</small>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // 현재 페이지 활성화
        document.addEventListener('DOMContentLoaded', function() {{
            const currentPath = window.location.pathname;
            const navLinks = document.querySelectorAll('.nav-link');
            
            navLinks.forEach(link => {{
                if (link.getAttribute('href') === currentPath) {{
                    link.classList.add('active');
                }} else {{
                    link.classList.remove('active');
                }}
            }});
        }});
        
        // 실시간 통계 업데이트 (예시)
        function updateStats() {{
            // 실제로는 API에서 데이터를 가져와서 업데이트
            console.log('통계 업데이트 중...');
        }}
        
        // 30초마다 통계 업데이트
        setInterval(updateStats, 30000);
    </script>
</body>
</html>
"""
        return html
    
    def save_dashboard(self, html_content):
        """대시보드 HTML 저장"""
        output_dir = "templates"
        os.makedirs(output_dir, exist_ok=True)
        
        filepath = os.path.join(output_dir, "dashboard.html")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ 대시보드 저장 완료: {filepath}")
        return filepath
    
    def build_dashboard(self):
        """대시보드 빌드 실행"""
        print("🎨 Figma 디자인 기반 대시보드 빌드 시작...")
        
        # Figma 디자인 데이터 가져오기
        figma_data = self.get_figma_design_data()
        
        # 디자인 토큰 추출
        design_tokens = self.extract_design_tokens(figma_data)
        
        # 대시보드 HTML 생성
        html_content = self.generate_dashboard_html(design_tokens)
        
        # 파일 저장
        filepath = self.save_dashboard(html_content)
        
        print("🎉 대시보드 빌드 완료!")
        return filepath

def main():
    """메인 실행 함수"""
    builder = FigmaDashboardBuilder()
    dashboard_path = builder.build_dashboard()
    
    print(f"\n📁 생성된 파일: {dashboard_path}")
    print("🌐 웹사이트에서 확인: http://localhost:5000/dashboard")

if __name__ == "__main__":
    main() 