#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
메모리 관리 시스템
- 2GB RAM 환경에서 효율적인 메모리 사용
- 지연 로딩 및 가비지 컬렉션 관리
"""

import gc
import time
import threading
from typing import Dict, Any, Optional

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️ psutil이 설치되지 않았습니다. 메모리 모니터링이 제한됩니다.")

class MemoryManager:
    """메모리 사용량 관리 및 최적화"""
    
    def __init__(self, memory_limit_mb: int = 1800):
        """
        Args:
            memory_limit_mb: 메모리 사용 제한 (MB), 기본값 1.8GB
        """
        self.memory_limit = memory_limit_mb
        self._models: Dict[str, Any] = {}
        self._loaded: Dict[str, bool] = {}
        self._lock = threading.Lock()
        self._last_cleanup = time.time()
        self._cleanup_interval = 300  # 5분마다 정리
        
    def get_memory_usage(self) -> float:
        """현재 메모리 사용량 반환 (MB)"""
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process()
                memory_mb = process.memory_info().rss / 1024 / 1024
                return round(memory_mb, 2)
            except:
                return 0.0
        return 0.0
    
    def check_memory_limit(self) -> bool:
        """메모리 제한 확인"""
        current_usage = self.get_memory_usage()
        return current_usage < self.memory_limit
    
    def cleanup_if_needed(self) -> bool:
        """필요시 메모리 정리"""
        current_time = time.time()
        
        # 주기적 정리
        if current_time - self._last_cleanup > self._cleanup_interval:
            self._force_cleanup()
            self._last_cleanup = current_time
            return True
        
        # 메모리 제한 초과시 강제 정리
        if not self.check_memory_limit():
            self._force_cleanup()
            return True
            
        return False
    
    def _force_cleanup(self):
        """강제 메모리 정리"""
        with self._lock:
            # 가비지 컬렉션 실행
            collected = gc.collect()
            print(f"🧹 메모리 정리 완료: {collected}개 객체 수집")
    
    def get_model(self, model_name: str, loader_func) -> Any:
        """모델 지연 로딩"""
        with self._lock:
            if model_name not in self._loaded:
                print(f"🔄 {model_name} 모델 로딩 중...")
                
                # 메모리 정리 확인
                self.cleanup_if_needed()
                
                # 모델 로드
                self._models[model_name] = loader_func()
                self._loaded[model_name] = True
                
                print(f"✅ {model_name} 모델 로딩 완료")
                
            return self._models[model_name]
    
    def preload_essential_models(self, essential_models: Dict[str, callable]):
        """핵심 모델 미리 로드"""
        print("🚀 핵심 모델 미리 로딩 시작...")
        
        for model_name, loader_func in essential_models.items():
            try:
                self.get_model(model_name, loader_func)
            except Exception as e:
                print(f"⚠️ {model_name} 모델 로딩 실패: {e}")
        
        print("✅ 핵심 모델 로딩 완료")
    
    def get_status(self) -> Dict[str, Any]:
        """메모리 상태 정보 반환"""
        return {
            'memory_usage_mb': self.get_memory_usage(),
            'memory_limit_mb': self.memory_limit,
            'usage_percentage': round((self.get_memory_usage() / self.memory_limit) * 100, 2),
            'loaded_models': list(self._loaded.keys()),
            'model_count': len(self._loaded),
            'last_cleanup': time.strftime('%H:%M:%S', time.localtime(self._last_cleanup))
        }

# 전역 메모리 매니저 인스턴스
memory_manager = MemoryManager()

def get_memory_manager() -> MemoryManager:
    """전역 메모리 매니저 반환"""
    return memory_manager 