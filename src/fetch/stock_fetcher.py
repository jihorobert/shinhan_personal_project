# 주식 정보 fetch 모듈
import requests
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional, Any
try:
    from .news_fetcher import get_latest_news
except ImportError:
    from news_fetcher import get_latest_news

load_dotenv()

class KoreanStockFetcher:
    """한국어 특화 주가 정보 API Fetcher"""
    
    def __init__(self):
        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_KEY")
        self.kis_app_key = os.getenv("KIS_APP_KEY")
        self.kis_app_secret = os.getenv("KIS_APP_SECRET")
        self.kis_access_token = os.getenv("KIS_ACCESS_TOKEN")
        
    def get_stock_price_yahoo(self, symbol: str, period: str = "1mo") -> Dict[str, Any]:
        """
        Yahoo Finance API를 사용하여 주가 정보 가져오기
        
        Args:
            symbol: 주식 심볼 (예: "005930.KS" for 삼성전자)
            period: 기간 ("1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max")
        
        Returns:
            주가 정보 딕셔너리
        """
        try:
            # 한국 주식의 경우 .KS 접미사 추가
            if not symbol.endswith('.KS'):
                symbol = f"{symbol}.KS"
            
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                return {"error": "주가 정보를 찾을 수 없습니다."}
            
            # 최신 데이터
            latest = hist.iloc[-1]
            info = ticker.info
            
            result = {
                "symbol": symbol,
                "company_name": info.get('longName', '알 수 없음'),
                "current_price": float(latest['Close']),
                "open_price": float(latest['Open']),
                "high_price": float(latest['High']),
                "low_price": float(latest['Low']),
                "volume": int(latest['Volume']),
                "change": float(latest['Close'] - hist.iloc[-2]['Close']) if len(hist) > 1 else 0,
                "change_percent": float(((latest['Close'] - hist.iloc[-2]['Close']) / hist.iloc[-2]['Close']) * 100) if len(hist) > 1 else 0,
                "date": latest.name.strftime('%Y-%m-%d'),
                "market_cap": info.get('marketCap', 0),
                "pe_ratio": info.get('trailingPE', 0),
                "dividend_yield": info.get('dividendYield', 0),
                "currency": info.get('currency', 'KRW')
            }
            
            return result
            
        except Exception as e:
            return {"error": f"주가 정보 조회 중 오류 발생: {str(e)}"}
    
    def get_stock_price_alpha_vantage(self, symbol: str) -> Dict[str, Any]:
        """
        Alpha Vantage API를 사용하여 실시간 주가 정보 가져오기
        
        Args:
            symbol: 주식 심볼 (예: "005930" for 삼성전자)
        
        Returns:
            주가 정보 딕셔너리
        """
        if not self.alpha_vantage_key:
            return {"error": "Alpha Vantage API 키가 설정되지 않았습니다."}
        
        try:
            url = f"https://www.alphavantage.co/query"
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": f"{symbol}.KS",
                "apikey": self.alpha_vantage_key
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if "Global Quote" not in data:
                return {"error": "주가 정보를 찾을 수 없습니다."}
            
            quote = data["Global Quote"]
            
            result = {
                "symbol": symbol,
                "current_price": float(quote.get("05. price", 0)),
                "open_price": float(quote.get("02. open", 0)),
                "high_price": float(quote.get("03. high", 0)),
                "low_price": float(quote.get("04. low", 0)),
                "volume": int(quote.get("06. volume", 0)),
                "change": float(quote.get("09. change", 0)),
                "change_percent": quote.get("10. change percent", "0%").replace("%", ""),
                "date": quote.get("07. latest trading day", ""),
                "currency": "KRW"
            }
            
            return result
            
        except Exception as e:
            return {"error": f"Alpha Vantage API 조회 중 오류 발생: {str(e)}"}
    
    def get_korean_stock_list(self) -> List[Dict[str, str]]:
        """
        주요 한국 주식 목록 반환
        
        Returns:
            한국 주식 목록
        """
        korean_stocks = [
            {"symbol": "005930", "name": "삼성전자", "yahoo_symbol": "005930.KS"},
            {"symbol": "000660", "name": "SK하이닉스", "yahoo_symbol": "000660.KS"},
            {"symbol": "035420", "name": "NAVER", "yahoo_symbol": "035420.KS"},
            {"symbol": "051910", "name": "LG화학", "yahoo_symbol": "051910.KS"},
            {"symbol": "006400", "name": "삼성SDI", "yahoo_symbol": "006400.KS"},
            {"symbol": "035720", "name": "카카오", "yahoo_symbol": "035720.KS"},
            {"symbol": "207940", "name": "삼성바이오로직스", "yahoo_symbol": "207940.KS"},
            {"symbol": "068270", "name": "셀트리온", "yahoo_symbol": "068270.KS"},
            {"symbol": "323410", "name": "카카오뱅크", "yahoo_symbol": "323410.KS"},
            {"symbol": "373220", "name": "LG에너지솔루션", "yahoo_symbol": "373220.KS"}
        ]
        return korean_stocks
    
    def get_multiple_stock_prices(self, symbols: List[str], source: str = "yahoo") -> List[Dict[str, Any]]:
        """
        여러 주식의 가격 정보를 한 번에 가져오기
        
        Args:
            symbols: 주식 심볼 리스트
            source: 데이터 소스 ("yahoo" 또는 "alpha_vantage")
        
        Returns:
            주가 정보 리스트
        """
        results = []
        
        for symbol in symbols:
            if source == "yahoo":
                result = self.get_stock_price_yahoo(symbol)
            elif source == "alpha_vantage":
                result = self.get_stock_price_alpha_vantage(symbol)
            else:
                result = {"error": "지원하지 않는 데이터 소스입니다."}
            
            results.append(result)
        
        return results
    
    def get_stock_news(self, symbol: str, num_articles: int = 5, days_back: int = 7) -> List[Dict[str, str]]:
        """
        특정 주식 관련 뉴스 가져오기 (NewsAPI 활용)
        
        Args:
            symbol: 주식 심볼
            num_articles: 가져올 뉴스 개수
            days_back: 몇 일 전까지의 뉴스를 가져올지
        
        Returns:
            뉴스 리스트
        """
        try:
            # 주식 심볼을 회사명으로 변환
            stock_list = self.get_korean_stock_list()
            company_name = None
            
            for stock in stock_list:
                if stock['symbol'] == symbol:
                    company_name = stock['name']
                    break
            
            if not company_name:
                return [{"error": f"주식 심볼 {symbol}에 해당하는 회사를 찾을 수 없습니다."}]
            
            # 날짜 계산
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # NewsAPI를 사용하여 뉴스 가져오기
            news_json = get_latest_news(
                query=company_name,
                from_date=start_date.strftime('%Y-%m-%d'),
                to_date=end_date.strftime('%Y-%m-%d'),
                num_articles=num_articles
            )
            
            # JSON 문자열을 파싱
            news_list = json.loads(news_json)
            
            # 결과 포맷 통일
            result = []
            for article in news_list:
                if 'title' in article and 'description' in article:
                    result.append({
                        "title": article['title'],
                        "summary": article['description'],
                        "source": "NewsAPI",
                        "company": company_name
                    })
            
            return result
            
        except Exception as e:
            return [{"error": f"뉴스 조회 중 오류 발생: {str(e)}"}]
    
    def get_market_summary(self) -> Dict[str, Any]:
        """
        한국 시장 요약 정보 가져오기
        
        Returns:
            시장 요약 정보
        """
        try:
            # KOSPI 지수 정보
            kospi = yf.Ticker("^KS11")
            kospi_info = kospi.info
            kospi_hist = kospi.history(period="5d")
            
            # KOSDAQ 지수 정보
            kosdaq = yf.Ticker("^KQ11")
            kosdaq_info = kosdaq.info
            kosdaq_hist = kosdaq.history(period="5d")
            
            result = {
                "kospi": {
                    "current": float(kospi_hist.iloc[-1]['Close']) if not kospi_hist.empty else 0,
                    "change": float(kospi_hist.iloc[-1]['Close'] - kospi_hist.iloc[-2]['Close']) if len(kospi_hist) > 1 else 0,
                    "change_percent": float(((kospi_hist.iloc[-1]['Close'] - kospi_hist.iloc[-2]['Close']) / kospi_hist.iloc[-2]['Close']) * 100) if len(kospi_hist) > 1 else 0
                },
                "kosdaq": {
                    "current": float(kosdaq_hist.iloc[-1]['Close']) if not kosdaq_hist.empty else 0,
                    "change": float(kosdaq_hist.iloc[-1]['Close'] - kosdaq_hist.iloc[-2]['Close']) if len(kosdaq_hist) > 1 else 0,
                    "change_percent": float(((kosdaq_hist.iloc[-1]['Close'] - kosdaq_hist.iloc[-2]['Close']) / kosdaq_hist.iloc[-2]['Close']) * 100) if len(kosdaq_hist) > 1 else 0
                },
                "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return result
            
        except Exception as e:
            return {"error": f"시장 요약 정보 조회 중 오류 발생: {str(e)}"}

# 사용 예시
def main():
    fetcher = KoreanStockFetcher()
    
    # 1. 개별 주식 정보 조회
    print("=== 삼성전자 주가 정보 ===")
    samsung_info = fetcher.get_stock_price_yahoo("005930")
    print(json.dumps(samsung_info, ensure_ascii=False, indent=2))
    
    # 2. 여러 주식 정보 조회
    print("\n=== 주요 한국 주식 정보 ===")
    symbols = ["005930", "000660", "035420"]  # 삼성전자, SK하이닉스, NAVER
    multiple_info = fetcher.get_multiple_stock_prices(symbols)
    for info in multiple_info:
        print(f"{info.get('symbol', 'N/A')}: {info.get('current_price', 0):,.0f}원")
    
    # 3. 시장 요약 정보
    print("\n=== 한국 시장 요약 ===")
    market_summary = fetcher.get_market_summary()
    print(json.dumps(market_summary, ensure_ascii=False, indent=2))
    
    # 4. 주식 관련 뉴스 (NewsAPI 활용)
    print("\n=== 삼성전자 관련 뉴스 (NewsAPI) ===")
    news = fetcher.get_stock_news("005930", 3, days_back=7)
    for i, article in enumerate(news, 1):
        if 'error' in article:
            print(f"{i}. 오류: {article['error']}")
        else:
            print(f"{i}. {article.get('title', 'N/A')}")
            print(f"   요약: {article.get('summary', 'N/A')[:100]}...")
            print(f"   출처: {article.get('source', 'N/A')}")
            print()

if __name__ == "__main__":
    main()