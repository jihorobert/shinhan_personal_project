#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
투자보고서 생성 API 서버
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
from datetime import datetime
import traceback

from analysis.analyze import generate_investment_report_with_pdf

app = Flask(__name__)
CORS(app)  # Next.js 프론트엔드와의 CORS 문제 해결

@app.route('/api/health', methods=['GET'])
def health_check():
    """서버 상태 확인"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    """투자보고서 생성 API"""
    try:
        # 요청 데이터 파싱
        data = request.get_json()
        
        if not data or 'company_name' not in data:
            return jsonify({
                'error': '기업명이 필요합니다.',
                'message': 'company_name 필드가 누락되었습니다.'
            }), 400
        
        company_name = data['company_name'].strip()
        
        if not company_name:
            return jsonify({
                'error': '유효한 기업명을 입력해주세요.',
                'message': '기업명이 비어있습니다.'
            }), 400
        
        print(f"📊 {company_name} 투자보고서 생성 시작...")
        
        # 투자보고서 생성
        result = generate_investment_report_with_pdf(company_name)
        
        if 'error' in result:
            return jsonify({
                'error': result['error'],
                'message': f'{company_name}에 대한 투자보고서 생성에 실패했습니다.'
            }), 500
        
        # 성공적으로 생성된 경우
        response_data = {
            'success': True,
            'message': f'{company_name} 투자보고서가 성공적으로 생성되었습니다.',
            'company_name': company_name,
            'json_file': result['json_file'],
            'pdf_file': result.get('pdf_file'),
            'timestamp': datetime.now().isoformat()
        }
        
        # JSON 파일에서 요약 정보 추출
        try:
            with open(result['json_file'], 'r', encoding='utf-8') as f:
                report_data = json.load(f)
            
            response_data['summary'] = {
                'current_price': report_data.get('stock_data', {}).get('current_price', 'N/A'),
                'change': report_data.get('stock_data', {}).get('change', 'N/A'),
                'change_percent': report_data.get('stock_data', {}).get('change_percent', 'N/A'),
                'analysis_period': report_data.get('analysis_period', 'N/A'),
                'news_count': report_data.get('news_count', 0)
            }
        except Exception as e:
            print(f"요약 정보 추출 중 오류: {e}")
            response_data['summary'] = None
        
        print(f"✅ {company_name} 투자보고서 생성 완료")
        return jsonify(response_data)
        
    except Exception as e:
        error_message = str(e)
        print(f"❌ 투자보고서 생성 중 오류 발생: {error_message}")
        print(traceback.format_exc())
        
        return jsonify({
            'error': error_message,
            'message': '투자보고서 생성 중 예상치 못한 오류가 발생했습니다.',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/download-pdf/<path:filename>', methods=['GET'])
def download_pdf(filename):
    """PDF 파일 다운로드"""
    try:
        # 보안을 위해 파일명 검증
        if not filename.endswith('.pdf'):
            return jsonify({'error': '유효하지 않은 파일 형식입니다.'}), 400
        
        file_path = os.path.join('reports', filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': '파일을 찾을 수 없습니다.'}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        print(f"PDF 다운로드 중 오류: {e}")
        return jsonify({'error': 'PDF 다운로드 중 오류가 발생했습니다.'}), 500

@app.route('/api/supported-companies', methods=['GET'])
def get_supported_companies():
    """지원되는 기업 목록 반환"""
    try:
        from fetch.stock_fetcher import KOREAN_COMPANIES
        
        companies = []
        for name, ticker in KOREAN_COMPANIES.items():
            companies.append({
                'name': name,
                'ticker': ticker
            })
        
        return jsonify({
            'companies': companies,
            'count': len(companies)
        })
        
    except Exception as e:
        print(f"지원 기업 목록 조회 중 오류: {e}")
        return jsonify({
            'error': '지원 기업 목록을 가져오는 중 오류가 발생했습니다.',
            'companies': [],
            'count': 0
        }), 500

if __name__ == '__main__':
    print("🚀 투자보고서 생성 API 서버 시작")
    print("📍 서버 주소: http://localhost:5001")
    print("📋 API 엔드포인트:")
    print("   - GET  /api/health              : 서버 상태 확인")
    print("   - GET  /api/supported-companies : 지원 기업 목록")
    print("   - POST /api/generate-report     : 투자보고서 생성")
    print("   - GET  /api/download-pdf/<file> : PDF 다운로드")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5001)