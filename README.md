# 신한 개인 프로젝트

한국어 특화 주가 정보 및 뉴스 분석 프로젝트입니다.

## 기능

- 한국 주식 실시간 가격 정보 조회
- KOSPI/KOSDAQ 지수 정보
- 주식 관련 뉴스 수집
- 투자 분석 리포트 생성

## 설치 및 설정

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 다음 API 키들을 설정하세요:

```env
# 주가 정보 API 키들
ALPHA_VANTAGE_KEY=your_alpha_vantage_api_key_here

# 한국투자증권 API 키들 (선택사항)
KIS_APP_KEY=your_kis_app_key_here
KIS_APP_SECRET=your_kis_app_secret_here
KIS_ACCESS_TOKEN=your_kis_access_token_here

# 뉴스 API 키
NEWSAPI_KEY=your_newsapi_key_here
```

### 3. API 키 발급

- **Alpha Vantage**: https://www.alphavantage.co/support/#api-key
- **NewsAPI**: https://newsapi.org/register
- **한국투자증권 API**: https://securities.kisline.com/

## 사용법

### 주가 정보 조회

```python
from src.fetch.stock_fetcher import KoreanStockFetcher

# Fetcher 인스턴스 생성
fetcher = KoreanStockFetcher()

# 개별 주식 정보 조회
samsung_info = fetcher.get_stock_price_yahoo("005930")
print(samsung_info)

# 여러 주식 정보 조회
symbols = ["005930", "000660", "035420"]  # 삼성전자, SK하이닉스, NAVER
multiple_info = fetcher.get_multiple_stock_prices(symbols)

# 시장 요약 정보
market_summary = fetcher.get_market_summary()

# 주식 관련 뉴스
news = fetcher.get_stock_news("005930", 5)
```

### 뉴스 정보 조회

```python
from src.fetch.news_fetcher import get_latest_news

# 최신 뉴스 조회
news = get_latest_news("삼성전자", "2024-01-01", "2024-12-31", 10)
```

## 주요 한국 주식 심볼

| 심볼   | 회사명           | Yahoo Finance 심볼 |
| ------ | ---------------- | ------------------ |
| 005930 | 삼성전자         | 005930.KS          |
| 000660 | SK하이닉스       | 000660.KS          |
| 035420 | NAVER            | 035420.KS          |
| 051910 | LG화학           | 051910.KS          |
| 006400 | 삼성SDI          | 006400.KS          |
| 035720 | 카카오           | 035720.KS          |
| 207940 | 삼성바이오로직스 | 207940.KS          |
| 068270 | 셀트리온         | 068270.KS          |
| 323410 | 카카오뱅크       | 323410.KS          |
| 373220 | LG에너지솔루션   | 373220.KS          |

## 프로젝트 구조

```
src/
├── fetch/
│   ├── stock_fetcher.py    # 주가 정보 수집
│   └── news_fetcher.py     # 뉴스 정보 수집
├── analysis/
│   └── outlook_generator.py # 투자 분석 리포트 생성
└── frontend/               # Next.js 웹 프론트엔드
```

## 실행 예시

```bash
# 주가 정보 조회 테스트
python src/fetch/stock_fetcher.py
```
