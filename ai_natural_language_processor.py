"""
무료 AI 서비스를 활용한 자연어 처리 모듈
Hugging Face, OpenAI API (무료 티어), 로컬 모델 등을 활용
"""

import json
import logging
import requests
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re
import os

logger = logging.getLogger(__name__)

@dataclass
class AIProcessedQuery:
    """AI 처리된 질의 결과"""
    original_query: str
    processed_query: str
    intent: str
    entities: Dict[str, Any]
    confidence: float
    ai_service_used: str

class FreeAINaturalLanguageProcessor:
    """무료 AI 서비스를 활용한 자연어 처리기"""
    
    def __init__(self):
        self.huggingface_api_key = os.getenv('HUGGINGFACE_API_KEY', '')
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '')
        
        # 무료 AI 서비스 설정
        self.services = {
            'huggingface': {
                'enabled': bool(self.huggingface_api_key),
                'url': 'https://api-inference.huggingface.co/models/',
                'models': {
                    'text_classification': 'facebook/bart-large-mnli',
                    'question_answering': 'deepset/roberta-base-squad2',
                    'text_generation': 'gpt2'
                }
            },
            'openai': {
                'enabled': bool(self.openai_api_key),
                'url': 'https://api.openai.com/v1/',
                'models': {
                    'chat': 'gpt-3.5-turbo',
                    'completion': 'text-davinci-003'
                }
            }
        }
        
        # 로컬 규칙 기반 처리
        self.intent_patterns = {
            'regulation': [
                r'규제|서류|필요|요구|준수|법규|법령',
                r'중국.*라면|미국.*라면|수출.*규제|FDA|GB'
            ],
            'statistics': [
                r'통계|수치|데이터|비교|분석|추이|성장률|점유율',
                r'HS코드|수출.*통계|수입.*통계|무역.*통계'
            ],
            'market_analysis': [
                r'시장|동향|전망|성장|리스크|기회|경쟁',
                r'시장.*분석|동향.*분석|전략.*보고서'
            ],
            'documentation': [
                r'서류|문서|인증서|증명서|신고서|신청서',
                r'필요.*서류|준비.*서류|제출.*서류'
            ]
        }
        
        self.entity_patterns = {
            'country': [
                r'중국|차이나|중화',
                r'미국|USA|US|아메리카'
            ],
            'product': [
                r'라면|면류|인스턴트|즉석',
                r'식품|음식|가공식품'
            ],
            'hs_code': [
                r'HS코드|HS.*코드|코드.*\d{6}',
                r'\d{6}.*코드'
            ],
            'time_period': [
                r'\d{4}년|\d{4}년.*분기|\d{4}년.*월',
                r'올해|작년|내년|최근|현재'
            ]
        }
    
    def process_query(self, query: str) -> AIProcessedQuery:
        """질의를 AI로 처리하여 구조화된 정보 추출"""
        try:
            # 1. 의도 분석
            intent = self._analyze_intent(query)
            
            # 2. 엔티티 추출
            entities = self._extract_entities(query)
            
            # 3. AI 서비스를 통한 고급 처리
            processed_query = self._enhance_with_ai(query, intent, entities)
            
            # 4. 신뢰도 계산
            confidence = self._calculate_confidence(query, intent, entities)
            
            # 5. 사용된 AI 서비스 결정
            ai_service = self._determine_ai_service()
            
            return AIProcessedQuery(
                original_query=query,
                processed_query=processed_query,
                intent=intent,
                entities=entities,
                confidence=confidence,
                ai_service_used=ai_service
            )
            
        except Exception as e:
            logger.error(f"AI 처리 중 오류: {e}")
            # 폴백: 기본 규칙 기반 처리
            return self._fallback_processing(query)
    
    def _analyze_intent(self, query: str) -> str:
        """의도 분석"""
        query_lower = query.lower()
        
        # AI 서비스 활용 (가능한 경우)
        if self.services['huggingface']['enabled']:
            try:
                return self._huggingface_intent_analysis(query)
            except:
                pass
        
        # 규칙 기반 분석
        scores = {}
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    score += 1
            scores[intent] = score
        
        # 가장 높은 점수의 의도 반환
        if scores:
            return max(scores, key=scores.get)
        
        return 'general'
    
    def _extract_entities(self, query: str) -> Dict[str, Any]:
        """엔티티 추출"""
        entities = {}
        
        for entity_type, patterns in self.entity_patterns.items():
            matches = []
            for pattern in patterns:
                found = re.findall(pattern, query, re.IGNORECASE)
                matches.extend(found)
            
            if matches:
                entities[entity_type] = list(set(matches))
        
        return entities
    
    def _enhance_with_ai(self, query: str, intent: str, entities: Dict[str, Any]) -> str:
        """AI 서비스를 통한 질의 향상"""
        
        # OpenAI API 활용 (무료 티어)
        if self.services['openai']['enabled']:
            try:
                return self._openai_enhancement(query, intent, entities)
            except Exception as e:
                logger.warning(f"OpenAI API 오류: {e}")
        
        # Hugging Face 활용
        if self.services['huggingface']['enabled']:
            try:
                return self._huggingface_enhancement(query, intent, entities)
            except Exception as e:
                logger.warning(f"Hugging Face API 오류: {e}")
        
        # 기본 향상
        return self._basic_enhancement(query, intent, entities)
    
    def _openai_enhancement(self, query: str, intent: str, entities: Dict[str, Any]) -> str:
        """OpenAI API를 통한 질의 향상"""
        try:
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            # 컨텍스트 기반 프롬프트 생성
            context = self._build_context(intent, entities)
            
            prompt = f"""
다음은 무역/수출입 관련 질문입니다. 더 구체적이고 명확한 질문으로 개선해주세요.

원본 질문: {query}
의도: {intent}
추출된 정보: {json.dumps(entities, ensure_ascii=False)}

컨텍스트: {context}

개선된 질문:
"""
            
            data = {
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {'role': 'system', 'content': '당신은 무역/수출입 전문가입니다. 질문을 더 구체적이고 명확하게 개선해주세요.'},
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 150,
                'temperature': 0.3
            }
            
            response = requests.post(
                f"{self.services['openai']['url']}chat/completions",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            
        except Exception as e:
            logger.error(f"OpenAI API 호출 오류: {e}")
        
        return query
    
    def _huggingface_enhancement(self, query: str, intent: str, entities: Dict[str, Any]) -> str:
        """Hugging Face를 통한 질의 향상"""
        try:
            headers = {'Authorization': f'Bearer {self.huggingface_api_key}'}
            
            # 텍스트 분류를 통한 의도 확인
            data = {
                'inputs': query,
                'parameters': {
                    'candidate_labels': ['regulation', 'statistics', 'market_analysis', 'documentation', 'general']
                }
            }
            
            response = requests.post(
                f"{self.services['huggingface']['url']}{self.services['huggingface']['models']['text_classification']}",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                # 분류 결과를 바탕으로 질의 개선
                return self._improve_query_based_on_classification(query, result)
            
        except Exception as e:
            logger.error(f"Hugging Face API 호출 오류: {e}")
        
        return query
    
    def _basic_enhancement(self, query: str, intent: str, entities: Dict[str, Any]) -> str:
        """기본 규칙 기반 질의 향상"""
        enhanced = query
        
        # 국가 정보 추가
        if 'country' not in entities and intent in ['regulation', 'statistics']:
            if '중국' in query or '차이나' in query:
                entities['country'] = ['중국']
            elif '미국' in query or 'USA' in query:
                entities['country'] = ['미국']
        
        # 제품 정보 추가
        if 'product' not in entities and '라면' in query:
            entities['product'] = ['라면']
        
        # 의도별 키워드 추가
        if intent == 'regulation':
            if '규제' not in query and '서류' not in query:
                enhanced += " 규제 요구사항"
        elif intent == 'statistics':
            if '통계' not in query and '수치' not in query:
                enhanced += " 통계 데이터"
        
        return enhanced
    
    def _build_context(self, intent: str, entities: Dict[str, Any]) -> str:
        """컨텍스트 구축"""
        context_parts = []
        
        if intent == 'regulation':
            context_parts.append("규제 및 서류 요구사항 관련")
        elif intent == 'statistics':
            context_parts.append("무역 통계 및 수치 관련")
        elif intent == 'market_analysis':
            context_parts.append("시장 분석 및 동향 관련")
        
        if 'country' in entities:
            countries = ', '.join(entities['country'])
            context_parts.append(f"대상 국가: {countries}")
        
        if 'product' in entities:
            products = ', '.join(entities['product'])
            context_parts.append(f"제품: {products}")
        
        return ' | '.join(context_parts)
    
    def _calculate_confidence(self, query: str, intent: str, entities: Dict[str, Any]) -> float:
        """신뢰도 계산"""
        confidence = 0.5  # 기본값
        
        # 엔티티 개수에 따른 점수
        entity_count = len(entities)
        confidence += min(entity_count * 0.1, 0.3)
        
        # 의도 명확성
        if intent != 'general':
            confidence += 0.2
        
        # 질문 길이 (적절한 길이일 때 높은 점수)
        query_length = len(query)
        if 10 <= query_length <= 100:
            confidence += 0.1
        
        # 특정 키워드 존재
        specific_keywords = ['라면', '중국', '미국', '수출', '규제', '통계']
        keyword_count = sum(1 for keyword in specific_keywords if keyword in query)
        confidence += min(keyword_count * 0.05, 0.2)
        
        return min(confidence, 1.0)
    
    def _determine_ai_service(self) -> str:
        """사용된 AI 서비스 결정"""
        if self.services['openai']['enabled']:
            return 'OpenAI GPT-3.5'
        elif self.services['huggingface']['enabled']:
            return 'Hugging Face'
        else:
            return 'Rule-based'
    
    def _fallback_processing(self, query: str) -> AIProcessedQuery:
        """폴백 처리"""
        return AIProcessedQuery(
            original_query=query,
            processed_query=query,
            intent='general',
            entities={},
            confidence=0.5,
            ai_service_used='Rule-based (fallback)'
        )
    
    def generate_natural_response(self, query: str, data_results: Dict[str, Any]) -> str:
        """자연스러운 응답 생성"""
        try:
            # AI 서비스를 통한 응답 생성
            if self.services['openai']['enabled']:
                return self._generate_openai_response(query, data_results)
            elif self.services['huggingface']['enabled']:
                return self._generate_huggingface_response(query, data_results)
            else:
                return self._generate_improved_rule_based_response(query, data_results)
                
        except Exception as e:
            logger.error(f"응답 생성 중 오류: {e}")
            return self._generate_improved_rule_based_response(query, data_results)
    
    def _generate_openai_response(self, query: str, data_results: Dict[str, Any]) -> str:
        """무료 AI 서비스를 통한 자연스러운 응답 생성"""
        try:
            # 데이터 요약
            data_summary = self._summarize_data_for_ai(data_results)
            
            # 무료 AI 서비스 활용 (Hugging Face 또는 로컬 모델)
            if self.huggingface_api_key:
                return self._generate_huggingface_response(query, data_summary)
            else:
                return self._generate_improved_rule_based_response(query, data_results)
            
        except Exception as e:
            logger.error(f"AI 응답 생성 오류: {e}")
            return self._generate_improved_rule_based_response(query, data_results)
    
    def _generate_huggingface_response(self, query: str, data_summary: str) -> str:
        """Hugging Face를 통한 응답 생성"""
        try:
            headers = {'Authorization': f'Bearer {self.huggingface_api_key}'}
            
            # 텍스트 생성 모델 사용
            prompt = f"질문: {query}\n데이터: {data_summary}\n답변:"
            
            data = {
                'inputs': prompt,
                'parameters': {
                    'max_length': 300,
                    'temperature': 0.7,
                    'do_sample': True
                }
            }
            
            response = requests.post(
                f"{self.services['huggingface']['url']}{self.services['huggingface']['models']['text_generation']}",
                headers=headers,
                json=data,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                return result[0]['generated_text'].split('답변:')[-1].strip()
            
        except Exception as e:
            logger.error(f"Hugging Face 응답 생성 오류: {e}")
        
        return self._generate_improved_rule_based_response(query, {})
    
    def _generate_improved_rule_based_response(self, query: str, data_results: Dict[str, Any]) -> str:
        """개선된 규칙 기반 응답 생성 (더 자연스럽게)"""
        response_parts = []
        
        # 질문 의도에 따른 자연스러운 시작
        if '규제' in query or '서류' in query or '인증' in query:
            response_parts.append("🔍 **규제 정보 안내**")
        elif '통계' in query or '수치' in query or '데이터' in query:
            response_parts.append("📊 **무역 통계 현황**")
        elif '시장' in query or '동향' in query or '전망' in query:
            response_parts.append("📈 **시장 분석 결과**")
        else:
            response_parts.append("💡 **수출 정보 안내**")
        
        # 규제 정보 (중복 제거 및 자연스럽게)
        if data_results.get('regulations'):
            regulations = data_results['regulations']
            # 중복 제거
            unique_regs = []
            seen = set()
            for reg in regulations:
                key = f"{reg[1]}_{reg[2]}"
                if key not in seen:
                    unique_regs.append(reg)
                    seen.add(key)
            
            for reg in unique_regs[:2]:  # 최대 2개만
                country = reg[1]
                product = reg[2]
                title = reg[3]
                description = reg[4]
                requirements = reg[5]
                
                response_parts.append(f"\n**{country} {product} 수출 규제**")
                if description and description != title:
                    response_parts.append(f"• {description}")
                
                if requirements and requirements != description:
                    # 요구사항을 더 구체적으로 표시
                    if '서류' in requirements or '인증' in requirements:
                        response_parts.append(f"• **필요 서류**: {requirements}")
                    else:
                        response_parts.append(f"• **주요 요구사항**: {requirements}")
                
                response_parts.append(f"• **출처**: {reg[7]}")
        
        # 무역 통계
        if data_results.get('trade_statistics'):
            response_parts.append("\n📊 **무역 통계 현황**")
            for stat in data_results['trade_statistics'][:2]:
                country = stat[0]
                product = stat[2]
                period = stat[3]
                export_amount = stat[5]
                import_amount = stat[6]
                growth_rate = stat[8]
                
                response_parts.append(f"\n**{country} {product} ({period})**")
                response_parts.append(f"• 수출액: {export_amount:,.0f}만원")
                response_parts.append(f"• 수입액: {import_amount:,.0f}만원")
                if growth_rate:
                    response_parts.append(f"• 성장률: {growth_rate:+.1f}%")
                response_parts.append(f"• 출처: {stat[10]}")
        
        # 시장 분석
        if data_results.get('market_analysis'):
            response_parts.append("\n📈 **시장 분석 결과**")
            for analysis in data_results['market_analysis'][:1]:
                title = analysis[4]
                content = analysis[5]
                response_parts.append(f"\n**{title}**")
                response_parts.append(f"• {content[:150]}...")
                response_parts.append(f"• 출처: {analysis[9]}")
        
        # 데이터가 없는 경우
        if not any([data_results.get('regulations'), data_results.get('trade_statistics'), data_results.get('market_analysis')]):
            response_parts.append("\n😔 **죄송합니다**")
            response_parts.append("현재 해당 정보를 찾을 수 없습니다.")
            response_parts.append("다른 키워드로 검색해 보시거나, 더 구체적인 질문을 해주세요.")
        
        return '\n'.join(response_parts)
    
    def _summarize_data_for_ai(self, data_results: Dict[str, Any]) -> str:
        """AI용 데이터 요약"""
        summary_parts = []
        
        if data_results.get('regulations'):
            summary_parts.append("📋 규제 정보:")
            for reg in data_results['regulations'][:2]:
                summary_parts.append(f"- {reg[1]} {reg[2]}: {reg[4]}")
        
        if data_results.get('trade_statistics'):
            summary_parts.append("📊 무역 통계:")
            for stat in data_results['trade_statistics'][:2]:
                summary_parts.append(f"- {stat[0]} {stat[2]}: 수출 {stat[5]:,.0f}만원, 수입 {stat[6]:,.0f}만원")
        
        if data_results.get('market_analysis'):
            summary_parts.append("📈 시장 분석:")
            for analysis in data_results['market_analysis'][:1]:
                summary_parts.append(f"- {analysis[4]}: {analysis[5][:100]}...")
        
        return '\n'.join(summary_parts) 