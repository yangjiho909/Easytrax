# integrated_nlg_engine.py
# 통합 자연어 생성 엔진

from typing import Dict, List, Any, Optional
from customs_analysis_nlg import CustomsAnalysisNLG
from regulation_nlg import RegulationNLG

class IntegratedNLGEngine:
    """통합 자연어 생성 엔진"""
    
    def __init__(self):
        self.customs_nlg = CustomsAnalysisNLG()
        self.regulation_nlg = RegulationNLG()
    
    def generate_comprehensive_response(self, 
                                      user_query: str,
                                      customs_results: List[Dict],
                                      regulation_results: Optional[Dict] = None,
                                      threshold_info: Optional[Dict] = None) -> str:
        """종합적인 자연어 응답 생성"""
        
        response_parts = []
        
        # 1. 통관 거부사례 분석 결과
        if customs_results:
            customs_summary = self.customs_nlg.generate_customs_summary(
                customs_results, user_query
            )
            response_parts.append(customs_summary)
            
            # 임계값 설명
            if threshold_info:
                threshold_explanation = self.customs_nlg.generate_threshold_explanation(
                    threshold_info.get('final_threshold', 0.3),
                    threshold_info.get('initial_threshold', 0.3),
                    threshold_info.get('retry_count', 0)
                )
                response_parts.append(threshold_explanation)
        
        # 2. 규제정보 요약
        if regulation_results:
            regulation_summary = self.regulation_nlg.generate_regulation_summary(
                regulation_results.get('country', ''),
                regulation_results.get('product', ''),
                regulation_results.get('regulations', {})
            )
            response_parts.append(regulation_summary)
        
        # 3. 개선 제안
        improvement_suggestions = self.generate_improvement_suggestions(
            customs_results, regulation_results
        )
        if improvement_suggestions:
            response_parts.append(improvement_suggestions)
        
        return "\n\n".join(response_parts)
    
    def generate_improvement_suggestions(self, 
                                       customs_results: List[Dict],
                                       regulation_results: Optional[Dict] = None) -> str:
        """개선 제안 생성"""
        
        suggestions = []
        
        # 통관 거부사례 기반 제안
        if customs_results:
            customs_suggestions = self.customs_nlg.generate_improvement_suggestions(customs_results)
            suggestions.extend(customs_suggestions)
        
        # 규제정보 기반 제안
        if regulation_results:
            regulations = regulation_results.get('regulations', {})
            if '필요서류' in regulations:
                suggestions.append("• 규제정보에 명시된 필요서류를 모두 준비하세요")
            if '주의사항' in regulations:
                suggestions.append("• 규제정보의 주의사항을 반드시 확인하세요")
        
        if suggestions:
            return "🛠️ 개선 제안:\n" + "\n".join(suggestions[:8])  # 상위 8개만
        
        return ""
    
    def generate_detailed_regulation_response(self, 
                                            country: str, 
                                            product: str, 
                                            regulations: Dict) -> str:
        """상세 규제정보 응답 생성"""
        return self.regulation_nlg.generate_detailed_explanation(
            country, product, regulations
        )
    
    def generate_customs_analysis_response(self,
                                         cases: List[Dict],
                                         user_query: str,
                                         threshold_info: Optional[Dict] = None) -> str:
        """통관 거부사례 분석 응답 생성"""
        response_parts = []
        
        # 요약 생성
        summary = self.customs_nlg.generate_customs_summary(cases, user_query)
        response_parts.append(summary)
        
        # 임계값 설명
        if threshold_info:
            threshold_explanation = self.customs_nlg.generate_threshold_explanation(
                threshold_info.get('final_threshold', 0.3),
                threshold_info.get('initial_threshold', 0.3),
                threshold_info.get('retry_count', 0)
            )
            response_parts.append(threshold_explanation)
        
        # 개선 제안
        suggestions = self.customs_nlg.generate_improvement_suggestions(cases)
        if suggestions:
            response_parts.append("🛠️ 개선 제안:\n" + "\n".join(suggestions))
        
        return "\n\n".join(response_parts)
    
    def generate_regulation_info_response(self,
                                        country: str,
                                        product: str,
                                        regulations: Dict,
                                        show_detail: bool = False) -> str:
        """규제정보 응답 생성"""
        response_parts = []
        
        # 요약 생성
        summary = self.regulation_nlg.generate_regulation_summary(country, product, regulations)
        response_parts.append(summary)
        
        # 상세 정보 (요청시에만)
        if show_detail:
            detailed_info = self.regulation_nlg.generate_detailed_explanation(
                country, product, regulations
            )
            response_parts.append(detailed_info)
        
        return "\n\n".join(response_parts)
    
    def generate_regulation_summary(self, regulations: Dict) -> str:
        """규제정보 요약 생성 (단순 버전)"""
        if not regulations:
            return "❌ 규제정보가 없습니다."
        
        # 국가와 제품 추출
        country = regulations.get('국가', '알 수 없음')
        product = regulations.get('제품', '알 수 없음')
        
        summary_parts = []
        summary_parts.append(f"📋 {country} - {product} 규제정보 요약")
        summary_parts.append("=" * 50)
        
        # 주요 정보 추출
        if '제한사항' in regulations:
            restrictions = regulations['제한사항']
            if isinstance(restrictions, list) and restrictions:
                summary_parts.append(f"🚫 주요 제한사항: {len(restrictions)}개")
                for i, restriction in enumerate(restrictions[:3], 1):  # 상위 3개만
                    summary_parts.append(f"   {i}. {restriction}")
                if len(restrictions) > 3:
                    summary_parts.append(f"   ... 외 {len(restrictions)-3}개")
        
        if '필요서류' in regulations:
            documents = regulations['필요서류']
            if isinstance(documents, list) and documents:
                summary_parts.append(f"📄 필요서류: {len(documents)}개")
                for i, doc in enumerate(documents[:3], 1):  # 상위 3개만
                    summary_parts.append(f"   {i}. {doc}")
                if len(documents) > 3:
                    summary_parts.append(f"   ... 외 {len(documents)-3}개")
        
        if '추가정보' in regulations:
            additional = regulations['추가정보']
            if isinstance(additional, dict):
                if '최종업데이트' in additional:
                    summary_parts.append(f"🕐 최종업데이트: {additional['최종업데이트']}")
                if '데이터_상태' in additional:
                    summary_parts.append(f"📊 데이터상태: {additional['데이터_상태']}")
        
        return "\n".join(summary_parts) 