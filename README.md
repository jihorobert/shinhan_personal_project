<<<<<<< HEAD
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
=======
# 신한 개인프로젝트: AI 투자보고서 생성 시스템

주가 정보와 뉴스 데이터를 기반으로 GPT를 활용한 전문적인 투자보고서를 자동 생성하는 시스템입니다.

## 📋 주요 기능

- **주가 데이터 수집**: Yahoo Finance API를 통한 실시간 주가 정보 수집
- **뉴스 데이터 수집**: NewsAPI를 통한 관련 뉴스 기사 수집  
- **AI 분석**: OpenAI GPT-4를 활용한 전문적인 투자보고서 생성
- **종합 분석**: 기술적 분석, 기본적 분석, 뉴스 분석을 통합한 투자 의견 제공

## 🚀 설치 및 설정

### 1. 가상환경 설정 (권장)
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt

# yfinance 관련 오류가 발생하는 경우 최신 버전으로 업그레이드
pip install yfinance --upgrade --no-cache-dir
```

### 3. 환경변수 설정
`.env` 파일을 생성하고 다음 API 키들을 설정하세요:

```env
GPT_KEY=your_openai_api_key_here
NEWSAPI_KEY=your_newsapi_key_here
```

#### API 키 발급 방법
- **OpenAI API Key**: [OpenAI Platform](https://platform.openai.com/api-keys)에서 발급
- **NewsAPI Key**: [NewsAPI](https://newsapi.org/register)에서 무료 계정 생성 후 발급

## 💻 사용법

### 방법 1: 예제 스크립트 실행
```bash
python example_usage.py
```

### 방법 2: 직접 모듈 사용
```python
from src.analysis.analyze import generate_investment_report

# 단일 기업 분석
report = generate_investment_report('삼성전자')
print(report)

# 여러 기업 분석
from src.analysis.analyze import generate_multiple_reports
reports = generate_multiple_reports(['삼성전자', 'SK하이닉스', 'NAVER'])
```

### 방법 3: 개별 모듈 테스트
```bash
# 주가 데이터만 확인
cd src/fetch
python stock_fetcher.py

# 뉴스 데이터만 확인  
python news_fetcher.py

# 투자보고서 생성
cd ../analysis
python analyze.py
```

## 📊 투자보고서 구조

생성되는 투자보고서는 다음 섹션들을 포함합니다:

1. **종목 개요** - 기업 소개 및 현재 주가 상황
2. **기술적 분석** - 주가 차트 패턴, 거래량, 지지/저항선 분석
3. **기본적 분석** - 재무지표, PER, 시가총액 등 분석
4. **뉴스 및 시장 동향** - 최근 뉴스가 주가에 미치는 영향 분석
5. **투자 의견** - 매수/매도/보유 추천 및 근거
6. **위험 요소** - 투자 시 주의해야 할 리스크
7. **목표가** - 향후 3-6개월 예상 주가 범위

## 📁 프로젝트 구조

```
shinhan_personal_project/
├── src/
│   ├── fetch/
│   │   ├── stock_fetcher.py      # 주가 데이터 수집
│   │   └── news_fetcher.py       # 뉴스 데이터 수집
│   ├── analysis/
│   │   └── analyze.py            # GPT 기반 투자보고서 생성
│   └── frontend/                 # Next.js 프론트엔드 (개발 중)
├── requirements.txt              # Python 의존성
├── example_usage.py             # 사용 예제
└── README.md
```

## 🎯 지원 종목

현재 다음 한국 주요 기업들을 지원합니다:

- 삼성전자, SK하이닉스, LG에너지솔루션
- NAVER, 카카오, LG화학
- 현대차, 기아, POSCO홀딩스
- KB금융, 신한지주, LG전자
- 삼성바이오로직스, 현대모비스, 셀트리온
- SK텔레콤, KT&G, 한국전력
- 삼성물산, LG디스플레이

## ⚠️ 주의사항

- 이 시스템은 투자 참고용으로만 사용하시기 바랍니다.
- 실제 투자 결정은 반드시 본인의 판단과 책임 하에 이루어져야 합니다.
- API 사용량 제한에 주의하시기 바랍니다.
- 생성된 보고서는 `reports/` 폴더에 자동 저장됩니다.

## 🔧 문제 해결

### 일반적인 오류들
1. **API 키 오류**: `.env` 파일의 API 키가 올바른지 확인
2. **모듈 임포트 오류**: `pip install -r requirements.txt` 재실행
3. **주가 데이터 없음**: 종목명이 지원 목록에 있는지 확인
4. **뉴스 데이터 없음**: 검색 기간을 늘려보거나 다른 키워드 사용

### yfinance 관련 오류 해결
**"Failed to get ticker" 또는 "Expecting value: line 1 column 1" 오류가 발생하는 경우:**

```bash
# yfinance를 최신 버전으로 업그레이드
pip install yfinance --upgrade --no-cache-dir

# 또는 가상환경에서
source venv/bin/activate
pip install yfinance --upgrade --no-cache-dir
```

이 명령어는 다음과 같은 문제들을 해결합니다:
- Yahoo Finance API 접근 문제
- 한국 주식 티커 심볼 인식 오류
- JSON 파싱 오류
- API 응답 형식 변경으로 인한 오류

## 📝 라이선스

이 프로젝트는 개인 학습 및 연구 목적으로 개발되었습니다.
>>>>>>> 75031126ccee83e21527913b2a8d2c6fdbdcab30
