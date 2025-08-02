#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
배포 환경 파일 생성/다운로드 문제 해결 도구
클라우드 환경에서 발생하는 파일 시스템 문제를 해결합니다.
"""

import os
import sys
import tempfile
import shutil
import base64
import io
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

class DeploymentFileManager:
    """배포 환경 전용 파일 관리자"""
    
    def __init__(self):
        self.is_cloud = self._detect_cloud_environment()
        self.temp_dir = self._setup_temp_directory()
        self.file_cache = {}  # 메모리 기반 파일 캐시
        
        print(f"🌐 클라우드 환경: {self.is_cloud}")
        print(f"📁 임시 디렉토리: {self.temp_dir}")
    
    def _detect_cloud_environment(self) -> bool:
        """클라우드 환경 감지"""
        return any([
            os.environ.get('RENDER') is not None,
            os.environ.get('IS_HEROKU', False),
            os.environ.get('IS_RAILWAY', False),
            os.environ.get('DYNO') is not None,  # Heroku
            os.environ.get('PORT') is not None and os.environ.get('PORT') != '5000'
        ])
    
    def _setup_temp_directory(self) -> str:
        """임시 디렉토리 설정"""
        if self.is_cloud:
            # 클라우드 환경에서는 시스템 임시 디렉토리 사용
            temp_dir = tempfile.mkdtemp(prefix='kati_')
            print(f"✅ 클라우드 임시 디렉토리 생성: {temp_dir}")
        else:
            # 로컬 환경에서는 기존 디렉토리 사용
            temp_dir = "generated_documents"
            os.makedirs(temp_dir, exist_ok=True)
            print(f"✅ 로컬 디렉토리 사용: {temp_dir}")
        
        return temp_dir
    
    def ensure_directory(self, directory: str) -> bool:
        """디렉토리 존재 확인 및 생성"""
        try:
            if self.is_cloud:
                # 클라우드 환경에서는 임시 디렉토리 내에 생성
                full_path = os.path.join(self.temp_dir, directory)
            else:
                full_path = directory
            
            os.makedirs(full_path, exist_ok=True)
            
            # 권한 확인
            if os.access(full_path, os.W_OK):
                print(f"✅ 디렉토리 준비 완료: {full_path}")
                return True
            else:
                print(f"❌ 디렉토리 쓰기 권한 없음: {full_path}")
                return False
                
        except Exception as e:
            print(f"❌ 디렉토리 생성 실패: {str(e)}")
            return False
    
    def create_file(self, filename: str, content: str, file_type: str = 'txt') -> Dict[str, Any]:
        """파일 생성 (클라우드 환경 대응)"""
        try:
            # 파일명에 타임스탬프 추가
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = f"{filename}_{timestamp}.{file_type}"
            
            if self.is_cloud:
                # 클라우드 환경: 메모리 캐시 + 임시 파일
                file_path = os.path.join(self.temp_dir, safe_filename)
                
                # 파일 생성
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # 메모리 캐시에 저장
                self.file_cache[safe_filename] = {
                    'path': file_path,
                    'content': content,
                    'size': len(content),
                    'created': datetime.now(),
                    'type': file_type
                }
                
                print(f"✅ 클라우드 파일 생성: {safe_filename} ({len(content)} bytes)")
                
            else:
                # 로컬 환경: 일반 파일 생성
                file_path = os.path.join("generated_documents", safe_filename)
                os.makedirs("generated_documents", exist_ok=True)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"✅ 로컬 파일 생성: {safe_filename} ({len(content)} bytes)")
            
            return {
                'success': True,
                'filename': safe_filename,
                'path': file_path,
                'size': len(content),
                'type': file_type
            }
            
        except Exception as e:
            print(f"❌ 파일 생성 실패: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_pdf_file(self, filename: str, pdf_content: bytes) -> Dict[str, Any]:
        """PDF 파일 생성 (클라우드 환경 대응)"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = f"{filename}_{timestamp}.pdf"
            
            if self.is_cloud:
                # 클라우드 환경: 임시 파일 + 메모리 캐시
                file_path = os.path.join(self.temp_dir, safe_filename)
                
                with open(file_path, 'wb') as f:
                    f.write(pdf_content)
                
                # 메모리 캐시에 저장
                self.file_cache[safe_filename] = {
                    'path': file_path,
                    'content': pdf_content,
                    'size': len(pdf_content),
                    'created': datetime.now(),
                    'type': 'pdf'
                }
                
                print(f"✅ 클라우드 PDF 생성: {safe_filename} ({len(pdf_content)} bytes)")
                
            else:
                # 로컬 환경: 일반 PDF 생성
                file_path = os.path.join("generated_documents", safe_filename)
                os.makedirs("generated_documents", exist_ok=True)
                
                with open(file_path, 'wb') as f:
                    f.write(pdf_content)
                
                print(f"✅ 로컬 PDF 생성: {safe_filename} ({len(pdf_content)} bytes)")
            
            return {
                'success': True,
                'filename': safe_filename,
                'path': file_path,
                'size': len(pdf_content),
                'type': 'pdf'
            }
            
        except Exception as e:
            print(f"❌ PDF 생성 실패: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_file_content(self, filename: str) -> Optional[bytes]:
        """파일 내용 가져오기"""
        try:
            # 1. 메모리 캐시에서 먼저 확인
            if filename in self.file_cache:
                print(f"📦 메모리 캐시에서 파일 발견: {filename}")
                cache_entry = self.file_cache[filename]
                if cache_entry['type'] == 'pdf':
                    return cache_entry['content']
                else:
                    return cache_entry['content'].encode('utf-8')
            
            # 2. 여러 경로에서 파일 검색
            possible_paths = []
            
            # 클라우드 환경
            if self.is_cloud:
                possible_paths.append(os.path.join(self.temp_dir, filename))
            
            # 로컬 환경
            possible_paths.extend([
                os.path.join("generated_documents", filename),
                os.path.join("temp_uploads", filename),
                os.path.join("uploaded_documents", filename),
                filename  # 현재 디렉토리
            ])
            
            # 각 경로에서 파일 확인
            for file_path in possible_paths:
                if os.path.exists(file_path):
                    print(f"📁 파일 발견: {file_path}")
                    try:
                        with open(file_path, 'rb') as f:
                            content = f.read()
                        
                        # 메모리 캐시에 추가 (향후 빠른 접근을 위해)
                        file_size = len(content)
                        self.file_cache[filename] = {
                            'path': file_path,
                            'content': content,
                            'size': file_size,
                            'created': datetime.now(),
                            'type': 'pdf' if filename.endswith('.pdf') else 'txt'
                        }
                        print(f"✅ 파일을 메모리 캐시에 추가: {filename} ({file_size} bytes)")
                        return content
                    except Exception as e:
                        print(f"⚠️ 파일 읽기 실패: {file_path} - {e}")
                        continue
            
            print(f"❌ 파일을 찾을 수 없음: {filename}")
            print(f"🔍 검색한 경로들: {possible_paths}")
            return None
            
        except Exception as e:
            print(f"❌ 파일 내용 가져오기 실패: {str(e)}")
            return None
    
    def get_file_info(self, filename: str) -> Optional[Dict[str, Any]]:
        """파일 정보 가져오기"""
        try:
            if filename in self.file_cache:
                return self.file_cache[filename]
            
            if self.is_cloud:
                file_path = os.path.join(self.temp_dir, filename)
            else:
                file_path = os.path.join("generated_documents", filename)
            
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                return {
                    'path': file_path,
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_ctime),
                    'modified': datetime.fromtimestamp(stat.st_mtime),
                    'type': 'pdf' if filename.endswith('.pdf') else 'txt'
                }
            
            return None
            
        except Exception as e:
            print(f"❌ 파일 정보 가져오기 실패: {str(e)}")
            return None
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """오래된 파일 정리"""
        try:
            current_time = datetime.now()
            files_to_remove = []
            
            # 메모리 캐시 정리
            for filename, cache_entry in self.file_cache.items():
                age = (current_time - cache_entry['created']).total_seconds() / 3600
                if age > max_age_hours:
                    files_to_remove.append(filename)
            
            for filename in files_to_remove:
                del self.file_cache[filename]
                print(f"🗑️ 메모리 캐시에서 제거: {filename}")
            
            # 임시 파일 정리 (클라우드 환경)
            if self.is_cloud and os.path.exists(self.temp_dir):
                for filename in os.listdir(self.temp_dir):
                    file_path = os.path.join(self.temp_dir, filename)
                    if os.path.isfile(file_path):
                        file_age = (current_time - datetime.fromtimestamp(os.path.getctime(file_path))).total_seconds() / 3600
                        if file_age > max_age_hours:
                            os.remove(file_path)
                            print(f"🗑️ 임시 파일 제거: {filename}")
            
            print(f"✅ 파일 정리 완료: {len(files_to_remove)}개 파일 제거")
            
        except Exception as e:
            print(f"❌ 파일 정리 실패: {str(e)}")
    
    def get_cache_status(self) -> Dict[str, Any]:
        """캐시 상태 확인"""
        return {
            'cache_size': len(self.file_cache),
            'temp_dir': self.temp_dir,
            'is_cloud': self.is_cloud,
            'total_size': sum(entry['size'] for entry in self.file_cache.values())
        }
    
    def optimize_memory(self, max_cache_size_mb: int = 50):
        """메모리 최적화 - 캐시 크기 제한"""
        try:
            total_size_mb = sum(entry['size'] for entry in self.file_cache.values()) / (1024 * 1024)
            
            if total_size_mb > max_cache_size_mb:
                print(f"⚠️ 메모리 최적화 필요: {total_size_mb:.2f}MB > {max_cache_size_mb}MB")
                
                # 가장 오래된 파일부터 제거
                sorted_files = sorted(
                    self.file_cache.items(),
                    key=lambda x: x[1]['created']
                )
                
                removed_count = 0
                for filename, cache_entry in sorted_files:
                    if total_size_mb <= max_cache_size_mb:
                        break
                    
                    del self.file_cache[filename]
                    removed_size_mb = cache_entry['size'] / (1024 * 1024)
                    total_size_mb -= removed_size_mb
                    removed_count += 1
                    print(f"🗑️ 메모리 최적화로 제거: {filename} ({removed_size_mb:.2f}MB)")
                
                print(f"✅ 메모리 최적화 완료: {removed_count}개 파일 제거, {total_size_mb:.2f}MB")
            
        except Exception as e:
            print(f"❌ 메모리 최적화 실패: {str(e)}")
    
    def ensure_file_persistence(self, filename: str) -> bool:
        """파일 지속성 보장 (클라우드 환경에서 중요)"""
        try:
            if filename in self.file_cache:
                # 메모리에 있는 파일을 임시 디렉토리에 저장
                cache_entry = self.file_cache[filename]
                temp_path = os.path.join(self.temp_dir, filename)
                
                with open(temp_path, 'wb') as f:
                    if cache_entry['type'] == 'pdf':
                        f.write(cache_entry['content'])
                    else:
                        f.write(cache_entry['content'].encode('utf-8'))
                
                print(f"✅ 파일 지속성 보장: {filename} -> {temp_path}")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ 파일 지속성 보장 실패: {str(e)}")
            return False

