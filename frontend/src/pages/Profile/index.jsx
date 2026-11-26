import { TopNav } from '@/components/layout/top-nav'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Textarea } from '@/components/ui/textarea'
import { useAuth } from '@/context/auth-context'
import { usePageTitle } from '@/hooks/use-page-title'
import { getProfile, reprocessResume, updateProfile, uploadResume } from '@/services/interview-service'
import { FileText, Pencil, Upload } from 'lucide-react'
import { useEffect, useMemo, useRef, useState } from 'react'

const emptyProfile = { careerGoal: '', skills: [], projects: [], targetCompanies: [], resume: null, resumeData: null }

function listValue(value) { return Array.isArray(value) ? value.join('\n') : '' }
function lines(value) { return Array.isArray(value) ? value : value ? value.split('\n').filter(Boolean) : [] }

export function ProfilePage() {
  usePageTitle('Profile')
  const { user } = useAuth()
  const fileInput = useRef(null)
  const [profile, setProfile] = useState(emptyProfile)
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState(false)
  const [saving, setSaving] = useState(false)
  const [status, setStatus] = useState('')

  useEffect(() => {
    let active = true
    getProfile().then(async (response) => {
      let nextProfile = { ...emptyProfile, ...response.profile }
      if (nextProfile.resume && !nextProfile.resume.textAvailable) {
        try { const reparsed = await reprocessResume(); nextProfile = { ...nextProfile, ...reparsed.profile, resume: reparsed.file } } catch { /* Keep the file visible if reprocessing is unavailable. */ }
      }
      if (active) setProfile(nextProfile)
    }).catch((error) => { if (active) setStatus(error.message) }).finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [])

  const completeness = useMemo(() => {
    const fields = [profile.careerGoal, profile.skills?.length, profile.projects?.length, profile.targetCompanies?.length, profile.resume]
    return Math.round((fields.filter(Boolean).length / fields.length) * 100)
  }, [profile])

  function setField(field, value) { setProfile((current) => ({ ...current, [field]: value })) }

  async function saveProfile(event) {
    event.preventDefault()
    setSaving(true)
    setStatus('Saving profile...')
    try {
      const response = await updateProfile({ careerGoal: profile.careerGoal, skills: profile.skills, projects: profile.projects, targetCompanies: profile.targetCompanies })
      setProfile((current) => ({ ...current, ...response.profile }))
      setEditing(false)
      setStatus('Profile saved.')
    } catch (error) { setStatus(error.message) } finally { setSaving(false) }
  }

  async function handleResumeUpload(event) {
    const file = event.target.files?.[0]
    if (!file) return
    setStatus('Uploading and extracting resume...')
    try {
      const response = await uploadResume(file)
      setProfile((current) => ({ ...current, ...response.profile, resume: response.file }))
      setStatus('Resume uploaded and profile data updated.')
    } catch (error) { setStatus(error.message) }
  }

  if (loading) return <div className="space-y-5"><TopNav title="Professional Profile" subtitle="Loading your saved profile" /><div className="h-56 animate-pulse bg-muted/40" /></div>

  const sections = profile.resumeData?.sections || {}
  const hasExtractedResume = Boolean(profile.resumeData?.rawText)

  return (
    <div>
      <TopNav title="Professional Profile" subtitle="Your saved preparation identity" />
      <div className="mb-6 flex flex-col justify-between gap-5 border-b border-border pb-6 md:flex-row md:items-end">
        <div><p className="eyebrow">Saved student evidence</p><h2 className="mt-4 font-display text-4xl text-foreground">{user?.name || 'Your profile'}</h2><p className="mt-2 text-sm text-muted-foreground">{user?.email}</p></div>
        <div className="flex items-end gap-4"><div className="w-44"><div className="mb-2 flex justify-between text-xs text-muted-foreground"><span>Completeness</span><span className="font-data text-foreground">{completeness}%</span></div><Progress value={completeness} /></div><Button variant="outline" onClick={() => setEditing((value) => !value)}><Pencil size={15} className="mr-2" />{editing ? 'Cancel editing' : 'Edit profile'}</Button></div>
      </div>

      {editing ? <form onSubmit={saveProfile} className="grid gap-4 xl:grid-cols-3">
        <Card className="xl:col-span-2"><CardHeader><CardTitle>Edit Profile Evidence</CardTitle></CardHeader><CardContent className="space-y-5"><div><label className="eyebrow" htmlFor="career-goal">Career direction</label><Textarea id="career-goal" className="mt-2" value={profile.careerGoal} onChange={(event) => setField('careerGoal', event.target.value)} /></div><div><label className="eyebrow" htmlFor="skills">Skills <span className="normal-case tracking-normal">(one per line)</span></label><Textarea id="skills" className="mt-2" value={listValue(profile.skills)} onChange={(event) => setField('skills', lines(event.target.value))} /></div><div><label className="eyebrow" htmlFor="projects">Projects <span className="normal-case tracking-normal">(one per line)</span></label><Textarea id="projects" className="mt-2" value={listValue(profile.projects)} onChange={(event) => setField('projects', lines(event.target.value))} /></div></CardContent></Card>
        <Card><CardHeader><CardTitle>Target Companies</CardTitle></CardHeader><CardContent><label className="eyebrow" htmlFor="target-companies">Companies <span className="normal-case tracking-normal">(one per line)</span></label><Textarea id="target-companies" className="mt-2" value={listValue(profile.targetCompanies)} onChange={(event) => setField('targetCompanies', lines(event.target.value))} /><Button type="submit" className="mt-5 w-full" disabled={saving}>{saving ? 'Saving...' : 'Save profile'}</Button></CardContent></Card>
      </form> : <div className="grid gap-4 xl:grid-cols-3">
        <Card className="xl:col-span-2"><CardHeader><CardTitle>Profile Evidence</CardTitle></CardHeader><CardContent className="space-y-6"><div><p className="eyebrow">Career direction</p><p className="mt-2 whitespace-pre-line leading-7 text-foreground">{profile.careerGoal || 'No career direction saved yet.'}</p></div><div><p className="eyebrow">Skills</p><div className="mt-3 flex flex-wrap gap-2">{profile.skills?.length ? profile.skills.map((skill) => <Badge key={skill}>{skill}</Badge>) : <p className="text-sm text-muted-foreground">No skills saved yet.</p>}</div></div><div><p className="eyebrow">Projects</p><div className="mt-3 space-y-3">{profile.projects?.length ? profile.projects.map((project, index) => <p key={index} className="whitespace-pre-line border-l-2 border-border pl-4 text-sm leading-6 text-muted-foreground">{project}</p>) : <p className="text-sm text-muted-foreground">No projects saved yet.</p>}</div></div>{hasExtractedResume ? <div className="border-t border-border pt-5"><p className="eyebrow">Resume sections indexed</p><div className="mt-3 flex flex-wrap gap-2">{Object.keys(sections).map((section) => <Badge key={section}>{section}</Badge>)}</div></div> : null}</CardContent></Card>
        <Card><CardHeader><CardTitle>Resume + Targets</CardTitle></CardHeader><CardContent className="space-y-5"><div className="border border-dashed border-accent/40 bg-accent/5 p-4"><p className="font-data text-xs text-accent">{profile.resume ? 'RESUME INDEXED' : 'NO RESUME YET'}</p><p className="mt-2 flex items-center gap-2 text-foreground"><FileText size={15} />{profile.resume?.name || 'Upload your resume'}</p>{profile.resume?.uploadedAt ? <p className="mt-1 text-xs text-muted-foreground">Updated {new Date(profile.resume.uploadedAt).toLocaleString()}</p> : null}</div><input ref={fileInput} className="hidden" type="file" accept="application/pdf,.doc,.docx" onChange={handleResumeUpload} /><Button variant="outline" className="w-full" onClick={() => fileInput.current?.click()}><Upload size={15} className="mr-2" />Upload New Resume</Button><div><p className="eyebrow">Target companies</p><div className="mt-3 flex flex-wrap gap-2">{profile.targetCompanies?.length ? profile.targetCompanies.map((company) => <Badge key={company}>{company}</Badge>) : <p className="text-sm text-muted-foreground">No target companies saved yet.</p>}</div></div></CardContent></Card>
      </div>}
      {status ? <p className="mt-5 border-t border-border pt-4 text-xs text-muted-foreground">{status}</p> : null}
    </div>
  )
}
