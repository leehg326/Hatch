import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { api } from '@/lib/api';
import SignatureField from '@/components/contract/SignatureField';
import { getSignatureRoles } from '@/types/signature';

// Helper function to safely convert values to text
export const toText = (v: unknown): string =>
  v == null ? '' : (typeof v === 'object' ? '' : String(v));

// 계약 유형 정의 (백엔드와 일치)
type ContractType = 'SALE' | 'JEONSE' | 'WOLSE';

// 통합 스키마 (모든 필드를 optional로 하고 런타임에서 검증)
const contractSchema = z.object({
  type: z.enum(['SALE', 'JEONSE', 'WOLSE']),
  seller_name: z.string().min(2, '매도인/임대인 이름은 최소 2글자 이상이어야 합니다'),
  seller_phone: z.string().min(10, '매도인/임대인 전화번호를 입력해주세요'),
  buyer_name: z.string().min(2, '매수인/임차인 이름은 최소 2글자 이상이어야 합니다'),
  buyer_phone: z.string().min(10, '매수인/임차인 전화번호를 입력해주세요'),
  property_address: z.string().min(5, '부동산 주소를 입력해주세요'),
  start_date: z.string().min(1, '시작일을 선택해주세요'),
  special_terms: z.string().optional(),
  // 타입별 금액 필드 (모두 optional)
  price_total: z.string().optional(),
  deposit: z.string().optional(),
  monthly_rent: z.string().optional(),
  monthly_due_day: z.number().min(1).max(31).optional(),
  // 날짜 필드
  end_date: z.string().optional(),
  handover_date: z.string().optional(),
  // 서명 필드들
  signatures: z.object({
    seller: z.string().optional(),
    buyer: z.string().optional(),
    broker: z.string().optional(),
    lessor: z.string().optional(),
    lessee: z.string().optional(),
  }).optional(),
}).refine((data) => {
  // 런타임에서 타입별 검증
  if (data.type === 'SALE') {
    if (!data.price_total || data.price_total.trim() === '') {
      return false;
    }
    const num = parseInt(data.price_total.replace(/,/g, ''));
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

export default function OneClickContractForm() {
  const navigate = useNavigate();
  const { toast } = useToast();
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
      type: 'SALE',
      seller_name: '',
      seller_phone: '',
      buyer_name: '',
      buyer_phone: '',
      property_address: '',
      start_date: '',
      special_terms: '',
      signatures: {
        seller: '',
        buyer: '',
        broker: '',
        lessor: '',
        lessee: '',
      },
    },
  });

  const contractType = watch('type') as ContractType;

  // 타입 변경 시 필드 초기화
  useEffect(() => {
    console.log('=== CONTRACT TYPE CHANGED ===');
    console.log('New contract type:', contractType);
    console.log('Current form values:', getValues());
    
    if (contractType === 'SALE') {
      console.log('Clearing JEONSE/WOLSE fields');
      // 전세/월세 필드 클리어
      unregister(['deposit', 'monthly_rent', 'monthly_due_day', 'end_date']);
      clearErrors(['deposit', 'monthly_rent', 'monthly_due_day', 'end_date']);
    } else if (contractType === 'JEONSE') {
      console.log('Clearing SALE/WOLSE fields');
      // 매매/월세 필드 클리어
      unregister(['price_total', 'monthly_rent', 'monthly_due_day']);
      clearErrors(['price_total', 'monthly_rent', 'monthly_due_day']);
    } else if (contractType === 'WOLSE') {
      console.log('Clearing SALE fields');
      // 매매 필드 클리어
      unregister(['price_total']);
      clearErrors(['price_total']);
    }
    
    console.log('Form values after clearing:', getValues());
  }, [contractType, unregister, clearErrors, getValues]);

  // 페이로드 정규화 함수 - 새로운 API 구조에 맞게 수정
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

    // 계약 유형별 필수 필드 전송
    if (data.type === 'SALE') {
      // 매매: sale_price만 전송 (값이 있을 때만)
      if (data.price_total && data.price_total.trim()) {
        payload.sale_price = Number(data.price_total.replace(/,/g, ''));
      }
    } else if (data.type === 'JEONSE') {
      // 전세: deposit만 전송 (값이 있을 때만)
      if (data.deposit && data.deposit.trim()) {
        payload.deposit = Number(data.deposit.replace(/,/g, ''));
      }
    } else if (data.type === 'WOLSE') {
      // 월세: deposit, monthly_rent 전송 (값이 있을 때만)
      if (data.deposit && data.deposit.trim()) {
        payload.deposit = Number(data.deposit.replace(/,/g, ''));
      }
      if (data.monthly_rent && data.monthly_rent.trim()) {
        payload.monthly_rent = Number(data.monthly_rent.replace(/,/g, ''));
      }
      if (data.monthly_due_day) {
        payload.monthly_payday = data.monthly_due_day;
      }
    }

    // 날짜 필드 (ISO 형식으로 변환)
    if (data.start_date) {
      payload.contract_date = new Date(data.start_date).toISOString().split('T')[0]; // YYYY-MM-DD 형식
    }
    if (data.handover_date) {
      payload.handover_date = new Date(data.handover_date).toISOString().split('T')[0]; // YYYY-MM-DD 형식
    }

    // 특약사항 (선택사항)
    if (data.special_terms?.trim()) {
      payload.special_terms = data.special_terms.trim();
    }

    // 서명 데이터 추가 (유효한 서명만)
    if (data.signatures) {
      const validSignatures: any = {};
      Object.entries(data.signatures).forEach(([key, value]) => {
        if (value && typeof value === 'string' && value.length > 20) {
          validSignatures[key] = value;
        }
      });
      
      if (Object.keys(validSignatures).length > 0) {
        payload.signatures = validSignatures;
      }
    }

    return payload;
  };

  // 금액 포맷팅 함수
  const formatPrice = (value: string) => {
    const numericValue = value.replace(/[^0-9]/g, '');
    return numericValue.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  };

  const onSubmit = async (data: ContractFormData) => {
    try {
      setIsSubmitting(true);

      console.log('=== ONE-CLICK FORM SUBMISSION ===');
      console.log('Form data received:', data);
      console.log('Current form values:', getValues());
      console.log('Form errors:', errors);
      console.log('Contract type:', data.type);

      // 페이로드 정규화
      const contractData = buildPayload(data);
      console.log('Normalized payload:', contractData);
      console.log('Payload JSON:', JSON.stringify(contractData, null, 2));
      
      // 타입별 특별 디버깅
      if (data.type === 'JEONSE') {
        console.log('=== JEONSE DEBUG ===');
        console.log('deposit:', data.deposit);
        console.log('end_date:', data.end_date);
      }
      if (data.type === 'WOLSE') {
        console.log('=== WOLSE DEBUG ===');
        console.log('deposit:', data.deposit);
        console.log('monthly_rent:', data.monthly_rent);
        console.log('monthly_due_day:', data.monthly_due_day);
        console.log('end_date:', data.end_date);
      }

      // API 호출 (Content-Type: application/json 보장)
      const response = await api.post('/contracts', contractData, {
        headers: {
          'Content-Type': 'application/json',
        },
      });

      console.log('Contract created successfully:', response.data);

      toast({
        title: '계약서가 생성되었습니다',
        description: '원클릭 계약서가 성공적으로 생성되었습니다.',
      });

      // 계약서 상세 페이지로 이동
      navigate(`/contracts/${response.data.id}`);
    } catch (error: any) {
      console.error('One-click contract creation error:', error);
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
          description: errorData?.error || errorData?.message || '원클릭 계약서 저장에 실패했습니다.',
          variant: 'destructive',
        });
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900">원클릭 계약서 작성</h1>
        <p className="text-gray-600 mt-2">간편하게 계약서를 작성하고 서명까지 완료하세요</p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* 계약 유형 선택 */}
        <Card>
          <CardHeader>
            <CardTitle className="text-xl">계약 유형</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="type">계약 유형 *</Label>
                <Select
                  value={contractType}
                  onValueChange={(value: ContractType) => {
                    setValue('type', value);
                  }}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="계약 유형을 선택하세요" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="SALE">매매</SelectItem>
                    <SelectItem value="JEONSE">전세</SelectItem>
                    <SelectItem value="WOLSE">월세</SelectItem>
                  </SelectContent>
                </Select>
                {errors.type && (
                  <p className="text-sm text-red-600">{errors.type.message}</p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* 당사자 정보 */}
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
                <Label htmlFor="seller_phone">매도인/임대인 전화번호 *</Label>
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
                <Label htmlFor="buyer_phone">매수인/임차인 전화번호 *</Label>
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

        {/* 부동산 정보 */}
        <Card>
          <CardHeader>
            <CardTitle className="text-xl">부동산 정보</CardTitle>
          </CardHeader>
          <CardContent>
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
          </CardContent>
        </Card>

        {/* 계약 기간 */}
        <Card>
          <CardHeader>
            <CardTitle className="text-xl">계약 기간</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="start_date">시작일 *</Label>
                <Input
                  id="start_date"
                  type="date"
                  {...register('start_date')}
                  className="mt-1"
                />
                {errors.start_date && (
                  <p className="text-sm text-red-600 mt-1">{errors.start_date.message}</p>
                )}
              </div>
              
              {/* 전세/월세만 종료일 표시 */}
              {(contractType === 'JEONSE' || contractType === 'WOLSE') && (
                <div>
                  <Label htmlFor="end_date">종료일 *</Label>
                  <Input
                    id="end_date"
                    type="date"
                    {...register('end_date')}
                    className="mt-1"
                  />
                  {(errors as any).end_date && (
                    <p className="text-sm text-red-600 mt-1">{(errors as any).end_date?.message}</p>
                  )}
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* 금액 정보 */}
        <Card>
          <CardHeader>
            <CardTitle className="text-xl">금액 정보</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* 매매 전용 필드 */}
            {contractType === 'SALE' && (
              <div>
                <Label htmlFor="price_total">매매가격 (원) *</Label>
                <Input
                  id="price_total"
                  {...register('price_total')}
                  placeholder="300,000,000"
                  className="mt-1"
                  onChange={(e) => {
                    const formatted = formatPrice(e.target.value);
                    e.target.value = formatted;
                  }}
                />
                <p className="text-xs text-gray-500 mt-1">금액은 쉼표 없이 숫자만 입력하세요</p>
                {errors.price_total && (
                  <p className="text-sm text-red-600 mt-1">{errors.price_total.message}</p>
                )}
              </div>
            )}

            {/* 전세/월세 공통 필드 */}
            {(contractType === 'JEONSE' || contractType === 'WOLSE') && (
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
                  <p className="text-xs text-gray-500 mt-1">금액은 쉼표 없이 숫자만 입력하세요</p>
                  {(errors as any).deposit && (
                    <p className="text-sm text-red-600 mt-1">{(errors as any).deposit?.message}</p>
                  )}
                </div>
                
                {/* 월세 전용 필드 */}
                {contractType === 'WOLSE' && (
                  <>
                    <div>
                      <Label htmlFor="monthly_rent">월차임 (원) *</Label>
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
                      <p className="text-xs text-gray-500 mt-1">금액은 쉼표 없이 숫자만 입력하세요</p>
                      {(errors as any).monthly_rent && (
                        <p className="text-sm text-red-600 mt-1">{(errors as any).monthly_rent?.message}</p>
                      )}
                    </div>
                    <div>
                      <Label htmlFor="monthly_due_day">매월 지급일 *</Label>
                      <Input
                        id="monthly_due_day"
                        type="number"
                        min="1"
                        max="31"
                        {...register('monthly_due_day', { valueAsNumber: true })}
                        placeholder="1"
                        className="mt-1"
                      />
                      <p className="text-xs text-gray-500 mt-1">1~31 사이의 숫자를 입력하세요</p>
                      {(errors as any).monthly_due_day && (
                        <p className="text-sm text-red-600 mt-1">{(errors as any).monthly_due_day?.message}</p>
                      )}
                    </div>
                  </>
                )}
              </div>
            )}
          </CardContent>
        </Card>

        {/* 특약사항 */}
        <Card>
          <CardHeader>
            <CardTitle className="text-xl">특약사항</CardTitle>
          </CardHeader>
          <CardContent>
            <div>
              <Label htmlFor="special_terms">특약사항 (선택사항)</Label>
              <Textarea
                id="special_terms"
                {...register('special_terms')}
                placeholder="특별한 계약 조건이나 약속사항을 입력하세요"
                className="mt-1"
                rows={3}
              />
            </div>
          </CardContent>
        </Card>

        {/* 서명 섹션 */}
        <Card>
          <CardHeader>
            <CardTitle className="text-xl">서명</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {getSignatureRoles(contractType as any).map((role) => {
                // 역할별 한국어 라벨 매핑
                const getKoreanLabel = (role: string) => {
                  switch (role) {
                    case 'SELLER':
                      return '매도인 서명';
                    case 'BUYER':
                      return '매수인 서명';
                    case 'LESSOR':
                      return '임대인 서명';
                    case 'LESSEE':
                      return '임차인 서명';
                    case 'BROKER':
                      return '중개인 서명';
                    default:
                      return role;
                  }
                };

                return (
                  <SignatureField
                    key={role}
                    label={getKoreanLabel(role)}
                    name={`signatures.${role.toLowerCase()}`}
                    value={watch(`signatures.${role.toLowerCase()}` as any) || ''}
                    setValue={setValue as any}
                    errors={errors}
                  />
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* 제출 버튼 */}
        <div className="flex justify-center">
          <Button
            type="submit"
            disabled={isSubmitting}
            className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 text-lg"
          >
            {isSubmitting ? '계약서 생성 중...' : '계약서 생성하기'}
          </Button>
        </div>
      </form>
    </div>
  );
}