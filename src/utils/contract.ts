import dayjs from 'dayjs';

export interface ContractSignature {
  id: number;
  role: 'SELLER' | 'BUYER' | 'AGENT';
  image_url: string;
  signed_at: string;
}

export interface Contract {
  id: number;
  type: 'SALE' | 'JEONSE' | 'WOLSE';
  status?: 'DRAFT' | 'ACTIVE' | 'EXPIRED' | 'CANCELLED';
  seller_name: string;
  seller_phone: string;
  buyer_name: string;
  buyer_phone: string;
  property_address: string;
  unit?: {
    area?: string;
    structure?: string;
  };
  price_total?: number;
  sale_price?: number;
  deposit?: number;
  monthly_rent?: number;
  monthly_payday?: number;
  mgmt_fee?: number;
  mgmt_note?: string;
  schedule?: {
    contract_date?: string;
    middle_date?: string;
    balance_date?: string;
    transfer_date?: string;
    handover_date?: string;
  };
  brokerage?: {
    office_name?: string;
    rep?: string;
    reg_no?: string;
    address?: string;
    phone?: string;
    fee?: string;
    fee_note?: string;
  };
  attachments?: {
    registry?: boolean;
    building?: boolean;
    land?: boolean;
  };
  special_terms?: string;
  doc_no: string;
  doc_hash: string;
  short_hash: string;
  created_at: string;
  updated_at: string;
  signatures?: ContractSignature[];
}

/**
 * 계약서 상태를 자동으로 계산합니다
 */
export const autoStatus = (startDate: dayjs.Dayjs, endDate: dayjs.Dayjs): 'DRAFT' | 'ACTIVE' | 'EXPIRED' | 'CANCELLED' => {
  const today = dayjs();
  
  if (!startDate.isValid() && !endDate.isValid()) return 'DRAFT';
  if (endDate.isValid() && today.isAfter(endDate, 'day')) return 'EXPIRED';
  if (startDate.isValid() && today.isBefore(startDate, 'day')) return 'DRAFT';
  
  return 'ACTIVE';
};

/**
 * 계약서 날짜를 포맷팅합니다
 */
export const formatContractDate = (dateString: string | undefined): string => {
  if (!dateString) return '미정';
  
  const date = dayjs(dateString);
  return date.isValid() ? date.format('YYYY.MM.DD') : '미정';
};

/**
 * 계약서 금액을 포맷팅합니다
 */
export const formatContractPrice = (contract: Contract): string => {
  const { type, sale_price, deposit, monthly_rent } = contract;
  
  // 매매의 경우
  if (type === 'SALE') {
    const price = Number(sale_price ?? 0);
    return price > 0 ? `${price.toLocaleString('ko-KR')}원` : '금액 미정';
  }
  
  // 전세의 경우
  if (type === 'JEONSE') {
    const depositAmount = Number(deposit ?? 0);
    return depositAmount > 0 ? `보증금 ${depositAmount.toLocaleString('ko-KR')}원` : '금액 미정';
  }
  
  // 월세의 경우
  if (type === 'WOLSE') {
    const depositAmount = Number(deposit ?? 0);
    const rentAmount = Number(monthly_rent ?? 0);
    
    if (depositAmount > 0 && rentAmount > 0) {
      return `보증금 ${depositAmount.toLocaleString('ko-KR')}원 / 월세 ${rentAmount.toLocaleString('ko-KR')}원`;
    } else if (depositAmount > 0) {
      return `보증금 ${depositAmount.toLocaleString('ko-KR')}원`;
    } else if (rentAmount > 0) {
      return `월세 ${rentAmount.toLocaleString('ko-KR')}원`;
    }
    
    return '금액 미정';
  }
  
  return '금액 미정';
};

/**
 * 계약서 상태 배지를 반환합니다
 */
export const getContractStatusBadge = (status: string) => {
  const statusMap = {
    'DRAFT': { label: '작성중', variant: 'secondary' as const },
    'ACTIVE': { label: '진행중', variant: 'default' as const },
    'EXPIRED': { label: '종료', variant: 'outline' as const },
    'CANCELLED': { label: '해지', variant: 'destructive' as const }
  };
  
  return statusMap[status as keyof typeof statusMap] || { label: status, variant: 'secondary' as const };
};

/**
 * 계약서 타입 라벨을 반환합니다
 */
export const getContractTypeLabel = (type: string): string => {
  const typeMap = {
    'SALE': '매매',
    'JEONSE': '전세',
    'WOLSE': '월세'
  };
  
  return typeMap[type as keyof typeof typeMap] || type;
};

/**
 * 계약서 기간을 포맷팅합니다
 */
export const formatContractPeriod = (contract: Contract): string => {
  const { contract_date, handover_date, schedule } = contract;
  
  // 직접 날짜 필드가 있는 경우 우선 사용
  if (contract_date || handover_date) {
    const start = formatContractDate(contract_date);
    const end = formatContractDate(handover_date);
    return `${start} ~ ${end}`;
  }
  
  // 기존 schedule 필드 호환성 유지
  if (schedule) {
    const startDate = dayjs(schedule.contract_date || schedule.middle_date);
    const endDate = dayjs(schedule.handover_date || schedule.transfer_date);
    
    const start = startDate.isValid() ? startDate.format('YYYY.MM.DD') : '미정';
    const end = endDate.isValid() ? endDate.format('YYYY.MM.DD') : '미정';
    
    return `${start} ~ ${end}`;
  }
  
  return '미정';
};
