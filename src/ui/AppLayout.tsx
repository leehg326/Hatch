import { Outlet } from 'react-router-dom'
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet'
import { Button } from '@/components/ui/button'
import Sidebar from '@/components/Sidebar'

function Topbar() {
  return (
    <header className="sticky top-0 z-30 h-16 flex items-center justify-center px-4 bg-transparent border-none shadow-none outline-none">
      <div className="md:hidden">
        <Sheet>
          <SheetTrigger asChild>
            <Button variant="outline" size="sm" className="rounded-xl">메뉴</Button>
          </SheetTrigger>
          <SheetContent side="left" className="p-0 w-72">
            <Sidebar />
          </SheetContent>
        </Sheet>
      </div>
    </header>
  )
}

export default function AppLayout() {
  return (
    <div className="min-h-screen grid md:grid-cols-[16rem_1fr] bg-gray-50">
      <Sidebar />
      <div className="flex flex-col bg-white/50 min-h-screen">
        <Topbar />
        <main className="flex-1 p-4 md:p-6 pb-8 pt-0">
          <div className="mx-auto max-w-7xl">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}


