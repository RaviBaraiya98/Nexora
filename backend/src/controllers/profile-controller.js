const { z } = require('zod')
const { cloudinary, isConfigured } = require('../config/cloudinary')
const { findProfile, updateProfile } = require('../repositories/profile-repository')
const { extractResumeData } = require('../services/resume-parser')

const profileSchema = z.object({ careerGoal: z.string().max(10000).optional(), skills: z.array(z.string().max(500)).max(200).optional(), projects: z.array(z.string().max(10000)).max(100).optional(), targetCompanies: z.array(z.string().max(500)).max(100).optional() }).partial()

async function getProfile(req, res) {
  const user = await findProfile(req.user.sub)
  if (!user) return res.status(404).json({ error: 'Profile not found' })
  res.json({ profile: user.profile || {}, name: user.name, email: user.email })
}

async function patchProfile(req, res) {
  const profile = profileSchema.parse(req.body)
  const user = await updateProfile(req.user.sub, profile)
  if (!user) return res.status(404).json({ error: 'Profile not found' })
  res.json({ profile: user.profile || {} })
}

async function uploadResume(req, res) {
  if (!req.file) return res.status(400).json({ error: 'Resume file is required' })
  if (!isConfigured) return res.status(503).json({ error: 'Cloudinary is not configured. Add the Cloudinary variables to backend/.env.' })

  let result
  try {
    result = await new Promise((resolve, reject) => {
      const stream = cloudinary.uploader.upload_stream(
        { folder: 'nexora/resumes', resource_type: 'raw', public_id: `${Date.now()}-${req.file.originalname.replace(/[^a-z0-9.-]/gi, '-')}` },
        (error, uploadResult) => (error ? reject(error) : resolve(uploadResult)),
      )
      stream.end(req.file.buffer)
    })
  } catch (error) {
    console.error(`Cloudinary upload failed: ${error.message}`)
    return res.status(502).json({ error: 'Cloudinary upload failed. Check the Cloudinary credentials and account configuration.' })
  }

  const file = { name: req.file.originalname, url: result.secure_url, publicId: result.public_id, size: req.file.size, uploadedAt: new Date() }
  let extraction
  try {
    extraction = await extractResumeData(req.file)
  } catch (error) {
    console.error(`Resume parsing failed: ${error.message}`)
    extraction = { fields: {}, textAvailable: false }
  }

  const fields = extraction.fields || {}
  const extractedProfile = {
    resume: { ...file, parsedAt: new Date(), textAvailable: extraction.textAvailable },
    resumeData: { rawText: extraction.rawText || '', sections: fields.sections || {}, contact: { name: fields.name || '', email: fields.email || '', phone: fields.phone || '' }, extractedAt: new Date() },
    ...(fields.skills?.length ? { skills: fields.skills } : {}),
    ...(fields.projects?.length ? { projects: fields.projects } : {}),
    ...(fields.careerGoal ? { careerGoal: fields.careerGoal } : {}),
    ...(fields.email ? { resumeEmail: fields.email } : {}),
    ...(fields.phone ? { phone: fields.phone } : {}),
  }
  const user = await updateProfile(req.user.sub, extractedProfile)
  res.status(201).json({ file: extractedProfile.resume, extracted: fields, profile: user?.profile || {} })
}

async function reprocessResume(req, res) {
  const user = await findProfile(req.user.sub)
  const resume = user?.profile?.resume
  if (!resume?.url) return res.status(404).json({ error: 'No uploaded resume found' })

  const response = await fetch(resume.url)
  if (!response.ok) return res.status(502).json({ error: 'Previously uploaded resume could not be downloaded' })
  const extraction = await extractResumeData({ originalname: resume.name, mimetype: response.headers.get('content-type') || 'application/pdf', buffer: Buffer.from(await response.arrayBuffer()) })
  const fields = extraction.fields || {}
  const updatedResume = { ...resume, parsedAt: new Date(), textAvailable: extraction.textAvailable }
  const extractedProfile = { resume: updatedResume, resumeData: { rawText: extraction.rawText || '', sections: fields.sections || {}, contact: { name: fields.name || '', email: fields.email || '', phone: fields.phone || '' }, extractedAt: new Date() }, ...(fields.skills?.length ? { skills: fields.skills } : {}), ...(fields.projects?.length ? { projects: fields.projects } : {}), ...(fields.careerGoal ? { careerGoal: fields.careerGoal } : {}) }
  const updated = await updateProfile(req.user.sub, extractedProfile)
  res.json({ file: updatedResume, extracted: fields, profile: updated?.profile || {} })
}

module.exports = { getProfile, patchProfile, reprocessResume, uploadResume }
