#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📁 규제정보 데이터 관리 시스템
- 실시간 크롤링된 규제 데이터를 별도 폴더에 체계적으로 저장
- model/ 폴더와 유사한 구조로 데이터 관리
- 국가별, 제품별, 날짜별 분류 저장
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class RegulationDataManager:
    """규제정보 데이터 관리 시스템"""
    
    def __init__(self):
        self.regulation_data_dir = "regulation_data"
        self.cache_dir = "regulation_cache"
        self.ensure_directories()
    
    def ensure_directories(self):
        """필요한 디렉토리 생성"""
        directories = [
            self.regulation_data_dir,
            f"{self.regulation_data_dir}/중국",
            f"{self.regulation_data_dir}/미국", 
            f"{self.regulation_data_dir}/한국",
            f"{self.regulation_data_dir}/통합",
            f"{self.regulation_data_dir}/백업"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def organize_cached_data(self):
        """캐시된 데이터를 체계적으로 정리"""
        print("📁 규제정보 데이터 정리 중...")
        
        if not os.path.exists(self.cache_dir):
            print(f"❌ 캐시 디렉토리가 없습니다: {self.cache_dir}")
            return
        
        cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.json')]
        
        if not cache_files:
            print("❌ 캐시된 규제 데이터가 없습니다.")
            return
        
        print(f"✅ {len(cache_files)}개의 캐시 파일을 발견했습니다.")
        
        # 통합 데이터 수집
        all_regulations = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
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
                    key = f"{country}_{product}"
                    all_regulations[key] = data
                    
                    # 국가별 폴더에 저장
                    country_dir = os.path.join(self.regulation_data_dir, country)
                    if os.path.exists(country_dir):
                        country_file = os.path.join(country_dir, f"{product}_{timestamp}.json")
                        with open(country_file, 'w', encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=2)
                        print(f"✅ {country}/{product}_{timestamp}.json 저장됨")
                
            except Exception as e:
                print(f"❌ 처리 실패 {cache_file}: {e}")
        
        # 통합 데이터 저장
        if all_regulations:
            # 통합 파일 저장
            combined_file = os.path.join(self.regulation_data_dir, "통합", f"all_regulations_{timestamp}.json")
            with open(combined_file, 'w', encoding='utf-8') as f:
                json.dump(all_regulations, f, ensure_ascii=False, indent=2)
            print(f"✅ 통합/all_regulations_{timestamp}.json 저장됨")
            
            # 최신 통합 파일 (항상 최신 버전 유지)
            latest_file = os.path.join(self.regulation_data_dir, "통합", "latest_regulations.json")
            with open(latest_file, 'w', encoding='utf-8') as f:
                json.dump(all_regulations, f, ensure_ascii=False, indent=2)
            print(f"✅ 통합/latest_regulations.json 업데이트됨")
            
            # 백업 생성
            backup_file = os.path.join(self.regulation_data_dir, "백업", f"backup_{timestamp}.json")
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(all_regulations, f, ensure_ascii=False, indent=2)
            print(f"✅ 백업/backup_{timestamp}.json 생성됨")
        
        print(f"\n📊 데이터 정리 완료!")
        print(f"📁 저장 위치: {self.regulation_data_dir}/")
        print(f"   🌍 국가별: {self.regulation_data_dir}/[국가명]/")
        print(f"   📋 통합: {self.regulation_data_dir}/통합/")
        print(f"   💾 백업: {self.regulation_data_dir}/백업/")
    
    def get_latest_regulations(self) -> Dict[str, Any]:
        """최신 규제 데이터 로드"""
        latest_file = os.path.join(self.regulation_data_dir, "통합", "latest_regulations.json")
        
        if not os.path.exists(latest_file):
            print("❌ 최신 규제 데이터 파일이 없습니다.")
            return {}
        
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ 최신 규제 데이터 로드됨 ({len(data)}개)")
            return data
        except Exception as e:
            print(f"❌ 최신 규제 데이터 로드 실패: {e}")
            return {}
    
    def get_country_regulations(self, country: str) -> Dict[str, Any]:
        """특정 국가의 규제 데이터 로드"""
        country_dir = os.path.join(self.regulation_data_dir, country)
        
        if not os.path.exists(country_dir):
            print(f"❌ {country}의 규제 데이터 폴더가 없습니다.")
            return {}
        
        country_files = [f for f in os.listdir(country_dir) if f.endswith('.json')]
        
        if not country_files:
            print(f"❌ {country}의 규제 데이터 파일이 없습니다.")
            return {}
        
        # 가장 최신 파일 찾기
        latest_file = max(country_files, key=lambda x: os.path.getctime(os.path.join(country_dir, x)))
        latest_path = os.path.join(country_dir, latest_file)
        
        try:
            with open(latest_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ {country} 규제 데이터 로드됨: {latest_file}")
            return data
        except Exception as e:
            print(f"❌ {country} 규제 데이터 로드 실패: {e}")
            return {}
    
    def get_product_regulations(self, product: str) -> Dict[str, Any]:
        """특정 제품의 규제 데이터 로드"""
        all_regulations = self.get_latest_regulations()
        
        if not all_regulations:
            return {}
        
        product_regulations = {k: v for k, v in all_regulations.items() if product in k}
        
        if not product_regulations:
            print(f"❌ {product}의 규제 데이터가 없습니다.")
            return {}
        
        print(f"✅ {product} 규제 데이터 로드됨 ({len(product_regulations)}개)")
        return product_regulations
    
    def list_available_data(self):
        """사용 가능한 데이터 목록 표시"""
        print("📋 사용 가능한 규제 데이터:")
        print("=" * 50)
        
        # 국가별 데이터
        for country in ["중국", "미국", "한국"]:
            country_dir = os.path.join(self.regulation_data_dir, country)
            if os.path.exists(country_dir):
                files = [f for f in os.listdir(country_dir) if f.endswith('.json')]
                if files:
                    latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(country_dir, x)))
                    print(f"🌍 {country}: {len(files)}개 파일 (최신: {latest_file})")
                else:
                    print(f"🌍 {country}: 데이터 없음")
            else:
                print(f"🌍 {country}: 폴더 없음")
        
        # 통합 데이터
        combined_dir = os.path.join(self.regulation_data_dir, "통합")
        if os.path.exists(combined_dir):
            files = [f for f in os.listdir(combined_dir) if f.endswith('.json')]
            if files:
                print(f"📋 통합: {len(files)}개 파일")
            else:
                print(f"📋 통합: 데이터 없음")
        else:
            print(f"📋 통합: 폴더 없음")
        
        # 백업 데이터
        backup_dir = os.path.join(self.regulation_data_dir, "백업")
        if os.path.exists(backup_dir):
            files = [f for f in os.listdir(backup_dir) if f.endswith('.json')]
            if files:
                print(f"💾 백업: {len(files)}개 파일")
            else:
                print(f"💾 백업: 데이터 없음")
        else:
            print(f"💾 백업: 폴더 없음")
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """오래된 데이터 정리"""
        print(f"🧹 {days_to_keep}일 이상 된 데이터 정리 중...")
        
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        total_removed = 0
        
        for subdir in ["중국", "미국", "한국", "통합", "백업"]:
            dir_path = os.path.join(self.regulation_data_dir, subdir)
            if not os.path.exists(dir_path):
                continue
            
            files = [f for f in os.listdir(dir_path) if f.endswith('.json')]
            
            for file in files:
                file_path = os.path.join(dir_path, file)
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                
                if file_time < cutoff_date and not file.startswith("latest_"):
                    try:
                        os.remove(file_path)
                        print(f"🗑️ 삭제됨: {subdir}/{file}")
                        total_removed += 1
                    except Exception as e:
                        print(f"❌ 삭제 실패 {subdir}/{file}: {e}")
        
        print(f"✅ 정리 완료! {total_removed}개 파일 삭제됨")
    
    def create_data_summary(self):
        """데이터 요약 정보 생성"""
        print("📊 규제 데이터 요약 정보 생성 중...")
        
        all_regulations = self.get_latest_regulations()
        
        if not all_regulations:
            print("❌ 요약할 데이터가 없습니다.")
            return
        
        summary = {
            "생성_시간": datetime.now().isoformat(),
            "총_규제_데이터_수": len(all_regulations),
            "국가별_통계": {},
            "제품별_통계": {},
            "데이터_상태": {}
        }
        
        countries = set()
        products = set()
        
        for key, data in all_regulations.items():
            country, product = key.split('_', 1)
            countries.add(country)
            products.add(product)
            
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
            
            # 데이터 상태
            if "추가정보" in data and "데이터_상태" in data["추가정보"]:
                summary["데이터_상태"][key] = data["추가정보"]["데이터_상태"]
        
        # 제품별 통계
        for product in products:
            summary["제품별_통계"][product] = {
                "지원_국가_수": len([k for k in all_regulations.keys() if product in k])
            }
        
        # 요약 파일 저장
        summary_file = os.path.join(self.regulation_data_dir, "data_summary.json")
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 데이터 요약 저장됨: {summary_file}")
        
        # 요약 출력
        print(f"\n📊 데이터 요약:")
        print(f"   총 규제 데이터: {summary['총_규제_데이터_수']}개")
        print(f"   지원 국가: {', '.join(countries)}")
        print(f"   지원 제품: {', '.join(products)}")
        
        for country, stats in summary["국가별_통계"].items():
            print(f"   {country}: {stats['제품_수']}개 제품, {stats['규제_항목_수']}개 항목")

