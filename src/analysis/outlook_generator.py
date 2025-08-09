# GPT 기반 투자 전망 생성 모듈
import os
import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# stock_fetcher 모듈 import
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'fetch'))
    from stock_fetcher import KoreanStockFetcher
except ImportError:
    from src.fetch.stock_fetcher import KoreanStockFetcher

from openai import OpenAI

# PDF 및 시각화 관련 import
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

load_dotenv()

class InvestmentReportGenerator:
    """GPT API를 활용한 투자 보고서 생성기"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("GPT_KEY"))
        self.stock_fetcher = KoreanStockFetcher()
        
        # 한글 폰트 설정
        self.setup_korean_font()
        
    def setup_korean_font(self):
        """한글 폰트 설정"""
        # matplotlib 한글 폰트 설정
        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.rcParams['axes.unicode_minus'] = False
        
        # seaborn 스타일 설정
        sns.set_style("whitegrid")
        sns.set_palette("husl")
        
        # PDF용 한글 폰트 설정
        self.setup_pdf_korean_font()
    
    def setup_pdf_korean_font(self):
        """PDF용 한글 폰트 설정"""
        try:
            # macOS에서 사용 가능한 한글 폰트들 (우선순위 순)
            korean_fonts = [
                '/System/Library/Fonts/AppleGothic.ttf',  # AppleGothic
                '/System/Library/Fonts/Supplemental/Arial Unicode MS.ttf',  # Arial Unicode MS
                '/Library/Fonts/Arial Unicode MS.ttf',  # Arial Unicode MS
                '/System/Library/Fonts/STHeiti Light.ttc',  # STHeiti
                '/System/Library/Fonts/PingFang.ttc',  # PingFang
            ]
            
            # 사용 가능한 폰트 찾기
            available_font = None
            for font_path in korean_fonts:
                if os.path.exists(font_path):
                    available_font = font_path
                    break
            
            if available_font:
                try:
                    # 폰트 등록
                    pdfmetrics.registerFont(TTFont('KoreanFont', available_font))
                    self.korean_font_name = 'KoreanFont'
                    print(f"한글 폰트 등록 완료: {available_font}")
                except Exception as font_error:
                    print(f"폰트 등록 실패: {font_error}")
                    # 대체 방법: 기본 폰트 사용
                    self.korean_font_name = 'Helvetica'
                    print("기본 폰트를 사용합니다.")
            else:
                # 기본 폰트 사용
                self.korean_font_name = 'Helvetica'
                print("한글 폰트를 찾을 수 없어 기본 폰트를 사용합니다.")
                
        except Exception as e:
            print(f"폰트 설정 중 오류: {str(e)}")
            self.korean_font_name = 'Helvetica'
        
    def generate_stock_analysis_prompt(self, stock_data: Dict[str, Any], news_data: List[Dict[str, str]], market_data: Dict[str, Any]) -> str:
        """주식 분석을 위한 프롬프트 생성"""
        
        # 주식 기본 정보
        stock_info = f"""
주식 정보:
- 회사명: {stock_data.get('company_name', 'N/A')}
- 현재가: {stock_data.get('current_price', 0):,.0f}원
- 전일대비: {stock_data.get('change', 0):+,.0f}원 ({stock_data.get('change_percent', 0):+.2f}%)
- 시가총액: {stock_data.get('market_cap', 0):,.0f}원
- PER: {stock_data.get('pe_ratio', 0):.2f}
- 배당수익률: {stock_data.get('dividend_yield', 0):.2f}%
- 거래량: {stock_data.get('volume', 0):,}주
"""
        
        # 뉴스 정보
        news_info = "\n관련 뉴스:\n"
        for i, news in enumerate(news_data[:5], 1):  # 최대 5개 뉴스만 사용
            if 'error' not in news:
                news_info += f"{i}. {news.get('title', 'N/A')}\n"
                news_info += f"   요약: {news.get('summary', 'N/A')}\n\n"
        
        # 시장 정보
        market_info = f"""
