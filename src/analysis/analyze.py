# GPT를 사용한 투자보고서 분석 모듈
from dotenv import load_dotenv
import os
import json
import sys
from datetime import datetime, timedelta

# 프로젝트 루트 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from fetch.stock_fetcher import get_stock_data
from fetch.news_fetcher import get_latest_news

load_dotenv()

from openai import OpenAI
client = OpenAI(api_key=os.getenv("GPT_KEY"))

def generate_investment_report(company_name, period='1mo', news_days=7):
    """
    주가 정보와 뉴스 정보를 기반으로 투자보고서를 생성하는 함수
    
    Parameters:
    - company_name: 회사명 (예: '삼성전자')
    - period: 주가 데이터 기간 (기본값: '1mo')
    - news_days: 뉴스 검색 기간 (기본값: 7일)
    
    Returns:
    - GPT가 생성한 투자보고서 (JSON 형태)
    """
    try:
        print(f"=== {company_name} 투자보고서 생성 중 ===")
        
        # 1. 주가 데이터 가져오기
        print("1. 주가 데이터 수집 중...")
        stock_data = get_stock_data(company_name, period=period)
        stock_info = json.loads(stock_data)
        
        if 'error' in stock_info:
            return {"error": f"주가 데이터를 가져올 수 없습니다: {stock_info['error']}"}
        
        # 2. 뉴스 데이터 가져오기
        print("2. 관련 뉴스 수집 중...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=news_days)
        
        news_data = get_latest_news(
            query=company_name,
            from_date=start_date.strftime('%Y-%m-%d'),
            to_date=end_date.strftime('%Y-%m-%d'),
            num_articles=10
        )
        news_info = json.loads(news_data)
        
        # 3. GPT 프롬프트 구성
        prompt = f"""
다음 정보를 바탕으로 {company_name}에 대한 전문적인 투자보고서를 작성해주세요.

## 주가 정보:
- 현재가: {stock_info.get('current_price', 'N/A')}원
- 전일대비: {stock_info.get('change', 'N/A')}원 ({stock_info.get('change_percent', 'N/A')}%)
- 거래량: {stock_info.get('volume', 'N/A')}주
- 고가: {stock_info.get('high', 'N/A')}원
- 저가: {stock_info.get('low', 'N/A')}원
- 시가총액: {stock_info.get('market_cap', 'N/A')}
- PER: {stock_info.get('pe_ratio', 'N/A')}
- 배당수익률: {stock_info.get('dividend_yield', 'N/A')}
- 52주 최고가: {stock_info.get('52_week_high', 'N/A')}원
- 52주 최저가: {stock_info.get('52_week_low', 'N/A')}원

## 최근 뉴스 (최근 {news_days}일):
"""
        
        # 뉴스 정보 추가
        if news_info and len(news_info) > 0:
            for i, news in enumerate(news_info[:5], 1):  # 상위 5개 뉴스만 사용
                prompt += f"{i}. {news.get('title', 'N/A')}\n   - {news.get('description', 'N/A')}\n\n"
        else:
            prompt += "관련 뉴스를 찾을 수 없습니다.\n\n"
        
        prompt += """
위 정보를 바탕으로 다음 구조로 투자보고서를 작성해주세요:

1. **종목 개요** (기업 소개 및 현재 주가 상황)
2. **기술적 분석** (주가 차트 패턴, 거래량, 지지/저항선 등)
3. **기본적 분석** (재무지표, PER, 시가총액 등 분석)
4. **뉴스 및 시장 동향** (최근 뉴스가 주가에 미치는 영향 분석)
5. **투자 의견** (매수/매도/보유 추천 및 근거)
6. **위험 요소** (투자 시 주의해야 할 리스크)
7. **목표가** (향후 3-6개월 예상 주가 범위)

각 섹션을 상세하고 전문적으로 작성해주세요. 투자 조언은 객관적 데이터에 기반하여 제공해주세요.
"""

        # 4. GPT API 호출
        print("3. GPT 분석 중...")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "당신은 경험이 풍부한 주식 애널리스트입니다. 주어진 데이터를 바탕으로 객관적이고 전문적인 투자보고서를 작성합니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        # 5. 결과 구성
        report = {
            "company_name": company_name,
            "report_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "stock_data": stock_info,
            "news_count": len(news_info) if news_info else 0,
            "analysis_period": f"{period} (주가), {news_days}일 (뉴스)",
            "investment_report": response.choices[0].message.content,
            "data_sources": {
                "stock_data": "Yahoo Finance",
                "news_data": "NewsAPI",
                "analysis": "OpenAI GPT-4"
            }
        }
        
        print("4. 투자보고서 생성 완료!")
        return json.dumps(report, ensure_ascii=False, indent=2)
        
    except Exception as e:
        print(f"투자보고서 생성 중 오류 발생: {str(e)}")
        return json.dumps({"error": f"투자보고서 생성 실패: {str(e)}"}, ensure_ascii=False, indent=2)

def generate_multiple_reports(company_names, period='1mo', news_days=7):
    """
    여러 기업의 투자보고서를 한번에 생성하는 함수
    
    Parameters:
    - company_names: 회사명 리스트
    - period: 주가 데이터 기간
    - news_days: 뉴스 검색 기간
    
    Returns:
    - 각 기업의 투자보고서를 포함한 딕셔너리
    """
    reports = {}
    for company_name in company_names:
        print(f"\n{'='*50}")
        report = generate_investment_report(company_name, period, news_days)
        reports[company_name] = json.loads(report)
    
    return json.dumps(reports, ensure_ascii=False, indent=2)

# Example usage
if __name__ == "__main__":
    company_name = input("분석할 회사명을 입력하세요: ")
    report = generate_investment_report(company_name)
    
    # 결과를 파일로 저장
    report_data = json.loads(report)
    if 'error' not in report_data:
        filename = f"{company_name}_investment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n투자보고서가 {filename}에 저장되었습니다.")
        
        # 콘솔에 요약 출력
        print(f"\n=== {company_name} 투자보고서 요약 ===")
        print(f"현재가: {report_data['stock_data']['current_price']}원")
        print(f"전일대비: {report_data['stock_data']['change']}원 ({report_data['stock_data']['change_percent']}%)")
        print(f"분석 기간: {report_data['analysis_period']}")
        print(f"뉴스 개수: {report_data['news_count']}개")
        print("\n=== GPT 분석 결과 ===")
        print(report_data['investment_report'][:500] + "..." if len(report_data['investment_report']) > 500 else report_data['investment_report'])
    else:
        print(f"오류: {report_data['error']}")
