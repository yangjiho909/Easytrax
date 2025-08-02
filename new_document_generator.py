#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
완전히 새로운 DocumentGenerator
문자열 오류를 완전히 해결한 버전
"""

import os
from datetime import datetime

class NewDocumentGenerator:
    def __init__(self):
        print("✅ 새로운 DocumentGenerator 초기화 완료")
        
    def generate_document(self, doc_type, country, product, company_info, **kwargs):
        """문서 생성 메인 함수"""
        try:
            if doc_type == "상업송장":
                return self._generate_commercial_invoice(country, product, company_info, **kwargs)
            elif doc_type == "포장명세서":
                return self._generate_packing_list(country, product, company_info, **kwargs)
            else:
                return "지원하지 않는 문서 유형: " + str(doc_type)
        except Exception as e:
            print("❌ 문서 생성 오류: " + str(e))
            return "문서 생성 중 오류가 발생했습니다: " + str(e)
    
    def _generate_commercial_invoice(self, country, product, company_info, **kwargs):
        """상업송장 생성"""
        try:
            # 데이터 추출 - Postman 데이터와 일치하도록 수정
            product_info = kwargs.get('product_info', {})
            buyer_info = kwargs.get('buyer_info', {})
            transport_info = kwargs.get('transport_info', {})
            payment_info = kwargs.get('payment_info', {})
            
            # 안전한 문자열 변환
            def safe_str(value):
                if value is None:
                    return 'N/A'
                try:
                    return str(value)
                except:
                    return 'N/A'
            
            # 총액 계산 - 문자열을 숫자로 변환
            quantity_str = product_info.get('quantity', '0')
            unit_price_str = product_info.get('unit_price', '0')
            
            # 숫자 추출 (문자열에서 숫자만 추출)
            import re
            quantity_match = re.search(r'(\d+(?:\.\d+)?)', str(quantity_str))
            unit_price_match = re.search(r'(\d+(?:\.\d+)?)', str(unit_price_str))
            
            quantity = float(quantity_match.group(1)) if quantity_match else 0
            unit_price = float(unit_price_match.group(1)) if unit_price_match else 0
            total_amount = quantity * unit_price
            
            # 문자열 연결 방식으로 문서 생성
            lines = []
            lines.append("=== 상업송장 (Commercial Invoice) ===")
            lines.append("")
            lines.append("📋 기본 정보")
            lines.append("- 국가: " + safe_str(country))
            lines.append("- 제품명: " + safe_str(product))
            lines.append("- 발행일: " + datetime.now().strftime('%Y-%m-%d'))
            lines.append("")
            lines.append("🏢 판매자 정보")
            lines.append("- 회사명: " + safe_str(company_info.get('name')))
            lines.append("- 주소: " + safe_str(company_info.get('address')))
            lines.append("- 연락처: " + safe_str(company_info.get('phone')))
            lines.append("- 이메일: " + safe_str(company_info.get('email')))
            lines.append("")
            lines.append("👤 구매자 정보")
            lines.append("- 회사명: " + safe_str(buyer_info.get('name')))
            lines.append("- 주소: " + safe_str(buyer_info.get('address')))
            lines.append("- 연락처: " + safe_str(buyer_info.get('phone')))
            lines.append("")
            lines.append("📦 제품 정보")
            lines.append("- 제품명: " + safe_str(product_info.get('name', product)))
            lines.append("- 수량: " + safe_str(product_info.get('quantity')))
            lines.append("- 단가: " + safe_str(product_info.get('unit_price')))
            lines.append("- 총액: " + safe_str(total_amount))
            lines.append("")
            lines.append("🚢 운송 정보")
            lines.append("- 운송방법: " + safe_str(transport_info.get('method', transport_info.get('mode'))))
            lines.append("- 출발지: " + safe_str(transport_info.get('origin', transport_info.get('port_of_departure'))))
            lines.append("- 도착지: " + safe_str(transport_info.get('destination', transport_info.get('port_of_arrival'))))
            lines.append("")
            lines.append("💳 결제 정보")
            lines.append("- 결제방법: " + safe_str(payment_info.get('method')))
            lines.append("- 통화: " + safe_str(payment_info.get('currency', 'USD')))
            lines.append("")
            lines.append("---")
            lines.append("KATI 수출 지원 시스템에서 생성된 상업송장입니다.")
            
            return "\n".join(lines)
            
        except Exception as e:
            print("❌ 상업송장 생성 오류: " + str(e))
            return "상업송장 생성 중 오류가 발생했습니다: " + str(e)
    
    def _generate_packing_list(self, country, product, company_info, **kwargs):
        """포장명세서 생성"""
        try:
            # 데이터 추출 - Postman 데이터와 일치하도록 수정
            product_info = kwargs.get('product_info', {})
            packing_details = kwargs.get('packing_details', {})
            
            # 안전한 문자열 변환
            def safe_str(value):
                if value is None:
                    return 'N/A'
                try:
                    return str(value)
                except:
                    return 'N/A'
            
            # 문자열 연결 방식으로 문서 생성
            lines = []
            lines.append("=== 포장명세서 (Packing List) ===")
            lines.append("")
            lines.append("📋 기본 정보")
            lines.append("- 국가: " + safe_str(country))
            lines.append("- 제품명: " + safe_str(product))
            lines.append("- 발행일: " + datetime.now().strftime('%Y-%m-%d'))
            lines.append("")
            lines.append("🏢 발송자 정보")
            lines.append("- 회사명: " + safe_str(company_info.get('name')))
            lines.append("- 주소: " + safe_str(company_info.get('address')))
            lines.append("- 연락처: " + safe_str(company_info.get('phone')))
            lines.append("")
            lines.append("📦 포장 정보")
            lines.append("- 포장 방법: " + safe_str(packing_details.get('method', packing_details.get('details'))))
            lines.append("- 포장 재질: " + safe_str(packing_details.get('material', 'Carton')))
            lines.append("- 포장 크기: " + safe_str(packing_details.get('size', 'Standard')))
            lines.append("- 포장 무게: " + safe_str(packing_details.get('weight', packing_details.get('total_weight'))))
            lines.append("")
            lines.append("📋 상세 명세")
            lines.append("- 제품명: " + safe_str(product_info.get('name', product)))
            lines.append("- 수량: " + safe_str(product_info.get('quantity')))
            lines.append("- 단위: " + safe_str(product_info.get('unit', '개')))
            lines.append("- 총 포장 수: " + safe_str(packing_details.get('total_packages')))
            lines.append("")
            lines.append("📝 특이사항")
            lines.append("- 취급 주의: " + safe_str(packing_details.get('handling_notes', packing_details.get('marks'))))
            lines.append("- 보관 조건: " + safe_str(packing_details.get('storage_conditions', packing_details.get('labels'))))
            lines.append("")
            lines.append("---")
            lines.append("KATI 수출 지원 시스템에서 생성된 포장명세서입니다.")
            
            return "\n".join(lines)
            
        except Exception as e:
            print("❌ 포장명세서 생성 오류: " + str(e))
            return "포장명세서 생성 중 오류가 발생했습니다: " + str(e)
    
    def generate_all_documents(self, country, product, company_info, **kwargs):
        """모든 문서 생성"""
        return {
            "상업송장": self._generate_commercial_invoice(country, product, company_info, **kwargs),
            "포장명세서": self._generate_packing_list(country, product, company_info, **kwargs)
        } 