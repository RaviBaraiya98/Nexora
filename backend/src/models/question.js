const mongoose = require('mongoose')

const QuestionSchema = new mongoose.Schema({ question: { type: String, required: true }, type: { type: String, default: 'technical' }, difficulty: String, skillId: String, topicId: String, companyId: String, roleId: String, expectedConcepts: [String], referenceAnswer: String, followUpQuestions: [String], source: mongoose.Schema.Types.Mixed }, { timestamps: true })
QuestionSchema.index({ question: 1, 'source.record_id': 1 }, { unique: true })
module.exports = mongoose.models.Question || mongoose.model('Question', QuestionSchema)
