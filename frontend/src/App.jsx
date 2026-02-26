import React, { useState } from 'react'
import Landing from './Landing.jsx'
import AppPage from './AppPage.jsx'

export default function App() {
  const [page, setPage] = useState('landing')

  if (page === 'app') {
    return <AppPage onBack={() => setPage('landing')} />
  }
  return <Landing onStart={() => setPage('app')} />
}
