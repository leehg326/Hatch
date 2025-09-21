import { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Card, CardContent } from '@/components/ui/card'
import { Loader2, CheckCircle, XCircle } from 'lucide-react'

// Hatch 로고 컴포넌트
const HatchLogo = () => (
  <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
    <rect width="32" height="32" rx="8" fill="#4F46E5"/>
    <path d="M8 12h16v2H8v-2zm0 4h16v2H8v-2zm0 4h12v2H8v-2z" fill="white"/>
  </svg>
)

export default function VerifyEmail() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [message, setMessage] = useState('')

  useEffect(() => {
    const token = searchParams.get('token')
    
    if (!token) {
      setStatus('error')
      setMessage('인증 토큰이 없습니다.')
      return
    }

    // Verify email
    const verifyEmail = async () => {
      try {
        const response = await fetch('/auth/email/verify', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ token })
        })

        const data = await response.json()

        if (response.ok) {
          setStatus('success')
          setMessage('이메일이 성공적으로 인증되었습니다!')
          // Redirect to login after 3 seconds
          setTimeout(() => {
            navigate('/email-login')
          }, 3000)
        } else {
          setStatus('error')
          setMessage(data.error || '이메일 인증에 실패했습니다.')
        }
      } catch (error) {
        setStatus('error')
        setMessage('네트워크 오류가 발생했습니다.')
      }
    }

    verifyEmail()
  }, [searchParams, navigate])

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-[420px]">
        <Card className="bg-white rounded-2xl shadow-md border-0 overflow-hidden">
          <CardContent className="p-8">
            {/* 헤더 영역 */}
            <div className="text-center mb-8">
              <div className="flex items-center justify-center gap-3 mb-4">
                <HatchLogo />
                <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-[#4F46E5] via-[#6366F1] to-[#06B6D4]">
                  Hatch
                </h1>
              </div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                이메일 인증
              </h2>
            </div>

            {/* 상태 표시 */}
            <div className="text-center">
              {status === 'loading' && (
                <>
                  <Loader2 className="h-16 w-16 text-blue-600 animate-spin mx-auto mb-4" />
                  <p className="text-gray-600">이메일을 인증하는 중입니다...</p>
                </>
              )}

              {status === 'success' && (
                <>
                  <CheckCircle className="h-16 w-16 text-green-600 mx-auto mb-4" />
                  <p className="text-green-600 font-medium mb-4">{message}</p>
                  <p className="text-sm text-gray-500">잠시 후 로그인 페이지로 이동합니다.</p>
                </>
              )}

              {status === 'error' && (
                <>
                  <XCircle className="h-16 w-16 text-red-600 mx-auto mb-4" />
                  <p className="text-red-600 font-medium mb-4">{message}</p>
                  <button
                    onClick={() => navigate('/email-login')}
                    className="text-sm text-blue-600 hover:text-blue-800 underline"
                  >
                    로그인 페이지로 돌아가기
                  </button>
                </>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}