시장 동향:
- KOSPI: {market_data.get('kospi', {}).get('current', 0):,.0f} ({market_data.get('kospi', {}).get('change_percent', 0):+.2f}%)
- KOSDAQ: {market_data.get('kosdaq', {}).get('current', 0):,.0f} ({market_data.get('kosdaq', {}).get('change_percent', 0):+.2f}%)
"""
        
        prompt = f"""
당신은 전문 투자 분석가입니다. 아래 정보를 바탕으로 {stock_data.get('company_name', '해당 기업')}에 대한 투자 보고서를 작성해주세요.

{stock_info}

{news_info}

{market_info}

다음 형식으로 한국어로 투자 보고서를 작성해주세요:

## 투자 보고서 - {stock_data.get('company_name', '기업명')}

### 1. 기업 개요
- 기업의 주요 사업 영역과 시장 포지션

### 2. 최근 주가 동향 분석
- 현재 주가 수준과 전일 대비 변동 요인
- 기술적 분석 (지지선, 저항선 등)

### 3. 재무 지표 분석
- PER, 배당수익률 등 주요 재무 지표 해석
- 업계 평균과의 비교

### 4. 뉴스 및 이벤트 분석
- 최근 주요 뉴스가 주가에 미치는 영향
- 향후 예상되는 이벤트

### 5. 투자 의견
- 매수/매도/관망 중 어느 것을 권장하는지
- 투자 시 고려사항과 리스크 요인

### 6. 투자 전망
- 단기(1-3개월) 및 중기(6개월-1년) 전망
- 목표가 설정 근거

