#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 시장 진출 전략보고서 처리기
KOTRA 진출전략보고서 PDF를 파싱하여 구조화된 데이터로 변환
"""

import fitz  # PyMuPDF
import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

# 기존 파서 import
from market_entry_strategy_parser import MarketEntryStrategyParser, MarketEntryReport

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFMarketStrategyProcessor:
    """PDF 시장 진출 전략보고서 처리기"""
    
    def __init__(self):
        self.parser = MarketEntryStrategyParser()
        self.upload_dir = "uploaded_documents"
        self.cache_dir = "regulation_cache"
        
        # 디렉토리 생성
        os.makedirs(self.cache_dir, exist_ok=True)
        
        logger.info("✅ PDF 시장 진출 전략보고서 처리기 초기화 완료")
    
    def process_pdf_file(self, pdf_path: str, country: str, product: str = "일반") -> Optional[MarketEntryReport]:
        """PDF 파일을 처리하여 시장 진출 전략보고서 생성"""
        try:
            logger.info(f"🔍 PDF 처리 시작: {pdf_path}")
            
            # PDF 텍스트 추출
            pdf_text = self._extract_text_from_pdf(pdf_path)
            if not pdf_text:
                logger.error(f"❌ PDF 텍스트 추출 실패: {pdf_path}")
                return None
            
            logger.info(f"✅ PDF 텍스트 추출 완료: {len(pdf_text)} 문자")
            
            # 텍스트 파싱하여 보고서 생성
            report = self.parser.parse_report_text(
                country=country,
                product=product,
                raw_text=pdf_text,
                source="KOTRA_PDF"
            )
            
            # 캐시에 저장
            self._save_report_to_cache(report, country, product)
            
            logger.info(f"✅ {country} {product} 시장 진출 전략보고서 처리 완료")
            return report
            
        except Exception as e:
            logger.error(f"❌ PDF 처리 중 오류: {e}")
            return None
    
    def _extract_text_from_pdf(self, pdf_path: str) -> Optional[str]:
        """PDF에서 텍스트 추출"""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text()
                text += page_text + "\n"
            
            doc.close()
            return text.strip()
            
        except Exception as e:
            logger.error(f"❌ PDF 텍스트 추출 오류: {e}")
            return None
    
    def _save_report_to_cache(self, report: MarketEntryReport, country: str, product: str):
        """보고서를 캐시에 저장"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"market_strategy_{country}_{product}_{timestamp}.json"
            filepath = os.path.join(self.cache_dir, filename)
            
            # dataclass를 dict로 변환
            report_dict = report.__dict__.copy()
            
            # dataclass 객체들을 dict로 변환
            if hasattr(report, 'key_issues'):
                report_dict['key_issues'] = [issue.__dict__ for issue in report.key_issues]
            if hasattr(report, 'market_trends'):
                report_dict['market_trends'] = [trend.__dict__ for trend in report.market_trends]
            if hasattr(report, 'customs_documents'):
                report_dict['customs_documents'] = [doc.__dict__ for doc in report.customs_documents]
            if hasattr(report, 'response_strategies'):
                report_dict['response_strategies'] = [strategy.__dict__ for strategy in report.response_strategies]
            if hasattr(report, 'meta_info'):
                report_dict['meta_info'] = report.meta_info.__dict__
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report_dict, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ 캐시 저장 완료: {filepath}")
            
        except Exception as e:
            logger.error(f"❌ 캐시 저장 오류: {e}")
    
    def process_all_uploaded_pdfs(self) -> Dict[str, Any]:
        """업로드된 모든 PDF 파일 처리"""
        results = {
            "success": True,
            "processed_files": [],
            "errors": [],
            "total_files": 0,
            "successful_files": 0
        }
        
        try:
            # 업로드 디렉토리에서 PDF 파일 찾기
            pdf_files = []
            for file in os.listdir(self.upload_dir):
                if file.lower().endswith('.pdf') and '진출전략' in file:
                    pdf_files.append(file)
            
            results["total_files"] = len(pdf_files)
            logger.info(f"🔍 발견된 진출전략 PDF 파일: {len(pdf_files)}개")
            
            for pdf_file in pdf_files:
                try:
                    # 파일명에서 국가 추출
                    country = self._extract_country_from_filename(pdf_file)
                    product = self._extract_product_from_filename(pdf_file)
                    
                    pdf_path = os.path.join(self.upload_dir, pdf_file)
                    report = self.process_pdf_file(pdf_path, country, product)
                    
                    if report:
                        results["processed_files"].append({
                            "filename": pdf_file,
                            "country": country,
                            "product": product,
                            "report_id": report.report_id,
                            "status": "success"
                        })
                        results["successful_files"] += 1
                    else:
                        results["errors"].append({
                            "filename": pdf_file,
                            "error": "PDF 처리 실패"
                        })
                        
                except Exception as e:
                    results["errors"].append({
                        "filename": pdf_file,
                        "error": str(e)
                    })
            
            logger.info(f"✅ PDF 처리 완료: {results['successful_files']}/{results['total_files']} 성공")
            return results
            
        except Exception as e:
            results["success"] = False
            results["errors"].append({"error": str(e)})
            logger.error(f"❌ 전체 PDF 처리 중 오류: {e}")
            return results
    
    def _extract_country_from_filename(self, filename: str) -> str:
        """파일명에서 국가 추출"""
        if '중국' in filename:
            return '중국'
        elif '미국' in filename:
            return '미국'
        elif '한국' in filename:
            return '한국'
        else:
            return '일반'
    
    def _extract_product_from_filename(self, filename: str) -> str:
        """파일명에서 제품 추출"""
        products = ['라면', '과자', '음료', '조미료', '건조식품', '커피', '차', '과일', '채소']
        for product in products:
            if product in filename:
                return product
        return '일반'
    
    def get_processed_reports(self) -> List[Dict[str, Any]]:
        """처리된 보고서 목록 조회"""
        reports = []
        
        try:
            for file in os.listdir(self.cache_dir):
                if file.startswith('market_strategy_') and file.endswith('.json'):
                    filepath = os.path.join(self.cache_dir, file)
                    
                    with open(filepath, 'r', encoding='utf-8') as f:
                        report_data = json.load(f)
                    
                    reports.append({
                        "filename": file,
                        "country": report_data.get('country', ''),
                        "product": report_data.get('product', ''),
                        "report_date": report_data.get('report_date', ''),
                        "title": report_data.get('title', ''),
                        "source": report_data.get('source', ''),
                        "file_size": os.path.getsize(filepath)
                    })
            
            # 날짜순 정렬
            reports.sort(key=lambda x: x['report_date'], reverse=True)
            
        except Exception as e:
            logger.error(f"❌ 처리된 보고서 조회 오류: {e}")
        
        return reports
    
    def get_report_details(self, filename: str) -> Optional[Dict[str, Any]]:
        """특정 보고서 상세 정보 조회"""
        try:
            filepath = os.path.join(self.cache_dir, filename)
            
            if not os.path.exists(filepath):
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
            
            return report_data
            
        except Exception as e:
            logger.error(f"❌ 보고서 상세 정보 조회 오류: {e}")
            return None

def main():
    """메인 실행 함수"""
    processor = PDFMarketStrategyProcessor()
    
    print("🚀 PDF 시장 진출 전략보고서 처리 시작")
    print("=" * 60)
    
    # 모든 업로드된 PDF 처리
    results = processor.process_all_uploaded_pdfs()
    
    print(f"📊 처리 결과:")
    print(f"   - 총 파일 수: {results['total_files']}")
    print(f"   - 성공: {results['successful_files']}")
    print(f"   - 실패: {len(results['errors'])}")
    
    if results['processed_files']:
        print(f"\n✅ 성공적으로 처리된 파일:")
        for file_info in results['processed_files']:
            print(f"   - {file_info['filename']} ({file_info['country']} {file_info['product']})")
    
    if results['errors']:
        print(f"\n❌ 처리 실패한 파일:")
        for error_info in results['errors']:
            print(f"   - {error_info['filename']}: {error_info['error']}")
    
    # 처리된 보고서 목록 조회
    print(f"\n📋 처리된 보고서 목록:")
    reports = processor.get_processed_reports()
    for report in reports:
        print(f"   - {report['filename']} ({report['country']} {report['product']}) - {report['report_date']}")

if __name__ == "__main__":
    main() 