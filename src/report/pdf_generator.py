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
        """주가 차트 생성"""
        try:
            if 'historical_data' not in stock_data or not stock_data['historical_data']:
                return None
                
            # 한글 폰트 설정 (matplotlib용)
            import matplotlib.pyplot as plt
            import matplotlib.font_manager as fm
            
            # matplotlib용 한글 폰트 설정 (시스템에서 사용 가능한 폰트명 사용)
            korean_font_names = [
                'Apple SD Gothic Neo',  # macOS
                'AppleGothic',          # macOS
                'Noto Sans Gothic',     # macOS
                'Malgun Gothic',        # Windows
                'NanumGothic',          # Linux
                'DejaVu Sans'           # Fallback
            ]
            
            font_prop = None
            for font_name in korean_font_names:
                try:
                    # 시스템에서 해당 폰트가 사용 가능한지 확인
                    available_fonts = [f.name for f in fm.fontManager.ttflist]
                    if font_name in available_fonts:
                        font_prop = fm.FontProperties(family=font_name)
                        break
                except:
                    continue
            
            # 데이터 준비
            dates = []
            prices = []
            
            for data in stock_data['historical_data']:
                dates.append(pd.to_datetime(data['date']))
                prices.append(data['close'])
            
            # 차트 생성
            plt.figure(figsize=(10, 6))
            plt.plot(dates, prices, linewidth=2, color='blue')
            
            # 한글 폰트가 있으면 사용, 없으면 영어로 표시
            if font_prop:
                plt.title(f"{stock_data['company_name']} Stock Price Trend", fontsize=14, pad=20, fontproperties=font_prop)
                plt.xlabel('Date', fontsize=12, fontproperties=font_prop)
                plt.ylabel('Price (KRW)', fontsize=12, fontproperties=font_prop)
            else:
                plt.title(f"{stock_data['company_name']} Stock Price Trend", fontsize=14, pad=20)
                plt.xlabel('Date', fontsize=12)
                plt.ylabel('Price (KRW)', fontsize=12)
            
            plt.grid(True, alpha=0.3)
            
            # 날짜 포맷팅
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
            plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=2))
            plt.xticks(rotation=45)
            
            plt.tight_layout()
            
            # 메모리에 이미지 저장
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            plt.close()
            
            return img_buffer
            
        except Exception as e:
            print(f"차트 생성 오류: {e}")
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
                
                # 주가 차트 추가 (임시로 비활성화)
                # chart_buffer = self.create_stock_chart(stock_data)
                # if chart_buffer:
                #     from reportlab.platypus import Image
                #     chart_image = ImageReader(chart_buffer)
                #     chart = Image(chart_image, width=6*inch, height=3.6*inch)
                #     story.append(chart)
                #     story.append(Spacer(1, 15))
            
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
                
                # 주가 차트 추가 (임시로 비활성화)
                # chart_buffer = self.create_stock_chart(stock_data)
                # if chart_buffer:
                #     from reportlab.platypus import Image
                #     chart_image = ImageReader(chart_buffer)
                #     chart = Image(chart_image, width=6*inch, height=3.6*inch)
                #     story.append(chart)
                #     story.append(Spacer(1, 15))
            
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