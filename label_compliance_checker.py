#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
✅ 라벨 규제 준수성 검토 시스템
- 국가별 라벨링 규정 검증
- 필수 표기사항 체크
- 언어 요구사항 검토
- 형식 및 레이아웃 검증
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json

class LabelComplianceChecker:
    """라벨 규제 준수성 검토기"""
    
    def __init__(self):
        self.regulations = self._load_regulations()
        self.required_fields = self._load_required_fields()
        self.language_requirements = self._load_language_requirements()
        self.format_requirements = self._load_format_requirements()
    
    def _load_regulations(self) -> Dict:
        """국가별 라벨링 규정 로딩"""
        return {
            "중국": {
                "name": "GB 7718-2025",
                "effective_date": "2025-01-01",
                "required_language": ["중국어"],
                "optional_language": ["영어"],
                "font_size_min": 1.8,  # mm
                "contrast_ratio": 4.5,
                "allergen_count": 8,
                "nutrition_components": ["열량", "단백질", "지방", "탄수화물", "나트륨", "당류"],
                "mandatory_statements": [
                    "제품명",
                    "성분표",
                    "제조사",
                    "유통기한",
                    "보관방법",
                    "중량",
                    "영양성분표"
                ]
            },
            "미국": {
                "name": "FDA 2025",
                "effective_date": "2025-01-01",
                "required_language": ["영어"],
                "optional_language": ["스페인어"],
                "font_size_min": 6,  # point
                "contrast_ratio": 3.0,
                "allergen_count": 9,
                "nutrition_components": [
                    "Calories", "Total Fat", "Saturated Fat", "Trans Fat",
                    "Cholesterol", "Sodium", "Total Carbohydrate", "Dietary Fiber",
                    "Total Sugars", "Added Sugars", "Protein", "Vitamin D",
                    "Calcium", "Iron", "Potassium"
                ],
                "mandatory_statements": [
                    "Product Name",
                    "Ingredients List",
                    "Manufacturer",
                    "Expiration Date",
                    "Storage Instructions",
                    "Net Weight",
                    "Nutrition Facts"
                ]
            },
            "한국": {
                "name": "식품표시기준",
                "effective_date": "2024-01-01",
                "required_language": ["한국어"],
                "optional_language": ["영어"],
                "font_size_min": 8,  # point
                "contrast_ratio": 3.5,
                "allergen_count": 7,
                "nutrition_components": ["열량", "단백질", "지방", "탄수화물", "나트륨", "당류"],
                "mandatory_statements": [
                    "제품명",
                    "성분명",
                    "제조사",
                    "유통기한",
                    "보관방법",
                    "중량",
                    "영양성분표"
                ]
            },
            "일본": {
                "name": "식품표시기준",
                "effective_date": "2024-01-01",
                "required_language": ["일본어"],
                "optional_language": ["영어"],
                "font_size_min": 8,  # point
                "contrast_ratio": 3.0,
                "allergen_count": 7,
                "nutrition_components": ["열량", "단백질", "지방", "탄수화물", "나트륨"],
                "mandatory_statements": [
                    "제품명",
                    "성분명",
                    "제조사",
                    "유통기한",
                    "보관방법",
                    "중량",
                    "영양성분표"
                ]
            },
            "EU": {
                "name": "EU Regulation 1169/2011",
                "effective_date": "2014-12-13",
                "required_language": ["영어"],
                "optional_language": ["프랑스어", "독일어", "이탈리아어", "스페인어"],
                "font_size_min": 1.2,  # mm
                "contrast_ratio": 3.0,
                "allergen_count": 14,
                "nutrition_components": [
                    "Energy", "Fat", "Saturates", "Carbohydrate", "Sugars",
                    "Protein", "Salt"
                ],
                "mandatory_statements": [
                    "Product Name",
                    "Ingredients List",
                    "Manufacturer",
                    "Best Before Date",
                    "Storage Instructions",
                    "Net Quantity",
                    "Nutrition Information"
                ]
            }
        }
    
    def _load_required_fields(self) -> Dict:
        """필수 필드 정의"""
        return {
            "product_name": {
                "required": True,
                "max_length": 100,
                "min_length": 2
            },
            "manufacturer": {
                "required": True,
                "max_length": 200,
                "min_length": 2
            },
            "ingredients": {
                "required": True,
                "max_length": 1000,
                "min_length": 5
            },
            "expiry_date": {
                "required": True,
                "format": r"\d{4}-\d{2}-\d{2}"
            },
            "weight": {
                "required": True,
                "format": r"\d+(?:\.\d+)?\s*(?:g|ml|kg|L)"
            },
            "nutrition": {
                "required": True,
                "min_components": 6
            },
            "allergies": {
                "required": False,
                "max_count": 20
            }
        }
    
    def _load_language_requirements(self) -> Dict:
        """언어 요구사항"""
        return {
            "중국어": {
                "characters": "가-힣",
                "required_chars": ["제품명", "성분", "제조사", "유통기한"],
                "forbidden_chars": ["※", "★", "♥"]
            },
            "영어": {
                "characters": "a-zA-Z",
                "required_chars": ["Product", "Ingredients", "Manufacturer", "Expiry"],
                "forbidden_chars": ["*", "★", "♥"]
            },
            "일본어": {
                "characters": "あ-んア-ン",
                "required_chars": ["商品名", "原材料", "製造者", "賞味期限"],
                "forbidden_chars": ["※", "★", "♥"]
            }
        }
    
    def _load_format_requirements(self) -> Dict:
        """형식 요구사항"""
        return {
            "date_formats": [
                r"\d{4}-\d{2}-\d{2}",
                r"\d{4}/\d{2}/\d{2}",
                r"\d{2}-\d{2}-\d{4}",
                r"\d{2}/\d{2}/\d{4}"
            ],
            "weight_formats": [
                r"\d+(?:\.\d+)?\s*g",
                r"\d+(?:\.\d+)?\s*ml",
                r"\d+(?:\.\d+)?\s*kg",
                r"\d+(?:\.\d+)?\s*L"
            ],
            "nutrition_formats": [
                r"\d+(?:\.\d+)?\s*(?:kcal|g|mg)"
            ]
        }
    
    def check_compliance(self, label_info: Dict, country: str) -> Dict:
        """라벨 규제 준수성 검토 - 단순하고 정확한 점수 계산"""
        
        print(f"🔍 라벨 준수성 검토 시작: {country}")
        print(f"📊 라벨 정보: {label_info}")
        
        if country not in self.regulations:
            return {
                "compliant": False,
                "errors": [f"지원하지 않는 국가: {country}"],
                "warnings": [],
                "score": 0,
                "compliance_status": "지원하지 않는 국가"
            }
        
        regulation = self.regulations[country]
        errors = []
        warnings = []
        score = 100
        
        # 1. 필수 필드 검증 (30점)
        field_errors, field_warnings, field_score = self._check_required_fields(
            label_info, regulation
        )
        errors.extend(field_errors)
        warnings.extend(field_warnings)
        score -= field_score
        
        # 2. 언어 요구사항 검증 (25점)
        lang_errors, lang_warnings, lang_score = self._check_language_requirements(
            label_info, regulation
        )
        errors.extend(lang_errors)
        warnings.extend(lang_warnings)
        score -= lang_score
        
        # 3. 영양성분 검증 (20점)
        nutrition_errors, nutrition_warnings, nutrition_score = self._check_nutrition_requirements(
            label_info, regulation
        )
        errors.extend(nutrition_errors)
        warnings.extend(nutrition_warnings)
        score -= nutrition_score
        
        # 4. 알레르기 정보 검증 (15점)
        allergy_errors, allergy_warnings, allergy_score = self._check_allergy_requirements(
            label_info, regulation
        )
        errors.extend(allergy_errors)
        warnings.extend(allergy_warnings)
        score -= allergy_score
        
        # 5. 형식 요구사항 검증 (10점)
        format_errors, format_warnings, format_score = self._check_format_requirements(
            label_info, regulation
        )
        errors.extend(format_errors)
        warnings.extend(format_warnings)
        score -= format_score
        
        # 점수 보정 (0-100 범위)
        final_score = max(0, min(100, score))
        
        # 준수 상태 결정
        if final_score >= 90:
            compliance_status = "준수"
        elif final_score >= 70:
            compliance_status = "부분 준수"
        elif final_score >= 50:
            compliance_status = "미준수 (개선 가능)"
        else:
            compliance_status = "심각한 미준수"
        
        print(f"✅ 라벨 검토 완료 - 점수: {final_score}, 상태: {compliance_status}")
        
        return {
            "compliant": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "score": final_score,
            "compliance_status": compliance_status,
            "regulation": regulation["name"],
            "check_timestamp": datetime.now().isoformat(),
            "analysis_details": {
                "country": country,
                "total_checks": 5,
                "passed_checks": 5 - len(errors),
                "field_score_deduction": field_score,
                "language_score_deduction": lang_score,
                "nutrition_score_deduction": nutrition_score,
                "allergy_score_deduction": allergy_score,
                "format_score_deduction": format_score
            }
        }
    
    def _check_required_fields(self, label_info: Dict, regulation: Dict) -> Tuple[List, List, int]:
        """필수 필드 검증 (30점 만점)"""
        errors = []
        warnings = []
        score_deduction = 0
        
        mandatory_statements = regulation.get("mandatory_statements", [])
        max_deduction_per_field = 30 // len(mandatory_statements) if mandatory_statements else 30
        
        for statement in mandatory_statements:
            if not self._has_required_field(label_info, statement):
                errors.append(f"필수 표기사항 누락: {statement}")
                score_deduction += max_deduction_per_field
            else:
                # 필드 길이 검증
                field_value = self._get_field_value(label_info, statement)
                if field_value:
                    if len(field_value) < 2:
                        warnings.append(f"표기사항이 너무 짧음: {statement}")
                        score_deduction += 2
                    elif len(field_value) > 500:
                        warnings.append(f"표기사항이 너무 김: {statement}")
                        score_deduction += 2
        
        # 최대 30점까지만 차감
        return errors, warnings, min(score_deduction, 30)
    
    def _check_language_requirements(self, label_info: Dict, regulation: Dict) -> Tuple[List, List, int]:
        """언어 요구사항 검증 (25점 만점)"""
        errors = []
        warnings = []
        score_deduction = 0
        
        required_languages = regulation.get("required_language", [])
        
        for language in required_languages:
            if not self._has_language_content(label_info, language):
                errors.append(f"필수 언어 누락: {language}")
                score_deduction += 25
            else:
                # 금지 문자 검증
                forbidden_chars = self._get_forbidden_characters([language])
                for field, value in label_info.items():
                    if isinstance(value, str):
                        for char in forbidden_chars:
                            if char in value:
                                warnings.append(f"금지 문자 사용: {char} in {field}")
                                score_deduction += 2
        
        # 최대 25점까지만 차감
        return errors, warnings, min(score_deduction, 25)
    
    def _check_format_requirements(self, label_info: Dict, regulation: Dict) -> Tuple[List, List, int]:
        """형식 요구사항 검증 (10점 만점)"""
        errors = []
        warnings = []
        score_deduction = 0
        
        # 날짜 형식 검증
        if "expiry_date" in label_info:
            date_value = label_info["expiry_date"]
            if not self._is_valid_date_format(date_value):
                errors.append("유통기한 형식이 올바르지 않음")
                score_deduction += 5
        
        # 중량 형식 검증
        if "weight" in label_info:
            weight_value = label_info["weight"]
            if not self._is_valid_weight_format(weight_value):
                errors.append("중량 형식이 올바르지 않음")
                score_deduction += 5
        
        # 영양성분 형식 검증
        if "nutrition" in label_info:
            nutrition_info = label_info["nutrition"]
            for nutrient, value in nutrition_info.items():
                if not self._is_valid_nutrition_format(value):
                    warnings.append(f"영양성분 형식 오류: {nutrient}")
                    score_deduction += 2
        
        # 최대 10점까지만 차감
        return errors, warnings, min(score_deduction, 10)
    
    def _check_nutrition_requirements(self, label_info: Dict, regulation: Dict) -> Tuple[List, List, int]:
        """영양성분 요구사항 검증 (20점 만점)"""
        errors = []
        warnings = []
        score_deduction = 0
        
        required_components = regulation.get("nutrition_components", [])
        nutrition_info = label_info.get("nutrition", {})
        
        # 필수 영양성분 검증
        max_deduction_per_component = 20 // len(required_components) if required_components else 20
        for component in required_components:
            if not self._has_nutrition_component(nutrition_info, component):
                errors.append(f"필수 영양성분 누락: {component}")
                score_deduction += max_deduction_per_component
        
        # 영양성분 값 검증
        for nutrient, value in nutrition_info.items():
            if value:
                try:
                    numeric_value = float(re.findall(r'\d+(?:\.\d+)?', str(value))[0])
                    if numeric_value < 0:
                        errors.append(f"영양성분 값이 음수: {nutrient}")
                        score_deduction += 5
                    elif numeric_value > 10000:
                        warnings.append(f"영양성분 값이 비정상적으로 큼: {nutrient}")
                        score_deduction += 2
                except (ValueError, IndexError):
                    warnings.append(f"영양성분 값 형식 오류: {nutrient}")
                    score_deduction += 2
        
        # 최대 20점까지만 차감
        return errors, warnings, min(score_deduction, 20)
    
    def _check_allergy_requirements(self, label_info: Dict, regulation: Dict) -> Tuple[List, List, int]:
        """알레르기 정보 요구사항 검증 (15점 만점)"""
        errors = []
        warnings = []
        score_deduction = 0
        
        max_allergen_count = regulation.get("allergen_count", 10)
        allergies = label_info.get("allergies", [])
        
        if isinstance(allergies, str):
            # 문자열을 리스트로 변환
            allergies = [allergy.strip() for allergy in allergies.split(',') if allergy.strip()]
        
        if len(allergies) > max_allergen_count:
            warnings.append(f"알레르기 정보가 너무 많음: {len(allergies)}개")
            score_deduction += 5
        
        # 알레르기 정보 품질 검증
        for allergy in allergies:
            if len(allergy) < 2:
                warnings.append(f"알레르기 정보가 너무 짧음: {allergy}")
                score_deduction += 2
        
        # 최대 15점까지만 차감
        return errors, warnings, min(score_deduction, 15)
    
    def _check_date_validity(self, label_info: Dict, regulation: Dict) -> Tuple[List, List, int]:
        """날짜 유효성 검증"""
        errors = []
        warnings = []
        score_deduction = 0
        
        if "expiry_date" in label_info:
            expiry_date = label_info["expiry_date"]
            try:
                # 날짜 파싱
                if re.match(r'\d{4}-\d{2}-\d{2}', expiry_date):
                    parsed_date = datetime.strptime(expiry_date, '%Y-%m-%d')
                elif re.match(r'\d{4}/\d{2}/\d{2}', expiry_date):
                    parsed_date = datetime.strptime(expiry_date, '%Y/%m/%d')
                else:
                    errors.append("유통기한 형식이 올바르지 않음")
                    score_deduction += 10
                    return errors, warnings, score_deduction
                
                # 과거 날짜 검증
                if parsed_date < datetime.now():
                    errors.append("유통기한이 이미 지났습니다")
                    score_deduction += 20
                
                # 너무 긴 유통기한 검증
                max_expiry = datetime.now() + timedelta(days=365*5)  # 5년
                if parsed_date > max_expiry:
                    warnings.append("유통기한이 비정상적으로 깁니다")
                    score_deduction += 5
                
            except ValueError:
                errors.append("유통기한을 파싱할 수 없습니다")
                score_deduction += 10
        
        return errors, warnings, score_deduction
    
    def _has_required_field(self, label_info: Dict, field_name: str) -> bool:
        """필수 필드 존재 여부 확인"""
        field_mapping = {
            "제품명": ["product_name", "name"],
            "Product Name": ["product_name", "name"],
            "성분표": ["ingredients", "ingredient_list"],
            "Ingredients List": ["ingredients", "ingredient_list"],
            "제조사": ["manufacturer", "producer"],
            "Manufacturer": ["manufacturer", "producer"],
            "유통기한": ["expiry_date", "expiration_date"],
            "Expiration Date": ["expiry_date", "expiration_date"],
            "보관방법": ["storage", "storage_method"],
            "Storage Instructions": ["storage", "storage_method"],
            "중량": ["weight", "net_weight"],
            "Net Weight": ["weight", "net_weight"],
            "영양성분표": ["nutrition", "nutrition_facts"],
            "Nutrition Facts": ["nutrition", "nutrition_facts"]
        }
        
        possible_fields = field_mapping.get(field_name, [field_name.lower()])
        return any(field in label_info for field in possible_fields)
    
    def _get_field_value(self, label_info: Dict, field_name: str) -> Optional[str]:
        """필드 값 가져오기"""
        field_mapping = {
            "제품명": ["product_name", "name"],
            "Product Name": ["product_name", "name"],
            "성분표": ["ingredients", "ingredient_list"],
            "Ingredients List": ["ingredients", "ingredient_list"],
            "제조사": ["manufacturer", "producer"],
            "Manufacturer": ["manufacturer", "producer"],
            "유통기한": ["expiry_date", "expiration_date"],
            "Expiration Date": ["expiry_date", "expiration_date"],
            "보관방법": ["storage", "storage_method"],
            "Storage Instructions": ["storage", "storage_method"],
            "중량": ["weight", "net_weight"],
            "Net Weight": ["weight", "net_weight"],
            "영양성분표": ["nutrition", "nutrition_facts"],
            "Nutrition Facts": ["nutrition", "nutrition_facts"]
        }
        
        possible_fields = field_mapping.get(field_name, [field_name.lower()])
        for field in possible_fields:
            if field in label_info:
                return str(label_info[field])
        
        return None
    
    def _has_language_content(self, label_info: Dict, language: str) -> bool:
        """언어별 내용 존재 여부 확인"""
        # 간단한 언어 감지 (실제로는 더 정교한 방법 필요)
        language_patterns = {
            "한국어": r"[가-힣]",
            "중국어": r"[一-龯]",
            "일본어": r"[あ-んア-ン]",
            "영어": r"[a-zA-Z]"
        }
        
        pattern = language_patterns.get(language, r"")
        if not pattern:
            return True  # 패턴이 없으면 모든 언어 허용
        
        # 모든 텍스트 필드에서 언어 확인
        for field, value in label_info.items():
            if isinstance(value, str) and re.search(pattern, value):
                return True
            elif isinstance(value, dict):
                for sub_field, sub_value in value.items():
                    if isinstance(sub_value, str) and re.search(pattern, sub_value):
                        return True
        
        return False
    
    def _get_forbidden_characters(self, languages: List[str]) -> List[str]:
        """금지 문자 목록 가져오기"""
        forbidden_chars = []
        for language in languages:
            if language in self.language_requirements:
                forbidden_chars.extend(self.language_requirements[language].get("forbidden_chars", []))
        return list(set(forbidden_chars))
    
    def _is_valid_date_format(self, date_str: str) -> bool:
        """날짜 형식 검증"""
        if not date_str:
            return False
        
        date_patterns = self.format_requirements["date_formats"]
        return any(re.match(pattern, date_str) for pattern in date_patterns)
    
    def _is_valid_weight_format(self, weight_str: str) -> bool:
        """중량 형식 검증"""
        if not weight_str:
            return False
        
        weight_patterns = self.format_requirements["weight_formats"]
        return any(re.match(pattern, weight_str) for pattern in weight_patterns)
    
    def _is_valid_nutrition_format(self, nutrition_str: str) -> bool:
        """영양성분 형식 검증"""
        if not nutrition_str:
            return False
        
        nutrition_patterns = self.format_requirements["nutrition_formats"]
        return any(re.match(pattern, nutrition_str) for pattern in nutrition_patterns)
    
    def _has_nutrition_component(self, nutrition_info: Dict, component: str) -> bool:
        """영양성분 존재 여부 확인"""
        # 영양성분 매핑
        component_mapping = {
            "열량": ["calories", "energy", "열량"],
            "단백질": ["protein", "단백질"],
            "지방": ["fat", "지방"],
            "탄수화물": ["carbohydrates", "carbs", "탄수화물"],
            "나트륨": ["sodium", "나트륨"],
            "당류": ["sugar", "당류"],
            "Calories": ["calories", "energy"],
            "Protein": ["protein"],
            "Fat": ["fat"],
            "Carbohydrate": ["carbohydrates", "carbs"],
            "Sodium": ["sodium"],
            "Sugar": ["sugar"]
        }
        
        possible_names = component_mapping.get(component, [component.lower()])
        return any(name in nutrition_info for name in possible_names)
    
    def generate_compliance_report(self, label_info: Dict, country: str) -> Dict:
        """규제 준수성 보고서 생성"""
        compliance_result = self.check_compliance(label_info, country)
        
        report = {
            "summary": {
                "country": country,
                "compliant": compliance_result["compliant"],
                "score": compliance_result["score"],
                "regulation": compliance_result["regulation"],
                "check_date": compliance_result["check_timestamp"]
            },
            "details": {
                "errors": compliance_result["errors"],
                "warnings": compliance_result["warnings"],
                "error_count": len(compliance_result["errors"]),
                "warning_count": len(compliance_result["warnings"])
            },
            "recommendations": self._generate_recommendations(
                compliance_result, label_info, country
            )
        }
        
        return report
    
    def _generate_recommendations(self, compliance_result: Dict, label_info: Dict, country: str) -> List[str]:
        """개선 권장사항 생성"""
        recommendations = []
        
        if not compliance_result["compliant"]:
            recommendations.append("⚠️ 규제 준수를 위해 오류를 수정해야 합니다.")
        
        if compliance_result["score"] < 80:
            recommendations.append("📈 라벨 품질을 향상시키기 위해 경고사항을 검토하세요.")
        
        # 구체적인 권장사항
        for error in compliance_result["errors"]:
            if "필수 표기사항" in error:
                recommendations.append("📝 필수 표기사항을 추가하세요.")
            elif "언어" in error:
                recommendations.append("🌐 필수 언어로 내용을 작성하세요.")
            elif "형식" in error:
                recommendations.append("📋 표준 형식에 맞춰 정보를 입력하세요.")
            elif "영양성분" in error:
                recommendations.append("🥗 필수 영양성분 정보를 추가하세요.")
        
        # 국가별 특화 권장사항
        if country == "중국":
            recommendations.append("🇨🇳 중국 GB 7718-2025 규정을 준수하세요.")
        elif country == "미국":
            recommendations.append("🇺🇸 미국 FDA 2025 규정을 준수하세요.")
        elif country == "한국":
            recommendations.append("🇰🇷 한국 식품표시기준을 준수하세요.")
        
        return recommendations

