const Report = require('../models/report')
const { createRecord, findMany } = require('../utils/memory-store')

async function createReport(data) {
  if (Report.db?.readyState === 1) return Report.create(data)
  return createRecord('reports', data)
}

async function listReports(userId) {
  if (Report.db?.readyState === 1) return Report.find({ userId }).sort({ createdAt: -1 })
  return findMany('reports', (item) => item.userId === userId)
}

module.exports = { createReport, listReports }
