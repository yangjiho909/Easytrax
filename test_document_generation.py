#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📄 서류생성 API 테스트 스크립트
- 서류생성 API의 PDF 생성 기능을 테스트
- 좌표 매핑과 파일 업로드 상태 확인
"""

import requests
import json
import time

def test_document_generation_api():
    """서류생성 API 테스트"""
    print("="*60)
    print("서류생성 API 테스트")
    print("="*60)
    
    # 테스트 데이터
    test_data = {
        "country": "중국",
        "product_info": {
            "name": "테스트 라면",
            "description": "맛있는 테스트 라면",
            "quantity": "1000",
            "unit_price": "1.00",
            "total_amount": "1000.00"
        },
        "company_info": {
            "name": "테스트 회사",
            "address": "서울시 강남구 테스트로 123",
            "phone": "02-1234-5678",
            "email": "test@company.com",
            "representative": "홍길동"
        },
        "buyer_info": {
            "name": "중국 구매자",
            "address": "중국 상하이시 테스트구 456",
            "phone": "+86-123-4567-8900",
            "email": "buyer@china.com",
            "notify_party": "중국 통관업체"
        },
        "transport_info": {
            "departure_date": "2025-08-01",
            "vessel_flight": "VESSEL001",
            "from_location": "인천항",
            "to_location": "상하이항",
            "delivery_terms": "FOB"
        },
        "payment_info": {
            "payment_terms": "L/C",
            "lc_number": "LC2025001",
            "lc_date": "2025-07-15",
            "reference": "REF001"
        },
        "packing_details": {
            "package_count": "100",
            "package_type": "박스",
            "shipping_marks": "TEST/MARK",
            "net_weight": "500kg",
            "gross_weight": "550kg",
            "dimensions": "50x30x20cm"
        },
        "selected_documents": ["상업송장", "포장명세서"],
        "customization": {
            "language": "ko",
            "format": "pdf"
        }
    }
    
    try:
        print("📤 API 요청 전송 중...")
        print(f"📋 선택된 서류: {test_data['selected_documents']}")
        
        response = requests.post(
            "http://localhost:5000/api/document-generation",
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=60
        )
        
        print(f"📥 응답 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API 호출 성공!")
            
            try:
                data = response.json()
                print(f"📋 응답 키: {list(data.keys())}")
                
                if 'success' in data:
                    print(f"✅ 성공 여부: {data['success']}")
                
                if 'message' in data:
                    print(f"📝 메시지: {data['message']}")
                
                if 'generated_count' in data:
                    print(f"📄 생성된 파일 수: {data['generated_count']}")
                
                if 'pdf_files' in data:
                    print(f"📁 PDF 파일들: {data['pdf_files']}")
                
                if 'download_urls' in data:
                    print(f"🔗 다운로드 URL들:")
                    for doc_name, url in data['download_urls'].items():
                        print(f"  - {doc_name}: {url}")
                
                if 'documents' in data:
                    print(f"📋 생성된 문서 내용:")
                    for doc_name, content in data['documents'].items():
                        print(f"  - {doc_name}: {len(str(content))} 문자")
                
                print("🎉 서류생성 API가 정상적으로 작동합니다!")
                return True
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON 파싱 오류: {e}")
                print(f"📄 응답 내용: {response.text[:500]}...")
                return False
                
        else:
            print(f"❌ API 호출 실패 (상태 코드: {response.status_code})")
            print(f"📄 응답 내용: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 연결 실패 - 서버가 실행 중인지 확인하세요")
        print("서버 실행 명령어: python app.py")
        return False
        
    except requests.exceptions.Timeout:
        print("❌ 타임아웃 - 서버 응답이 너무 느립니다")
        return False
        
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {str(e)}")
        return False

def test_file_upload_status():
    """파일 업로드 상태 확인"""
    print("\n" + "="*50)
    print("파일 업로드 상태 확인")
    print("="*50)
    
    import os
    
    # 필요한 파일들 확인
    required_files = [
        "uploaded_templates/상업송장 좌표 반영.json",
        "uploaded_templates/포장명세서 좌표 반영.json",
        "uploaded_templates/상업송장 빈 템플릿.pdf",
        "uploaded_templates/포장명세서 빈 템플릿.pdf"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"✅ {file_path} ({file_size} bytes)")
        else:
            print(f"❌ {file_path} (파일 없음)")
    
    # generated_documents 폴더 확인
    if os.path.exists("generated_documents"):
        files = os.listdir("generated_documents")
        print(f"✅ generated_documents 폴더 ({len(files)}개 파일)")
    else:
        print("❌ generated_documents 폴더 (폴더 없음)")

def test_coordinate_mapping():
    """좌표 매핑 테스트"""
    print("\n" + "="*50)
    print("좌표 매핑 테스트")
    print("="*50)
    
    try:
        import json
        
        # 상업송장 좌표 파일 확인
        with open("uploaded_templates/상업송장 좌표 반영.json", 'r', encoding='utf-8') as f:
            commercial_coords = json.load(f)
        
        print(f"✅ 상업송장 좌표 필드: {list(commercial_coords.keys())}")
        
        # 포장명세서 좌표 파일 확인
        with open("uploaded_templates/포장명세서 좌표 반영.json", 'r', encoding='utf-8') as f:
            packing_coords = json.load(f)
        
        print(f"✅ 포장명세서 좌표 필드: {list(packing_coords.keys())}")
        
    except Exception as e:
        print(f"❌ 좌표 매핑 테스트 실패: {e}")

if __name__ == "__main__":
    print("🚀 서류생성 API 종합 테스트 시작")
    
    # 파일 업로드 상태 확인
    test_file_upload_status()
    
    # 좌표 매핑 테스트
    test_coordinate_mapping()
    
    # API 테스트
    success = test_document_generation_api()
    
    print("\n" + "="*60)
    if success:
        print("🎉 모든 테스트가 성공적으로 완료되었습니다!")
    else:
        print("❌ 일부 테스트에서 문제가 발생했습니다.")
    print("="*60) 