import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import SignatureCanvas from 'react-signature-canvas';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { api } from '@/lib/api';

// 통합 스키마 (모든 필드를 optional로 하고 런타임에서 검증)
const contractSchema = z.object({
  type: z.enum(['SALE', 'JEONSE', 'WOLSE']),
  seller_name: z.string().min(2, '매도인/임대인 이름은 최소 2글자 이상이어야 합니다'),
  seller_phone: z.string().min(10, '매도인/임대인 전화번호를 입력해주세요'),
  buyer_name: z.string().min(2, '매수인/임차인 이름은 최소 2글자 이상이어야 합니다'),
  buyer_phone: z.string().min(10, '매수인/임차인 전화번호를 입력해주세요'),
  property_address: z.string().min(5, '부동산 주소를 입력해주세요'),
  // 타입별 금액 필드 (모두 optional)
  sale_price: z.string().optional(),
  deposit: z.string().optional(),
  monthly_rent: z.string().optional(),
  monthly_payday: z.number().min(1).max(31).optional(),
  // 날짜 필드
  contract_date: z.string().optional(),
  handover_date: z.string().optional(),
  special_terms: z.string().optional(),
}).refine((data) => {
  // 런타임에서 타입별 검증
  if (data.type === 'SALE') {
    if (!data.sale_price || data.sale_price.trim() === '') {
      return false;
    }
    const num = parseInt(data.sale_price.replace(/,/g, ''));
    return !isNaN(num) && num > 0;
  }
  if (data.type === 'JEONSE') {
    if (!data.deposit || data.deposit.trim() === '') {
      return false;
    }
    const num = parseInt(data.deposit.replace(/,/g, ''));
    return !isNaN(num) && num > 0;
  }
  if (data.type === 'WOLSE') {
    if (!data.deposit || data.deposit.trim() === '' || !data.monthly_rent || data.monthly_rent.trim() === '') {
      return false;
    }
    const depositNum = parseInt(data.deposit.replace(/,/g, ''));
    const rentNum = parseInt(data.monthly_rent.replace(/,/g, ''));
    return !isNaN(depositNum) && depositNum > 0 && !isNaN(rentNum) && rentNum > 0;
  }
  return true;
}, {
  message: "계약 유형에 맞는 필수 필드를 입력해주세요",
  path: ["type"]
});

type ContractFormData = z.infer<typeof contractSchema>;

