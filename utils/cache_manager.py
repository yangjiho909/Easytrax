#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
캐싱 시스템
- 반복 요청 최적화
- 메모리 기반 캐싱
- TTL (Time To Live) 지원
"""

import time
import threading
import hashlib
import json
from typing import Dict, Any, Optional, Union
from datetime import datetime, timedelta

class CacheManager:
    """메모리 기반 캐싱 시스템"""
    
    def __init__(self, max_size: int = 1000):
        """
        Args:
            max_size: 최대 캐시 항목 수
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()
        self.max_size = max_size
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'evictions': 0
        }
    
    def _generate_key(self, *args, **kwargs) -> str:
        """캐시 키 생성"""
        # 인자들을 JSON으로 직렬화하여 키 생성
        key_data = {
            'args': args,
            'kwargs': kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, key: str, default: Any = None) -> Any:
        """캐시에서 값 조회"""
        with self.lock:
            if key in self.cache:
                cache_item = self.cache[key]
                
                # TTL 확인
                if 'expiry' in cache_item:
                    if time.time() > cache_item['expiry']:
                        # 만료된 항목 삭제
                        del self.cache[key]
                        self.stats['misses'] += 1
                        return default
                
                # 캐시 히트
                self.stats['hits'] += 1
                return cache_item['value']
            
            # 캐시 미스
            self.stats['misses'] += 1
            return default
    
    def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> None:
        """캐시에 값 저장"""
        with self.lock:
            # 캐시 크기 제한 확인
            if len(self.cache) >= self.max_size:
                self._evict_oldest()
            
            # 캐시 항목 생성
            cache_item = {
                'value': value,
                'timestamp': time.time()
            }
            
            # TTL 설정
            if ttl_seconds > 0:
                cache_item['expiry'] = time.time() + ttl_seconds
            
            self.cache[key] = cache_item
            self.stats['sets'] += 1
    
    def _evict_oldest(self):
        """가장 오래된 항목 제거"""
        if not self.cache:
            return
        
        # 가장 오래된 항목 찾기
        oldest_key = min(self.cache.keys(), 
                        key=lambda k: self.cache[k]['timestamp'])
        
        del self.cache[oldest_key]
        self.stats['evictions'] += 1
    
    def delete(self, key: str) -> bool:
        """캐시 항목 삭제"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """캐시 전체 삭제"""
        with self.lock:
            self.cache.clear()
            self.stats = {
                'hits': 0,
                'misses': 0,
                'sets': 0,
                'evictions': 0
            }
    
    def cleanup_expired(self) -> int:
        """만료된 항목 정리"""
        with self.lock:
            expired_keys = []
            current_time = time.time()
            
            for key, item in self.cache.items():
                if 'expiry' in item and current_time > item['expiry']:
                    expired_keys.append(key)
            
            # 만료된 항목 삭제
            for key in expired_keys:
                del self.cache[key]
            
            return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """캐시 통계 반환"""
        with self.lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'cache_size': len(self.cache),
                'max_size': self.max_size,
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'sets': self.stats['sets'],
                'evictions': self.stats['evictions'],
                'hit_rate_percent': round(hit_rate, 2),
                'total_requests': total_requests
            }
    
    def get_status(self) -> Dict[str, Any]:
        """캐시 상태 정보 반환"""
        stats = self.get_stats()
        expired_count = self.cleanup_expired()
        
        return {
            **stats,
            'expired_cleaned': expired_count,
            'memory_usage_estimate': len(self.cache) * 0.1  # 추정 메모리 사용량 (MB)
        }

# 함수 데코레이터로 캐싱 적용
def cached(ttl_seconds: int = 3600, key_prefix: str = ""):
    """함수 결과 캐싱 데코레이터"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 캐시 키 생성
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # 캐시에서 조회
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # 함수 실행
            result = func(*args, **kwargs)
            
            # 결과 캐싱
            cache_manager.set(cache_key, result, ttl_seconds)
            
            return result
        return wrapper
    return decorator

# 전역 캐시 매니저 인스턴스
cache_manager = CacheManager()

def get_cache_manager() -> CacheManager:
    """전역 캐시 매니저 반환"""
    return cache_manager 