
import { TopNav } from '@/components/layout/top-nav'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { usePageTitle } from '@/hooks/use-page-title'
import { interviewService } from '@/services/interview-service'
import { useEffect, useState } from 'react'

const metrics = [
  ['Technical relevance', 'technical_relevance'],
  ['Concept coverage', 'concept_coverage'],
  ['Answer structure', 'answer_structure'],
  ['Communication', 'communication'],
]

function FeedbackList({ title, items, emptyText }) {
  return (
    <Card>
      <CardHeader><CardTitle>{title}</CardTitle></CardHeader>
      <CardContent className="space-y-2">
        {items?.length ? items.map((item, index) => (
          <p key={`${title}-${index}`} className="border-l-2 border-accent px-3 py-2 text-sm text-muted-foreground">
            {item}
          </p>
        )) : <p className="text-sm text-muted-foreground">{emptyText}</p>}
      </CardContent>
    </Card>
  )
}

export function ReportsPage() {
  usePageTitle('Reports')

  const [reports, setReports] = useState([])
  const [interviews, setInterviews] = useState([])
  const [selectedId, setSelectedId] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    Promise.all([interviewService.reports(), interviewService.list()])
      .then(([reportResponse, interviewResponse]) => {
        const savedReports = reportResponse.reports || []
        const savedInterviews = interviewResponse.interviews || []
        setReports(savedReports)
        setInterviews(savedInterviews)

        if (savedInterviews.length) {
          setSelectedId(String(savedInterviews[0]._id))
        } else if (savedReports.length) {
          setSelectedId(String(savedReports[0].interviewId))
        }
      })
      .catch((err) => setError(err.message || 'Could not load interviews and reports.'))
      .finally(() => setLoading(false))
  }, [])

  const selectedInterview = interviews.find(
    (item) => String(item._id) === selectedId
  )
  const report = reports.find(
    (item) => String(item.interviewId) === selectedId
  )
  const analysis = report?.analysis || {}
  const answers = analysis.answers || []

  return (
    <div>
      <TopNav
        title="Interview Intelligence Reports"
        subtitle="Select an interview to review its saved report and answer-level feedback"
      />

      {loading ? (
        <div className="h-64 animate-pulse bg-muted/40" />
      ) : error ? (
        <div className="border border-dashed border-border p-10 text-center text-sm text-muted-foreground">
          {error}
        </div>
      ) : (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Your Interview History</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {interviews.length ? (
                interviews.map((item, index) => {
                  const id = String(item._id)
                  const itemReport = reports.find(
                    (saved) => String(saved.interviewId) === id
                  )
                  const active = selectedId === id

                  return (
                    <button
                      type="button"
                      key={id}
                      onClick={() => setSelectedId(id)}
                      className={`w-full rounded-lg border p-4 text-left transition ${
                        active
                          ? 'border-primary bg-muted'
                          : 'border-border hover:bg-muted/50'
                      }`}
                    >
                      <div className="flex flex-wrap items-center justify-between gap-3">
                        <div>
                          <p className="font-medium text-foreground">
                            {item.companySnapshot?.name || 'Interview'} — {item.roleSnapshot?.name || 'Role not specified'}
                          </p>
                          <p className="mt-1 text-xs text-muted-foreground">
                            {item.createdAt ? new Date(item.createdAt).toLocaleString() : `Interview ${interviews.length - index}`}
                            {' · '}{item.answeredQuestions ?? 0} / {item.totalQuestions ?? 0} answers
                          </p>
                        </div>
                        <Badge>
                          {itemReport ? 'Report available' : item.analysisStatus || item.status || 'Pending'}
                        </Badge>
                      </div>
                    </button>
                  )
                })
              ) : reports.length ? (
                reports.map((item, index) => (
                  <button
                    type="button"
                    key={item._id || item.interviewId || index}
                    onClick={() => setSelectedId(String(item.interviewId))}
                    className="w-full rounded-lg border border-border p-4 text-left hover:bg-muted/50"
                  >
                    Interview report {index + 1}
                  </button>
                ))
              ) : (
                <p className="text-sm text-muted-foreground">
                  No interviews found yet. Your interview history will appear here.
                </p>
              )}
            </CardContent>
          </Card>

          {!selectedId ? (
            <p className="text-sm text-muted-foreground">Select an interview to continue.</p>
          ) : !report ? (
            <Card>
              <CardContent className="p-6">
                <h2 className="text-lg font-semibold">
                  {selectedInterview?.companySnapshot?.name || 'Selected interview'} — Report not available yet
                </h2>
                <p className="mt-2 text-sm text-muted-foreground">
                  Interview status: {selectedInterview?.status || 'Unknown'}.
                  {selectedInterview?.analysisStatus
                    ? ` Analysis status: ${selectedInterview.analysisStatus}.`
                    : ''}
                  {' '}A report appears here once report generation succeeds.
                </p>
              </CardContent>
            </Card>
          ) : (
            <section className="space-y-5">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h2 className="font-display text-xl text-foreground">
                    {selectedInterview?.companySnapshot?.name || 'Interview'} — {selectedInterview?.roleSnapshot?.name || 'Report'}
                  </h2>
                  <p className="mt-1 text-xs text-muted-foreground">
                    {report.createdAt ? `Generated ${new Date(report.createdAt).toLocaleString()}` : 'Saved interview analysis'}
                  </p>
                </div>
                <Badge>{analysis.status || 'saved'}</Badge>
              </div>

              <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                {metrics.map(([label, key]) => {
                  const value = analysis[key]
                  const valid = value !== null && value !== undefined && Number.isFinite(Number(value))
                  return (
                    <Card key={key}>
                      <CardContent className="p-5">
                        <p className="eyebrow">{label}</p>
                        <p className="mt-3 font-data text-3xl text-foreground">
                          {valid ? `${value}%` : 'N/A'}
                        </p>
                      </CardContent>
                    </Card>
                  )
                })}
              </div>

              <p className="text-sm text-muted-foreground">
                Analyzed answers: {analysis.analyzedAnswers ?? answers.length}
                {analysis.totalAnswers != null ? ` / ${analysis.totalAnswers}` : ''}
              </p>

              <div className="grid gap-4 lg:grid-cols-2">
                <FeedbackList title="Detected concepts" items={analysis.detected} emptyText="No concepts were returned." />
                <FeedbackList title="Missing concepts" items={analysis.missing} emptyText="No missing concepts were returned." />
                <FeedbackList title="Strengths" items={analysis.strengths} emptyText="No strengths were returned." />
                <FeedbackList title="Areas to improve" items={analysis.weaknesses} emptyText="No weaknesses were returned." />
                <div className="lg:col-span-2">
                  <FeedbackList title="Recommendations" items={analysis.recommendations} emptyText="No recommendations were returned." />
                </div>
              </div>

              <Card>
                <CardHeader><CardTitle>Question-by-question feedback</CardTitle></CardHeader>
                <CardContent className="space-y-4">
                  {answers.length ? answers.map((item, index) => (
                    <div key={`${report.interviewId}-answer-${index}`} className="border border-border bg-muted/30 p-4">
                      <p className="text-sm font-medium text-foreground">
                        {index + 1}. {item.question || 'Question unavailable'}
                      </p>
                      <p className="mt-3 whitespace-pre-line text-sm leading-6 text-muted-foreground">
                        {item.answer || 'No answer text available'}
                      </p>

                      {item.analysis?.predicted_answer_quality_score != null &&
                        Number.isFinite(Number(item.analysis.predicted_answer_quality_score)) && (
                          <div className="mt-4 rounded-lg border border-border bg-background p-3">
                            <p className="eyebrow">Predicted Answer Quality Score</p>
                            <p className="mt-1 font-data text-2xl text-foreground">
                              {Number(item.analysis.predicted_answer_quality_score).toFixed(1)} <span className="text-sm text-muted-foreground">/ 90</span>
                            </p>
                            <p className="mt-1 text-xs text-muted-foreground">
                              Experimental ML estimate, not a validated interview score.
                            </p>
                          </div>
                        )}

                      {item.analysis && (
                        <div className="mt-4 flex flex-wrap gap-2">
                          {metrics.map(([label, key]) => {
                            const value = item.analysis[key]
                            const valid = value !== null && value !== undefined && Number.isFinite(Number(value))
                            return <Badge key={key}>{label}: {valid ? `${value}%` : 'N/A'}</Badge>
                          })}
                        </div>
                      )}

                      {['strengths', 'weaknesses', 'recommendations'].map((key) =>
                        item.analysis?.[key]?.length ? (
                          <div className="mt-4" key={key}>
                            <p className="eyebrow">
                              {key === 'weaknesses' ? 'Areas to improve' : key[0].toUpperCase() + key.slice(1)}
                            </p>
                            <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-muted-foreground">
                              {item.analysis[key].map((value, i) => <li key={i}>{value}</li>)}
                            </ul>
                          </div>
                        ) : null
                      )}
                    </div>
                  )) : (
                    <p className="text-sm text-muted-foreground">
                      This report does not contain saved question-level feedback.
                    </p>
                  )}
                </CardContent>
              </Card>
            </section>
          )}
        </div>
      )}
    </div>
  )
}
