#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os

# PyMuPDF 선택적 import
try:
    import fitz
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False
    print("⚠️ PyMuPDF (fitz) 모듈이 없습니다. PDF 생성 기능이 제한됩니다.")

class DocumentGenerator:
    """규제 정보 기반 자동 서류 생성 시스템"""
    
    def __init__(self):
        self.templates = self._load_templates()
        self.regulations = self._load_regulations()
    
    def _load_templates(self) -> Dict:
        """서류 템플릿 로딩"""
        return {
            # === 기본 필수 서류 (모든 국가 공통) ===
            "상업송장": {
                "filename": "상업송장_{country}_{product}_{date}.txt",
                "template": """상업송장 (Commercial Invoice)
=====================================

송장번호: {invoice_number}
발행일자: {issue_date}
유효기간: {expiry_date}

수출자 정보 (Shipper/Exporter):
- 회사명: {exporter_name}
- 주소: {exporter_address}
- 연락처: {exporter_contact}
- 사업자등록번호: {business_number}

수입자 정보 (Consignee):
- 회사명: {importer_name}
- 주소: {importer_address}
- 연락처: {importer_contact}

제품 정보:
- 제품명: {product_name}
- 원산지: 대한민국
- 수량: {quantity}
- 단가: {unit_price}
- 총액: {total_amount}

운송 정보:
- 선적항: {port_of_loading}
- 도착항: {final_destination}
- 운송조건: {incoterms}

결제 조건:
- 결제방법: {payment_terms}
- 통화: {currency}

발급기관: {issuing_authority}
담당자: {contact_person}
연락처: {contact_info}

※ 본 송장은 {country} 수입신고를 위한 공식 서류입니다.
"""
            },
            "포장명세서": {
                "filename": "포장명세서_{country}_{product}_{date}.txt",
                "template": """포장명세서 (Packing List)
=====================================

명세서번호: {packing_number}
발행일자: {issue_date}

수출자 정보:
- 회사명: {exporter_name}
- 주소: {exporter_address}
- 연락처: {exporter_contact}

수입자 정보:
- 회사명: {importer_name}
- 주소: {importer_address}

제품 정보:
- 제품명: {product_name}
- 원산지: 대한민국
- 수량: {quantity}

포장 정보:
- 순중량: {net_weight}
- 총중량: {gross_weight}
- 용적: {cbm}
- 포장 개수: {package_count}
- 포장 마크: {marks_numbers}

상세 포장 내역:
{packing_details}

발급기관: {issuing_authority}
담당자: {contact_person}
연락처: {contact_info}

※ 본 명세서는 {country} 통관검사를 위한 포장 내역서입니다.
"""
            },
            "원산지증명서": {
                "filename": "원산지증명서_{country}_{product}_{date}.txt",
                "template": """원산지증명서 (Certificate of Origin)
=====================================

증명서번호: {cert_number}
발급일자: {issue_date}
유효기간: {expiry_date}

수출자 정보:
- 회사명: {exporter_name}
- 주소: {exporter_address}
- 연락처: {exporter_contact}

수입자 정보:
- 회사명: {importer_name}
- 주소: {importer_address}

제품 정보:
- 제품명: {product_name}
- 원산지: 대한민국
- 제조사: {manufacturer}
- 수량: {quantity}

원산지 증명내용:
1. 원료의 원산지: 대한민국
2. 제조공정: 대한민국에서 완전히 제조
3. 품질관리: 대한민국 기준 적용
4. FTA 특혜관세 적용: {fta_applicable}

증명기준:
{origin_standards}

발급기관: {issuing_authority}
담당자: {contact_person}
연락처: {contact_info}

※ 본 증명서는 {country} 원산지표시기준에 따라 발급되었습니다.
"""
            },
            "선하증권": {
                "filename": "선하증권_{country}_{product}_{date}.txt",
                "template": """선하증권 (Bill of Lading)
=====================================

B/L 번호: {bl_number}
발행일자: {issue_date}

화주 정보 (Shipper):
- 회사명: {exporter_name}
- 주소: {exporter_address}
- 연락처: {exporter_contact}

수하인 정보 (Consignee):
- 회사명: {importer_name}
- 주소: {importer_address}
- 연락처: {importer_contact}

제품 정보:
- 제품명: {product_name}
- 원산지: 대한민국
- 수량: {quantity}
- 포장: {package_type}

운송 정보:
- 선적항: {port_of_loading}
- 도착항: {final_destination}
- 선박명: {vessel_name}
- 항해번호: {voyage_number}
- 컨테이너 번호: {container_number}

화물 정보:
- 순중량: {net_weight}
- 총중량: {gross_weight}
- 용적: {cbm}
- 포장 개수: {package_count}

운송조건: {incoterms}
운임지급: {freight_terms}

발급기관: {issuing_authority}
담당자: {contact_person}
연락처: {contact_info}

※ 본 선하증권은 화물수취증명서, 운송계약서, 소유권증서 역할을 합니다.
"""
            },
            "수출신고필증": {
                "filename": "수출신고필증_{country}_{product}_{date}.txt",
                "template": """수출신고필증
=====================================

신고번호: {declaration_number}
신고일자: {declaration_date}
승인일자: {approval_date}

수출자 정보:
- 회사명: {exporter_name}
- 사업자등록번호: {business_number}
- 주소: {exporter_address}
- 연락처: {exporter_contact}

제품 정보:
- 제품명: {product_name}
- 원산지: 대한민국
- 제조사: {manufacturer}
- 수입국: {country}
- 수량: {quantity}
- 가격: {price}

신고 내용:
{declaration_details}

필요서류:
{required_documents}

신고절차:
{declaration_procedures}

승인기관: {approval_authority}
담당자: {contact_person}
연락처: {contact_info}

※ 본 필증은 수출신고 후 세관에서 발급하는 증명서입니다.
"""
            },
            "위생증명서": {
                "filename": "위생증명서_{country}_{product}_{date}.txt",
                "template": """위생증명서 (Health Certificate)
=====================================

증명서번호: {cert_number}
발급일자: {issue_date}
유효기간: {expiry_date}

제품 정보:
- 제품명: {product_name}
- 원산지: 대한민국
- 제조사: {manufacturer}
- 수입국: {country}

위생 기준:
{health_standards}

증명 내용:
1. 제조·생산·가공·관리: 적합
2. 국내 자유판매: 가능
3. 기준 및 규격: 적합
4. 제조방법 및 원재료: 적합

검사 결과:
{inspection_results}

발급기관: {issuing_authority}
담당자: {contact_person}
연락처: {contact_info}

※ 본 증명서는 식품위생법에 따라 적합하게 제조·생산된 제품임을 증명합니다.
"""
            },
            # === 국가별 추가 서류 ===
            "FDA등록번호": {
                "filename": "FDA등록번호_{country}_{product}_{date}.txt",
                "template": """FDA 등록번호 (Food Facility Registration)
=====================================

등록번호: {fda_number}
등록일자: {registration_date}
갱신일자: {renewal_date}

회사 정보:
- 회사명: {exporter_name}
- 주소: {exporter_address}
- 대표자: {representative}
- 담당자: {contact_person}
- 연락처: {exporter_contact}

생산 품목:
- 제품명: {product_name}
- 제품 분류: {product_category}

미국 내 에이전트 정보:
- 에이전트명: {us_agent_name}
- 주소: {us_agent_address}
- 연락처: {us_agent_contact}

등록 정보:
- 등록 유형: 식품제조시설
- 등록 상태: 활성
- 갱신 필요일: {next_renewal_date}

발급기관: FDA (Food and Drug Administration)
담당자: {contact_person}
연락처: {contact_info}

※ 본 등록번호는 미국 내 통관을 위해 필수입니다. 2년마다 갱신이 필요합니다.
"""
            },
            "FSVP인증서": {
                "filename": "FSVP인증서_{country}_{product}_{date}.txt",
                "template": """FSVP 인증서 (Foreign Supplier Verification Program)
=====================================

인증번호: {fsvp_number}
인증일자: {certification_date}
유효기간: {expiry_date}

회사 정보:
- 회사명: {exporter_name}
- 주소: {exporter_address}
- 담당자: {contact_person}
- 연락처: {exporter_contact}

제품 정보:
- 제품명: {product_name}
- 제품 분류: {product_category}

인증 내용:
1. 해외공급업자 검증 프로그램 적합
2. 미국 식품안전현대화법(FSMA) 준수
3. 사전예방관리 시스템 구축
4. 위험분석 및 예방통제 적용

검증 항목:
{verification_items}

면제 대상 여부: {exemption_status}

발급기관: FDA (Food and Drug Administration)
담당자: {contact_person}
연락처: {contact_info}

※ 본 인증서는 미국 식품안전현대화법(FSMA)에 따른 사전예방관리를 위한 인증입니다.
"""
            },
            "중문라벨": {
                "filename": "중문라벨_{country}_{product}_{date}.txt",
                "template": """중문 라벨 (중국어 제품 라벨)
=====================================

라벨 번호: {label_number}
작성일자: {issue_date}

제품 정보 (중국어):
- 제품명: {product_name_chinese}
- 원산지: 韩国制造 (한국산)
- 제조사: {manufacturer_chinese}
- 유통기한: {expiry_date_chinese}

성분 정보 (중국어):
{ingredients_chinese}

영양성분표 (중국어):
{nutrition_chinese}

보관방법 (중국어):
{storage_chinese}

알레르기 정보 (중국어):
{allergy_chinese}

라벨 요구사항:
{label_requirements}

번역 확인:
- 번역자: {translator}
- 번역기관: {translation_agency}
- 확인일자: {verification_date}

발급기관: {issuing_authority}
담당자: {contact_person}
연락처: {contact_info}

※ 본 라벨은 중국 수입을 위한 중국어 제품 라벨입니다.
"""
            },
            "방사능검사증명서": {
                "filename": "방사능검사증명서_{country}_{product}_{date}.txt",
                "template": """방사능 검사증명서
=====================================

검사번호: {inspection_number}
검사일자: {inspection_date}
유효기간: {expiry_date}

제품 정보:
- 제품명: {product_name}
- 원산지: 대한민국
- 제조사: {manufacturer}
- 수입국: {country}

검사 항목:
1. 요오드(131I): {iodine_result}
2. 세슘(134Cs): {cesium134_result}
3. 세슘(137Cs): {cesium137_result}

검사 결과:
{inspection_results}

허용기준:
- 요오드(131I): 100 Bq/kg 이하
- 세슘(134Cs+137Cs): 100 Bq/kg 이하

검사기관: {inspection_authority}
검사자: {inspector}
연락처: {contact_info}

※ 본 증명서는 일본 수입을 위한 방사능 검사 결과입니다.
"""
            },
            "생산지증명서": {
                "filename": "생산지증명서_{country}_{product}_{date}.txt",
                "template": """생산지 증명서
=====================================

증명서번호: {cert_number}
발급일자: {issue_date}
유효기간: {expiry_date}

제품 정보:
- 제품명: {product_name}
- 원산지: 대한민국
- 제조사: {manufacturer}
- 수입국: {country}

생산지 정보:
- 생산지역: {production_area}
- 생산시설: {production_facility}
- 생산일자: {production_date}

증명 내용:
1. 후쿠시마 원전사고 영향 지역 아님
2. 방사능 오염 위험 지역 아님
3. 안전한 생산지역에서 생산
4. 일본 정부 기준 적합

지역 확인:
{area_verification}

발급기관: {issuing_authority}
담당자: {contact_person}
연락처: {contact_info}

※ 본 증명서는 후쿠시마 원전사고 관련하여 생산지역을 증명하는 서류입니다.
"""
            },
            "EU작업장등록": {
                "filename": "EU작업장등록_{country}_{product}_{date}.txt",
                "template": """EU 작업장 등록증
=====================================

등록번호: {registration_number}
등록일자: {registration_date}
유효기간: {expiry_date}

회사 정보:
- 회사명: {exporter_name}
- 주소: {exporter_address}
- 담당자: {contact_person}
- 연락처: {exporter_contact}

작업장 정보:
- 작업장명: {facility_name}
- 주소: {facility_address}
- 등록 유형: {facility_type}

제품 정보:
- 제품명: {product_name}
- 제품 분류: {product_category}

등록 내용:
1. EU 식품안전기준 준수
2. HACCP 시스템 구축
3. 위생관리 기준 적합
4. EU 작업장 등록 완료

신청 기관: 관할 지방청 농축수산물안전과
담당자: {contact_person}
연락처: {contact_info}

※ 본 등록증은 EU 수출을 위한 작업장 등록 증명서입니다.
"""
            },
            "EORI번호": {
                "filename": "EORI번호_{country}_{product}_{date}.txt",
                "template": """EORI 번호 (유럽연합위원회 세관등록번호)
=====================================

EORI 번호: {eori_number}
등록일자: {registration_date}
유효기간: {expiry_date}

회사 정보:
- 회사명: {exporter_name}
- 주소: {exporter_address}
- 담당자: {contact_person}
- 연락처: {exporter_contact}

등록 정보:
- 등록 유형: 경제운영자
- 등록 상태: 활성
- EU 회원국: {eu_member_state}

제품 정보:
- 제품명: {product_name}
- 제품 분류: {product_category}

등록 내용:
1. EU 세관 시스템 등록 완료
2. 경제운영자 자격 인정
3. EU 통관 절차 준수
4. 세관 신고 자격 확보

발급기관: EU 세관청
담당자: {contact_person}
연락처: {contact_info}

※ 본 번호는 EU 통관을 위한 필수 등록번호입니다.
"""
            },
            # === 기존 서류 (식품 특화) ===
            "식품안전인증서": {
                "filename": "식품안전인증서_{country}_{product}_{date}.txt",
                "template": """식품안전인증서
=====================================

발급일자: {issue_date}
인증번호: {cert_number}
유효기간: {expiry_date}

제품정보:
- 제품명: {product_name}
- 원산지: 대한민국
- 제조사: {manufacturer}
- 수입국: {country}

인증기준:
{standards}

인증내용:
{requirements}

발급기관: {issuing_authority}
담당자: {contact_person}
연락처: {contact_info}

※ 본 인증서는 {country} 식품안전기준에 따라 발급되었습니다.
"""
            },
            "원산지증명서": {
                "filename": "원산지증명서_{country}_{product}_{date}.txt",
                "template": """원산지증명서
=====================================

발급일자: {issue_date}
증명번호: {cert_number}

제품정보:
- 제품명: {product_name}
- 원산지: 대한민국
- 제조사: {manufacturer}
- 수입국: {country}

원산지 증명내용:
1. 원료의 원산지: 대한민국
2. 제조공정: 대한민국에서 완전히 제조
3. 품질관리: 대한민국 기준 적용

증명기준:
{origin_standards}

발급기관: {issuing_authority}
담당자: {contact_person}
연락처: {contact_info}

※ 본 증명서는 {country} 원산지표시기준에 따라 발급되었습니다.
"""
            },
            "성분분석서": {
                "filename": "성분분석서_{country}_{product}_{date}.txt",
                "template": """성분분석서
=====================================

분석일자: {analysis_date}
분석번호: {analysis_number}

제품정보:
- 제품명: {product_name}
- 원산지: 대한민국
- 제조사: {manufacturer}
- 수입국: {country}

분석결과:
{analysis_results}

허용기준:
{allowed_standards}

분석기관: {analysis_authority}
분석자: {analyst}
연락처: {contact_info}

※ 본 분석서는 {country} 식품성분기준에 따라 작성되었습니다.
"""
            },
            "라벨검토서": {
                "filename": "라벨검토서_{country}_{product}_{date}.txt",
                "template": """라벨검토서
=====================================

검토일자: {review_date}
검토번호: {review_number}

제품정보:
- 제품명: {product_name}
- 원산지: 대한민국
- 제조사: {manufacturer}
- 수입국: {country}

라벨요구사항:
{label_requirements}

검토결과:
{review_results}

주의사항:
{precautions}

검토기관: {review_authority}
검토자: {reviewer}
연락처: {contact_info}

※ 본 검토서는 {country} 라벨링기준에 따라 작성되었습니다.
"""
            },
            "수출신고서": {
                "filename": "수출신고서_{country}_{product}_{date}.txt",
                "template": """수출신고서
=====================================

신고일자: {declaration_date}
신고번호: {declaration_number}

수출자정보:
- 수출자명: {exporter_name}
- 사업자등록번호: {business_number}
- 주소: {exporter_address}
- 연락처: {exporter_contact}

제품정보:
- 제품명: {product_name}
- 원산지: 대한민국
- 제조사: {manufacturer}
- 수입국: {country}
- 수량: {quantity}
- 가격: {price}

필요서류:
{required_documents}

신고절차:
{declaration_procedures}

신고기관: {declaration_authority}
담당자: {contact_person}
연락처: {contact_info}

※ 본 신고서는 {country} 수입절차에 따라 작성되었습니다.
"""
            }
        }
    
    def _load_regulations(self) -> Dict:
        """규제 정보 로딩"""
        try:
            from detailed_regulations import DETAILED_REGULATIONS
            return DETAILED_REGULATIONS
        except ImportError:
            print("⚠️ 상세 규제정보를 찾을 수 없습니다.")
            return {}
    
    def fill_pdf_template(self, template_path, field_values, output_path):
        """PDF 템플릿의 텍스트 필드에 값 채워서 저장 (PyMuPDF 기반)"""
        if not FITZ_AVAILABLE:
            print("❌ PyMuPDF 모듈이 없어 PDF 템플릿 채우기가 불가능합니다.")
            return

        doc = fitz.open(template_path)
        for page in doc:
            for field, value in field_values.items():
                # 텍스트 치환 (간단 버전: 필드명으로 검색 후 value로 대체)
                areas = page.search_for(field)
                for rect in areas:
                    page.add_redact_annot(rect, fill=(1,1,1))
                    page.apply_redactions()
                    page.insert_text((rect.x0, rect.y0), str(value), fontsize=11, color=(0,0,0))
        doc.save(output_path)
        doc.close()

    def generate_document(self, doc_type, country, product, 
                         company_info, **kwargs) -> str:
        """특정 서류 생성"""
        
        # 서류 유형 매핑
        doc_mapping = {
            # 기본 필수 서류
            "상업송장": "상업송장",
            "포장명세서": "포장명세서", 
            "원산지증명서": "원산지증명서",
            "선하증권": "선하증권",
            "수출신고서": "수출신고서",
            "수출신고필증": "수출신고필증",
            "위생증명서": "위생증명서",
            
            # 국가별 특화 서류
            "중문라벨": "중문라벨",
            "제조공정도": "중문라벨",
            "검사신청서류": "위생증명서",
            "FDA등록번호": "FDA등록번호",
            "FSVP인증서": "FSVP인증서",
            "FCE/SID번호": "FDA등록번호",
            "방사능검사증명서": "방사능검사증명서",
            "생산지증명서": "생산지증명서",
            "EU작업장등록": "EU작업장등록",
            "EORI번호": "EORI번호",
            
            # 식품 특화 서류
            "식품안전인증서": "식품안전인증서",
            "성분분석서": "성분분석서",
            "라벨검토서": "라벨검토서",
            "영양성분분석서": "성분분석서"
        }
        
        # 매핑된 서류 유형 확인
        mapped_doc_type = doc_mapping.get(doc_type, doc_type)
        
        if mapped_doc_type not in self.templates:
            return f"❌ 지원하지 않는 서류 유형: {doc_type} (매핑: {mapped_doc_type})"
        
        # 매핑된 서류 유형으로 템플릿 가져오기
        template = self.templates[mapped_doc_type]
        
        # 기본 정보 설정
        current_date = datetime.now()
        issue_date = current_date.strftime("%Y-%m-%d")
        expiry_date = (current_date + timedelta(days=365)).strftime("%Y-%m-%d")
        
        # 규제 정보 가져오기
        regulations = self.regulations.get(country, {}).get(product, {})
        
        # 서류별 특화 정보 생성
        doc_data = {
            "issue_date": issue_date,
            "expiry_date": expiry_date,
            "analysis_date": issue_date,
            "review_date": issue_date,
            "declaration_date": issue_date,
            "cert_number": f"CERT-{country.upper()}-{product.upper()}-{current_date.strftime('%Y%m%d')}",
            "analysis_number": f"ANAL-{country.upper()}-{product.upper()}-{current_date.strftime('%Y%m%d')}",
            "review_number": f"REV-{country.upper()}-{product.upper()}-{current_date.strftime('%Y%m%d')}",
            "declaration_number": f"DEC-{country.upper()}-{product.upper()}-{current_date.strftime('%Y%m%d')}",
            "product_name": kwargs.get("product_name", product),
            "manufacturer": company_info.get("manufacturer", "한국 제조사"),
            "country": country,
            "issuing_authority": company_info.get("issuing_authority", "한국 식품의약품안전처"),
            "contact_person": company_info.get("contact_person", "담당자"),
            "contact_info": company_info.get("contact_info", "연락처"),
            "exporter_name": company_info.get("exporter_name", "수출자명"),
            "business_number": company_info.get("business_number", "사업자등록번호"),
            "exporter_address": company_info.get("exporter_address", "수출자주소"),
            "exporter_contact": company_info.get("exporter_contact", "수출자연락처"),
            "quantity": kwargs.get("quantity", "수량"),
            "price": kwargs.get("price", "가격"),
            "analyst": company_info.get("analyst", "분석자"),
            "reviewer": company_info.get("reviewer", "검토자"),
            "analysis_authority": company_info.get("analysis_authority", "분석기관"),
            "review_authority": company_info.get("review_authority", "검토기관"),
            "declaration_authority": company_info.get("declaration_authority", "신고기관")
        }
        
        # 서류별 특화 내용 생성 (매핑된 서류 유형 사용)
        if mapped_doc_type == "상업송장":
            doc_data.update(self._generate_invoice_data(company_info, kwargs))
        elif mapped_doc_type == "포장명세서":
            doc_data.update(self._generate_packing_data(company_info, kwargs))
        elif mapped_doc_type == "원산지증명서":
            doc_data.update({
                "origin_standards": self._format_list(regulations.get("허용기준", [])),
                "fta_applicable": "적용 가능" if country in ["미국", "EU", "중국"] else "해당 없음"
            })
        elif mapped_doc_type == "선하증권":
            doc_data.update(self._generate_bill_of_lading_data(company_info, kwargs))
        elif mapped_doc_type == "수출신고필증":
            doc_data.update({
                "declaration_details": self._generate_declaration_details(regulations),
                "required_documents": self._format_list(regulations.get("필요서류", [])),
                "declaration_procedures": self._format_list(regulations.get("통관절차", [])),
                "approval_authority": "관세청",
                "approval_date": issue_date
            })
        elif mapped_doc_type == "위생증명서":
            doc_data.update({
                "health_standards": self._format_list(regulations.get("허용기준", [])),
                "inspection_results": self._generate_health_inspection_results(regulations)
            })
        elif mapped_doc_type == "FDA등록번호":
            doc_data.update(self._generate_fda_data(company_info, kwargs))
        elif mapped_doc_type == "FSVP인증서":
            doc_data.update(self._generate_fsvp_data(company_info, kwargs))
        elif mapped_doc_type == "중문라벨":
            doc_data.update(self._generate_chinese_label_data(company_info, kwargs))
        elif mapped_doc_type == "방사능검사증명서":
            doc_data.update(self._generate_radiation_data(company_info, kwargs))
        elif mapped_doc_type == "생산지증명서":
            doc_data.update(self._generate_production_area_data(company_info, kwargs))
        elif mapped_doc_type == "EU작업장등록":
            doc_data.update(self._generate_eu_facility_data(company_info, kwargs))
        elif mapped_doc_type == "EORI번호":
            doc_data.update(self._generate_eori_data(company_info, kwargs))
        elif mapped_doc_type == "식품안전인증서":
            doc_data.update({
                "standards": self._format_list(regulations.get("허용기준", [])),
                "requirements": self._format_list(regulations.get("제한사항", []))
            })
        elif mapped_doc_type == "성분분석서":
            doc_data.update({
                "analysis_results": self._generate_analysis_results(regulations),
                "allowed_standards": self._format_list(regulations.get("허용기준", []))
            })
        elif mapped_doc_type == "라벨검토서":
            doc_data.update({
                "label_requirements": self._format_list(regulations.get("제한사항", [])),
                "review_results": self._generate_label_review_results(regulations),
                "precautions": self._format_list(regulations.get("주의사항", []))
            })
        elif mapped_doc_type == "수출신고서":
            doc_data.update({
                "required_documents": self._format_list(regulations.get("필요서류", [])),
                "declaration_procedures": self._format_list(regulations.get("통관절차", []))
            })
        
        # 템플릿 적용
        content = template["template"].format(**doc_data)
        
        return content
    
    def _format_list(self, items: List[str]) -> str:
        """리스트를 포맷된 문자열로 변환"""
        if not items:
            return "해당 정보 없음"
        
        formatted = ""
        for i, item in enumerate(items, 1):
            formatted += f"{i}. {item}\n"
        return formatted.strip()
    
    def _generate_analysis_results(self, regulations: Dict) -> str:
        """성분분석 결과 생성"""
        results = []
        
        # 허용기준에서 분석 항목 추출
        standards = regulations.get("허용기준", [])
        for standard in standards:
            if "방부제" in standard or "첨가물" in standard:
                results.append(f"방부제 함량: 0.05% (허용기준: 0.1% 이하) - 적합")
            elif "미생물" in standard:
                results.append(f"총균수: 5,000 CFU/g (허용기준: 10,000 CFU/g 이하) - 적합")
            elif "알레르기" in standard:
                results.append(f"알레르기 원료: 함유 없음 - 적합")
        
        if not results:
            results = [
                "일반성분: 정상",
                "식품첨가물: 허용기준 이하",
                "미생물검사: 적합"
            ]
        
        return self._format_list(results)
    
    def _generate_label_review_results(self, regulations: Dict) -> str:
        """라벨검토 결과 생성"""
        results = []
        
        # 제한사항에서 라벨 요구사항 추출
        restrictions = regulations.get("제한사항", [])
        for restriction in restrictions:
            if "라벨" in restriction or "표기" in restriction:
                if "중국어" in restriction:
                    results.append("중국어 라벨: 적합")
                elif "영어" in restriction:
                    results.append("영어 라벨: 적합")
                elif "원산지" in restriction:
                    results.append("원산지 표기: 적합")
                elif "알레르기" in restriction:
                    results.append("알레르기 정보: 적합")
        
        if not results:
            results = [
                "제품명 표기: 적합",
                "성분표: 적합",
                "원산지 표기: 적합",
                "유통기한: 적합"
            ]
        
        return self._format_list(results)
    
    def _generate_invoice_data(self, company_info: Dict, kwargs: Dict) -> Dict:
        """상업송장 데이터 생성"""
        # 구매자 정보 처리
        buyer_info = kwargs.get('buyer_info', {})
        
        # 총액 계산
        quantity = kwargs.get('quantity', 1000)
        unit_price = kwargs.get('unit_price', 10.0)
        total_amount = quantity * unit_price
        
        return {
            "invoice_number": f"INV-{datetime.now().strftime('%Y%m%d')}-{kwargs.get('quantity', '001')}",
            "importer_name": buyer_info.get("name", kwargs.get("importer_name", "수입자명")),
            "importer_address": buyer_info.get("address", kwargs.get("importer_address", "수입자주소")),
            "importer_contact": buyer_info.get("contact", kwargs.get("importer_contact", "수입자연락처")),
            "quantity": f"{kwargs.get('quantity', 1000):,}{kwargs.get('unit', '개')}",
            "unit_price": f"{kwargs.get('unit_price', 10.0):.2f}",
            "total_amount": f"{total_amount:,.2f}",
            "port_of_loading": kwargs.get("port_of_loading", "부산항"),
            "final_destination": kwargs.get("port_of_arrival", kwargs.get("final_destination", "도착항")),
            "incoterms": kwargs.get("incoterms", "FOB"),
            "payment_terms": kwargs.get("payment_terms", "L/C"),
            "currency": kwargs.get("currency", "USD")
        }
    
    def _generate_packing_data(self, company_info: Dict, kwargs: Dict) -> Dict:
        """포장명세서 데이터 생성"""
        # 구매자 정보 처리
        buyer_info = kwargs.get('buyer_info', {})
        
        # 상세 포장 내역 생성
        packing_details = []
        if kwargs.get('packing_unit'):
            packing_details.append(f"포장단위: {kwargs.get('packing_unit')}")
        if kwargs.get('box_size'):
            packing_details.append(f"박스크기: {kwargs.get('box_size')}cm")
        if kwargs.get('box_weight'):
            packing_details.append(f"박스중량: {kwargs.get('box_weight')}kg")
        if kwargs.get('total_boxes'):
            packing_details.append(f"총박스수: {kwargs.get('total_boxes')}박스")
        
        # 기본값 설정
        if not packing_details:
            packing_details = [
                "포장단위: 20개/박스",
                "박스크기: 40cm x 30cm x 20cm",
                "박스중량: 11kg",
                "총박스수: 50박스"
            ]
        
        return {
            "packing_number": f"PKG-{datetime.now().strftime('%Y%m%d')}-{kwargs.get('quantity', '001')}",
            "importer_name": buyer_info.get("name", kwargs.get("importer_name", "수입자명")),
            "importer_address": buyer_info.get("address", kwargs.get("importer_address", "수입자주소")),
            "quantity": f"{kwargs.get('quantity', 1000):,}{kwargs.get('unit', '개')}",
            "net_weight": f"{kwargs.get('net_weight', 500):.1f}kg",
            "gross_weight": f"{kwargs.get('gross_weight', 550):.1f}kg",
            "cbm": f"{kwargs.get('volume', 2.5):.1f} CBM",
            "package_count": f"{kwargs.get('package_count', 50)}박스",
            "marks_numbers": kwargs.get("package_marks", "MADE IN KOREA"),
            "packing_details": self._format_list(packing_details)
        }
    
    def _generate_bill_of_lading_data(self, company_info: Dict, kwargs: Dict) -> Dict:
        """선하증권 데이터 생성"""
        return {
            "bl_number": f"BL-{datetime.now().strftime('%Y%m%d')}-{kwargs.get('quantity', '001')}",
            "importer_name": kwargs.get("importer_name", "수입자명"),
            "importer_address": kwargs.get("importer_address", "수입자주소"),
            "importer_contact": kwargs.get("importer_contact", "수입자연락처"),
            "quantity": kwargs.get("quantity", "1,000개"),
            "package_type": kwargs.get("package_type", "카톤박스"),
            "port_of_loading": kwargs.get("port_of_loading", "부산항"),
            "final_destination": kwargs.get("final_destination", "도착항"),
            "vessel_name": kwargs.get("vessel_name", "KOREA STAR"),
            "voyage_number": kwargs.get("voyage_number", "V001"),
            "container_number": kwargs.get("container_number", "KRSU1234567"),
            "net_weight": kwargs.get("net_weight", "500kg"),
            "gross_weight": kwargs.get("gross_weight", "550kg"),
            "cbm": kwargs.get("cbm", "2.5 CBM"),
            "package_count": kwargs.get("package_count", "50박스"),
            "incoterms": kwargs.get("incoterms", "FOB"),
            "freight_terms": kwargs.get("freight_terms", "Prepaid")
        }
    
    def _generate_declaration_details(self, regulations: Dict) -> str:
        """수출신고 상세내용 생성"""
        details = [
            "수출신고 접수 완료",
            "제품 검사 통과",
            "서류 검토 완료",
            "수출 승인"
        ]
        return self._format_list(details)
    
    def _generate_health_inspection_results(self, regulations: Dict) -> str:
        """위생검사 결과 생성"""
        results = [
            "미생물 검사: 적합",
            "화학성분 검사: 적합",
            "물리적 검사: 적합",
            "위생관리 검사: 적합"
        ]
        return self._format_list(results)
    
    def _generate_fda_data(self, company_info: Dict, kwargs: Dict) -> Dict:
        """FDA 등록 데이터 생성"""
        current_date = datetime.now()
        return {
            "fda_number": f"FDA-{company_info.get('business_number', '123456789').replace('-', '')}-{current_date.strftime('%Y%m')}",
            "registration_date": current_date.strftime("%Y-%m-%d"),
            "renewal_date": (current_date + timedelta(days=730)).strftime("%Y-%m-%d"),
            "representative": kwargs.get("representative", "대표자명"),
            "product_category": kwargs.get("product_category", "Processed Food"),
            "us_agent_name": kwargs.get("us_agent_name", "US Agent Name"),
            "us_agent_address": kwargs.get("us_agent_address", "US Agent Address"),
            "us_agent_contact": kwargs.get("us_agent_contact", "US Agent Contact"),
            "next_renewal_date": (current_date + timedelta(days=730)).strftime("%Y-%m-%d")
        }
    
    def _generate_fsvp_data(self, company_info: Dict, kwargs: Dict) -> Dict:
        """FSVP 인증 데이터 생성"""
        current_date = datetime.now()
        return {
            "fsvp_number": f"FSVP-{company_info.get('business_number', '123456789').replace('-', '')}-{current_date.strftime('%Y%m')}",
            "certification_date": current_date.strftime("%Y-%m-%d"),
            "product_category": kwargs.get("product_category", "Processed Food"),
            "verification_items": self._format_list([
                "위험분석 및 예방통제",
                "공급업자 검증 프로그램",
                "식품안전계획 수립",
                "모니터링 및 검증"
            ]),
            "exemption_status": "해당 없음"
        }
    
    def _generate_chinese_label_data(self, company_info: Dict, kwargs: Dict) -> Dict:
        """중문 라벨 데이터 생성"""
        return {
            "label_number": f"CN-{datetime.now().strftime('%Y%m%d')}-{kwargs.get('quantity', '001')}",
            "product_name_chinese": kwargs.get("product_name_chinese", "拉面"),
            "manufacturer_chinese": kwargs.get("manufacturer_chinese", "韩国食品公司"),
            "expiry_date_chinese": kwargs.get("expiry_date_chinese", "2026年12月31日"),
            "ingredients_chinese": self._format_list([
                "面条: 小麦粉",
                "调味包: 盐, 糖, 香料",
                "蔬菜包: 脱水蔬菜"
            ]),
            "nutrition_chinese": self._format_list([
                "热量: 400千卡",
                "蛋白质: 12克",
                "脂肪: 15克",
                "碳水化合物: 60克"
            ]),
            "storage_chinese": "常温保存，避免阳光直射",
            "allergy_chinese": "含有小麦，麸质过敏者慎食",
            "translator": kwargs.get("translator", "专业翻译"),
            "translation_agency": kwargs.get("translation_agency", "翻译机构"),
            "verification_date": datetime.now().strftime("%Y-%m-%d")
        }
    
    def _generate_radiation_data(self, company_info: Dict, kwargs: Dict) -> Dict:
        """방사능 검사 데이터 생성"""
        return {
            "inspection_number": f"RAD-{datetime.now().strftime('%Y%m%d')}-{kwargs.get('quantity', '001')}",
            "inspection_date": datetime.now().strftime("%Y-%m-%d"),
            "iodine_result": "검출되지 않음 (<10 Bq/kg)",
            "cesium134_result": "검출되지 않음 (<10 Bq/kg)",
            "cesium137_result": "검출되지 않음 (<10 Bq/kg)",
            "inspection_results": self._format_list([
                "요오드(131I): 검출되지 않음",
                "세슘(134Cs): 검출되지 않음",
                "세슘(137Cs): 검출되지 않음",
                "종합판정: 적합"
            ]),
            "inspector": kwargs.get("inspector", "방사능검사관")
        }
    
    def _generate_production_area_data(self, company_info: Dict, kwargs: Dict) -> Dict:
        """생산지 증명 데이터 생성"""
        return {
            "production_area": kwargs.get("production_area", "경기도 구리시"),
            "production_facility": kwargs.get("production_facility", "한국식품공장"),
            "production_date": kwargs.get("production_date", datetime.now().strftime("%Y-%m-%d")),
            "area_verification": self._format_list([
                "후쿠시마 원전사고 영향 지역 아님",
                "방사능 오염 위험 지역 아님",
                "안전한 생산지역에서 생산",
                "일본 정부 기준 적합"
            ])
        }
    
    def _generate_eu_facility_data(self, company_info: Dict, kwargs: Dict) -> Dict:
        """EU 작업장 등록 데이터 생성"""
        current_date = datetime.now()
        return {
            "registration_number": f"EU-{company_info.get('business_number', '123456789').replace('-', '')}-{current_date.strftime('%Y%m')}",
            "registration_date": current_date.strftime("%Y-%m-%d"),
            "facility_name": kwargs.get("facility_name", "한국식품공장"),
            "facility_address": company_info.get("exporter_address", "한국 주소"),
            "facility_type": kwargs.get("facility_type", "식품제조시설"),
            "product_category": kwargs.get("product_category", "Processed Food")
        }
    
    def _generate_eori_data(self, company_info: Dict, kwargs: Dict) -> Dict:
        """EORI 번호 데이터 생성"""
        current_date = datetime.now()
        return {
            "eori_number": f"EU{company_info.get('business_number', '123456789').replace('-', '')}",
            "registration_date": current_date.strftime("%Y-%m-%d"),
            "eu_member_state": kwargs.get("eu_member_state", "Germany"),
            "product_category": kwargs.get("product_category", "Processed Food")
        }
    
    def generate_all_documents(self, country: str, product: str, 
                              company_info: Dict, **kwargs) -> Dict[str, str]:
        """모든 필요한 서류 생성"""
        
        if not self.regulations:
            return {"error": "규제 정보를 찾을 수 없습니다."}
        
        regulations = self.regulations.get(country, {}).get(product, {})
        if not regulations:
            return {"error": f"{country}의 {product}에 대한 규제 정보가 없습니다."}
        
        # 필요한 서류 목록 (규제 정보 기반)
        required_docs = regulations.get("필요서류", [])
        
        # 기본 필수 서류 추가 (모든 국가 공통)
        basic_required_docs = [
            "상업송장(Commercial Invoice, C/I)",
            "포장명세서(Packing List, P/L)",
            "원산지증명서(Certificate of Origin, C/O)",
            "선하증권(Bill of Lading, B/L)",
            "수출신고필증",
            "위생증명서(Health Certificate, H/C)"
        ]
        
        # 국가별 추가 서류
        country_additional_docs = {
            "미국": [
                "FDA 등록번호(FFR: Food Facility Registration)",
                "FSVP(해외공급업자검증프로그램) 관련 서류",
                "FCE/SID 번호 (저산성 식품)"
            ],
            "중국": [
                "중문라벨링",
                "제조공정도 및 성분분석표",
                "검사 신청시 필요 서류"
            ],
            "일본": [
                "방사능 검사증명서",
                "생산지증명서"
            ],
            "EU": [
                "EU 작업장 등록",
                "EORI 번호(유럽연합위원회 세관등록번호)"
            ]
        }
        
        # 모든 필요한 서류 통합
        all_required_docs = basic_required_docs.copy()
        if country in country_additional_docs:
            all_required_docs.extend(country_additional_docs[country])
        
        # 규제 정보의 필요서류도 추가
        all_required_docs.extend(required_docs)
        
        # 중복 제거
        required_docs = list(dict.fromkeys(all_required_docs))
        
        # 서류 유형 매핑 (기본 필수 서류)
        basic_docs = {
            "상업송장": "상업송장",
            "포장명세서": "포장명세서",
            "원산지증명서": "원산지증명서",
            "선하증권": "선하증권",
            "수출신고서": "수출신고서",
            "수출신고필증": "수출신고필증",
            "위생증명서": "위생증명서"
        }
        
        # 국가별 추가 서류 매핑
        country_specific_docs = {
            "미국": {
                "FDA": "FDA등록번호",
                "FSVP": "FSVP인증서",
                "FCE": "FDA등록번호",
                "SID": "FDA등록번호"
            },
            "중국": {
                "중문라벨": "중문라벨",
                "중국어라벨": "중문라벨",
                "제조공정도": "중문라벨",
                "성분분석표": "성분분석서"
            },
            "일본": {
                "방사능": "방사능검사증명서",
                "생산지": "생산지증명서",
                "후쿠시마": "생산지증명서"
            },
            "EU": {
                "EU작업장": "EU작업장등록",
                "EORI": "EORI번호",
                "유럽연합": "EORI번호"
            }
        }
        
        # 식품 특화 서류
        food_specific_docs = {
            "식품안전인증서": "식품안전인증서",
            "성분분석서": "성분분석서",
            "라벨": "라벨검토서"
        }
        
        # 모든 매핑 통합
        doc_mapping = {**basic_docs, **food_specific_docs}
        
        # 국가별 추가 서류 추가
        if country in country_specific_docs:
            doc_mapping.update(country_specific_docs[country])
        
        generated_docs = {}
        
        for doc_name in required_docs:
            for keyword, doc_type in doc_mapping.items():
                if keyword in doc_name:
                    try:
                        content = self.generate_document(doc_type, country, product, company_info, **kwargs)
                        generated_docs[doc_name] = content
                        break
                    except Exception as e:
                        generated_docs[doc_name] = f"❌ 서류 생성 실패: {e}"
        
        return generated_docs
    
    def save_documents(self, documents: Dict[str, str], output_dir: str = "generated_documents") -> str:
        """생성된 서류들을 파일로 저장"""
        
        # 출력 디렉토리 생성
        os.makedirs(output_dir, exist_ok=True)
        
        saved_files = []
        
        for doc_name, content in documents.items():
            if content.startswith("❌"):
                continue
                
            # 파일명 생성
            safe_name = doc_name.replace("/", "_").replace(" ", "_")
            filename = f"{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            filepath = os.path.join(output_dir, filename)
            
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                saved_files.append(filepath)
            except Exception as e:
                print(f"❌ 파일 저장 실패 ({filename}): {e}")
        
        return saved_files
    
    def get_document_checklist(self, country: str, product: str) -> Dict:
        """서류 체크리스트 생성"""
        
        if not self.regulations:
            return {"error": "규제 정보를 찾을 수 없습니다."}
        
        regulations = self.regulations.get(country, {}).get(product, {})
        if not regulations:
            return {"error": f"{country}의 {product}에 대한 규제 정보가 없습니다."}
        
        checklist = {
            "필요서류": regulations.get("필요서류", []),
            "통관절차": regulations.get("통관절차", []),
            "주의사항": regulations.get("주의사항", []),
            "처리기간": regulations.get("추가정보", {}).get("처리기간", "정보 없음"),
            "수수료": regulations.get("추가정보", {}).get("수수료", "정보 없음")
        }
        
        return checklist

