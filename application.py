#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🌐 나만의 통관 수출 도우미 - AWS Elastic Beanstalk 배포용
- Flask 기반 웹 애플리케이션
- 중국, 미국 라면 수출 지원
"""

from app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False) 