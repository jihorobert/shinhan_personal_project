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
from report.pdf_generator import generate_pdf_report_from_data

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
            to_date=end_date.strftime('%Y-%m-%d')
            # num_articles는 기간에 따라 자동 계산됨
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
6. **위험 요소** (투자 시 주의해야 할 리스크 - 특히 상세히 작성)
7. **목표가** (향후 3-6개월 예상 주가 범위 - 현실적이고 보수적으로 설정)

**중요한 분석 지침:**
- 투자 조언은 보수적이고 신중한 관점에서 제공하세요
- 위험 요소를 충분히 강조하고 구체적으로 설명하세요
- 목표가는 과도하게 낙관적이지 않도록 현실적 범위로 설정하세요
- 불확실성과 시장 변동성을 반드시 고려하세요
- 긍정적 요인과 부정적 요인을 균형있게 분석하세요
- 단기적 변동성과 장기적 불확실성을 모두 언급하세요

각 섹션을 상세하고 전문적으로 작성해주세요. 투자 조언은 객관적 데이터에 기반하되, 보수적 관점을 유지해주세요.
"""

        # 4. GPT API 호출
        print("3. GPT 분석 중...")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "당신은 경험이 풍부하고 보수적인 주식 애널리스트입니다. 주어진 데이터를 바탕으로 객관적이고 신중한 투자보고서를 작성합니다. 리스크를 충분히 고려하고, 과도한 낙관론을 피하며, 현실적이고 보수적인 관점에서 분석합니다. 불확실성과 잠재적 위험요소를 항상 강조합니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
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

def generate_multiple_reports_with_pdf(company_names, period='1mo', news_days=7):
    """
    여러 기업의 투자보고서를 한번에 생성하고 각각 PDF로도 저장하는 함수
    
    Parameters:
    - company_names: 회사명 리스트
    - period: 주가 데이터 기간
    - news_days: 뉴스 검색 기간
    
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

def generate_investment_report_with_pdf(company_name, period='1mo', news_days=7, save_pdf=True):
    """
    주가 정보와 뉴스 정보를 기반으로 투자보고서를 생성하고 PDF로도 저장하는 함수
    
    Parameters:
    - company_name: 회사명 (예: '삼성전자')
    - period: 주가 데이터 기간 (기본값: '1mo')
    - news_days: 뉴스 검색 기간 (기본값: 7일)
    - save_pdf: PDF 파일 생성 여부 (기본값: True)
    
    Returns:
    - 생성된 파일 경로들을 포함한 딕셔너리
    """
    try:
        print(f"=== {company_name} 투자보고서 생성 중 ===")
        
        # 1. 투자보고서 생성
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
