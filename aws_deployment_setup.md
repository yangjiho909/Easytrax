# 🚀 AWS 배포 설정 완료 가이드

## ✅ 완료된 작업

### 1. GitHub Actions 워크플로우 설정
- `.github/workflows/deploy-aws.yml` 생성
- 자동 배포 파이프라인 구성
- AWS Elastic Beanstalk 배포 자동화

### 2. AWS Elastic Beanstalk 설정
- `.ebextensions/01_flask.config` - Flask 애플리케이션 설정
- `.ebextensions/02_packages.config` - 시스템 패키지 설치
- `.ebextensions/03_cloudwatch.config` - 로깅 설정
- `.ebextensions/04_autoscaling.config` - 자동 스케일링 설정

### 3. 배포 파일 최적화
- `Procfile` - Gunicorn 설정 최적화
- `runtime.txt` - Python 3.11 버전 설정
- `.ebignore` - 배포 제외 파일 설정

## 🔧 AWS 설정 필요사항

### 1. AWS 계정 설정
```bash
# AWS CLI 설치
pip install awscli

# AWS 자격 증명 설정
aws configure
```

### 2. GitHub Secrets 설정
GitHub 저장소 설정에서 다음 시크릿을 추가해야 합니다:

- `AWS_ACCESS_KEY_ID`: AWS 액세스 키
- `AWS_SECRET_ACCESS_KEY`: AWS 시크릿 키

### 3. AWS 서비스 활성화
- Elastic Beanstalk
- S3 (파일 저장용)
- CloudWatch (모니터링)

## 🚀 배포 프로세스

### 1. 자동 배포
- `main` 브랜치에 푸시하면 자동으로 배포됩니다
- GitHub Actions가 AWS Elastic Beanstalk에 배포를 진행합니다

### 2. 수동 배포 (필요시)
```bash
# EB CLI 설치
pip install awsebcli

# EB 초기화
eb init kati-export-helper --region ap-northeast-2 --platform "Python 3.11"

# 환경 생성
eb create kati-production --elb-type application --instance-type t3.small

# 배포
eb deploy kati-production
```

## 📊 모니터링 및 관리

### 1. 배포 상태 확인
- GitHub Actions 탭에서 배포 진행상황 확인
- AWS Elastic Beanstalk 콘솔에서 환경 상태 확인

### 2. 로그 확인
```bash
# EB 로그 확인
eb logs

# 실시간 로그 스트리밍
eb logs --all --stream
```

### 3. 애플리케이션 접속
- 배포 완료 후 제공되는 URL로 접속
- 예: `http://kati-production.elasticbeanstalk.com`

## 🔒 보안 설정

### 1. 환경 변수
- `SECRET_KEY`: 프로덕션용 시크릿 키
- `FLASK_ENV`: production
- `FLASK_DEBUG`: false

### 2. 보안 그룹
- HTTP (80)
- HTTPS (443)
- SSH (22) - 관리용

## 💰 비용 최적화

### 1. 인스턴스 타입
- 개발: t3.micro (무료 티어)
- 프로덕션: t3.small (권장)

### 2. 자동 스케일링
- CPU 사용률 80% 초과 시 인스턴스 추가
- CPU 사용률 20% 미만 시 인스턴스 감소
- 최소 1개, 최대 4개 인스턴스

## 🛠️ 문제 해결

### 1. 일반적인 문제들
- **메모리 부족**: 인스턴스 타입 업그레이드
- **타임아웃**: Gunicorn 워커 수 조정
- **파일 업로드 실패**: S3 설정 확인

### 2. 로그 확인 방법
```bash
# EB 로그
eb logs

# 애플리케이션 로그
eb ssh
tail -f /var/log/app.log
```

## 📈 성능 최적화

### 1. Gunicorn 설정
- 워커 수: 3개
- 타임아웃: 120초
- 최대 요청: 1000개

### 2. 자동 스케일링
- CPU 임계값: 20-80%
- 스케일링 지속시간: 5분

## 🔗 도메인 설정 (선택사항)

### 1. Route 53 설정
- 도메인 등록 또는 기존 도메인 연결
- A 레코드로 EB 환경 연결

### 2. SSL 인증서
- AWS Certificate Manager에서 무료 인증서 발급
- EB 환경에 자동 적용

## 📞 지원 및 문의

문제가 발생하면 다음을 확인하세요:
1. GitHub Actions 로그
2. EB 로그: `eb logs`
3. AWS CloudWatch 메트릭
4. 보안 그룹 설정

---

**배포 완료 후 확인사항:**
- [ ] GitHub Actions 배포 성공
- [ ] 애플리케이션 접속 가능
- [ ] 파일 업로드/다운로드 정상 작동
- [ ] 로깅 설정 확인
- [ ] 자동 스케일링 설정 확인 