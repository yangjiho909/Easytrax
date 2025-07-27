# 🌐 KATI MVP 통합 수출 지원 시스템

## 📋 프로젝트 개요

KATI MVP 통합 수출 지원 시스템은 한국 기업의 해외 수출을 지원하는 종합적인 웹 플랫폼입니다. 실시간 규제정보 조회, 통관 거부사례 분석, 규제 준수성 분석, 자동 서류 생성, 영양정보 라벨 생성 등의 기능을 제공합니다.

## 🚀 주요 기능

### 1. 📊 실시간 규제정보 조회
- **중국**: 식품의약품감독관리총국 실시간 크롤링
- **미국**: FDA 공식 API 연동
- **6시간마다 자동 업데이트**

### 2. 🔍 AI 기반 통관 거부사례 분석
- 머신러닝 기반 유사도 분석
- 중국, 미국 통관 거부사례 검색
- 실시간 분석 결과 제공

### 3. ✅ 규제 준수성 분석
- 제품별 규제 준수성 체크
- 개선 방안 제시
- 점수 기반 평가 시스템

### 4. 📄 자동 서류 생성
- 14종 수출 서류 자동 생성
- 국가별 맞춤형 템플릿
- 실시간 규제정보 반영

### 5. 🏷️ 영양정보 라벨 생성
- 중국 2027년 규정 준수
- 미국 FDA 2025년 규정 준수
- 이미지 및 텍스트 형태 제공

## 🛠️ 기술 스택

- **Backend**: Python 3.9, Flask 3.1.1
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **AI/ML**: scikit-learn, soynlp
- **Data Processing**: pandas
- **Web Scraping**: BeautifulSoup4, requests
- **Image Processing**: Pillow
- **Deployment**: Render, gunicorn

## 📦 설치 및 실행

### 로컬 개발 환경

1. **저장소 클론**
```bash
git clone <repository-url>
cd KATI2
```

2. **의존성 설치**
```bash
pip install -r requirements.txt
```

3. **애플리케이션 실행**
```bash
python app.py
```

4. **브라우저에서 접속**
```
http://localhost:5000
```

### 배포 환경

이 프로젝트는 [Render](https://render.com)에서 배포됩니다.

## 🌐 배포된 웹사이트

**URL**: [https://kati-customs-helper.onrender.com](https://kati-customs-helper.onrender.com)

## 📁 프로젝트 구조

```
KATI2/
├── app.py                          # 메인 Flask 애플리케이션
├── requirements.txt                # Python 의존성
├── Procfile                       # Render 배포 설정
├── render.yaml                    # Render 서비스 설정
├── runtime.txt                    # Python 버전
├── templates/                     # HTML 템플릿
│   ├── index.html                # 메인 페이지
│   ├── regulation_info.html      # 규제정보 페이지
│   ├── customs_analysis.html     # 통관분석 페이지
│   ├── compliance_analysis.html  # 준수성분석 페이지
│   ├── document_generation.html  # 서류생성 페이지
│   └── nutrition_label.html      # 영양라벨 페이지
├── model/                        # AI 모델 파일
├── data/                         # 데이터 파일
└── advanced_labels/              # 생성된 라벨 이미지
```

## 🔧 API 엔드포인트

### 규제정보 API
- `POST /api/regulation-info`
- 국가별 실시간 규제정보 조회

### 통관분석 API
- `POST /api/customs-analysis`
- AI 기반 통관 거부사례 분석

### 준수성분석 API
- `POST /api/compliance-analysis`
- 규제 준수성 분석

### 서류생성 API
- `POST /api/document-generation`
- 자동 서류 생성

### 영양라벨 API
- `POST /api/nutrition-label`
- 영양정보 라벨 생성

## 📊 데이터 출처

- **중국**: 중국 식품의약품감독관리총국 (NMPA)
- **미국**: 미국 식품의약품청 (FDA)
- **한국**: 식품의약품안전처 (MFDS)

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해 주세요.

---

**개발팀**: KATI MVP 개발팀  
**최종 업데이트**: 2025년 7월 27일 