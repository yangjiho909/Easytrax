#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 KATI 최소 배포 버전
- 최소한의 기능만 포함
- 안정적인 배포를 위한 단순화
"""

import os
from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS

# Flask 앱 생성
app = Flask(__name__)
CORS(app)

print("🚀 KATI 최소 버전 시작")

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
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/health')
def api_health():
    """API 헬스 체크"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/system-status')
def system_status():
    """시스템 상태"""
    return jsonify({
        'status': 'operational',
        'version': 'minimal-1.0',
        'timestamp': datetime.now().isoformat()
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
    app.run(host='0.0.0.0', port=port, debug=False) 