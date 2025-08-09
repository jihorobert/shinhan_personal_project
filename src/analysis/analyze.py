# GPT를 사용한 투자보고서 분석 모듈
from dotenv import load_dotenv
import os
import json
import sys
from datetime import datetime, timedelta

# 프로젝트 루트 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from fetch.stock_fetcher import get_stock_data, KoreanStockFetcher
from fetch.news_fetcher import get_latest_news
from report.pdf_generator import generate_pdf_report_from_data

load_dotenv()

from openai import OpenAI
import numpy as np

client = OpenAI(api_key=os.getenv("GPT_KEY"))

def analyze_technical_indicators(stock_info):
    """
    주가 데이터를 바탕으로 기술적 지표들을 분석하는 함수
    """
    try:
        historical_data = stock_info.get('historical_data', [])
        if not historical_data or len(historical_data) < 5:
            return {
                'short_trend': 'N/A (데이터 부족)',
                'medium_trend': 'N/A (데이터 부족)', 
                'long_trend': 'N/A (데이터 부족)',
                'trend_strength': 'N/A',
                'volatility_level': 'N/A',
                'price_vs_ma': 'N/A',
                'support_resistance': 'N/A',
                'volume_ratio': 'N/A'
            }
        
        # 가격 데이터 추출 (최신순으로 정렬)
        prices = [float(data['close']) for data in historical_data]
        volumes = [float(data.get('volume', 0)) for data in historical_data]
        
        current_price = stock_info.get('current_price', prices[0] if prices else 0)
        
        # 1. 추세 분석 (단기/중기/장기)
        def calculate_trend(price_list, period_name):
            if len(price_list) < 2:
                return f"N/A (데이터 부족)"
            
            start_price = price_list[-1]  # 가장 오래된 가격
            end_price = price_list[0]     # 가장 최근 가격
            
            if start_price == 0:
                return "N/A (데이터 오류)"
                
            change_percent = ((end_price - start_price) / start_price) * 100
            
            if change_percent > 2:
                return f"강한 상승세 (+{change_percent:.1f}%)"
            elif change_percent > 0.5:
                return f"상승세 (+{change_percent:.1f}%)"
            elif change_percent > -0.5:
                return f"횡보 ({change_percent:+.1f}%)"
            elif change_percent > -2:
                return f"하락세 ({change_percent:.1f}%)"
            else:
                return f"강한 하락세 ({change_percent:.1f}%)"
        
        short_trend = calculate_trend(prices[:5], "단기")
        medium_trend = calculate_trend(prices[:20] if len(prices) >= 20 else prices, "중기")
        long_trend = calculate_trend(prices, "장기")
        
        # 2. 추세 강도 계산
        recent_prices = prices[:10] if len(prices) >= 10 else prices
        if len(recent_prices) >= 3:
            price_changes = [abs(recent_prices[i] - recent_prices[i+1]) for i in range(len(recent_prices)-1)]
            avg_change = np.mean(price_changes)
            price_std = np.std(recent_prices)
            
            if price_std > 0:
                trend_strength_ratio = avg_change / price_std
                if trend_strength_ratio > 1.5:
                    trend_strength = "매우 강함"
                elif trend_strength_ratio > 1.0:
                    trend_strength = "강함"
                elif trend_strength_ratio > 0.5:
                    trend_strength = "보통"
                else:
                    trend_strength = "약함"
            else:
                trend_strength = "N/A"
        else:
            trend_strength = "N/A (데이터 부족)"
        
        # 3. 변동성 수준 분석
        if len(prices) >= 10:
            volatility = np.std(prices[:10]) / np.mean(prices[:10]) * 100
            if volatility > 5:
                volatility_level = f"높음 ({volatility:.1f}%)"
            elif volatility > 2:
                volatility_level = f"보통 ({volatility:.1f}%)"
            else:
                volatility_level = f"낮음 ({volatility:.1f}%)"
        else:
            volatility_level = "N/A (데이터 부족)"
        
        # 4. 이동평균 대비 현재가 위치
        if len(prices) >= 20:
            ma5 = np.mean(prices[:5])
            ma20 = np.mean(prices[:20])
            
            if current_price > ma5 > ma20:
                price_vs_ma = "강세 (현재가 > 5일선 > 20일선)"
            elif current_price > ma5 and current_price > ma20:
                price_vs_ma = "상승 추세 (현재가 > 이동평균선들)"
            elif current_price < ma5 < ma20:
                price_vs_ma = "약세 (현재가 < 5일선 < 20일선)"
            elif current_price < ma5 and current_price < ma20:
                price_vs_ma = "하락 추세 (현재가 < 이동평균선들)"
            else:
                price_vs_ma = "혼조 (이동평균선들과 교차)"
        else:
            price_vs_ma = "N/A (데이터 부족)"
        
        # 5. 지지/저항 수준 분석
        if len(prices) >= 20:
            recent_high = max(prices[:20])
            recent_low = min(prices[:20])
            current_position = (current_price - recent_low) / (recent_high - recent_low) * 100
            
            if current_position > 80:
                support_resistance = f"저항선 근처 (상위 {current_position:.0f}% 구간)"
            elif current_position < 20:
                support_resistance = f"지지선 근처 (하위 {current_position:.0f}% 구간)"
            else:
                support_resistance = f"중간 구간 ({current_position:.0f}% 위치)"
        else:
            support_resistance = "N/A (데이터 부족)"
        
        # 6. 거래량 비율 분석
        if len(volumes) >= 10:
            recent_volume = volumes[0] if volumes[0] > 0 else 1
            avg_volume = np.mean([v for v in volumes[:10] if v > 0])
            
            if avg_volume > 0:
                volume_ratio = recent_volume / avg_volume
                if volume_ratio > 2:
                    volume_ratio_text = f"매우 높음 ({volume_ratio:.1f}배)"
                elif volume_ratio > 1.5:
                    volume_ratio_text = f"높음 ({volume_ratio:.1f}배)"
                elif volume_ratio > 0.7:
                    volume_ratio_text = f"보통 ({volume_ratio:.1f}배)"
                else:
                    volume_ratio_text = f"낮음 ({volume_ratio:.1f}배)"
            else:
                volume_ratio_text = "N/A"
        else:
            volume_ratio_text = "N/A (데이터 부족)"
        
        return {
            'short_trend': short_trend,
            'medium_trend': medium_trend,
            'long_trend': long_trend,
            'trend_strength': trend_strength,
            'volatility_level': volatility_level,
            'price_vs_ma': price_vs_ma,
            'support_resistance': support_resistance,
            'volume_ratio': volume_ratio_text
        }
        
    except Exception as e:
        print(f"기술적 지표 분석 중 오류: {e}")
        return {
            'short_trend': 'N/A (분석 오류)',
            'medium_trend': 'N/A (분석 오류)',
            'long_trend': 'N/A (분석 오류)',
            'trend_strength': 'N/A',
            'volatility_level': 'N/A',
            'price_vs_ma': 'N/A',
            'support_resistance': 'N/A',
            'volume_ratio': 'N/A'
        }

