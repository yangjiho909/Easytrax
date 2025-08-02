#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
규제 업데이트 시간 테스트
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from real_time_regulation_system import RealTimeRegulationCrawler
from datetime import datetime

def test_regulation_update_time():
    """규제 업데이트 시간 테스트"""
    
    print("🔍 규제 업데이트 시간 테스트")
    print("=" * 50)
    
    try:
        # 실시간 크롤러 초기화
        crawler = RealTimeRegulationCrawler()
        
        # 마지막 업데이트 시간 가져오기
        update_time = crawler.get_last_update_time()
        
        print(f"✅ 규제 업데이트 시간: {update_time}")
        print(f"📅 현재 시간: {datetime.now().strftime('%m-%d %H:%M')}")
        
        # 캐시 파일 상태 확인
        print("\n📁 캐시 파일 상태:")
        for country in ["중국", "미국", "한국"]:
            cache_key = crawler.get_cache_key(country, "라면")
            cache_file = crawler.get_cache_file(cache_key)
            
            if cache_file.exists():
                file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
                print(f"   {country}: {file_time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # 캐시 파일 내용에서 실제 업데이트 시간 확인
                try:
                    import json
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if '추가정보' in data and '최종업데이트' in data['추가정보']:
                            actual_time = data['추가정보']['최종업데이트']
                            print(f"     실제 업데이트: {actual_time}")
                except Exception as e:
                    print(f"     파일 읽기 오류: {e}")
            else:
                print(f"   {country}: 파일 없음")
        
        return True
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        return False

if __name__ == "__main__":
    test_regulation_update_time() 