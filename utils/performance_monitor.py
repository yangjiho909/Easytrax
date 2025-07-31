#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
성능 모니터링 시스템
- 실시간 성능 추적
- 응답 시간 모니터링
- 에러율 추적
"""

import time
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque

class PerformanceMonitor:
    """실시간 성능 모니터링"""
    
    def __init__(self, max_history: int = 1000):
        """
        Args:
            max_history: 최대 히스토리 저장 개수
        """
        self.start_time = time.time()
        self.max_history = max_history
        
        # 요청 통계
        self.request_count = 0
        self.error_count = 0
        self.total_response_time = 0.0
        
        # 엔드포인트별 통계
        self.endpoint_stats = defaultdict(lambda: {
            'count': 0,
            'errors': 0,
            'total_time': 0.0,
            'min_time': float('inf'),
            'max_time': 0.0
        })
        
        # 응답 시간 히스토리
        self.response_times = deque(maxlen=max_history)
        self.error_history = deque(maxlen=max_history)
        
        # 스레드 안전성
        self.lock = threading.Lock()
        
        # 메모리 사용량 추적
        self.memory_history = deque(maxlen=max_history)
        self.last_memory_check = 0
        self.memory_check_interval = 60  # 1분마다 메모리 체크
    
    def log_request(self, endpoint: str, response_time: float, 
                   success: bool = True, error_message: str = None) -> None:
        """요청 로깅"""
        with self.lock:
            # 전체 통계 업데이트
            self.request_count += 1
            self.total_response_time += response_time
            
            if not success:
                self.error_count += 1
                self.error_history.append({
                    'timestamp': time.time(),
                    'endpoint': endpoint,
                    'error': error_message,
                    'response_time': response_time
                })
            
            # 응답 시간 히스토리
            self.response_times.append({
                'timestamp': time.time(),
                'endpoint': endpoint,
                'response_time': response_time,
                'success': success
            })
            
            # 엔드포인트별 통계 업데이트
            stats = self.endpoint_stats[endpoint]
            stats['count'] += 1
            stats['total_time'] += response_time
            stats['min_time'] = min(stats['min_time'], response_time)
            stats['max_time'] = max(stats['max_time'], response_time)
            
            if not success:
                stats['errors'] += 1
    
    def get_memory_usage(self) -> float:
        """메모리 사용량 조회"""
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            return round(memory_mb, 2)
        except ImportError:
            return 0.0
    
    def update_memory_usage(self) -> None:
        """메모리 사용량 업데이트"""
        current_time = time.time()
        if current_time - self.last_memory_check > self.memory_check_interval:
            memory_usage = self.get_memory_usage()
            self.memory_history.append({
                'timestamp': current_time,
                'memory_mb': memory_usage
            })
            self.last_memory_check = current_time
    
    def get_stats(self) -> Dict[str, Any]:
        """전체 통계 반환"""
        with self.lock:
            self.update_memory_usage()
            
            uptime_hours = (time.time() - self.start_time) / 3600
            avg_response_time = (self.total_response_time / max(self.request_count, 1))
            error_rate = (self.error_count / max(self.request_count, 1)) * 100
            
            # 최근 1시간 통계
            one_hour_ago = time.time() - 3600
            recent_requests = [r for r in self.response_times if r['timestamp'] > one_hour_ago]
            recent_avg_time = sum(r['response_time'] for r in recent_requests) / max(len(recent_requests), 1)
            
            return {
                'uptime_hours': round(uptime_hours, 2),
                'total_requests': self.request_count,
                'error_count': self.error_count,
                'error_rate_percent': round(error_rate, 2),
                'avg_response_time_seconds': round(avg_response_time, 3),
                'recent_avg_response_time_seconds': round(recent_avg_time, 3),
                'memory_usage_mb': self.get_memory_usage(),
                'endpoint_count': len(self.endpoint_stats),
                'recent_requests_1h': len(recent_requests)
            }
    
    def get_endpoint_stats(self) -> Dict[str, Dict[str, Any]]:
        """엔드포인트별 통계 반환"""
        with self.lock:
            result = {}
            for endpoint, stats in self.endpoint_stats.items():
                if stats['count'] > 0:
                    avg_time = stats['total_time'] / stats['count']
                    error_rate = (stats['errors'] / stats['count']) * 100
                    
                    result[endpoint] = {
                        'request_count': stats['count'],
                        'error_count': stats['errors'],
                        'error_rate_percent': round(error_rate, 2),
                        'avg_response_time_seconds': round(avg_time, 3),
                        'min_response_time_seconds': round(stats['min_time'], 3),
                        'max_response_time_seconds': round(stats['max_time'], 3)
                    }
            return result
    
    def get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """최근 에러 목록 반환"""
        with self.lock:
            recent_errors = list(self.error_history)[-limit:]
            return [
                {
                    'timestamp': datetime.fromtimestamp(error['timestamp']).strftime('%Y-%m-%d %H:%M:%S'),
                    'endpoint': error['endpoint'],
                    'error': error['error'],
                    'response_time': round(error['response_time'], 3)
                }
                for error in recent_errors
            ]
    
    def get_performance_trends(self, hours: int = 24) -> Dict[str, Any]:
        """성능 트렌드 분석"""
        with self.lock:
            cutoff_time = time.time() - (hours * 3600)
            recent_data = [r for r in self.response_times if r['timestamp'] > cutoff_time]
            
            if not recent_data:
                return {'message': '최근 데이터가 없습니다.'}
            
            # 시간대별 분할
            hourly_stats = defaultdict(lambda: {'count': 0, 'total_time': 0, 'errors': 0})
            
            for request in recent_data:
                hour = datetime.fromtimestamp(request['timestamp']).strftime('%Y-%m-%d %H:00')
                hourly_stats[hour]['count'] += 1
                hourly_stats[hour]['total_time'] += request['response_time']
                if not request['success']:
                    hourly_stats[hour]['errors'] += 1
            
            # 시간대별 평균 응답 시간 계산
            hourly_avg = {}
            for hour, stats in hourly_stats.items():
                if stats['count'] > 0:
                    hourly_avg[hour] = {
                        'avg_response_time': round(stats['total_time'] / stats['count'], 3),
                        'request_count': stats['count'],
                        'error_count': stats['errors']
                    }
            
            return {
                'total_requests': len(recent_data),
                'avg_response_time': round(sum(r['response_time'] for r in recent_data) / len(recent_data), 3),
                'error_rate': round(sum(1 for r in recent_data if not r['success']) / len(recent_data) * 100, 2),
                'hourly_stats': dict(hourly_avg)
            }
    
    def reset_stats(self) -> None:
        """통계 초기화"""
        with self.lock:
            self.request_count = 0
            self.error_count = 0
            self.total_response_time = 0.0
            self.endpoint_stats.clear()
            self.response_times.clear()
            self.error_history.clear()
            self.memory_history.clear()
            self.start_time = time.time()

# 전역 성능 모니터 인스턴스
performance_monitor = PerformanceMonitor()

def get_performance_monitor() -> PerformanceMonitor:
    """전역 성능 모니터 반환"""
    return performance_monitor

# 데코레이터로 성능 측정
def monitor_performance(endpoint: str = None):
    """함수 성능 측정 데코레이터"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            error_message = None
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error_message = str(e)
                raise
            finally:
                response_time = time.time() - start_time
                monitor_endpoint = endpoint or func.__name__
                performance_monitor.log_request(
                    monitor_endpoint, response_time, success, error_message
                )
        
        # Flask 엔드포인트 중복 방지를 위해 원본 함수 이름 유지
        wrapper.__name__ = func.__name__
        return wrapper
    return decorator 