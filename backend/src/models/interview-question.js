const mongoose = require('mongoose')

const InterviewQuestionSchema = new mongoose.Schema({ interviewId: { type: String, required: true, index: true }, questionId: { type: String, required: true }, order: Number, section: String, skillId: String, topicId: String, questionSnapshot: mongoose.Schema.Types.Mixed, status: { type: String, default: 'pending' }, startedAt: Date, submittedAt: Date, answerId: String }, { timestamps: true })
InterviewQuestionSchema.index({ interviewId: 1, order: 1 }, { unique: true })
InterviewQuestionSchema.index({ interviewId: 1, questionId: 1 }, { unique: true })
module.exports = mongoose.models.InterviewQuestion || mongoose.model('InterviewQuestion', InterviewQuestionSchema)