# Flask 애플리케이션에 통합할 수 있는 헬퍼 함수들
def create_deployment_safe_pdf(content: str, filename: str) -> Dict[str, Any]:
    """배포 환경 안전 PDF 생성"""
    file_manager = DeploymentFileManager()
    
    try:
        # 간단한 PDF 생성 (ReportLab 사용)
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        
        # 임시 PDF 생성
        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=A4)
        
        # 한글 폰트 설정 시도
        try:
            pdfmetrics.registerFont(TTFont('NanumGothic', 'fonts/malgun.ttf'))
            c.setFont('NanumGothic', 12)
        except:
            c.setFont('Helvetica', 12)
        
        # 텍스트 추가
        y_position = 750
        for line in content.split('\n'):
            if y_position < 50:
                c.showPage()
                y_position = 750
            c.drawString(50, y_position, line)
            y_position -= 15
        
        c.save()
        pdf_content = pdf_buffer.getvalue()
        pdf_buffer.close()
        
        return file_manager.create_pdf_file(filename, pdf_content)
        
    except ImportError:
        # ReportLab이 없으면 텍스트 파일로 대체
        print("⚠️ ReportLab 없음, 텍스트 파일로 대체")
        return file_manager.create_file(filename, content, 'txt')
    
    except Exception as e:
        print(f"❌ PDF 생성 실패: {str(e)}")
        return file_manager.create_file(filename, content, 'txt')