def analyze_market_sentiment(stock_info):
    """
    시장 심리와 모멘텀을 분석하는 함수
    """
    try:
        current_price = stock_info.get('current_price', 0)
        change_percent = stock_info.get('change_percent', 0)
        week_52_high = stock_info.get('52_week_high', 0)
        week_52_low = stock_info.get('52_week_low', 0)
        volume = stock_info.get('volume', 0)
        historical_data = stock_info.get('historical_data', [])
        
        # 1. 전반적 모멘텀 분석
        if isinstance(change_percent, (int, float)):
            if change_percent > 3:
                momentum = "매우 강한 상승 모멘텀"
            elif change_percent > 1:
                momentum = "상승 모멘텀"
            elif change_percent > -1:
                momentum = "중립적 모멘텀"
            elif change_percent > -3:
                momentum = "하락 모멘텀"
            else:
                momentum = "강한 하락 모멘텀"
        else:
            momentum = "N/A"
        
        # 2. 52주 기준 가격 위치
        if week_52_high and week_52_low and current_price:
            if week_52_high != week_52_low:
                position_percent = ((current_price - week_52_low) / (week_52_high - week_52_low)) * 100
                
                if position_percent > 90:
                    price_position = f"52주 최고가 근처 ({position_percent:.0f}% 구간)"
                elif position_percent > 70:
                    price_position = f"상위 구간 ({position_percent:.0f}% 구간)"
                elif position_percent > 30:
                    price_position = f"중간 구간 ({position_percent:.0f}% 구간)"
                elif position_percent > 10:
                    price_position = f"하위 구간 ({position_percent:.0f}% 구간)"
                else:
                    price_position = f"52주 최저가 근처 ({position_percent:.0f}% 구간)"
            else:
                price_position = "52주 최고가 = 최저가"
        else:
            price_position = "N/A"
        
        # 3. 거래량 패턴 분석
        if historical_data and len(historical_data) >= 5:
            recent_volumes = [float(data.get('volume', 0)) for data in historical_data[:5]]
            recent_prices = [float(data['close']) for data in historical_data[:5]]
            
            # 거래량과 가격 변화의 상관관계
            price_changes = [recent_prices[i] - recent_prices[i+1] for i in range(len(recent_prices)-1)]
            volume_changes = [recent_volumes[i] - recent_volumes[i+1] for i in range(len(recent_volumes)-1)]
            
            if len(price_changes) > 0 and len(volume_changes) > 0:
                # 상승시 거래량 증가 여부
                up_days = [i for i, pc in enumerate(price_changes) if pc > 0]
                if up_days:
                    up_volume_avg = np.mean([volume_changes[i] for i in up_days])
                    if up_volume_avg > 0:
                        volume_pattern = "상승시 거래량 증가 (건전한 상승)"
                    else:
                        volume_pattern = "상승시 거래량 감소 (약한 상승)"
                else:
                    volume_pattern = "최근 상승일 없음"
            else:
                volume_pattern = "N/A (데이터 부족)"
        else:
            volume_pattern = "N/A (데이터 부족)"
        
        # 4. 변동성 추세 분석
        if historical_data and len(historical_data) >= 20:
            recent_prices = [float(data['close']) for data in historical_data[:10]]
            older_prices = [float(data['close']) for data in historical_data[10:20]]
            
            recent_volatility = np.std(recent_prices) if len(recent_prices) > 1 else 0
            older_volatility = np.std(older_prices) if len(older_prices) > 1 else 0
            
            if older_volatility > 0:
                volatility_change = (recent_volatility - older_volatility) / older_volatility * 100
                
                if volatility_change > 20:
                    volatility_trend = f"변동성 급증 (+{volatility_change:.0f}%)"
                elif volatility_change > 5:
                    volatility_trend = f"변동성 증가 (+{volatility_change:.0f}%)"
                elif volatility_change > -5:
                    volatility_trend = f"변동성 안정 ({volatility_change:+.0f}%)"
                elif volatility_change > -20:
                    volatility_trend = f"변동성 감소 ({volatility_change:.0f}%)"
                else:
                    volatility_trend = f"변동성 급감 ({volatility_change:.0f}%)"
            else:
                volatility_trend = "N/A"
        else:
            volatility_trend = "N/A (데이터 부족)"
        
        return {
            'momentum': momentum,
            'price_position': price_position,
            'volume_pattern': volume_pattern,
            'volatility_trend': volatility_trend
        }
        
    except Exception as e:
        print(f"시장 심리 분석 중 오류: {e}")
        return {
            'momentum': 'N/A (분석 오류)',
            'price_position': 'N/A (분석 오류)', 
            'volume_pattern': 'N/A (분석 오류)',
            'volatility_trend': 'N/A (분석 오류)'
        }