export default function ContractForm() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const signatureRef = useRef<SignatureCanvas>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch,
    getValues,
    unregister,
    clearErrors,
  } = useForm<ContractFormData>({
    resolver: zodResolver(contractSchema),
    defaultValues: {
      type: 'SALE', // 기본값 설정
    },
  });

  const contractType = watch('type');

  // 타입 변경 시 필드 초기화
  useEffect(() => {
    if (contractType === 'SALE') {
      // 전세/월세 필드 클리어
      unregister(['deposit', 'monthly_rent', 'monthly_payday']);
      clearErrors(['deposit', 'monthly_rent', 'monthly_payday']);
    } else if (contractType === 'JEONSE') {
      // 매매/월세 필드 클리어
      unregister(['sale_price', 'monthly_rent', 'monthly_payday']);
      clearErrors(['sale_price', 'monthly_rent', 'monthly_payday']);
    } else if (contractType === 'WOLSE') {
      // 매매 필드 클리어
      unregister(['sale_price']);
      clearErrors(['sale_price']);
    }
  }, [contractType, unregister, clearErrors]);

  // 페이로드 정규화 함수 - 타입별로 정확한 필드만 전송
  const buildPayload = (data: ContractFormData) => {
    const payload: any = {
      type: data.type,
      property_address_full: data.property_address?.trim() || '',
      parties: [
        {
          role: 'SELLER',
          name: data.seller_name?.trim() || '',
          phone: data.seller_phone?.trim() || ''
        },
        {
          role: 'BUYER', 
          name: data.buyer_name?.trim() || '',
          phone: data.buyer_phone?.trim() || ''
        }
      ]
    };

    // 타입별 필수 필드만 전송 (사용하지 않는 필드는 아예 포함하지 않음)
    if (data.type === 'SALE') {
      // 매매: sale_price만 전송
      if (data.sale_price && data.sale_price.trim()) {
        payload.sale_price = Number(data.sale_price.replace(/,/g, ''));
      }
    } else if (data.type === 'JEONSE') {
      // 전세: deposit만 전송
      if (data.deposit && data.deposit.trim()) {
        payload.deposit = Number(data.deposit.replace(/,/g, ''));
      }
    } else if (data.type === 'WOLSE') {
      // 월세: deposit, monthly_rent 전송
      if (data.deposit && data.deposit.trim()) {
        payload.deposit = Number(data.deposit.replace(/,/g, ''));
      }
      if (data.monthly_rent && data.monthly_rent.trim()) {
        payload.monthly_rent = Number(data.monthly_rent.replace(/,/g, ''));
      }
      if (data.monthly_payday) {
        payload.monthly_payday = data.monthly_payday;
      }
    }

    // 날짜 필드 (ISO 형식으로 변환)
    if (data.contract_date) {
      payload.contract_date = new Date(data.contract_date).toISOString().split('T')[0]; // YYYY-MM-DD 형식
    }
    if (data.handover_date) {
      payload.handover_date = new Date(data.handover_date).toISOString().split('T')[0]; // YYYY-MM-DD 형식
    }

    // 특약사항 (선택사항)
    if (data.special_terms?.trim()) {
      payload.special_terms = data.special_terms.trim();
    }

    return payload;
  };

  const onSubmit = async (data: ContractFormData) => {
    try {
      setIsSubmitting(true);

      console.log('=== FORM SUBMISSION ===');
      console.log('Form data received:', data);
      console.log('Current form values:', getValues());
      console.log('Form errors:', errors);
      console.log('Contract type:', data.type);

      // 페이로드 정규화
      const contractData = buildPayload(data);
      console.log('Normalized payload:', contractData);
      console.log('Payload JSON:', JSON.stringify(contractData, null, 2));

      // API 호출 (Content-Type: application/json 보장)
      const response = await api.post('/contracts', contractData, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.data) {
        toast({
          title: '계약서가 성공적으로 저장되었습니다',
          description: '계약서 목록에서 확인할 수 있습니다.',
        });
        navigate('/contracts');
      }
    } catch (error: any) {
      console.error('Contract creation error:', error);
      const errorData = error.response?.data;
      
      if (errorData?.details) {
        // 새로운 validation 오류 구조
        const details = errorData.details;
        const errorMessages = Object.entries(details).map(([field, message]) => `${field}: ${message}`).join(', ');
        toast({
          title: '입력 오류',
          description: errorMessages,
          variant: 'destructive',
        });
        
        // 첫 번째 오류 필드에 포커스
        const firstErrorField = Object.keys(details)[0];
        if (firstErrorField) {
          const element = document.querySelector(`[name="${firstErrorField}"]`) as HTMLElement;
          if (element) {
            element.focus();
          }
        }
      } else {
        toast({
          title: '오류가 발생했습니다',
          description: errorData?.error || errorData?.message || '계약서 저장에 실패했습니다.',
          variant: 'destructive',
        });
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const clearSignature = () => {
    signatureRef.current?.clear();
  };

  const formatPrice = (value: string) => {
    const numericValue = (value || '').replace(/[^0-9]/g, '');
    return numericValue.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">새 계약서 작성</h1>
          <p className="text-gray-600">부동산 표준계약서를 작성해주세요</p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-xl">계약 유형</CardTitle>
            </CardHeader>
            <CardContent>
              <div>
                <Label htmlFor="type">계약 유형 *</Label>
                <Select 
                  value={watch('type')} 
                  onValueChange={(value) => setValue('type', value as any)}
                >
                  <SelectTrigger className="mt-1">
                    <SelectValue placeholder="계약 유형을 선택하세요" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="SALE">매매</SelectItem>
                    <SelectItem value="JEONSE">전세</SelectItem>
                    <SelectItem value="WOLSE">월세</SelectItem>
                    <SelectItem value="BANJEONSE">반전세</SelectItem>
                  </SelectContent>
                </Select>
                {errors.type && (
                  <p className="text-sm text-red-600 mt-1">{errors.type.message}</p>
                )}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-xl">당사자 정보</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="seller_name">매도인/임대인 이름 *</Label>
                  <Input
                    id="seller_name"
                    {...register('seller_name')}
                    placeholder="홍길동"
                    className="mt-1"
                  />
                  {errors.seller_name && (
                    <p className="text-sm text-red-600 mt-1">{errors.seller_name.message}</p>
                  )}
                </div>
                <div>
                  <Label htmlFor="seller_phone">매도인/임대인 연락처 *</Label>
                  <Input
                    id="seller_phone"
                    {...register('seller_phone')}
                    placeholder="010-1234-5678"
                    className="mt-1"
                  />
                  {errors.seller_phone && (
                    <p className="text-sm text-red-600 mt-1">{errors.seller_phone.message}</p>
                  )}
                </div>
                <div>
                  <Label htmlFor="buyer_name">매수인/임차인 이름 *</Label>
                  <Input
                    id="buyer_name"
                    {...register('buyer_name')}
                    placeholder="김철수"
                    className="mt-1"
                  />
                  {errors.buyer_name && (
                    <p className="text-sm text-red-600 mt-1">{errors.buyer_name.message}</p>
                  )}
                </div>
                <div>
                  <Label htmlFor="buyer_phone">매수인/임차인 연락처 *</Label>
                  <Input
                    id="buyer_phone"
                    {...register('buyer_phone')}
                    placeholder="010-9876-5432"
                    className="mt-1"
                  />
                  {errors.buyer_phone && (
                    <p className="text-sm text-red-600 mt-1">{errors.buyer_phone.message}</p>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-xl">부동산 정보</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="property_address">부동산 주소 *</Label>
                <Input
                  id="property_address"
                  {...register('property_address')}
                  placeholder="서울시 강남구 테헤란로 123"
                  className="mt-1"
                />
                {errors.property_address && (
                  <p className="text-sm text-red-600 mt-1">{errors.property_address.message}</p>
                )}
              </div>
              {/* 타입별 금액 필드 분기 */}
              {watch('type') === 'SALE' && (
                <div>
                  <Label htmlFor="sale_price">매매가격 (원) *</Label>
                  <Input
                    id="sale_price"
                    {...register('sale_price')}
                    placeholder="500,000,000"
                    className="mt-1"
                    onChange={(e) => {
                      const formatted = formatPrice(e.target.value);
                      e.target.value = formatted;
                    }}
                  />
                  {errors.sale_price && (
                    <p className="text-sm text-red-600 mt-1">{errors.sale_price.message}</p>
                  )}
                </div>
              )}
              
              {watch('type') === 'JEONSE' && (
                <div>
                  <Label htmlFor="deposit">전세보증금 (원) *</Label>
                  <Input
                    id="deposit"
                    {...register('deposit')}
                    placeholder="100,000,000"
                    className="mt-1"
                    onChange={(e) => {
                      const formatted = formatPrice(e.target.value);
                      e.target.value = formatted;
                    }}
                  />
                  {errors.deposit && (
                    <p className="text-sm text-red-600 mt-1">{errors.deposit.message}</p>
                  )}
                </div>
              )}
              
              {watch('type') === 'WOLSE' && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="deposit">보증금 (원) *</Label>
                    <Input
                      id="deposit"
                      {...register('deposit')}
                      placeholder="50,000,000"
                      className="mt-1"
                      onChange={(e) => {
                        const formatted = formatPrice(e.target.value);
                        e.target.value = formatted;
                      }}
                    />
                    {errors.deposit && (
                      <p className="text-sm text-red-600 mt-1">{errors.deposit.message}</p>
                    )}
                  </div>
                  <div>
                    <Label htmlFor="monthly_rent">월세 (원) *</Label>
                    <Input
                      id="monthly_rent"
                      {...register('monthly_rent')}
                      placeholder="1,000,000"
                      className="mt-1"
                      onChange={(e) => {
                        const formatted = formatPrice(e.target.value);
                        e.target.value = formatted;
                      }}
                    />
                    {errors.monthly_rent && (
                      <p className="text-sm text-red-600 mt-1">{errors.monthly_rent.message}</p>
                    )}
                  </div>
                  <div>
                    <Label htmlFor="monthly_payday">매월 지급일</Label>
                    <Input
                      id="monthly_payday"
                      type="number"
                      min="1"
                      max="31"
                      {...register('monthly_payday', { valueAsNumber: true })}
                      placeholder="1"
                      className="mt-1"
                    />
                    {errors.monthly_payday && (
                      <p className="text-sm text-red-600 mt-1">{errors.monthly_payday.message}</p>
                    )}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-xl">계약 기간</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="contract_date">계약일</Label>
                  <Input
                    id="contract_date"
                    type="date"
                    {...register('contract_date')}
                    className="mt-1"
                  />
                  {errors.contract_date && (
                    <p className="text-sm text-red-600 mt-1">{errors.contract_date.message}</p>
                  )}
                </div>
                <div>
                  <Label htmlFor="handover_date">인도일</Label>
                  <Input
                    id="handover_date"
                    type="date"
                    {...register('handover_date')}
                    className="mt-1"
                  />
                  {errors.handover_date && (
                    <p className="text-sm text-red-600 mt-1">{errors.handover_date.message}</p>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-xl">특약사항</CardTitle>
            </CardHeader>
            <CardContent>
              <div>
                <Label htmlFor="special_terms">특약사항</Label>
                <Textarea
                  id="special_terms"
                  {...register('special_terms')}
                  placeholder="계약 관련 특약사항을 입력해주세요"
                  className="mt-1"
                  rows={4}
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-xl">서명</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-4">
                  <SignatureCanvas
                    ref={signatureRef}
                    canvasProps={{
                      width: 500,
                      height: 200,
                      className: 'signature-canvas border rounded',
                    }}
                    backgroundColor="white"
                    penColor="black"
                  />
                </div>
                <div className="flex gap-2">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={clearSignature}
                    className="text-sm"
                  >
                    서명 지우기
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          <div className="flex gap-4 pt-6">
            <Button
              type="button"
              variant="outline"
              onClick={() => navigate('/contracts')}
              className="flex-1"
            >
              취소
            </Button>
            <Button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 bg-blue-600 hover:bg-blue-700"
            >
              {isSubmitting ? '저장 중...' : '계약서 저장'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