def serve_deployment_file(filename: str, as_attachment: bool = True) -> Tuple[bytes, str, Dict[str, str]]:
    """배포 환경 파일 서빙"""
    file_manager = DeploymentFileManager()
    
    print(f"🔍 파일 서빙 요청: {filename}")
    
    file_content = file_manager.get_file_content(filename)
    if file_content is None:
        # 파일을 찾을 수 없는 경우 더 자세한 정보 제공
        print(f"❌ 파일을 찾을 수 없음: {filename}")
        print(f"📦 현재 캐시 상태: {file_manager.get_cache_status()}")
        
        # 캐시된 파일 목록 출력
        if file_manager.file_cache:
            print(f"📋 캐시된 파일들: {list(file_manager.file_cache.keys())}")
        
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {filename}")
    
    print(f"✅ 파일 서빙 성공: {filename} ({len(file_content)} bytes)")
    
    # MIME 타입 결정
    if filename.endswith('.pdf'):
        mime_type = 'application/pdf'
    elif filename.endswith('.txt'):
        mime_type = 'text/plain; charset=utf-8'
    else:
        mime_type = 'application/octet-stream'
    
    # 헤더 설정
    headers = {
        'Content-Type': mime_type,
        'Content-Length': str(len(file_content))
    }
    
    if as_attachment:
        headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return file_content, mime_type, headers

# 테스트 함수
def test_deployment_file_manager():
    """배포 파일 관리자 테스트"""
    print("🧪 배포 파일 관리자 테스트")
    print("=" * 50)
    
    file_manager = DeploymentFileManager()
    
    # 1. 텍스트 파일 생성 테스트
    print("\n1. 텍스트 파일 생성 테스트")
    result = file_manager.create_file("test_document", "테스트 문서 내용입니다.", "txt")
    print(f"결과: {result}")
    
    # 2. PDF 파일 생성 테스트
    print("\n2. PDF 파일 생성 테스트")
    pdf_result = create_deployment_safe_pdf("테스트 PDF 문서입니다.\n두 번째 줄입니다.", "test_pdf")
    print(f"결과: {pdf_result}")
    
    # 3. 캐시 상태 확인
    print("\n3. 캐시 상태 확인")
    cache_status = file_manager.get_cache_status()
    print(f"캐시 상태: {cache_status}")
    
    # 4. 파일 정리
    print("\n4. 파일 정리")
    file_manager.cleanup_old_files(max_age_hours=1)
    
    print("\n✅ 테스트 완료")

if __name__ == "__main__":
    test_deployment_file_manager() 