#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
☁️ 클라우드 스토리지 시스템
- 로컬 파일 시스템과 동일한 인터페이스 제공
- 클라우드 환경에서 파일 저장/로드 지원
- 임시 파일 시스템으로 대체
"""

import os
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, BinaryIO
import base64
from datetime import datetime
import threading

class CloudStorage:
    """클라우드 스토리지 시스템 (로컬 파일 시스템 호환)"""
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="kati_cloud_")
        self.file_registry = {}
        self.lock = threading.Lock()
        
        # 필요한 디렉토리 생성
        self._create_directories()
        print(f"☁️ 클라우드 스토리지 초기화: {self.temp_dir}")
    
    def _create_directories(self):
        """필요한 디렉토리 생성"""
        directories = [
            'uploaded_documents',
            'generated_documents', 
            'uploaded_labels',
            'advanced_labels',
            'uploaded_templates',
            'regulation_cache',
            'model'
        ]
        
        for directory in directories:
            os.makedirs(os.path.join(self.temp_dir, directory), exist_ok=True)
    
    def save_file(self, file_path: str, content: bytes, mode: str = 'wb') -> bool:
        """파일 저장 (로컬 파일 시스템 호환)"""
        try:
            full_path = os.path.join(self.temp_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, mode) as f:
                f.write(content)
            
            with self.lock:
                self.file_registry[file_path] = {
                    'size': len(content),
                    'created': datetime.now().isoformat(),
                    'path': full_path
                }
            
            print(f"✅ 파일 저장 완료: {file_path}")
            return True
            
        except Exception as e:
            print(f"❌ 파일 저장 실패: {file_path} - {e}")
            return False
    
    def load_file(self, file_path: str, mode: str = 'rb') -> Optional[bytes]:
        """파일 로드 (로컬 파일 시스템 호환)"""
        try:
            full_path = os.path.join(self.temp_dir, file_path)
            
            if not os.path.exists(full_path):
                print(f"⚠️ 파일이 존재하지 않음: {file_path}")
                return None
            
            with open(full_path, mode) as f:
                content = f.read()
            
            print(f"✅ 파일 로드 완료: {file_path}")
            return content
            
        except Exception as e:
            print(f"❌ 파일 로드 실패: {file_path} - {e}")
            return None
    
    def file_exists(self, file_path: str) -> bool:
        """파일 존재 여부 확인"""
        full_path = os.path.join(self.temp_dir, file_path)
        return os.path.exists(full_path)
    
    def list_files(self, directory: str) -> list:
        """디렉토리 내 파일 목록"""
        full_path = os.path.join(self.temp_dir, directory)
        if not os.path.exists(full_path):
            return []
        
        files = []
        for filename in os.listdir(full_path):
            file_path = os.path.join(full_path, filename)
            if os.path.isfile(file_path):
                files.append(filename)
        
        return files
    
    def get_file_info(self, file_path: str) -> Optional[Dict]:
        """파일 정보 조회"""
        full_path = os.path.join(self.temp_dir, file_path)
        if not os.path.exists(full_path):
            return None
        
        stat = os.stat(full_path)
        return {
            'size': stat.st_size,
            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'path': full_path
        }
    
    def delete_file(self, file_path: str) -> bool:
        """파일 삭제"""
        try:
            full_path = os.path.join(self.temp_dir, file_path)
            if os.path.exists(full_path):
                os.remove(full_path)
                print(f"✅ 파일 삭제 완료: {file_path}")
                return True
            return False
        except Exception as e:
            print(f"❌ 파일 삭제 실패: {file_path} - {e}")
            return False
    
    def cleanup(self):
        """임시 파일 정리"""
        try:
            shutil.rmtree(self.temp_dir)
            print(f"🧹 임시 파일 정리 완료: {self.temp_dir}")
        except Exception as e:
            print(f"❌ 임시 파일 정리 실패: {e}")

# 전역 인스턴스
cloud_storage = CloudStorage() 