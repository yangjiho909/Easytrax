#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pickle
import pandas as pd
import numpy as np
from collections import Counter
import re
from datetime import datetime

class DashboardAnalyzer:
    """통관 거부사례 대시보드 분석 시스템"""
    
    def __init__(self):
        self.raw_data = None
        self.load_data()
    
    def load_data(self):
        """raw_data.pkl 로딩"""
        try:
            with open("model/raw_data.pkl", "rb") as f:
                self.raw_data = pickle.load(f)
            print(f"✅ 데이터 로딩 완료! 총 {len(self.raw_data):,}건")
        except Exception as e:
            print(f"❌ 데이터 로딩 실패: {e}")
            self.raw_data = None
    
    def analyze_rejection_reasons(self, top_n=10):
        """가장 많이 발생한 통관 거부 사유 분석"""
        if self.raw_data is None:
            return None
        
        print("🔍 통관 거부 사유 분석")
        print("=" * 60)
        
        # 문제사유 컬럼 확인
        if "문제사유" not in self.raw_data.columns:
            print("❌ 문제사유 컬럼이 없습니다.")
            return None
        
        # 문제사유 텍스트 정리
        reasons = self.raw_data["문제사유"].dropna()
        reasons = reasons[reasons != "정보 없음"]
        
        if len(reasons) == 0:
            print("❌ 분석 가능한 문제사유 데이터가 없습니다.")
            return None
        
        print(f"📊 분석 대상: {len(reasons):,}건")
        
        # 1. 전체 문제사유 빈도 분석
        print(f"\n📋 1. 전체 문제사유 빈도 (상위 {top_n}개)")
        print("-" * 50)
        
        reason_counts = Counter(reasons)
        top_reasons = reason_counts.most_common(top_n)
        
        for i, (reason, count) in enumerate(top_reasons, 1):
            percentage = (count / len(reasons)) * 100
            print(f"{i:2d}. {reason[:60]}{'...' if len(reason) > 60 else ''}")
            print(f"    📊 {count:,}건 ({percentage:.1f}%)")
            print()
        
        # 2. 문제 유형별 분류
        print(f"📋 2. 문제 유형별 분류")
        print("-" * 50)
        
        problem_categories = {
            '서류/인증': ['서류', '인증', '증명', '허가', '승인', '등록'],
            '라벨/표시': ['라벨', '표시', '표기', '인쇄', '부착'],
            '성분/첨가물': ['성분', '첨가물', '방부제', '색소', '화학물질'],
            '검역/위생': ['검역', '위생', '미생물', '농약', '방사능'],
            '세관/통관': ['세관', '통관', '신고', '서류', '신고서'],
            '포장/용기': ['포장', '용기', '포장재'],
            '원산지/제조국': ['원산지', '제조국', '생산지'],
            '품질/기준': ['품질', '기준', '불합격', '검사']
        }
        
        category_counts = {}
        for category, keywords in problem_categories.items():
            count = 0
            for reason in reasons:
                if any(keyword in reason for keyword in keywords):
                    count += 1
            if count > 0:
                category_counts[category] = count
        
        # 카테고리별 정렬
        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        
        for category, count in sorted_categories:
            percentage = (count / len(reasons)) * 100
            print(f"🔸 {category:<15}: {count:,}건 ({percentage:.1f}%)")
        
        return {
            'top_reasons': top_reasons,
            'category_counts': category_counts,
            'total_analyzed': len(reasons)
        }
    
    def analyze_by_country(self, top_n=15):
        """국가별 통관 거부 현황 분석"""
        if self.raw_data is None:
            return None
        
        print("\n🌍 국가별 통관 거부 현황 분석")
        print("=" * 60)
        
        # 수입국 분석
        if "수입국" not in self.raw_data.columns:
            print("❌ 수입국 컬럼이 없습니다.")
            return None
        
        countries = self.raw_data["수입국"].dropna()
        countries = countries[countries != "정보 없음"]
        
        if len(countries) == 0:
            print("❌ 분석 가능한 수입국 데이터가 없습니다.")
            return None
        
        print(f"📊 분석 대상: {len(countries):,}건")
        
        # 1. 전체 국가별 빈도
        country_counts = Counter(countries)
        top_countries = country_counts.most_common(top_n)
        
        print(f"\n📋 1. 국가별 통관 거부 빈도 (상위 {top_n}개)")
        print("-" * 50)
        
        for i, (country, count) in enumerate(top_countries, 1):
            percentage = (count / len(countries)) * 100
            print(f"{i:2d}. {country:<15} {count:,}건 ({percentage:.1f}%)")
        
        # 2. 한국 수출 관련 분석
        print(f"\n📋 2. 한국 수출 관련 분석")
        print("-" * 50)
        
        # 한국이 원산지인 경우
        korean_origin = self.raw_data[self.raw_data["원산지"].str.contains("한국|대한민국", na=False)]
        
        if len(korean_origin) > 0:
            korean_countries = korean_origin["수입국"].value_counts().head(10)
            print(f"🇰🇷 한국 원산지 통관 거부 (총 {len(korean_origin):,}건)")
            
            for i, (country, count) in enumerate(korean_countries.items(), 1):
                percentage = (count / len(korean_origin)) * 100
                print(f"   {i:2d}. {country:<15} {count:,}건 ({percentage:.1f}%)")
        else:
            print("🇰🇷 한국 원산지 데이터가 없습니다.")
        
        return {
            'top_countries': top_countries,
            'korean_origin_data': len(korean_origin) if len(korean_origin) > 0 else 0,
            'total_analyzed': len(countries)
        }
    
    def analyze_by_product(self, top_n=15):
        """품목별 통관 거부 현황 분석"""
        if self.raw_data is None:
            return None
        
        print("\n📦 품목별 통관 거부 현황 분석")
        print("=" * 60)
        
        # 품목 분석
        if "품목" not in self.raw_data.columns:
            print("❌ 품목 컬럼이 없습니다.")
            return None
        
        items = self.raw_data["품목"].dropna()
        items = items[items != "정보 없음"]
        
        if len(items) == 0:
            print("❌ 분석 가능한 품목 데이터가 없습니다.")
            return None
        
        print(f"📊 분석 대상: {len(items):,}건")
        
        # 1. 전체 품목별 빈도
        item_counts = Counter(items)
        top_items = item_counts.most_common(top_n)
        
        print(f"\n📋 1. 품목별 통관 거부 빈도 (상위 {top_n}개)")
        print("-" * 50)
        
        for i, (item, count) in enumerate(top_items, 1):
            percentage = (count / len(items)) * 100
            print(f"{i:2d}. {item:<25} {count:,}건 ({percentage:.1f}%)")
        
        # 2. 한국 주요 수출품목 분석
        print(f"\n📋 2. 한국 주요 수출품목 분석")
        print("-" * 50)
        
        korean_products = ['라면', '김치', '소주', '전자제품', '자동차', '반도체', '화장품', '의류', '신발']
        
        for product in korean_products:
            product_data = items[items.str.contains(product, na=False)]
            if len(product_data) > 0:
                print(f"🔸 {product:<10}: {len(product_data):,}건")
        
        return {
            'top_items': top_items,
            'total_analyzed': len(items)
        }
    
    def analyze_trends(self):
        """시계열 트렌드 분석 (출처파일 기준)"""
        if self.raw_data is None:
            return None
        
        print("\n📈 시계열 트렌드 분석")
        print("=" * 60)
        
        if "출처파일" not in self.raw_data.columns:
            print("❌ 출처파일 컬럼이 없습니다.")
            return None
        
        # 출처파일별 데이터 수
        file_counts = self.raw_data["출처파일"].value_counts()
        
        print(f"📊 파일별 데이터 분포")
        print("-" * 50)
        
        for i, (file, count) in enumerate(file_counts.items(), 1):
            percentage = (count / len(self.raw_data)) * 100
            print(f"{i:2d}. {file:<30} {count:,}건 ({percentage:.1f}%)")
        
        return {
            'file_distribution': file_counts.to_dict(),
            'total_files': len(file_counts)
        }
    
    def generate_strategic_insights(self):
        """수출 전략 인사이트 생성"""
        if self.raw_data is None:
            return None
        
        print("\n🎯 수출 전략 인사이트")
        print("=" * 60)
        
        insights = []
        
        # 1. 가장 위험한 수입국
        countries = self.raw_data["수입국"].dropna()
        country_counts = Counter(countries)
        top_risky_countries = country_counts.most_common(5)
        
        print("🚨 가장 위험한 수입국 (통관 거부 빈도 기준)")
        print("-" * 50)
        for i, (country, count) in enumerate(top_risky_countries, 1):
            print(f"{i}. {country}: {count:,}건")
            insights.append(f"⚠️ {country}은(는) 통관 거부가 {count:,}건으로 가장 위험한 수입국입니다.")
        
        # 2. 가장 문제가 되는 품목
        items = self.raw_data["품목"].dropna()
        item_counts = Counter(items)
        top_problematic_items = item_counts.most_common(5)
        
        print(f"\n📦 가장 문제가 되는 품목")
        print("-" * 50)
        for i, (item, count) in enumerate(top_problematic_items, 1):
            print(f"{i}. {item}: {count:,}건")
            insights.append(f"📦 {item}은(는) 통관 거부가 {count:,}건으로 가장 문제가 되는 품목입니다.")
        
        # 3. 주요 문제 유형
        reasons = self.raw_data["문제사유"].dropna()
        reason_counts = Counter(reasons)
        top_reasons = reason_counts.most_common(3)
        
        print(f"\n❌ 주요 문제 유형")
        print("-" * 50)
        for i, (reason, count) in enumerate(top_reasons, 1):
            short_reason = reason[:50] + "..." if len(reason) > 50 else reason
            print(f"{i}. {short_reason}")
            insights.append(f"❌ '{short_reason}'이(가) 주요 문제 유형입니다.")
        
        # 4. 한국 수출 특화 분석
        korean_origin = self.raw_data[self.raw_data["원산지"].str.contains("한국|대한민국", na=False)]
        
        if len(korean_origin) > 0:
            print(f"\n🇰🇷 한국 수출 특화 분석")
            print("-" * 50)
            
            # 한국 수출 시 가장 위험한 국가
            korean_countries = korean_origin["수입국"].value_counts().head(3)
            for i, (country, count) in enumerate(korean_countries.items(), 1):
                print(f"{i}. {country}: {count:,}건")
                insights.append(f"🇰🇷 한국 수출 시 {country}이(가) 가장 위험한 국가입니다 ({count:,}건).")
            
            # 한국 수출 시 가장 문제가 되는 품목
            korean_items = korean_origin["품목"].value_counts().head(3)
            for i, (item, count) in enumerate(korean_items.items(), 1):
                print(f"{i}. {item}: {count:,}건")
                insights.append(f"🇰🇷 한국 수출 시 {item}이(가) 가장 문제가 되는 품목입니다 ({count:,}건).")
        
        return insights
    
    def generate_dashboard_report(self):
        """종합 대시보드 리포트 생성"""
        if self.raw_data is None:
            print("❌ 데이터가 로드되지 않았습니다.")
            return
        
        print("📊 KATI 통관 거부사례 대시보드 리포트")
        print("=" * 80)
        print(f"📅 생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 총 데이터: {len(self.raw_data):,}건")
        print("=" * 80)
        
        # 각 분석 실행
        reasons_analysis = self.analyze_rejection_reasons()
        country_analysis = self.analyze_by_country()
        product_analysis = self.analyze_by_product()
        trend_analysis = self.analyze_trends()
        strategic_insights = self.generate_strategic_insights()
        
        # 종합 요약
        print(f"\n📋 종합 요약")
        print("=" * 80)
        
        if reasons_analysis:
            print(f"🔍 문제사유 분석: {reasons_analysis['total_analyzed']:,}건")
        if country_analysis:
            print(f"🌍 국가별 분석: {country_analysis['total_analyzed']:,}건")
        if product_analysis:
            print(f"📦 품목별 분석: {product_analysis['total_analyzed']:,}건")
        if trend_analysis:
            print(f"📈 트렌드 분석: {trend_analysis['total_files']}개 파일")
        
        print(f"\n💡 전략적 제안")
        print("=" * 80)
        if strategic_insights:
            for i, insight in enumerate(strategic_insights[:10], 1):  # 상위 10개만
                print(f"{i}. {insight}")
        
        print(f"\n✅ 대시보드 리포트 생성 완료!")

def main():
    """대시보드 분석 실행"""
    analyzer = DashboardAnalyzer()
    analyzer.generate_dashboard_report()

if __name__ == "__main__":
    main() 