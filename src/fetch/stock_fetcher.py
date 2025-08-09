# 주가정보 fetch 모듈
# yfinance api 사용

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import json

# 한국 주요 기업의 티커 심볼 매핑
KOREAN_COMPANIES = {
    '삼성전자': '005930.KS',
    'SK하이닉스': '000660.KS', 
    'LG에너지솔루션': '373220.KS',
    'NAVER': '035420.KS',
    '카카오': '035720.KS',
    'LG화학': '051910.KS',
    '현대차': '005380.KS',
    '기아': '000270.KS',
    'POSCO홀딩스': '005490.KS',
    'KB금융': '105560.KS',
    '신한지주': '055550.KS',
    'LG전자': '066570.KS',
    '삼성바이오로직스': '207940.KS',
    '현대모비스': '012330.KS',
    '셀트리온': '068270.KS',
    'SK텔레콤': '017670.KS',
    'KT&G': '033780.KS',
    '한국전력': '015760.KS',
    '삼성물산': '028260.KS',
    'LG디스플레이': '034220.KS'
}

def get_ticker_symbol(company_name):
    """
    한국 기업명을 야후 파이낸스 티커 심볼로 변환
    """
    # 정확한 매칭 먼저 시도
    if company_name in KOREAN_COMPANIES:
        return KOREAN_COMPANIES[company_name]
    
    # 부분 매칭 시도 (예: "삼성" -> "삼성전자")
    for korean_name, ticker in KOREAN_COMPANIES.items():
        if company_name in korean_name or korean_name in company_name:
            return ticker
    
    # 매칭되지 않으면 원래 이름 반환 (직접 입력된 티커일 수도 있음)
    return company_name

def get_stock_data(company_name, period='1mo', interval='1d'):
    """
    주식 데이터를 가져오는 함수
    
    Parameters:
    - company_name: 회사명 (예: '삼성전자')
    - period: 기간 ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
    - interval: 간격 ('1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo')
    
    Returns:
    - JSON 형태의 주가 데이터
    """
    try:
        # 티커 심볼 가져오기
        ticker_symbol = get_ticker_symbol(company_name)
        print(f"Fetching stock data for: {company_name} ({ticker_symbol})")
        
        # 주식 객체 생성
        stock = yf.Ticker(ticker_symbol)
        
        # 주가 데이터 가져오기
        hist_data = stock.history(period=period, interval=interval)
        
        if hist_data.empty:
            print(f"No data found for {company_name} ({ticker_symbol})")
            return json.dumps({"error": f"No data found for {company_name}"}, ensure_ascii=False, indent=2)
        
        # 기본 정보 가져오기
        info = stock.info
        
        # 최신 주가 정보
        latest_data = hist_data.iloc[-1]
        current_price = latest_data['Close']
        
        # 전일 대비 변화량 계산
        if len(hist_data) > 1:
            prev_close = hist_data.iloc[-2]['Close']
            change = current_price - prev_close
            change_percent = (change / prev_close) * 100
        else:
            change = 0
            change_percent = 0
        
        # 결과 데이터 구성
        result = {
            "company_name": company_name,
            "ticker_symbol": ticker_symbol,
            "current_price": round(current_price, 2),
            "change": round(change, 2),
            "change_percent": round(change_percent, 2),
            "volume": int(latest_data['Volume']),
            "high": round(latest_data['High'], 2),
            "low": round(latest_data['Low'], 2),
            "open": round(latest_data['Open'], 2),
            "market_cap": info.get('marketCap', 'N/A'),
            "pe_ratio": info.get('forwardPE', 'N/A'),
            "dividend_yield": info.get('dividendYield', 'N/A'),
            "52_week_high": info.get('fiftyTwoWeekHigh', 'N/A'),
            "52_week_low": info.get('fiftyTwoWeekLow', 'N/A'),
            "historical_data": []
        }
        
        # 히스토리컬 데이터 추가 (최근 10일)
        recent_data = hist_data.tail(10)
        for date, row in recent_data.iterrows():
            result["historical_data"].append({
                "date": date.strftime('%Y-%m-%d'),
                "open": round(row['Open'], 2),
                "high": round(row['High'], 2),
                "low": round(row['Low'], 2),
                "close": round(row['Close'], 2),
                "volume": int(row['Volume'])
            })
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        print(f"Error fetching stock data for {company_name}: {str(e)}")
        return json.dumps({"error": f"Error fetching data: {str(e)}"}, ensure_ascii=False, indent=2)

def get_multiple_stocks_data(company_names, period='1mo'):
    """
    여러 기업의 주가 데이터를 한번에 가져오는 함수
    
    Parameters:
    - company_names: 회사명 리스트 (예: ['삼성전자', 'SK하이닉스'])
    - period: 기간
    
    Returns:
    - 각 기업의 주가 데이터를 포함한 딕셔너리
    """
    results = {}
    for company_name in company_names:
        results[company_name] = json.loads(get_stock_data(company_name, period))
    
    return json.dumps(results, ensure_ascii=False, indent=2)

# Example usage
if __name__ == "__main__":
    company_name = input("회사명을 입력하세요: ")
    print(get_stock_data(company_name))