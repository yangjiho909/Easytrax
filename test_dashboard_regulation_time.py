#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
대시보드 규제 업데이트 시간 테스트
"""

import requests
import json
from datetime import datetime

def test_dashboard_regulation_time():
    """대시보드 규제 업데이트 시간 테스트"""
    
    base_url = "http://localhost:5000"
    
    print("🔍 대시보드 규제 업데이트 시간 테스트")
    print("=" * 50)
    
    try:
        # 대시보드 통계 API 호출
        print("📊 대시보드 통계 API 호출 중...")
        response = requests.get(f"{base_url}/api/dashboard-stats", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                stats = data.get('stats', {})
                
                print("✅ 대시보드 통계 조회 성공!")
                print(f"📅 마지막 업데이트: {stats.get('last_updated', 'N/A')}")
                print(f"🕐 규제 업데이트 시간: {stats.get('regulation_update_time', 'N/A')}")
                print(f"🌍 지원 국가 수: {stats.get('supported_country_count', 'N/A')}")
                print(f"📊 총 거부 사례: {stats.get('total_rejection_cases', 'N/A')}")
                
                # 규제 업데이트 시간이 제대로 표시되는지 확인
                regulation_time = stats.get('regulation_update_time', '')
                if regulation_time and regulation_time != '정보 없음':
                    print(f"✅ 규제 업데이트 시간이 정상적으로 표시됩니다: {regulation_time}")
                else:
                    print(f"⚠️ 규제 업데이트 시간이 표시되지 않습니다: {regulation_time}")
                
                # 최근 활동 확인
                recent_activities = stats.get('recent_activities', [])
                if recent_activities:
                    print(f"📋 최근 활동 수: {len(recent_activities)}")
                    for i, activity in enumerate(recent_activities[:3]):
                        print(f"   {i+1}. {activity.get('title', 'N/A')} - {activity.get('time', 'N/A')}")
                
            else:
                print(f"❌ API 응답 실패: {data.get('error', '알 수 없는 오류')}")
        else:
            print(f"❌ HTTP 오류: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인해주세요.")
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")

def test_regulation_status():
    """규제 상태 API 테스트"""
    
    base_url = "http://localhost:5000"
    
    print("\n🔍 규제 상태 API 테스트")
    print("=" * 30)
    
    try:
        response = requests.get(f"{base_url}/api/regulation-status", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 규제 상태 조회 성공!")
            print(f"📊 상태: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ HTTP 오류: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다.")
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")

if __name__ == "__main__":
    test_dashboard_regulation_time()
    test_regulation_status() 