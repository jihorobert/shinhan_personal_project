'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  ArrowLeftIcon,
  SparklesIcon,
  ClockIcon,
  DocumentTextIcon,
  CheckCircleIcon,
  BuildingOfficeIcon,
  ArrowDownTrayIcon,
} from '@heroicons/react/24/outline';
import { Company, ReportSummary, ReportResult } from '@/types';

export default function AIInvestmentReport() {
  const [isGenerating, setIsGenerating] = useState(false);
  const [reportGenerated, setReportGenerated] = useState(false);
  const [companyName, setCompanyName] = useState('');
  const [supportedCompanies, setSupportedCompanies] = useState<Company[]>([]);
  const [reportResult, setReportResult] = useState<ReportResult | null>(null);
  const [error, setError] = useState('');
  const [isLoadingCompanies, setIsLoadingCompanies] = useState(true);

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
                <label className="block text-sm font-medium text-gray-700 mb-2">지원되는 기업 목록</label>
                {isLoadingCompanies ? (
                  <div className="text-center py-4">
                    <ClockIcon className="h-5 w-5 animate-spin mx-auto text-gray-400" />
                    <p className="text-sm text-gray-500 mt-1">기업 목록 로딩 중...</p>
                  </div>
                ) : supportedCompanies.length > 0 ? (
                  <div className="max-h-40 overflow-y-auto border border-gray-200 rounded-lg p-3">
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                      {supportedCompanies.map((company) => (
                        <button
                          key={company.ticker}
                          onClick={() => setCompanyName(company.name)}
                          className="text-left px-2 py-1 text-sm text-blue-600 hover:bg-blue-50 rounded transition-colors"
                        >
                          {company.name} ({company.ticker})
                        </button>
                      ))}
                    </div>
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">
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