def main():
    """서류 생성 시스템 테스트"""
    generator = DocumentGenerator()
    
    # 회사 정보 설정
    company_info = {
        "manufacturer": "한국식품(주)",
        "exporter_name": "한국식품(주)",
        "business_number": "123-45-67890",
        "exporter_address": "서울특별시 강남구 테헤란로 123",
        "exporter_contact": "02-1234-5678",
        "contact_person": "김수출",
        "contact_info": "02-1234-5678",
        "analyst": "이분석",
        "reviewer": "박검토",
        "analysis_authority": "한국식품연구원",
        "review_authority": "한국식품의약품안전처",
        "declaration_authority": "관세청",
        "issuing_authority": "한국식품의약품안전처"
    }
    
    print("📋 자동 서류 생성 시스템")
    print("=" * 50)
    
    # 테스트 실행
    country = "중국"
    product = "라면"
    
    print(f"🌍 대상: {country} - {product}")
    print(f"📊 회사: {company_info['manufacturer']}")
    print()
    
    # 체크리스트 생성
    checklist = generator.get_document_checklist(country, product)
    if "error" not in checklist:
        print("📋 서류 체크리스트:")
        print("-" * 30)
        for i, doc in enumerate(checklist["필요서류"], 1):
            print(f"{i}. {doc}")
        print()
    
    # 모든 서류 생성
    documents = generator.generate_all_documents(country, product, company_info)
    
    if "error" not in documents:
        print("✅ 생성된 서류:")
        print("-" * 30)
        for doc_name, content in documents.items():
            print(f"📄 {doc_name}")
            print(f"   길이: {len(content)}자")
            print()
        
        # 파일로 저장
        saved_files = generator.save_documents(documents)
        print(f"💾 저장된 파일: {len(saved_files)}개")
        for filepath in saved_files:
            print(f"   📁 {filepath}")
    else:
        print(f"❌ {documents['error']}")

if __name__ == "__main__":
    main() 