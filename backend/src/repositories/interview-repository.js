const Interview = require('../models/interview')
const { createRecord, findMany, findOne } = require('../utils/memory-store')

async function createInterview(data) {
  if (Interview.db?.readyState === 1) return Interview.create(data)
  return createRecord('interviews', data)
}

async function listInterviews(userId) {
  if (Interview.db?.readyState === 1) return Interview.find({ userId }).sort({ createdAt: -1 })
  return findMany('interviews', (item) => item.userId === userId)
}

async function findInterview(id, userId) {
  if (Interview.db?.readyState === 1) return Interview.findOne({ _id: id, userId })
  return findOne('interviews', (item) => item._id === id && item.userId === userId)
}

module.exports = { createInterview, listInterviews, findInterview }
