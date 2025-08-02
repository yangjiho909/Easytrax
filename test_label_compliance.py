#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
라벨 준수성 검사기 테스트
개선된 점수 계산 로직 검증
"""

from label_compliance_checker import LabelComplianceChecker

def test_label_compliance_scores():
    """라벨 준수성 점수 테스트"""
    print("🔍 라벨 준수성 검사기 점수 계산 테스트")
    print("=" * 60)
    
    checker = LabelComplianceChecker()
    
    # 테스트 케이스 1: 완벽한 중국 라벨
    print("\n📊 테스트 케이스 1: 완벽한 중국 라벨")
    perfect_china_label = {
        "product_name": "한국 라면",
        "manufacturer": "한국식품(주)",
        "ingredients": "면류(밀가루, 소금), 분말스프, 건조야채, 조미료, 향신료",
        "expiry_date": "2025-12-31",
        "weight": "120g",
        "nutrition": {
            "열량": "400kcal",
            "단백질": "12g",
            "지방": "15g",
            "탄수화물": "60g",
            "나트륨": "800mg",
            "당류": "5g"
        },
        "allergies": ["밀", "대두"]
    }
    
    # 테스트 케이스 2: 부족한 중국 라벨
    print("\n📊 테스트 케이스 2: 부족한 중국 라벨")
    poor_china_label = {
        "product_name": "라면",
        "manufacturer": "",
        "ingredients": "",
        "expiry_date": "",
        "weight": "",
        "nutrition": {},
        "allergies": []
    }
    
    # 테스트 케이스 3: 중간 품질 중국 라벨
    print("\n📊 테스트 케이스 3: 중간 품질 중국 라벨")
    medium_china_label = {
        "product_name": "한국 라면",
        "manufacturer": "한국식품",
        "ingredients": "면, 스프",
        "expiry_date": "2025-12-31",
        "weight": "120g",
        "nutrition": {
            "열량": "400kcal",
            "단백질": "12g",
            "지방": "15g",
            "탄수화물": "60g",
            "나트륨": "1200mg",  # 높은 나트륨
            "당류": "5g"
        },
        "allergies": ["밀"]
    }
    
    # 테스트 실행
    test_cases = [
        ("완벽한 중국 라벨", perfect_china_label, "중국"),
        ("부족한 중국 라벨", poor_china_label, "중국"),
        ("중간 품질 중국 라벨", medium_china_label, "중국")
    ]
    
    results = []
    
    for case_name, label_info, country in test_cases:
        print(f"\n🔍 {case_name} 분석 중...")
        
        try:
            result = checker.check_compliance(label_info, country)
            
            results.append({
                "case": case_name,
                "score": result["score"],
                "status": result["compliance_status"],
                "errors": len(result["errors"]),
                "warnings": len(result["warnings"])
            })
            
            print(f"   점수: {result['score']:.1f}%")
            print(f"   상태: {result['compliance_status']}")
            print(f"   오류: {len(result['errors'])}개")
            print(f"   경고: {len(result['warnings'])}개")
            
            if result['errors']:
                print("   주요 오류:")
                for error in result['errors'][:3]:
                    print(f"     - {error}")
            
        except Exception as e:
            print(f"   ❌ 오류 발생: {e}")
            results.append({
                "case": case_name,
                "score": 0,
                "status": "오류",
                "errors": 0,
                "warnings": 0
            })
    
    # 결과 비교
    print("\n" + "=" * 60)
    print("📊 테스트 결과 비교")
    print("=" * 60)
    
    for result in results:
        print(f"{result['case']}: {result['score']:.1f}% ({result['status']}) - 오류: {result['errors']}개, 경고: {result['warnings']}개")
    
    # 점수 차이 확인
    if len(results) >= 2:
        score_diff_1_2 = abs(results[0]['score'] - results[1]['score'])
        score_diff_1_3 = abs(results[0]['score'] - results[2]['score'])
        score_diff_2_3 = abs(results[1]['score'] - results[2]['score'])
        
        print(f"\n📈 점수 차이:")
        print(f"   완벽한 라벨 vs 부족한 라벨: {score_diff_1_2:.1f}점")
        print(f"   완벽한 라벨 vs 중간 품질 라벨: {score_diff_1_3:.1f}점")
        print(f"   부족한 라벨 vs 중간 품질 라벨: {score_diff_2_3:.1f}점")
        
        if score_diff_1_2 > 20 and score_diff_1_3 > 10:
            print("\n✅ 성공: 입력값에 따라 점수가 달라집니다!")
            print("   - 라벨 품질에 따라 점수가 차등 적용됨")
            print("   - 개선된 점수 계산 로직이 정상 작동함")
        else:
            print("\n❌ 문제: 점수 차이가 너무 작습니다.")
            print("   - 점수 계산 로직을 더 개선해야 함")
    
    return results

if __name__ == "__main__":
    test_label_compliance_scores() 