보고서는 객관적이고 전문적인 톤으로 작성하되, 일반 투자자도 이해할 수 있도록 명확하게 설명해주세요.
"""
        
        return prompt
    
    def generate_stock_price_chart(self, symbol: str, period: str = "6mo") -> str:
        """주식 가격 차트 생성"""
        try:
            # 주식 데이터 가져오기
            stock_data = self.stock_fetcher.get_stock_price_yahoo(symbol, period)
            if 'error' in stock_data:
                return None
            
            # Yahoo Finance에서 히스토리 데이터 가져오기
            import yfinance as yf
            ticker = yf.Ticker(f"{symbol}.KS")
            hist = ticker.history(period=period)
            
            if hist.empty:
                return None
            
            # 차트 생성
            plt.figure(figsize=(12, 8))
            
            # 주가 차트
            plt.subplot(2, 1, 1)
            plt.plot(hist.index, hist['Close'], linewidth=2, color='blue', label='종가')
            plt.plot(hist.index, hist['Open'], linewidth=1, color='red', alpha=0.7, label='시가')
            plt.fill_between(hist.index, hist['High'], hist['Low'], alpha=0.3, color='gray', label='고가-저가')
            
            plt.title(f'{stock_data.get("company_name", symbol)} 주가 차트 ({period})', fontsize=14, fontweight='bold')
            plt.ylabel('주가 (원)', fontsize=12)
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            # 거래량 차트
            plt.subplot(2, 1, 2)
            plt.bar(hist.index, hist['Volume'], color='green', alpha=0.7, label='거래량')
            plt.title('거래량', fontsize=12, fontweight='bold')
            plt.ylabel('거래량 (주)', fontsize=12)
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # 차트 저장
            chart_path = os.path.join(os.path.dirname(__file__), '..', 'reports', f'chart_{symbol}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return chart_path
            
        except Exception as e:
            print(f"차트 생성 중 오류: {str(e)}")
            return None
    
    def generate_comparison_chart(self, symbols: List[str], period: str = "3mo") -> str:
        """여러 주식 비교 차트 생성"""
        try:
            plt.figure(figsize=(14, 10))
            
            # 서브플롯 생성
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
            
            colors_list = ['blue', 'red', 'green', 'orange', 'purple']
            
            for i, symbol in enumerate(symbols[:5]):  # 최대 5개
                try:
                    import yfinance as yf
                    ticker = yf.Ticker(f"{symbol}.KS")
                    hist = ticker.history(period=period)
                    
                    if not hist.empty:
                        # 정규화된 가격 (첫날을 100으로 설정)
                        normalized_price = (hist['Close'] / hist['Close'].iloc[0]) * 100
                        
                        ax1.plot(hist.index, normalized_price, 
                               linewidth=2, color=colors_list[i % len(colors_list)], 
                               label=f'{symbol}')
                        
                        # 변동률 계산
                        daily_return = hist['Close'].pct_change() * 100
                        ax2.plot(hist.index, daily_return, 
                               linewidth=1, color=colors_list[i % len(colors_list)], 
                               alpha=0.7, label=f'{symbol}')
                        
                except Exception as e:
                    print(f"주식 {symbol} 데이터 처리 중 오류: {str(e)}")
                    continue
            
            # 첫 번째 차트 (정규화된 가격)
            ax1.set_title('주식 가격 비교 (정규화)', fontsize=14, fontweight='bold')
            ax1.set_ylabel('정규화된 가격 (첫날=100)', fontsize=12)
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # 두 번째 차트 (일간 변동률)
            ax2.set_title('일간 변동률 비교', fontsize=14, fontweight='bold')
            ax2.set_ylabel('변동률 (%)', fontsize=12)
            ax2.set_xlabel('날짜', fontsize=12)
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # 차트 저장
            chart_path = os.path.join(os.path.dirname(__file__), '..', 'reports', f'comparison_chart_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return chart_path
            
        except Exception as e:
            print(f"비교 차트 생성 중 오류: {str(e)}")
            return None
    
    def generate_interactive_chart(self, symbol: str, period: str = "6mo") -> str:
        """인터랙티브 차트 생성 (Plotly)"""
        try:
            import yfinance as yf
            ticker = yf.Ticker(f"{symbol}.KS")
            hist = ticker.history(period=period)
            
            if hist.empty:
                return None
            
            # 캔들스틱 차트 생성
            fig = make_subplots(rows=2, cols=1, 
                              shared_xaxes=True,
                              vertical_spacing=0.03,
                              subplot_titles=(f'{symbol} 주가 차트', '거래량'),
                              row_width=[0.7, 0.3])
            
            # 캔들스틱 차트
            fig.add_trace(go.Candlestick(x=hist.index,
                                        open=hist['Open'],
                                        high=hist['High'],
                                        low=hist['Low'],
                                        close=hist['Close'],
                                        name='OHLC'),
                         row=1, col=1)
            
            # 거래량 차트
            fig.add_trace(go.Bar(x=hist.index, y=hist['Volume'],
                                name='거래량',
                                marker_color='rgba(0, 128, 0, 0.5)'),
                         row=2, col=1)
            
            # 레이아웃 설정
            fig.update_layout(
                title=f'{symbol} 주가 분석 차트',
                yaxis_title='주가 (원)',
                yaxis2_title='거래량',
                xaxis_rangeslider_visible=False,
                height=600
            )
            
            # HTML 파일로 저장
            html_path = os.path.join(os.path.dirname(__file__), '..', 'reports', f'interactive_chart_{symbol}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html')
            fig.write_html(html_path)
            
            return html_path
            
        except Exception as e:
            print(f"인터랙티브 차트 생성 중 오류: {str(e)}")
            return None
    
    def create_pdf_report(self, report: Dict[str, Any], chart_path: str = None, comparison_chart_path: str = None) -> str:
        """PDF 보고서 생성"""
        try:
            # PDF 파일 경로 설정
            if 'symbol' in report:
                pdf_filename = f"investment_report_{report['symbol']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            else:
                pdf_filename = f"market_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            pdf_path = os.path.join(os.path.dirname(__file__), '..', 'reports', pdf_filename)
            
            # PDF 문서 생성
            doc = SimpleDocTemplate(pdf_path, pagesize=A4)
            styles = getSampleStyleSheet()
            
            # 스타일 정의 (한글 폰트 적용)
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontName=self.korean_font_name,
                fontSize=18,
                spaceAfter=30,
                alignment=1  # 중앙 정렬
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontName=self.korean_font_name,
                fontSize=14,
                spaceAfter=12,
                spaceBefore=20
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontName=self.korean_font_name,
                fontSize=10,
                spaceAfter=6,
                leading=14
            )
            
            # 내용 구성
            story = []
            
            # 제목
            if 'symbol' in report:
                title = f"투자 보고서 - {report['company_name']} ({report['symbol']})"
            else:
                title = "한국 주식 시장 투자 보고서"
            
            # 한글 텍스트 인코딩 처리
            title = title.encode('utf-8').decode('utf-8')
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 20))
            
            # 생성 정보
            info_text = f"생성일시: {report['report_date']}"
            if 'analysis_period' in report:
                info_text += f" | 분석기간: {report['analysis_period']}"
            info_text = info_text.encode('utf-8').decode('utf-8')
            story.append(Paragraph(info_text, normal_style))
            story.append(Spacer(1, 20))
            
            # 구분선
            story.append(Paragraph("=" * 50, normal_style))
            story.append(Spacer(1, 20))
            
            # 보고서 내용을 섹션별로 분리
            content_lines = report['report_content'].split('\n')
            current_section = ""
            
            for line in content_lines:
                line = line.strip()
                if not line:
                    continue
                
                if line.startswith('##'):
                    # 메인 제목
                    title_text = line.replace('##', '').strip()
                    title_text = title_text.encode('utf-8').decode('utf-8')
                    story.append(Paragraph(title_text, title_style))
                    story.append(Spacer(1, 15))
                elif line.startswith('###'):
                    # 섹션 제목
                    heading_text = line.replace('###', '').strip()
                    heading_text = heading_text.encode('utf-8').decode('utf-8')
                    story.append(Paragraph(heading_text, heading_style))
                    story.append(Spacer(1, 10))
                else:
                    # 일반 텍스트
                    if line:
                        line = line.encode('utf-8').decode('utf-8')
                        story.append(Paragraph(line, normal_style))
                        story.append(Spacer(1, 5))
            
            # 차트 추가
            if chart_path and os.path.exists(chart_path):
                story.append(Spacer(1, 20))
                chart_title = "주가 차트".encode('utf-8').decode('utf-8')
                story.append(Paragraph(chart_title, heading_style))
                story.append(Spacer(1, 10))
                
                # 이미지 크기 조정
                img = Image(chart_path, width=6*inch, height=4*inch)
                story.append(img)
                story.append(Spacer(1, 15))
            
            if comparison_chart_path and os.path.exists(comparison_chart_path):
                comparison_title = "주식 비교 차트".encode('utf-8').decode('utf-8')
                story.append(Paragraph(comparison_title, heading_style))
                story.append(Spacer(1, 10))
                
                img = Image(comparison_chart_path, width=6*inch, height=4*inch)
                story.append(img)
                story.append(Spacer(1, 15))
            
            # 분석 데이터 요약 테이블
            story.append(Spacer(1, 20))
            summary_title = "분석 데이터 요약".encode('utf-8').decode('utf-8')
            story.append(Paragraph(summary_title, heading_style))
            story.append(Spacer(1, 10))
            
            if 'stock_data' in report:
                stock = report['stock_data']
                data = [
                    ['항목', '값'],
                    ['현재가', f"{stock.get('current_price', 0):,.0f}원"],
                    ['전일대비', f"{stock.get('change', 0):+,.0f}원 ({stock.get('change_percent', 0):+.2f}%)"],
                    ['거래량', f"{stock.get('volume', 0):,}주"],
                    ['PER', f"{stock.get('pe_ratio', 0):.2f}"],
                    ['배당수익률', f"{stock.get('dividend_yield', 0):.2f}%"]
                ]
                
                # 테이블 데이터 한글 인코딩 처리
                for i in range(len(data)):
                    for j in range(len(data[i])):
                        data[i][j] = data[i][j].encode('utf-8').decode('utf-8')
                
                if 'news_count' in report:
                    news_data_row = ['분석된 뉴스 수', f"{report['news_count']}개"]
                    # 뉴스 데이터 한글 인코딩 처리
                    news_data_row[0] = news_data_row[0].encode('utf-8').decode('utf-8')
                    news_data_row[1] = news_data_row[1].encode('utf-8').decode('utf-8')
                    data.append(news_data_row)
                
                table = Table(data, colWidths=[2*inch, 4*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), self.korean_font_name),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('FONTNAME', (0, 1), (-1, -1), self.korean_font_name),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(table)
            
            # PDF 생성
            doc.build(story)
            
            return pdf_path
            
        except Exception as e:
            return f"PDF 생성 중 오류 발생: {str(e)}"
    
    def generate_investment_report(self, symbol: str, period: str = "1mo") -> Dict[str, Any]:
        """
        특정 주식에 대한 투자 보고서 생성
        
        Args:
            symbol: 주식 심볼 (예: "005930")
            period: 분석 기간 (예: "1mo", "3mo", "6mo")
        
        Returns:
            투자 보고서 딕셔너리
        """
        try:
            # 1. 주식 정보 가져오기
            print(f"주식 정보를 가져오는 중... (심볼: {symbol})")
            stock_data = self.stock_fetcher.get_stock_price_yahoo(symbol, period)
            
            if 'error' in stock_data:
                return {"error": f"주식 정보 조회 실패: {stock_data['error']}"}
            
            # 2. 관련 뉴스 가져오기
            print("관련 뉴스를 가져오는 중...")
            news_data = self.stock_fetcher.get_stock_news(symbol, num_articles=5, days_back=7)
            
            # 3. 시장 요약 정보 가져오기
            print("시장 정보를 가져오는 중...")
            market_data = self.stock_fetcher.get_market_summary()
            
            if 'error' in market_data:
                market_data = {"kospi": {"current": 0, "change_percent": 0}, 
                              "kosdaq": {"current": 0, "change_percent": 0}}
            
            # 4. GPT 프롬프트 생성
            prompt = self.generate_stock_analysis_prompt(stock_data, news_data, market_data)
            
            # 5. GPT API 호출
            print("GPT API를 통해 투자 보고서를 생성하는 중...")
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "당신은 한국 주식 시장 전문 투자 분석가입니다. 객관적이고 전문적인 투자 보고서를 작성해주세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            report_content = response.choices[0].message.content
            
            # 6. 차트 생성
            print("주가 차트를 생성하는 중...")
            chart_path = self.generate_stock_price_chart(symbol, period)
            
            # 7. 관련 기업 비교 차트 생성
            print("관련 기업 비교 차트를 생성하는 중...")
            stock_list = self.stock_fetcher.get_korean_stock_list()
            related_symbols = [stock['symbol'] for stock in stock_list[:5]]  # 상위 5개
            comparison_chart_path = self.generate_comparison_chart(related_symbols, period)
            
            # 8. 인터랙티브 차트 생성
            print("인터랙티브 차트를 생성하는 중...")
            interactive_chart_path = self.generate_interactive_chart(symbol, period)
            
            # 9. 결과 구성
            result = {
                "symbol": symbol,
                "company_name": stock_data.get('company_name', 'N/A'),
                "report_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "analysis_period": period,
                "stock_data": stock_data,
                "news_count": len([n for n in news_data if 'error' not in n]),
                "market_data": market_data,
                "report_content": report_content,
                "chart_path": chart_path,
                "comparison_chart_path": comparison_chart_path,
                "interactive_chart_path": interactive_chart_path
            }
            
            return result
            
        except Exception as e:
            return {"error": f"투자 보고서 생성 중 오류 발생: {str(e)}"}
    
    def generate_market_report(self) -> Dict[str, Any]:
        """
        전체 시장에 대한 투자 보고서 생성
        
        Returns:
            시장 투자 보고서 딕셔너리
        """
        try:
            # 주요 주식들의 정보 가져오기
            print("주요 주식들의 정보를 가져오는 중...")
            stock_list = self.stock_fetcher.get_korean_stock_list()
            symbols = [stock['symbol'] for stock in stock_list[:5]]  # 상위 5개만
            stocks_data = self.stock_fetcher.get_multiple_stock_prices(symbols)
            
            # 시장 요약 정보
            market_data = self.stock_fetcher.get_market_summary()
            
            # 시장 분석 프롬프트 생성
            prompt = f"""
