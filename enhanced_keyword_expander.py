#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 강화된 키워드 확장 시스템
- 동의어 사전 확장
- 제품 카테고리별 키워드
- HS 코드 기반 연관 키워드
- 단어 단위 유사도 계산
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
import re
import pickle
import os

class EnhancedKeywordExpander:
    """강화된 키워드 확장 시스템"""
    
    def __init__(self):
        self.synonym_dict = self._load_synonym_dictionary()
        self.product_categories = self._load_product_categories()
        self.hs_code_keywords = self._load_hs_code_keywords()
        self.word_similarity_matrix = None
        self.word_vectorizer = None
        self._build_word_similarity_matrix()
    
    def _load_synonym_dictionary(self):
        """동의어 사전 로드"""
        return {
            # 라면 관련 동의어
            '라면': ['면류', '인스턴트', '즉석', '컵라면', '봉지라면', '생면', '건면', '우동', '소바', '파스타'],
            '면류': ['라면', '우동', '소바', '파스타', '스파게티', '국수', '냉면', '칼국수'],
            '인스턴트': ['즉석', '간편식', '조리식품', '가공식품', '레토르트'],
            
            # 국가 관련 동의어
            '중국': ['차이나', '중화', '중화인민공화국', 'PRC', 'China'],
            '미국': ['USA', 'US', '아메리카', 'United States', '미합중국'],
            '한국': ['대한민국', 'ROK', 'Korea', 'South Korea'],
            
            # 제품 상태 관련 동의어
            '신선': ['생', '냉장', '냉동', '냉각', '신선식품'],
            '가공': ['조리', '제조', '가공식품', '조리식품'],
            '건조': ['말린', '건조식품', '건면', '건조과일'],
            
            # 거부 사유 관련 동의어
            '위생': ['위생증명서', '위생검사', '위생기준', '위생규정'],
            '검역': ['검역증명서', '검역검사', '검역기준', '검역규정'],
            '원산지': ['원산지증명서', '원산지표시', '원산지기준'],
            '성분': ['성분분석', '성분표시', '성분기준', '영양성분'],
            '첨가물': ['식품첨가물', '방부제', '색소', '향료', '보존료'],
            '농약': ['농약잔류', '농약검사', '농약기준', '농약규정'],
            '중금속': ['납', '카드뮴', '수은', '비소', '중금속검사'],
            '미생물': ['세균', '바이러스', '곰팡이', '미생물검사', '미생물기준'],
            '방사능': ['방사능검사', '방사능기준', '방사능오염', '세슘', '요오드'],
            
            # 조치사항 관련 동의어
            '반송': ['반출', '반환', '송환', '반송처리'],
            '폐기': ['소각', '매립', '폐기처리', '폐기물처리'],
            '재검사': ['재검역', '재검사', '추가검사', '재시험'],
            '수정': ['보완', '수정서류', '보완서류', '재제출']
        }
    
    def _load_product_categories(self):
        """제품 카테고리별 키워드 로드"""
        return {
            '면류': {
                'keywords': ['라면', '우동', '소바', '파스타', '스파게티', '국수', '냉면', '칼국수', '면류'],
                'hs_codes': ['1902', '1905', '1103', '1108'],
                'related_terms': ['밀가루', '면', '국수', '조리면', '건면', '생면']
            },
            '과일': {
                'keywords': ['사과', '배', '복숭아', '포도', '오렌지', '바나나', '키위', '망고', '과일'],
                'hs_codes': ['0801', '0802', '0803', '0804', '0805', '0806', '0807', '0808', '0809'],
                'related_terms': ['신선과일', '건조과일', '냉동과일', '과일주스', '과일잼']
            },
            '채소': {
                'keywords': ['고추', '마늘', '양파', '당근', '양배추', '상추', '채소'],
                'hs_codes': ['0701', '0702', '0703', '0704', '0705', '0706', '0707', '0708', '0709'],
                'related_terms': ['신선채소', '냉동채소', '건조채소', '채소주스', '채소가공품']
            },
            '수산물': {
                'keywords': ['생선', '새우', '게', '조개', '굴', '전복', '수산물'],
                'hs_codes': ['0301', '0302', '0303', '0304', '0305', '0306', '0307'],
                'related_terms': ['신선수산물', '냉동수산물', '건조수산물', '수산가공품']
            },
            '육류': {
                'keywords': ['돼지고기', '소고기', '닭고기', '양고기', '육류'],
                'hs_codes': ['0201', '0202', '0203', '0204', '0205', '0206', '0207'],
                'related_terms': ['신선육류', '냉동육류', '육가공품', '육제품']
            },
            '유제품': {
                'keywords': ['우유', '치즈', '버터', '요구르트', '유제품'],
                'hs_codes': ['0401', '0402', '0403', '0404', '0405', '0406'],
                'related_terms': ['신선유제품', '냉동유제품', '유가공품', '유제품']
            }
        }
    
    def _load_hs_code_keywords(self):
        """HS 코드 기반 연관 키워드 로드"""
        return {
            # 면류 관련 HS 코드
            '1902': ['면류', '파스타', '스파게티', '라면', '우동', '소바'],
            '1905': ['빵', '과자', '제과', '제빵', '베이커리'],
            '1103': ['밀가루', '곡물가루', '분말'],
            '1108': ['전분', '녹말', '가공전분'],
            
            # 과일 관련 HS 코드
            '0801': ['코코넛', '브라질넛', '캐슈넛'],
            '0802': ['호두', '견과류'],
            '0803': ['바나나', '바나나류'],
            '0804': ['대추야자', '무화과', '파인애플', '아보카도'],
            '0805': ['오렌지', '감귤류'],
            '0806': ['포도', '포도류'],
            '0807': ['멜론', '수박', '과실류'],
            '0808': ['사과', '배', '석류'],
            '0809': ['살구', '체리', '복숭아', '자두'],
            
            # 채소 관련 HS 코드
            '0701': ['감자', '토란', '마', '고구마'],
            '0702': ['토마토', '토마토류'],
            '0703': ['양파', '마늘', '부추', '파'],
            '0704': ['양배추', '브로콜리', '콜리플라워'],
            '0705': ['상추', '치커리', '엔디브'],
            '0706': ['당근', '순무', '사탕무'],
            '0707': ['오이', '피클용오이'],
            '0708': ['콩', '완두콩'],
            '0709': ['기타채소', '채소류'],
            
            # 수산물 관련 HS 코드
            '0301': ['생선', '신선어류'],
            '0302': ['생선', '냉동어류'],
            '0303': ['생선', '냉동어류'],
            '0304': ['생선', '냉동어류'],
            '0305': ['생선', '염장어류'],
            '0306': ['갑각류', '새우', '게'],
            '0307': ['연체동물', '조개', '굴', '전복']
        }
    
    def _build_word_similarity_matrix(self):
        """단어 단위 유사도 행렬 구축"""
        try:
            # 모든 키워드를 수집
            all_words = set()
            
            # 동의어 사전에서 단어 수집
            for words in self.synonym_dict.values():
                all_words.update(words)
            
            # 제품 카테고리에서 단어 수집
            for category in self.product_categories.values():
                all_words.update(category['keywords'])
                all_words.update(category['related_terms'])
            
            # HS 코드 키워드에서 단어 수집
            for words in self.hs_code_keywords.values():
                all_words.update(words)
            
            # 단어 리스트로 변환
            word_list = list(all_words)
            
            # TF-IDF 벡터화
            self.word_vectorizer = TfidfVectorizer(
                analyzer='char',  # 문자 단위 분석
                ngram_range=(2, 4),  # 2-4글자 n-gram
                min_df=1
            )
            
            # 단어들을 벡터화
            word_vectors = self.word_vectorizer.fit_transform(word_list)
            
            # 유사도 행렬 계산
            self.word_similarity_matrix = cosine_similarity(word_vectors)
            
            # 단어-인덱스 매핑 저장
            self.word_to_index = {word: idx for idx, word in enumerate(word_list)}
            self.index_to_word = {idx: word for idx, word in enumerate(word_list)}
            
            print(f"✅ 단어 유사도 행렬 구축 완료: {len(word_list)}개 단어")
            
        except Exception as e:
            print(f"❌ 단어 유사도 행렬 구축 실패: {e}")
            self.word_similarity_matrix = None
    
    def calculate_word_similarity(self, word1, word2):
        """두 단어 간의 유사도 계산"""
        if self.word_similarity_matrix is None:
            return 0.0
        
        try:
            idx1 = self.word_to_index.get(word1)
            idx2 = self.word_to_index.get(word2)
            
            if idx1 is not None and idx2 is not None:
                return self.word_similarity_matrix[idx1][idx2]
            else:
                return 0.0
        except:
            return 0.0
    
    def find_similar_words(self, target_word, threshold=0.3, max_results=10):
        """유사한 단어들 찾기"""
        if self.word_similarity_matrix is None:
            return []
        
        try:
            target_idx = self.word_to_index.get(target_word)
            if target_idx is None:
                return []
            
            # 유사도 계산
            similarities = self.word_similarity_matrix[target_idx]
            
            # 유사한 단어들 찾기
            similar_words = []
            for idx, similarity in enumerate(similarities):
                if idx != target_idx and similarity >= threshold:
                    similar_words.append({
                        'word': self.index_to_word[idx],
                        'similarity': similarity
                    })
            
            # 유사도 순으로 정렬
            similar_words.sort(key=lambda x: x['similarity'], reverse=True)
            return similar_words[:max_results]
            
        except Exception as e:
            print(f"❌ 유사 단어 검색 실패: {e}")
            return []
    
    def expand_keywords_with_synonyms(self, keywords):
        """동의어를 이용한 키워드 확장"""
        expanded = set(keywords)
        
        for keyword in keywords:
            if keyword in self.synonym_dict:
                expanded.update(self.synonym_dict[keyword])
        
        return list(expanded)
    
    def expand_keywords_with_categories(self, keywords):
        """제품 카테고리를 이용한 키워드 확장"""
        expanded = set(keywords)
        
        for keyword in keywords:
            for category_name, category_info in self.product_categories.items():
                if keyword in category_info['keywords']:
                    expanded.update(category_info['keywords'])
                    expanded.update(category_info['related_terms'])
                    break
        
        return list(expanded)
    
    def expand_keywords_with_hs_codes(self, keywords):
        """HS 코드를 이용한 키워드 확장"""
        expanded = set(keywords)
        
        for keyword in keywords:
            for hs_code, hs_keywords in self.hs_code_keywords.items():
                if keyword in hs_keywords:
                    expanded.update(hs_keywords)
                    break
        
        return list(expanded)
    
    def expand_keywords_with_similarity(self, keywords, threshold=0.3):
        """유사도 기반 키워드 확장"""
        expanded = set(keywords)
        
        for keyword in keywords:
            similar_words = self.find_similar_words(keyword, threshold)
            for similar_word in similar_words:
                expanded.add(similar_word['word'])
        
        return list(expanded)
    
    def enhanced_expand_keywords(self, user_input, use_synonyms=True, use_categories=True, 
                               use_hs_codes=True, use_similarity=True, similarity_threshold=0.3):
        """통합 키워드 확장"""
        # 입력을 단어로 분리
        words = user_input.split()
        expanded_words = set(words)
        
        if use_synonyms:
            expanded_words.update(self.expand_keywords_with_synonyms(words))
        
        if use_categories:
            expanded_words.update(self.expand_keywords_with_categories(words))
        
        if use_hs_codes:
            expanded_words.update(self.expand_keywords_with_hs_codes(words))
        
        if use_similarity:
            expanded_words.update(self.expand_keywords_with_similarity(words, similarity_threshold))
        
        # 확장된 키워드들을 공백으로 연결
        expanded_input = ' '.join(expanded_words)
        
        return expanded_input, list(expanded_words)
    
    def get_expansion_info(self, user_input):
        """키워드 확장 정보 반환"""
        original_words = user_input.split()
        
        expansion_info = {
            'original_input': user_input,
            'original_words': original_words,
            'expansions': {}
        }
        
        # 동의어 확장
        synonym_expanded = self.expand_keywords_with_synonyms(original_words)
        expansion_info['expansions']['synonyms'] = {
            'words': synonym_expanded,
            'count': len(synonym_expanded)
        }
        
        # 카테고리 확장
        category_expanded = self.expand_keywords_with_categories(original_words)
        expansion_info['expansions']['categories'] = {
            'words': category_expanded,
            'count': len(category_expanded)
        }
        
        # HS 코드 확장
        hs_expanded = self.expand_keywords_with_hs_codes(original_words)
        expansion_info['expansions']['hs_codes'] = {
            'words': hs_expanded,
            'count': len(hs_expanded)
        }
        
        # 유사도 확장
        similarity_expanded = self.expand_keywords_with_similarity(original_words)
        expansion_info['expansions']['similarity'] = {
            'words': similarity_expanded,
            'count': len(similarity_expanded)
        }
        
        return expansion_info

# 사용 예시
if __name__ == "__main__":
    expander = EnhancedKeywordExpander()
    
    # 테스트
    test_input = "중국 라면"
    expanded_input, expanded_words = expander.enhanced_expand_keywords(test_input)
    
    print(f"원본 입력: {test_input}")
    print(f"확장된 입력: {expanded_input}")
    print(f"확장된 단어 수: {len(expanded_words)}")
    
    # 확장 정보 출력
    expansion_info = expander.get_expansion_info(test_input)
    print("\n확장 정보:")
    for method, info in expansion_info['expansions'].items():
        print(f"{method}: {info['count']}개 단어")
    
    # 유사 단어 테스트
    print(f"\n'라면'과 유사한 단어들:")
    similar_words = expander.find_similar_words('라면', threshold=0.2)
    for word_info in similar_words[:5]:
        print(f"  {word_info['word']}: {word_info['similarity']:.3f}") 