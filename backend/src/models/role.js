const mongoose = require('mongoose')

const RoleSchema = new mongoose.Schema({ name: { type: String, required: true, trim: true }, companyId: String, description: String, skills: [String], topics: [String], difficulty: String, interviewPattern: mongoose.Schema.Types.Mixed, source: mongoose.Schema.Types.Mixed, confidence: String, lastUpdated: Date }, { timestamps: true })
RoleSchema.index({ name: 1, companyId: 1 }, { unique: true })
module.exports = mongoose.models.Role || mongoose.model('Role', RoleSchema)
