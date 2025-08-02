#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 KATI 간단 배포 버전
- 핵심 기능만 포함
- 무거운 모듈 제거
- 빠른 시작을 위한 최적화
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
app.secret_key = os.environ.get('SECRET_KEY', 'kati_simple_secret_key_2024')
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploaded_documents')

# 환경 감지
IS_RENDER = os.environ.get('RENDER') is not None
IS_CLOUD = IS_RENDER

print(f"🚀 KATI 간단 버전 시작 - 환경: {'클라우드' if IS_CLOUD else '로컬'}")

# 기본 라우트
@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """대시보드"""
    return render_template('dashboard.html')

@app.route('/document-generation')
def document_generation():
    """서류 생성 페이지"""
    return render_template('document_generation.html')

@app.route('/nutrition-label')
def nutrition_label():
    """영양성분표 페이지"""
    return render_template('nutrition_label.html')

@app.route('/compliance-analysis')
def compliance_analysis():
    """규정 준수 분석 페이지"""
    return render_template('compliance_analysis.html')

@app.route('/customs-analysis')
def customs_analysis():
    """통관 분석 페이지"""
    return render_template('customs_analysis.html')

@app.route('/regulation-info')
def regulation_info():
    """규정 정보 페이지"""
    return render_template('regulation_info.html')

# API 라우트
@app.route('/api/health', methods=['GET'])
def health_check():
    """헬스 체크"""
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
        'version': 'simple-1.0',
        'environment': 'cloud' if IS_CLOUD else 'local',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/document-generation', methods=['POST'])
def api_document_generation():
    """서류 생성 API (간단 버전)"""
    try:
        data = request.get_json()
        
        # 기본 검증
        if not data:
            return jsonify({'error': '데이터가 없습니다'}), 400
        
        # 간단한 서류 생성 (텍스트 파일)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 상업송장 생성
        commercial_invoice_content = f"""
=== 상업송장 (Commercial Invoice) ===
생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

판매자 정보:
- 회사명: {data.get('company_name', '한국기업')}
- 주소: {data.get('company_address', '서울시 강남구')}
- 연락처: {data.get('company_phone', '02-1234-5678')}

제품 정보:
- 제품명: {data.get('product_name', '제품')}
- 수량: {data.get('quantity', 1)}
- 단가: ${data.get('unit_price', 10)}
- 총액: ${data.get('quantity', 1) * data.get('unit_price', 10)}

배송 정보:
- 목적지: {data.get('destination', '미국')}
- 운송방법: {data.get('shipping_method', '해상운송')}

이 문서는 KATI 시스템에서 자동 생성되었습니다.
        """
        
        # 포장명세서 생성
        packing_list_content = f"""
=== 포장명세서 (Packing List) ===
생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

포장 정보:
- 포장번호: PKG-{timestamp}
- 총 포장수: 1

제품 정보:
- 제품명: {data.get('product_name', '제품')}
- 수량: {data.get('quantity', 1)}
- 무게: {data.get('weight', 1)}kg
- 포장타입: Carton

이 문서는 KATI 시스템에서 자동 생성되었습니다.
        """
        
        # 파일 저장
        os.makedirs('generated_documents', exist_ok=True)
        
        commercial_invoice_filename = f"상업송장_{timestamp}.txt"
        packing_list_filename = f"포장명세서_{timestamp}.txt"
        
        with open(os.path.join('generated_documents', commercial_invoice_filename), 'w', encoding='utf-8') as f:
            f.write(commercial_invoice_content)
        
        with open(os.path.join('generated_documents', packing_list_filename), 'w', encoding='utf-8') as f:
            f.write(packing_list_content)
        
        return jsonify({
            'success': True,
            'message': '서류 생성 완료',
            'documents': {
                '상업송장': commercial_invoice_filename,
                '포장명세서': packing_list_filename
            },
            'note': '간단 버전: 텍스트 파일로 생성되었습니다'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'서류 생성 실패: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/download-document/<filename>')
def download_document(filename):
    """문서 다운로드"""
    try:
        file_path = os.path.join('generated_documents', filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': '파일을 찾을 수 없습니다'}), 404
    except Exception as e:
        return jsonify({'error': f'다운로드 실패: {str(e)}'}), 500

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
    print("✅ KATI 간단 버전 서버 시작")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 