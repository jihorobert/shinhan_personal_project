# 신한은행 모킹앱

신한은행 모킹앱은 Next.js와 TypeScript를 사용하여 개발된 은행 서비스 체험 애플리케이션입니다.

## 🚀 주요 기능

- **계좌조회**: 계좌 정보와 잔액 확인
- **카드관리**: 카드 정보와 사용 내역
- **거래내역**: 입출금 및 이체 내역 조회
- **내정보**: 개인정보 및 설정 관리

## 🛠 기술 스택

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Heroicons
- **Package Manager**: npm

## 📦 설치 및 실행

### 필수 요구사항
- Node.js 18.0.0 이상
- npm 9.0.0 이상

### 설치
```bash
# 의존성 설치
npm install
```

### 개발 서버 실행
```bash
# 개발 서버 시작
npm run dev
```

브라우저에서 [http://localhost:3000](http://localhost:3000)을 열어 애플리케이션을 확인하세요.

### 빌드
```bash
# 프로덕션 빌드
npm run build

# 프로덕션 서버 실행
npm start
```

## 📁 프로젝트 구조

```
src/
├── app/                 # Next.js App Router
│   ├── layout.tsx      # 루트 레이아웃
│   ├── page.tsx        # 메인 페이지
│   └── globals.css     # 전역 스타일
├── components/         # 재사용 가능한 컴포넌트
├── lib/               # 유틸리티 함수
│   └── utils.ts       # 공통 유틸리티
├── types/             # TypeScript 타입 정의
│   └── index.ts       # 타입 인터페이스
└── data/              # 모킹 데이터
```

## 🎨 디자인 시스템

### 색상 팔레트
- **Primary Blue**: 신한은행 브랜드 블루 (#0ea5e9)
- **Secondary Green**: 신한은행 그린 (#22c55e)
- **Neutral Gray**: 중성 그레이 (#6b7280)

### 컴포넌트
- 반응형 디자인
- 접근성 고려
- 모던한 UI/UX

## 🔧 개발 가이드

### 새로운 페이지 추가
1. `src/app/` 디렉토리에 새 폴더 생성
2. `page.tsx` 파일 생성
3. 라우팅 자동 설정

### 컴포넌트 추가
1. `src/components/` 디렉토리에 컴포넌트 생성
2. TypeScript 인터페이스 정의
3. Tailwind CSS로 스타일링

### 유틸리티 함수 추가
1. `src/lib/utils.ts`에 함수 추가
2. 타입 안전성 보장
3. 재사용 가능하도록 설계

## 📝 라이센스

이 프로젝트는 교육 및 포트폴리오 목적으로 제작되었습니다.

## 🤝 기여

프로젝트 개선을 위한 제안이나 버그 리포트는 언제든 환영합니다.

---

**신한은행 모킹앱** - 은행 서비스 체험을 위한 모던 웹 애플리케이션
