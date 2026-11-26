const mongoose = require('mongoose')

const CompanySchema = new mongoose.Schema({
  name: { type: String, required: true, unique: true, trim: true },
  description: String,
  industry: String,
  interviewProcess: mongoose.Schema.Types.Mixed,
  source: String,
  confidence: String,
  lastUpdated: Date,
}, { timestamps: true })

module.exports = mongoose.models.Company || mongoose.model('Company', CompanySchema)
