# AWS 배포 가이드 - 나만의 통관 수출 도우미

## 🚀 AWS 배포 옵션

### 1. AWS Elastic Beanstalk (권장)
- 가장 간단하고 관리가 쉬운 방법
- 자동 스케일링 및 로드 밸런싱
- SSL 인증서 자동 관리

### 2. AWS EC2 + Docker
- 더 많은 제어권 필요
- 커스텀 설정 가능
- 비용 효율적

### 3. AWS Lambda + API Gateway
- 서버리스 아키텍처
- 사용량 기반 과금
- 제한사항 있음 (15분 타임아웃)

## 📋 사전 준비사항

### 1. AWS 계정 설정
```bash
# AWS CLI 설치
pip install awscli

# AWS 자격 증명 설정
aws configure
```

### 2. 필요한 AWS 서비스
- Elastic Beanstalk (또는 EC2)
- S3 (파일 저장용)
- RDS (데이터베이스, 선택사항)
- CloudFront (CDN, 선택사항)

## 🔧 배포 파일 설정

### 1. requirements.txt (이미 존재)
- Python 의존성 관리

### 2. Procfile (Elastic Beanstalk용)
```
web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 3 --timeout 120
```

### 3. .ebextensions/01_flask.config
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: app:app
  aws:elasticbeanstalk:application:environment:
    FLASK_ENV: production
    PYTHONPATH: /var/app/current:$PYTHONPATH
  aws:autoscaling:launchconfiguration:
    InstanceType: t3.small
  aws:elasticbeanstalk:environment:
    EnvironmentType: LoadBalanced
```

### 4. .ebextensions/02_packages.config
```yaml
packages:
  yum:
    gcc: []
    python3-devel: []
    libjpeg-devel: []
    zlib-devel: []
    freetype-devel: []
    lcms2-devel: []
    libwebp-devel: []
    tcl-devel: []
    tk-devel: []
    libffi-devel: []
    openssl-devel: []
```

## 🚀 배포 단계

### 1. Elastic Beanstalk 배포
```bash
# EB CLI 설치
pip install awsebcli

# EB 초기화
eb init

# 환경 생성
eb create kati-production

# 배포
eb deploy
```

### 2. EC2 배포
```bash
# EC2 인스턴스에 접속
ssh -i your-key.pem ec2-user@your-instance-ip

# Python 및 의존성 설치
sudo yum update -y
sudo yum install python3 python3-pip -y

# 애플리케이션 다운로드
git clone your-repository
cd your-app

# 의존성 설치
pip3 install -r requirements.txt

# Gunicorn으로 실행
gunicorn app:app --bind 0.0.0.0:8000 --workers 3
```

## 🔒 보안 설정

### 1. 환경 변수 설정
```bash
# Elastic Beanstalk 환경 변수
FLASK_ENV=production
SECRET_KEY=your-secret-key
DATABASE_URL=your-database-url
```

### 2. 보안 그룹 설정
- HTTP (80)
- HTTPS (443)
- SSH (22) - EC2만

## 📊 모니터링 및 로깅

### 1. CloudWatch 설정
```yaml
# .ebextensions/03_cloudwatch.config
files:
  "/opt/elasticbeanstalk/tasks/taillogs.d/app.conf":
    mode: "000755"
    owner: root
    group: root
    content: |
      /var/log/app.log
      /var/log/nginx/access.log
      /var/log/nginx/error.log
```

### 2. 애플리케이션 로깅
```python
import logging
from flask import Flask

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)
```

## 💰 비용 최적화

### 1. 인스턴스 타입 선택
- 개발: t3.micro (무료 티어)
- 프로덕션: t3.small 또는 t3.medium

### 2. 자동 스케일링 설정
```yaml
# .ebextensions/04_autoscaling.config
option_settings:
  aws:autoscaling:trigger:
    BreachDuration: 5
    LowerBreachScaleIncrement: -1
    LowerThreshold: 20
    MeasureName: CPUUtilization
    Period: 5
    UpperBreachScaleIncrement: 1
    UpperThreshold: 80
```

## 🔄 CI/CD 파이프라인

### 1. GitHub Actions 설정
```yaml
# .github/workflows/deploy.yml
name: Deploy to AWS
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Deploy to EB
      uses: einaregilsson/beanstalk-deploy@v21
      with:
        aws_access_key: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws_secret_key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        application_name: kati-app
        environment_name: kati-production
        region: ap-northeast-2
        version_label: ${{ github.sha }}
        deployment_package: ./
```

## 🛠️ 문제 해결

### 1. 일반적인 문제들
- 메모리 부족: 인스턴스 타입 업그레이드
- 타임아웃: Gunicorn 워커 수 조정
- 파일 업로드 실패: S3 설정 확인

### 2. 로그 확인
```bash
# EB 로그 확인
eb logs

# 실시간 로그 스트리밍
eb logs --all --stream
```

## 📈 성능 최적화

### 1. 정적 파일 처리
```python
# S3에 정적 파일 업로드
from flask import send_from_directory
import boto3

s3 = boto3.client('s3')
```

### 2. 캐싱 설정
```python
# Redis 캐싱 (선택사항)
from flask_caching import Cache

cache = Cache(config={'CACHE_TYPE': 'redis'})
```

## 🔗 도메인 및 SSL 설정

### 1. Route 53 설정
- 도메인 등록 또는 기존 도메인 연결
- A 레코드로 EB 환경 연결

### 2. SSL 인증서
- AWS Certificate Manager에서 무료 인증서 발급
- EB 환경에 자동 적용

## 📞 지원 및 문의

문제가 발생하면 다음을 확인하세요:
1. EB 로그: `eb logs`
2. 애플리케이션 로그
3. AWS CloudWatch 메트릭
4. 보안 그룹 설정

---

**배포 완료 후 확인사항:**
- [ ] 애플리케이션 접속 가능
- [ ] 파일 업로드/다운로드 정상 작동
- [ ] 데이터베이스 연결 확인
- [ ] SSL 인증서 적용 확인
- [ ] 모니터링 설정 확인 