def main():
    """라벨 규제 준수성 검토 시스템 테스트"""
    
    print("✅ 라벨 규제 준수성 검토 시스템")
    print("=" * 50)
    
    checker = LabelComplianceChecker()
    
    # 테스트 데이터
    test_label_info = {
        "product_name": "한국 라면",
        "manufacturer": "한국식품(주)",
        "ingredients": "면, 조미료, 건조야채",
        "expiry_date": "2025-12-31",
        "weight": "120g",
        "nutrition": {
            "calories": "400kcal",
            "protein": "12g",
            "fat": "15g",
            "carbohydrates": "60g",
            "sodium": "800mg",
            "sugar": "5g"
        },
        "allergies": ["밀", "대두"]
    }
    
    # 국가별 준수성 검토
    countries = ["중국", "미국", "한국", "일본", "EU"]
    
    for country in countries:
        print(f"\n🔍 {country} 규제 준수성 검토:")
        result = checker.check_compliance(test_label_info, country)
        
        print(f"   규정: {result['regulation']}")
        print(f"   준수: {'✅' if result['compliant'] else '❌'}")
        print(f"   점수: {result['score']}/100")
        
        if result['errors']:
            print(f"   오류: {len(result['errors'])}개")
            for error in result['errors'][:3]:  # 최대 3개만 표시
                print(f"     - {error}")
        
        if result['warnings']:
            print(f"   경고: {len(result['warnings'])}개")
            for warning in result['warnings'][:3]:  # 최대 3개만 표시
                print(f"     - {warning}")
    
    # 상세 보고서 생성
    print(f"\n📋 상세 보고서 (중국):")
    report = checker.generate_compliance_report(test_label_info, "중국")
    
    print(f"   요약: {report['summary']}")
    print(f"   권장사항:")
    for rec in report['recommendations']:
        print(f"     {rec}")

if __name__ == "__main__":
    main() 