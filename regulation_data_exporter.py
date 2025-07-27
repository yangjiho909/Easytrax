#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📊 규제정보 데이터 내보내기 시스템
- 실시간 크롤링된 규제 데이터를 다양한 형태로 저장
- Excel, JSON, CSV, TXT 등 다양한 형식 지원
- 국가별, 제품별 분류 저장
- 통합 보고서 생성
"""

import os
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import csv

class RegulationDataExporter:
    """규제정보 데이터 내보내기 시스템"""
    
    def __init__(self):
        self.export_dir = "exported_regulations"
        self.cache_dir = "regulation_cache"
        self.ensure_directories()
    
    def ensure_directories(self):
        """필요한 디렉토리 생성"""
        directories = [
            self.export_dir,
            f"{self.export_dir}/excel",
            f"{self.export_dir}/json",
            f"{self.export_dir}/csv",
            f"{self.export_dir}/txt",
            f"{self.export_dir}/reports"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def load_cached_regulations(self) -> Dict[str, Any]:
        """캐시된 규제 데이터 로드"""
        regulations = {}
        
        if not os.path.exists(self.cache_dir):
            print(f"❌ 캐시 디렉토리가 없습니다: {self.cache_dir}")
            return regulations
        
        cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.json')]
        
        for cache_file in cache_files:
            try:
                file_path = os.path.join(self.cache_dir, cache_file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 파일명에서 국가와 제품 추출
                filename = cache_file.replace('.json', '')
                parts = filename.split('_')
                if len(parts) >= 2:
                    country = parts[0]
                    product = parts[1]
                    regulations[f"{country}_{product}"] = data
                
                print(f"✅ 로드됨: {cache_file}")
                
            except Exception as e:
                print(f"❌ 로드 실패 {cache_file}: {e}")
        
        return regulations
    
    def export_to_json(self, regulations: Dict[str, Any], filename: str = None):
        """JSON 형태로 내보내기"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"regulations_export_{timestamp}.json"
        
        file_path = os.path.join(self.export_dir, "json", filename)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(regulations, f, ensure_ascii=False, indent=2)
            
            print(f"✅ JSON 내보내기 완료: {file_path}")
            return file_path
        except Exception as e:
            print(f"❌ JSON 내보내기 실패: {e}")
            return None
    
    def export_to_excel(self, regulations: Dict[str, Any], filename: str = None):
        """Excel 형태로 내보내기"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"regulations_export_{timestamp}.xlsx"
        
        file_path = os.path.join(self.export_dir, "excel", filename)
        
        try:
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # 국가별 시트 생성
                for key, data in regulations.items():
                    country, product = key.split('_', 1)
                    sheet_name = f"{country}_{product}"[:31]  # Excel 시트명 제한
                    
                    # 데이터를 DataFrame으로 변환
                    df_data = []
                    for category, content in data.items():
                        if category == "추가정보":
                            # 추가정보는 별도 처리
                            continue
                        
                        if isinstance(content, list):
                            for i, item in enumerate(content, 1):
                                df_data.append({
                                    "카테고리": category,
                                    "순번": i,
                                    "내용": item
                                })
                        else:
                            df_data.append({
                                "카테고리": category,
                                "순번": 1,
                                "내용": str(content)
                            })
                    
                    if df_data:
                        df = pd.DataFrame(df_data)
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # 추가정보 시트 생성
                additional_info = []
                for key, data in regulations.items():
                    if "추가정보" in data:
                        info = data["추가정보"]
                        info["국가_제품"] = key
                        additional_info.append(info)
                
                if additional_info:
                    df_additional = pd.DataFrame(additional_info)
                    df_additional.to_excel(writer, sheet_name="추가정보", index=False)
            
            print(f"✅ Excel 내보내기 완료: {file_path}")
            return file_path
        except Exception as e:
            print(f"❌ Excel 내보내기 실패: {e}")
            return None
    
    def export_to_csv(self, regulations: Dict[str, Any], filename: str = None):
        """CSV 형태로 내보내기"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"regulations_export_{timestamp}.csv"
        
        file_path = os.path.join(self.export_dir, "csv", filename)
        
        try:
            csv_data = []
            
            for key, data in regulations.items():
                country, product = key.split('_', 1)
                
                for category, content in data.items():
                    if category == "추가정보":
                        continue
                    
                    if isinstance(content, list):
                        for i, item in enumerate(content, 1):
                            csv_data.append({
                                "국가": country,
                                "제품": product,
                                "카테고리": category,
                                "순번": i,
                                "내용": item
                            })
                    else:
                        csv_data.append({
                            "국가": country,
                            "제품": product,
                            "카테고리": category,
                            "순번": 1,
                            "내용": str(content)
                        })
            
            if csv_data:
                df = pd.DataFrame(csv_data)
                df.to_csv(file_path, index=False, encoding='utf-8-sig')
                print(f"✅ CSV 내보내기 완료: {file_path}")
                return file_path
            else:
                print("❌ 내보낼 데이터가 없습니다.")
                return None
                
        except Exception as e:
            print(f"❌ CSV 내보내기 실패: {e}")
            return None
    
    def export_to_txt(self, regulations: Dict[str, Any], filename: str = None):
        """TXT 형태로 내보내기 (읽기 쉬운 형태)"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"regulations_export_{timestamp}.txt"
        
        file_path = os.path.join(self.export_dir, "txt", filename)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("📋 규제정보 내보내기 보고서\n")
                f.write("=" * 60 + "\n")
                f.write(f"생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"총 규제 데이터: {len(regulations)}개\n\n")
                
                for key, data in regulations.items():
                    country, product = key.split('_', 1)
                    
                    f.write(f"🌍 {country} - {product} 규제정보\n")
                    f.write("-" * 40 + "\n")
                    
                    for category, content in data.items():
                        if category == "추가정보":
                            continue
                        
                        f.write(f"\n📌 {category}:\n")
                        if isinstance(content, list):
                            for i, item in enumerate(content, 1):
                                f.write(f"   {i}. {item}\n")
                        else:
                            f.write(f"   {content}\n")
                    
                    # 추가정보 별도 출력
                    if "추가정보" in data:
                        f.write(f"\n📊 추가정보:\n")
                        for info_key, info_value in data["추가정보"].items():
                            f.write(f"   • {info_key}: {info_value}\n")
                    
                    f.write("\n" + "=" * 60 + "\n\n")
            
            print(f"✅ TXT 내보내기 완료: {file_path}")
            return file_path
        except Exception as e:
            print(f"❌ TXT 내보내기 실패: {e}")
            return None
    
    def generate_summary_report(self, regulations: Dict[str, Any], filename: str = None):
        """요약 보고서 생성"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"regulations_summary_{timestamp}.json"
        
        file_path = os.path.join(self.export_dir, "reports", filename)
        
        try:
            summary = {
                "생성_시간": datetime.now().isoformat(),
                "총_규제_데이터_수": len(regulations),
                "국가별_통계": {},
                "제품별_통계": {},
                "카테고리별_통계": {},
                "최신_업데이트": {},
                "데이터_상태": {}
            }
            
            countries = set()
            products = set()
            categories = set()
            
            for key, data in regulations.items():
                country, product = key.split('_', 1)
                countries.add(country)
                products.add(product)
                
                # 카테고리 통계
                for category in data.keys():
                    categories.add(category)
                
                # 국가별 통계
                if country not in summary["국가별_통계"]:
                    summary["국가별_통계"][country] = {
                        "제품_수": 0,
                        "규제_항목_수": 0
                    }
                summary["국가별_통계"][country]["제품_수"] += 1
                
                # 규제 항목 수 계산
                total_items = 0
                for category, content in data.items():
                    if category != "추가정보":
                        if isinstance(content, list):
                            total_items += len(content)
                        else:
                            total_items += 1
                summary["국가별_통계"][country]["규제_항목_수"] += total_items
                
                # 최신 업데이트 정보
                if "추가정보" in data and "최종업데이트" in data["추가정보"]:
                    summary["최신_업데이트"][key] = data["추가정보"]["최종업데이트"]
                
                # 데이터 상태
                if "추가정보" in data and "데이터_상태" in data["추가정보"]:
                    summary["데이터_상태"][key] = data["추가정보"]["데이터_상태"]
            
            # 제품별 통계
            for product in products:
                summary["제품별_통계"][product] = {
                    "지원_국가_수": len([k for k in regulations.keys() if product in k])
                }
            
            # 카테고리별 통계
            for category in categories:
                if category != "추가정보":
                    summary["카테고리별_통계"][category] = {
                        "포함된_규제_수": len([k for k, v in regulations.items() if category in v])
                    }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 요약 보고서 생성 완료: {file_path}")
            return file_path
        except Exception as e:
            print(f"❌ 요약 보고서 생성 실패: {e}")
            return None
    
    def export_all_formats(self, regulations: Dict[str, Any] = None):
        """모든 형태로 내보내기"""
        if regulations is None:
            regulations = self.load_cached_regulations()
        
        if not regulations:
            print("❌ 내보낼 규제 데이터가 없습니다.")
            return
        
        print(f"📊 {len(regulations)}개의 규제 데이터를 모든 형태로 내보내기 시작...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. JSON 내보내기
        json_file = self.export_to_json(regulations, f"regulations_{timestamp}.json")
        
        # 2. Excel 내보내기
        excel_file = self.export_to_excel(regulations, f"regulations_{timestamp}.xlsx")
        
        # 3. CSV 내보내기
        csv_file = self.export_to_csv(regulations, f"regulations_{timestamp}.csv")
        
        # 4. TXT 내보내기
        txt_file = self.export_to_txt(regulations, f"regulations_{timestamp}.txt")
        
        # 5. 요약 보고서 생성
        summary_file = self.generate_summary_report(regulations, f"summary_{timestamp}.json")
        
        # 결과 요약
        print(f"\n📋 내보내기 완료 요약:")
        print(f"   📁 저장 위치: {self.export_dir}/")
        print(f"   📊 JSON: {json_file}")
        print(f"   📈 Excel: {excel_file}")
        print(f"   📋 CSV: {csv_file}")
        print(f"   📝 TXT: {txt_file}")
        print(f"   📊 요약: {summary_file}")
        
        return {
            "json": json_file,
            "excel": excel_file,
            "csv": csv_file,
            "txt": txt_file,
            "summary": summary_file
        }
    
    def export_by_country(self, country: str, regulations: Dict[str, Any] = None):
        """특정 국가의 규제 데이터만 내보내기"""
        if regulations is None:
            regulations = self.load_cached_regulations()
        
        country_regulations = {k: v for k, v in regulations.items() if k.startswith(country)}
        
        if not country_regulations:
            print(f"❌ {country}의 규제 데이터가 없습니다.")
            return
        
        print(f"🌍 {country}의 {len(country_regulations)}개 규제 데이터 내보내기...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_prefix = f"{country}_regulations_{timestamp}"
        
        return {
            "json": self.export_to_json(country_regulations, f"{filename_prefix}.json"),
            "excel": self.export_to_excel(country_regulations, f"{filename_prefix}.xlsx"),
            "csv": self.export_to_csv(country_regulations, f"{filename_prefix}.csv"),
            "txt": self.export_to_txt(country_regulations, f"{filename_prefix}.txt"),
            "summary": self.generate_summary_report(country_regulations, f"{country}_summary_{timestamp}.json")
        }
    
    def export_by_product(self, product: str, regulations: Dict[str, Any] = None):
        """특정 제품의 규제 데이터만 내보내기"""
        if regulations is None:
            regulations = self.load_cached_regulations()
        
        product_regulations = {k: v for k, v in regulations.items() if product in k}
        
        if not product_regulations:
            print(f"❌ {product}의 규제 데이터가 없습니다.")
            return
        
        print(f"📦 {product}의 {len(product_regulations)}개 규제 데이터 내보내기...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_prefix = f"{product}_regulations_{timestamp}"
        
        return {
            "json": self.export_to_json(product_regulations, f"{filename_prefix}.json"),
            "excel": self.export_to_excel(product_regulations, f"{filename_prefix}.xlsx"),
            "csv": self.export_to_csv(product_regulations, f"{filename_prefix}.csv"),
            "txt": self.export_to_txt(product_regulations, f"{filename_prefix}.txt"),
            "summary": self.generate_summary_report(product_regulations, f"{product}_summary_{timestamp}.json")
        }

def main():
    """메인 실행 함수"""
    exporter = RegulationDataExporter()
    
    print("📊 규제정보 데이터 내보내기 시스템")
    print("=" * 50)
    
    # 캐시된 데이터 로드
    regulations = exporter.load_cached_regulations()
    
    if not regulations:
        print("❌ 캐시된 규제 데이터가 없습니다.")
        print("💡 먼저 실시간 크롤링을 실행해주세요.")
        return
    
    print(f"✅ {len(regulations)}개의 규제 데이터를 찾았습니다.")
    
    # 사용자 선택
    print("\n📋 내보내기 옵션:")
    print("1. 모든 데이터를 모든 형태로 내보내기")
    print("2. 특정 국가의 데이터만 내보내기")
    print("3. 특정 제품의 데이터만 내보내기")
    print("4. 특정 형태로만 내보내기")
    
    choice = input("\n선택하세요 (1-4): ").strip()
    
    if choice == "1":
        exporter.export_all_formats(regulations)
    
    elif choice == "2":
        countries = list(set([k.split('_')[0] for k in regulations.keys()]))
        print(f"🌍 사용 가능한 국가: {', '.join(countries)}")
        country = input("국가명을 입력하세요: ").strip()
        exporter.export_by_country(country, regulations)
    
    elif choice == "3":
        products = list(set([k.split('_')[1] for k in regulations.keys()]))
        print(f"📦 사용 가능한 제품: {', '.join(products)}")
        product = input("제품명을 입력하세요: ").strip()
        exporter.export_by_product(product, regulations)
    
    elif choice == "4":
        print("📁 내보내기 형태 선택:")
        print("1. JSON")
        print("2. Excel")
        print("3. CSV")
        print("4. TXT")
        print("5. 요약 보고서")
        
        format_choice = input("형태를 선택하세요 (1-5): ").strip()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_choice == "1":
            exporter.export_to_json(regulations, f"regulations_{timestamp}.json")
        elif format_choice == "2":
            exporter.export_to_excel(regulations, f"regulations_{timestamp}.xlsx")
        elif format_choice == "3":
            exporter.export_to_csv(regulations, f"regulations_{timestamp}.csv")
        elif format_choice == "4":
            exporter.export_to_txt(regulations, f"regulations_{timestamp}.txt")
        elif format_choice == "5":
            exporter.generate_summary_report(regulations, f"summary_{timestamp}.json")
        else:
            print("❌ 잘못된 선택입니다.")
    
    else:
        print("❌ 잘못된 선택입니다.")
    
    print(f"\n✅ 내보내기 완료! 파일들은 {exporter.export_dir}/ 폴더에 저장되었습니다.")

if __name__ == "__main__":
    main() 