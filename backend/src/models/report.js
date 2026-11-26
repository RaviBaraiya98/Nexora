const mongoose = require('mongoose')

const ReportSchema = new mongoose.Schema({
  userId: { type: String, required: true, index: true },
  interviewId: { type: String, required: true },
  analysis: { type: Object, required: true },
}, { timestamps: true })

module.exports = mongoose.models.Report || mongoose.model('Report', ReportSchema)
