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

const registerSchema = z.object({
  name: z.string().min(2, 'Name is required'),
  email: z.string().email('Enter a valid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
})

export function RegisterPage() {
  usePageTitle('Register')
  const form = useForm({
    resolver: zodResolver(registerSchema),
    defaultValues: { name: '', email: '', password: '' },
  })
  const { register: registerAccount } = useAuth()
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function handleRegister(values) {
    setError('')
    setSubmitting(true)
    try { await registerAccount(values); window.location.href = ROUTE_PATHS.DASHBOARD } catch (requestError) { setError(requestError.message) } finally { setSubmitting(false) }
  }

  return (
    <div className="mx-auto flex min-h-[80vh] max-w-6xl items-center px-4 pb-16 lg:px-8">
      <div className="grid w-full max-w-5xl gap-12 lg:grid-cols-[1fr_0.75fr] lg:items-center">
      <div className="hidden lg:block"><p className="eyebrow">Nexora / first signal</p><h1 className="mt-5 max-w-xl font-display text-6xl leading-none text-foreground">Start with one honest interview.</h1><p className="mt-6 max-w-md text-sm leading-7 text-muted-foreground">Nexora turns your answer into a clearer preparation path. Begin with a profile, choose a target, and let the evidence guide the next step.</p></div>
      <motion.div initial={{ opacity: 0, y: 14 }} animate={{ opacity: 1, y: 0 }} className="w-full">
      <Card className="mx-auto w-full max-w-md">
        <CardHeader>
          <CardTitle>Create your Nexora workspace</CardTitle>
        </CardHeader>
        <CardContent>
          <form className="space-y-4" onSubmit={form.handleSubmit(handleRegister)}>
            <div className="space-y-1">
              <label className="text-sm text-muted-foreground">Full name</label>
              <Input placeholder="Alex Morgan" {...form.register('name')} />
            </div>
            <div className="space-y-1">
              <label className="text-sm text-muted-foreground">Email</label>
              <Input placeholder="name@university.edu" {...form.register('email')} />
            </div>
            <div className="space-y-1">
              <label className="text-sm text-muted-foreground">Password</label>
              <Input type="password" placeholder="Create a password" {...form.register('password')} />
            </div>
            {error ? <p className="text-xs text-accent">{error}</p> : null}
            <Button className="w-full" disabled={submitting}>{submitting ? 'Creating workspace...' : 'Create Account'}</Button>
            <p className="text-xs text-muted-foreground">
              Already have an account? <Link to={ROUTE_PATHS.LOGIN} className="text-accent">Sign in</Link>
            </p>
          </form>
        </CardContent>
      </Card>
      </motion.div>
      </div>
    </div>
  )
}
