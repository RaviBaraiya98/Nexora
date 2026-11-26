import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { ROUTE_PATHS } from '@/constants/route-paths'
import { useAuth } from '@/context/auth-context'
import { usePageTitle } from '@/hooks/use-page-title'
import { zodResolver } from '@hookform/resolvers/zod'
import { motion } from 'framer-motion'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link } from 'react-router-dom'
import { z } from 'zod'

const loginSchema = z.object({
  email: z.string().email('Enter a valid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
})

export function LoginPage() {
  usePageTitle('Login')
  const form = useForm({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: '', password: '' },
  })
  const { login } = useAuth()
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function handleLogin(values) {
    setError('')
    setSubmitting(true)
    try { await login(values); window.location.href = ROUTE_PATHS.DASHBOARD } catch (requestError) { setError(requestError.message) } finally { setSubmitting(false) }
  }

  return (
    <div className="mx-auto flex min-h-[80vh] max-w-6xl items-center px-4 pb-16 lg:px-8">
      <div className="grid w-full max-w-5xl gap-12 lg:grid-cols-[1fr_0.75fr] lg:items-center">
      <div className="hidden lg:block"><p className="eyebrow">Nexora / secure workspace</p><h1 className="mt-5 max-w-xl font-display text-6xl leading-none text-foreground">Return to the work that makes you ready.</h1><p className="mt-6 max-w-md text-sm leading-7 text-muted-foreground">Your interviews, evidence, gaps, and next practice step stay connected in one career intelligence workspace.</p></div>
      <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} className="w-full">
      <Card className="mx-auto w-full max-w-md">
        <CardHeader>
          <CardTitle>Welcome back to Nexora</CardTitle>
        </CardHeader>
        <CardContent>
          <form className="space-y-4" onSubmit={form.handleSubmit(handleLogin)}>
            <div className="space-y-1">
              <label className="text-sm text-muted-foreground">Email</label>
              <Input placeholder="name@university.edu" {...form.register('email')} />
            </div>
            <div className="space-y-1">
              <label className="text-sm text-muted-foreground">Password</label>
              <Input type="password" placeholder="Your password" {...form.register('password')} />
            </div>
            {error ? <p className="text-xs text-accent">{error}</p> : null}
            <Button className="w-full" disabled={submitting}>{submitting ? 'Connecting...' : 'Sign In'}</Button>
            <p className="text-xs text-muted-foreground">
              New here? <Link to={ROUTE_PATHS.REGISTER} className="text-accent">Create an account</Link>
            </p>
          </form>
        </CardContent>
      </Card>
      </motion.div>
      </div>
    </div>
  )
}
