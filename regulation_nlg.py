# regulation_nlg.py
# 규제정보 자연어 생성

from natural_language_generator import BaseNLG
from typing import Dict, List

class RegulationNLG(BaseNLG):
    def __init__(self):
        super().__init__()
        
        # 국가별 템플릿
        self.regulation_templates = {
            '중국': {
                'intro': "중국으로 {product}을(를) 수출할 때는",
                'restriction': "특히 {restriction}에 유의해야 합니다",
                'documents': "필요한 서류로는 {documents} 등이 있으며",
                'procedure': "통관 절차는 {procedure}를 따릅니다"
            },
            '미국': {
                'intro': "미국으로 {product}을(를) 수출할 때는",
                'restriction': "특히 {restriction}에 주의해야 합니다",
                'documents': "필요한 서류로는 {documents} 등이 필요하며",
                'procedure': "통관 절차는 {procedure}를 거칩니다"
            },
            '일본': {
                'intro': "일본으로 {product}을(를) 수출할 때는",
                'restriction': "특히 {restriction}에 유의해야 합니다",
                'documents': "필요한 서류로는 {documents} 등이 필요하며",
                'procedure': "통관 절차는 {procedure}를 거칩니다"
            },
            'EU': {
                'intro': "EU로 {product}을(를) 수출할 때는",
                'restriction': "특히 {restriction}에 주의해야 합니다",
                'documents': "필요한 서류로는 {documents} 등이 필요하며",
                'procedure': "통관 절차는 {procedure}를 거칩니다"
            }
        }
    
    def extract_key_restriction(self, restrictions: List[str]) -> str:
        """주요 제한사항 추출"""
        if not restrictions:
            return ""
        
        # 가장 중요한 제한사항 선택
        key_restrictions = []
        for restriction in restrictions[:2]:  # 상위 2개만
            if any(keyword in restriction for keyword in ['필수', '제한', '금지', '허용', '이하']):
                key_restrictions.append(restriction)
        
        if key_restrictions:
            return key_restrictions[0]
        return restrictions[0] if restrictions else ""
    
    def extract_key_documents(self, documents: List[str]) -> str:
        """주요 필요서류 추출"""
        if not documents:
            return ""
        
        # 가장 중요한 서류들 선택
        key_docs = []
        for doc in documents[:3]:  # 상위 3개만
            if any(keyword in doc for keyword in ['인증서', '검사서', '증명서', '분석서']):
                key_docs.append(doc)
        
        if key_docs:
            return ", ".join(key_docs)
        return ", ".join(documents[:2]) if documents else ""
    
    def extract_key_procedure(self, procedures: List[str]) -> str:
        """주요 통관절차 추출"""
        if not procedures:
            return ""
        
        # 핵심 절차 단계 추출
        key_steps = []
        for procedure in procedures:
            if any(keyword in procedure for keyword in ['신고', '검사', '승인', '통관']):
                key_steps.append(procedure)
        
        if key_steps:
            return " → ".join(key_steps)
        return " → ".join(procedures[:3]) if procedures else ""
    
    def generate_additional_info_summary(self, additional_info: Dict) -> str:
        """추가정보 자연어 요약"""
        summary_parts = []
        
        # 처리기간
        if '처리기간' in additional_info:
            summary_parts.append(f"처리기간은 {additional_info['처리기간']}이며")
        
        # 수수료
        if '수수료' in additional_info:
            summary_parts.append(f"수수료는 {additional_info['수수료']}입니다")
        
        # 검사기관
        if '검사기관' in additional_info:
            summary_parts.append(f"검사는 {additional_info['검사기관']}에서 진행됩니다")
        
        return " ".join(summary_parts)
    
    def generate_regulation_summary(self, country: str, product: str, 
                                  regulations: Dict) -> str:
        """규제정보 종합 요약 생성"""
        
        template = self.regulation_templates.get(country, self.regulation_templates['중국'])
        
        # 핵심 정보 추출
        key_restriction = self.extract_key_restriction(regulations.get('제한사항', []))
        key_documents = self.extract_key_documents(regulations.get('필요서류', []))
        key_procedure = self.extract_key_procedure(regulations.get('통관절차', []))
        additional_info = regulations.get('추가정보', {})
        
        # 자연어 요약 생성
        summary_parts = []
        
        # 1. 기본 소개
        summary_parts.append(template['intro'].format(product=product))
        
        # 2. 주요 제한사항
        if key_restriction:
            summary_parts.append(template['restriction'].format(restriction=key_restriction))
        
        # 3. 필요서류
        if key_documents:
            summary_parts.append(template['documents'].format(documents=key_documents))
        
        # 4. 통관절차
        if key_procedure:
            summary_parts.append(template['procedure'].format(procedure=key_procedure))
        
        # 5. 추가 정보
        if additional_info:
            additional_summary = self.generate_additional_info_summary(additional_info)
            if additional_summary:
                summary_parts.append(additional_summary)
        
        return " ".join(summary_parts)
    
    def generate_detailed_explanation(self, country: str, product: str, 
                                    regulations: Dict) -> str:
        """상세 규제정보 자연어 설명"""
        
        explanation_parts = []
        
        # 1. 제목
        explanation_parts.append(f"📋 {country} - {product} 상세 규제정보")
        explanation_parts.append("=" * 60)
        
        # 2. 각 섹션별 상세 설명
        section_templates = {
            '제한사항': {
                'intro': "🚫 주요 제한사항:",
                'item_format': "• {item}"
            },
            '허용기준': {
                'intro': "✅ 허용기준:",
                'item_format': "• {item}"
            },
            '필요서류': {
                'intro': "📋 필요서류:",
                'item_format': "• {item}"
            },
            '통관절차': {
                'intro': "🔄 통관절차:",
                'item_format': "• {item}"
            },
            '주의사항': {
                'intro': "⚠️ 주의사항:",
                'item_format': "• {item}"
            }
        }
        
        for section, template in section_templates.items():
            if section in regulations and regulations[section]:
                explanation_parts.append(f"\n{template['intro']}")
                
                items = regulations[section]
                if isinstance(items, list):
                    for item in items[:5]:  # 상위 5개만 표시
                        explanation_parts.append(template['item_format'].format(item=item))
                    
                    if len(items) > 5:
                        explanation_parts.append(f"• ... 외 {len(items) - 5}개 항목")
                else:
                    explanation_parts.append(template['item_format'].format(item=items))
        
        # 3. 추가정보 섹션
        if '추가정보' in regulations:
            explanation_parts.append(self.generate_additional_section(regulations['추가정보']))
        
        return "\n".join(explanation_parts)
    
    def generate_additional_section(self, additional_info: Dict) -> str:
        """추가정보 섹션 생성"""
        section_parts = ["\n📊 추가 정보:", "-" * 40]
        
        info_mapping = {
            '관련법규': '📜 관련법규',
            '검사기관': '🏢 검사기관',
            '처리기간': '⏱️ 처리기간',
            '수수료': '💰 수수료',
            '최종업데이트': '📅 최종업데이트'
        }
        
        for key, display_name in info_mapping.items():
            if key in additional_info:
                section_parts.append(f"   {display_name}: {additional_info[key]}")
        
        return "\n".join(section_parts) 