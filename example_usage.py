#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
투자보고서 생성 시스템 사용 예제

사용하기 전에 다음을 확인하세요:
1. pip install -r requirements.txt
2. .env 파일에 다음 환경변수 설정:
   - GPT_KEY=your_openai_api_key
   - NEWSAPI_KEY=your_newsapi_key
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from analysis.analyze import generate_investment_report_with_pdf, generate_multiple_reports_with_pdf

def main():
    print("=== 신한 개인프로젝트: AI 투자보고서 생성 시스템 ===\n")
    
    while True:
        print("1. 단일 기업 투자보고서 생성 (JSON + PDF, 뉴스 기간: 7-30일)")
        print("2. 여러 기업 투자보고서 생성 (JSON + PDF, 뉴스 기간: 7-30일)")
        print("3. 종료")
        
        choice = input("\n선택하세요 (1-3): ").strip()
        
        if choice == '1':
            company_name = input("분석할 회사명을 입력하세요 (예: 삼성전자): ").strip()
            if company_name:
                # 뉴스 수집 기간 선택
                while True:
                    news_period = input("뉴스 수집 기간을 입력하세요 (7-30일, 기본값: 7): ").strip()
                    if not news_period:  # 빈 입력시 기본값 사용
                        news_days = 7
                        break
                    try:
                        news_days = int(news_period)
                        if 7 <= news_days <= 30:
                            break
                        else:
                            print("❌ 뉴스 수집 기간은 7일에서 30일 사이여야 합니다.")
                    except ValueError:
                        print("❌ 숫자를 입력해주세요.")
                
                print(f"\n{company_name} 투자보고서를 생성합니다... (뉴스 기간: {news_days}일)")
                try:
                    result = generate_investment_report_with_pdf(company_name, news_days=news_days)
                    
                    if 'error' not in result:
                        print(f"✅ JSON 보고서가 {result['json_file']}에 저장되었습니다.")
                        if result.get('pdf_file'):
                            print(f"✅ PDF 보고서가 {result['pdf_file']}에 저장되었습니다.")
                        
                        # 요약 출력을 위해 JSON 파일 읽기
                        import json
                        with open(result['json_file'], 'r', encoding='utf-8') as f:
                            report_data = json.load(f)
                        
                        print(f"\n📊 {company_name} 투자보고서 요약:")
                        print(f"현재가: {report_data['stock_data']['current_price']}원")
                        print(f"전일대비: {report_data['stock_data']['change']}원 ({report_data['stock_data']['change_percent']}%)")
                        print(f"분석된 뉴스: {report_data['news_count']}개")
                        print("\n" + "="*50)
                    else:
                        print(f"❌ 오류: {result['error']}")
                        
                except Exception as e:
                    print(f"❌ 오류 발생: {str(e)}")
            else:
                print("❌ 회사명을 입력해주세요.")
                
        elif choice == '2':
            companies_input = input("분석할 회사들을 쉼표로 구분하여 입력하세요 (예: 삼성전자,SK하이닉스,NAVER): ").strip()
            if companies_input:
                companies = [company.strip() for company in companies_input.split(',')]
                
                # 뉴스 수집 기간 선택
                while True:
                    news_period = input("뉴스 수집 기간을 입력하세요 (7-30일, 기본값: 7): ").strip()
                    if not news_period:  # 빈 입력시 기본값 사용
                        news_days = 7
                        break
                    try:
                        news_days = int(news_period)
                        if 7 <= news_days <= 30:
                            break
                        else:
                            print("❌ 뉴스 수집 기간은 7일에서 30일 사이여야 합니다.")
                    except ValueError:
                        print("❌ 숫자를 입력해주세요.")
                
                print(f"\n{len(companies)}개 기업의 투자보고서를 생성합니다... (뉴스 기간: {news_days}일)")
                
                try:
                    results = generate_multiple_reports_with_pdf(companies, news_days=news_days)
                    
                    # 결과 요약 출력
                    successful_count = 0
                    failed_count = 0
                    
                    for company_name, result in results.items():
                        if 'error' not in result:
                            successful_count += 1
                            print(f"✅ {company_name}: JSON({result['json_file']}), PDF({result.get('pdf_file', 'N/A')})")
                        else:
                            failed_count += 1
                            print(f"❌ {company_name}: {result['error']}")
                    
                    print(f"\n📊 최종 결과: 성공 {successful_count}개, 실패 {failed_count}개")
                    
                except Exception as e:
                    print(f"❌ 오류 발생: {str(e)}")
            else:
                print("❌ 회사명들을 입력해주세요.")
                
        elif choice == '3':
            print("프로그램을 종료합니다.")
            break
            
        else:
            print("❌ 잘못된 선택입니다. 1-3 중에서 선택해주세요.")
        
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()