import { TopNav } from '@/components/layout/top-nav'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useTheme } from '@/context/theme-context'
import { usePageTitle } from '@/hooks/use-page-title'
import { useState } from 'react'

export function SettingsPage() {
  usePageTitle('Settings')
  const { theme, toggleTheme } = useTheme()
  const [mailUpdates, setMailUpdates] = useState(true)

  return (
    <div>
      <TopNav title="Workspace Settings" subtitle="Tune your experience, preferences, and notification rules" />

      <div className="mb-6 border-b border-border pb-6"><p className="eyebrow">Workspace controls / preferences</p><p className="mt-3 max-w-2xl font-display text-3xl text-foreground">Keep the signal clear while you prepare.</p></div>
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Appearance</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm text-muted-foreground">
            <p><span className="eyebrow">Current theme</span><span className="ml-3 font-data text-foreground">{theme}</span></p>
            <Button variant="outline" onClick={toggleTheme}>Toggle Theme</Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Notifications</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm text-muted-foreground">
            <label className="flex items-center justify-between border border-border bg-muted/40 p-3">
              <span>Email Interview Alerts</span>
              <input type="checkbox" checked={mailUpdates} onChange={() => setMailUpdates((state) => !state)} aria-label="Email Interview Alerts" />
            </label>
            <Button variant="outline">Save Preferences</Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
