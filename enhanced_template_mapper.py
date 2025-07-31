
def map_data_to_new_templates(doc_type, data):
    """새로운 템플릿에 데이터 매핑"""
    from datetime import datetime
    
    timestamp = datetime.now()
    invoice_number = f"INV-{timestamp.strftime('%Y%m%d%H%M%S')}"
    package_number = f"PKG-{timestamp.strftime('%Y%m%d%H%M%S')}"
    
    company_info = data.get('company_info', {})
    buyer_info = data.get('buyer_info', {})
    product_info = data.get('product_info', {})
    transport_info = data.get('transport_info', {})
    payment_info = data.get('payment_info', {})
    packing_details = data.get('packing_details', {})
    
    if doc_type == "상업송장":
        return {
            # 기본 정보
            "송장번호": invoice_number,
            "송장날짜": timestamp.strftime('%Y-%m-%d'),
            "계약번호": f"CON-{timestamp.strftime('%Y%m%d')}",
            "L/C번호": f"LC-{timestamp.strftime('%Y%m%d')}",
            
            # 판매자 정보
            "판매자": company_info.get('name', ''),
            "판매자주소": company_info.get('address', ''),
            "판매자전화": company_info.get('phone', ''),
            "판매자이메일": company_info.get('email', ''),
            "사업자등록번호": company_info.get('business_license', ''),
            
            # 구매자 정보
            "구매자": buyer_info.get('name', ''),
            "구매자주소": buyer_info.get('address', ''),
            "구매자전화": buyer_info.get('phone', ''),
            "구매자이메일": buyer_info.get('email', ''),
            
            # 제품 정보
            "품목": product_info.get('name', ''),
            "제품명": product_info.get('name', ''),
            "HS코드": product_info.get('code', ''),
            "수량": str(product_info.get('quantity', 0)),
            "단가": f"${product_info.get('unit_price', 0)}",
            "총액": f"${product_info.get('quantity', 0) * product_info.get('unit_price', 0)}",
            "원산지": product_info.get('origin', 'KOREA'),
            "단위": product_info.get('unit', '개'),
            
            # 운송 정보
            "출발항": transport_info.get('port_of_departure', 'BUSAN, KOREA'),
            "도착항": transport_info.get('port_of_arrival', ''),
            "운송방식": transport_info.get('mode', 'SEA'),
            "선박명": transport_info.get('vessel_name', ''),
            "항공편": transport_info.get('flight_number', '')
        }
    
    elif doc_type == "포장명세서":
        return {
            # 기본 정보
            "포장번호": package_number,
            "송장번호": invoice_number,
            "송장날짜": timestamp.strftime('%Y-%m-%d'),
            
            # 판매자/구매자 정보
            "판매자": company_info.get('name', ''),
            "구매자": buyer_info.get('name', ''),
            "판매자주소": company_info.get('address', ''),
            "구매자주소": buyer_info.get('address', ''),
            
            # 포장 정보
            "총 포장 수": str(packing_details.get('total_packages', 0)),
            "총 무게": f"{packing_details.get('total_weight', 0)} kg",
            "총 부피": f"{packing_details.get('total_volume', 0)} m³",
            "마크": packing_details.get('marks', ''),
            "라벨": packing_details.get('labels', ''),
            "포장상세": packing_details.get('details', '')
        }
    
    return {}
