'use client';

import { useState, useEffect, useMemo } from 'react';
import Link from 'next/link';
import {
  ArrowLeftIcon,
  SparklesIcon,
  ClockIcon,
  DocumentTextIcon,
  CheckCircleIcon,
  BuildingOfficeIcon,
  ArrowDownTrayIcon,
  MagnifyingGlassIcon,
  FunnelIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline';
import { Company, ReportSummary, ReportResult } from '@/types';

// 업종별 카테고리 정의
const COMPANY_CATEGORIES: { [key: string]: string[] } = {
  '반도체/전자': ['삼성전자', 'SK하이닉스', '삼성SDI', 'LG전자', '삼성전기', 'LG디스플레이'],
  '금융': ['KB금융', '신한지주', '하나금융지주', '우리금융지주', '한국금융지주', '삼성생명', '삼성화재'],
  '자동차': ['현대차', '기아', '현대모비스', '현대글로비스', '한온시스템', '현대위아'],
  '화학/에너지': ['LG화학', 'LG에너지솔루션', 'SK이노베이션', '한화솔루션', '롯데케미칼', 'S-Oil'],
  'IT/게임': ['NAVER', '카카오', '엔씨소프트', '크래프톤', '넷마블', 'SK스퀘어'],
  '건설/중공업': ['현대건설', '대우건설', 'GS건설', '현대중공업', '한국조선해양', '삼성중공업'],
  '바이오/제약': ['삼성바이오로직스', '셀트리온', '한미사이언스', '한미약품', 'SK바이오팜'],
  '유통/소비재': ['롯데쇼핑', 'GS리테일', '현대백화점', '현대홈쇼핑', '오리온', 'CJ제일제당'],
  '통신': ['SK텔레콤', 'KT', 'LG유플러스'],
  '기타': []
};

export default function AIInvestmentReport() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [reportGenerated, setReportGenerated] = useState(false);
  const [companyName, setCompanyName] = useState('');
  const [supportedCompanies, setSupportedCompanies] = useState<Company[]>([]);
  const [reportResult, setReportResult] = useState<ReportResult | null>(null);
  const [error, setError] = useState('');
  const [isLoadingCompanies, setIsLoadingCompanies] = useState(true);
  
  // 검색 및 필터링 상태
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('전체');
  const [showCompanyList, setShowCompanyList] = useState(false);

  // 기업 카테고리 분류 함수
  const getCompanyCategory = (companyName: string) => {
    for (const [category, companies] of Object.entries(COMPANY_CATEGORIES)) {
      if (companies.includes(companyName)) {
        return category;
      }
    }
    return '기타';
  };

  // 필터링된 기업 목록
  const filteredCompanies = useMemo(() => {
    let filtered = supportedCompanies;

    // 검색어로 필터링
    if (searchTerm) {
      filtered = filtered.filter(company => 
        company.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        company.ticker.includes(searchTerm)
      );
    }

    // 카테고리로 필터링
    if (selectedCategory !== '전체') {
      filtered = filtered.filter(company => 
        getCompanyCategory(company.name) === selectedCategory
      );
    }

    return filtered;
  }, [supportedCompanies, searchTerm, selectedCategory]);

  // 지원되는 기업 목록 가져오기
  useEffect(() => {
    const fetchSupportedCompanies = async () => {
      try {
        const response = await fetch('http://localhost:5001/api/supported-companies');
        if (response.ok) {
          const data = await response.json();
          setSupportedCompanies(data.companies || []);
        } else {
          console.error('지원 기업 목록을 가져오는데 실패했습니다.');
        }
      } catch (error) {
        console.error('지원 기업 목록을 가져오는 중 오류:', error);
      } finally {
        setIsLoadingCompanies(false);
      }
    };

    fetchSupportedCompanies();
  }, []);

  const handleGenerateReport = async () => {
    if (!companyName.trim()) {
      setError('기업명을 입력해주세요.');
      return;
    }

    setIsGenerating(true);
    setError('');

    try {
      const response = await fetch('http://localhost:5001/api/generate-report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          company_name: companyName.trim(),
        }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setReportResult(data);
        setReportGenerated(true);
      } else {
        setError(data.error || data.message || '투자보고서 생성에 실패했습니다.');
      }
    } catch (error) {
      console.error('투자보고서 생성 중 오류:', error);
      setError('서버와 통신 중 오류가 발생했습니다. 백엔드 서버(http://localhost:5001)가 실행 중인지 확인해주세요.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownloadPdf = async () => {
    if (!reportResult?.pdf_file) return;

    try {
      const filename = reportResult.pdf_file.split('/').pop();
      const response = await fetch(`http://localhost:5001/api/download-pdf/${filename}`);

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename || 'investment_report.pdf';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        setError('PDF 다운로드에 실패했습니다.');
      }
    } catch (error) {
      console.error('PDF 다운로드 중 오류:', error);
      setError('PDF 다운로드 중 오류가 발생했습니다.');
    }
  };

  const resetForm = () => {
    setReportGenerated(false);
    setReportResult(null);
    setCompanyName('');
    setError('');
  };

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
                <BuildingOfficeIcon className="h-8 w-8 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">기업 투자 보고서 생성</h2>
              <p className="text-gray-600">
                분석하고 싶은 기업명을 입력하시면 AI가 실시간 데이터를 기반으로 투자 보고서를 생성해드립니다
              </p>
            </div>

            {/* 에러 메시지 */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <p className="text-red-800 text-sm">{error}</p>
              </div>
            )}

            {/* 입력 폼 */}
            <div className="bg-white rounded-lg shadow-md p-6 space-y-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">기업 정보 입력</h3>

              {/* 기업명 입력 */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">분석할 기업명</label>
                <input
                  type="text"
                  placeholder="예: 삼성전자, SK하이닉스, NAVER 등"
                  className="w-full px-3 py-2 border border-gray-300 placeholder:text-gray-300 text-black rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && !isGenerating && companyName.trim()) {
                      handleGenerateReport();
                    }
                  }}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Enter키를 누르거나 아래 버튼을 클릭하여 보고서를 생성하세요
                </p>
              </div>

              {/* 지원 기업 목록 */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-sm font-medium text-gray-700">
                    지원되는 기업 목록 ({supportedCompanies.length}개)
                  </label>
                  <button
                    onClick={() => setShowCompanyList(!showCompanyList)}
                    className="text-sm text-purple-600 hover:text-purple-700 flex items-center space-x-1"
                  >
                    <span>{showCompanyList ? '숨기기' : '전체 보기'}</span>
                    <FunnelIcon className="h-4 w-4" />
                  </button>
                </div>

                {isLoadingCompanies ? (
                  <div className="text-center py-8">
                    <ClockIcon className="h-8 w-8 animate-spin mx-auto text-gray-400" />
                    <p className="text-sm text-gray-500 mt-2">기업 목록 로딩 중...</p>
                  </div>
                ) : supportedCompanies.length > 0 ? (
                  <>
                    {/* 인기 기업 빠른 선택 */}
                    <div className="mb-4">
                      <p className="text-xs text-gray-500 mb-2">인기 기업 빠른 선택</p>
                      <div className="flex flex-wrap gap-2">
                        {['삼성전자', 'SK하이닉스', 'NAVER', '카카오', '현대차', 'LG에너지솔루션'].map((company) => (
                          <button
                            key={company}
                            onClick={() => setCompanyName(company)}
                            className="px-3 py-1 text-xs bg-purple-100 text-purple-700 rounded-full hover:bg-purple-200 transition-colors"
                          >
                            {company}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* 전체 기업 목록 */}
                    {showCompanyList && (
                      <div className="border border-gray-200 rounded-lg">
                        <div className="p-4 bg-gray-50 border-b border-gray-200">
                          {/* 검색 바 */}
                          <div className="relative mb-4">
                            <MagnifyingGlassIcon className="h-5 w-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                            <input
                              type="text"
                              placeholder="기업명 또는 종목코드 검색..."
                              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-sm"
                              value={searchTerm}
                              onChange={(e) => setSearchTerm(e.target.value)}
                            />
                            {searchTerm && (
                              <button
                                onClick={() => setSearchTerm('')}
                                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                              >
                                <XMarkIcon className="h-4 w-4" />
                              </button>
                            )}
                          </div>

                          {/* 카테고리 필터 */}
                          <div className="flex flex-wrap gap-2">
                            <button
                              onClick={() => setSelectedCategory('전체')}
                              className={`px-3 py-1 text-xs rounded-full transition-colors ${
                                selectedCategory === '전체'
                                  ? 'bg-purple-600 text-white'
                                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                              }`}
                            >
                              전체
                            </button>
                            {Object.keys(COMPANY_CATEGORIES).map((category) => (
                              <button
                                key={category}
                                onClick={() => setSelectedCategory(category)}
                                className={`px-3 py-1 text-xs rounded-full transition-colors ${
                                  selectedCategory === category
                                    ? 'bg-purple-600 text-white'
                                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                                }`}
                              >
                                {category}
                              </button>
                            ))}
                          </div>
                        </div>

                        {/* 기업 목록 */}
                        <div className="max-h-64 overflow-y-auto p-4">
                          {filteredCompanies.length > 0 ? (
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                              {filteredCompanies.map((company) => (
                                <button
                                  key={company.ticker}
                                  onClick={() => {
                                    setCompanyName(company.name);
                                    setShowCompanyList(false);
                                  }}
                                  className="text-left p-3 border border-gray-200 rounded-lg hover:border-purple-300 hover:bg-purple-50 transition-all group"
                                >
                                  <div className="flex items-center justify-between">
                                    <div>
                                      <p className="font-medium text-sm text-gray-900 group-hover:text-purple-700">
                                        {company.name}
                                      </p>
                                      <p className="text-xs text-gray-500">
                                        {company.ticker}
                                      </p>
                                    </div>
                                    <div className="text-xs text-gray-400">
                                      {getCompanyCategory(company.name)}
                                    </div>
                                  </div>
                                </button>
                              ))}
                            </div>
                          ) : (
                            <div className="text-center py-8">
                              <p className="text-sm text-gray-500">
                                검색 조건에 맞는 기업이 없습니다.
                              </p>
                            </div>
                          )}
                        </div>

                        {/* 결과 요약 */}
                        <div className="px-4 py-2 bg-gray-50 border-t border-gray-200 text-xs text-gray-600">
                          {searchTerm || selectedCategory !== '전체' 
                            ? `${filteredCompanies.length}개 기업이 검색되었습니다.`
                            : `총 ${supportedCompanies.length}개 기업을 지원합니다.`
                          }
                        </div>
                      </div>
                    )}
                  </>
                ) : (
                  <p className="text-sm text-gray-500 text-center py-4">
                    지원 기업 목록을 불러올 수 없습니다. 백엔드 서버를 확인해주세요.
                  </p>
                )}
              </div>

              {/* 생성 버튼 */}
              <div className="pt-4">
                <button
                  onClick={handleGenerateReport}
                  disabled={isGenerating || !companyName.trim()}
                  className="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:from-purple-700 hover:to-blue-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                >
                  {isGenerating ? (
                    <>
                      <ClockIcon className="h-5 w-5 animate-spin" />
                      <span>AI 분석 중... (1-2분 소요)</span>
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
                {reportResult?.company_name} 투자 보고서 생성 완료!
              </h2>
              <p className="text-gray-600">AI가 분석한 실시간 투자 보고서를 확인해보세요</p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center space-x-3 mb-4">
                <DocumentTextIcon className="h-6 w-6 text-purple-600" />
                <h3 className="text-lg font-semibold text-gray-900">{reportResult?.company_name} 투자 분석 보고서</h3>
              </div>

              {reportResult?.summary && (
                <div className="space-y-4">
                  <div className="border-b border-gray-200 pb-4">
                    <h4 className="font-semibold text-gray-900 mb-2">주요 지표</h4>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-600">현재가:</span>
                        <span className="ml-2 font-medium">{reportResult.summary.current_price}원</span>
                      </div>
                      <div>
                        <span className="text-gray-600">전일대비:</span>
                        <span
                          className={`ml-2 font-medium ${
                            (reportResult.summary.change_percent || 0) < 0 ? 'text-red-600' : 'text-green-600'
                          }`}
                        >
                          {reportResult.summary.change}원 ({reportResult.summary.change_percent}%)
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-600">분석 기간:</span>
                        <span className="ml-2 font-medium">{reportResult.summary.analysis_period}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">분석된 뉴스:</span>
                        <span className="ml-2 font-medium">{reportResult.summary.news_count}개</span>
                      </div>
                    </div>
                  </div>

                  <div className="border-b border-gray-200 pb-4">
                    <h4 className="font-semibold text-gray-900 mb-2">보고서 정보</h4>
                    <div className="space-y-3">
                      <div className="bg-blue-50 p-4 rounded-lg">
                        <h5 className="font-medium text-blue-900 mb-2">생성 정보</h5>
                        <div className="text-sm text-blue-800 space-y-1">
                          <p>• 생성 시간: {new Date(reportResult.timestamp).toLocaleString('ko-KR')}</p>
                          <p>• JSON 파일: {reportResult.json_file}</p>
                          {reportResult.pdf_file && <p>• PDF 파일: {reportResult.pdf_file}</p>}
                        </div>
                      </div>
                      <div className="bg-green-50 p-4 rounded-lg">
                        <h5 className="font-medium text-green-900 mb-2">분석 완료</h5>
                        <p className="text-sm text-green-800">{reportResult.message}</p>
                      </div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">보고서 내용</h4>
                    <div className="text-sm text-gray-700 space-y-2">
                      <p>• 실시간 주가 데이터 분석</p>
                      <p>• 최신 뉴스 기반 시장 동향 분석</p>
                      <p>• AI 기반 투자 의견 및 전략 제시</p>
                      <p>• 리스크 분석 및 주의사항</p>
                    </div>
                  </div>
                </div>
              )}

              <div className="mt-6 flex space-x-4">
                {reportResult?.pdf_file && (
                  <button
                    onClick={handleDownloadPdf}
                    className="flex-1 bg-purple-600 text-white py-2 px-4 rounded-lg hover:bg-purple-700 transition-colors flex items-center justify-center space-x-2"
                  >
                    <ArrowDownTrayIcon className="h-4 w-4" />
                    <span>PDF 다운로드</span>
                  </button>
                )}
                <button
                  onClick={resetForm}
                  className="flex-1 bg-gray-200 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  다른 기업 분석하기
                </button>
                <Link
                  href="/"
                  className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors text-center"
                >
                  홈으로 돌아가기
                </Link>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
