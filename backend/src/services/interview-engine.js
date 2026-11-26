const mongoose = require('mongoose')
const { z } = require('zod')
const Company = require('../models/company')
const Role = require('../models/role')
const Question = require('../models/question')
const Interview = require('../models/interview')
const Blueprint = require('../models/interview-blueprint')
const InterviewQuestion = require('../models/interview-question')
const Answer = require('../models/answer')
const { analyzeAnswer } = require('./ai-analysis-service')
const { createReport, listReports } = require('../repositories/report-repository')

const buildSchema = z.object({ company: z.string().trim().min(2).max(160), role: z.string().trim().min(2).max(160), jobDescription: z.string().trim().max(20000).optional().default(''), difficulty: z.enum(['easy', 'medium', 'hard']).default('medium'), durationMinutes: z.coerce.number().int().refine((value) => [15, 30, 45].includes(value)), questionCount: z.coerce.number().int().refine((value) => [10, 15, 20].includes(value)) })

function requireDatabase() { if (mongoose.connection.readyState !== 1) { const error = new Error('MongoDB is required for interview sessions'); error.statusCode = 503; throw error } }
function tokens(value) { return String(value || '').toLowerCase().split(/[^a-z0-9+#.]+/).filter((token) => token.length > 2) }
function normalizeQuestionText(value) { return String(value || '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim() }
function questionSnapshot(question) { return { text: question.question, skill: question.skillId || null, topic: question.topicId || null, difficulty: question.difficulty || null, type: question.type || 'technical' } }

async function resolveContext(input) {
  const company = await Company.findOne({ name: new RegExp(`^${input.company.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}$`, 'i') }).lean()
  const role = await Role.findOne({ name: new RegExp(`^${input.role.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}$`, 'i') }).lean()
  return { company, role }
}

async function buildInterview(userId, rawInput) {
  requireDatabase()
  const input = buildSchema.parse(rawInput)
  const { company, role } = await resolveContext(input)
  const allQuestions = await Question.find({}).lean()
  const searchTokens = new Set([...tokens(input.role), ...tokens(input.jobDescription)])
  const ranked = allQuestions.map((question) => {
    const textTokens = tokens(`${question.question} ${question.topicId || ''} ${question.skillId || ''}`)
    const relevance = textTokens.filter((token) => searchTokens.has(token)).length
    return { question, relevance }
  }).sort((a, b) => b.relevance - a.relevance || String(a.question._id).localeCompare(String(b.question._id)))
  const selected = []
  const seenQuestionIds = new Set()
  const seenQuestionTexts = new Set()
  for (const item of ranked) {
    const questionId = String(item.question._id)
    const normalizedText = normalizeQuestionText(item.question.question)
    if (seenQuestionIds.has(questionId) || !normalizedText || seenQuestionTexts.has(normalizedText)) continue
    if (item.question.difficulty && item.question.difficulty.toLowerCase() !== input.difficulty) continue
    selected.push(item.question)
    seenQuestionIds.add(questionId)
    seenQuestionTexts.add(normalizedText)
    if (selected.length >= input.questionCount) break
  }
  if (!selected.length) { const error = new Error('No questions are available for this interview configuration'); error.statusCode = 422; throw error }

  const sectionCounts = new Map()
  selected.forEach((question) => { const section = question.topicId || question.skillId || 'General technical'; sectionCounts.set(section, (sectionCounts.get(section) || 0) + 1) })
  const sections = [...sectionCounts.entries()].map(([name, questionCount]) => ({ name, questionCount }))
  const blueprint = await Blueprint.create({ companyId: company?._id?.toString(), roleId: role?._id?.toString(), companyNameSnapshot: input.company, roleNameSnapshot: input.role, jobDescription: input.jobDescription, difficulty: input.difficulty, durationMinutes: input.durationMinutes, totalQuestions: selected.length, sections, generationSource: { type: company ? 'knowledge_base' : 'user_provided', confidence: company && role ? 'high' : 'user_context' } })
  const interview = await Interview.create({ studentId: userId, companyId: company?._id?.toString(), roleId: role?._id?.toString(), companySnapshot: { name: input.company }, roleSnapshot: { name: input.role }, jobDescription: input.jobDescription, blueprintId: blueprint._id.toString(), difficulty: input.difficulty, status: 'ready', totalQuestions: selected.length, answeredQuestions: 0, currentQuestionIndex: 0, analysisStatus: 'not_started' })
  await InterviewQuestion.insertMany(selected.map((question, index) => ({ interviewId: interview._id.toString(), questionId: question._id.toString(), order: index, section: question.topicId || question.skillId || 'General technical', skillId: question.skillId || null, topicId: question.topicId || null, questionSnapshot: { ...questionSnapshot(question), normalizedText: normalizeQuestionText(question.question) }, status: 'pending' })))
  return getSession(interview._id.toString(), userId)
}

async function startInterview(id, userId) {
  requireDatabase()
  const interview = await Interview.findOne({ _id: id, studentId: userId })
  if (!interview) return null
  if (interview.status === 'completed') return getSession(id, userId)
  if (!interview.startedAt) interview.startedAt = new Date()
  interview.status = 'in_progress'
  const current = await InterviewQuestion.findOne({ interviewId: id, order: interview.currentQuestionIndex })
  if (current && !current.startedAt) { current.startedAt = new Date(); current.status = 'active'; await current.save() }
  await interview.save()
  return getSession(id, userId)
}

async function getSession(id, userId) {
  requireDatabase()
  const interview = await Interview.findOne({ _id: id, studentId: userId }).lean()
  if (!interview) return null
  const questions = await InterviewQuestion.find({ interviewId: id }).sort({ order: 1 }).lean()
  const answers = await Answer.find({ interviewId: id, studentId: userId }).lean()
  const answerByQuestion = new Map(answers.map((answer) => [answer.interviewQuestionId, answer]))
  return { interview, questions: questions.map((question) => ({ ...question, answer: answerByQuestion.get(question._id.toString()) || null })) }
}

async function listInterviews(userId, page = 1, limit = 20) {
  requireDatabase()
  const skip = (page - 1) * limit
  const [interviews, total] = await Promise.all([Interview.find({ studentId: userId }).sort({ createdAt: -1 }).skip(skip).limit(limit).lean(), Interview.countDocuments({ studentId: userId })])
  return { interviews, page, limit, total, pages: Math.ceil(total / limit) }
}


async function submitAnswer(id, interviewQuestionId, userId, input) {
  requireDatabase()

  const interview = await Interview.findOne({
    _id: id,
    studentId: userId,
  })

  if (!interview) return null

  if (interview.status !== 'in_progress') {
    const error = new Error('Interview is not accepting answers')
    error.statusCode = 409
    throw error
  }

  const question = await InterviewQuestion.findOne({
    _id: interviewQuestionId,
    interviewId: id,
  })

  if (!question) {
    const error = new Error('Interview question not found')
    error.statusCode = 404
    throw error
  }

  const text = z.string().trim().min(1).max(20000).parse(
    input?.answer?.text ?? input?.text ?? ''
  )

  const submittedAt = new Date()
  const startedAt = question.startedAt || submittedAt
  const durationSeconds = Math.max(
    0,
    Math.round((submittedAt.getTime() - startedAt.getTime()) / 1000)
  )

  // Save the answer first. AI failure must not lose the student's answer.
  const answer = await Answer.findOneAndUpdate(
    { interviewQuestionId, studentId: userId },
    {
      interviewId: id,
      questionId: question.questionId,
      studentId: userId,
      questionSnapshot: question.questionSnapshot,
      answer: { type: 'text', text },
      timing: { startedAt, submittedAt, durationSeconds },
      status: 'submitted',
    },
    {
      upsert: true,
      returnDocument: 'after',
      setDefaultsOnInsert: true,
    }
  )

  // Analyze this answer using the existing Python AI service.
  let analysis = null

  try {
    analysis = await analyzeAnswer({
      company: interview.companySnapshot?.name || 'Unknown company',
      role: interview.roleSnapshot?.name || 'Unknown role',
      question: question.questionSnapshot?.text || '',
      answer: text,
    })

    answer.analysis = analysis
    await answer.save()
  } catch (error) {
    console.warn(
      'AI analysis unavailable; answer was saved:',
      error.message
    )
  }

  question.status = 'answered'
  question.submittedAt = submittedAt
  question.answerId = answer._id.toString()
  await question.save()

  const answeredQuestions = await Answer.countDocuments({
    interviewId: id,
    studentId: userId,
  })

  interview.answeredQuestions = answeredQuestions

  const allQuestions = await InterviewQuestion.countDocuments({
    interviewId: id,
  })

  if (answeredQuestions >= allQuestions) {
    interview.status = 'completed'
    interview.completedAt = submittedAt
    interview.durationSeconds = Math.max(
      0,
      Math.round((submittedAt - interview.startedAt) / 1000)
    )
    interview.currentQuestionIndex = allQuestions
    interview.analysisStatus = 'processing'

    await interview.save()

    // Build a report from the answers that were successfully analyzed.
    try {
      const answers = await Answer.find({
        interviewId: id,
        studentId: userId,
      }).lean()

      const analyzedAnswers = answers.filter(
        (item) => item.analysis && typeof item.analysis === 'object'
      )

      if (analyzedAnswers.length > 0) {
        const metrics = [
          'technical_relevance',
          'concept_coverage',
          'answer_structure',
          'communication',
        ]

        const averages = {}

        for (const metric of metrics) {
          const values = analyzedAnswers
            .map((item) => Number(item.analysis[metric]))
            .filter(Number.isFinite)

          if (values.length > 0) {
            averages[metric] = Math.round(
              values.reduce((sum, value) => sum + value, 0) /
                values.length
            )
          }
        }

        const collect = (key) => [
          ...new Set(
            analyzedAnswers.flatMap((item) =>
              Array.isArray(item.analysis[key])
                ? item.analysis[key].filter(
                    (value) => typeof value === 'string'
                  )
                : []
            )
          ),
        ]

        const existingReports = await listReports(userId)
        const alreadyExists = existingReports.some(
          (report) => String(report.interviewId) === String(id)
        )

        if (!alreadyExists) {
          await createReport({
            userId,
            interviewId: String(id),
            analysis: {
              ...averages,
              analyzedAnswers: analyzedAnswers.length,
              totalAnswers: answers.length,
              status:
                analyzedAnswers.length === answers.length
                  ? 'completed'
                  : 'partial',
              detected: collect('detected'),
              missing: collect('missing'),
              strengths: collect('strengths'),
              weaknesses: collect('weaknesses'),
              recommendations: collect('recommendations'),
              answers: analyzedAnswers.map((item) => ({
                question: item.questionSnapshot?.text || '',
                answer: item.answer?.text || '',
                analysis: item.analysis,
              })),
            },
          })
        }

        interview.analysisStatus = 'completed'
      } else {
        interview.analysisStatus = 'failed'
      }
    } catch (error) {
      console.warn('Could not generate interview report:', error.message)
      interview.analysisStatus = 'failed'
    }

    await interview.save()
  } else {
    const next = await InterviewQuestion.findOne({
      interviewId: id,
      order: { $gt: question.order },
      status: { $ne: 'answered' },
    }).sort({ order: 1 })

    if (next) {
      next.status = 'active'
      next.startedAt = next.startedAt || submittedAt
      await next.save()
      interview.currentQuestionIndex = next.order
    }

    await interview.save()
  }

  return getSession(id, userId)
}


module.exports = { buildInterview, getSession, listInterviews, startInterview, submitAnswer }
