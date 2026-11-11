import { useEffect, useState } from 'react'
import { Menu } from 'lucide-react'
import Badge from '../ui/Badge'
import { DATA_ORIGIN } from '../../data/mockData'

function Clock() {
  const [now, setNow] = useState(() => new Date())
  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 30000)
    return () => clearInterval(id)
  }, [])
  return (
    <time dateTime={now.toISOString()} className="hidden font-mono text-sm text-text-muted sm:block">
      {now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}
    </time>
  )
}

export default function Header({ onMenu }) {
  return (
    <header className="sticky top-0 z-30 flex h-14 items-center gap-3 border-b border-navy-700 bg-navy-900/90 px-4 backdrop-blur">
      <button onClick={onMenu} aria-label="Open navigation" className="rounded-md p-2 text-text-muted hover:bg-navy-700 lg:hidden">
        <Menu className="h-5 w-5" />
      </button>
      <div className="flex-1" />
      <Badge tone="verify">Data: {DATA_ORIGIN}</Badge>
      <Clock />
    </header>
  )
}