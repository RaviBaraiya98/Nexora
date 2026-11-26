import { TopNav } from '@/components/layout/top-nav'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Progress } from '@/components/ui/progress'
import { Textarea } from '@/components/ui/textarea'
import { usePageTitle } from '@/hooks/use-page-title'
import { interviewService } from '@/services/interview-service'
import { ArrowLeft, ArrowRight, Clock3, Play, RotateCcw } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { useParams } from 'react-router-dom'

const ACTIVE_KEY = 'nexora.active-interview'
const initialSetup = { company: '', role: '', jobDescription: '', difficulty: 'medium', durationMinutes: 30, questionCount: 10 }

function formatSeconds(value) { const seconds = Math.max(0, value); return `${String(Math.floor(seconds / 60)).padStart(2, '0')}:${String(seconds % 60).padStart(2, '0')}` }

export function InterviewPage() {
  usePageTitle('Interview')
  const [setup, setSetup] = useState(initialSetup)
  const [session, setSession] = useState(null)
  const [index, setIndex] = useState(0)
  const [answer, setAnswer] = useState('')
  const [status, setStatus] = useState('')
  const [loading, setLoading] = useState(false)
  const [elapsed, setElapsed] = useState(0)
  const { interviewId } = useParams()

  useEffect(() => {
    const id = interviewId || localStorage.getItem(ACTIVE_KEY)
    if (!id) return
    interviewService.get(id).then((next) => { setSession(next); setIndex(next.interview.currentQuestionIndex || 0) }).catch(() => localStorage.removeItem(ACTIVE_KEY))
  }, [interviewId])

  useEffect(() => {
    if (!session?.interview?.startedAt || session.interview.status === 'completed') return undefined
    const timer = window.setInterval(() => setElapsed(Math.floor((Date.now() - new Date(session.interview.startedAt).getTime()) / 1000)), 1000)
    return () => window.clearInterval(timer)
  }, [session?.interview?.startedAt, session?.interview?.status])

  const current = session?.questions?.[index]
  const progress = session?.interview?.totalQuestions ? (session.interview.answeredQuestions / session.interview.totalQuestions) * 100 : 0
  const answered = useMemo(() => session?.questions?.filter((item) => item.status === 'answered').length || 0, [session])

  useEffect(() => {
    setAnswer(current?.answer?.answer?.text || '')
  }, [current?._id, current?.answer?.answer?.text])

  function updateSetup(field, value) { setSetup((currentSetup) => ({ ...currentSetup, [field]: value })) }

  async function build() {
    setLoading(true); setStatus('Building interview from the knowledge base...')
    try { const next = await interviewService.build(setup); localStorage.setItem(ACTIVE_KEY, next.interview._id); setSession(next); setStatus('Interview blueprint ready.'); setIndex(0) } catch (error) { setStatus(error.message) } finally { setLoading(false) }
  }

  async function start() {
    setLoading(true); setStatus('Starting interview...')
    try { const next = await interviewService.start(session.interview._id); setSession(next); setIndex(next.interview.currentQuestionIndex || 0); setStatus('') } catch (error) { setStatus(error.message) } finally { setLoading(false) }
  }

  async function submit() {
    if (!current || !answer.trim()) { setStatus('Write an answer before submitting.') ; return }
    setLoading(true); setStatus('Saving answer...')
    try { const next = await interviewService.submitAnswer(session.interview._id, current._id, { answer: { type: 'text', text: answer }, startedAt: current.startedAt, submittedAt: new Date().toISOString() }); setSession(next); setIndex(next.interview.currentQuestionIndex || Math.min(index + 1, next.questions.length - 1)); setAnswer(''); setStatus(next.interview.status === 'completed' ? 'Interview completed.' : '') } catch (error) { setStatus(error.message) } finally { setLoading(false) }
  }

  if (!session) return <SetupView setup={setup} updateSetup={updateSetup} build={build} loading={loading} status={status} />
  if (session.interview.status === 'completed') return <CompletionView session={session} reset={() => { localStorage.removeItem(ACTIVE_KEY); setSession(null); setSetup(initialSetup); setStatus('') }} />
  if (session.interview.status === 'ready') return <BlueprintView session={session} start={start} loading={loading} status={status} />

  return <SessionView session={session} current={current} index={index} answer={answer} setAnswer={setAnswer} progress={progress} answered={answered} elapsed={elapsed} submit={submit} loading={loading} status={status} setIndex={setIndex} />
}

