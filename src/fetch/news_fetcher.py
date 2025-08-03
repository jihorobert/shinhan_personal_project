from newsapi import NewsApiClient
import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

# 스크래핑 해온 뉴스 기사를 가져오는 함수
# query: 검색어, from_date: 시작 날짜,
# to_date: 종료 날짜, num_articles: 가져올 기사 수
# 각 기사의 title과 description을 포함한 리스트를 반환
def get_latest_news(query, from_date, to_date, num_articles=5):
    url = (
        f'https://newsapi.org/v2/everything'
        f'?q={query}'
        f'&from={from_date}'  
        f'&to={to_date}'      
        f'&language=ko'       
        f'&sortBy=publishedAt'
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
    
    result_list = json.dumps(result_list, ensure_ascii=False, indent=2)
    return result_list
        
# Example usage
# print(get_latest_news('삼성', '2025-07-27', '2025-08-02'))
