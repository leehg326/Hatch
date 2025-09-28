import { useRef, useEffect, useState } from 'react';
import SignaturePad from 'signature_pad';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Card, CardContent } from '@/components/ui/card';
import { RotateCcw, Trash2 } from 'lucide-react';

interface SignatureFieldProps {
  label: string;
  name: string;
  required?: boolean;
  height?: number;
  setValue: (name: string, value: any, options?: any) => void;
  errors: any;
  value?: string;
}

export default function SignatureField({
  label,
  name,
  required = false,
  height = 180,
  setValue,
  errors,
  value = '',
}: SignatureFieldProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const signaturePadRef = useRef<SignaturePad | null>(null);
  const [isDrawing, setIsDrawing] = useState(false);

  useEffect(() => {
    if (canvasRef.current && !signaturePadRef.current) {
      const canvas = canvasRef.current;
      
      // 캔버스 크기 설정
      const rect = canvas.getBoundingClientRect();
      const dpr = window.devicePixelRatio || 1;
      
      // 실제 크기 설정
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      
      // CSS 크기 설정
      canvas.style.width = rect.width + 'px';
      canvas.style.height = rect.height + 'px';
      
      // 컨텍스트 스케일 조정
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.scale(dpr, dpr);
      }
      
      signaturePadRef.current = new SignaturePad(canvas, {
        backgroundColor: 'rgba(255, 255, 255, 0)',
        penColor: 'rgb(0, 0, 0)',
        minWidth: 1,
        maxWidth: 3,
        throttle: 16,
        minDistance: 5,
      });

      // 서명 시작
      signaturePadRef.current.addEventListener('beginStroke', () => {
        setIsDrawing(true);
      });

      // 서명 종료
      signaturePadRef.current.addEventListener('endStroke', () => {
        setIsDrawing(false);
        if (signaturePadRef.current && !signaturePadRef.current.isEmpty()) {
          const dataURL = signaturePadRef.current.toDataURL('image/png');
          setValue(name, dataURL, { shouldValidate: true });
        }
      });

      // 기존 값이 있으면 로드
      if (value && signaturePadRef.current.isEmpty()) {
        const img = new Image();
        img.onload = () => {
          if (signaturePadRef.current) {
            const ctx = signaturePadRef.current.getContext();
            ctx.clearRect(0, 0, canvasRef.current!.width, canvasRef.current!.height);
            ctx.drawImage(img, 0, 0);
          }
        };
        img.src = value;
      }
    }

    // 윈도우 리사이즈 이벤트 리스너
    const handleResize = () => {
      if (canvasRef.current && signaturePadRef.current) {
        const canvas = canvasRef.current;
        const rect = canvas.getBoundingClientRect();
        const dpr = window.devicePixelRatio || 1;
        
        canvas.width = rect.width * dpr;
        canvas.height = rect.height * dpr;
        canvas.style.width = rect.width + 'px';
        canvas.style.height = rect.height + 'px';
        
        const ctx = canvas.getContext('2d');
        if (ctx) {
          ctx.scale(dpr, dpr);
        }
        
        signaturePadRef.current.clear();
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      if (signaturePadRef.current) {
        signaturePadRef.current.removeEventListener('beginStroke', () => {});
        signaturePadRef.current.removeEventListener('endStroke', () => {});
      }
      window.removeEventListener('resize', handleResize);
    };
  }, [name, setValue, value]);

  const clearSignature = () => {
    if (signaturePadRef.current) {
      signaturePadRef.current.clear();
      setValue(name, '', { shouldValidate: true });
    }
  };

  const undoLastStroke = () => {
    if (signaturePadRef.current) {
      const data = signaturePadRef.current.toData();
      if (data.length > 0) {
        data.pop();
        signaturePadRef.current.fromData(data);
        if (signaturePadRef.current.isEmpty()) {
          setValue(name, '', { shouldValidate: true });
        } else {
          const dataURL = signaturePadRef.current.toDataURL('image/png');
          setValue(name, dataURL, { shouldValidate: true });
        }
      }
    }
  };

  // 중첩된 필드명 처리 (예: signatures.seller)
  const getNestedError = (errors: any, fieldName: string) => {
    const keys = fieldName.split('.');
    let error = errors;
    for (const key of keys) {
      if (error && typeof error === 'object') {
        error = error[key];
      } else {
        return null;
      }
    }
    return error;
  };

  const hasError = getNestedError(errors, name);

  return (
    <Card className="w-full">
      <CardContent className="p-4">
        <div className="space-y-3">
          <Label className="text-sm font-medium">
            {label}
            {required && <span className="text-red-500 ml-1">*</span>}
          </Label>
          
          <div className="border-2 border-dashed border-gray-300 rounded-lg overflow-hidden">
            <canvas
              ref={canvasRef}
              className="w-full cursor-crosshair"
              style={{ 
                minHeight: `${height}px`,
                maxHeight: `${height}px`,
                width: '100%',
                height: `${height}px`
              }}
            />
          </div>
          
          <div className="flex gap-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={clearSignature}
              className="flex items-center gap-1"
            >
              <Trash2 className="w-3 h-3" />
              지우기
            </Button>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={undoLastStroke}
              className="flex items-center gap-1"
            >
              <RotateCcw className="w-3 h-3" />
              되돌리기
            </Button>
          </div>
          
          <p className="text-xs text-gray-500">
            서명 후 저장됩니다. 지우기는 언제든 가능합니다.
          </p>
          
          {hasError && (
            <p className="text-sm text-red-600">
              {hasError.message as string}
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