function SetupView({ setup, updateSetup, build, loading, status }) {
  return <div><TopNav title="Build an Interview" subtitle="Create a persistent session from Nexora's question knowledge base" /><Card className="max-w-3xl"><CardHeader><CardTitle>Interview setup</CardTitle></CardHeader><CardContent className="grid gap-5 md:grid-cols-2"><div><label className="eyebrow" htmlFor="company">Company</label><Input id="company" className="mt-2" value={setup.company} onChange={(event) => updateSetup('company', event.target.value)} placeholder="TCS or any company" /></div><div><label className="eyebrow" htmlFor="role">Role</label><Input id="role" className="mt-2" value={setup.role} onChange={(event) => updateSetup('role', event.target.value)} placeholder="Java Developer" /></div><div className="md:col-span-2"><label className="eyebrow" htmlFor="job-description">Job description <span className="normal-case tracking-normal">(optional)</span></label><Textarea id="job-description" className="mt-2" value={setup.jobDescription} onChange={(event) => updateSetup('jobDescription', event.target.value)} placeholder="Paste the role description to improve deterministic skill/topic matching." /></div><div><label className="eyebrow" htmlFor="difficulty">Difficulty</label><select id="difficulty" className="mt-2 h-11 w-full rounded-xl border border-border bg-muted/40 px-3 text-sm text-foreground" value={setup.difficulty} onChange={(event) => updateSetup('difficulty', event.target.value)}><option value="easy">Easy</option><option value="medium">Medium</option><option value="hard">Hard</option></select></div><div><label className="eyebrow" htmlFor="duration">Duration</label><select id="duration" className="mt-2 h-11 w-full rounded-xl border border-border bg-muted/40 px-3 text-sm text-foreground" value={setup.durationMinutes} onChange={(event) => updateSetup('durationMinutes', Number(event.target.value))}><option value="15">15 minutes</option><option value="30">30 minutes</option><option value="45">45 minutes</option></select></div><div><label className="eyebrow" htmlFor="question-count">Questions</label><select id="question-count" className="mt-2 h-11 w-full rounded-xl border border-border bg-muted/40 px-3 text-sm text-foreground" value={setup.questionCount} onChange={(event) => updateSetup('questionCount', Number(event.target.value))}><option value="10">10 questions</option><option value="15">15 questions</option><option value="20">20 questions</option></select></div><div className="flex items-end"><Button className="w-full" onClick={build} disabled={loading || !setup.company || !setup.role}><Play size={15} className="mr-2" />{loading ? 'Building...' : 'Build my interview'}</Button></div>{status ? <p className="md:col-span-2 text-xs text-muted-foreground">{status}</p> : null}</CardContent></Card></div>
}

function BlueprintView({ session, start, loading, status }) {
  return <div><TopNav title="Interview Blueprint" subtitle="Review the generated session before you begin" /><Card className="max-w-3xl"><CardHeader><CardTitle>{session.interview.companySnapshot.name} · {session.interview.roleSnapshot.name}</CardTitle></CardHeader><CardContent className="space-y-5"><div className="flex flex-wrap gap-2"><Badge>{session.interview.difficulty}</Badge><Badge>{session.interview.totalQuestions} questions</Badge><Badge>{session.interview.status}</Badge></div><p className="text-sm leading-6 text-muted-foreground">This session contains question snapshots from the current Nexora knowledge base. Internal reference answers and evaluation metadata are not shown during the interview.</p><div className="border border-border p-4"><p className="eyebrow">Question coverage</p><p className="mt-2 text-2xl font-data text-foreground">{session.questions.length} selected questions</p></div><Button onClick={start} disabled={loading}><Play size={15} className="mr-2" />{loading ? 'Starting...' : 'Start interview'}</Button>{status ? <p className="text-xs text-muted-foreground">{status}</p> : null}</CardContent></Card></div>
}

