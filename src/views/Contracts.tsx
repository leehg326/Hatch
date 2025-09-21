import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { api } from '@/lib/api';
import { Search, Plus, FileText, Calendar, MapPin, User, Phone } from 'lucide-react';

interface Contract {
  id: number;
  customer_name: string;
  customer_phone: string;
  property_address: string;
  price: number;
  start_date: string;
  end_date: string;
  memo?: string;
  created_at: string;
}

export default function Contracts() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [contracts, setContracts] = useState<Contract[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const fetchContracts = async (page = 1, query = '') => {
    try {
      setLoading(true);
      const response = await api.get('/contracts', {
        params: {
          page,
          per_page: 20,
          q: query,
        },
      });

      if (response.data) {
        setContracts(response.data.contracts);
        setTotalPages(response.data.pages);
        setCurrentPage(page);
      }
    } catch (error: any) {
      toast({
        title: '오류가 발생했습니다',
        description: error.response?.data?.error || '계약서 목록을 불러오는데 실패했습니다.',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchContracts();
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchContracts(1, searchQuery);
  };

  const handleContractClick = (contractId: number) => {
    navigate(`/contracts/${contractId}`);
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('ko-KR').format(price) + '원';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ko-KR');
  };

  const getContractStatus = (startDate: string, endDate: string) => {
    const now = new Date();
    const start = new Date(startDate);
    const end = new Date(endDate);

    if (now < start) {
      return { label: '계약 예정', variant: 'secondary' as const };
    } else if (now >= start && now <= end) {
      return { label: '진행 중', variant: 'default' as const };
    } else {
      return { label: '종료', variant: 'outline' as const };
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">계약서 관리</h1>
              <p className="text-gray-600">부동산 임대차 계약서를 관리하세요</p>
            </div>
            <Button
              onClick={() => navigate('/contracts/new')}
              className="bg-blue-600 hover:bg-blue-700"
            >
              <Plus className="w-4 h-4 mr-2" />
              새 계약서
            </Button>
          </div>

          {/* 검색 바 */}
          <form onSubmit={handleSearch} className="flex gap-2">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                placeholder="고객명, 전화번호, 주소로 검색..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            <Button type="submit" variant="outline">
              검색
            </Button>
          </form>
        </div>

        {/* 계약서 목록 */}
        {loading ? (
          <div className="flex justify-center items-center py-12">
            <div className="text-gray-500">로딩 중...</div>
          </div>
        ) : contracts.length === 0 ? (
          <Card>
            <CardContent className="text-center py-12">
              <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">계약서가 없습니다</h3>
              <p className="text-gray-600 mb-4">첫 번째 계약서를 작성해보세요</p>
              <Button
                onClick={() => navigate('/contracts/new')}
                className="bg-blue-600 hover:bg-blue-700"
              >
                <Plus className="w-4 h-4 mr-2" />
                새 계약서 작성
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {contracts.map((contract) => {
              const status = getContractStatus(contract.start_date, contract.end_date);
              return (
                <Card
                  key={contract.id}
                  className="cursor-pointer hover:shadow-md transition-shadow"
                  onClick={() => handleContractClick(contract.id)}
                >
                  <CardContent className="p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-xl font-semibold text-gray-900">
                            {contract.customer_name}
                          </h3>
                          <Badge variant={status.variant}>{status.label}</Badge>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm text-gray-600">
                          <div className="flex items-center gap-2">
                            <Phone className="w-4 h-4" />
                            <span>{contract.customer_phone}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <MapPin className="w-4 h-4" />
                            <span className="truncate">{contract.property_address}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <Calendar className="w-4 h-4" />
                            <span>
                              {formatDate(contract.start_date)} ~ {formatDate(contract.end_date)}
                            </span>
                          </div>
                          <div className="font-semibold text-blue-600">
                            {formatPrice(contract.price)}
                          </div>
                        </div>
                        {contract.memo && (
                          <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                            <p className="text-sm text-gray-700">{contract.memo}</p>
                          </div>
                        )}
                      </div>
                    </div>
                    <div className="flex justify-between items-center text-xs text-gray-500">
                      <span>작성일: {formatDate(contract.created_at)}</span>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleContractClick(contract.id);
                        }}
                      >
                        자세히 보기
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}

        {/* 페이지네이션 */}
        {totalPages > 1 && (
          <div className="flex justify-center items-center gap-2 mt-8">
            <Button
              variant="outline"
              size="sm"
              onClick={() => fetchContracts(currentPage - 1, searchQuery)}
              disabled={currentPage === 1}
            >
              이전
            </Button>
            <span className="text-sm text-gray-600">
              {currentPage} / {totalPages}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => fetchContracts(currentPage + 1, searchQuery)}
              disabled={currentPage === totalPages}
            >
              다음
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}