import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import time
import re
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TradeStatistics:
    """수출입 통계 데이터 구조"""
    country: str
    hs_code: str
    period: str
    export_amount: float
    import_amount: float
    trade_balance: float
    issue_count: int
    major_issues: List[str]
    trend_summary: str
    data_points: List[Dict]
    created_at: str

class KOTRATradeStatisticsCrawler:
    """KOTRA 빅데이터 시각화 사이트 수출입 통계 크롤러"""
    
    def __init__(self):
        self.base_url = "https://www.kotra.or.kr/bigdata/bhrcMarket"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # 지원 국가 및 HS CODE 매핑
        self.country_mapping = {
            "중국": "CN",
            "미국": "US"
        }
        
        # 주요 HS CODE (식품 관련)
        self.common_hs_codes = {
            "라면": "190230",
            "과자": "190531",
            "음료": "220210",
            "조미료": "210390",
            "건조식품": "071290"
        }
        
        # 캐시 디렉토리
        self.cache_dir = "trade_statistics_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        
        logger.info("✅ KOTRA 수출입 통계 크롤러 초기화 완료")
    
    def get_trade_statistics(self, country: str, hs_code: str, period: str) -> Optional[TradeStatistics]:
        """특정 국가, HS CODE, 기간의 수출입 통계 조회"""
        try:
            logger.info(f"🔍 {country} {hs_code} {period} 수출입 통계 조회 시작")
            
            # 캐시 확인
            cache_key = f"{country}_{hs_code}_{period}"
            cached_data = self._load_from_cache(cache_key)
            if cached_data:
                logger.info(f"✅ 캐시된 데이터 사용: {cache_key}")
                return cached_data
            
            # Selenium을 사용한 동적 크롤링
            statistics = self._crawl_with_selenium(country, hs_code, period)
            
            if statistics:
                # 캐시 저장
                self._save_to_cache(cache_key, statistics)
                logger.info(f"✅ {country} {hs_code} {period} 통계 조회 완료")
                return statistics
            else:
                logger.warning(f"⚠️ {country} {hs_code} {period} 통계 데이터 없음")
                return None
                
        except Exception as e:
            logger.error(f"❌ 수출입 통계 조회 중 오류: {str(e)}")
            return None
    
    def _crawl_with_selenium(self, country: str, hs_code: str, period: str) -> Optional[TradeStatistics]:
        """Selenium을 사용한 동적 크롤링"""
        driver = None
        try:
            # Chrome 옵션 설정
            chrome_options = Options()
            chrome_options.add_argument("--headless")  # 헤드리스 모드
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(self.base_url)
            
            # 페이지 로딩 대기
            wait = WebDriverWait(driver, 10)
            
            # 국가 선택
            country_code = self.country_mapping.get(country)
            if not country_code:
                logger.error(f"❌ 지원하지 않는 국가: {country}")
                return None
            
            # HS CODE 입력
            hs_input = wait.until(EC.presence_of_element_located((By.NAME, "hsCode")))
            hs_input.clear()
            hs_input.send_keys(hs_code)
            
            # 기간 설정
            period_data = self._parse_period(period)
            if period_data:
                start_date = driver.find_element(By.NAME, "startDate")
                end_date = driver.find_element(By.NAME, "endDate")
                start_date.clear()
                start_date.send_keys(period_data['start'])
                end_date.clear()
                end_date.send_keys(period_data['end'])
            
            # 검색 버튼 클릭
            search_button = driver.find_element(By.XPATH, "//button[contains(text(), '검색')]")
            search_button.click()
            
            # 결과 로딩 대기
            time.sleep(3)
            
            # 통계 데이터 추출
            statistics = self._extract_statistics_data(driver, country, hs_code, period)
            
            return statistics
            
        except TimeoutException:
            logger.error("❌ 페이지 로딩 시간 초과")
            return None
        except Exception as e:
            logger.error(f"❌ Selenium 크롤링 중 오류: {str(e)}")
            return None
        finally:
            if driver:
                driver.quit()
    
    def _extract_statistics_data(self, driver, country: str, hs_code: str, period: str) -> Optional[TradeStatistics]:
        """웹페이지에서 통계 데이터 추출"""
        try:
            # 수출입 금액 추출
            export_amount = self._extract_amount(driver, "export")
            import_amount = self._extract_amount(driver, "import")
            trade_balance = export_amount - import_amount
            
            # 주요 이슈 추출
            major_issues = self._extract_major_issues(driver)
            issue_count = len(major_issues)
            
            # 시계열 데이터 포인트 추출
            data_points = self._extract_time_series_data(driver)
            
            # 트렌드 요약 생성
            trend_summary = self._generate_trend_summary(data_points, export_amount, import_amount)
            
            statistics = TradeStatistics(
                country=country,
                hs_code=hs_code,
                period=period,
                export_amount=export_amount,
                import_amount=import_amount,
                trade_balance=trade_balance,
                issue_count=issue_count,
                major_issues=major_issues,
                trend_summary=trend_summary,
                data_points=data_points,
                created_at=datetime.now().isoformat()
            )
            
            return statistics
            
        except Exception as e:
            logger.error(f"❌ 통계 데이터 추출 중 오류: {str(e)}")
            return None
    
    def _extract_amount(self, driver, trade_type: str) -> float:
        """수출/수입 금액 추출"""
        try:
            # 실제 웹사이트 구조에 맞게 선택자 수정 필요
            if trade_type == "export":
                selector = "//div[contains(@class, 'export-amount')]//span[@class='value']"
            else:
                selector = "//div[contains(@class, 'import-amount')]//span[@class='value']"
            
            element = driver.find_element(By.XPATH, selector)
            amount_text = element.text.strip()
            
            # 숫자만 추출 (콤마, 원화 기호 등 제거)
            amount = re.sub(r'[^\d.]', '', amount_text)
            return float(amount) if amount else 0.0
            
        except NoSuchElementException:
            logger.warning(f"⚠️ {trade_type} 금액 요소를 찾을 수 없음")
            return 0.0
        except Exception as e:
            logger.error(f"❌ {trade_type} 금액 추출 중 오류: {str(e)}")
            return 0.0
    
    def _extract_major_issues(self, driver) -> List[str]:
        """주요 통관 이슈 추출"""
        issues = []
        try:
            # 실제 웹사이트 구조에 맞게 선택자 수정 필요
            issue_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'issue-item')]")
            
            for element in issue_elements[:5]:  # 상위 5개 이슈만
                issue_text = element.text.strip()
                if issue_text:
                    issues.append(issue_text)
            
        except Exception as e:
            logger.error(f"❌ 주요 이슈 추출 중 오류: {str(e)}")
        
        return issues
    
    def _extract_time_series_data(self, driver) -> List[Dict]:
        """시계열 데이터 포인트 추출"""
        data_points = []
        try:
            # 실제 웹사이트 구조에 맞게 선택자 수정 필요
            chart_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'chart-data-point')]")
            
            for element in chart_elements:
                try:
                    date = element.get_attribute("data-date")
                    export_val = element.get_attribute("data-export")
                    import_val = element.get_attribute("data-import")
                    
                    if date and export_val and import_val:
                        data_points.append({
                            "date": date,
                            "export": float(export_val),
                            "import": float(import_val),
                            "balance": float(export_val) - float(import_val)
                        })
                except Exception as e:
                    logger.warning(f"⚠️ 데이터 포인트 파싱 실패: {str(e)}")
                    continue
            
        except Exception as e:
            logger.error(f"❌ 시계열 데이터 추출 중 오류: {str(e)}")
        
        return data_points
    
    def _generate_trend_summary(self, data_points: List[Dict], export_amount: float, import_amount: float) -> str:
        """트렌드 요약 생성"""
        if not data_points:
            return "데이터 부족으로 트렌드 분석 불가"
        
        try:
            # 최근 3개월 데이터로 트렌드 분석
            recent_data = data_points[-3:] if len(data_points) >= 3 else data_points
            
            export_trend = "증가" if recent_data[-1]["export"] > recent_data[0]["export"] else "감소"
            import_trend = "증가" if recent_data[-1]["import"] > recent_data[0]["import"] else "감소"
            
            balance_trend = "흑자" if export_amount > import_amount else "적자"
            
            summary = f"수출은 {export_trend} 추세, 수입은 {import_trend} 추세이며, {balance_trend} 상태입니다."
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ 트렌드 요약 생성 중 오류: {str(e)}")
            return "트렌드 분석 중 오류 발생"
    
    def _parse_period(self, period: str) -> Optional[Dict]:
        """기간 문자열 파싱"""
        try:
            # "2025년 1분기" 형식 파싱
            year_match = re.search(r'(\d{4})년', period)
            quarter_match = re.search(r'(\d+)분기', period)
            
            if year_match and quarter_match:
                year = int(year_match.group(1))
                quarter = int(quarter_match.group(1))
                
                # 분기별 시작/종료 월 계산
                start_month = (quarter - 1) * 3 + 1
                end_month = quarter * 3
                
                start_date = f"{year:04d}-{start_month:02d}-01"
                end_date = f"{year:04d}-{end_month:02d}-28"  # 간단히 28일로 설정
                
                return {
                    "start": start_date,
                    "end": end_date
                }
            
            return None
            
        except Exception as e:
            logger.error(f"❌ 기간 파싱 중 오류: {str(e)}")
            return None
    
    def _save_to_cache(self, key: str, data: TradeStatistics):
        """캐시에 데이터 저장"""
        try:
            cache_file = os.path.join(self.cache_dir, f"{key}.json")
            
            # dataclass를 dict로 변환
            cache_data = {
                "country": data.country,
                "hs_code": data.hs_code,
                "period": data.period,
                "export_amount": data.export_amount,
                "import_amount": data.import_amount,
                "trade_balance": data.trade_balance,
                "issue_count": data.issue_count,
                "major_issues": data.major_issues,
                "trend_summary": data.trend_summary,
                "data_points": data.data_points,
                "created_at": data.created_at
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ 캐시 저장 완료: {cache_file}")
            
        except Exception as e:
            logger.error(f"❌ 캐시 저장 중 오류: {str(e)}")
    
    def _load_from_cache(self, key: str) -> Optional[TradeStatistics]:
        """캐시에서 데이터 로드"""
        try:
            cache_file = os.path.join(self.cache_dir, f"{key}.json")
            
            if not os.path.exists(cache_file):
                return None
            
            # 캐시 만료 확인 (24시간)
            file_time = os.path.getmtime(cache_file)
            if time.time() - file_time > 86400:  # 24시간
                logger.info(f"🔄 캐시 만료: {cache_file}")
                return None
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # dict를 dataclass로 변환
            statistics = TradeStatistics(
                country=cache_data["country"],
                hs_code=cache_data["hs_code"],
                period=cache_data["period"],
                export_amount=cache_data["export_amount"],
                import_amount=cache_data["import_amount"],
                trade_balance=cache_data["trade_balance"],
                issue_count=cache_data["issue_count"],
                major_issues=cache_data["major_issues"],
                trend_summary=cache_data["trend_summary"],
                data_points=cache_data["data_points"],
                created_at=cache_data["created_at"]
            )
            
            logger.info(f"✅ 캐시 로드 완료: {cache_file}")
            return statistics
            
        except Exception as e:
            logger.error(f"❌ 캐시 로드 중 오류: {str(e)}")
            return None
    
    def generate_db_table_data(self, statistics: TradeStatistics) -> Dict:
        """DB 적재용 테이블 형태 데이터 생성"""
        try:
            db_data = {
                "table_name": "trade_statistics",
                "columns": [
                    "country", "hs_code", "period", "export_amount", 
                    "import_amount", "trade_balance", "issue_count",
                    "major_issues", "trend_summary", "created_at"
                ],
                "data": [
                    {
                        "country": statistics.country,
                        "hs_code": statistics.hs_code,
                        "period": statistics.period,
                        "export_amount": statistics.export_amount,
                        "import_amount": statistics.import_amount,
                        "trade_balance": statistics.trade_balance,
                        "issue_count": statistics.issue_count,
                        "major_issues": json.dumps(statistics.major_issues, ensure_ascii=False),
                        "trend_summary": statistics.trend_summary,
                        "created_at": statistics.created_at
                    }
                ],
                "time_series_table": {
                    "table_name": "trade_statistics_time_series",
                    "columns": ["country", "hs_code", "period", "date", "export", "import", "balance"],
                    "data": [
                        {
                            "country": statistics.country,
                            "hs_code": statistics.hs_code,
                            "period": statistics.period,
                            "date": point["date"],
                            "export": point["export"],
                            "import": point["import"],
                            "balance": point["balance"]
                        }
                        for point in statistics.data_points
                    ]
                }
            }
            
            return db_data
            
        except Exception as e:
            logger.error(f"❌ DB 테이블 데이터 생성 중 오류: {str(e)}")
            return {}
    
    def generate_visualization_data(self, statistics: TradeStatistics) -> Dict:
        """시각화용 그래프 데이터 생성"""
        try:
            viz_data = {
                "summary": {
                    "export_amount": statistics.export_amount,
                    "import_amount": statistics.import_amount,
                    "trade_balance": statistics.trade_balance,
                    "issue_count": statistics.issue_count
                },
                "trend_summary": statistics.trend_summary,
                "time_series": {
                    "labels": [point["date"] for point in statistics.data_points],
                    "export_data": [point["export"] for point in statistics.data_points],
                    "import_data": [point["import"] for point in statistics.data_points],
                    "balance_data": [point["balance"] for point in statistics.data_points]
                },
                "major_issues": statistics.major_issues
            }
            
            return viz_data
            
        except Exception as e:
            logger.error(f"❌ 시각화 데이터 생성 중 오류: {str(e)}")
            return {}
    
    def get_api_status(self) -> Dict:
        """API 상태 확인"""
        return {
            "service_available": True,
            "supported_countries": list(self.country_mapping.keys()),
            "common_hs_codes": self.common_hs_codes,
            "cache_directory": self.cache_dir,
            "last_update": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "api_connection": "initialized"
        }

# 사용 예시
if __name__ == "__main__":
    crawler = KOTRATradeStatisticsCrawler()
    
    # 테스트 실행
    statistics = crawler.get_trade_statistics("중국", "190230", "2025년 1분기")
    
    if statistics:
        print(f"✅ 통계 조회 성공: {statistics.country} {statistics.hs_code}")
        print(f"수출액: {statistics.export_amount:,.0f}")
        print(f"수입액: {statistics.import_amount:,.0f}")
        print(f"무역수지: {statistics.trade_balance:,.0f}")
        print(f"주요 이슈: {len(statistics.major_issues)}개")
        print(f"트렌드: {statistics.trend_summary}")
        
        # DB 테이블 데이터 생성
        db_data = crawler.generate_db_table_data(statistics)
        print(f"DB 테이블 데이터 생성 완료: {len(db_data.get('data', []))}개 행")
        
        # 시각화 데이터 생성
        viz_data = crawler.generate_visualization_data(statistics)
        print(f"시각화 데이터 생성 완료: {len(viz_data.get('time_series', {}).get('labels', []))}개 데이터 포인트")
    else:
        print("❌ 통계 조회 실패") 