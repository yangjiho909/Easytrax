#!/bin/bash

echo "🚀 KATI 애플리케이션 배포 시작..."
echo "=================================="

# 1. 프로젝트 디렉토리로 이동
echo "📁 1단계: 프로젝트 디렉토리 설정..."
cd /home/ec2-user/kati-app
echo "✅ 디렉토리 설정 완료"

# 2. 가상환경 생성 및 활성화
echo "🔧 2단계: 가상환경 설정..."
python3 -m venv venv
source venv/bin/activate
echo "✅ 가상환경 설정 완료"

# 3. 필요한 패키지 설치
echo "📦 3단계: Python 패키지 설치..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ 패키지 설치 완료"

# 4. 애플리케이션 파일 복사 (로컬에서 업로드된 경우)
echo "📄 4단계: 애플리케이션 파일 설정..."
# 여기서는 로컬 파일을 업로드하는 것으로 가정
# 실제로는 git clone이나 scp를 사용할 수 있습니다

# 5. Gunicorn 서비스 파일 생성
echo "⚙️ 5단계: Gunicorn 서비스 설정..."
sudo tee /etc/systemd/system/kati-app.service > /dev/null <<EOF
[Unit]
Description=KATI Export Helper Application
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/kati-app
Environment="PATH=/home/ec2-user/kati-app/venv/bin"
ExecStart=/home/ec2-user/kati-app/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 6. 서비스 시작
echo "🚀 6단계: 애플리케이션 서비스 시작..."
sudo systemctl daemon-reload
sudo systemctl enable kati-app
sudo systemctl start kati-app
echo "✅ 서비스 시작 완료"

# 7. 상태 확인
echo "📊 7단계: 서비스 상태 확인..."
echo "KATI 앱 상태: $(sudo systemctl is-active kati-app)"
echo "Nginx 상태: $(sudo systemctl is-active nginx)"
echo "포트 5000 확인: $(netstat -tlnp | grep :5000 || echo '포트 5000에서 실행 중이지 않음')"

# 8. SSL 인증서 설정 (도메인이 있는 경우)
echo "🔒 8단계: SSL 인증서 설정 (선택사항)..."
echo "도메인이 있다면 다음 명령어로 SSL 인증서를 발급받을 수 있습니다:"
echo "sudo certbot --nginx -d your-domain.com"

echo "=================================="
echo "🎉 배포 완료!"
echo "애플리케이션 URL: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
echo "==================================" 