당신은 한국 주식 시장 전문 분석가입니다. 아래 정보를 바탕으로 한국 주식 시장 전반에 대한 투자 보고서를 작성해주세요.

## 주요 지수 현황
- KOSPI: {market_data.get('kospi', {}).get('current', 0):,.0f} ({market_data.get('kospi', {}).get('change_percent', 0):+.2f}%)
- KOSDAQ: {market_data.get('kosdaq', {}).get('current', 0):,.0f} ({market_data.get('kosdaq', {}).get('change_percent', 0):+.2f}%)

## 주요 종목 현황
"""
            
            for stock_data in stocks_data:
                if 'error' not in stock_data:
                    prompt += f"- {stock_data.get('company_name', 'N/A')}: {stock_data.get('current_price', 0):,.0f}원 ({stock_data.get('change_percent', 0):+.2f}%)\n"
            
            prompt += """
다음 형식으로 한국어로 시장 투자 보고서를 작성해주세요:

## 한국 주식 시장 투자 보고서

### 1. 시장 개요
- 현재 시장 상황과 주요 지수 동향

### 2. 섹터별 분석
- 주요 섹터의 성과와 특징

### 3. 투자 테마
- 현재 주목받는 투자 테마와 트렌드

### 4. 리스크 요인
- 시장에 영향을 미칠 수 있는 리스크 요인

