#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
준수성 분석 점수 계산 테스트
입력값에 따라 점수가 달라지는지 확인
"""

from mvp_integrated_system import MVPSystem

def test_compliance_scores():
    """준수성 분석 점수 테스트"""
    print("🔍 준수성 분석 점수 계산 테스트")
    print("=" * 60)
    
    system = MVPSystem()
    
    # 테스트 케이스 1: 완벽한 데이터
    print("\n📊 테스트 케이스 1: 완벽한 데이터")
    test_case_1 = {
        "country": "중국",
        "product": "라면",
        "company_info": {
            "company_name": "한국식품(주)",
            "address": "서울특별시 강남구 테헤란로 123",
            "phone": "02-1234-5678",
            "email": "export@koreafood.com",
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
            "ingredients": ["면류(밀가루, 소금)", "분말스프", "건조야채", "조미료", "향신료"],
            "allergy_ingredients": ["밀", "대두"],
            "storage_method": "직사광선을 피해 서늘한 곳에 보관"
        },
        "prepared_documents": [
            "상업송장 (Commercial Invoice)",
            "포장명세서 (Packing List)",
            "원산지증명서 (Certificate of Origin)",
            "위생증명서 (Health Certificate)",
            "중국 라벨링 승인서 (중국용)"
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
    
    # 테스트 케이스 2: 부족한 데이터
    print("\n📊 테스트 케이스 2: 부족한 데이터")
    test_case_2 = {
        "country": "중국",
        "product": "라면",
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
    
    # 테스트 케이스 3: 중간 품질 데이터
    print("\n📊 테스트 케이스 3: 중간 품질 데이터")
    test_case_3 = {
        "country": "중국",
        "product": "라면",
        "company_info": {
            "company_name": "한국식품(주)",
            "address": "서울시",
            "phone": "02-1234-5678",
            "email": "test@company.com",
            "representative": "김대표"
        },
        "product_info": {
            "product_name": "한국 라면",
            "manufacturer": "한국식품(주)",
            "origin": "한국",
            "expiry_date": "2025-12-31",
            "nutrition": {
                "열량": "400kcal",
                "단백질": "12g",
                "지방": "15g",
                "탄수화물": "60g",
                "나트륨": "1200mg",  # 높은 나트륨
                "당류": "5g"
            },
            "ingredients": ["면", "스프", "야채"],
            "allergy_ingredients": ["밀"],
            "storage_method": "서늘한 곳"
        },
        "prepared_documents": [
            "상업송장 (Commercial Invoice)",
            "포장명세서 (Packing List)"
        ],
        "labeling_info": {
            "has_nutrition_label": True,
            "has_allergy_info": True,
            "has_expiry_date": True,
            "has_ingredients": False,
            "has_storage_info": True,
            "has_manufacturer_info": False
        }
    }
    
    # 테스트 실행
    test_cases = [
        ("완벽한 데이터", test_case_1),
        ("부족한 데이터", test_case_2),
        ("중간 품질 데이터", test_case_3)
    ]
    
    results = []
    
    for case_name, test_case in test_cases:
        print(f"\n🔍 {case_name} 분석 중...")
        
        try:
            analysis = system._analyze_compliance(
                test_case["country"],
                test_case["product"],
                test_case["company_info"],
                test_case["product_info"],
                test_case["prepared_documents"],
                test_case["labeling_info"]
            )
            
            results.append({
                "case": case_name,
                "score": analysis["overall_score"],
                "status": analysis["compliance_status"],
                "details": analysis.get("score_details", {})
            })
            
            print(f"   점수: {analysis['overall_score']:.1f}%")
            print(f"   상태: {analysis['compliance_status']}")
            
            if "score_details" in analysis:
                print("   세부 점수:")
                for category, score in analysis["score_details"].items():
                    print(f"     {category}: {score}")
            
        except Exception as e:
            print(f"   ❌ 오류 발생: {e}")
            results.append({
                "case": case_name,
                "score": 0,
                "status": "오류",
                "details": {}
            })
    
    # 결과 비교
    print("\n" + "=" * 60)
    print("📊 테스트 결과 비교")
    print("=" * 60)
    
    for result in results:
        print(f"{result['case']}: {result['score']:.1f}% ({result['status']})")
    
    # 점수 차이 확인
    if len(results) >= 2:
        score_diff_1_2 = abs(results[0]['score'] - results[1]['score'])
        score_diff_1_3 = abs(results[0]['score'] - results[2]['score'])
        score_diff_2_3 = abs(results[1]['score'] - results[2]['score'])
        
        print(f"\n📈 점수 차이:")
        print(f"   완벽한 데이터 vs 부족한 데이터: {score_diff_1_2:.1f}점")
        print(f"   완벽한 데이터 vs 중간 품질 데이터: {score_diff_1_3:.1f}점")
        print(f"   부족한 데이터 vs 중간 품질 데이터: {score_diff_2_3:.1f}점")
        
        if score_diff_1_2 > 10 and score_diff_1_3 > 10:
            print("\n✅ 성공: 입력값에 따라 점수가 달라집니다!")
        else:
            print("\n❌ 문제: 점수 차이가 너무 작습니다.")
    
    return results

if __name__ == "__main__":
    test_compliance_scores() 