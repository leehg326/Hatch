import { useState } from 'react'
import { Calendar as RBCalendar, dateFnsLocalizer } from 'react-big-calendar'
import { format, parse, startOfWeek, getDay } from 'date-fns'
import { ko } from 'date-fns/locale'
import 'react-big-calendar/lib/css/react-big-calendar.css'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'

type Event = { id: string; title: string; start: Date; end: Date }
const storageKey = 'events'
function readAll(): Event[] { const raw = localStorage.getItem(storageKey); return raw ? (JSON.parse(raw) as any[]).map(v=>({ ...v, start: new Date(v.start), end: new Date(v.end)})) : [] }
function writeAll(list: Event[]) { localStorage.setItem(storageKey, JSON.stringify(list)) }

const locales = { 'ko': ko }
const localizer = dateFnsLocalizer({
  format,
  parse: (str: string, fmt: string) => parse(str, fmt, new Date()),
  startOfWeek: () => startOfWeek(new Date(), { weekStartsOn: 1 }),
  getDay,
  locales,
})

export default function Schedule(){
  const [events, setEvents] = useState<Event[]>(readAll())
  const [open, setOpen] = useState(false)
  const [draft, setDraft] = useState<Event | null>(null)

  function onSelectSlot(slot: any){
    setDraft({ id: crypto.randomUUID(), title: '', start: slot.start, end: slot.end })
    setOpen(true)
  }

  function onSelectEvent(e: Event){
    setDraft(e)
    setOpen(true)
  }

  function save(){
    if(!draft) return
    setEvents(prev => {
      const list = [...prev]
      const i = list.findIndex(v=>v.id===draft.id)
      if(i>=0) list[i]=draft
      else list.push(draft)
      writeAll(list)
      return list
    })
    setOpen(false)
  }

  function remove(){
    if(!draft) return
    setEvents(prev => {
      const list = prev.filter(v=>v.id!==draft.id)
      writeAll(list)
      return list
    })
    setOpen(false)
  }

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">일정</h2>
      <Card className="rounded-2xl shadow-soft">
        <CardContent className="p-3">
          <RBCalendar
            localizer={localizer}
            events={events}
            startAccessor="start"
            endAccessor="end"
            selectable
            onSelectSlot={onSelectSlot}
            onSelectEvent={(e) => onSelectEvent(e as unknown as Event)}
            style={{ height: 700 }}
            culture="ko"
            messages={{ next: '다음', previous: '이전', today: '오늘', month: '월', week: '주', day: '일', agenda: '목록' }}
          />
        </CardContent>
      </Card>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="rounded-2xl">
          <DialogHeader><DialogTitle>일정 {draft && events.some(v=>v.id===draft.id) ? '수정' : '추가'}</DialogTitle></DialogHeader>
          <div className="space-y-3">
            <div>
              <label className="block text-sm text-gray-600 mb-1">제목</label>
              <Input value={draft?.title ?? ''} onChange={(e)=>setDraft(d=>d ? { ...d, title: e.target.value } : d)} />
            </div>
            <div className="text-sm text-gray-600">{draft && `${format(draft.start, 'Pp')} - ${format(draft.end, 'Pp')}`}</div>
            <div className="flex justify-end gap-2">
              {draft && events.some(v=>v.id===draft.id) && <Button variant="outline" className="rounded-xl" onClick={remove}>삭제</Button>}
              <Button className="rounded-xl" onClick={save}>저장</Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}


