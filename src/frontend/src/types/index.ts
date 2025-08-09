// 계좌 정보 타입
export interface Account {
  id: string
  accountNumber: string
  accountName: string
  balance: number
  accountType: '입출금' | '예금' | '적금' | '대출'
  bankCode: string
  bankName: string
  isActive: boolean
  createdAt: Date
  updatedAt: Date
}

// 카드 정보 타입
export interface Card {
  id: string
  cardNumber: string
  cardName: string
  cardType: '체크카드' | '신용카드' | '기프트카드'
  cardCompany: string
  limit: number
  usedAmount: number
  availableAmount: number
  expiryDate: string
  isActive: boolean
  createdAt: Date
}

// 거래 내역 타입
export interface Transaction {
  id: string
  accountId: string
  type: '입금' | '출금' | '이체' | '결제'
  amount: number
  balance: number
  description: string
  category: string
  counterparty: string
  transactionDate: Date
  createdAt: Date
}

// 사용자 정보 타입
export interface User {
  id: string
  name: string
  email: string
  phoneNumber: string
  customerNumber: string
  isActive: boolean
  createdAt: Date
  updatedAt: Date
}

// 대출 정보 타입
export interface Loan {
  id: string
  loanNumber: string
  loanType: '담보대출' | '신용대출' | '전세대출' | '주택담보대출'
  principal: number
  remainingPrincipal: number
  interestRate: number
  monthlyPayment: number
  startDate: Date
  endDate: Date
  isActive: boolean
  createdAt: Date
}

// 알림 타입
export interface Notification {
  id: string
  userId: string
  type: '거래' | '대출' | '카드' | '시스템'
  title: string
  message: string
  isRead: boolean
  createdAt: Date
}

// 메뉴 아이템 타입
export interface MenuItem {
  id: string
  name: string
  icon: string
  path: string
  description: string
  isActive: boolean
}

// AI 투자 보고서 관련 타입
export interface Company {
  name: string
  ticker: string
}

export interface ReportSummary {
  current_price: string
  change: string
  change_percent: number
  analysis_period: string
  news_count: number
}

export interface ReportResult {
  success: boolean
  message: string
  company_name: string
  json_file: string
  pdf_file?: string
  summary?: ReportSummary
  timestamp: string
} 