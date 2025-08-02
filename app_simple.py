#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 KATI 최소 배포 버전
- 최소한의 기능만 포함
- 안정적인 배포를 위한 단순화
"""

import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS

# Flask 앱 생성
app = Flask(__name__)
CORS(app)

# 기본 설정
app.secret_key = os.environ.get('SECRET_KEY', 'kati_minimal_secret_key_2024')

# 환경 감지
IS_RENDER = os.environ.get('RENDER') is not None
IS_CLOUD = IS_RENDER

print(f"🚀 KATI 최소 버전 시작 - 환경: {'클라우드' if IS_CLOUD else '로컬'}")

# 기본 라우트
@app.route('/')
def index():
    """메인 페이지"""
    return jsonify({
        'message': 'KATI 시스템이 정상적으로 작동 중입니다',
        'status': 'operational',
        'version': 'minimal-1.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/health')
def health():
    """헬스 체크"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'environment': 'cloud' if IS_CLOUD else 'local'
    })

@app.route('/api/health', methods=['GET'])
def api_health_check():
    """API 헬스 체크"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'environment': 'cloud' if IS_CLOUD else 'local'
    })

@app.route('/api/system-status')
def api_system_status():
    """시스템 상태"""
    return jsonify({
        'status': 'operational',
        'version': 'minimal-1.0',
        'environment': 'cloud' if IS_CLOUD else 'local',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/document-generation', methods=['POST'])
def api_document_generation():
    """서류 생성 API (최소 버전)"""
    try:
        data = request.get_json()
        
        # 기본 검증
        if not data:
            return jsonify({'error': '데이터가 없습니다'}), 400
        
        # 간단한 응답
        return jsonify({
            'success': True,
            'message': '서류 생성 요청이 정상적으로 처리되었습니다',
            'note': '최소 버전에서는 실제 파일 생성이 비활성화되어 있습니다',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': f'서류 생성 실패: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/download-document/<filename>')
def download_document(filename):
    """문서 다운로드 (최소 버전)"""
    return jsonify({
        'error': '최소 버전에서는 파일 다운로드가 비활성화되어 있습니다',
        'filename': filename,
        'timestamp': datetime.now().isoformat()
    }), 404

@app.route('/api/dashboard-stats')
def api_dashboard_stats():
    """대시보드 통계"""
    return jsonify({
        'total_documents': 0,
        'total_analyses': 0,
        'system_status': 'operational',
        'last_update': datetime.now().isoformat()
    })

# 에러 핸들러
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': '페이지를 찾을 수 없습니다'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': '서버 내부 오류가 발생했습니다'}), 500

if __name__ == '__main__':
    print("✅ KATI 최소 버전 서버 시작")
    port = int(os.environ.get('PORT', 5000))
    print(f"🌐 서버 포트: {port}")
    print(f"🌍 호스트: 0.0.0.0")
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True) 