def main():
    """메인 실행 함수"""
    manager = RegulationDataManager()
    
    print("📁 규제정보 데이터 관리 시스템")
    print("=" * 50)
    
    while True:
        print("\n📋 관리 옵션:")
        print("1. 캐시 데이터 정리 및 체계화")
        print("2. 사용 가능한 데이터 목록")
        print("3. 최신 규제 데이터 로드")
        print("4. 특정 국가 데이터 로드")
        print("5. 특정 제품 데이터 로드")
        print("6. 데이터 요약 생성")
        print("7. 오래된 데이터 정리")
        print("8. 종료")
        
        choice = input("\n선택 (1-8): ").strip()
        
        if choice == "1":
            manager.organize_cached_data()
        
        elif choice == "2":
            manager.list_available_data()
        
        elif choice == "3":
            data = manager.get_latest_regulations()
            if data:
                print(f"📊 최신 데이터 키: {list(data.keys())}")
        
        elif choice == "4":
            countries = ["중국", "미국", "한국"]
            print(f"🌍 사용 가능한 국가: {', '.join(countries)}")
            country = input("국가명을 입력하세요: ").strip()
            if country in countries:
                data = manager.get_country_regulations(country)
                if data:
                    print(f"📊 {country} 데이터 키: {list(data.keys())}")
            else:
                print(f"❌ {country}는 지원하지 않습니다.")
        
        elif choice == "5":
            products = ["라면"]
            print(f"📦 사용 가능한 제품: {', '.join(products)}")
            product = input("제품명을 입력하세요: ").strip()
            if product in products:
                data = manager.get_product_regulations(product)
                if data:
                    print(f"📊 {product} 데이터 키: {list(data.keys())}")
            else:
                print(f"❌ {product}는 지원하지 않습니다.")
        
        elif choice == "6":
            manager.create_data_summary()
        
        elif choice == "7":
            days = input("몇 일 이상 된 데이터를 삭제할까요? (기본: 30): ").strip()
            try:
                days = int(days) if days else 30
                manager.cleanup_old_data(days)
            except ValueError:
                print("❌ 올바른 숫자를 입력하세요.")
        
        elif choice == "8":
            print("👋 데이터 관리 시스템을 종료합니다.")
            break
        
        else:
            print("❌ 잘못된 선택입니다.")
        
        input("\n계속하려면 Enter를 누르세요...")

if __name__ == "__main__":
    main() 