function SessionView({ session, current, index, answer, setAnswer, progress, answered, elapsed, submit, loading, status, setIndex }) {
  return <div><TopNav title="Mock Interview Workspace" subtitle={`${session.interview.companySnapshot.name} · ${session.interview.roleSnapshot.name}`} /><div className="grid gap-4 xl:grid-cols-[2fr_1fr]"><Card className="border-accent/30"><CardHeader><CardTitle>Question {index + 1} of {session.questions.length}</CardTitle></CardHeader><CardContent className="space-y-5"><div className="flex items-center justify-between border-b border-border pb-4"><Badge className="border-accent/30 bg-accent/10 text-accent">{current?.questionSnapshot?.type || 'technical'}</Badge><span className="font-data text-xs text-accent">{current?.questionSnapshot?.topic || current?.questionSnapshot?.skill || 'General technical'}</span></div><p className="border-l-2 border-accent bg-muted/40 p-4 font-display text-2xl leading-tight text-foreground">{current?.questionSnapshot?.text}</p><Textarea value={answer} onChange={(event) => setAnswer(event.target.value)} placeholder="Type your answer..." disabled={current?.status === 'answered'} /><div className="flex items-center justify-between"><Button variant="outline" onClick={() => setIndex((value) => Math.max(0, value - 1))} disabled={index === 0}><ArrowLeft size={16} className="mr-2" />Previous</Button><Button onClick={submit} disabled={loading || current?.status === 'answered'}>{loading ? 'Saving...' : 'Submit answer'}<ArrowRight size={16} className="ml-2" /></Button></div>{status ? <p className="text-xs text-muted-foreground">{status}</p> : null}</CardContent></Card><Card><CardHeader><CardTitle>Session progress</CardTitle></CardHeader><CardContent className="space-y-5 text-sm text-muted-foreground"><div className="flex items-center gap-2 border border-border bg-muted/40 p-3 text-foreground"><Clock3 size={16} /><span>{formatSeconds(elapsed)}</span></div><div><div className="mb-2 flex justify-between"><span>Answered</span><span className="font-data text-foreground">{answered}/{session.questions.length}</span></div><Progress value={progress} /></div><div className="flex flex-wrap gap-1">{session.questions.map((question, questionIndex) => <button key={question._id} onClick={() => setIndex(questionIndex)} className={`h-7 w-7 border text-xs ${questionIndex === index ? 'border-accent text-accent' : question.status === 'answered' ? 'border-positive text-positive' : 'border-border text-muted-foreground'}`} aria-label={`Question ${questionIndex + 1}`}>{questionIndex + 1}</button>)}</div><p className="border-t border-border pt-4">Answers are saved on the server. Refreshing this page will restore this session.</p></CardContent></Card></div></div>
}
/* 
function CompletionView({ session, reset }) {
  return <div><TopNav title="Interview Completed" subtitle="Your session is saved for future analysis" /><Card className="max-w-4xl"><CardHeader><CardTitle>{session.interview.companySnapshot.name} · {session.interview.roleSnapshot.name}</CardTitle></CardHeader><CardContent className="space-y-5"><div className="grid gap-4 sm:grid-cols-3"><div><p className="eyebrow">Questions</p><p className="mt-2 font-data text-2xl text-foreground">{session.interview.answeredQuestions}/{session.interview.totalQuestions}</p></div><div><p className="eyebrow">Duration</p><p className="mt-2 font-data text-2xl text-foreground">{formatSeconds(session.interview.durationSeconds)}</p></div><div><p className="eyebrow">Analysis</p><p className="mt-2 text-sm text-accent">AI analysis pending</p></div></div><div className="space-y-3 border-t border-border pt-5"><p className="eyebrow">Stored answers</p>{session.questions.map((question, index) => <div key={question._id} className="border border-border bg-muted/40 p-4"><div className="flex justify-between gap-4"><p className="text-sm font-medium text-foreground">{index + 1}. {question.questionSnapshot?.text}</p><span className="font-data text-xs text-muted-foreground">{formatSeconds(question.answer?.timing?.durationSeconds || 0)}</span></div><p className="mt-3 whitespace-pre-line text-sm leading-6 text-muted-foreground">{question.answer?.answer?.text || 'No answer stored'}</p></div>)}</div><p className="text-sm leading-6 text-muted-foreground">Your question snapshots, answers, timing, and role context are stored. No score has been generated.</p><Button variant="outline" onClick={reset}><RotateCcw size={15} className="mr-2" />Build another interview</Button></CardContent></Card></div>
}
 */

