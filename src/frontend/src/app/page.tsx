import Link from 'next/link'
import { 
  BanknotesIcon, 
  CreditCardIcon, 
  ChartBarIcon, 
  UserIcon,
  ArrowRightIcon,
  SparklesIcon
} from '@heroicons/react/24/outline'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* 헤더 */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-2xl font-bold text-blue-600">신한은행</h1>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button className="text-gray-500 hover:text-gray-700">
                <UserIcon className="h-6 w-6" />
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* 메인 컨텐츠 */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 환영 메시지 */}
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            안녕하세요, 고객님
          </h2>
          <p className="text-lg text-gray-600">
            신한은행 모킹앱에 오신 것을 환영합니다
          </p>
        </div>

        {/* AI 투자 보고서 생성 기능 - 특별 섹션 */}
        <div className="mb-12">
          <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl shadow-lg p-6 text-white">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="bg-white/20 rounded-full p-3">
                  <SparklesIcon className="h-8 w-8 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-bold mb-2">AI 투자 보고서 생성</h3>
                  <p className="text-purple-100">
                    AI가 분석한 맞춤형 투자 보고서를 받아보세요
                  </p>
                </div>
              </div>
              <Link href="/ai-investment-report" className="group">
                <button className="bg-white text-purple-600 px-6 py-3 rounded-lg font-semibold hover:bg-purple-50 transition-colors duration-200 flex items-center space-x-2">
                  <span>시작하기</span>
                  <ArrowRightIcon className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
                </button>
              </Link>
            </div>
          </div>
        </div>

        {/* 메뉴 그리드 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <Link href="/accounts" className="group">
            <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow duration-200">
              <div className="flex items-center justify-between">
                <div>
                  <BanknotesIcon className="h-8 w-8 text-blue-600 mb-3" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">계좌조회</h3>
                  <p className="text-sm text-gray-600">내 계좌 정보와 잔액 확인</p>
                </div>
                <ArrowRightIcon className="h-5 w-5 text-gray-400 group-hover:text-blue-600 transition-colors" />
              </div>
            </div>
          </Link>

          <Link href="/cards" className="group">
            <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow duration-200">
              <div className="flex items-center justify-between">
                <div>
                  <CreditCardIcon className="h-8 w-8 text-green-600 mb-3" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">카드관리</h3>
                  <p className="text-sm text-gray-600">카드 정보와 사용 내역</p>
                </div>
                <ArrowRightIcon className="h-5 w-5 text-gray-400 group-hover:text-green-600 transition-colors" />
              </div>
            </div>
          </Link>

          <Link href="/transactions" className="group">
            <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow duration-200">
              <div className="flex items-center justify-between">
                <div>
                  <ChartBarIcon className="h-8 w-8 text-purple-600 mb-3" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">거래내역</h3>
                  <p className="text-sm text-gray-600">입출금 및 이체 내역</p>
                </div>
                <ArrowRightIcon className="h-5 w-5 text-gray-400 group-hover:text-purple-600 transition-colors" />
              </div>
            </div>
          </Link>

          <Link href="/profile" className="group">
            <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow duration-200">
              <div className="flex items-center justify-between">
                <div>
                  <UserIcon className="h-8 w-8 text-orange-600 mb-3" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">내정보</h3>
                  <p className="text-sm text-gray-600">개인정보 및 설정</p>
                </div>
                <ArrowRightIcon className="h-5 w-5 text-gray-400 group-hover:text-orange-600 transition-colors" />
              </div>
            </div>
          </Link>
        </div>

        {/* 빠른 액션 */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">빠른 액션</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
              이체하기
            </button>
            <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors">
              예금하기
            </button>
            <button className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors">
              대출신청
            </button>
          </div>
        </div>
      </main>
    </div>
  )
}
