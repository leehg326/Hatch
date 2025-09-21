export default function NotFound() {
  return (
    <div className="min-h-screen grid place-items-center p-6">
      <div className="text-center space-y-4">
        <div className="text-3xl font-bold">페이지를 찾을 수 없습니다</div>
        <div className="text-muted-foreground">요청하신 페이지가 존재하지 않거나 이동되었어요.</div>
        <div className="flex items-center justify-center gap-3">
          <a href="/" className="px-4 py-2 rounded-md bg-gray-900 text-white">대시보드로 이동</a>
          <a href="/auth" className="px-4 py-2 rounded-md border">로그인으로 이동</a>
        </div>
      </div>
    </div>
  )
}











