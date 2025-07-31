#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
간단한 Flask 서버 테스트
"""

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({"message": "서버가 정상적으로 실행 중입니다!"})

@app.route('/test')
def test():
    return jsonify({"status": "success", "message": "테스트 성공"})

if __name__ == '__main__':
    print("🚀 간단한 테스트 서버 시작...")
    app.run(debug=True, host='0.0.0.0', port=5000) 