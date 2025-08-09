#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
투자보고서 생성 데모 (PDF 포함)
"""

import sys
import os
from datetime import datetime

# 프로젝트 루트 경로 추가
sys.path.append('src')

from analysis.analyze import generate_investment_report_with_pdf

def main():
    """메인 함수"""
    print("=== AI 투자보고서 생성기 (PDF 포함) ===")
    print("주가 정보와 뉴스를 분석하여 투자보고서를 생성합니다.")
    print("JSON과 PDF 형식으로 보고서가 저장됩니다.\n")
    
    # 사용 가능한 기업 목록
    available_companies = [
        '삼성전자', 'SK하이닉스', 'LG에너지솔루션', 'NAVER', '카카오',
        'LG화학', '현대차', '기아', 'POSCO홀딩스', 'KB금융',
        '신한지주', 'LG전자', '삼성바이오로직스', '현대모비스', '셀트리온'
    ]
    
    print("📈 분석 가능한 주요 기업:")
    for i, company in enumerate(available_companies[:10], 1):
        print(f"{i:2d}. {company}")
    print("    ... 및 기타 한국 상장기업")
    
    try:
        # 기업명 입력
        company_name = input(f"\n분석할 기업명을 입력하세요: ").strip()
        
        if not company_name:
            print("기업명을 입력해주세요.")
            return
        
        # 분석 옵션 설정
        print(f"\n📊 {company_name} 투자보고서를 생성합니다...")
        print("- 주가 데이터: 최근 1개월")
        print("- 뉴스 데이터: 최근 7일")
        print("- 출력 형식: JSON + PDF")
        
        # 보고서 생성
        result = generate_investment_report_with_pdf(
            company_name=company_name,
            period='1mo',
            news_days=7,
            save_pdf=True
        )
        
        # 결과 출력
        if 'error' in result:
            print(f"❌ 오류: {result['error']}")
        else:
            print(f"\n✅ {company_name} 투자보고서 생성 완료!")
            print(f"📄 JSON 파일: {result['json_file']}")
            
            if result.get('pdf_file'):
                print(f"📑 PDF 파일: {result['pdf_file']}")
            else:
                print("⚠️  PDF 생성에 실패했지만 JSON 파일은 정상 생성되었습니다.")
            
            print(f"\n💡 생성된 파일들은 reports/ 디렉토리에서 확인할 수 있습니다.")
    
    except KeyboardInterrupt:
        print("\n\n보고서 생성이 취소되었습니다.")
    except Exception as e:
        print(f"예상치 못한 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()