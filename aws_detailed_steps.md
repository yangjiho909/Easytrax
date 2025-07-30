# AWS 배포 상세 단계별 가이드 - 나만의 통관 수출 도우미

## 🚀 1단계: AWS CLI 설치

### 1.1 Windows에서 AWS CLI 설치
```bash
# 방법 1: winget 사용 (권장)
winget install -e --id Amazon.AWSCLI

# 방법 2: Python으로 설치
pip install awscli

# 설치 확인
aws --version
```

### 1.2 설치 후 터미널 재시작
PowerShell을 완전히 닫고 다시 열어주세요.

---

## 🔑 2단계: AWS IAM 사용자 생성

### 2.1 AWS 콘솔 접속
1. 브라우저에서 [AWS 콘솔](https://console.aws.amazon.com/) 접속
2. AWS 계정으로 로그인

### 2.2 IAM 서비스로 이동
1. AWS 콘솔 상단 검색창에 "IAM" 입력
2. IAM 서비스 클릭

### 2.3 사용자 생성
1. 왼쪽 메뉴에서 **"사용자"** 클릭
2. **"사용자 생성"** 버튼 클릭

### 2.4 사용자 세부 정보 입력
```
사용자 이름: kati-deploy-user
액세스 키 - 프로그래밍 방식 액세스: ✅ 체크
```

### 2.5 권한 설정
1. **"기존 정책 직접 연결"** 선택
2. 다음 정책들을 검색하여 체크:
   - `AWSElasticBeanstalkFullAccess`
   - `AmazonS3FullAccess`
   - `AmazonEC2FullAccess`
   - `CloudWatchFullAccess`

### 2.6 사용자 생성 완료
1. **"다음: 태그"** → **"다음: 검토"** → **"사용자 생성"**
2. **중요**: 액세스 키 정보를 안전한 곳에 저장!

### 2.7 액세스 키 정보 저장
생성된 다음 정보를 메모장에 저장:
```
AWS Access Key ID: AKIA...
AWS Secret Access Key: ...
```

---

## ⚙️ 3단계: AWS 자격 증명 설정

### 3.1 PowerShell에서 AWS 설정
```bash
aws configure
```

### 3.2 다음 정보 입력
```
AWS Access Key ID [None]: AKIA... (2단계에서 생성한 키)
AWS Secret Access Key [None]: ... (2단계에서 생성한 키)
Default region name [None]: ap-northeast-2
Default output format [None]: json
```

### 3.3 설정 확인
```bash
aws sts get-caller-identity
```
성공하면 다음과 같은 정보가 출력됩니다:
```json
{
    "UserId": "AIDA...",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/kati-deploy-user"
}
```

---

## 📦 4단계: Elastic Beanstalk CLI 설치

### 4.1 EB CLI 설치
```bash
pip install awsebcli
```

### 4.2 설치 확인
```bash
eb --version
```
출력 예시: `EB CLI 3.20.10 (Python 3.11.x)`

---

## 🏗️ 5단계: 프로젝트 초기화

### 5.1 프로젝트 디렉토리로 이동
```bash
cd "C:\Users\양지호\OneDrive - 숭실대학교 - Soongsil University\바탕 화면\대외 활동\산업통상자원부 데이터공모전\KATI2"
```

### 5.2 EB 초기화
```bash
eb init
```

### 5.3 초기화 옵션 선택
다음과 같이 선택하세요:

```
Select a default region
1) us-east-1 : US East (N. Virginia)
2) us-west-1 : US West (N. California)
3) us-west-2 : US West (Oregon)
4) eu-west-1 : EU (Ireland)
5) eu-central-1 : EU (Frankfurt)
6) ap-south-1 : Asia Pacific (Mumbai)
7) ap-northeast-1 : Asia Pacific (Tokyo)
8) ap-northeast-2 : Asia Pacific (Seoul)
9) ap-southeast-1 : Asia Pacific (Singapore)
10) ap-southeast-2 : Asia Pacific (Sydney)
11) sa-east-1 : South America (São Paulo)
(default is 3): 8

Enter Application Name
(default is "KATI2"): kati-export-helper

It appears you are using Python. Is this correct?
(Y/n): Y

Select a platform branch.
1) Python 3.11
2) Python 3.10
3) Python 3.9
4) Python 3.8
(default is 1): 1

Select a platform version.
1) Python 3.11 running on 64bit Amazon Linux 2
2) Python 3.11 running on 64bit Amazon Linux 2023
(default is 1): 1

Do you wish to set up SSH for your instances?
(Y/n): N
```

### 5.4 환경 생성
```bash
eb create kati-production
```

### 5.5 환경 생성 옵션
```
Enter Environment Name
(default is kati-production): kati-production

Enter DNS CNAME prefix
(default is kati-production): kati-production-2024

Select a load balancer type.
1) classic
2) application
3) network
(default is 2): 2

Would you like to enable Spot Fleet requests for this environment?
(Y/n): N
```

---

## 🔧 6단계: 환경 변수 설정

### 6.1 환경 변수 설정
```bash
eb setenv FLASK_ENV=production
eb setenv SECRET_KEY=your-super-secret-key-change-this-2024
eb setenv PYTHONPATH=/var/app/current
```

### 6.2 또는 EB 콘솔에서 설정
1. [EB 콘솔](https://console.aws.amazon.com/elasticbeanstalk/) 접속
2. 애플리케이션 `kati-export-helper` 선택
3. 환경 `kati-production` 선택
4. **"구성"** 클릭
5. **"소프트웨어"** 섹션에서 **"편집"** 클릭
6. **"환경 속성"** 섹션에서 다음 추가:
   ```
   FLASK_ENV = production
   SECRET_KEY = your-super-secret-key-change-this-2024
   PYTHONPATH = /var/app/current
   ```

---

## 📁 7단계: 필요한 디렉토리 생성

### 7.1 로컬에서 디렉토리 생성
```bash
# PowerShell에서 실행
mkdir advanced_labels
mkdir generated_documents
mkdir uploaded_labels
mkdir uploaded_templates
mkdir temp_uploads
mkdir regulation_cache
mkdir static
```

---

## 🚀 8단계: 배포 실행

### 8.1 첫 배포
```bash
eb deploy
```

### 8.2 배포 진행 상황 확인
배포가 진행되면서 다음과 같은 메시지들이 나타납니다:
```
Creating application version archive "app-240730_143000".
Uploading kati-export-helper/app-240730_143000.zip to S3. This may take a while.
Upload Complete.
Environment update is initiating.
```

### 8.3 배포 완료 확인
```bash
eb status
```
출력 예시:
```
Environment details for: kati-production
  Application name: kati-export-helper
  Region: ap-northeast-2
  Deployed Version: app-240730_143000
  Environment ID: e-abc123def4
  Platform: arn:aws:elasticbeanstalk:ap-northeast-2::platform/Python 3.11
  Tier: WebServer
  CNAME: kati-production-2024.ap-northeast-2.elasticbeanstalk.com
  Updated: 2024-07-30 14:30:00.000000+00:00
  Status: Ready
  Health: Green
```

### 8.4 웹사이트 접속 확인
브라우저에서 다음 URL 접속:
```
http://kati-production-2024.ap-northeast-2.elasticbeanstalk.com
```

---

## 📊 9단계: 로그 확인

### 9.1 실시간 로그 확인
```bash
eb logs --all --stream
```

### 9.2 특정 로그 파일 확인
```bash
eb ssh
# 서버에 접속 후
tail -f /var/log/app.log
```

---

## 🛠️ 문제 해결

### 메모리 부족 오류 발생 시
```bash
# 인스턴스 타입 업그레이드
eb config
# InstanceType을 t3.medium으로 변경 후 저장
eb deploy
```

### 타임아웃 오류 발생 시
```bash
# Procfile 수정
web: gunicorn app:app --bind 0.0.0.0:$PORT --workers 3 --timeout 300
eb deploy
```

### 배포 실패 시
```bash
# 로그 확인
eb logs

# 환경 재시작
eb restart
```

---

## ✅ 배포 완료 확인사항

배포가 완료되면 다음 기능들을 테스트해보세요:

1. **메인 페이지**: `/`
2. **대시보드**: `/dashboard`
3. **통관 분석**: `/customs-analysis`
4. **규제 정보**: `/regulation-info`
5. **문서 생성**: `/document-generation`
6. **영양성분표**: `/nutrition-label`
7. **파일 업로드**: 각 페이지의 파일 업로드 기능
8. **API 엔드포인트**: 모든 API가 정상 작동하는지 확인

---

## 📞 지원

문제가 발생하면:
1. `eb logs` 명령어로 로그 확인
2. EB 콘솔에서 환경 상태 확인
3. CloudWatch 메트릭 확인
4. 보안 그룹 설정 확인

**배포 URL**: `http://kati-production-2024.ap-northeast-2.elasticbeanstalk.com` 