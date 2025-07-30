# AWS 배포 단계별 가이드 - 나만의 통관 수출 도우미

## 🚀 1단계: AWS CLI 설치 및 설정

### 1.1 AWS CLI 설치
```bash
# Windows (PowerShell)
winget install -e --id Amazon.AWSCLI

# 또는 Python으로 설치
pip install awscli
```

### 1.2 AWS 자격 증명 설정
```bash
aws configure
```
다음 정보를 입력하세요:
- **AWS Access Key ID**: AWS 콘솔에서 생성
- **AWS Secret Access Key**: AWS 콘솔에서 생성  
- **Default region name**: `ap-northeast-2` (서울)
- **Default output format**: `json`

## 🔑 2단계: AWS IAM 사용자 생성

### 2.1 AWS 콘솔에서 IAM 사용자 생성
1. AWS 콘솔 → IAM → 사용자 → 사용자 생성
2. 사용자 이름: `kati-deploy-user`
3. 액세스 키 생성 체크
4. 권한 정책 연결:
   - `AWSElasticBeanstalkFullAccess`
   - `AmazonS3FullAccess`
   - `AmazonEC2FullAccess`

### 2.2 액세스 키 다운로드
- Access Key ID와 Secret Access Key를 안전한 곳에 저장

## 📦 3단계: Elastic Beanstalk CLI 설치

```bash
# EB CLI 설치
pip install awsebcli

# 설치 확인
eb --version
```

## 🏗️ 4단계: 프로젝트 초기화

### 4.1 EB 초기화
```bash
# 프로젝트 디렉토리에서
eb init
```

다음 옵션들을 선택하세요:
- **Select a default region**: `ap-northeast-2`
- **Enter Application Name**: `kati-export-helper`
- **It appears you are using Python. Is this correct?**: `Y`
- **Select a platform branch**: `Python 3.11`
- **Select a platform version**: 최신 버전
- **Do you wish to set up SSH for your instances?**: `N` (나중에 설정 가능)

### 4.2 환경 생성
```bash
eb create kati-production
```

옵션:
- **Enter Environment Name**: `kati-production`
- **Enter DNS CNAME prefix**: `kati-production-2024`
- **Select a load balancer type**: `application`

## 🔧 5단계: 환경 변수 설정

### 5.1 EB 환경 변수 설정
```bash
eb setenv FLASK_ENV=production
eb setenv SECRET_KEY=your-super-secret-key-change-this
eb setenv PYTHONPATH=/var/app/current
```

### 5.2 또는 EB 콘솔에서 설정
1. EB 콘솔 → 환경 선택 → 구성
2. 소프트웨어 → 환경 속성
3. 다음 변수 추가:
   - `FLASK_ENV` = `production`
   - `SECRET_KEY` = `your-super-secret-key-change-this`
   - `PYTHONPATH` = `/var/app/current`

## 📁 6단계: 필요한 디렉토리 생성

```bash
# 로컬에서 실행
mkdir -p advanced_labels
mkdir -p generated_documents
mkdir -p uploaded_labels
mkdir -p uploaded_templates
mkdir -p temp_uploads
mkdir -p regulation_cache
mkdir -p static
```

## 🚀 7단계: 배포 실행

### 7.1 첫 배포
```bash
eb deploy
```

### 7.2 배포 상태 확인
```bash
eb status
eb health
```

### 7.3 로그 확인
```bash
eb logs
```

## 🌐 8단계: 도메인 설정 (선택사항)

### 8.1 Route 53 도메인 연결
1. EB 콘솔 → 환경 → 구성
2. 도메인 → 도메인 추가
3. 도메인 이름 입력

### 8.2 SSL 인증서 설정
1. AWS Certificate Manager에서 인증서 요청
2. EB 환경에 SSL 인증서 연결

## 📊 9단계: 모니터링 설정

### 9.1 CloudWatch 알람 설정
1. CloudWatch → 알람 → 알람 생성
2. CPU 사용률, 메모리 사용률 모니터링

### 9.2 로그 스트리밍
```bash
eb logs --all --stream
```

## 🔄 10단계: 자동 배포 설정 (GitHub Actions)

### 10.1 GitHub Secrets 설정
GitHub 저장소 → Settings → Secrets and variables → Actions에서:
- `AWS_ACCESS_KEY_ID`: AWS 액세스 키
- `AWS_SECRET_ACCESS_KEY`: AWS 시크릿 키

### 10.2 GitHub Actions 워크플로우 생성
`.github/workflows/deploy.yml` 파일 생성 (이미 가이드에 포함됨)

## 🛠️ 문제 해결

### 일반적인 문제들:

1. **메모리 부족 오류**
   ```bash
   # 인스턴스 타입 업그레이드
   eb config
   # InstanceType을 t3.medium으로 변경
   ```

2. **타임아웃 오류**
   ```bash
   # Procfile에서 timeout 값 증가
   web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 3 --timeout 300
   ```

3. **파일 업로드 실패**
   - S3 버킷 권한 확인
   - EB 환경 변수 확인

### 로그 확인 명령어:
```bash
# 실시간 로그
eb logs --all --stream

# 특정 로그 파일
eb ssh
tail -f /var/log/app.log
```

## 💰 비용 최적화 팁

1. **개발 환경**: t3.micro (무료 티어)
2. **프로덕션**: t3.small 또는 t3.medium
3. **자동 스케일링**: 필요시에만 활성화
4. **S3 수명주기**: 오래된 파일 자동 삭제

## ✅ 배포 완료 확인사항

- [ ] 웹사이트 접속 가능
- [ ] 모든 API 엔드포인트 정상 작동
- [ ] 파일 업로드/다운로드 기능 확인
- [ ] 영양성분표 생성 기능 확인
- [ ] 문서 생성 기능 확인
- [ ] 규제 정보 조회 기능 확인
- [ ] 통관 분석 기능 확인
- [ ] OCR 기능 확인
- [ ] 대시보드 기능 확인

## 📞 지원

문제 발생 시:
1. `eb logs` 명령어로 로그 확인
2. EB 콘솔에서 환경 상태 확인
3. CloudWatch 메트릭 확인
4. 보안 그룹 설정 확인

---

**배포 URL**: `http://kati-production-2024.ap-northeast-2.elasticbeanstalk.com` 