import React, { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Download, Eye, Shield, FileText, Calendar } from 'lucide-react';

interface PdfPreviewProps {
  contractId: number;
  contractType: 'SALE' | 'JEONSE' | 'WOLSE';
  contractStatus?: string;
  onError?: (error: string) => void;
}

interface PdfInfo {
  contract_id: number;
  doc_no: string;
  doc_hash: string;
  pdf_hash: string;
  created_at: string;
  updated_at: string;
  form_version: string;
}

const PdfPreview: React.FC<PdfPreviewProps> = ({
  contractId,
  contractType,
  contractStatus,
  onError
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [pdfInfo, setPdfInfo] = useState<PdfInfo | null>(null);
  const [isValid, setIsValid] = useState<boolean | null>(null);
  const [error, setError] = useState<string | null>(null);
  const iframeRef = useRef<HTMLIFrameElement>(null);

  // PDF 정보 로드
  const loadPdfInfo = async () => {
    try {
      const response = await fetch(`/api/contracts/${contractId}/pdf/info`);
      if (!response.ok) {
        throw new Error('PDF 정보를 불러올 수 없습니다');
      }
      const data = await response.json();
      setPdfInfo(data);
    } catch (err) {
      console.error('PDF 정보 로드 실패:', err);
      setError(err instanceof Error ? err.message : '알 수 없는 오류');
    }
  };

  // PDF 무결성 검증
  const verifyPdfIntegrity = async () => {
    try {
      setIsLoading(true);
      const response = await fetch(`/api/contracts/${contractId}/pdf/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error('PDF 무결성 검증에 실패했습니다');
      }
      
      const data = await response.json();
      setIsValid(data.is_valid);
      
      if (!data.is_valid) {
        setError('PDF 무결성이 손상되었습니다. 다시 생성해주세요.');
      }
    } catch (err) {
      console.error('PDF 무결성 검증 실패:', err);
      setError(err instanceof Error ? err.message : '검증 중 오류가 발생했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  // PDF 다운로드
  const downloadPdf = async () => {
    try {
      setIsLoading(true);
      
      // 직접 다운로드 링크로 이동
      const link = document.createElement('a');
      link.href = pdfDownloadUrl;
      link.download = `contract_${contractId}_${contractType.toLowerCase()}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
    } catch (err) {
      console.error('PDF 다운로드 실패:', err);
      setError(err instanceof Error ? err.message : '다운로드 중 오류가 발생했습니다');
      onError?.(err instanceof Error ? err.message : '다운로드 중 오류가 발생했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  // PDF 미리보기 새로고침
  const refreshPreview = () => {
    if (iframeRef.current) {
      const iframe = iframeRef.current;
      iframe.src = iframe.src;
    }
  };

  // 컴포넌트 마운트 시 PDF 정보 로드
  useEffect(() => {
    loadPdfInfo();
  }, [contractId]);

  // PDF 미리보기 URL 생성
  const pdfPreviewUrl = `/api/contracts/${contractId}/pdf?mode=inline&t=${Date.now()}`;
  
  // PDF 다운로드 URL 생성
  const pdfDownloadUrl = `/api/contracts/${contractId}/pdf?mode=download`;

  // 계약 유형 한글명
  const getContractTypeKorean = (type: string) => {
    const typeMap = {
      'SALE': '매매',
      'JEONSE': '전세',
      'WOLSE': '월세'
    };
    return typeMap[type as keyof typeof typeMap] || type;
  };

  // 상태별 배지 색상
  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'SIGNED': return 'default';
      case 'DRAFT': return 'secondary';
      case 'ARCHIVED': return 'outline';
      default: return 'secondary';
    }
  };

  return (
    <div className="space-y-4">
      {/* PDF 정보 카드 */}
      {pdfInfo && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              PDF 정보
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="font-medium">문서번호:</span>
                <span className="ml-2 font-mono text-xs">{pdfInfo.doc_no}</span>
              </div>
              <div>
                <span className="font-medium">계약유형:</span>
                <Badge variant="outline" className="ml-2">
                  {getContractTypeKorean(contractType)}
                </Badge>
              </div>
              <div>
                <span className="font-medium">상태:</span>
                <Badge 
                  variant={getStatusBadgeVariant(contractStatus || 'DRAFT')} 
                  className="ml-2"
                >
                  {contractStatus || 'DRAFT'}
                </Badge>
              </div>
              <div>
                <span className="font-medium">문서버전:</span>
                <span className="ml-2 text-xs">{pdfInfo.form_version}</span>
              </div>
            </div>
            
            {pdfInfo.pdf_hash && (
              <div className="pt-2 border-t">
                <div className="text-xs text-muted-foreground">
                  <span className="font-medium">PDF 해시:</span>
                  <span className="ml-2 font-mono">{pdfInfo.pdf_hash.substring(0, 16)}...</span>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* 액션 버튼들 */}
      <div className="flex gap-2 flex-wrap">
        <Button
          onClick={downloadPdf}
          disabled={isLoading}
          className="flex items-center gap-2"
        >
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Download className="h-4 w-4" />
          )}
          PDF 다운로드
        </Button>
        
        <Button
          onClick={refreshPreview}
          variant="outline"
          className="flex items-center gap-2"
        >
          <Eye className="h-4 w-4" />
          미리보기 새로고침
        </Button>
        
        <Button
          onClick={verifyPdfIntegrity}
          disabled={isLoading}
          variant="outline"
          className="flex items-center gap-2"
        >
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Shield className="h-4 w-4" />
          )}
          무결성 검증
        </Button>
      </div>

      {/* 무결성 검증 결과 */}
      {isValid !== null && (
        <Alert variant={isValid ? "default" : "destructive"}>
          <Shield className="h-4 w-4" />
          <AlertDescription>
            {isValid 
              ? 'PDF 무결성이 확인되었습니다.' 
              : 'PDF 무결성이 손상되었습니다. 다시 생성해주세요.'
            }
          </AlertDescription>
        </Alert>
      )}

      {/* 에러 메시지 */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* PDF 미리보기 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Eye className="h-5 w-5" />
            PDF 미리보기
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="border rounded-lg overflow-hidden">
            <iframe
              ref={iframeRef}
              src={pdfPreviewUrl}
              width="100%"
              height="600"
              className="border-0"
              title={`계약서 ${contractId} PDF 미리보기`}
              onLoad={() => setIsLoading(false)}
              onError={() => {
                setError('PDF 미리보기를 불러올 수 없습니다');
                setIsLoading(false);
              }}
            />
          </div>
          
          {isLoading && (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin" />
              <span className="ml-2">PDF를 불러오는 중...</span>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 생성 정보 */}
      {pdfInfo && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              생성 정보
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <span className="font-medium">생성일:</span>
                <span className="ml-2">
                  {new Date(pdfInfo.created_at).toLocaleString('ko-KR')}
                </span>
              </div>
              <div>
                <span className="font-medium">수정일:</span>
                <span className="ml-2">
                  {new Date(pdfInfo.updated_at).toLocaleString('ko-KR')}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default PdfPreview;
