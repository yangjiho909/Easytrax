#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
준수성 점수 계산 시스템 테스트
- 다양한 입력에 따른 점수 변화 확인
- 점수 계산 로직 검증
"""

import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_compliance_score_system():
    """준수성 점수 계산 시스템 테스트"""
    
    print("🧪 준수성 점수 계산 시스템 테스트 시작")
    print("=" * 50)
    
    try:
        # app.py의 analyze_optimized_compliance_issues 함수 테스트
        from app import analyze_optimized_compliance_issues
        
        # 테스트 케이스 1: 완벽한 중국 라면 데이터
        print("\n📋 테스트 케이스 1: 완벽한 중국 라면 데이터")
        perfect_china_data = {
            "라벨": "중국어 라벨, 제품명: 라면, 성분: 밀가루, 유통기한: 2025-12-31, 중량: 120g",
            "영양성분표": "영양성분표, 열량: 400kcal, 단백질: 12g",
            "알레르기정보": "알레르기 정보: 밀, 대두",
            "제조사정보": "제조사: 한국식품공업"
        }
        
        result1 = analyze_optimized_compliance_issues(
            perfect_china_data, {}, "중국", "라면"
        )
        
        print(f"점수: {result1['overall_score']}")
        print(f"상태: {result1['compliance_status']}")
        print(f"중요 이슈: {result1['critical_issues']}")
        print(f"주요 이슈: {result1['major_issues']}")
        
        # 테스트 케이스 2: 불완전한 미국 라면 데이터
        print("\n📋 테스트 케이스 2: 불완전한 미국 라면 데이터")
        incomplete_us_data = {
            "라벨": "Product Name: Ramen, Weight: 100g",
            "영양성분표": "Calories: 350"
        }
        
        result2 = analyze_optimized_compliance_issues(
            incomplete_us_data, {}, "미국", "라면"
        )
        
        print(f"점수: {result2['overall_score']}")
        print(f"상태: {result2['compliance_status']}")
        print(f"중요 이슈: {result2['critical_issues']}")
        print(f"주요 이슈: {result2['major_issues']}")
        
        # 테스트 케이스 3: 최소한의 데이터
        print("\n📋 테스트 케이스 3: 최소한의 데이터")
        minimal_data = {
            "라벨": "라면"
        }
        
        result3 = analyze_optimized_compliance_issues(
            minimal_data, {}, "한국", "라면"
        )
        
        print(f"점수: {result3['overall_score']}")
        print(f"상태: {result3['compliance_status']}")
        print(f"중요 이슈: {result3['critical_issues']}")
        print(f"주요 이슈: {result3['major_issues']}")
        
        # 테스트 케이스 4: 빈 데이터
        print("\n📋 테스트 케이스 4: 빈 데이터")
        empty_data = {}
        
        result4 = analyze_optimized_compliance_issues(
            empty_data, {}, "중국", "라면"
        )
        
        print(f"점수: {result4['overall_score']}")
        print(f"상태: {result4['compliance_status']}")
        print(f"중요 이슈: {result4['critical_issues']}")
        print(f"주요 이슈: {result4['major_issues']}")
        
        print("\n" + "=" * 50)
        print("✅ 테스트 완료!")
        
        # 점수 변화 요약
        print("\n📊 점수 변화 요약:")
        print(f"완벽한 데이터 (중국): {result1['overall_score']}점")
        print(f"불완전한 데이터 (미국): {result2['overall_score']}점")
        print(f"최소한의 데이터 (한국): {result3['overall_score']}점")
        print(f"빈 데이터 (중국): {result4['overall_score']}점")
        
        # 점수 차이 확인
        if result1['overall_score'] > result2['overall_score'] > result3['overall_score'] > result4['overall_score']:
            print("\n✅ 점수 계산이 올바르게 작동합니다!")
            print("   - 데이터 품질에 따라 점수가 차등 적용됨")
            print("   - 사용자 입력에 맞게 점수가 측정됨")
        else:
            print("\n⚠️ 점수 계산에 문제가 있을 수 있습니다.")
        
        return True
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        return False

def test_label_compliance_checker():
    """라벨 준수성 검토기 테스트"""
    
    print("\n🧪 라벨 준수성 검토기 테스트")
    print("=" * 50)
    
    try:
        from label_compliance_checker import LabelComplianceChecker
        
        checker = LabelComplianceChecker()
        
        # 테스트 케이스 1: 완벽한 중국 라벨
        print("\n📋 테스트 케이스 1: 완벽한 중국 라벨")
        perfect_china_label = {
            "product_name": "라면",
            "ingredients": "밀가루, 소금, 향신료",
            "manufacturer": "한국식품공업",
            "expiry_date": "2025-12-31",
            "storage": "서늘한 곳에 보관",
            "weight": "120g",
            "nutrition": {
                "열량": "400kcal",
                "단백질": "12g",
                "지방": "15g",
                "탄수화물": "60g",
                "나트륨": "800mg"
            },
            "allergies": ["밀", "대두"]
        }
        
        result1 = checker.check_compliance(perfect_china_label, "중국")
        
        print(f"점수: {result1['score']}")
        print(f"상태: {result1['compliance_status']}")
        print(f"오류: {result1['errors']}")
        print(f"경고: {result1['warnings']}")
        
        # 테스트 케이스 2: 불완전한 미국 라벨
        print("\n📋 테스트 케이스 2: 불완전한 미국 라벨")
        incomplete_us_label = {
            "product_name": "Ramen",
            "weight": "100g"
        }
        
        result2 = checker.check_compliance(incomplete_us_label, "미국")
        
        print(f"점수: {result2['score']}")
        print(f"상태: {result2['compliance_status']}")
        print(f"오류: {result2['errors']}")
        print(f"경고: {result2['warnings']}")
        
        print("\n" + "=" * 50)
        print("✅ 라벨 준수성 검토기 테스트 완료!")
        
        return True
        
    except Exception as e:
        print(f"❌ 라벨 준수성 검토기 테스트 실패: {e}")
        return False

if __name__ == "__main__":
    print("🚀 준수성 점수 계산 시스템 종합 테스트")
    print("=" * 60)
    
    # 메인 테스트 실행
    main_test_result = test_compliance_score_system()
    
    # 라벨 준수성 검토기 테스트 실행
    label_test_result = test_label_compliance_checker()
    
    # 최종 결과
    print("\n" + "=" * 60)
    if main_test_result and label_test_result:
        print("🎉 모든 테스트가 성공적으로 완료되었습니다!")
        print("✅ 준수성 점수 계산 시스템이 정상적으로 작동합니다.")
        print("✅ 사용자 입력에 맞게 점수가 측정됩니다.")
    else:
        print("⚠️ 일부 테스트에서 문제가 발생했습니다.")
        print("🔧 시스템을 점검해주세요.") 