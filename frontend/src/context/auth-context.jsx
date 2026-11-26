import { authService } from '@/services/auth-service'
import { createContext, useContext, useEffect, useMemo, useState } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(authService.user())
  const [isLoading, setIsLoading] = useState(true)
  useEffect(() => {
    let active = true
    async function restoreSession() {
      try {
        if (authService.token()) {
          try {
            const session = await authService.me()
            if (active) setUser(session.user)
          } catch {
            const session = await authService.refresh()
            if (active) setUser(session.user)
          }
        } else {
          const session = await authService.refresh()
          if (active) setUser(session.user)
        }
      } catch {
        authService.logout()
        if (active) setUser(null)
      } finally {
        if (active) setIsLoading(false)
      }
    }
    restoreSession()
    return () => { active = false }
  }, [])
  const value = useMemo(() => ({
    user,
    isLoading,
    isAuthenticated: Boolean(user && authService.token()),
    async login(input) { const session = await authService.login(input); setUser(session.user); return session },
    async register(input) { const session = await authService.register(input); setUser(session.user); return session },
    async logout() { await authService.logout(); setUser(null) },
  }), [isLoading, user])
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used inside AuthProvider')
  return context
}
