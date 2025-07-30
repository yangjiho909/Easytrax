# AWS CLI 수동 설치 가이드

## 🚀 AWS CLI 설치 방법

### 방법 1: 공식 설치 파일 다운로드 (권장)

1. **AWS CLI 공식 다운로드 페이지 접속**
   - 브라우저에서 [AWS CLI 다운로드 페이지](https://awscli.amazonaws.com/AWSCLIV2.msi) 접속
   - 또는 https://awscli.amazonaws.com/AWSCLIV2.msi 직접 다운로드

2. **설치 파일 실행**
   - 다운로드한 `AWSCLIV2.msi` 파일을 더블클릭
   - 설치 마법사의 안내에 따라 설치 진행

3. **설치 완료 후 PowerShell 재시작**
   - PowerShell을 완전히 닫고 다시 열기

4. **설치 확인**
   ```bash
   aws --version
   ```

### 방법 2: Python pip 사용 (대안)

만약 방법 1이 안 되면:
```bash
pip install awscli
```

---

## ⚙️ AWS 자격 증명 설정

AWS CLI가 설치되면 다음 단계로 진행:

### 1. AWS 설정
```bash
aws configure
```

### 2. 다음 정보 입력
```
AWS Access Key ID [None]: AKIA... (생성한 액세스 키 ID)
AWS Secret Access Key [None]: ... (생성한 시크릿 액세스 키)
Default region name [None]: ap-northeast-2
Default output format [None]: json
```

### 3. 설정 확인
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

## 📦 EB CLI 설치

AWS CLI 설정이 완료되면:

```bash
pip install awsebcli
```

설치 확인:
```bash
eb --version
```

---

## 🚀 다음 단계

AWS CLI 설치가 완료되면 다음 단계로 진행:

1. **프로젝트 초기화**: `eb init`
2. **환경 생성**: `eb create kati-production`
3. **배포**: `eb deploy`

---

## 🛠️ 문제 해결

### AWS CLI가 인식되지 않는 경우
1. PowerShell을 관리자 권한으로 실행
2. 시스템 환경 변수 PATH에 AWS CLI 경로 추가
3. 컴퓨터 재시작

### 설치 오류 발생 시
1. 기존 AWS CLI 제거 후 재설치
2. Python 버전 확인 (3.7 이상 권장)
3. pip 업그레이드: `python -m pip install --upgrade pip` 