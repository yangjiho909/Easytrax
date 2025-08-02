#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
체크박스 체크 여부에 따른 준수성 분석 테스트
"""

from mvp_integrated_system import MVPSystem

def test_checkbox_compliance():
    """체크박스 체크 여부에 따른 준수성 분석 테스트"""
    print("🔍 체크박스 체크 여부에 따른 준수성 분석 테스트")
    print("=" * 60)
    
    system = MVPSystem()
    
    # 기본 테스트 데이터
    base_data = {
        "country": "중국",
        "product": "라면",
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
            "상업송장 (Commercial Invoice)",
            "포장명세서 (Packing List)",
            "원산지증명서 (Certificate of Origin)",
            "위생증명서 (Health Certificate)"
        ]
    }
    
    # 테스트 케이스 1: 모든 라벨링 항목 체크
    print("\n📊 테스트 케이스 1: 모든 라벨링 항목 체크")
    all_checked_labeling = {
        "has_nutrition_label": True,
        "has_allergy_info": True,
        "has_expiry_date": True,
        "has_ingredients": True,
        "has_storage_info": True,
        "has_manufacturer_info": True
    }
    
    # 테스트 케이스 2: 일부 라벨링 항목만 체크
    print("\n📊 테스트 케이스 2: 일부 라벨링 항목만 체크")
    partial_checked_labeling = {
        "has_nutrition_label": True,
        "has_allergy_info": False,
        "has_expiry_date": True,
        "has_ingredients": False,
        "has_storage_info": True,
        "has_manufacturer_info": False
    }
    
    # 테스트 케이스 3: 모든 라벨링 항목 미체크
    print("\n📊 테스트 케이스 3: 모든 라벨링 항목 미체크")
    none_checked_labeling = {
        "has_nutrition_label": False,
        "has_allergy_info": False,
        "has_expiry_date": False,
        "has_ingredients": False,
        "has_storage_info": False,
        "has_manufacturer_info": False
    }
    
    # 테스트 실행
    test_cases = [
        ("모든 항목 체크", all_checked_labeling),
        ("일부 항목 체크", partial_checked_labeling),
        ("모든 항목 미체크", none_checked_labeling)
    ]
    
    results = []
    
    for case_name, labeling_info in test_cases:
        print(f"\n🔍 {case_name} 분석 중...")
        
        try:
            analysis = system._analyze_compliance(
                base_data["country"],
                base_data["product"],
                base_data["company_info"],
                base_data["product_info"],
                base_data["prepared_documents"],
                labeling_info
            )
            
            results.append({
                "case": case_name,
                "score": analysis["overall_score"],
                "status": analysis["compliance_status"],
                "critical_issues": len(analysis["critical_issues"]),
                "minor_issues": len(analysis["minor_issues"]),
                "critical_issues_list": analysis["critical_issues"],
                "minor_issues_list": analysis["minor_issues"]
            })
            
            print(f"   점수: {analysis['overall_score']:.1f}%")
            print(f"   상태: {analysis['compliance_status']}")
            print(f"   긴급 이슈: {len(analysis['critical_issues'])}개")
            print(f"   권장 이슈: {len(analysis['minor_issues'])}개")
            
            if analysis['critical_issues']:
                print("   긴급 이슈 목록:")
                for issue in analysis['critical_issues']:
                    print(f"     - {issue}")
            
            if analysis['minor_issues']:
                print("   권장 이슈 목록:")
                for issue in analysis['minor_issues']:
                    print(f"     - {issue}")
            
        except Exception as e:
            print(f"   ❌ 오류 발생: {e}")
            results.append({
                "case": case_name,
                "score": 0,
                "status": "오류",
                "critical_issues": 0,
                "minor_issues": 0,
                "critical_issues_list": [],
                "minor_issues_list": []
            })
    
    # 결과 비교
    print("\n" + "=" * 60)
    print("📊 테스트 결과 비교")
    print("=" * 60)
    
    for result in results:
        print(f"{result['case']}: {result['score']:.1f}% ({result['status']}) - 긴급: {result['critical_issues']}개, 권장: {result['minor_issues']}개")
    
    # 체크박스 효과 확인
    print(f"\n📈 체크박스 효과 분석:")
    print(f"   모든 항목 체크 vs 모든 항목 미체크 점수 차이: {abs(results[0]['score'] - results[2]['score']):.1f}점")
    print(f"   모든 항목 체크 vs 일부 항목 체크 점수 차이: {abs(results[0]['score'] - results[1]['score']):.1f}점")
    
    # 체크박스가 제대로 작동하는지 확인
    if results[0]['critical_issues'] < results[2]['critical_issues']:
        print("\n✅ 성공: 체크박스 체크 여부에 따라 이슈 개수가 달라집니다!")
        print("   - 체크된 항목은 이슈에서 제외됨")
        print("   - 체크되지 않은 항목만 이슈로 표시됨")
    else:
        print("\n❌ 문제: 체크박스 체크 여부가 결과에 반영되지 않습니다.")
    
    return results

if __name__ == "__main__":
    test_checkbox_compliance() 