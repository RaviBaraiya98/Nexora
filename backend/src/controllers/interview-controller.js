const { z } = require('zod')
const { listReports } = require('../repositories/report-repository')
const { buildInterview, getSession, listInterviews, startInterview, submitAnswer } = require('../services/interview-engine')

async function build(req, res) { res.status(201).json(await buildInterview(req.user.sub, req.body)) }
async function start(req, res) { const session = await startInterview(req.params.id, req.user.sub); if (!session) return res.status(404).json({ error: 'Interview not found' }); res.json(session) }
async function list(req, res) { res.json(await listInterviews(req.user.sub, Number(req.query.page || 1), Math.min(Number(req.query.limit || 20), 50))) }
async function get(req, res) { const session = await getSession(req.params.id, req.user.sub); if (!session) return res.status(404).json({ error: 'Interview not found' }); res.json(session) }
async function answer(req, res) { const session = await submitAnswer(req.params.id, req.params.questionId, req.user.sub, req.body); if (!session) return res.status(404).json({ error: 'Interview not found' }); res.json(session) }
async function reports(req, res) { res.json({ reports: await listReports(req.user.sub) }) }

module.exports = { answer, build, get, list, reports, start }
