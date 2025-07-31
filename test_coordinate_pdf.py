#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
좌표 기반 PDF 생성기 직접 테스트
"""

from coordinate_based_pdf_generator import CoordinateBasedPDFGenerator

def test_coordinate_pdf():
    """좌표 기반 PDF 생성기 테스트"""
    
    print("🚀 좌표 기반 PDF 생성기 테스트 시작...")
    
    # 생성기 초기화
    generator = CoordinateBasedPDFGenerator()
    
    # 상업송장 테스트 데이터
    commercial_invoice_data = {
        "shipper_seller": "한국식품산업(주)",
        "invoice_no_date": "INV-20240115-001 / 2024-01-15",
        "lc_no_date": "LC2024001 / 2024-01-10",
        "buyer": "중국식품무역(주)",
        "other_references": "REF001",
        "departure_date": "2024-01-15",
        "vessel_flight": "EVER GIVEN 001W",
        "from_location": "부산항",
        "to_location": "상하이항",
        "terms_delivery_payment": "FOB 부산 / 신용장 90일",
        "shipping_marks": "KOREA FOOD",
        "package_count_type": "100 박스",
        "goods_description": "매운맛 라면",
        "quantity": "1000",
        "unit_price": "5.00",
        "amount": "5000.00",
        "signed_by": "김대표"
    }
    
    # 포장명세서 테스트 데이터
    packing_list_data = {
        "seller": "한국식품산업(주)",
        "consignee": "중국식품무역(주)",
        "notify_party": "중국식품무역(주)",
        "departure_date": "2024-01-15",
        "vessel_flight": "EVER GIVEN 001W",
        "from_location": "부산항",
        "to_location": "상하이항",
        "invoice_no_date": "INV-20240115-001 / 2024-01-15",
        "buyer": "중국식품무역(주)",
        "other_references": "REF001",
        "shipping_marks": "KOREA FOOD",
        "package_count_type": "100 박스",
        "goods_description": "매운맛 라면",
        "quantity_net_weight": "1000 / 8kg",
        "gross_weight": "10kg",
        "measurement": "30x20x15cm",
        "signed_by": "김대표"
    }
    
    try:
        # 상업송장 PDF 생성
        print("📄 상업송장 PDF 생성 중...")
        commercial_pdf_path = generator.generate_pdf_with_coordinates(
            "상업송장",
            commercial_invoice_data,
            coordinate_file="uploaded_templates/상품송장 좌표 반영.json"
        )
        print(f"✅ 상업송장 PDF 생성 완료: {commercial_pdf_path}")
        
        # 포장명세서 PDF 생성
        print("📄 포장명세서 PDF 생성 중...")
        packing_pdf_path = generator.generate_pdf_with_coordinates(
            "포장명세서",
            packing_list_data,
            coordinate_file="uploaded_templates/포장명세서 좌표 반영.json"
        )
        print(f"✅ 포장명세서 PDF 생성 완료: {packing_pdf_path}")
        
        print("🎉 모든 PDF 생성 완료!")
        
    except Exception as e:
        print(f"❌ PDF 생성 중 오류 발생: {str(e)}")
        import traceback
        print(f"📋 상세 오류: {traceback.format_exc()}")

if __name__ == "__main__":
    test_coordinate_pdf() 