### 5. 투자 전략
- 현재 시점에서의 투자 전략 제안

### 6. 시장 전망
- 단기 및 중기 시장 전망

보고서는 객관적이고 전문적인 톤으로 작성하되, 일반 투자자도 이해할 수 있도록 명확하게 설명해주세요.
"""
            
            # GPT API 호출
            print("GPT API를 통해 시장 보고서를 생성하는 중...")
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "당신은 한국 주식 시장 전문 분석가입니다. 객관적이고 전문적인 시장 투자 보고서를 작성해주세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            report_content = response.choices[0].message.content
            
            # 비교 차트 생성
            comparison_chart_path = self.generate_comparison_chart(symbols, "3mo")
            
            result = {
                "report_type": "market_report",
                "report_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "market_data": market_data,
                "analyzed_stocks": len([s for s in stocks_data if 'error' not in s]),
                "report_content": report_content,
                "comparison_chart_path": comparison_chart_path
            }
            
            return result
            
        except Exception as e:
            return {"error": f"시장 보고서 생성 중 오류 발생: {str(e)}"}
    
    def save_report_to_file(self, report: Dict[str, Any], filename: str = None) -> str:
        """
        투자 보고서를 파일로 저장
        
        Args:
            report: 투자 보고서 딕셔너리
            filename: 저장할 파일명 (없으면 자동 생성)
        
        Returns:
            저장된 파일 경로
        """
        try:
            if not filename:
                if 'symbol' in report:
                    filename = f"investment_report_{report['symbol']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                else:
                    filename = f"market_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            # reports 디렉토리 생성
            reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
            os.makedirs(reports_dir, exist_ok=True)
            
            filepath = os.path.join(reports_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                if 'symbol' in report:
                    f.write(f"투자 보고서 - {report['company_name']} ({report['symbol']})\n")
                    f.write(f"생성일시: {report['report_date']}\n")
                    f.write(f"분석기간: {report['analysis_period']}\n")
                    f.write("=" * 50 + "\n\n")
                else:
                    f.write("한국 주식 시장 투자 보고서\n")
                    f.write(f"생성일시: {report['report_date']}\n")
                    f.write("=" * 50 + "\n\n")
                
                f.write(report['report_content'])
                
                # 추가 정보
                f.write("\n\n" + "=" * 50 + "\n")
                f.write("분석 데이터 요약\n")
                f.write("=" * 50 + "\n")
                
                if 'stock_data' in report:
                    stock = report['stock_data']
                    f.write(f"현재가: {stock.get('current_price', 0):,.0f}원\n")
                    f.write(f"전일대비: {stock.get('change', 0):+,.0f}원 ({stock.get('change_percent', 0):+.2f}%)\n")
                    f.write(f"거래량: {stock.get('volume', 0):,}주\n")
                    f.write(f"PER: {stock.get('pe_ratio', 0):.2f}\n")
                    f.write(f"배당수익률: {stock.get('dividend_yield', 0):.2f}%\n")
                
                if 'news_count' in report:
                    f.write(f"분석된 뉴스 수: {report['news_count']}개\n")
                
                # 차트 파일 경로 정보
                if 'chart_path' in report and report['chart_path']:
                    f.write(f"주가 차트: {report['chart_path']}\n")
                if 'comparison_chart_path' in report and report['comparison_chart_path']:
                    f.write(f"비교 차트: {report['comparison_chart_path']}\n")
                if 'interactive_chart_path' in report and report['interactive_chart_path']:
                    f.write(f"인터랙티브 차트: {report['interactive_chart_path']}\n")
            
            return filepath
            
        except Exception as e:
            return f"파일 저장 중 오류 발생: {str(e)}"
    
    def generate_complete_report(self, symbol: str, period: str = "3mo") -> Dict[str, Any]:
        """
        완전한 투자 보고서 생성 (텍스트 + PDF + 차트)
        
        Args:
            symbol: 주식 심볼
            period: 분석 기간
        
        Returns:
            완전한 보고서 정보
        """
        try:
            # 1. 기본 보고서 생성
            report = self.generate_investment_report(symbol, period)
            
            if 'error' in report:
                return report
            
            # 2. 텍스트 파일 저장
            txt_path = self.save_report_to_file(report)
            
            # 3. PDF 파일 생성
            pdf_path = self.create_pdf_report(report, report.get('chart_path'), report.get('comparison_chart_path'))
            
            # 4. 결과에 파일 경로 추가
            report['txt_file_path'] = txt_path
            report['pdf_file_path'] = pdf_path
            
            return report
            
        except Exception as e:
            return {"error": f"완전한 보고서 생성 중 오류 발생: {str(e)}"}

# 사용 예시
def main():
    generator = InvestmentReportGenerator()
    
    # 한글 PDF 테스트
    print("=== 한글 PDF 테스트 ===")
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
        pdf_path = generator.create_pdf_report(test_report)
        if pdf_path and not pdf_path.startswith("PDF 생성 중 오류"):
            print(f"✅ 한글 PDF 테스트 성공: {pdf_path}")
        else:
            print(f"❌ 한글 PDF 테스트 실패: {pdf_path}")
    except Exception as e:
        print(f"❌ 한글 PDF 테스트 중 오류: {str(e)}")
    
    # 1. 완전한 투자 보고서 생성 (텍스트 + PDF + 차트)
    print("\n=== 삼성전자 완전한 투자 보고서 생성 ===")
    samsung_report = generator.generate_complete_report("005930", "3mo")
    
    if 'error' not in samsung_report:
        print("보고서 생성 완료!")
        print(f"회사명: {samsung_report['company_name']}")
        print(f"생성일시: {samsung_report['report_date']}")
        print(f"분석된 뉴스 수: {samsung_report['news_count']}개")
        
        # 파일 경로 출력
        print(f"텍스트 파일: {samsung_report['txt_file_path']}")
        print(f"PDF 파일: {samsung_report['pdf_file_path']}")
        if samsung_report.get('chart_path'):
            print(f"주가 차트: {samsung_report['chart_path']}")
        if samsung_report.get('comparison_chart_path'):
            print(f"비교 차트: {samsung_report['comparison_chart_path']}")
        if samsung_report.get('interactive_chart_path'):
            print(f"인터랙티브 차트: {samsung_report['interactive_chart_path']}")
        
        # 보고서 내용 일부 출력
        print("\n=== 보고서 내용 미리보기 ===")
        lines = samsung_report['report_content'].split('\n')[:10]
        for line in lines:
            print(line)
    else:
        print(f"오류: {samsung_report['error']}")
    
    # 2. 시장 투자 보고서 생성
    print("\n=== 시장 투자 보고서 생성 ===")
    market_report = generator.generate_market_report()
    
    if 'error' not in market_report:
        print("시장 보고서 생성 완료!")
        print(f"생성일시: {market_report['report_date']}")
        print(f"분석된 주식 수: {market_report['analyzed_stocks']}개")
        
        # 파일로 저장
        filepath = generator.save_report_to_file(market_report)
        print(f"시장 보고서가 저장되었습니다: {filepath}")
        
        # PDF 생성
        pdf_path = generator.create_pdf_report(market_report, None, market_report.get('comparison_chart_path'))
        print(f"시장 보고서 PDF가 생성되었습니다: {pdf_path}")
    else:
        print(f"오류: {market_report['error']}")

if __name__ == "__main__":
    main()
