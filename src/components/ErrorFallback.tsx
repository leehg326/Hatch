import { useNavigate } from 'react-router-dom'

type Props = { error?: any }

export default function ErrorFallback({ error }: Props) {
  const navigate = useNavigate()
  const isDev = import.meta.env.DEV
  return (
    <div className="min-h-screen grid place-items-center p-6">
      <div className="max-w-lg w-full space-y-4 text-center">
        <h1 className="text-2xl font-bold">문제가 발생했습니다</h1>
        <p className="text-muted-foreground">일시적인 오류가 발생했어요. 아래 버튼으로 이동해 주세요.</p>
        <div className="flex items-center justify-center gap-3">
          <button className="px-4 py-2 rounded-md bg-gray-900 text-white" onClick={() => navigate('/')}>대시보드로 이동</button>
          <button className="px-4 py-2 rounded-md border" onClick={() => navigate('/auth')}>로그인 화면 열기</button>
        </div>
        {isDev && error?.message && (
          <pre className="text-left whitespace-pre-wrap text-xs bg-gray-50 border p-3 rounded-md overflow-auto max-h-64">{String(error.message)}</pre>
        )}
      </div>
    </div>
  )
}











