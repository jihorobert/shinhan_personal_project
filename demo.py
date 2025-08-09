#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
투자보고서 시스템 간단 데모

API 키 설정 없이도 모듈들이 정상적으로 로드되는지 확인하는 데모입니다.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """모든 모듈이 정상적으로 임포트되는지 테스트"""
    print("=== 모듈 임포트 테스트 ===")
    
    try:
        from fetch.stock_fetcher import get_stock_data, get_multiple_stocks_data, KOREAN_COMPANIES
        print("✅ stock_fetcher 모듈 임포트 성공")
        print(f"   지원 기업 수: {len(KOREAN_COMPANIES)}개")
    except ImportError as e:
        print(f"❌ stock_fetcher 모듈 임포트 실패: {e}")
        return False
    
    try:
        from fetch.news_fetcher import get_latest_news
        print("✅ news_fetcher 모듈 임포트 성공")
    except ImportError as e:
        print(f"❌ news_fetcher 모듈 임포트 실패: {e}")
        return False
    
    try:
        from analysis.analyze import generate_investment_report, generate_multiple_reports
        print("✅ analyze 모듈 임포트 성공")
    except ImportError as e:
        print(f"❌ analyze 모듈 임포트 실패: {e}")
        return False
    
    return True

def show_supported_companies():
    """지원되는 기업 목록 출력"""
    from fetch.stock_fetcher import KOREAN_COMPANIES
    
    print("\n=== 지원 기업 목록 ===")
    for i, (name, ticker) in enumerate(KOREAN_COMPANIES.items(), 1):
        print(f"{i:2d}. {name:15s} ({ticker})")

def show_usage_example():
    """사용법 예제 출력"""
    print("\n=== 사용법 예제 ===")
    print("1. 환경변수 설정 (.env 파일):")
    print("   GPT_KEY=your_openai_api_key")
    print("   NEWSAPI_KEY=your_newsapi_key")
    print()
    print("2. 단일 기업 분석:")
    print("   python -c \"from src.analysis.analyze import generate_investment_report; print(generate_investment_report('삼성전자'))\"")
    print()
    print("3. 대화형 실행:")
    print("   python example_usage.py")
    print()
    print("4. 개별 모듈 테스트:")
    print("   cd src/fetch && python stock_fetcher.py")
    print("   cd src/fetch && python news_fetcher.py")
    print("   cd src/analysis && python analyze.py")

def main():
    print("🚀 신한 개인프로젝트: AI 투자보고서 생성 시스템 데모")
    print("=" * 60)
    
    # 모듈 임포트 테스트
    if not test_imports():
        print("\n❌ 모듈 임포트에 실패했습니다. requirements.txt를 확인하고 의존성을 설치해주세요:")
        print("   pip install -r requirements.txt")
        return
    
    # 지원 기업 목록 출력
    show_supported_companies()
    
    # 사용법 예제 출력
    show_usage_example()
    
    print("\n" + "=" * 60)
    print("✅ 시스템이 정상적으로 설정되었습니다!")
    print("📝 실제 투자보고서를 생성하려면 .env 파일에 API 키를 설정하고 example_usage.py를 실행하세요.")

if __name__ == "__main__":
    main()