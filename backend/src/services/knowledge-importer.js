const fs = require('node:fs/promises')
const path = require('node:path')
const Skill = require('../models/skill')
const Role = require('../models/role')
const Topic = require('../models/topic')
const Question = require('../models/question')

const finalDir = path.resolve(__dirname, '../../../datasets/final')

async function readJson(name) { return JSON.parse(await fs.readFile(path.join(finalDir, name), 'utf8')) }

async function importKnowledge() {
  const [skills, roles, topics, questions] = await Promise.all([readJson('skills.json'), readJson('roles.json'), readJson('topics.json'), readJson('questions.json')])
  let imported = { skills: 0, roles: 0, topics: 0, questions: 0 }
  for (const item of skills) { await Skill.updateOne({ name: item.name }, { $set: item }, { upsert: true }); imported.skills += 1 }
  for (const item of roles) { await Role.updateOne({ name: item.name, companyId: item.companyId || null }, { $set: item }, { upsert: true }); imported.roles += 1 }
  for (const item of topics) { await Topic.updateOne({ name: item.name }, { $set: item }, { upsert: true }); imported.topics += 1 }
  for (const item of questions) {
    await Question.updateOne({ question: item.question, 'source.record_id': item.source?.record_id }, { $set: { question: item.question, type: item.type, difficulty: item.difficulty || null, skillId: item.skill || null, topicId: item.topic || null, expectedConcepts: item.expectedConcepts || [], referenceAnswer: item.referenceAnswer || null, source: item.source, followUpQuestions: item.followUpQuestions || [] } }, { upsert: true })
    imported.questions += 1
  }
  return imported
}

module.exports = { importKnowledge }
