#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📊 실시간 규제 모니터링 대시보드
- 실시간 규제 데이터 상태 모니터링
- 자동 업데이트 알림
- 규제 변경 감지
- 웹 대시보드 (향후 확장)
"""

import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
from pathlib import Path
from real_time_regulation_system import RealTimeRegulationCrawler

class RegulationMonitor:
    """실시간 규제 모니터링 시스템"""
    
    def __init__(self):
        self.crawler = RealTimeRegulationCrawler()
        self.monitoring_active = False
        self.alert_history = []
        self.change_history = []
        
        # 모니터링 설정
        self.monitoring_config = {
            "update_interval": 3600,  # 1시간마다 체크
            "alert_threshold": 7200,  # 2시간 이상 지연시 알림
            "countries": ["중국", "미국", "한국"],
            "products": ["라면"]
        }
    
    def start_monitoring(self):
        """모니터링 시작"""
        print("📊 실시간 규제 모니터링 시작...")
        self.monitoring_active = True
        
        # 모니터링 스레드 시작
        monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        monitor_thread.start()
        
        print("✅ 모니터링이 시작되었습니다.")
        print(f"   📅 체크 주기: {self.monitoring_config['update_interval']}초")
        print(f"   🚨 알림 임계값: {self.monitoring_config['alert_threshold']}초")
        print(f"   🌍 모니터링 국가: {', '.join(self.monitoring_config['countries'])}")
    
    def stop_monitoring(self):
        """모니터링 중지"""
        print("🛑 실시간 규제 모니터링 중지...")
        self.monitoring_active = False
        print("✅ 모니터링이 중지되었습니다.")
    
    def _monitoring_loop(self):
        """모니터링 루프"""
        while self.monitoring_active:
            try:
                # 현재 상태 체크
                self._check_regulation_status()
                
                # 설정된 간격만큼 대기
                time.sleep(self.monitoring_config["update_interval"])
                
            except Exception as e:
                print(f"❌ 모니터링 오류: {e}")
                time.sleep(60)  # 오류 시 1분 대기
    
    def _check_regulation_status(self):
        """규제 상태 체크"""
        current_time = datetime.now()
        print(f"\n🕐 규제 상태 체크: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        status = self.crawler.get_regulation_status()
        
        for country in self.monitoring_config["countries"]:
            cache_info = status["캐시_상태"].get(country, {})
            
            if cache_info.get("파일_존재"):
                file_age_hours = cache_info.get("파일_나이_시간", 0)
                file_age_seconds = file_age_hours * 3600
                
                # 알림 임계값 체크
                if file_age_seconds > self.monitoring_config["alert_threshold"]:
                    alert_msg = f"🚨 {country} 규제 데이터가 {file_age_hours:.1f}시간 전 업데이트되었습니다!"
                    self._add_alert(country, alert_msg, "지연")
                    print(alert_msg)
                else:
                    print(f"✅ {country}: {file_age_hours:.1f}시간 전 업데이트 (정상)")
            else:
                alert_msg = f"🚨 {country} 규제 데이터가 없습니다!"
                self._add_alert(country, alert_msg, "누락")
                print(alert_msg)
    
    def _add_alert(self, country: str, message: str, alert_type: str):
        """알림 추가"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "country": country,
            "message": message,
            "type": alert_type
        }
        self.alert_history.append(alert)
        
        # 알림 히스토리 최대 100개 유지
        if len(self.alert_history) > 100:
            self.alert_history = self.alert_history[-100:]
    
    def get_monitoring_dashboard(self) -> Dict:
        """모니터링 대시보드 데이터 반환"""
        
        status = self.crawler.get_regulation_status()
        current_time = datetime.now()
        
        dashboard = {
            "모니터링_상태": {
                "활성화": self.monitoring_active,
                "마지막_체크": current_time.isoformat(),
                "체크_주기": f"{self.monitoring_config['update_interval']}초",
                "알림_임계값": f"{self.monitoring_config['alert_threshold']}초"
            },
            "국가별_상태": {},
            "알림_요약": {
                "총_알림": len(self.alert_history),
                "최근_알림": self.alert_history[-5:] if self.alert_history else [],
                "알림_타입별": self._count_alert_types()
            },
            "시스템_상태": {
                "캐시_디렉토리": str(self.crawler.cache_dir),
                "자동_업데이트": status.get("자동_업데이트", "알 수 없음"),
                "업데이트_시간": status.get("업데이트_시간", "알 수 없음")
            }
        }
        
        # 국가별 상태 상세 정보
        for country in self.monitoring_config["countries"]:
            cache_info = status["캐시_상태"].get(country, {})
            live_info = status["실시간_데이터"].get(country, {})
            
            country_status = {
                "캐시_상태": {
                    "파일_존재": cache_info.get("파일_존재", False),
                    "마지막_업데이트": cache_info.get("마지막_업데이트"),
                    "파일_나이_시간": cache_info.get("파일_나이_시간"),
                    "유효성": cache_info.get("유효성", False)
                },
                "실시간_데이터": {
                    "데이터_존재": live_info.get("데이터_존재", False),
                    "업데이트_시간": live_info.get("업데이트_시간")
                },
                "상태_등급": self._get_status_grade(cache_info, live_info)
            }
            
            dashboard["국가별_상태"][country] = country_status
        
        return dashboard
    
    def _get_status_grade(self, cache_info: Dict, live_info: Dict) -> str:
        """상태 등급 결정"""
        if not cache_info.get("파일_존재"):
            return "🔴 위험"
        
        file_age = cache_info.get("파일_나이_시간", 0)
        
        if file_age > 24:  # 24시간 이상
            return "🔴 위험"
        elif file_age > 12:  # 12시간 이상
            return "🟡 주의"
        elif file_age > 6:  # 6시간 이상
            return "🟠 경고"
        else:
            return "🟢 정상"
    
    def _count_alert_types(self) -> Dict:
        """알림 타입별 개수 계산"""
        alert_counts = {}
        for alert in self.alert_history:
            alert_type = alert["type"]
            alert_counts[alert_type] = alert_counts.get(alert_type, 0) + 1
        return alert_counts
    
    def force_update_all(self):
        """모든 규제 데이터 강제 업데이트"""
        print("🔄 모든 규제 데이터 강제 업데이트 시작...")
        
        try:
            for product in self.monitoring_config["products"]:
                updated_data = self.crawler.update_all_regulations(product)
                
                print(f"✅ {product} 규제 데이터 업데이트 완료")
                for country, data in updated_data.items():
                    update_time = data['추가정보']['최종업데이트']
                    print(f"   {country}: {update_time}")
            
            print("✅ 모든 규제 데이터 강제 업데이트 완료!")
            
        except Exception as e:
            print(f"❌ 강제 업데이트 실패: {e}")
    
    def get_alert_history(self, limit: int = 20) -> List[Dict]:
        """알림 히스토리 반환"""
        return self.alert_history[-limit:] if self.alert_history else []
    
    def clear_alert_history(self):
        """알림 히스토리 초기화"""
        self.alert_history.clear()
        print("✅ 알림 히스토리가 초기화되었습니다.")
    
    def export_monitoring_report(self, filename: str = None):
        """모니터링 리포트 내보내기"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"regulation_monitoring_report_{timestamp}.json"
        
        report = {
            "리포트_생성_시간": datetime.now().isoformat(),
            "대시보드_데이터": self.get_monitoring_dashboard(),
            "알림_히스토리": self.alert_history,
            "변경_히스토리": self.change_history
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 모니터링 리포트가 저장되었습니다: {filename}")
        return filename

def main():
    """실시간 규제 모니터링 시스템 테스트"""
    
    print("📊 실시간 규제 모니터링 시스템")
    print("=" * 60)
    
    # 모니터링 시스템 초기화
    monitor = RegulationMonitor()
    
    # 모니터링 시작
    monitor.start_monitoring()
    
    try:
        # 대시보드 표시 (5초마다)
        for i in range(6):
            time.sleep(5)
            
            print(f"\n{'='*60}")
            print(f"📊 모니터링 대시보드 (체크 #{i+1})")
            print(f"{'='*60}")
            
            dashboard = monitor.get_monitoring_dashboard()
            
            # 모니터링 상태
            monitoring_status = dashboard["모니터링_상태"]
            print(f"🔄 모니터링 상태: {'활성화' if monitoring_status['활성화'] else '비활성화'}")
            print(f"🕐 마지막 체크: {monitoring_status['마지막_체크']}")
            print(f"⏰ 체크 주기: {monitoring_status['체크_주기']}")
            
            # 국가별 상태
            print(f"\n🌍 국가별 상태:")
            for country, status in dashboard["국가별_상태"].items():
                grade = status["상태_등급"]
                cache_age = status["캐시_상태"]["파일_나이_시간"]
                if cache_age is not None:
                    print(f"   {country}: {grade} ({cache_age:.1f}시간 전)")
                else:
                    print(f"   {country}: {grade} (데이터 없음)")
            
            # 알림 요약
            alert_summary = dashboard["알림_요약"]
            print(f"\n🚨 알림 요약:")
            print(f"   총 알림: {alert_summary['총_알림']}개")
            
            alert_types = alert_summary["알림_타입별"]
            for alert_type, count in alert_types.items():
                print(f"   {alert_type}: {count}개")
            
            # 최근 알림
            recent_alerts = alert_summary["최근_알림"]
            if recent_alerts:
                print(f"\n📢 최근 알림:")
                for alert in recent_alerts[-3:]:  # 최근 3개만
                    timestamp = alert["timestamp"][:19]  # 시간만 표시
                    print(f"   {timestamp}: {alert['message']}")
        
        # 강제 업데이트 테스트
        print(f"\n{'='*60}")
        print("🔄 강제 업데이트 테스트")
        print(f"{'='*60}")
        monitor.force_update_all()
        
        # 최종 대시보드
        print(f"\n{'='*60}")
        print("📊 최종 모니터링 대시보드")
        print(f"{'='*60}")
        
        final_dashboard = monitor.get_monitoring_dashboard()
        
        # 국가별 상태
        print(f"🌍 국가별 상태:")
        for country, status in final_dashboard["국가별_상태"].items():
            grade = status["상태_등급"]
            cache_age = status["캐시_상태"]["파일_나이_시간"]
            if cache_age is not None:
                print(f"   {country}: {grade} ({cache_age:.1f}시간 전)")
            else:
                print(f"   {country}: {grade} (데이터 없음)")
        
        # 리포트 내보내기
        print(f"\n📄 모니터링 리포트 내보내기...")
        report_file = monitor.export_monitoring_report()
        
        print(f"\n✅ 모니터링 시스템 테스트 완료!")
        print(f"📁 리포트 파일: {report_file}")
        
    finally:
        # 모니터링 중지
        monitor.stop_monitoring()

if __name__ == "__main__":
    main() 