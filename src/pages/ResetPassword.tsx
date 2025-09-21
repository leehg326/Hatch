import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { Loader2, Eye, EyeOff, CheckCircle, XCircle } from 'lucide-react'

// Hatch 로고 컴포넌트
const HatchLogo = () => (
  <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
    <rect width="32" height="32" rx="8" fill="#4F46E5"/>
    <path d="M8 12h16v2H8v-2zm0 4h16v2H8v-2zm0 4h12v2H8v-2z" fill="white"/>
  </svg>
)

export default function ResetPassword() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [token, setToken] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [isSuccess, setIsSuccess] = useState(false)
  const [error, setError] = useState('')
  const [passwordError, setPasswordError] = useState('')
  const [confirmError, setConfirmError] = useState('')

  useEffect(() => {
    const tokenParam = searchParams.get('token')
    if (!tokenParam) {
      setError('유효하지 않은 재설정 링크입니다.')
      return
    }
    setToken(tokenParam)
  }, [searchParams])

  const validatePassword = (password: string) => {
    if (password.length < 8) {
      return '비밀번호는 최소 8자 이상이어야 합니다'
    }
    if (!/(?=.*[a-zA-Z])(?=.*\d)/.test(password)) {
      return '비밀번호는 숫자와 문자를 포함해야 합니다'
    }
    return null
  }

  const handlePasswordChange = (value: string) => {
    setNewPassword(value)
    setPasswordError(validatePassword(value) || '')
  }

  const handleConfirmPasswordChange = (value: string) => {
    setConfirmPassword(value)
    if (value && newPassword !== value) {
      setConfirmError('비밀번호가 일치하지 않습니다')
    } else {
      setConfirmError('')
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    // Validation
    const passwordValidation = validatePassword(newPassword)
    if (passwordValidation) {
      setPasswordError(passwordValidation)
      return
    }

    if (newPassword !== confirmPassword) {
      setConfirmError('비밀번호가 일치하지 않습니다')
      return
    }

    setIsLoading(true)

    try {
      const response = await fetch('/auth/email/reset', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          token,
          new_password: newPassword
        })
      })

      const data = await response.json()

      if (response.ok) {
        setIsSuccess(true)
        // Redirect to login after 3 seconds
        setTimeout(() => {
          navigate('/email-login')
        }, 3000)
      } else {
        setError(data.error || '비밀번호 재설정에 실패했습니다.')
      }
    } catch (error) {
      setError('네트워크 오류가 발생했습니다.')
    } finally {
      setIsLoading(false)
    }
  }

  if (isSuccess) {
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
                  비밀번호 재설정 완료
                </h2>
              </div>

              {/* 성공 메시지 */}
              <div className="text-center">
                <CheckCircle className="h-16 w-16 text-green-600 mx-auto mb-4" />
                <p className="text-green-600 font-medium mb-4">
                  비밀번호가 성공적으로 재설정되었습니다!
                </p>
                <p className="text-sm text-gray-500 mb-6">
                  잠시 후 로그인 페이지로 이동합니다.
                </p>

                <button
                  onClick={() => navigate('/email-login')}
                  className="w-full h-14 rounded-full bg-blue-600 hover:bg-blue-700 text-white font-bold text-base transition-all duration-200"
                >
                  로그인 페이지로 이동
                </button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  if (error && !token) {
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
                  오류
                </h2>
              </div>

              {/* 에러 메시지 */}
              <div className="text-center">
                <XCircle className="h-16 w-16 text-red-600 mx-auto mb-4" />
                <p className="text-red-600 font-medium mb-4">{error}</p>
                <button
                  onClick={() => navigate('/email-login')}
                  className="text-sm text-blue-600 hover:text-blue-800 underline"
                >
                  로그인 페이지로 돌아가기
                </button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

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
                새 비밀번호 설정
              </h2>
              <h3 className="text-gray-600">
                새로운 비밀번호를 입력해주세요.
              </h3>
            </div>

            {/* 폼 */}
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="new-password">새 비밀번호</Label>
                <div className="relative">
                  <Input
                    id="new-password"
                    type={showPassword ? "text" : "password"}
                    placeholder="새 비밀번호를 입력하세요"
                    value={newPassword}
                    onChange={(e) => handlePasswordChange(e.target.value)}
                    className="h-12 rounded-xl border-gray-200 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 pr-12"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                  </button>
                </div>
                {passwordError && (
                  <p className="text-sm text-red-500">{passwordError}</p>
                )}
                {newPassword && !passwordError && (
                  <p className="text-sm text-green-600">✓ 비밀번호가 유효합니다</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="confirm-password">비밀번호 확인</Label>
                <div className="relative">
                  <Input
                    id="confirm-password"
                    type={showPassword ? "text" : "password"}
                    placeholder="비밀번호를 다시 입력하세요"
                    value={confirmPassword}
                    onChange={(e) => handleConfirmPasswordChange(e.target.value)}
                    className="h-12 rounded-xl border-gray-200 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 pr-12"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                  </button>
                </div>
                {confirmError && (
                  <p className="text-sm text-red-500">{confirmError}</p>
                )}
                {confirmPassword && !confirmError && newPassword === confirmPassword && (
                  <p className="text-sm text-green-600">✓ 비밀번호가 일치합니다</p>
                )}
              </div>

              {error && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-sm text-red-600">{error}</p>
                </div>
              )}

              <Button
                type="submit"
                disabled={isLoading || !!passwordError || !!confirmError || !newPassword || !confirmPassword}
                className="w-full h-14 rounded-full bg-blue-600 hover:bg-blue-700 text-white font-bold text-base transition-all duration-200"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    재설정 중...
                  </>
                ) : (
                  '비밀번호 재설정'
                )}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}




