#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌐 KATI 안정 버전 - 로컬호스트 실행용
- 기본 기능만 포함
- 의존성 문제 해결
- 안정적인 실행 보장
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
import pandas as pd

# Flask 앱 생성
app = Flask(__name__)
app.secret_key = 'kati-stable-secret-key-2025'

# 기본 설정
UPLOAD_FOLDER = 'temp_uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'xlsx', 'xls', 'docx', 'doc'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 기본 데이터
SAMPLE_REGULATIONS = {
    "중국": {
        "라면": {
            "영양성분표": "GB 7718-2025 규정 준수 필요",
            "알레르기": "8대 알레르기 원료 표시 필수",
            "성분표": "원료명칭 및 함량 표시",
            "포장": "식품안전 포장재 사용"
        }
    },
    "미국": {
        "라면": {
            "영양성분표": "FDA 규정 준수 필요",
            "알레르기": "9대 알레르기 원료 표시 필수",
            "성분표": "영양성분표 필수",
            "포장": "FDA 승인 포장재 사용"
        }
    }
}

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """대시보드 페이지"""
    return render_template('dashboard.html')

@app.route('/customs-analysis')
def customs_analysis():
    """통관 분석 페이지"""
    return render_template('customs_analysis.html')

@app.route('/regulation-info')
def regulation_info():
    """규제 정보 페이지"""
    return render_template('regulation_info.html')

@app.route('/compliance-analysis')
def compliance_analysis():
    """준수성 분석 페이지"""
    return render_template('compliance_analysis.html')

@app.route('/document-generation')
def document_generation():
    """문서 생성 페이지"""
    return render_template('document_generation.html')

@app.route('/nutrition-label')
def nutrition_label():
    """영양성분표 페이지"""
    return render_template('nutrition_label.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """헬스 체크 API"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "stable-1.0.0"
    })

@app.route('/api/dashboard-stats')
def api_dashboard_stats():
    """대시보드 통계 API"""
    return jsonify({
        "success": True,
        "data": {
            "supported_countries": ["중국", "미국"],
            "total_regulations": 8,
            "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M'),
            "system_status": "정상",
            "recent_activities": [
                {
                    "type": "system_start",
                    "title": "시스템 시작",
                    "description": "안정 버전 서버가 시작되었습니다.",
                    "time": "방금 전",
                    "status": "success"
                }
            ]
        }
    })

@app.route('/api/regulation-info', methods=['POST'])
def api_regulation_info():
    """규제 정보 API"""
    try:
        data = request.get_json()
        country = data.get('country', '중국')
        product = data.get('product', '라면')
        
        regulations = SAMPLE_REGULATIONS.get(country, {}).get(product, {})
        
        return jsonify({
            "success": True,
            "regulations": regulations,
            "country": country,
            "product": product,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/customs-analysis', methods=['POST'])
def api_customs_analysis():
    """통관 분석 API"""
    try:
        data = request.get_json()
        user_input = data.get('user_input', '')
        
        # 간단한 분석 결과
        analysis_result = {
            "input": user_input,
            "analysis": "안정 버전에서는 기본 분석만 제공됩니다.",
            "risk_level": "중간",
            "suggestions": [
                "규제 정보를 확인하세요",
                "필요한 서류를 준비하세요",
                "전문가와 상담하세요"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify({
            "success": True,
            "result": analysis_result
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/compliance-analysis', methods=['POST'])
def api_compliance_analysis():
    """준수성 분석 API"""
    try:
        data = request.get_json()
        country = data.get('country', '중국')
        product = data.get('product', '라면')
        
        # 기본 준수성 분석
        compliance_result = {
            "country": country,
            "product": product,
            "overall_score": 75,
            "issues": [
                {
                    "category": "영양성분표",
                    "severity": "중간",
                    "description": "규정에 맞는 영양성분표 필요",
                    "solution": "GB 7718-2025 규정 준수"
                }
            ],
            "recommendations": [
                "규제 정보를 정확히 확인하세요",
                "필요한 서류를 미리 준비하세요"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify({
            "success": True,
            "result": compliance_result
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/document-generation', methods=['POST'])
def api_document_generation():
    """문서 생성 API"""
    try:
        data = request.get_json()
        doc_type = data.get('doc_type', '상업송장')
        country = data.get('country', '중국')
        product = data.get('product', '라면')
        
        # 기본 문서 생성
        document_content = f"""
=== {doc_type} ===
국가: {country}
제품: {product}
생성일: {datetime.now().strftime('%Y-%m-%d')}

이 문서는 안정 버전에서 생성되었습니다.
실제 사용을 위해서는 완전한 기능을 사용하세요.
        """
        
        return jsonify({
            "success": True,
            "document": {
                "type": doc_type,
                "content": document_content,
                "filename": f"{doc_type}_{country}_{product}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/nutrition-label', methods=['POST'])
def api_nutrition_label():
    """영양성분표 생성 API"""
    try:
        data = request.get_json()
        country = data.get('country', '중국')
        product_info = data.get('product_info', {})
        
        # 기본 영양성분표
        nutrition_label = {
            "country": country,
            "product_name": product_info.get('name', '라면'),
            "nutrition_info": {
                "에너지": "400 kcal",
                "단백질": "8g",
                "지방": "15g",
                "탄수화물": "60g",
                "나트륨": "1200mg"
            },
            "allergens": ["밀", "대두"],
            "regulations": SAMPLE_REGULATIONS.get(country, {}).get('라면', {}),
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify({
            "success": True,
            "label": nutrition_label
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/system-status')
def api_system_status():
    """시스템 상태 API"""
    return jsonify({
        "success": True,
        "status": {
            "version": "stable-1.0.0",
            "uptime": "정상",
            "memory_usage": "정상",
            "database_status": "정상",
            "api_status": "정상",
            "timestamp": datetime.now().isoformat()
        }
    })

if __name__ == '__main__':
    print("🚀 KATI 안정 버전 서버 시작...")
    print("📍 서버 주소: http://localhost:5000")
    print("🔧 디버그 모드: 활성화")
    print("📁 업로드 폴더:", UPLOAD_FOLDER)
    
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port) 