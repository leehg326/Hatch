import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { api } from '@/lib/api';
import { 
  ArrowLeft, 
  Download, 
  Printer, 
  FileText, 
  Calendar, 
  MapPin, 
  User, 
  Phone,
  Banknote,
  PenTool
} from 'lucide-react';
import type { 
  Contract
} from '@/utils/contract';
import { 
  formatContractDate, 
  formatContractPrice, 
  getContractStatusBadge, 
  getContractTypeLabel,
  formatContractPeriod
} from '@/utils/contract';

export default function ContractPreview() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [contract, setContract] = useState<Contract | null>(null);
  const [loading, setLoading] = useState(true);
  const [pdfLoading, setPdfLoading] = useState(false);

  useEffect(() => {
    if (id) {
      fetchContract(parseInt(id));
    }
  }, [id]);

  const fetchContract = async (contractId: number) => {
    try {
      setLoading(true);
      const response = await api.get(`/contracts/${contractId}`);
      
      if (response.data) {
        setContract(response.data.contract);
      }
    } catch (error: any) {
      toast({
        title: '오류가 발생했습니다',
        description: error.response?.data?.error || '계약서를 불러오는데 실패했습니다.',
        variant: 'destructive',
      });
      navigate('/contracts');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = async () => {
    if (!contract) return;

    try {
      setPdfLoading(true);
      const response = await api.get(`/contracts/${contract.id}/pdf`, {
        responseType: 'blob',
      });

      // PDF 다운로드
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `contract_${contract.id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      toast({
        title: 'PDF가 다운로드되었습니다',
        description: '계약서 PDF가 성공적으로 다운로드되었습니다.',
      });
    } catch (error: any) {
      toast({
        title: '오류가 발생했습니다',
        description: error.response?.data?.error || 'PDF 다운로드에 실패했습니다.',
        variant: 'destructive',
      });
    } finally {
      setPdfLoading(false);
    }
  };

  const handlePrint = async () => {
    if (!contract) return;

    try {
      setPdfLoading(true);
      const response = await api.get(`/contracts/${contract.id}/pdf`, {
        responseType: 'blob',
      });

      // PDF를 새 창에서 열어서 인쇄
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const printWindow = window.open(url, '_blank');
      
      if (printWindow) {
        printWindow.onload = () => {
          printWindow.print();
        };
      }
    } catch (error: any) {
      toast({
        title: '오류가 발생했습니다',
        description: error.response?.data?.error || '인쇄에 실패했습니다.',
        variant: 'destructive',
      });
    } finally {
      setPdfLoading(false);
    }
  };

  const getSignatureRoleLabel = (role: string) => {
    const roleMap = {
      'SELLER': '매도인',
      'BUYER': '매수인',
      'LESSOR': '임대인',
      'LESSEE': '임차인',
      'AGENT': '중개인',
      'BROKER': '중개인'
    };
    return roleMap[role as keyof typeof roleMap] || role;
  };

  const handlePdfView = () => {
    if (contract) {
      window.open(`/api/contracts/${contract.id}/pdf/preview?include=signatures,stamps`, '_blank');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">계약서를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (!contract) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">계약서를 찾을 수 없습니다</h2>
          <p className="text-gray-600 mb-4">요청하신 계약서가 존재하지 않거나 삭제되었습니다.</p>
          <Button onClick={() => navigate('/contracts')}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            계약서 목록으로 돌아가기
          </Button>
        </div>
      </div>
    );
  }

  const status = getContractStatusBadge(contract.status || 'DRAFT');
  const contractType = getContractTypeLabel(contract.type);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* 헤더 */}
        <div className="mb-8">
          <div className="flex items-center gap-4 mb-4">
            <Button
              variant="ghost"
              onClick={() => navigate('/contracts')}
              className="p-2"
            >
              <ArrowLeft className="w-4 h-4" />
            </Button>
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-gray-900">계약서 상세</h1>
              <p className="text-gray-600">계약서 정보를 확인하고 PDF를 다운로드하세요</p>
            </div>
            <div className="flex gap-2">
              <Button
                onClick={handlePdfView}
                className="bg-green-600 hover:bg-green-700"
              >
                <FileText className="w-4 h-4 mr-2" />
                PDF 미리보기
              </Button>
              <Button
                onClick={handleDownloadPDF}
                disabled={pdfLoading}
                className="bg-blue-600 hover:bg-blue-700"
              >
                <Download className="w-4 h-4 mr-2" />
                {pdfLoading ? '다운로드 중...' : 'PDF 다운로드'}
              </Button>
              <Button
                onClick={handlePrint}
                disabled={pdfLoading}
                variant="outline"
              >
                <Printer className="w-4 h-4 mr-2" />
                {pdfLoading ? '인쇄 중...' : '인쇄'}
              </Button>
            </div>
          </div>
        </div>

        {/* 계약서 정보 */}
        <div className="space-y-6">
          {/* 상태 및 기본 정보 */}
          <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <CardTitle className="text-xl">{contractType}계약서 정보</CardTitle>
                <div className="flex gap-2">
                  <Badge variant={status.variant}>{status.label}</Badge>
                  <Badge variant="outline">문서번호: {contract.doc_no}</Badge>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {contract.type === 'SALE' ? (
                // 매매계약서 정보
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-4">
                      <div className="flex items-center gap-3">
                        <User className="w-5 h-5 text-blue-500" />
                        <div>
                          <p className="text-sm text-gray-600">매수인</p>
                          <p className="font-semibold text-lg">{contract.buyer_name}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <Phone className="w-5 h-5 text-gray-500" />
                        <div>
                          <p className="text-sm text-gray-600">매수인 연락처</p>
                          <p className="font-semibold">{contract.buyer_phone}</p>
                        </div>
                      </div>
                    </div>
                    <div className="space-y-4">
                      <div className="flex items-center gap-3">
                        <User className="w-5 h-5 text-green-500" />
                        <div>
                          <p className="text-sm text-gray-600">매도인</p>
                          <p className="font-semibold text-lg">{contract.seller_name}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <Phone className="w-5 h-5 text-gray-500" />
                        <div>
                          <p className="text-sm text-gray-600">매도인 연락처</p>
                          <p className="font-semibold">{contract.seller_phone}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="flex items-center gap-3">
                      <MapPin className="w-5 h-5 text-gray-500" />
                      <div>
                        <p className="text-sm text-gray-600">부동산 주소</p>
                        <p className="font-semibold">{contract.property_address}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <Banknote className="w-5 h-5 text-purple-500" />
                      <div>
                        <p className="text-sm text-gray-600">매매금액</p>
                        <p className="font-semibold text-lg text-purple-600">
                          {formatContractPrice(contract)}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                // 임대차/전세/월세/반전세 계약서 정보
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div className="flex items-center gap-3">
                      <User className="w-5 h-5 text-gray-500" />
                      <div>
                        <p className="text-sm text-gray-600">고객명</p>
                        <p className="font-semibold text-lg">{contract.buyer_name}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <Phone className="w-5 h-5 text-gray-500" />
                      <div>
                        <p className="text-sm text-gray-600">연락처</p>
                        <p className="font-semibold">{contract.buyer_phone}</p>
                      </div>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <div className="flex items-center gap-3">
                      <MapPin className="w-5 h-5 text-gray-500" />
                      <div>
                        <p className="text-sm text-gray-600">부동산 주소</p>
                        <p className="font-semibold">{contract.property_address}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <Banknote className="w-5 h-5 text-gray-500" />
                      <div>
                        <p className="text-sm text-gray-600">계약 금액</p>
                        <p className="font-semibold text-lg text-blue-600">
                          {formatContractPrice(contract)}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* 계약 기간 */}
          <Card>
            <CardHeader>
              <CardTitle className="text-xl">계약 기간</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-3">
                <Calendar className="w-5 h-5 text-gray-500" />
                <div>
                  <p className="text-sm text-gray-600">계약 기간</p>
                  <p className="font-semibold text-lg">
                    {formatContractPeriod(contract)}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* 서명 */}
          <Card>
            <CardHeader>
              <CardTitle className="text-xl flex items-center gap-2">
                <PenTool className="w-5 h-5" />
                서명
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {(() => {
                  // 계약 유형에 따른 서명 역할 결정
                  const getSignatureRoles = (contractType: string) => {
                    switch (contractType) {
                      case 'SALE':
                        return ['SELLER', 'BUYER', 'AGENT'];
                      case 'JEONSE':
                      case 'WOLSE':
                        return ['LESSOR', 'LESSEE', 'BROKER'];
                      default:
                        return ['SELLER', 'BUYER', 'AGENT'];
                    }
                  };
                  
                  return getSignatureRoles(contract?.type || 'SALE');
                })().map((role) => {
                  const signature = contract.signatures?.find(sig => sig.role === role);
                  return (
                    <div key={role} className="border rounded-lg p-4 text-center">
                      <h4 className="font-semibold text-gray-900 mb-2">
                        {getSignatureRoleLabel(role)}
                      </h4>
                      {signature && signature.image_url ? (
                        <div>
                          <img 
                            src={signature.image_url}
                            alt={`${getSignatureRoleLabel(role)} 서명`}
                            className="w-32 h-16 mx-auto border rounded mb-2"
                            onError={(e) => {
                              // 이미지 로드 실패 시 서명 대기 표시
                              const container = e.currentTarget.parentElement;
                              if (container) {
                                container.innerHTML = `
                                  <div class="w-32 h-16 mx-auto border rounded mb-2 flex items-center justify-center bg-gray-50">
                                    <span class="text-xs text-gray-500">서명 대기</span>
                                  </div>
                                  <p class="text-xs text-gray-500">서명하지 않음</p>
                                `;
                              }
                            }}
                          />
                          <p className="text-xs text-gray-500">
                            {formatContractDate(signature.signed_at)}
                          </p>
                        </div>
                      ) : (
                        <div className="w-32 h-16 mx-auto border rounded mb-2 flex items-center justify-center bg-gray-50">
                          <span className="text-xs text-gray-500">서명 대기</span>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          {/* 특이사항 */}
          {contract.special_terms && (
            <Card>
              <CardHeader>
                <CardTitle className="text-xl">특약사항</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <p className="text-gray-700 whitespace-pre-wrap">{contract.special_terms}</p>
                </div>
              </CardContent>
            </Card>
          )}

          {/* 계약서 메타 정보 */}
          <Card>
            <CardHeader>
              <CardTitle className="text-xl">계약서 정보</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <p className="text-gray-600">계약서 ID</p>
                  <p className="font-semibold">#{contract.id}</p>
                </div>
                <div>
                  <p className="text-gray-600">문서번호</p>
                  <p className="font-semibold">{contract.doc_no}</p>
                </div>
                <div>
                  <p className="text-gray-600">작성일</p>
                  <p className="font-semibold">{formatContractDate(contract.created_at)}</p>
                </div>
                <div>
                  <p className="text-gray-600">문서 해시</p>
                  <p className="font-mono text-xs">{contract.short_hash}</p>
                </div>
                <div>
                  <p className="text-gray-600">수정일</p>
                  <p className="font-semibold">{formatContractDate(contract.updated_at)}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
