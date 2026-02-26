import React, { useEffect, useState } from 'react'

const MESSAGES = [
  'Scanning your fridge…',
  'Identifying ingredients…',
  'Finding the best recipes…',
  'Almost done…',
]

export default function LoadingOverlay() {
  const [i, setI] = useState(0)

  useEffect(() => {
    const t = setInterval(() => setI(n => (n + 1) % MESSAGES.length), 1800)
    return () => clearInterval(t)
  }, [])

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center"
      style={{ backgroundColor: 'rgba(250,247,240,0.85)', backdropFilter: 'blur(6px)' }}
    >
      <div className="flex flex-col items-center gap-4">
        <div
          className="w-9 h-9 rounded-full border-2 animate-spin"
          style={{ borderColor: '#E8E4DC', borderTopColor: '#1C1B1A' }}
        />
        <p className="text-sm font-semibold" style={{ color: '#6B6560' }}>{MESSAGES[i]}</p>
      </div>
    </div>
  )
}
