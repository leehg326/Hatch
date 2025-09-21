import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
// import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'
import { Eye, EyeOff } from 'lucide-react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useAuth } from '../auth/AuthProvider.tsx'
import { z } from 'zod'


// Apple 아이콘 컴포넌트
const AppleIcon = ({ className = "w-5 h-5" }) => (
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
       fill="currentColor" aria-hidden="true" className={className}>
    <path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/>
  </svg>
)

// 소셜 로그인 아이콘들
const KakaoIcon = () => (
  <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
    <path d="M10 2C5.58 2 2 5.13 2 9c0 2.38 1.19 4.47 3 5.74V18l3.5-1.78c.5.08 1.02.12 1.5.12 4.42 0 8-3.13 8-7s-3.58-7-8-7z" fill="currentColor"/>
  </svg>
)

const GoogleIcon = () => (
  <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
    <path d="M19.6 10.23c0-.82-.1-1.42-.25-2.05H10v3.72h5.5c-.15.96-.74 2.36-2.1 3.28v2.71h3.4c2.01-1.85 3.2-4.58 3.2-7.66z" fill="#4285F4"/>
    <path d="M10 20c2.7 0 4.96-.89 6.6-2.42l-3.4-2.71c-.89.6-2.04.95-3.2.95-2.46 0-4.54-1.66-5.28-3.9H1.3v2.8A9.99 9.99 0 0010 20z" fill="#34A853"/>
    <path d="M4.72 11.92c-.22-.6-.35-1.24-.35-1.92s.13-1.32.35-1.92V5.28H1.3A9.99 9.99 0 000 10c0 1.61.39 3.14 1.3 4.72l3.42-2.8z" fill="#FBBC05"/>
    <path d="M10 3.98c1.39 0 2.63.48 3.6 1.42l2.7-2.7C14.96.99 12.7 0 10 0 6.09 0 2.72 2.25 1.3 5.28l3.42 2.8C5.46 5.64 7.54 3.98 10 3.98z" fill="#EA4335"/>
  </svg>
)


const FacebookIcon = () => (
  <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
    <path d="M20 10C20 4.48 15.52 0 10 0S0 4.48 0 10c0 4.84 3.44 8.87 8 9.8V13H6v-3h2V7.5C8 5.57 9.57 4 11.5 4H14v3h-2c-.55 0-1 .45-1 1v2h3v3h-3v6.95c5.05-.5 9-4.76 9-9.95z" fill="#1877F2"/>
  </svg>
)

// 소셜 로그인 버튼 컴포넌트
const SocialLoginButton = ({
  icon,
  text,
  onClick,
  variant = "outline"
}: {
  icon: React.ReactNode
  text: string
  onClick: () => void
  variant?: "default" | "outline"
}) => {
  const baseClasses = "w-full h-14 rounded-full font-semibold flex items-center justify-center gap-3 transition-all duration-200 hover:scale-[1.02] active:scale-[0.98]"

  const variantClasses = {
    default: "bg-[#FEE500] hover:brightness-95 text-black shadow-sm",
    outline: "bg-white border border-gray-200 hover:bg-gray-50 text-gray-700 shadow-sm"
  }

  return (
    <button
      onClick={onClick}
      className={`${baseClasses} ${variantClasses[variant]}`}
    >
      {icon}
      {text}
    </button>
  )
}

// 폼 스키마
const loginSchema = z.object({
  email: z.string().email('올바른 이메일을 입력해주세요.'),
  password: z.string().min(1, '비밀번호를 입력해주세요.'),
})

const registerSchema = z.object({
  name: z.string().min(2, '이름은 2자 이상이어야 합니다.'),
  email: z.string().email('올바른 이메일을 입력해주세요.'),
  password: z.string().min(8, '비밀번호는 최소 8자 이상이어야 합니다.'),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: '비밀번호가 일치하지 않습니다.',
  path: ['confirmPassword'],
})

const forgotPasswordSchema = z.object({
  email: z.string().email('올바른 이메일을 입력해주세요.'),
})

