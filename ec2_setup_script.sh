#!/bin/bash

echo "🚀 EC2 서버 설정 시작..."
echo "=================================="

# 1. 시스템 업데이트
echo "📦 1단계: 시스템 업데이트 중..."
sudo yum update -y
echo "✅ 시스템 업데이트 완료"

# 2. Python 및 개발 도구 설치
echo "🐍 2단계: Python 및 개발 도구 설치 중..."
sudo yum install -y python3 python3-pip python3-devel gcc git
echo "✅ Python 및 개발 도구 설치 완료"

# 3. JDK 설치 (Spring Boot용)
echo "☕ 3단계: JDK 17 설치 중..."
sudo yum install -y java-17-openjdk java-17-openjdk-devel
echo "✅ JDK 17 설치 완료"

# 4. Nginx 설치 및 설정
echo "🌐 4단계: Nginx 설치 및 설정 중..."
sudo yum install -y nginx
sudo systemctl start nginx
sudo systemctl enable nginx
echo "✅ Nginx 설치 및 설정 완료"

# 5. Certbot 설치 (SSL 인증서용)
echo "🔒 5단계: Certbot 설치 중..."
sudo yum install -y epel-release
sudo yum install -y certbot python3-certbot-nginx
echo "✅ Certbot 설치 완료"

# 6. 가상환경 도구 설치
echo "🔧 6단계: 가상환경 도구 설치 중..."
sudo pip3 install virtualenv
echo "✅ 가상환경 도구 설치 완료"

# 7. 프로젝트 디렉토리 생성
echo "📁 7단계: 프로젝트 디렉토리 설정 중..."
mkdir -p /home/ec2-user/kati-app
cd /home/ec2-user/kati-app
echo "✅ 프로젝트 디렉토리 설정 완료"

# 8. 방화벽 설정
echo "🔥 8단계: 방화벽 설정 중..."
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
echo "✅ 방화벽 설정 완료"

# 9. Nginx 설정 파일 생성
echo "⚙️ 9단계: Nginx 설정 파일 생성 중..."
sudo tee /etc/nginx/conf.d/kati-app.conf > /dev/null <<EOF
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /static {
        alias /home/ec2-user/kati-app/static;
        expires 30d;
    }
}
EOF

sudo nginx -t
sudo systemctl reload nginx
echo "✅ Nginx 설정 완료"

# 10. 시스템 정보 출력
echo "📊 10단계: 시스템 정보 확인..."
echo "Python 버전: $(python3 --version)"
echo "Java 버전: $(java -version 2>&1 | head -n 1)"
echo "Nginx 상태: $(systemctl is-active nginx)"
echo "현재 디렉토리: $(pwd)"

echo "=================================="
echo "🎉 EC2 서버 설정 완료!"
echo "다음 단계: 애플리케이션 배포"
echo "==================================" 