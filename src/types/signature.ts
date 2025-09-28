// 서명 역할 타입 정의
export type SignatureRole = 'SELLER' | 'BUYER' | 'BROKER' | 'LESSOR' | 'LESSEE';

// 서명 데이터 구조
export interface SignatureData {
  role: SignatureRole;
  data_url: string;
  signed_at: string;
}

// 계약 유형별 서명 역할 매핑
export const getSignatureRoles = (contractType: 'SALE' | 'JEONSE' | 'WOLSE'): SignatureRole[] => {
  switch (contractType) {
    case 'SALE':
      return ['SELLER', 'BUYER', 'BROKER'];
    case 'JEONSE':
    case 'WOLSE':
      return ['LESSOR', 'LESSEE', 'BROKER'];
    default:
      return [];
  }
};

// 서명 역할을 한국어 라벨로 변환
export const getSignatureLabel = (role: SignatureRole): string => {
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
      return '중개사 서명';
    default:
      return '';
  }
};

// 서명 데이터를 정규화된 배열로 변환
export const buildSignatures = (
  contractType: 'SALE' | 'JEONSE' | 'WOLSE',
  signatures: {
    seller?: string;
    buyer?: string;
    broker?: string;
    lessor?: string;
    lessee?: string;
  }
): SignatureData[] => {
  const roles = getSignatureRoles(contractType);
  const result: SignatureData[] = [];

  roles.forEach((role) => {
    let dataUrl = '';
    
    switch (role) {
      case 'SELLER':
        dataUrl = signatures.seller || '';
        break;
      case 'BUYER':
        dataUrl = signatures.buyer || '';
        break;
      case 'LESSOR':
        dataUrl = signatures.lessor || '';
        break;
      case 'LESSEE':
        dataUrl = signatures.lessee || '';
        break;
      case 'BROKER':
        dataUrl = signatures.broker || '';
        break;
    }

    if (dataUrl && dataUrl.length > 20) {
      result.push({
        role,
        data_url: dataUrl,
        signed_at: new Date().toISOString(),
      });
    }
  });

  return result;
};

