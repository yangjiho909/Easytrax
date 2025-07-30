# mvp_regulations.py
# MVP 버전 - 중국, 미국만 지원

import pandas as pd
import json
from datetime import datetime

# MVP 버전 규제 데이터 (중국, 미국만)
MVP_REGULATIONS = {
    "중국": {
        "라면": {
            "제한사항": [
                "방부제 함량 제한: 0.1% 이하 (BHA, BHT, TBHQ 등)",
                "라벨에 중국어 표기 필수 (제품명, 성분, 원산지, 유통기한)",
                "식품안전인증 필요 (GB 2760-2014 기준)",
                "원산지 명시 필수 (중국어로 표기)",
                "알레르기 정보 표시 필수 (8대 알레르기 원료)",
                "영양성분표 필수 (100g당 열량, 단백질, 지방, 탄수화물, 나트륨)",
                "식품첨가물 기준 준수 (중국 식품첨가물 사용기준)",
                "미생물 기준: 총균수 10,000 CFU/g 이하, 대장균군 음성"
            ],
            "허용기준": [
                "방부제 0.1% 이하 (BHA, BHT, TBHQ, PG 등)",
                "원산지 명시 필수 (중국어로 표기)",
                "중국어 라벨 필수 (제품명, 성분, 원산지, 유통기한, 보관방법)",
                "식품안전인증서 소지 (GB 2760-2014 기준)",
                "알레르기 정보 표시 (8대 알레르기 원료 포함 여부)",
                "영양성분표 표시 (100g당 기준)",
                "식품첨가물 기준 준수 (중국 식품첨가물 사용기준)",
                "미생물 기준 준수 (총균수, 대장균군, 황색포도상구균 등)"
            ],
            "필요서류": [
                "상업송장 (Commercial Invoice)",
                "포장명세서 (Packing List)",
                "원산지증명서 (Certificate of Origin)",
                "위생증명서 (Health Certificate)"
            ],
            "통관절차": [
                "1. 수출신고 (한국 관세청)",
                "2. 검역검사 (중국 검역소)",
                "3. 식품안전검사 (중국 식품의약품감독관리총국)",
                "4. 라벨 검사 (중국어 라벨 적합성)",
                "5. 통관승인 (중국 세관)",
                "6. 국내 유통 허가 (중국 식품의약품감독관리총국)"
            ],
            "주의사항": [
                "중국어 라벨 미표기 시 반송 가능 (라벨 번역 전문업체 이용 권장)",
                "방부제 함량 초과 시 폐기 처리 (0.1% 이하 준수 필수)",
                "알레르기 정보 미표기 시 반송 (8대 알레르기 원료 포함 여부)",
                "원산지 미표기 시 반송 (중국어로 '한국산' 표기 필수)",
                "식품안전인증서 미소지 시 반송 (GB 2760-2014 기준)",
                "미생물 기준 초과 시 폐기 (총균수, 대장균군 등)",
                "유통기한 표기 오류 시 반송 (YYYY-MM-DD 형식)",
                "보관방법 미표기 시 반송 (온도, 습도 등)"
            ],
            "추가정보": {
                "관련법규": "중국 식품안전법, 식품첨가물 사용기준 GB 2760-2014",
                "검사기관": "중국 식품의약품감독관리총국, 검역소",
                "처리기간": "통상 7-14일 (검사 결과에 따라 변동)",
                "수수료": "검사비 약 2,000-5,000위안 (제품별 차이)",
                "최종업데이트": "2024-01-15",
                "원본언어": "zh-CN",
                "번역출처": "MFDS CES Food DataBase"
            }
        }
    },
    "미국": {
        "라면": {
            "제한사항": [
                "FDA 등록번호 필수 (Food Facility Registration)",
                "라벨에 영어 표기 필수 (제품명, 성분, 원산지, 유통기한)",
                "영양성분표 필수 (FDA 기준)",
                "알레르기 정보 표시 필수 (8대 알레르기 원료)",
                "성분표 필수 (내림차순)",
                "제조사 정보 표시 필수",
                "유통기한 표기 필수",
                "보관방법 표시 필수"
            ],
            "허용기준": [
                "FDA 등록번호 소지 (Food Facility Registration)",
                "영어 라벨 필수 (제품명, 성분, 원산지, 유통기한, 보관방법)",
                "영양성분표 표시 (FDA 기준)",
                "알레르기 정보 표시 (8대 알레르기 원료 포함 여부)",
                "성분표 표시 (내림차순)",
                "제조사 정보 표시",
                "유통기한 표기",
                "보관방법 표시"
            ],
            "필요서류": [
                "상업송장 (Commercial Invoice)",
                "포장명세서 (Packing List)",
                "원산지증명서 (Certificate of Origin)",
                "위생증명서 (Health Certificate)"
            ],
            "통관절차": [
                "1. 수출신고 (한국 관세청)",
                "2. FDA 검사 (미국 FDA)",
                "3. 라벨 검사 (영어 라벨 적합성)",
                "4. 통관승인 (미국 세관)",
                "5. 국내 유통 허가 (미국 FDA)"
            ],
            "주의사항": [
                "영어 라벨 미표기 시 반송 가능 (라벨 번역 전문업체 이용 권장)",
                "FDA 등록번호 미소지 시 반송 (Food Facility Registration 필수)",
                "알레르기 정보 미표기 시 반송 (8대 알레르기 원료 포함 여부)",
                "원산지 미표기 시 반송 (Country of Origin 표기 필수)",
                "영양성분표 오류 시 반송 (FDA 기준)",
                "성분표 오류 시 반송 (내림차순)",
                "제조사 정보 미표기 시 반송",
                "유통기한 표기 오류 시 반송"
            ],
            "추가정보": {
                "관련법규": "미국 식품안전법, FDA 규정",
                "검사기관": "미국 FDA, 세관",
                "처리기간": "통상 5-10일 (검사 결과에 따라 변동)",
                "수수료": "검사비 약 $500-1,500 (제품별 차이)",
                "최종업데이트": "2024-01-15",
                "원본언어": "en-US",
                "번역출처": "MFDS CES Food DataBase"
            }
        }
    }
}