def adjust_analysis_period(stock_info, default_period='1mo'):
    """
    주식의 변동성에 따라 분석 기간을 동적으로 조정하는 함수
    
    변동성 기준:
    - 높은 변동성 (8% 이상): 2개월 주가, 10일 뉴스 → 안정적 분석을 위한 긴 기간
    - 중간 변동성 (4-8%): 1개월 주가, 7일 뉴스 → 표준 분석 기간  
    - 낮은 변동성 (4% 미만): 3개월 주가, 14일 뉴스 → 트렌드 파악을 위한 긴 기간
    """
    try:
        historical_data = stock_info.get('historical_data', [])
        if not historical_data or len(historical_data) < 10:
            print("📊 데이터 부족으로 기본 기간 사용 (1개월 주가, 7일 뉴스)")
            return default_period, 7
        
        # 최근 10일간의 변동성 계산
        recent_prices = [float(data['close']) for data in historical_data[:10]]
        volatility = np.std(recent_prices) / np.mean(recent_prices) * 100
        
        # 변동성에 따른 기간 조정
        if volatility > 8:  # 높은 변동성
            period, news_days = '2mo', 10
            volatility_level = "높음"
            reason = "변동성이 높아 안정적 분석을 위해 긴 기간 적용"
        elif volatility > 4:  # 중간 변동성
            period, news_days = '1mo', 7
            volatility_level = "중간"
            reason = "적정 변동성으로 표준 분석 기간 적용"
        else:  # 낮은 변동성
            period, news_days = '3mo', 14
            volatility_level = "낮음"
            reason = "변동성이 낮아 장기 트렌드 파악을 위해 긴 기간 적용"
        
        print(f"📊 변동성 분석 결과:")
        print(f"   - 변동성 수준: {volatility_level} ({volatility:.2f}%)")
        print(f"   - 선택된 기간: {period} 주가, {news_days}일 뉴스")
        print(f"   - 선택 이유: {reason}")
        
        return period, news_days
            
    except Exception as e:
        print(f"❌ 변동성 분석 중 오류: {e}")
        print("📊 기본 기간 사용 (1개월 주가, 7일 뉴스)")
        return default_period, 7

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
        
        # 1.5. 변동성에 따른 동적 기간 조정
        adjusted_period, adjusted_news_days = adjust_analysis_period(stock_info, period)
        if adjusted_period != period or adjusted_news_days != news_days:
            # 조정된 기간으로 다시 주가 데이터 가져오기
            if adjusted_period != period:
                print("📈 조정된 기간으로 주가 데이터를 다시 수집합니다...")
                stock_data = get_stock_data(company_name, period=adjusted_period)
                stock_info = json.loads(stock_data)
            news_days = adjusted_news_days
            period = adjusted_period
        
        # 2. 뉴스 데이터 가져오기
        print("2. 관련 뉴스 수집 중...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=news_days)
        
        news_data = get_latest_news(
            query=company_name,
            from_date=start_date.strftime('%Y-%m-%d'),
            to_date=end_date.strftime('%Y-%m-%d')
            # num_articles는 기간에 따라 자동 계산됨
        )
        news_info = json.loads(news_data)
        
        # 3. 기술적 지표 및 추세 분석 추가
        technical_analysis = analyze_technical_indicators(stock_info)
        market_sentiment = analyze_market_sentiment(stock_info)
        
        # 4. GPT 프롬프트 구성 (더 상세한 기술적 분석 정보 포함)
        prompt = f"""
다음 정보를 바탕으로 {company_name}에 대한 전문적인 투자보고서를 작성해주세요.

## 주가 현황:
- 현재가: {stock_info.get('current_price', 'N/A')}원
- 전일대비: {stock_info.get('change', 'N/A')}원 ({stock_info.get('change_percent', 'N/A')}%)
- 거래량: {stock_info.get('volume', 'N/A')}주 (평균 대비 {technical_analysis.get('volume_ratio', 'N/A')})
- 고가: {stock_info.get('high', 'N/A')}원
- 저가: {stock_info.get('low', 'N/A')}원
- 시가총액: {stock_info.get('market_cap', 'N/A')}
- PER: {stock_info.get('pe_ratio', 'N/A')}
- 배당수익률: {stock_info.get('dividend_yield', 'N/A')}
- 52주 최고가: {stock_info.get('52_week_high', 'N/A')}원
- 52주 최저가: {stock_info.get('52_week_low', 'N/A')}원

## 기술적 분석 지표:
- 단기 추세 (5일): {technical_analysis.get('short_trend', 'N/A')}
- 중기 추세 (20일): {technical_analysis.get('medium_trend', 'N/A')}
- 장기 추세 (60일): {technical_analysis.get('long_trend', 'N/A')}
- 추세 강도: {technical_analysis.get('trend_strength', 'N/A')}
- 변동성 수준: {technical_analysis.get('volatility_level', 'N/A')}
- 현재가 vs 이동평균: {technical_analysis.get('price_vs_ma', 'N/A')}
- 지지/저항 수준: {technical_analysis.get('support_resistance', 'N/A')}

## 시장 심리 분석:
- 전반적 모멘텀: {market_sentiment.get('momentum', 'N/A')}
- 가격 위치 (52주 기준): {market_sentiment.get('price_position', 'N/A')}
- 거래량 패턴: {market_sentiment.get('volume_pattern', 'N/A')}
- 변동성 추세: {market_sentiment.get('volatility_trend', 'N/A')}

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
2. **기술적 분석** 
   - 제공된 기술적 지표를 바탕으로 추세 방향성과 강도 분석
   - 단기/중기/장기 추세의 일치성 또는 divergence 분석
   - 현재 변동성 수준과 과거 대비 비교
   - 거래량 패턴과 가격 움직임의 상관관계
   - 지지/저항 수준 근처에서의 가격 행동 분석
3. **기본적 분석** (재무지표, PER, 시가총액 등 분석)
4. **시장 심리 및 모멘텀 분석**
   - 현재 시장 심리 상태와 모멘텀 방향
   - 52주 기준 가격 위치의 의미
   - 거래량과 변동성 패턴이 시사하는 바
5. **뉴스 및 시장 동향** (최근 뉴스가 주가에 미치는 영향 분석)
6. **투자 의견** (매수/매도/보유 추천 및 근거)
7. **위험 요소** (투자 시 주의해야 할 리스크 - 특히 상세히 작성)
8. **목표가 및 시나리오 분석** 
   - 기술적 분석을 바탕으로 한 단기 목표가 (1-3개월)
   - 기본적 분석 기반 중장기 목표가 (3-12개월)
   - 상승/하락 시나리오별 예상 주가 범위

**중요한 분석 지침:**
- 제공된 기술적 지표들을 적극 활용하여 차트 패턴과 추세를 구체적으로 분석하세요
- 추세 강도와 변동성 수준을 고려한 동적인 분석을 제공하세요
- 단기/중기/장기 추세 간의 상호작용과 시사점을 분석하세요
- 거래량과 변동성 패턴을 통한 시장 참여자들의 심리 상태를 해석하세요
- 투자 조언은 보수적이고 신중한 관점에서 제공하되, 기술적 신호도 반영하세요
- 위험 요소를 충분히 강조하고 구체적으로 설명하세요
- 목표가는 기술적/기본적 분석을 종합하여 현실적 범위로 설정하세요
- 시장 변동성과 불확실성을 반드시 고려하세요

각 섹션을 상세하고 전문적으로 작성해주세요. 특히 기술적 분석 부분에서는 제공된 지표들을 구체적으로 언급하며 분석하세요.
"""

        # 5. GPT API 호출
        print("4. GPT 분석 중...")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": """당신은 경험이 풍부하고 보수적인 주식 애널리스트입니다. 

주요 분석 능력:
- 기술적 분석: 차트 패턴, 추세선, 이동평균, 거래량 분석
- 기본적 분석: 재무지표, 밸류에이션, 산업 분석
- 시장 심리 분석: 모멘텀, 변동성, 투자자 심리

분석 원칙:
1. 제공된 기술적 지표를 구체적으로 언급하며 분석
2. 단기/중기/장기 추세의 일치성과 divergence 해석
3. 거래량과 가격 움직임의 상관관계 분석
4. 변동성과 시장 심리를 고려한 위험 평가
5. 보수적이고 현실적인 목표가 설정
6. 시나리오별 분석 (상승/하락/횡보)

항상 리스크를 충분히 고려하고, 불확실성을 강조하며, 객관적 데이터에 기반한 분석을 제공합니다."""},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=2500
        )
        
        # 5. 결과 구성
        report = {
            "company_name": company_name,
            "report_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "stock_data": stock_info,
            "technical_analysis": technical_analysis,
            "market_sentiment": market_sentiment,
            "news_count": len(news_info) if news_info else 0,
            "analysis_period": f"{period} (주가), {news_days}일 (뉴스)",
            "investment_report": response.choices[0].message.content,
            "data_sources": {
                "stock_data": "Yahoo Finance",
                "news_data": "NewsAPI",
                "technical_analysis": "Custom Analysis",
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

def generate_multiple_reports_with_pdf(company_names, period='1mo', news_days=None):
    """
    여러 기업의 투자보고서를 한번에 생성하고 각각 PDF로도 저장하는 함수
    
    Parameters:
    - company_names: 회사명 리스트
    - period: 주가 데이터 기간 (변동성에 따라 자동 조정됨)
    - news_days: 뉴스 검색 기간 (None이면 변동성에 따라 자동 결정)
    
    Returns:
    - 각 기업의 생성된 파일 정보를 포함한 딕셔너리
    """
    results = {}
    successful_reports = []
    failed_reports = []
    
    for company_name in company_names:
        print(f"\n{'='*50}")
        print(f"{company_name} 처리 중...")
        
        try:
            if news_days is None:
                result = generate_investment_report_with_pdf(company_name, period)
            else:
                result = generate_investment_report_with_pdf(company_name, period, news_days)
            results[company_name] = result
            
            if 'error' not in result:
                successful_reports.append(company_name)
                print(f"✅ {company_name} 보고서 생성 완료")
            else:
                failed_reports.append(company_name)
                print(f"❌ {company_name} 보고서 생성 실패: {result['error']}")
                
        except Exception as e:
            error_result = {"error": f"처리 중 오류 발생: {str(e)}"}
            results[company_name] = error_result
            failed_reports.append(company_name)
            print(f"❌ {company_name} 처리 중 오류: {str(e)}")
    
    # 종합 결과 출력
    print(f"\n{'='*60}")
    print("📊 전체 처리 결과:")
    print(f"✅ 성공: {len(successful_reports)}개 기업")
    print(f"❌ 실패: {len(failed_reports)}개 기업")
    
    if successful_reports:
        print(f"\n성공한 기업: {', '.join(successful_reports)}")
    if failed_reports:
        print(f"\n실패한 기업: {', '.join(failed_reports)}")
    
    return results

def generate_investment_report_with_pdf(company_name, period='1mo', news_days=None, save_pdf=True):
    """
    주가 정보와 뉴스 정보를 기반으로 투자보고서를 생성하고 PDF로도 저장하는 함수
    
    Parameters:
    - company_name: 회사명 (예: '삼성전자')
    - period: 주가 데이터 기간 (기본값: '1mo', 변동성에 따라 자동 조정됨)
    - news_days: 뉴스 검색 기간 (None이면 변동성에 따라 자동 결정)
    - save_pdf: PDF 파일 생성 여부 (기본값: True)
    
    Returns:
    - 생성된 파일 경로들을 포함한 딕셔너리
    """
    try:
        print(f"=== {company_name} 투자보고서 생성 중 ===")
        
        # 1. 투자보고서 생성 (news_days가 None이면 변동성 기반 자동 결정)
        if news_days is None:
            report_json = generate_investment_report(company_name, period)
        else:
            report_json = generate_investment_report(company_name, period, news_days)
        report_data = json.loads(report_json)
        
        if 'error' in report_data:
            return {"error": f"투자보고서 생성 실패: {report_data['error']}"}
        
        # 2. JSON 파일 저장
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_filename = f"reports/{company_name}_report_{timestamp}.json"
        
        # reports 디렉토리가 없으면 생성
        os.makedirs('reports', exist_ok=True)
        
        with open(json_filename, 'w', encoding='utf-8') as f:
            f.write(report_json)
        
        result = {
            "company_name": company_name,
            "json_file": json_filename,
            "pdf_file": None,
            "status": "success"
        }
        
        # 3. PDF 파일 생성
        if save_pdf:
            print("5. PDF 보고서 생성 중...")
            pdf_filename = f"reports/{company_name}_report_{timestamp}.pdf"
            
            try:
                pdf_path = generate_pdf_report_from_data(report_data, pdf_filename)
                if pdf_path:
                    result["pdf_file"] = pdf_filename
                    print(f"PDF 보고서 생성 완료: {pdf_filename}")
                else:
                    print("PDF 생성에 실패했지만 JSON 보고서는 정상적으로 생성되었습니다.")
            except Exception as e:
                print(f"PDF 생성 중 오류 발생: {e}")
                print("JSON 보고서는 정상적으로 생성되었습니다.")
        
        print("투자보고서 생성 완료!")
        return result
        
    except Exception as e:
        print(f"투자보고서 생성 중 오류 발생: {str(e)}")
        return {"error": f"투자보고서 생성 실패: {str(e)}"}

def convert_existing_report_to_pdf(json_file_path):
    """
    기존 JSON 보고서를 PDF로 변환하는 함수
    
    Parameters:
    - json_file_path: JSON 보고서 파일 경로
    
    Returns:
    - PDF 파일 경로 또는 None
    """
    try:
        if not os.path.exists(json_file_path):
            print(f"파일을 찾을 수 없습니다: {json_file_path}")
            return None
        
        # JSON 파일 읽기
        with open(json_file_path, 'r', encoding='utf-8') as f:
            report_data = json.load(f)
        
        # PDF 파일명 생성
        base_name = os.path.splitext(json_file_path)[0]
        pdf_path = f"{base_name}.pdf"
        
        # PDF 생성
        result = generate_pdf_report_from_data(report_data, pdf_path)
        return result
        
    except Exception as e:
        print(f"PDF 변환 중 오류 발생: {e}")
        return None

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
