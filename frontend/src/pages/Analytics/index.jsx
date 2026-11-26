import { TopNav } from '@/components/layout/top-nav'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { usePageTitle } from '@/hooks/use-page-title'
import { interviewService } from '@/services/interview-service'
import { useEffect, useState } from 'react'
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

export function AnalyticsPage() {
  usePageTitle('Analytics')
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)
  useEffect(() => { interviewService.reports().then((response) => setReports(response.reports || [])).catch(() => {}).finally(() => setLoading(false)) }, [])
  const progressSeries = reports.map((report, index) => ({ week: `#${index + 1}`, score: report.analysis?.technical_relevance || 0 }))

  return (
    <div>
      <TopNav title="Performance Analytics" subtitle="Visualize trend velocity and preparation consistency" />

      <div className="grid gap-4 xl:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Readiness Velocity</CardTitle>
          </CardHeader>
          <CardContent className="h-72">
            {progressSeries.length ? <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={progressSeries}>
                <defs>
                  <linearGradient id="velocity" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#5b8db8" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#5b8db8" stopOpacity={0.1} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="week" stroke="var(--muted-foreground)" />
                <YAxis stroke="var(--muted-foreground)" />
                <Tooltip />
                <Area type="monotone" dataKey="score" stroke="#5b8db8" fill="url(#velocity)" />
              </AreaChart>
            </ResponsiveContainer> : <div className="flex h-full items-center justify-center text-sm text-muted-foreground">{loading ? 'Loading your saved analytics...' : 'Complete an interview to create analytics.'}</div>}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Insight Timeline</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm text-muted-foreground">
            {reports.length ? reports.slice(0, 3).map((report, index) => <div key={report._id || index} className="rounded-xl border border-border bg-muted/40 p-3">Attempt {index + 1}: technical relevance {report.analysis?.technical_relevance || 0}%.</div>) : <div className="rounded-xl border border-dashed border-border p-3">Your saved report milestones will appear here.</div>}
          </CardContent>
        </Card>
      </div>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Improvement Timeline</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            {reports.slice(0, 3).map((report, index) => (
              <div key={report._id || index} className="relative border-l border-border pl-4">
                <p className="eyebrow">Attempt {index + 1}</p>
                <p className="mt-3 font-data text-xl text-foreground">{report.analysis?.technical_relevance || 0}%</p>
                <p className="mt-1 text-sm text-muted-foreground">Saved interview analysis</p>
                {index < 2 ? <span className="absolute -right-2 top-5 hidden h-px w-4 bg-accent md:block" /> : null}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
