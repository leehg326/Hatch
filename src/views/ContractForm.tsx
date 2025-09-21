import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import SignatureCanvas from 'react-signature-canvas';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { api } from '@/lib/api';

// 폼 검증 스키마
const contractSchema = z.object({
  customer_name: z.string().min(2, '고객명은 최소 2글자 이상이어야 합니다'),
  customer_phone: z.string().min(10, '올바른 전화번호를 입력해주세요'),
  property_address: z.string().min(5, '부동산 주소를 입력해주세요'),
  price: z.string().min(1, '임대료를 입력해주세요'),
  start_date: z.string().min(1, '시작일을 선택해주세요'),
  end_date: z.string().min(1, '종료일을 선택해주세요'),
  memo: z.string().optional(),
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
    watch,
  } = useForm<ContractFormData>({
    resolver: zodResolver(contractSchema),
  });

  const onSubmit = async (data: ContractFormData) => {
    try {
      setIsSubmitting(true);

      // 서명 데이터 가져오기
      const signatureData = signatureRef.current?.toDataURL() || '';

      // API 호출
      const response = await api.post('/contracts', {
        ...data,
        price: parseInt(data.price.replace(/,/g, '')),
        signature_data: signatureData,
      });

      if (response.data) {
        toast({
          title: '계약서가 성공적으로 저장되었습니다',
          description: '계약서 목록에서 확인할 수 있습니다.',
        });
        navigate('/contracts');
      }
    } catch (error: any) {
      toast({
        title: '오류가 발생했습니다',
        description: error.response?.data?.error || '계약서 저장에 실패했습니다.',
        variant: 'destructive',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const clearSignature = () => {
    signatureRef.current?.clear();
  };

  const formatPrice = (value: string) => {
    const numericValue = value.replace(/[^0-9]/g, '');
    return numericValue.replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">새 계약서 작성</h1>
          <p className="text-gray-600">부동산 임대차 계약서를 작성해주세요</p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-xl">고객 정보</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="customer_name">고객명 *</Label>
                  <Input
                    id="customer_name"
                    {...register('customer_name')}
                    placeholder="홍길동"
                    className="mt-1"
                  />
                  {errors.customer_name && (
                    <p className="text-sm text-red-600 mt-1">{errors.customer_name.message}</p>
                  )}
                </div>
                <div>
                  <Label htmlFor="customer_phone">연락처 *</Label>
                  <Input
                    id="customer_phone"
                    {...register('customer_phone')}
                    placeholder="010-1234-5678"
                    className="mt-1"
                  />
                  {errors.customer_phone && (
                    <p className="text-sm text-red-600 mt-1">{errors.customer_phone.message}</p>
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
              <div>
                <Label htmlFor="price">임대료 (원) *</Label>
                <Input
                  id="price"
                  {...register('price')}
                  placeholder="1,000,000"
                  className="mt-1"
                  onChange={(e) => {
                    const formatted = formatPrice(e.target.value);
                    e.target.value = formatted;
                  }}
                />
                {errors.price && (
                  <p className="text-sm text-red-600 mt-1">{errors.price.message}</p>
                )}
              </div>
            </CardContent>
          </Card>

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
                <div>
                  <Label htmlFor="end_date">종료일 *</Label>
                  <Input
                    id="end_date"
                    type="date"
                    {...register('end_date')}
                    className="mt-1"
                  />
                  {errors.end_date && (
                    <p className="text-sm text-red-600 mt-1">{errors.end_date.message}</p>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-xl">특이사항</CardTitle>
            </CardHeader>
            <CardContent>
              <div>
                <Label htmlFor="memo">메모</Label>
                <Textarea
                  id="memo"
                  {...register('memo')}
                  placeholder="계약 관련 특이사항을 입력해주세요"
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
