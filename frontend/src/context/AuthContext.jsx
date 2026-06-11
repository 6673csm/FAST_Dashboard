import { createContext, useContext, useState, useCallback } from 'react'
import client from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem('fast_user')) } catch { return null }
  })

  const login = useCallback(async (username, password) => {
    const params = new URLSearchParams({ username, password })
    const { data } = await client.post('/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    localStorage.setItem('fast_token', data.access_token)
    localStorage.setItem('fast_user', JSON.stringify({ username: data.username }))
    setUser({ username: data.username })
    return data
  }, [])

  const register = useCallback(async (username, email, password) => {
    const { data } = await client.post('/auth/register', { username, email, password })
    return data
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('fast_token')
    localStorage.removeItem('fast_user')
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
