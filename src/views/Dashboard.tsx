import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { FileText, UserPlus, CalendarPlus, FileSignature, CalendarClock, Files, Clock3 } from 'lucide-react'
import { Link } from 'react-router-dom'
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts'
import { format } from 'date-fns'
import { ko } from 'date-fns/locale'
import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
// import { getCurrentUser } from '@/lib/user'
// @ts-ignore
import { useAuth } from '@/auth/AuthProvider.tsx'
// @ts-ignore
import Greeting from '@/components/Greeting'

const chartData = [
  { name: '1월', value: 10 },
  { name: '2월', value: 12 },
  { name: '3월', value: 8 },
  { name: '4월', value: 15 },
  { name: '5월', value: 18 },
  { name: '6월', value: 20 },
]

export default function Dashboard() {
  const [contractStats, setContractStats] = useState({
    total: 0,
    pending: 0,
    recent: []
  })
  const [loading, setLoading] = useState(true)

  const today = format(new Date(), "yyyy년 M월 d일", { locale: ko })
  

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await api.get('/contracts?per_page=5')
        if (response.data) {
          const contracts = response.data.contracts || response.data.items || [];
          setContractStats({
            total: response.data.total || 0,
            pending: contracts.filter((c: any) => {
              const endDate = new Date(c.end_date)
              const now = new Date()
              return endDate > now
            }).length,
            recent: contracts.slice(0, 3)
          })
        }
      } catch (error) {
        console.error('Failed to fetch contract stats:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

  const activities = [
    ...contractStats.recent.map((contract: any, _: number) => ({
      id: `contract-${contract.id}`,
      icon: FileText,
      text: `새 계약서가 생성되었습니다 (${contract.customer_name}님 - ${contract.property_address})`,
      time: format(new Date(contract.created_at), 'MM월 dd일 HH:mm', { locale: ko })
    })),
    { id: 'a2', icon: FileSignature, text: '계약서 서명이 요청되었습니다 (박영희님 - 전세)', time: '오늘 09:40' },
    { id: 'a3', icon: CalendarClock, text: '내일 14:00 매물 미팅 일정이 등록되었습니다', time: '어제 17:30' },
  ].slice(0, 3)

  return (
    <div className="w-full space-y-6">
      {/* Header */}
      <div className="rounded-2xl bg-white shadow-sm p-6 md:p-8 border border-gray-100">
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900">
              <Greeting />
            </h1>
            <p className="text-gray-600 mt-2 text-lg">오늘의 업무를 한눈에 확인하세요</p>
          </div>
          <Badge variant="secondary" className="rounded-xl text-gray-700 bg-gray-100 px-4 py-2 text-sm font-medium">{today}</Badge>
        </div>
      </div>

      {/* Action Cards */}
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <Link to="/contracts" className="block group">
          <Card className="rounded-2xl shadow-sm hover:shadow-lg transition-all duration-300 group-hover:scale-[1.02] border border-gray-100">
            <CardContent className="p-6 flex items-center gap-4">
              <div className="h-12 w-12 rounded-xl bg-blue-100 flex items-center justify-center text-blue-600 group-hover:bg-blue-200 transition-colors">
                <FileText size={20} />
              </div>
              <div>
                <div className="text-sm text-gray-500">문서</div>
                <div className="font-semibold text-gray-900">계약서</div>
              </div>
            </CardContent>
          </Card>
        </Link>
        <Link to="/clients" className="block group">
          <Card className="rounded-2xl shadow-sm hover:shadow-lg transition-all duration-300 group-hover:scale-[1.02] border border-gray-100">
            <CardContent className="p-6 flex items-center gap-4">
              <div className="h-12 w-12 rounded-xl bg-green-100 flex items-center justify-center text-green-600 group-hover:bg-green-200 transition-colors">
                <UserPlus size={20} />
              </div>
              <div>
                <div className="text-sm text-gray-500">고객</div>
                <div className="font-semibold text-gray-900">고객 등록</div>
              </div>
            </CardContent>
          </Card>
        </Link>
        <Link to="/schedule" className="block group">
          <Card className="rounded-2xl shadow-sm hover:shadow-lg transition-all duration-300 group-hover:scale-[1.02] border border-gray-100">
            <CardContent className="p-6 flex items-center gap-4">
              <div className="h-12 w-12 rounded-xl bg-purple-100 flex items-center justify-center text-purple-600 group-hover:bg-purple-200 transition-colors">
                <CalendarPlus size={20} />
              </div>
              <div>
                <div className="text-sm text-gray-500">일정</div>
                <div className="font-semibold text-gray-900">일정 추가</div>
              </div>
            </CardContent>
          </Card>
        </Link>
      </div>

      {/* Stats + Chart + Activity */}
      <div className="space-y-6">
        <div className="grid gap-6 md:grid-cols-3">
          <Card className="rounded-2xl shadow-sm border border-gray-100">
            <CardContent className="p-6 flex items-center justify-between">
              <div>
                <div className="text-sm text-gray-500">총 계약서</div>
                <div className="text-3xl font-bold text-gray-900">
                  {loading ? '...' : contractStats.total}
                </div>
              </div>
              <div className="h-12 w-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center"><Files size={20}/></div>
            </CardContent>
          </Card>
          <Card className="rounded-2xl shadow-sm border border-gray-100">
            <CardContent className="p-6 flex items-center justify-between">
              <div>
                <div className="text-sm text-gray-500">진행 중인 계약</div>
                <div className="text-3xl font-bold text-gray-900">
                  {loading ? '...' : contractStats.pending}
                </div>
              </div>
              <div className="h-12 w-12 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center"><FileSignature size={20}/></div>
            </CardContent>
          </Card>
          <Card className="rounded-2xl shadow-sm border border-gray-100">
            <CardContent className="p-6 flex items-center justify-between">
              <div>
                <div className="text-sm text-gray-500">예정된 일정</div>
                <div className="text-3xl font-bold text-gray-900">0</div>
              </div>
              <div className="h-12 w-12 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center"><CalendarClock size={20}/></div>
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          <Card className="rounded-2xl shadow-sm lg:col-span-2 border border-gray-100">
            <CardHeader className="pb-4">
              <CardTitle className="text-lg font-semibold">월별 계약 건수</CardTitle>
            </CardHeader>
            <CardContent className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="name" stroke="#64748b" />
                  <YAxis stroke="#64748b" />
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: 'white',
                      border: '1px solid #e2e8f0',
                      borderRadius: '12px',
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                    }}
                  />
                  <Line type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={3} dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
          <Card className="rounded-2xl shadow-sm border border-gray-100">
            <CardHeader className="pb-4">
              <CardTitle className="text-lg font-semibold">최근 활동</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-4">
                {activities.map(a => (
                  <li key={a.id} className="flex items-start gap-3">
                    <div className="h-10 w-10 rounded-xl bg-gray-100 text-gray-700 flex items-center justify-center mt-0.5">
                      <a.icon size={18} />
                    </div>
                    <div className="flex-1">
                      <div className="text-sm text-gray-700 leading-relaxed">{a.text}</div>
                      <div className="text-xs text-gray-500 flex items-center gap-1 mt-2">
                        <Clock3 size={12}/> {a.time}
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}


