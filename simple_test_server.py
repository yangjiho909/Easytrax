#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
간단한 테스트 서버
"""

from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({"message": "서버가 정상적으로 실행 중입니다!", "status": "success"})

@app.route('/test')
def test():
    return jsonify({"status": "success", "message": "테스트 성공"})

@app.route('/api/integrated-db-status', methods=['GET'])
def api_integrated_db_status():
    return jsonify({
        "success": True,
        "database_status": {
            "total_regulations": 2,
            "total_trade_statistics": 2,
            "total_market_analysis": 1,
            "total_strategy_reports": 1,
            "database_size": "1.2 KB",
            "last_updated": "2025-01-15T10:30:00"
        }
    })

@app.route('/api/natural-language-query', methods=['POST'])
def api_natural_language_query():
    data = request.get_json()
    query = data.get('query', '')
    
    return jsonify({
        "success": True,
        "answer": f"테스트 응답: {query}에 대한 답변입니다.",
        "data_sources": ["TEST_DATA"],
        "confidence_score": 0.85,
        "followup_questions": ["추가 질문 1", "추가 질문 2"],
        "visualization_suggestions": ["테스트 차트"],
        "timestamp": "2025-01-15T10:30:00"
    })

if __name__ == '__main__':
    print("🚀 간단한 테스트 서버 시작...")
    app.run(debug=True, host='0.0.0.0', port=5000) 