# 🚀 나만의 통관 수출 도우미 (KATI)

## 🌐 배포 상태
- **AWS Elastic Beanstalk**: 설정 완료, 자동 배포 대기 중
- **GitHub Actions**: 자동 배포 파이프라인 구성 완료
- **배포 URL**: 배포 후 `http://kati-production.elasticbeanstalk.com`

## 📋 주요 기능
- 통관 규정 분석 및 조회
- 영양성분표 자동 생성
- 문서 생성 (상업송장, 포장명세서)
- OCR 기반 문서 분석
- 실시간 규제 업데이트 모니터링

## 🚀 배포 정보
- **플랫폼**: AWS Elastic Beanstalk
- **인스턴스**: t3.small
- **자동 스케일링**: CPU 20-80% 기준
- **예상 비용**: 월 $35-50

## 🔧 기술 스택
- **Backend**: Flask, Python 3.11
- **Deployment**: AWS Elastic Beanstalk, GitHub Actions
- **Monitoring**: CloudWatch
- **Scaling**: Auto Scaling Group

---
*마지막 업데이트: 2024년 12월 19일* 