#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from src.analysis.outlook_generator import InvestmentReportGenerator

def test_korean_pdf():
    """한글 PDF 생성 테스트"""
    print("한글 PDF 생성 테스트를 시작합니다...")
    
    # 보고서 생성기 초기화
    generator = InvestmentReportGenerator()
    
    # 테스트용 간단한 보고서 데이터
    test_report = {
        "symbol": "005930",
        "company_name": "삼성전자",
        "report_date": "2024-01-15 14:30:00",
        "analysis_period": "3mo",
        "stock_data": {
            "current_price": 75000,
            "change": 1500,
            "change_percent": 2.04,
            "volume": 15000000,
            "pe_ratio": 15.5,
            "dividend_yield": 2.1
        },
        "news_count": 5,
        "report_content": """## 투자 보고서 - 삼성전자 (005930)

### 1. 기업 개요
삼성전자는 세계 최대의 반도체 및 전자제품 제조업체 중 하나입니다.

### 2. 최근 주가 동향 분석
현재 주가는 75,000원으로 전일 대비 1,500원 상승했습니다.

### 3. 재무 지표 분석
PER 15.5배로 업계 평균 대비 적정 수준을 보이고 있습니다.

### 4. 뉴스 및 이벤트 분석
최근 반도체 시장 회복세와 관련된 긍정적인 뉴스가 주가에 긍정적 영향을 미치고 있습니다.

### 5. 투자 의견
현재 시점에서 매수 의견을 유지합니다.

### 6. 투자 전망
단기적으로는 80,000원, 중기적으로는 90,000원 수준을 목표로 설정합니다."""
    }
    
    try:
        # PDF 생성
        print("PDF 파일을 생성하는 중...")
        pdf_path = generator.create_pdf_report(test_report)
        
        if pdf_path and not pdf_path.startswith("PDF 생성 중 오류"):
            print(f"✅ PDF 생성 성공: {pdf_path}")
            print("한글 텍스트가 제대로 표시되는지 확인해주세요.")
        else:
            print(f"❌ PDF 생성 실패: {pdf_path}")
            
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    test_korean_pdf() 