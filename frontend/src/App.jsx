import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Sidebar from './components/Sidebar'

import Login from './pages/Login'
import Register from './pages/Register'
import Home from './pages/Home'
import DataExplorer from './pages/DataExplorer'
import AutoMLArena from './pages/AutoMLArena'
import ForecastEval from './pages/ForecastEval'
import PolicySimulator from './pages/PolicySimulator'
import ExplainableAI from './pages/ExplainableAI'
import GeoIntelligence from './pages/GeoIntelligence'
import ReportGenerator from './pages/ReportGenerator'

function AppLayout({ children }) {
  return (
    <div className="page-layout">
      <Sidebar />
      <main className="page-content">{children}</main>
    </div>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route path="/login"    element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Protected routes */}
          <Route path="/" element={
            <ProtectedRoute>
              <AppLayout><Home /></AppLayout>
            </ProtectedRoute>
          } />
          <Route path="/data" element={
            <ProtectedRoute>
              <AppLayout><DataExplorer /></AppLayout>
            </ProtectedRoute>
          } />
          <Route path="/automl" element={
            <ProtectedRoute>
              <AppLayout><AutoMLArena /></AppLayout>
            </ProtectedRoute>
          } />
          <Route path="/forecast" element={
            <ProtectedRoute>
              <AppLayout><ForecastEval /></AppLayout>
            </ProtectedRoute>
          } />
          <Route path="/simulator" element={
            <ProtectedRoute>
              <AppLayout><PolicySimulator /></AppLayout>
            </ProtectedRoute>
          } />
          <Route path="/explainable" element={
            <ProtectedRoute>
              <AppLayout><ExplainableAI /></AppLayout>
            </ProtectedRoute>
          } />
          <Route path="/geo" element={
            <ProtectedRoute>
              <AppLayout><GeoIntelligence /></AppLayout>
            </ProtectedRoute>
          } />
          <Route path="/report" element={
            <ProtectedRoute>
              <AppLayout><ReportGenerator /></AppLayout>
            </ProtectedRoute>
          } />

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
