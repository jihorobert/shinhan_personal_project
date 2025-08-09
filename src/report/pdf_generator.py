# PDF 보고서 생성 모듈
# reportlab을 사용하여 투자보고서를 PDF 형식으로 생성

from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import black, blue, red, green
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import font_manager
import io
from reportlab.lib.utils import ImageReader
import pandas as pd

class PDFReportGenerator:
    def __init__(self):
        self.setup_fonts()
        self.setup_styles()
    
    def setup_fonts(self):
        """한글 폰트 설정"""
        try:
            # 시스템에서 TTF 형식의 한글 폰트 찾기 (TTC 파일은 reportlab에서 지원하지 않음)
            korean_fonts = [
                '/System/Library/Fonts/Supplemental/AppleGothic.ttf',  # macOS
                '/System/Library/Fonts/Supplemental/NotoSansGothic-Regular.ttf',  # macOS
                'C:/Windows/Fonts/malgun.ttf',  # Windows
                'C:/Windows/Fonts/gulim.ttc',  # Windows
                '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',  # Linux
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux fallback
            ]
            
            font_registered = False
            for font_path in korean_fonts:
                if os.path.exists(font_path):
                    try:
                        # TTC 파일인지 확인
                        if font_path.endswith('.ttc'):
                            print(f"TTC 파일은 지원하지 않음: {font_path}")
                            continue
                            
                        pdfmetrics.registerFont(TTFont('Korean', font_path))
                        font_registered = True
                        print(f"한글 폰트 등록 성공: {font_path}")
                        break
                    except Exception as font_error:
                        print(f"폰트 등록 실패 {font_path}: {font_error}")
                        continue
            
            if not font_registered:
                print("한글 폰트를 찾을 수 없어 기본 폰트를 사용합니다.")
                self.korean_font = 'Helvetica'
            else:
                self.korean_font = 'Korean'
                
        except Exception as e:
            print(f"폰트 설정 오류: {e}")
            self.korean_font = 'Helvetica'
    
    def setup_styles(self):
        """PDF 스타일 설정"""
        self.styles = getSampleStyleSheet()
        
        # 한글 제목 스타일
        self.title_style = ParagraphStyle(
            'KoreanTitle',
            parent=self.styles['Title'],
            fontName=self.korean_font,
            fontSize=18,
            textColor=colors.darkblue,
            spaceAfter=20,
            alignment=1  # 중앙 정렬
        )
        
        # 한글 제목2 스타일
        self.heading_style = ParagraphStyle(
            'KoreanHeading',
            parent=self.styles['Heading2'],
            fontName=self.korean_font,
            fontSize=14,
            textColor=colors.darkblue,
            spaceBefore=15,
            spaceAfter=10
        )
        
        # 한글 본문 스타일
        self.body_style = ParagraphStyle(
            'KoreanBody',
            parent=self.styles['Normal'],
            fontName=self.korean_font,
            fontSize=10,
            leading=14,
            spaceAfter=6
        )
        
        # 한글 작은 글씨 스타일
        self.small_style = ParagraphStyle(
            'KoreanSmall',
            parent=self.styles['Normal'],
            fontName=self.korean_font,
            fontSize=8,
            textColor=colors.grey
        )

    def create_stock_chart(self, stock_data):
        """과거/현재/미래 전망을 포함한 주가 차트 생성"""
        try:
            if 'historical_data' not in stock_data or not stock_data['historical_data']:
                return None
                
            # 한글 폰트 설정 (matplotlib용)
            import matplotlib.pyplot as plt
            import matplotlib.font_manager as fm
            import numpy as np
            from datetime import datetime, timedelta
            
            # matplotlib용 한글 폰트 설정
            import warnings
            warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib.font_manager')
            
            # 사용 가능한 폰트 찾기
            available_fonts = [f.name for f in fm.fontManager.ttflist]
            korean_fonts = ['AppleGothic', 'Apple SD Gothic Neo']
            
            for font in korean_fonts:
                if font in available_fonts:
                    plt.rcParams['font.family'] = [font]
                    break
            else:
                plt.rcParams['font.family'] = ['DejaVu Sans']
                
            plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지
            
            # 데이터 준비
            dates = []
            prices = []
            
            for data in stock_data['historical_data']:
                dates.append(pd.to_datetime(data['date']))
                prices.append(data['close'])
            
            # 데이터를 날짜순으로 정렬
            sorted_data = sorted(zip(dates, prices))
            dates, prices = zip(*sorted_data)
            dates = list(dates)
            prices = list(prices)
            
            # 차트 생성 (더 큰 사이즈)
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # 과거 데이터 (파란색 실선)
            ax.plot(dates, prices, linewidth=2.5, color='#1f77b4', label='과거 주가', alpha=0.8)
            
            # 현재가 포인트 강조
            current_price = stock_data.get('current_price', prices[-1] if prices else 0)
            current_date = dates[-1] if dates else datetime.now()
            ax.scatter([current_date], [current_price], color='red', s=100, zorder=5, label=f'현재가: {current_price:,}원')
            
            # 미래 전망 라인 (동적 추세 분석)
            if len(prices) >= 10:
                # 다중 기간 추세 분석으로 더 정확한 예측
                short_term_prices = prices[-5:]  # 단기 추세 (5일)
                medium_term_prices = prices[-15:] if len(prices) >= 15 else prices[-10:]  # 중기 추세
                long_term_prices = prices[-30:] if len(prices) >= 30 else prices  # 장기 추세
                
                # 각 기간별 추세 계산
                short_trend = (short_term_prices[-1] - short_term_prices[0]) / len(short_term_prices)
                medium_trend = (medium_term_prices[-1] - medium_term_prices[0]) / len(medium_term_prices)
                long_trend = (long_term_prices[-1] - long_term_prices[0]) / len(long_term_prices)
                
                # 가중 평균으로 최종 추세 결정 (단기 50%, 중기 30%, 장기 20%)
                weighted_trend = (short_trend * 0.5) + (medium_trend * 0.3) + (long_trend * 0.2)
                
                # 추세 강도 계산 (최근 변동성 고려)
                recent_volatility = np.std(prices[-10:])
                price_range = max(prices[-10:]) - min(prices[-10:])
                trend_strength = abs(weighted_trend) / (recent_volatility + 1e-6)  # 0으로 나누기 방지
                
                # 동적 추세 조정 - 강한 추세일수록 더 뚜렷하게, 약한 추세는 보수적으로
                if trend_strength > 0.5:  # 강한 추세
                    dynamic_trend = weighted_trend * 1.2  # 추세 강화
                    trend_confidence = 0.8
                elif trend_strength > 0.2:  # 중간 추세
                    dynamic_trend = weighted_trend * 1.0  # 원래 추세 유지
                    trend_confidence = 0.6
                else:  # 약한 추세
                    dynamic_trend = weighted_trend * 0.7  # 추세 완화
                    trend_confidence = 0.4
                
                # 미래 30일 예측 (비선형 곡선으로 더 현실적)
                future_dates = [current_date + timedelta(days=i) for i in range(1, 31)]
                future_prices = []
                
                for i in range(1, 31):
                    # 시간이 지날수록 추세의 영향력 감소 (현실적인 예측)
                    time_decay = np.exp(-i / 20)  # 20일 반감기
                    adjusted_trend = dynamic_trend * time_decay
                    
                    # 약간의 노이즈 추가로 더 자연스러운 곡선
                    noise_factor = np.sin(i / 3) * (recent_volatility * 0.1)
                    predicted_price = current_price + (adjusted_trend * i) + noise_factor
                    future_prices.append(predicted_price)
                
                # 동적 변동성 계산 (추세 강도에 따라 조정)
                base_volatility = np.std(prices[-20:]) if len(prices) >= 20 else np.std(prices)
                dynamic_volatility = base_volatility * (1.5 + trend_strength)  # 추세가 강할수록 변동성 증가
                
                future_upper = [p + dynamic_volatility for p in future_prices]
                future_lower = [p - dynamic_volatility for p in future_prices]
                
                # 추세 방향에 따른 색상 및 스타일 결정
                if weighted_trend > 0:
                    trend_color = '#ff4444'  # 상승 추세 - 빨간색
                    trend_label = f'예상 추세 (상승 {trend_strength:.1f})'
                    line_style = '-'  # 실선으로 강조
                elif weighted_trend < 0:
                    trend_color = '#4444ff'  # 하락 추세 - 파란색
                    trend_label = f'예상 추세 (하락 {trend_strength:.1f})'
                    line_style = '-'  # 실선으로 강조
                else:
                    trend_color = '#888888'  # 횡보 - 회색
                    trend_label = '예상 추세 (횡보)'
                    line_style = '--'  # 점선
                
                # 미래 예측선 (동적 색상과 굵기)
                line_width = 2.5 + (trend_strength * 1.5)  # 추세가 강할수록 굵게
                ax.plot(future_dates, future_prices, linewidth=line_width, color=trend_color, 
                       linestyle=line_style, alpha=0.8, label=trend_label)
                
                # 추세 방향 화살표 추가 (마지막 지점에)
                if abs(weighted_trend) > recent_volatility * 0.1:  # 의미있는 추세일 때만
                    arrow_props = dict(arrowstyle='->', lw=2, color=trend_color)
                    if weighted_trend > 0:
                        ax.annotate('', xy=(future_dates[-1], future_prices[-1] + dynamic_volatility * 0.3), 
                                   xytext=(future_dates[-5], future_prices[-5]), arrowprops=arrow_props)
                    else:
                        ax.annotate('', xy=(future_dates[-1], future_prices[-1] - dynamic_volatility * 0.3), 
                                   xytext=(future_dates[-5], future_prices[-5]), arrowprops=arrow_props)
                
                # 신뢰구간 (추세 강도에 따른 투명도)
                confidence_alpha = 0.1 + (trend_confidence * 0.15)
                ax.fill_between(future_dates, future_lower, future_upper, 
                               color=trend_color, alpha=confidence_alpha, label=f'신뢰구간 ({trend_confidence*100:.0f}%)')
            
            # 이동평균선 추가 (5일, 20일)
            if len(prices) >= 20:
                # 5일 이동평균
                ma5 = pd.Series(prices).rolling(window=5).mean()
                ax.plot(dates, ma5, linewidth=1.5, color='green', alpha=0.7, label='5일 이평선')
                
                # 20일 이동평균
                ma20 = pd.Series(prices).rolling(window=20).mean()
                ax.plot(dates, ma20, linewidth=1.5, color='purple', alpha=0.7, label='20일 이평선')
            
            # 차트 스타일링
            company_name = stock_data.get('company_name', '주식')
            ax.set_title(f'{company_name} 주가 분석 차트', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('날짜', fontsize=12)
            ax.set_ylabel('주가 (원)', fontsize=12)
            
            # 격자 스타일
            ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
            ax.set_axisbelow(True)
            
            # 범례
            ax.legend(loc='upper left', frameon=True, fancybox=True, shadow=True)
            
            # Y축 포맷팅 (천 단위 콤마)
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:,.0f}'))
            
            # X축 날짜 포맷팅
            if len(dates) > 30:
                ax.xaxis.set_major_locator(mdates.WeekdayLocator())
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            else:
                ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            
            plt.xticks(rotation=45)
            
            # 차트 영역 최적화
            plt.tight_layout()
            
            # 배경색 설정
            fig.patch.set_facecolor('white')
            ax.set_facecolor('#fafafa')
            
            # 메모리에 이미지 저장
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=200, bbox_inches='tight', 
                       facecolor='white', edgecolor='none')
            img_buffer.seek(0)
            plt.close(fig)  # 메모리 해제
            
            return img_buffer
            
        except Exception as e:
            print(f"차트 생성 오류: {e}")
            import traceback
            traceback.print_exc()
            return None

    def generate_pdf_report(self, json_report_path, output_path=None):
        """JSON 보고서를 PDF로 변환"""
        try:
            # JSON 보고서 읽기
            with open(json_report_path, 'r', encoding='utf-8') as f:
                report_data = json.load(f)
            
            # 출력 파일명 설정
            if output_path is None:
                base_name = os.path.splitext(json_report_path)[0]
                output_path = f"{base_name}.pdf"
            
            # PDF 문서 생성
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            story = []
            
            # 제목
            company_name = report_data.get('company_name', 'Unknown')
            report_date = report_data.get('report_date', datetime.now().strftime('%Y-%m-%d'))
            
            title = Paragraph(f"{company_name} 투자분석보고서", self.title_style)
            story.append(title)
            story.append(Spacer(1, 20))
            
            # 보고서 기본 정보
            info_data = [
                ['보고서 생성일', report_date],
                ['분석 기간', report_data.get('analysis_period', 'N/A')],
                ['참고 뉴스 수', f"{report_data.get('news_count', 0)}개"],
                ['데이터 출처', 'Yahoo Finance, NewsAPI, OpenAI GPT-4']
            ]
            
            info_table = Table(info_data, colWidths=[2*inch, 3*inch])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), self.korean_font),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            story.append(info_table)
            story.append(Spacer(1, 20))
            
            # 주가 정보 섹션
            if 'stock_data' in report_data:
                stock_data = report_data['stock_data']
                
                heading = Paragraph("주가 현황", self.heading_style)
                story.append(heading)
                
                # 주가 데이터 테이블
                current_price = stock_data.get('current_price', 'N/A')
                change = stock_data.get('change', 'N/A')
                change_percent = stock_data.get('change_percent', 'N/A')
                
                # 변화율에 따른 색상 설정
                if isinstance(change_percent, (int, float)):
                    if change_percent > 0:
                        change_color = colors.red
                        change_symbol = "▲"
                    elif change_percent < 0:
                        change_color = colors.blue
                        change_symbol = "▼"
                    else:
                        change_color = colors.black
                        change_symbol = ""
                else:
                    change_color = colors.black
                    change_symbol = ""
                
                stock_table_data = [
                    ['항목', '값'],
                    ['현재가', f"{current_price:,}원" if isinstance(current_price, (int, float)) else str(current_price)],
                    ['전일대비', f"{change_symbol} {change}원 ({change_percent}%)" if change != 'N/A' else 'N/A'],
                    ['거래량', f"{stock_data.get('volume', 'N/A'):,}주" if isinstance(stock_data.get('volume'), (int, float)) else str(stock_data.get('volume', 'N/A'))],
                    ['고가', f"{stock_data.get('high', 'N/A')}원"],
                    ['저가', f"{stock_data.get('low', 'N/A')}원"],
                    ['시가총액', str(stock_data.get('market_cap', 'N/A'))],
                    ['PER', str(stock_data.get('pe_ratio', 'N/A'))],
                    ['52주 최고가', f"{stock_data.get('52_week_high', 'N/A')}원"],
                    ['52주 최저가', f"{stock_data.get('52_week_low', 'N/A')}원"]
                ]
                
                stock_table = Table(stock_table_data, colWidths=[2*inch, 3*inch])
                stock_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), self.korean_font),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                
                story.append(stock_table)
                story.append(Spacer(1, 15))
                
                # 주가 차트 추가
                chart_buffer = self.create_stock_chart(stock_data)
                if chart_buffer:
                    from reportlab.platypus import Image
                    chart = Image(chart_buffer, width=7*inch, height=4.2*inch)
                    story.append(chart)
                    story.append(Spacer(1, 15))
            
            # GPT 분석 결과
            if 'investment_report' in report_data:
                heading = Paragraph("투자분석 리포트", self.heading_style)
                story.append(heading)
                
                # GPT 분석 내용을 단락별로 분리
                analysis_text = report_data['investment_report']
                paragraphs = analysis_text.split('\n\n')
                
                for paragraph in paragraphs:
                    if paragraph.strip():
                        # 텍스트 정리 (HTML 태그 제거)
                        import re
                        clean_text = paragraph.strip()
                        # **굵은 글씨** 처리를 위한 간단한 변환
                        clean_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', clean_text)
                        # HTML 태그가 중첩되지 않도록 정리
                        clean_text = re.sub(r'<b>\s*<b>', '<b>', clean_text)
                        clean_text = re.sub(r'</b>\s*</b>', '</b>', clean_text)
                        
                        # 번호 리스트 처리
                        if clean_text.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.')):
                            # 이미 <b> 태그가 있는지 확인
                            if not clean_text.startswith('<b>'):
                                clean_text = f"<b>{clean_text}</b>"
                        
                        try:
                            para = Paragraph(clean_text, self.body_style)
                            story.append(para)
                            story.append(Spacer(1, 8))
                        except Exception as e:
                            # 태그 처리에 실패하면 일반 텍스트로 처리
                            plain_text = re.sub(r'<[^>]+>', '', clean_text)
                            para = Paragraph(plain_text, self.body_style)
                            story.append(para)
                            story.append(Spacer(1, 8))
            
            # 페이지 하단 정보
            story.append(Spacer(1, 30))
            footer_text = f"본 보고서는 {datetime.now().strftime('%Y년 %m월 %d일')}에 생성되었으며, 투자 참고용으로만 사용하시기 바랍니다."
            footer = Paragraph(footer_text, self.small_style)
            story.append(footer)
            
            # PDF 생성
            doc.build(story)
            
            print(f"PDF 보고서가 생성되었습니다: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"PDF 생성 중 오류 발생: {e}")
            return None

    def generate_pdf_from_data(self, report_data, output_path):
        """딕셔너리 형태의 보고서 데이터를 직접 PDF로 변환"""
        try:
            # PDF 문서 생성
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            story = []
            
            # 제목
            company_name = report_data.get('company_name', 'Unknown')
            report_date = report_data.get('report_date', datetime.now().strftime('%Y-%m-%d'))
            
            title = Paragraph(f"{company_name} 투자분석보고서", self.title_style)
            story.append(title)
            story.append(Spacer(1, 20))
            
            # 보고서 기본 정보
            info_data = [
                ['보고서 생성일', report_date],
                ['분석 기간', report_data.get('analysis_period', 'N/A')],
                ['참고 뉴스 수', f"{report_data.get('news_count', 0)}개"],
                ['데이터 출처', 'Yahoo Finance, NewsAPI, OpenAI GPT-4']
            ]
            
            info_table = Table(info_data, colWidths=[2*inch, 3*inch])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), self.korean_font),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            story.append(info_table)
            story.append(Spacer(1, 20))
            
            # 주가 정보 섹션
            if 'stock_data' in report_data:
                stock_data = report_data['stock_data']
                
                heading = Paragraph("주가 현황", self.heading_style)
                story.append(heading)
                
                # 주가 데이터 테이블
                current_price = stock_data.get('current_price', 'N/A')
                change = stock_data.get('change', 'N/A')
                change_percent = stock_data.get('change_percent', 'N/A')
                
                stock_table_data = [
                    ['항목', '값'],
                    ['현재가', f"{current_price:,}원" if isinstance(current_price, (int, float)) else str(current_price)],
                    ['전일대비', f"{change}원 ({change_percent}%)" if change != 'N/A' else 'N/A'],
                    ['거래량', f"{stock_data.get('volume', 'N/A'):,}주" if isinstance(stock_data.get('volume'), (int, float)) else str(stock_data.get('volume', 'N/A'))],
                    ['고가', f"{stock_data.get('high', 'N/A')}원"],
                    ['저가', f"{stock_data.get('low', 'N/A')}원"],
                    ['시가총액', str(stock_data.get('market_cap', 'N/A'))],
                    ['PER', str(stock_data.get('pe_ratio', 'N/A'))],
                    ['52주 최고가', f"{stock_data.get('52_week_high', 'N/A')}원"],
                    ['52주 최저가', f"{stock_data.get('52_week_low', 'N/A')}원"]
                ]
                
                stock_table = Table(stock_table_data, colWidths=[2*inch, 3*inch])
                stock_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), self.korean_font),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                
                story.append(stock_table)
                story.append(Spacer(1, 15))
                
                # 주가 차트 추가
                chart_buffer = self.create_stock_chart(stock_data)
                if chart_buffer:
                    from reportlab.platypus import Image
                    chart = Image(chart_buffer, width=7*inch, height=4.2*inch)
                    story.append(chart)
                    story.append(Spacer(1, 15))
            
            # GPT 분석 결과
            if 'investment_report' in report_data:
                heading = Paragraph("투자분석 리포트", self.heading_style)
                story.append(heading)
                
                # GPT 분석 내용을 단락별로 분리
                analysis_text = report_data['investment_report']
                paragraphs = analysis_text.split('\n\n')
                
                for paragraph in paragraphs:
                    if paragraph.strip():
                        # 텍스트 정리 (HTML 태그 제거)
                        import re
                        clean_text = paragraph.strip()
                        # **굵은 글씨** 처리를 위한 간단한 변환
                        clean_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', clean_text)
                        # HTML 태그가 중첩되지 않도록 정리
                        clean_text = re.sub(r'<b>\s*<b>', '<b>', clean_text)
                        clean_text = re.sub(r'</b>\s*</b>', '</b>', clean_text)
                        
                        # 번호 리스트 처리
                        if clean_text.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.')):
                            # 이미 <b> 태그가 있는지 확인
                            if not clean_text.startswith('<b>'):
                                clean_text = f"<b>{clean_text}</b>"
                        
                        try:
                            para = Paragraph(clean_text, self.body_style)
                            story.append(para)
                            story.append(Spacer(1, 8))
                        except Exception as e:
                            # 태그 처리에 실패하면 일반 텍스트로 처리
                            plain_text = re.sub(r'<[^>]+>', '', clean_text)
                            para = Paragraph(plain_text, self.body_style)
                            story.append(para)
                            story.append(Spacer(1, 8))
            
            # 페이지 하단 정보
            story.append(Spacer(1, 30))
            footer_text = f"본 보고서는 {datetime.now().strftime('%Y년 %m월 %d일')}에 생성되었으며, 투자 참고용으로만 사용하시기 바랍니다."
            footer = Paragraph(footer_text, self.small_style)
            story.append(footer)
            
            # PDF 생성
            doc.build(story)
            
            print(f"PDF 보고서가 생성되었습니다: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"PDF 생성 중 오류 발생: {e}")
            return None

# 편의 함수들
def convert_json_to_pdf(json_file_path, pdf_output_path=None):
    """JSON 보고서 파일을 PDF로 변환하는 편의 함수"""
    generator = PDFReportGenerator()
    return generator.generate_pdf_report(json_file_path, pdf_output_path)

def generate_pdf_report_from_data(report_data, output_path):
    """딕셔너리 데이터를 PDF로 변환하는 편의 함수"""
    generator = PDFReportGenerator()
    return generator.generate_pdf_from_data(report_data, output_path)

# 테스트용 메인 함수
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
        pdf_file = sys.argv[2] if len(sys.argv) > 2 else None
        
        if os.path.exists(json_file):
            result = convert_json_to_pdf(json_file, pdf_file)
            if result:
                print(f"변환 완료: {result}")
            else:
                print("변환 실패")
        else:
            print(f"파일을 찾을 수 없습니다: {json_file}")
    else:
        print("사용법: python pdf_generator.py <json_file> [pdf_file]")