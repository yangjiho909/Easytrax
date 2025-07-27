# customs_analysis_nlg.py
# 통관 거부사례 분석 자연어 생성

from natural_language_generator import BaseNLG
from typing import List, Dict
from collections import Counter

class CustomsAnalysisNLG(BaseNLG):
    def __init__(self):
        super().__init__()
        
        # 한국어 키워드 패턴
        self.problem_patterns = {
            '라벨': ['라벨', '표기', '인쇄', '부착', '라벨링'],
            '인증': ['인증서', '허가', '승인', '등록', '인증'],
            '성분': ['성분', '첨가물', '방부제', '색소', '화학물질'],
            '검역': ['검역', '위생', '미생물', '농약', '방사능'],
            '세관': ['세관', '통관', '신고', '서류', '신고서'],
            '포장': ['포장', '용기', '포장재', '용기'],
            '원산지': ['원산지', '제조국', '생산지']
        }
    
    def extract_key_problems(self, cases: List[Dict]) -> List[tuple]:
        """상위 사례들의 핵심 문제 유형 추출"""
        all_problems = []
        
        for case in cases[:3]:  # 상위 3개 사례만 분석
            problem_text = self.clean_text(case.get('문제사유', ''))
            if problem_text:
                # 문제 유형 분류
                for category, keywords in self.problem_patterns.items():
                    if any(keyword in problem_text for keyword in keywords):
                        all_problems.append(category)
                        break
        
        # 가장 빈번한 문제 유형 반환
        if all_problems:
            return Counter(all_problems).most_common(2)
        return []
    
    def get_representative_action(self, cases: List[Dict]) -> str:
        """대표적인 조치사항 추출"""
        actions = []
        for case in cases:
            action = self.clean_text(case.get('조치사항', ''))
            if action:
                actions.append(action)
        
        if not actions:
            return "반송"
        
        # 가장 빈번한 조치사항 반환
        action_counter = Counter(actions)
        return action_counter.most_common(1)[0][0]
    
    def generate_customs_summary(self, cases: List[Dict], user_query: str) -> str:
        """통관 거부사례 종합 요약 생성"""
        if not cases:
            return "유사한 통관 거부사례를 찾을 수 없습니다."
        
        # 핵심 정보 추출
        top_cases = cases[:3]
        countries = [self.clean_text(case.get('수입국', '')) for case in top_cases]
        countries = [c for c in countries if c]
        
        products = [self.clean_text(case.get('품목', '')) for case in top_cases]
        products = [p for p in products if p]
        
        key_problems = self.extract_key_problems(top_cases)
        
        # 사용자 입력에서 제품/국가 추출
        user_product, user_country = self.extract_user_intent(user_query)
        
        # 자연어 요약 생성
        summary_parts = []
        
        # 1. 사용자 의도와의 연관성
        if user_product and user_country:
            summary_parts.append(f"사용자가 문의한 '{user_product}'을(를) '{user_country}'로 수출하는 경우와")
        elif user_product:
            summary_parts.append(f"사용자가 문의한 '{user_product}' 수출과")
        elif user_country:
            summary_parts.append(f"사용자가 문의한 '{user_country}' 수출과")
        else:
            summary_parts.append("사용자가 문의한 내용과")
        
        # 2. 유사 사례 개수
        summary_parts.append(f"가장 유사한 {len(top_cases)}개 사례를 분석한 결과")
        
        # 3. 주요 문제 유형
        if key_problems:
            problem_desc = []
            for problem, count in key_problems:
                if problem == '라벨':
                    problem_desc.append("라벨 표기 문제")
                elif problem == '인증':
                    problem_desc.append("인증서류 문제")
                elif problem == '성분':
                    problem_desc.append("성분 기준 문제")
                elif problem == '검역':
                    problem_desc.append("검역 기준 문제")
                elif problem == '세관':
                    problem_desc.append("세관 신고 문제")
                elif problem == '포장':
                    problem_desc.append("포장 기준 문제")
                elif problem == '원산지':
                    problem_desc.append("원산지 표기 문제")
            
            summary_parts.append(f"주로 {', '.join(problem_desc)}로 인한 통관 거부가 발생했습니다.")
        
        # 4. 대표적인 조치사항
        representative_action = self.get_representative_action(top_cases)
        if representative_action:
            summary_parts.append(f"일반적으로 '{representative_action}' 조치가 취해졌습니다.")
        
        return " ".join(summary_parts)
    
    def generate_threshold_explanation(self, 
                                     final_threshold: float, 
                                     initial_threshold: float = 0.3,
                                     retry_count: int = 0) -> str:
        """임계값 조정 과정을 자연어로 설명"""
        
        if final_threshold == initial_threshold and retry_count == 0:
            return "높은 유사도의 관련 사례를 바로 찾았습니다."
        
        explanation_parts = []
        
        if retry_count > 0:
            explanation_parts.append("처음에는 높은 유사도 사례가 없었으나,")
            
            if retry_count == 1:
                explanation_parts.append("임계값을 낮춰")
            else:
                explanation_parts.append("임계값을 여러 번 낮춰")
            
            # 임계값 수준 설명
            if final_threshold >= 0.5:
                threshold_desc = "매우 높은"
            elif final_threshold >= 0.3:
                threshold_desc = "높은"
            elif final_threshold >= 0.2:
                threshold_desc = "중간"
            else:
                threshold_desc = "낮은"
            
            explanation_parts.append(f"{threshold_desc} 유사도 수준의 사례를 찾아냈습니다.")
            
            # 신뢰도 안내
            if final_threshold < 0.3:
                explanation_parts.append("(참고용으로만 활용하시기 바랍니다)")
        
        return " ".join(explanation_parts)
    
    def generate_improvement_suggestions(self, cases: List[Dict]) -> List[str]:
        """개선 제안 생성"""
        suggestions = []
        
        if not cases:
            return suggestions
        
        # 통관 거부사례 기반 제안
        key_problems = self.extract_key_problems(cases)
        
        for problem, count in key_problems:
            if problem == '라벨':
                suggestions.append("• 제품 라벨에 원산지, 성분, 유통기한을 명확히 표기하세요")
            elif problem == '인증':
                suggestions.append("• 필요한 인증서류를 사전에 준비하고 검토하세요")
            elif problem == '성분':
                suggestions.append("• 제품 성분이 수입국 기준에 맞는지 확인하세요")
            elif problem == '검역':
                suggestions.append("• 검역 기준에 맞는 제품 상태를 유지하세요")
            elif problem == '세관':
                suggestions.append("• 세관 신고 서류를 정확히 작성하고 제출하세요")
            elif problem == '포장':
                suggestions.append("• 포장재가 수입국 기준에 맞는지 확인하세요")
            elif problem == '원산지':
                suggestions.append("• 원산지 표기가 정확한지 확인하세요")
        
        # 일반적인 제안 추가
        suggestions.extend([
            "• 과거 유사 사례를 기반으로 제품 정보를 신중히 점검하십시오",
            "• 관련 인증서류 및 시험성적서를 사전에 준비하십시오",
            "• 제품 라벨에 원산지, 수출자, 성분 정보를 명확히 표기하십시오"
        ])
        
        return suggestions[:8]  # 상위 8개만 반환 