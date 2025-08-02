#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
간단한 준수성 분석 테스트
"""

def test_basic_compliance():
    """기본 준수성 분석 테스트"""
    print("🔍 기본 준수성 분석 테스트")
    print("=" * 50)
    
    # 테스트 데이터 1: 완벽한 데이터
    perfect_data = {
        "company_info": {
            "company_name": "한국식품(주)",
            "address": "서울특별시 강남구",
            "phone": "02-1234-5678",
            "email": "test@company.com",
            "representative": "홍길동"
        },
        "product_info": {
            "product_name": "한국 라면",
            "manufacturer": "한국식품(주)",
            "origin": "대한민국",
            "expiry_date": "2026-12-31",
            "nutrition": {
                "열량": "400 kcal",
                "단백질": "12g",
                "지방": "15g",
                "탄수화물": "60g",
                "나트륨": "800mg",
                "당류": "5g"
            },
            "ingredients": ["면류", "스프", "야채", "조미료"],
            "allergy_ingredients": ["밀", "대두"],
            "storage_method": "서늘한 곳에 보관"
        },
        "prepared_documents": [
            "상업송장", "포장명세서", "원산지증명서", "위생증명서"
        ],
        "labeling_info": {
            "has_nutrition_label": True,
            "has_allergy_info": True,
            "has_expiry_date": True,
            "has_ingredients": True,
            "has_storage_info": True,
            "has_manufacturer_info": True
        }
    }
    
    # 테스트 데이터 2: 부족한 데이터
    poor_data = {
        "company_info": {
            "company_name": "한국식품",
            "address": "",
            "phone": "",
            "email": "",
            "representative": ""
        },
        "product_info": {
            "product_name": "라면",
            "manufacturer": "",
            "origin": "",
            "expiry_date": "",
            "nutrition": {
                "열량": "",
                "단백질": "",
                "지방": "",
                "탄수화물": "",
                "나트륨": "",
                "당류": ""
            },
            "ingredients": [],
            "allergy_ingredients": [],
            "storage_method": ""
        },
        "prepared_documents": [],
        "labeling_info": {
            "has_nutrition_label": False,
            "has_allergy_info": False,
            "has_expiry_date": False,
            "has_ingredients": False,
            "has_storage_info": False,
            "has_manufacturer_info": False
        }
    }
    
    # 점수 계산 함수 (간단한 버전)
    def calculate_compliance_score(data):
        score = 0
        max_score = 0
        
        # 1. 회사 정보 (15점)
        company_fields = ["company_name", "address", "phone", "email", "representative"]
        for field in company_fields:
            max_score += 3
            if field in data["company_info"] and data["company_info"][field] and len(str(data["company_info"][field]).strip()) > 0:
                score += 3
        
        # 2. 제품 정보 (20점)
        product_fields = ["product_name", "manufacturer", "origin", "expiry_date"]
        for field in product_fields:
            max_score += 5
            if field in data["product_info"] and data["product_info"][field] and len(str(data["product_info"][field]).strip()) > 0:
                score += 5
        
        # 3. 영양성분 (10점)
        nutrition = data["product_info"].get("nutrition", {})
        nutrition_fields = ["열량", "단백질", "지방", "탄수화물", "나트륨", "당류"]
        for field in nutrition_fields:
            max_score += 1.67
            if field in nutrition and nutrition[field] and len(str(nutrition[field]).strip()) > 0:
                score += 1.67
        
        # 4. 서류 준비 (30점)
        max_score += 30
        docs_ratio = len(data["prepared_documents"]) / 4 if data["prepared_documents"] else 0
        score += docs_ratio * 30
        
        # 5. 라벨링 (25점)
        labeling = data["labeling_info"]
        labeling_items = list(labeling.values())
        max_score += 25
        score += (sum(labeling_items) / len(labeling_items)) * 25
        
        # 최종 점수 계산
        if max_score > 0:
            final_score = (score / max_score) * 100
        else:
            final_score = 0
        
        return final_score
    
    # 테스트 실행
    print("\n📊 테스트 케이스 1: 완벽한 데이터")
    score1 = calculate_compliance_score(perfect_data)
    print(f"   점수: {score1:.1f}%")
    
    print("\n📊 테스트 케이스 2: 부족한 데이터")
    score2 = calculate_compliance_score(poor_data)
    print(f"   점수: {score2:.1f}%")
    
    # 결과 비교
    print("\n" + "=" * 50)
    print("📈 결과 비교:")
    print(f"   완벽한 데이터: {score1:.1f}%")
    print(f"   부족한 데이터: {score2:.1f}%")
    print(f"   점수 차이: {abs(score1 - score2):.1f}점")
    
    if abs(score1 - score2) > 20:
        print("\n✅ 성공: 입력값에 따라 점수가 달라집니다!")
        print("   - 데이터 품질에 따라 점수가 차등 적용됨")
        print("   - 사용자 입력에 맞게 점수가 측정됨")
    else:
        print("\n❌ 문제: 점수 차이가 너무 작습니다.")
        print("   - 점수 계산 로직을 개선해야 함")
    
    return score1, score2

if __name__ == "__main__":
    test_basic_compliance() 