// 소셜 로그인 카드 컴포넌트
const SocialCard = ({ onSwitchToEmail }: { onSwitchToEmail: () => void }) => {
  const navigate = useNavigate()

  const handleOAuth = (provider: 'kakao' | 'google' | 'apple' | 'facebook') => {
    const apiBaseUrl = ''
    window.location.href = `${apiBaseUrl}/auth/${provider}`
  }

  return (
    <div className="w-full max-w-md mx-auto bg-white rounded-2xl p-8 shadow-[0_10px_30px_rgba(0,0,0,0.08)]">
      {/* 헤더 영역 */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-extrabold bg-gradient-to-r from-[#4F46E5] via-[#6366F1] to-[#06B6D4] bg-clip-text text-transparent mb-4">
          Hatch
        </h1>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Hatch에 오신 것을 환영합니다</h2>
        <h3 className="text-gray-700 text-lg leading-relaxed">하나의 계정으로 모든 업무를 시작하세요.</h3>
      </div>

      {/* 소셜 로그인 버튼들 */}
      <div className="space-y-3 mb-8">
        <SocialLoginButton
          icon={<KakaoIcon />}
          text="카카오톡으로 시작"
          onClick={() => handleOAuth('kakao')}
          variant="default"
        />
        <SocialLoginButton
          icon={<GoogleIcon />}
          text="Google로 시작"
          onClick={() => handleOAuth('google')}
          variant="outline"
        />
        <button
          onClick={() => handleOAuth('apple')}
          className="w-full h-14 rounded-full bg-white border border-gray-200 font-semibold hover:bg-gray-50 flex items-center justify-center gap-2 text-gray-900 transition-all duration-200 hover:scale-[1.02] active:scale-[0.98] shadow-sm"
        >
          <AppleIcon className="w-5 h-5 shrink-0" />
          Apple로 등록
        </button>
        <SocialLoginButton
          icon={<FacebookIcon />}
          text="Facebook으로 시작"
          onClick={() => handleOAuth('facebook')}
          variant="outline"
        />
      </div>

      {/* 하단 링크들 */}
      <div className="space-y-4 text-center">
        <button
          onClick={onSwitchToEmail}
          className="block w-full text-sm text-gray-500 hover:text-gray-700 transition-colors duration-200"
        >
          이메일로 로그인하기
        </button>
        <button
          onClick={() => navigate('/')}
          className="block w-full text-sm text-gray-400 hover:text-gray-600 transition-colors duration-200"
        >
          대시보드로 돌아가기
        </button>
      </div>
    </div>
  )
}

// 이메일 로그인/회원가입 카드 컴포넌트
const EmailCard = ({ onSwitchToSocial }: { onSwitchToSocial: () => void }) => {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [currentTab, setCurrentTab] = useState<'login' | 'register' | 'forgot'>('login')
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [serverError, setServerError] = useState<string | null>(null)
  const [rememberMe, setRememberMe] = useState(false)

  // 폼 설정
  const loginForm = useForm<z.infer<typeof loginSchema>>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: '', password: '' },
  })

  const registerForm = useForm<z.infer<typeof registerSchema>>({
    resolver: zodResolver(registerSchema),
    defaultValues: { name: '', email: '', password: '', confirmPassword: '' },
  })

  const forgotPasswordForm = useForm<z.infer<typeof forgotPasswordSchema>>({
    resolver: zodResolver(forgotPasswordSchema),
    defaultValues: { email: '' },
  })

  // 로그인 처리
  const handleLoginSubmit = async (data: z.infer<typeof loginSchema>) => {
    setIsLoading(true)
    setServerError(null)
    
    try {
      const result = await login(data.email, data.password, rememberMe)
      if (result.success) {
        // AuthProvider가 자동으로 사용자 상태를 업데이트하고 대시보드로 이동
        navigate('/')
      } else {
        setServerError(result.error || '로그인에 실패했습니다.')
      }
    } catch (error) {
      setServerError('네트워크 오류가 발생했습니다.')
    } finally {
      setIsLoading(false)
    }
  }

  // 회원가입 처리
  const handleRegisterSubmit = async (data: z.infer<typeof registerSchema>) => {
    setIsLoading(true)
    setServerError(null)
    
    try {
      const response = await fetch('http://127.0.0.1:5000/auth/email/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ name: data.name, email: data.email, password: data.password }),
      })
      const result = await response.json()

      if (response.ok) {
        alert('회원가입이 완료되었습니다. 이메일을 확인해주세요.')
        setCurrentTab('login')
      } else {
        setServerError(result.error || '회원가입에 실패했습니다.')
      }
    } catch (error) {
      setServerError('네트워크 오류가 발생했습니다.')
    } finally {
      setIsLoading(false)
    }
  }

  // 비밀번호 찾기 처리
  const handleForgotPasswordSubmit = async (data: z.infer<typeof forgotPasswordSchema>) => {
    setIsLoading(true)
    setServerError(null)
    
    try {
      const response = await fetch('http://127.0.0.1:5000/auth/email/forgot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(data),
      })
      const result = await response.json()

      if (response.ok) {
        alert('비밀번호 재설정 링크가 이메일로 전송되었습니다.')
        setCurrentTab('login')
      } else {
        setServerError(result.error || '비밀번호 재설정 요청에 실패했습니다.')
      }
    } catch (error) {
      setServerError('네트워크 오류가 발생했습니다.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="w-full max-w-md mx-auto bg-white rounded-2xl p-8 shadow-[0_10px_30px_rgba(0,0,0,0.08)]">

      {/* 헤더 영역 */}
      <div className="text-center mb-6">
        <h1 className="text-3xl font-extrabold bg-gradient-to-r from-[#4F46E5] via-[#6366F1] to-[#06B6D4] bg-clip-text text-transparent mb-4">
          Hatch
        </h1>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Hatch에 오신 것을 환영합니다</h2>
        <h3 className="text-gray-700 text-lg leading-relaxed">하나의 계정으로 모든 업무를 시작하세요.</h3>
      </div>

      {/* 탭 전환 */}
      <div className="flex justify-center mb-6">
        <div className="flex bg-gray-100 rounded-full p-1">
          <Button
            variant={currentTab === 'login' ? 'default' : 'ghost'}
            onClick={() => setCurrentTab('login')}
            className="rounded-full px-4 py-2 text-sm"
          >
            로그인
          </Button>
          <Button
            variant={currentTab === 'register' ? 'default' : 'ghost'}
            onClick={() => setCurrentTab('register')}
            className="rounded-full px-4 py-2 text-sm"
          >
            회원가입
          </Button>
        </div>
      </div>

      {serverError && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
          {serverError}
        </div>
      )}

      {/* 로그인 폼 */}
      {currentTab === 'login' && (
        <form onSubmit={loginForm.handleSubmit(handleLoginSubmit)} className="space-y-4">
          <div>
            <Label htmlFor="email-login">이메일</Label>
            <Input
              id="email-login"
              type="email"
              placeholder="이메일을 입력하세요"
              className="mt-1 h-12 rounded-xl border-gray-200 focus:ring-blue-500/30"
              {...loginForm.register('email')}
            />
            {loginForm.formState.errors.email && (
              <p className="mt-1 text-sm text-red-500">{loginForm.formState.errors.email.message}</p>
            )}
          </div>

          <div>
            <Label htmlFor="password-login">비밀번호</Label>
            <div className="relative mt-1">
              <Input
                id="password-login"
                type={showPassword ? "text" : "password"}
                placeholder="비밀번호를 입력하세요"
                className="h-12 rounded-xl border-gray-200 focus:ring-blue-500/30 pr-10"
                {...loginForm.register('password')}
              />
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="absolute right-2 top-1/2 -translate-y-1/2 h-8 w-8 text-gray-500"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </Button>
            </div>
            {loginForm.formState.errors.password && (
              <p className="mt-1 text-sm text-red-500">{loginForm.formState.errors.password.message}</p>
            )}
          </div>

          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center space-x-2">
              <Checkbox 
                id="remember-me" 
                checked={rememberMe}
                onCheckedChange={(checked) => setRememberMe(checked === true)}
              />
              <Label htmlFor="remember-me">자동 로그인</Label>
            </div>
            <button
              type="button"
              onClick={() => setCurrentTab('forgot')}
              className="text-gray-600 hover:text-gray-800 transition-colors text-sm"
            >
              비밀번호 찾기
            </button>
          </div>

          <Button
            type="submit"
            disabled={isLoading}
            className="w-full h-14 rounded-full text-lg font-bold bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white"
          >
            {isLoading ? '로그인 중...' : '로그인'}
          </Button>

        </form>
      )}

      {/* 회원가입 폼 */}
      {currentTab === 'register' && (
        <form onSubmit={registerForm.handleSubmit(handleRegisterSubmit)} className="space-y-4">
          <div>
            <Label htmlFor="name-register">이름</Label>
            <Input
              id="name-register"
              type="text"
              placeholder="이름을 입력하세요"
              className="mt-1 h-12 rounded-xl border-gray-200 focus:ring-blue-500/30"
              {...registerForm.register('name')}
            />
            {registerForm.formState.errors.name && (
              <p className="mt-1 text-sm text-red-500">{registerForm.formState.errors.name.message}</p>
            )}
          </div>

          <div>
            <Label htmlFor="email-register">이메일</Label>
            <Input
              id="email-register"
              type="email"
              placeholder="이메일을 입력하세요"
              className="mt-1 h-12 rounded-xl border-gray-200 focus:ring-blue-500/30"
              {...registerForm.register('email')}
            />
            {registerForm.formState.errors.email && (
              <p className="mt-1 text-sm text-red-500">{registerForm.formState.errors.email.message}</p>
            )}
          </div>

          <div>
            <Label htmlFor="password-register">비밀번호</Label>
            <div className="relative mt-1">
              <Input
                id="password-register"
                type={showPassword ? "text" : "password"}
                placeholder="최소 8자, 숫자/문자 조합"
                className="h-12 rounded-xl border-gray-200 focus:ring-blue-500/30 pr-10"
                {...registerForm.register('password')}
              />
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="absolute right-2 top-1/2 -translate-y-1/2 h-8 w-8 text-gray-500"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </Button>
            </div>
            {registerForm.formState.errors.password && (
              <p className="mt-1 text-sm text-red-500">{registerForm.formState.errors.password.message}</p>
            )}
          </div>

          <div>
            <Label htmlFor="confirm-password-register">비밀번호 확인</Label>
            <div className="relative mt-1">
              <Input
                id="confirm-password-register"
                type={showPassword ? "text" : "password"}
                placeholder="비밀번호를 다시 입력하세요"
                className="h-12 rounded-xl border-gray-200 focus:ring-blue-500/30 pr-10"
                {...registerForm.register('confirmPassword')}
              />
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="absolute right-2 top-1/2 -translate-y-1/2 h-8 w-8 text-gray-500"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </Button>
            </div>
            {registerForm.formState.errors.confirmPassword && (
              <p className="mt-1 text-sm text-red-500">{registerForm.formState.errors.confirmPassword.message}</p>
            )}
          </div>

          <Button
            type="submit"
            disabled={isLoading}
            className="w-full h-14 rounded-full text-lg font-bold bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white"
          >
            {isLoading ? '가입 중...' : '회원가입'}
          </Button>
        </form>
      )}

      {/* 비밀번호 찾기 폼 */}
      {currentTab === 'forgot' && (
        <form onSubmit={forgotPasswordForm.handleSubmit(handleForgotPasswordSubmit)} className="space-y-4">
          <div>
            <Label htmlFor="email-forgot">이메일</Label>
            <Input
              id="email-forgot"
              type="email"
              placeholder="가입한 이메일을 입력하세요"
              className="mt-1 h-12 rounded-xl border-gray-200 focus:ring-blue-500/30"
              {...forgotPasswordForm.register('email')}
            />
            {forgotPasswordForm.formState.errors.email && (
              <p className="mt-1 text-sm text-red-500">{forgotPasswordForm.formState.errors.email.message}</p>
            )}
          </div>

          <Button
            type="submit"
            disabled={isLoading}
            className="w-full h-14 rounded-full text-lg font-bold bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white"
          >
            {isLoading ? '전송 중...' : '비밀번호 재설정 링크 받기'}
          </Button>
        </form>
      )}

      {/* 하단 링크 */}
      <div className="text-center mt-6">
        <button
          onClick={onSwitchToSocial}
          className="text-sm text-gray-400 hover:text-gray-600 transition-colors duration-200"
        >
          로그인 페이지로 돌아가기
        </button>
      </div>
    </div>
  )
}

// 메인 AuthPage 컴포넌트
export default function AuthPage() {
  const [searchParams] = useSearchParams()
  const [mode, setMode] = useState<'social' | 'email'>('social')

  // URL 쿼리로 강제 진입 허용
  useEffect(() => {
    const urlMode = searchParams.get('mode')
    if (urlMode === 'email') {
      setMode('email')
    } else {
      setMode('social')
    }
  }, [searchParams])

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      {mode === 'social' ? (
        <SocialCard onSwitchToEmail={() => setMode('email')} />
      ) : (
        <EmailCard onSwitchToSocial={() => setMode('social')} />
      )}
    </div>
  )
}
