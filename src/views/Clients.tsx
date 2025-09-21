import { useState } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { z } from 'zod'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Plus, Pencil, Trash2 } from 'lucide-react'

type Client = { id: string; name: string; phone: string; email?: string }
const storageKey = 'clients'
function readAll(): Client[] { const raw = localStorage.getItem(storageKey); return raw ? JSON.parse(raw) as Client[] : [] }
function writeAll(list: Client[]) { localStorage.setItem(storageKey, JSON.stringify(list)) }

const schema = z.object({ name: z.string().min(1, '이름을 입력하세요'), phone: z.string().min(1, '연락처를 입력하세요'), email: z.string().email('이메일 형식').optional() })
type FormValues = z.infer<typeof schema>

export default function Clients() {
  const qc = useQueryClient()
  const { data: clients = [] } = useQuery({ queryKey: ['clients'], queryFn: async () => readAll() })
  const upsert = useMutation({ mutationFn: async (c: Client) => { const list = readAll(); const i = list.findIndex(v => v.id===c.id); if(i>=0) list[i]=c; else list.push(c); writeAll(list)}, onSuccess: () => qc.invalidateQueries({ queryKey: ['clients'] }) })
  const remove = useMutation({ mutationFn: async (id: string) => { writeAll(readAll().filter(c=>c.id!==id)) }, onSuccess: () => qc.invalidateQueries({ queryKey: ['clients'] }) })

  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState<Client | null>(null)
  function onCreate(){ setEditing(null); setOpen(true) }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">고객</h2>
        <Button className="rounded-xl" onClick={onCreate}><Plus size={16} className="mr-2"/>새 고객</Button>
      </div>
      <Card className="rounded-2xl shadow-soft">
        <CardContent className="p-0">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 text-gray-500"><tr><th className="p-3 text-left">이름</th><th className="p-3 text-left">연락처</th><th className="p-3 text-left">이메일</th><th className="p-3 text-right">작업</th></tr></thead>
            <tbody>
              {clients.map(c=> (
                <tr key={c.id} className="border-t">
                  <td className="p-3">{c.name}</td>
                  <td className="p-3">{c.phone}</td>
                  <td className="p-3">{c.email}</td>
                  <td className="p-3 text-right">
                    <Button variant="ghost" size="sm" className="rounded-xl" onClick={()=>{setEditing(c); setOpen(true)}}><Pencil size={16}/></Button>
                    <Button variant="ghost" size="sm" className="rounded-xl" onClick={()=>remove.mutate(c.id)}><Trash2 size={16}/></Button>
                  </td>
                </tr>
              ))}
              {clients.length===0 && <tr><td colSpan={4} className="p-6 text-center text-gray-500">데이터가 없습니다</td></tr>}
            </tbody>
          </table>
        </CardContent>
      </Card>

      <ClientDialog open={open} setOpen={setOpen} editing={editing} onSave={(v)=>upsert.mutate(v)} />
    </div>
  )
}

function ClientDialog({ open, setOpen, editing, onSave }: { open: boolean; setOpen: (v: boolean)=>void; editing: Client|null; onSave: (c: Client)=>void }){
  const form = useForm<FormValues>({ resolver: zodResolver(schema), defaultValues: editing ?? { name:'', phone:'', email:'' } })
  function submit(values: FormValues){ onSave({ id: editing?.id ?? crypto.randomUUID(), ...values }); setOpen(false) }
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent className="sm:max-w-md rounded-2xl">
        <DialogHeader><DialogTitle>{editing? '고객 수정':'새 고객'}</DialogTitle></DialogHeader>
        <form className="space-y-4" onSubmit={form.handleSubmit(submit)}>
          <div className="space-y-2"><Label htmlFor="name">이름</Label><Input id="name" {...form.register('name')}/>{form.formState.errors.name && <p className="text-sm text-red-500">{form.formState.errors.name.message}</p>}</div>
          <div className="space-y-2"><Label htmlFor="phone">연락처</Label><Input id="phone" {...form.register('phone')}/>{form.formState.errors.phone && <p className="text-sm text-red-500">{form.formState.errors.phone.message}</p>}</div>
          <div className="space-y-2"><Label htmlFor="email">이메일</Label><Input id="email" type="email" {...form.register('email')}/>{form.formState.errors.email && <p className="text-sm text-red-500">{form.formState.errors.email.message}</p>}</div>
          <div className="flex justify-end gap-2"><Button type="button" variant="outline" className="rounded-xl" onClick={()=>setOpen(false)}>취소</Button><Button type="submit" className="rounded-xl">저장</Button></div>
        </form>
      </DialogContent>
    </Dialog>
  )
}