def get_mvp_regulations(country, product):
    """MVP 버전 국가별 규제정보 조회"""
    if country in MVP_REGULATIONS:
        if product in MVP_REGULATIONS[country]:
            return MVP_REGULATIONS[country][product]
    return None

def search_mvp_regulations(keyword):
    """키워드로 MVP 규제정보 검색"""
    results = []
    for country, products in MVP_REGULATIONS.items():
        for product, regulations in products.items():
            if keyword in product or any(keyword in str(reg) for reg in regulations.values()):
                results.append({
                    "국가": country,
                    "제품": product,
                    "규정": regulations
                })
    return results

def get_mvp_countries():
    """MVP 지원 국가 목록 반환"""
    return list(MVP_REGULATIONS.keys())

def get_mvp_products():
    """MVP 지원 제품 카테고리 목록 반환"""
    products = set()
    for country_data in MVP_REGULATIONS.values():
        products.update(country_data.keys())
    return list(products)

def display_mvp_regulation_info(country, product):
    """MVP 규제정보 출력"""
    regulations = get_mvp_regulations(country, product)
    if not regulations:
        return f"❌ {country}의 {product}에 대한 MVP 규제정보가 없습니다."
    
    result = f"\n📋 {country} - {product} MVP 규제정보\n"
    result += "=" * 60 + "\n"
    
    for key, value in regulations.items():
        if key == "추가정보":
            continue
        result += f"\n🔸 {key}:\n"
        if isinstance(value, list):
            for i, item in enumerate(value, 1):
                result += f"   {i:2d}. {item}\n"
        else:
            result += f"   {value}\n"
    
    # 추가정보 표시
    if "추가정보" in regulations:
        result += f"\n📊 추가 정보:\n"
        result += "-" * 40 + "\n"
        for key, value in regulations["추가정보"].items():
            result += f"   {key}: {value}\n"
    
    return result

def main():
    """MVP 규제정보 테스트"""
    print("🎯 MVP 규제정보 시스템")
    print("=" * 50)
    print(f"지원 국가: {', '.join(get_mvp_countries())}")
    print(f"지원 제품: {', '.join(get_mvp_products())}")
    print()
    
    # 테스트
    test_cases = [
        ("중국", "라면"),
        ("미국", "라면")
    ]
    
    for country, product in test_cases:
        print(f"🔍 {country} - {product} 규제정보:")
        print(display_mvp_regulation_info(country, product))
        print()

if __name__ == "__main__":
    main() 