from newsapi import NewsApiClient
import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

# 스크래핑 해온 뉴스 기사를 가져오는 함수
# query: 검색어, from_date: 시작 날짜,
# to_date: 종료 날짜, num_articles: 가져올 기사 수 (None이면 기간에 따라 자동 계산)
# 각 기사의 title과 description을 포함한 리스트를 반환
def get_latest_news(query, from_date, to_date, num_articles=None):
    # 날짜 차이를 계산하여 뉴스 수를 동적으로 결정
    if num_articles is None:
        from datetime import datetime
        start_date = datetime.strptime(from_date, '%Y-%m-%d')
        end_date = datetime.strptime(to_date, '%Y-%m-%d')
        date_diff = (end_date - start_date).days
        
        # 기간에 따른 뉴스 수 계산 (일주일당 5개 기준, 최소 5개, 최대 50개)
        base_articles_per_week = 5
        num_articles = max(5, min(50, int((date_diff / 7) * base_articles_per_week)))
        
        print(f"분석 기간: {date_diff}일, 계산된 뉴스 수: {num_articles}개")
    
    url = (
        f'https://newsapi.org/v2/everything'
        f'?q={query}'
        f'&from={from_date}'  
        f'&to={to_date}'      
        f'&language=ko'       
        # f'&sortBy=publishedAt'
        f'&sortBy=relevancy'
        # f'&sortBy=popularity'
        f'&apiKey={NEWSAPI_KEY}'
    )
    response = requests.get(url)
    print(f"Fetching news for query: {query} from {from_date} to {to_date}")
    print(f"response: {response}")
    if response.status_code == 200:
        articles = response.json().get('articles', [])[:num_articles]
        result_list = [{'title': article['title'], 
                        'description': article['description'],}
                        for article in articles]
    else:
        print(f"Error fetching news: {response.status_code}")
        result_list = []
    
    # 실제 가져온 뉴스 수를 출력
    actual_news_count = len(result_list)
    print(f"실제 가져온 뉴스 수: {actual_news_count}개")
    
    result_list = json.dumps(result_list, ensure_ascii=False, indent=2)
    return result_list
        
# Example usage
if __name__ == "__main__":
    company_name = input("회사명을 입력하세요: ")
    print(get_latest_news(company_name, '2025-07-27', '2025-08-02'))