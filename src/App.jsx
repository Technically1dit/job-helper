import { Routes, Route } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'

import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Jobs from './pages/Jobs'
import JobDetail from './pages/JobDetail'
import Profile from './pages/Profile'
import Gmail from './pages/Gmail'
import Applications from './pages/Applications'
import ApplicationGenerator from './pages/ApplicationGenerator'

function App() {
  const { user, loading } = useAuth()
  
  if (loading) return <div className="h-screen w-full flex items-center justify-center">Loading...</div>
  if (!user) return <Login />

  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="jobs" element={<Jobs />} />
        <Route path="jobs/:id" element={<JobDetail />} />
        <Route path="jobs/:id/application" element={<ApplicationGenerator />} />
        <Route path="applications" element={<Applications />} />
        <Route path="profile" element={<Profile />} />
        <Route path="gmail" element={<Gmail />} />
      </Route>
    </Routes>
  )
}

export default App
