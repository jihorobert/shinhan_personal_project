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

# 한국 주요 기업 딕셔너리 - 코스피 상위 100개 기업 (app.py에서 사용)
KOREAN_COMPANIES = {
    # 시가총액 상위 50개 기업
    '삼성전자': '005930',
    'LG에너지솔루션': '373220',
    'SK하이닉스': '000660',
    '삼성바이오로직스': '207940',
    '현대차': '005380',
    'NAVER': '035420',
    '삼성SDI': '006400',
    'LG화학': '051910',
    '카카오': '035720',
    '기아': '000270',
    '포스코홀딩스': '005490',
    'KB금융': '105560',
    '신한지주': '055550',
    '셀트리온': '068270',
    '현대모비스': '012330',
    'LG전자': '066570',
    '삼성물산': '028260',
    'SK이노베이션': '096770',
    '한국전력공사': '015760',
    'KT&G': '033780',
    'SK텔레콤': '017670',
    '카카오뱅크': '323410',
    '하나금융지주': '086790',
    '삼성생명': '032830',
    '한국가스공사': '036460',
    'CJ제일제당': '097950',
    '롯데케미칼': '011170',
    'SK': '034730',
    '현대건설': '000720',
    '두산에너빌리티': '034020',
    '대한항공': '003490',
    '아모레퍼시픽': '090430',
    '한화솔루션': '009830',
    'LG': '003550',
    '삼성화재': '000810',
    '삼성전자우': '005935',
    '우리금융지주': '316140',
    '삼성전기': '009150',
    'HMM': '011200',
    '현대중공업': '329180',
    'LG생활건강': '051900',
    '한국조선해양': '009540',
    '삼성에스디에스': '018260',
    '현대글로비스': '086280',
    'KT': '030200',
    '포스코케미칼': '003670',
    '삼성카드': '029780',
    'LG이노텍': '011070',
    '삼성엔지니어링': '028050',
    '현대제철': '004020',
    
    # 시가총액 51-100위 기업
    '한온시스템': '018880',
    '한국금융지주': '071050',
    '두산밥캣': '241560',
    'GS': '078930',
    '한미사이언스': '008930',
    '한국타이어앤테크놀로지': '161390',
    '한화에어로스페이스': '012450',
    '현대미포조선': '010620',
    '한미약품': '128940',
    '대우건설': '047040',
    '한화생명': '088350',
    '현대위아': '011210',
    '한전KPS': '051600',
    '현대해상': '001450',
    '한화': '000880',
    '롯데지주': '004990',
    '한화시스템': '272210',
    '현대엘리베이터': '017800',
    '한전기술': '052690',
    '현대리바트': '079430',
    '한화투자증권': '003530',
    '현대오토에버': '307950',
    '한화손해보험': '000370',
    'LG디스플레이': '034220',
    'SKC': '011790',
    '엔씨소프트': '036570',
    '크래프톤': '259960',
    '삼성중공업': '010140',
    'GS건설': '006360',
    'LG유플러스': '032640',
    '포스코인터내셔널': '047050',
    '한국항공우주': '047810',
    'SK스퀘어': '402340',
    '넷마블': '251270',
    '현대백화점': '069960',
    'SK바이오팜': '326030',
    'GS리테일': '007070',
    '현대홈쇼핑': '057050',
    'CJ ENM': '035760',
    'CJ대한통운': '000120',
    '롯데쇼핑': '023530',
    '한진': '002320',
    '동원시스템즈': '014820',
    '현대그린푸드': '005440',
    '한화갤러리아': '027390',
    'S-Oil': '010950',
    '현대산업개발': '012630',
    '금호석유': '011780',
    '동서': '026960',
    '오리온': '001800'
}

def get_stock_data(company_name, period='1mo'):
    """
    회사명으로 주식 데이터를 가져오는 래퍼 함수 (analyze.py에서 사용)
    
    Parameters:
    - company_name: 회사명 (예: '삼성전자')
    - period: 주가 데이터 기간 (기본값: '1mo')
    
    Returns:
    - JSON 형태의 주가 데이터 (문자열)
    """
    try:
        fetcher = KoreanStockFetcher()
        
        # 회사명을 심볼로 변환
        symbol = None
        if company_name in KOREAN_COMPANIES:
            symbol = KOREAN_COMPANIES[company_name]
        else:
            # 정확한 회사명이 아닌 경우, 부분 매칭 시도
            for name, ticker in KOREAN_COMPANIES.items():
                if company_name in name or name in company_name:
                    symbol = ticker
                    company_name = name  # 정확한 회사명으로 업데이트
                    break
        
        if not symbol:
            return json.dumps({
                "error": f"지원되지 않는 기업입니다: {company_name}",
                "supported_companies": list(KOREAN_COMPANIES.keys())
            }, ensure_ascii=False)
        
        # Yahoo Finance에서 주가 정보 가져오기
        stock_info = fetcher.get_stock_price_yahoo(symbol, period)
        
        if 'error' in stock_info:
            return json.dumps(stock_info, ensure_ascii=False)
        
        # 히스토리컬 데이터 추가 (기술적 분석을 위해)
        try:
            import yfinance as yf
            ticker = yf.Ticker(f"{symbol}.KS")
            hist = ticker.history(period=period)
            
            if not hist.empty:
                # 최신 데이터부터 정렬 (최신이 첫 번째)
                hist_data = []
                for date, row in hist.iterrows():
                    hist_data.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'open': float(row['Open']),
                        'high': float(row['High']),
                        'low': float(row['Low']),
                        'close': float(row['Close']),
                        'volume': int(row['Volume'])
                    })
                
                # 최신 데이터가 첫 번째가 되도록 역순 정렬
                hist_data.reverse()
                stock_info['historical_data'] = hist_data
                
                # 52주 최고가/최저가 계산
                if len(hist_data) > 0:
                    prices = [data['close'] for data in hist_data]
                    stock_info['52_week_high'] = max(prices)
                    stock_info['52_week_low'] = min(prices)
                
        except Exception as e:
            print(f"히스토리컬 데이터 추가 중 오류: {e}")
            stock_info['historical_data'] = []
        
        # 회사명 추가
        stock_info['company_name'] = company_name
        
        return json.dumps(stock_info, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"주가 데이터 조회 중 오류 발생: {str(e)}"
        }, ensure_ascii=False)

if __name__ == "__main__":
    main()
