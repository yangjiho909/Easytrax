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

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({"message": "Hello from KATI!", "status": "ok"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 