function CompletionView({ session, reset }) {
  const analysisStatus = session.interview.analysisStatus || 'not_started'

  const analysisLabel = {
    completed: 'Analysis ready',
    processing: 'Analysis processing',
    failed: 'Analysis unavailable',
    pending: 'Analysis pending',
    not_started: 'Not started',
  }[analysisStatus] || 'Analysis pending'

  const analysisMessage = {
    completed: 'Your interview analysis has been saved. Open Reports to review your results.',
    processing: 'Your answers are saved. The interview report is being prepared.',
    failed: 'Your answers are saved, but analysis could not be completed. Please check the AI service and try again.',
    pending: 'Your interview analysis is waiting to be processed.',
    not_started: 'Analysis has not started yet.',
  }[analysisStatus] || 'Your interview analysis is being prepared.'

  return (
    <div>
      <TopNav
        title="Interview Completed"
        subtitle="Your answers are saved and your analysis status is shown below"
      />

      <Card className="max-w-4xl">
        <CardHeader>
          <CardTitle>
            {session.interview.companySnapshot.name} · {session.interview.roleSnapshot.name}
          </CardTitle>
        </CardHeader>

        <CardContent className="space-y-5">
          <div className="grid gap-4 sm:grid-cols-3">
            <div>
              <p className="eyebrow">Questions</p>
              <p className="mt-2 font-data text-2xl text-foreground">
                {session.interview.answeredQuestions}/{session.interview.totalQuestions}
              </p>
            </div>

            <div>
              <p className="eyebrow">Duration</p>
              <p className="mt-2 font-data text-2xl text-foreground">
                {formatSeconds(session.interview.durationSeconds)}
              </p>
            </div>

            <div>
              <p className="eyebrow">Analysis</p>
              <p className="mt-2 text-sm text-accent">{analysisLabel}</p>
            </div>
          </div>

          <div className="border-t border-border pt-5">
            <p className="text-sm leading-6 text-muted-foreground">{analysisMessage}</p>
          </div>

          <div className="space-y-3 border-t border-border pt-5">
            <p className="eyebrow">Stored answers</p>

            {session.questions.map((question, index) => (
              <div key={question._id} className="border border-border bg-muted/40 p-4">
                <div className="flex justify-between gap-4">
                  <p className="text-sm font-medium text-foreground">
                    {index + 1}. {question.questionSnapshot?.text}
                  </p>
                  <span className="font-data text-xs text-muted-foreground">
                    {formatSeconds(question.answer?.timing?.durationSeconds || 0)}
                  </span>
                </div>

                <p className="mt-3 whitespace-pre-line text-sm leading-6 text-muted-foreground">
                  {question.answer?.answer?.text || 'No answer stored'}
                </p>

                {question.answer?.analysis && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {[
                      ['Technical relevance', question.answer.analysis.technical_relevance],
                      ['Concept coverage', question.answer.analysis.concept_coverage],
                      ['Structure', question.answer.analysis.answer_structure],
                      ['Communication', question.answer.analysis.communication],
                    ].map(([label, value]) => (
                      <Badge key={label}>
                        {label}: {Number.isFinite(Number(value)) ? `${value}%` : 'N/A'}
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>

          <Button
            variant="outline"
            onClick={reset}
          >
            <RotateCcw size={15} className="mr-2" />
            Build another interview
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
