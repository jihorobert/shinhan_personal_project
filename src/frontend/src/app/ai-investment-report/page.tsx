'use client'

import { useState } from 'react'
import Link from 'next/link'
import { 
  ArrowLeftIcon,
  SparklesIcon,
  ChartBarIcon,
  ClockIcon,
  DocumentTextIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline'

interface FormData {
  investmentAmount: string
  riskTolerance: string
  investmentPeriod: string
  investmentGoal: string
  preferredSectors: string[]
}

export default function AIInvestmentReport() {
  const [isGenerating, setIsGenerating] = useState(false)
  const [reportGenerated, setReportGenerated] = useState(false)
  const [formData, setFormData] = useState<FormData>({
    investmentAmount: '',
    riskTolerance: '보통',
    investmentPeriod: '1년',
    investmentGoal: '자산증식',
    preferredSectors: []
  })

  const riskOptions = ['보수적', '보통', '적극적']
  const periodOptions = ['6개월', '1년', '3년', '5년']
  const goalOptions = ['자산증식', '수익안정', '자유자재', '은퇴준비']
  const sectorOptions = ['IT/기술', '헬스케어', '금융', '에너지', '소비재', '부동산']

  const handleGenerateReport = async () => {
    setIsGenerating(true)
    
    // AI 보고서 생성 시뮬레이션 (3초 대기)
    setTimeout(() => {
      setIsGenerating(false)
      setReportGenerated(true)
    }, 3000)
  }

  const handleSectorToggle = (sector: string) => {
    setFormData((prev: FormData) => ({
      ...prev,
      preferredSectors: prev.preferredSectors.includes(sector)
        ? prev.preferredSectors.filter(s => s !== sector)
        : [...prev.preferredSectors, sector]
    }))
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
      {/* 헤더 */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <Link href="/" className="text-gray-500 hover:text-gray-700">
                <ArrowLeftIcon className="h-6 w-6" />
              </Link>
              <h1 className="text-xl font-semibold text-gray-900">AI 투자 보고서 생성</h1>
            </div>
            <div className="flex items-center space-x-2">
              <SparklesIcon className="h-6 w-6 text-purple-600" />
              <span className="text-sm text-purple-600 font-medium">AI 분석</span>
            </div>
          </div>
        </div>
      </header>

      {/* 메인 컨텐츠 */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {!reportGenerated ? (
          <div className="space-y-8">
            {/* 소개 섹션 */}
            <div className="text-center">
              <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <SparklesIcon className="h-8 w-8 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                AI 투자 보고서 생성
              </h2>
              <p className="text-gray-600">
                투자 성향과 목표를 입력하시면 AI가 맞춤형 투자 전략을 제안해드립니다
              </p>
            </div>

            {/* 입력 폼 */}
            <div className="bg-white rounded-lg shadow-md p-6 space-y-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">투자 정보 입력</h3>
              
              {/* 투자 금액 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  투자 예정 금액
                </label>
                <input
                  type="number"
                  placeholder="예: 10000000"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  value={formData.investmentAmount}
                  onChange={(e) => setFormData((prev: FormData) => ({ ...prev, investmentAmount: e.target.value }))}
                />
              </div>

              {/* 위험 성향 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  위험 성향
                </label>
                <div className="grid grid-cols-3 gap-3">
                  {riskOptions.map((risk) => (
                    <button
                      key={risk}
                      onClick={() => setFormData((prev: FormData) => ({ ...prev, riskTolerance: risk }))}
                      className={`px-4 py-2 rounded-lg border transition-colors ${
                        formData.riskTolerance === risk
                          ? 'bg-purple-600 text-white border-purple-600'
                          : 'bg-white text-gray-700 border-gray-300 hover:border-purple-300'
                      }`}
                    >
                      {risk}
                    </button>
                  ))}
                </div>
              </div>

              {/* 투자 기간 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  투자 기간
                </label>
                <div className="grid grid-cols-4 gap-3">
                  {periodOptions.map((period) => (
                    <button
                      key={period}
                      onClick={() => setFormData((prev: FormData) => ({ ...prev, investmentPeriod: period }))}
                      className={`px-3 py-2 rounded-lg border transition-colors ${
                        formData.investmentPeriod === period
                          ? 'bg-purple-600 text-white border-purple-600'
                          : 'bg-white text-gray-700 border-gray-300 hover:border-purple-300'
                      }`}
                    >
                      {period}
                    </button>
                  ))}
                </div>
              </div>

              {/* 투자 목표 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  투자 목표
                </label>
                <div className="grid grid-cols-2 gap-3">
                  {goalOptions.map((goal) => (
                    <button
                      key={goal}
                      onClick={() => setFormData((prev: FormData) => ({ ...prev, investmentGoal: goal }))}
                      className={`px-4 py-2 rounded-lg border transition-colors ${
                        formData.investmentGoal === goal
                          ? 'bg-purple-600 text-white border-purple-600'
                          : 'bg-white text-gray-700 border-gray-300 hover:border-purple-300'
                      }`}
                    >
                      {goal}
                    </button>
                  ))}
                </div>
              </div>

              {/* 선호 섹터 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  선호 섹터 (복수 선택 가능)
                </label>
                <div className="grid grid-cols-3 gap-3">
                  {sectorOptions.map((sector) => (
                    <button
                      key={sector}
                      onClick={() => handleSectorToggle(sector)}
                      className={`px-3 py-2 rounded-lg border transition-colors ${
                        formData.preferredSectors.includes(sector)
                          ? 'bg-purple-600 text-white border-purple-600'
                          : 'bg-white text-gray-700 border-gray-300 hover:border-purple-300'
                      }`}
                    >
                      {sector}
                    </button>
                  ))}
                </div>
              </div>

              {/* 생성 버튼 */}
              <div className="pt-4">
                <button
                  onClick={handleGenerateReport}
                  disabled={isGenerating || !formData.investmentAmount}
                  className="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:from-purple-700 hover:to-blue-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                >
                  {isGenerating ? (
                    <>
                      <ClockIcon className="h-5 w-5 animate-spin" />
                      <span>AI 분석 중...</span>
                    </>
                  ) : (
                    <>
                      <SparklesIcon className="h-5 w-5" />
                      <span>투자 보고서 생성하기</span>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        ) : (
          /* 보고서 결과 */
          <div className="space-y-6">
            <div className="text-center">
              <CheckCircleIcon className="h-16 w-16 text-green-500 mx-auto mb-4" />
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                AI 투자 보고서 생성 완료!
              </h2>
              <p className="text-gray-600">
                맞춤형 투자 전략을 확인해보세요
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center space-x-3 mb-4">
                <DocumentTextIcon className="h-6 w-6 text-purple-600" />
                <h3 className="text-lg font-semibold text-gray-900">투자 보고서</h3>
              </div>
              
              <div className="space-y-4">
                <div className="border-b border-gray-200 pb-4">
                  <h4 className="font-semibold text-gray-900 mb-2">투자 프로필</h4>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">투자 금액:</span>
                      <span className="ml-2 font-medium">{Number(formData.investmentAmount).toLocaleString()}원</span>
                    </div>
                    <div>
                      <span className="text-gray-600">위험 성향:</span>
                      <span className="ml-2 font-medium">{formData.riskTolerance}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">투자 기간:</span>
                      <span className="ml-2 font-medium">{formData.investmentPeriod}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">투자 목표:</span>
                      <span className="ml-2 font-medium">{formData.investmentGoal}</span>
                    </div>
                  </div>
                </div>

                <div className="border-b border-gray-200 pb-4">
                  <h4 className="font-semibold text-gray-900 mb-2">AI 투자 추천</h4>
                  <div className="space-y-3">
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <h5 className="font-medium text-blue-900 mb-2">포트폴리오 구성</h5>
                      <ul className="text-sm text-blue-800 space-y-1">
                        <li>• 주식형 펀드: 40%</li>
                        <li>• 채권형 펀드: 30%</li>
                        <li>• 부동산 투자신탁: 20%</li>
                        <li>• 현금: 10%</li>
                      </ul>
                    </div>
                    <div className="bg-green-50 p-4 rounded-lg">
                      <h5 className="font-medium text-green-900 mb-2">예상 수익률</h5>
                      <p className="text-sm text-green-800">
                        연 6-8% 수익률 예상 (시장 상황에 따라 변동 가능)
                      </p>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">투자 전략</h4>
                  <div className="text-sm text-gray-700 space-y-2">
                    <p>• 정기적인 포트폴리오 리밸런싱 (분기별)</p>
                    <p>• 분산 투자로 위험 분산</p>
                    <p>• 장기 투자 관점 유지</p>
                    <p>• 시장 변동성에 대비한 현금 보유</p>
                  </div>
                </div>
              </div>

              <div className="mt-6 flex space-x-4">
                <button className="flex-1 bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 transition-colors">
                  PDF 다운로드
                </button>
                <Link href="/" className="flex-1 bg-gray-200 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-300 transition-colors text-center">
                  홈으로 돌아가기
                </Link>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
} 