# PDF 투자보고서 생성 가이드

이 프로젝트에 PDF 보고서 생성 기능이 추가되었습니다. 이제 투자보고서를 JSON과 PDF 형식으로 생성할 수 있습니다.

## 🚀 새로운 기능

### 1. PDF 보고서 생성 모듈
- `src/report/pdf_generator.py`: PDF 생성 전용 모듈
- 한글 폰트 지원 (macOS 환경)
- 표, 차트, 서식이 포함된 전문적인 PDF 보고서

### 2. 통합된 보고서 생성
- JSON과 PDF 형식 동시 생성
- 기존 JSON 보고서를 PDF로 변환
- 주가 데이터 테이블과 분석 내용 포함

## 📋 사용 방법

### 새로운 보고서 생성 (JSON + PDF)

```bash
# 가상환경 활성화
source venv/bin/activate

# 새로운 보고서 생성 (JSON + PDF)
python demo_with_pdf.py
```

### 기존 JSON 보고서를 PDF로 변환

```bash
# 가상환경 활성화
source venv/bin/activate

# 변환 스크립트 실행
python convert_to_pdf.py

# 옵션 선택:
# - 특정 파일 선택 (1, 2, ...)
# - 모든 파일 변환 ('all' 입력)
```

## 📁 파일 구조

```
reports/
├── 삼성전자_report_20250809_154059.json    # 기존 JSON 보고서
├── 삼성전자_report_20250809_154059.pdf     # 변환된 PDF 보고서
├── SK하이닉스_report_20250809_170320.json  # 기존 JSON 보고서
├── SK하이닉스_report_20250809_170320.pdf   # 변환된 PDF 보고서
└── LG전자_report_20250809_172445.json      # 새로 생성된 JSON 보고서
└── LG전자_report_20250809_172445.pdf       # 새로 생성된 PDF 보고서
```

## 📊 PDF 보고서 내용

생성되는 PDF 보고서에는 다음 내용이 포함됩니다:

1. **보고서 제목 및 기본 정보**
   - 회사명, 생성일시, 분석 기간
   - 데이터 출처 정보

2. **주가 현황 테이블**
   - 현재가, 전일대비 변화
   - 거래량, 고가, 저가
   - 시가총액, PER, 배당수익률
   - 52주 최고가/최저가

3. **투자분석 리포트**
   - GPT-4가 생성한 전문적인 투자 분석
   - 종목 개요, 기술적 분석, 기본적 분석
   - 뉴스 분석, 투자 의견, 위험 요소, 목표가

4. **서식 및 디자인**
   - 한글 폰트 지원
   - 표와 구분선을 통한 깔끔한 레이아웃
   - 전문적인 보고서 형태

## ⚙️ 설치된 패키지

```
reportlab==4.0.9     # PDF 생성 라이브러리
matplotlib==3.8.2    # 차트 생성 (향후 활용)
```

## 🔧 주요 함수

### PDF 생성 관련 함수

```python
# 새로운 보고서 생성 (JSON + PDF)
from src.analysis.analyze import generate_investment_report_with_pdf

result = generate_investment_report_with_pdf("삼성전자", save_pdf=True)

# 기존 JSON을 PDF로 변환
from src.analysis.analyze import convert_existing_report_to_pdf

pdf_path = convert_existing_report_to_pdf("reports/삼성전자_report.json")
```

## 📝 참고사항

- macOS 환경에서 한글 폰트가 자동으로 감지됩니다
- 주가 차트 기능은 현재 비활성화되어 있습니다 (향후 개선 예정)
- PDF 생성에 실패해도 JSON 보고서는 정상적으로 생성됩니다
- 모든 생성된 파일은 `reports/` 디렉토리에 저장됩니다

## 🎯 다음 단계

1. 주가 차트 기능 개선
2. 더 다양한 시각화 요소 추가
3. 템플릿 커스터마이징 기능
4. Windows/Linux 환경 한글 폰트 지원 개선

---

이제 투자보고서를 PDF 형식으로도 생성할 수 있어 더욱 전문적인 보고서를 만들 수 있습니다! 🚀