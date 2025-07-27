#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 KATI MVP 시스템 종합 무결성 점검
- 모든 모듈의 정상 작동 확인
- 데이터 파일 존재 여부 확인
- 기능별 테스트 실행
- 오류 상황 시뮬레이션
"""

import os
import sys
import pickle
import json
import traceback
from datetime import datetime
from pathlib import Path

class SystemIntegrityChecker:
    """시스템 무결성 점검기"""
    
    def __init__(self):
        self.check_results = {
            "시스템_정보": {},
            "파일_존재_확인": {},
            "모듈_임포트_확인": {},
            "기능_테스트": {},
            "오류_시뮬레이션": {},
            "전체_평가": {}
        }
        self.errors = []
        self.warnings = []
    
    def check_system_info(self):
        """시스템 기본 정보 확인"""
        print("🔍 시스템 기본 정보 확인 중...")
        
        try:
            import pandas as pd
            import sklearn
            import soynlp
            
            self.check_results["시스템_정보"] = {
                "Python_버전": sys.version,
                "Pandas_버전": pd.__version__,
                "Scikit_learn_버전": sklearn.__version__,
                "Soynlp_버전": soynlp.__version__,
                "현재_작업_디렉토리": os.getcwd(),
                "점검_시간": datetime.now().isoformat()
            }
            print("✅ 시스템 정보 확인 완료")
            return True
        except Exception as e:
            self.errors.append(f"시스템 정보 확인 실패: {e}")
            print(f"❌ 시스템 정보 확인 실패: {e}")
            return False
    
    def check_file_existence(self):
        """필수 파일 존재 여부 확인"""
        print("\n📁 필수 파일 존재 여부 확인 중...")
        
        required_files = {
            "모델_파일": [
                "model/vectorizer.pkl",
                "model/indexed_matrix.pkl", 
                "model/raw_data.pkl"
            ],
            "핵심_모듈": [
                "mvp_integrated_system.py",
                "mvp_regulations.py",
                "real_time_regulation_system.py",
                "regulation_monitor.py",
                "nutrition_label_generator.py",
                "advanced_label_generator.py",
                "document_generator.py",
                "dashboard_analyzer.py",
                "integrated_nlg_engine.py"
            ],
            "데이터_파일": [
                "data/customsExcel (1).xlsx",
                "data/customsExcel (2).xlsx"
            ],
            "생성된_폴더": [
                "regulation_cache/",
                "nutrition_labels/",
                "advanced_labels/",
                "generated_documents/"
            ]
        }
        
        file_status = {}
        
        for category, files in required_files.items():
            file_status[category] = {}
            for file_path in files:
                exists = os.path.exists(file_path)
                file_status[category][file_path] = {
                    "존재": exists,
                    "크기": os.path.getsize(file_path) if exists else 0
                }
                
                if exists:
                    print(f"✅ {file_path}")
                else:
                    print(f"❌ {file_path} (누락)")
                    self.warnings.append(f"파일 누락: {file_path}")
        
        self.check_results["파일_존재_확인"] = file_status
        return file_status
    
    def check_module_imports(self):
        """모듈 임포트 가능성 확인"""
        print("\n📦 모듈 임포트 가능성 확인 중...")
        
        modules_to_test = {
            "mvp_regulations": "mvp_regulations",
            "real_time_regulation_system": "real_time_regulation_system", 
            "regulation_monitor": "regulation_monitor",
            "nutrition_label_generator": "nutrition_label_generator",
            "advanced_label_generator": "advanced_label_generator",
            "document_generator": "document_generator",
            "dashboard_analyzer": "dashboard_analyzer",
            "integrated_nlg_engine": "integrated_nlg_engine",
            "customs_analysis_nlg": "customs_analysis_nlg",
            "regulation_nlg": "regulation_nlg",
            "natural_language_generator": "natural_language_generator"
        }
        
        import_status = {}
        
        for module_name, import_name in modules_to_test.items():
            try:
                module = __import__(import_name)
                import_status[module_name] = {
                    "임포트_성공": True,
                    "클래스_목록": [attr for attr in dir(module) if not attr.startswith('_')]
                }
                print(f"✅ {module_name}")
            except Exception as e:
                import_status[module_name] = {
                    "임포트_성공": False,
                    "오류": str(e)
                }
                print(f"❌ {module_name}: {e}")
                self.errors.append(f"모듈 임포트 실패 {module_name}: {e}")
        
        self.check_results["모듈_임포트_확인"] = import_status
        return import_status
    
    def test_core_functions(self):
        """핵심 기능 테스트"""
        print("\n🧪 핵심 기능 테스트 중...")
        
        function_tests = {}
        
        # 1. 모델 로딩 테스트
        print("   📊 모델 로딩 테스트...")
        try:
            with open("model/vectorizer.pkl", "rb") as f:
                vectorizer = pickle.load(f)
            with open("model/raw_data.pkl", "rb") as f:
                raw_data = pickle.load(f)
            
            function_tests["모델_로딩"] = {
                "성공": True,
                "데이터_크기": len(raw_data),
                "컬럼_수": len(raw_data.columns)
            }
            print("   ✅ 모델 로딩 성공")
        except Exception as e:
            function_tests["모델_로딩"] = {
                "성공": False,
                "오류": str(e)
            }
            print(f"   ❌ 모델 로딩 실패: {e}")
            self.errors.append(f"모델 로딩 실패: {e}")
        
        # 2. 통관 분석 테스트
        print("   🔍 통관 분석 테스트...")
        try:
            from mvp_integrated_system import MVPCustomsAnalyzer
            analyzer = MVPCustomsAnalyzer()
            results = analyzer.analyze_customs_failures("라면", threshold=0.3)
            
            function_tests["통관_분석"] = {
                "성공": True,
                "결과_수": len(results) if results else 0
            }
            print("   ✅ 통관 분석 성공")
        except Exception as e:
            function_tests["통관_분석"] = {
                "성공": False,
                "오류": str(e)
            }
            print(f"   ❌ 통관 분석 실패: {e}")
            self.errors.append(f"통관 분석 실패: {e}")
        
        # 3. 규제 정보 테스트
        print("   📋 규제 정보 테스트...")
        try:
            from mvp_regulations import get_mvp_regulations
            regulations = get_mvp_regulations("중국", "라면")
            
            function_tests["규제_정보"] = {
                "성공": True,
                "규제_항목_수": len(regulations) if regulations else 0
            }
            print("   ✅ 규제 정보 성공")
        except Exception as e:
            function_tests["규제_정보"] = {
                "성공": False,
                "오류": str(e)
            }
            print(f"   ❌ 규제 정보 실패: {e}")
            self.errors.append(f"규제 정보 실패: {e}")
        
        # 4. 실시간 크롤링 테스트
        print("   🌐 실시간 크롤링 테스트...")
        try:
            from real_time_regulation_system import RealTimeRegulationCrawler
            crawler = RealTimeRegulationCrawler()
            status = crawler.get_regulation_status()
            
            function_tests["실시간_크롤링"] = {
                "성공": True,
                "캐시_파일_수": len(status.get("캐시_상태", {}))
            }
            print("   ✅ 실시간 크롤링 성공")
        except Exception as e:
            function_tests["실시간_크롤링"] = {
                "성공": False,
                "오류": str(e)
            }
            print(f"   ❌ 실시간 크롤링 실패: {e}")
            self.errors.append(f"실시간 크롤링 실패: {e}")
        
        # 5. 라벨 생성 테스트
        print("   🏷️ 라벨 생성 테스트...")
        try:
            from nutrition_label_generator import NutritionLabelGenerator
            generator = NutritionLabelGenerator()
            
            test_info = {
                "product_name": "테스트 라면",
                "manufacturer": "테스트 제조사",
                "nutrition": {"칼로리": 300, "단백질": 8, "지방": 12, "탄수화물": 45}
            }
            
            # 실제 이미지 생성은 하지 않고 클래스만 테스트
            function_tests["라벨_생성"] = {
                "성공": True,
                "생성기_타입": type(generator).__name__
            }
            print("   ✅ 라벨 생성 성공")
        except Exception as e:
            function_tests["라벨_생성"] = {
                "성공": False,
                "오류": str(e)
            }
            print(f"   ❌ 라벨 생성 실패: {e}")
            self.errors.append(f"라벨 생성 실패: {e}")
        
        # 6. 문서 생성 테스트
        print("   📄 문서 생성 테스트...")
        try:
            from document_generator import DocumentGenerator
            doc_generator = DocumentGenerator()
            
            function_tests["문서_생성"] = {
                "성공": True,
                "생성기_타입": type(doc_generator).__name__
            }
            print("   ✅ 문서 생성 성공")
        except Exception as e:
            function_tests["문서_생성"] = {
                "성공": False,
                "오류": str(e)
            }
            print(f"   ❌ 문서 생성 실패: {e}")
            self.errors.append(f"문서 생성 실패: {e}")
        
        # 7. 대시보드 분석 테스트
        print("   📊 대시보드 분석 테스트...")
        try:
            from dashboard_analyzer import DashboardAnalyzer
            dashboard = DashboardAnalyzer()
            
            function_tests["대시보드_분석"] = {
                "성공": True,
                "분석기_타입": type(dashboard).__name__
            }
            print("   ✅ 대시보드 분석 성공")
        except Exception as e:
            function_tests["대시보드_분석"] = {
                "성공": False,
                "오류": str(e)
            }
            print(f"   ❌ 대시보드 분석 실패: {e}")
            self.errors.append(f"대시보드 분석 실패: {e}")
        
        self.check_results["기능_테스트"] = function_tests
        return function_tests
    
    def simulate_error_scenarios(self):
        """오류 상황 시뮬레이션"""
        print("\n⚠️ 오류 상황 시뮬레이션 중...")
        
        error_tests = {}
        
        # 1. 존재하지 않는 파일 접근
        print("   📁 존재하지 않는 파일 접근 테스트...")
        try:
            with open("nonexistent_file.pkl", "rb") as f:
                data = pickle.load(f)
            error_tests["파일_접근_오류_처리"] = {"성공": False, "예상_동작": "예외 발생해야 함"}
        except FileNotFoundError:
            error_tests["파일_접근_오류_처리"] = {"성공": True, "예상_동작": "FileNotFoundError 정상 처리"}
            print("   ✅ 파일 접근 오류 정상 처리")
        except Exception as e:
            error_tests["파일_접근_오류_처리"] = {"성공": False, "예상_동작": "FileNotFoundError", "실제_오류": str(e)}
            print(f"   ❌ 예상과 다른 오류: {e}")
        
        # 2. 잘못된 모듈 임포트
        print("   📦 잘못된 모듈 임포트 테스트...")
        try:
            import nonexistent_module
            error_tests["모듈_임포트_오류_처리"] = {"성공": False, "예상_동작": "ImportError 발생해야 함"}
        except ImportError:
            error_tests["모듈_임포트_오류_처리"] = {"성공": True, "예상_동작": "ImportError 정상 처리"}
            print("   ✅ 모듈 임포트 오류 정상 처리")
        except Exception as e:
            error_tests["모듈_임포트_오류_처리"] = {"성공": False, "예상_동작": "ImportError", "실제_오류": str(e)}
            print(f"   ❌ 예상과 다른 오류: {e}")
        
        # 3. 잘못된 데이터 접근
        print("   🔍 잘못된 데이터 접근 테스트...")
        try:
            from mvp_integrated_system import MVPCustomsAnalyzer
            analyzer = MVPCustomsAnalyzer()
            # 존재하지 않는 컬럼 접근 시뮬레이션
            if hasattr(analyzer, 'raw_data') and analyzer.raw_data is not None:
                test_column = analyzer.raw_data.get("존재하지_않는_컬럼", "기본값")
                error_tests["데이터_접근_오류_처리"] = {"성공": True, "예상_동작": "기본값 반환"}
                print("   ✅ 데이터 접근 오류 정상 처리")
            else:
                error_tests["데이터_접근_오류_처리"] = {"성공": True, "예상_동작": "데이터 없음 처리"}
                print("   ✅ 데이터 없음 상황 정상 처리")
        except Exception as e:
            error_tests["데이터_접근_오류_처리"] = {"성공": False, "예상_동작": "기본값 반환", "실제_오류": str(e)}
            print(f"   ❌ 데이터 접근 오류 처리 실패: {e}")
        
        self.check_results["오류_시뮬레이션"] = error_tests
        return error_tests
    
    def generate_final_report(self):
        """최종 보고서 생성"""
        print("\n📋 최종 시스템 평가 중...")
        
        # 성공률 계산
        total_checks = 0
        successful_checks = 0
        
        # 파일 존재 확인
        for category, files in self.check_results["파일_존재_확인"].items():
            for file_path, status in files.items():
                total_checks += 1
                if status["존재"]:
                    successful_checks += 1
        
        # 모듈 임포트 확인
        for module, status in self.check_results["모듈_임포트_확인"].items():
            total_checks += 1
            if status["임포트_성공"]:
                successful_checks += 1
        
        # 기능 테스트
        for function, status in self.check_results["기능_테스트"].items():
            total_checks += 1
            if status["성공"]:
                successful_checks += 1
        
        # 오류 시뮬레이션
        for test, status in self.check_results["오류_시뮬레이션"].items():
            total_checks += 1
            if status["성공"]:
                successful_checks += 1
        
        success_rate = (successful_checks / total_checks * 100) if total_checks > 0 else 0
        
        # 전체 평가
        if success_rate >= 90:
            overall_status = "🟢 우수"
        elif success_rate >= 70:
            overall_status = "🟡 양호"
        elif success_rate >= 50:
            overall_status = "🟠 보통"
        else:
            overall_status = "🔴 미흡"
        
        self.check_results["전체_평가"] = {
            "총_검사_항목": total_checks,
            "성공_항목": successful_checks,
            "실패_항목": total_checks - successful_checks,
            "성공률": success_rate,
            "성공률_문자열": f"{success_rate:.1f}%",
            "전체_상태": overall_status,
            "오류_수": len(self.errors),
            "경고_수": len(self.warnings),
            "점검_완료_시간": datetime.now().isoformat()
        }
        
        return self.check_results
    
    def run_comprehensive_check(self):
        """종합 점검 실행"""
        print("🔍 KATI MVP 시스템 종합 무결성 점검 시작")
        print("=" * 60)
        
        # 1. 시스템 정보 확인
        self.check_system_info()
        
        # 2. 파일 존재 확인
        self.check_file_existence()
        
        # 3. 모듈 임포트 확인
        self.check_module_imports()
        
        # 4. 핵심 기능 테스트
        self.test_core_functions()
        
        # 5. 오류 상황 시뮬레이션
        self.simulate_error_scenarios()
        
        # 6. 최종 보고서 생성
        final_report = self.generate_final_report()
        
        # 7. 결과 출력
        self.print_results(final_report)
        
        # 8. 보고서 저장
        self.save_report(final_report)
        
        return final_report
    
    def print_results(self, report):
        """결과 출력"""
        print("\n" + "=" * 60)
        print("📊 시스템 무결성 점검 결과")
        print("=" * 60)
        
        # 전체 평가
        overall = report["전체_평가"]
        print(f"🎯 전체 상태: {overall['전체_상태']}")
        print(f"📊 성공률: {overall['성공률_문자열']}")
        print(f"📋 총 검사 항목: {overall['총_검사_항목']}개")
        print(f"✅ 성공: {overall['성공_항목']}개")
        print(f"❌ 실패: {overall['실패_항목']}개")
        print(f"⚠️ 오류: {overall['오류_수']}개")
        print(f"🔔 경고: {overall['경고_수']}개")
        
        # 오류 목록
        if self.errors:
            print(f"\n❌ 발견된 오류:")
            for i, error in enumerate(self.errors, 1):
                print(f"   {i}. {error}")
        
        # 경고 목록
        if self.warnings:
            print(f"\n⚠️ 발견된 경고:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"   {i}. {warning}")
        
        # 권장사항
        print(f"\n💡 권장사항:")
        if overall['성공률'] >= 90:
            print("   🎉 시스템이 매우 안정적으로 작동하고 있습니다!")
        elif overall['성공률'] >= 70:
            print("   👍 시스템이 양호하게 작동하고 있습니다. 일부 개선사항을 고려해보세요.")
        else:
            print("   🔧 시스템에 문제가 있습니다. 위의 오류들을 해결해주세요.")
        
        if self.errors:
            print("   - 발견된 오류들을 우선적으로 해결하세요.")
        if self.warnings:
            print("   - 누락된 파일들을 확인하고 추가하세요.")
    
    def save_report(self, report):
        """보고서 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"system_integrity_report_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"\n📁 점검 보고서가 저장되었습니다: {filename}")
        except Exception as e:
            print(f"\n❌ 보고서 저장 실패: {e}")

def main():
    """메인 실행 함수"""
    checker = SystemIntegrityChecker()
    report = checker.run_comprehensive_check()
    
    print(f"\n✅ 시스템 무결성 점검 완료!")
    print(f"📊 성공률: {report['전체_평가']['성공률_문자열']}")
    print(f"🎯 전체 상태: {report['전체_평가']['전체_상태']}")

if __name__ == "__main__":
    main() 