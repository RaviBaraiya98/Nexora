
const mongoose = require('mongoose')

const AnswerSchema = new mongoose.Schema({
  interviewId: { type: String, required: true, index: true },
  interviewQuestionId: { type: String, required: true, unique: true },
  questionId: String,
  studentId: { type: String, required: true, index: true },
  questionSnapshot: mongoose.Schema.Types.Mixed,
  answer: { type: mongoose.Schema.Types.Mixed, required: true },
  timing: mongoose.Schema.Types.Mixed,
  analysis: { type: mongoose.Schema.Types.Mixed, default: null },
  status: { type: String, default: 'submitted' }
}, { timestamps: true })

module.exports = mongoose.models.Answer || mongoose.model('Answer', AnswerSchema)
