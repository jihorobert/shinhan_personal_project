#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
기존 JSON 보고서를 PDF로 변환하는 스크립트
"""

import os
import sys
import json
from datetime import datetime

# 프로젝트 루트 경로 추가
sys.path.append('src')

from analysis.analyze import convert_existing_report_to_pdf

def main():
    """메인 함수"""
    print("=== JSON 보고서를 PDF로 변환 ===")
    
    # reports 디렉토리의 JSON 파일들 확인
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        print(f"{reports_dir} 디렉토리가 존재하지 않습니다.")
        return
    
    # JSON 파일 목록 가져오기
    json_files = [f for f in os.listdir(reports_dir) if f.endswith('.json')]
    
    if not json_files:
        print(f"{reports_dir} 디렉토리에 JSON 보고서 파일이 없습니다.")
        return
    
    print(f"\n발견된 JSON 보고서 파일들:")
    for i, filename in enumerate(json_files, 1):
        print(f"{i}. {filename}")
    
    # 사용자 선택
    try:
        choice = input(f"\n변환할 파일을 선택하세요 (1-{len(json_files)}) 또는 'all'을 입력하여 모든 파일 변환: ").strip()
        
        if choice.lower() == 'all':
            # 모든 파일 변환
            print("\n모든 JSON 보고서를 PDF로 변환 중...")
            success_count = 0
            
            for filename in json_files:
                json_path = os.path.join(reports_dir, filename)
                print(f"\n변환 중: {filename}")
                
                pdf_path = convert_existing_report_to_pdf(json_path)
                if pdf_path:
                    print(f"✅ 변환 완료: {os.path.basename(pdf_path)}")
                    success_count += 1
                else:
                    print(f"❌ 변환 실패: {filename}")
            
            print(f"\n변환 완료: {success_count}/{len(json_files)}개 파일")
            
        else:
            # 특정 파일 변환
            file_index = int(choice) - 1
            if 0 <= file_index < len(json_files):
                selected_file = json_files[file_index]
                json_path = os.path.join(reports_dir, selected_file)
                
                print(f"\n선택된 파일: {selected_file}")
                print("PDF로 변환 중...")
                
                pdf_path = convert_existing_report_to_pdf(json_path)
                if pdf_path:
                    print(f"✅ 변환 완료: {os.path.basename(pdf_path)}")
                else:
                    print("❌ 변환 실패")
            else:
                print("잘못된 선택입니다.")
                
    except ValueError:
        print("잘못된 입력입니다.")
    except KeyboardInterrupt:
        print("\n변환이 취소되었습니다.")

if __name__ == "__main__":
    main()