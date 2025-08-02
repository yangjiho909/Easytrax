#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
간단한 체크박스 테스트
"""

def test_simple_checkbox():
    """간단한 체크박스 로직 테스트"""
    print("🔍 간단한 체크박스 테스트")
    print("=" * 40)
    
    # 테스트 데이터
    test_cases = [
        {
            "name": "모든 항목 체크",
            "labeling_info": {
                "has_nutrition_label": True,
                "has_allergy_info": True,
                "has_expiry_date": True,
                "has_ingredients": True,
                "has_storage_info": True,
                "has_manufacturer_info": True
            }
        },
        {
            "name": "일부 항목 체크",
            "labeling_info": {
                "has_nutrition_label": True,
                "has_allergy_info": False,
                "has_expiry_date": True,
                "has_ingredients": False,
                "has_storage_info": True,
                "has_manufacturer_info": False
            }
        },
        {
            "name": "모든 항목 미체크",
            "labeling_info": {
                "has_nutrition_label": False,
                "has_allergy_info": False,
                "has_expiry_date": False,
                "has_ingredients": False,
                "has_storage_info": False,
                "has_manufacturer_info": False
            }
        }
    ]
    
    # 중국 라벨링 요구사항
    labeling_requirements = {
        "has_nutrition_label": ("영양성분표", 5, "critical"),
        "has_allergy_info": ("8대 알레르기 정보", 5, "critical"),
        "has_expiry_date": ("유통기한", 5, "critical"),
        "has_ingredients": ("성분표", 5, "critical"),
        "has_storage_info": ("보관방법", 3, "minor"),
        "has_manufacturer_info": ("제조사 정보", 2, "critical")
    }
    
    results = []
    
    for test_case in test_cases:
        print(f"\n📊 {test_case['name']}")
        
        labeling_score = 0
        critical_issues = []
        minor_issues = []
        
        for field, (description, points, severity) in labeling_requirements.items():
            if test_case["labeling_info"][field]:
                labeling_score += points
                print(f"   ✅ {description}: +{points}점")
            else:
                if severity == "critical":
                    critical_issues.append(f"중국 규정: {description} 필수")
                    print(f"   ❌ {description}: 필수 누락")
                else:
                    minor_issues.append(f"중국 규정: {description} 권장")
                    print(f"   ⚠️ {description}: 권장 누락")
        
        results.append({
            "name": test_case["name"],
            "score": labeling_score,
            "critical_issues": len(critical_issues),
            "minor_issues": len(minor_issues),
            "total_issues": len(critical_issues) + len(minor_issues)
        })
        
        print(f"   📊 점수: {labeling_score}/25점")
        print(f"   🚨 긴급 이슈: {len(critical_issues)}개")
        print(f"   ⚠️ 권장 이슈: {len(minor_issues)}개")
    
    # 결과 비교
    print("\n" + "=" * 40)
    print("📈 결과 비교")
    print("=" * 40)
    
    for result in results:
        print(f"{result['name']}: {result['score']}점, 이슈 {result['total_issues']}개")
    
    # 체크박스 효과 확인
    all_checked_score = results[0]['score']
    none_checked_score = results[2]['score']
    score_diff = all_checked_score - none_checked_score
    
    print(f"\n📊 체크박스 효과:")
    print(f"   모든 항목 체크: {all_checked_score}점")
    print(f"   모든 항목 미체크: {none_checked_score}점")
    print(f"   점수 차이: {score_diff}점")
    
    if score_diff > 0:
        print("\n✅ 성공: 체크박스 체크 여부에 따라 점수가 달라집니다!")
    else:
        print("\n❌ 문제: 체크박스 체크 여부가 점수에 반영되지 않습니다.")
    
    return results

if __name__ == "__main__":
    test_simple_checkbox() 