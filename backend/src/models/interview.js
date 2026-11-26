const mongoose = require('mongoose')

const InterviewSchema = new mongoose.Schema({
  studentId: { type: String, required: true, index: true },
  companyId: String,
  roleId: String,
  companySnapshot: { name: String },
  roleSnapshot: { name: String },
  jobDescription: String,
  blueprintId: String,
  difficulty: { type: String, required: true },
  status: { type: String, enum: ['created', 'ready', 'in_progress', 'paused', 'completed', 'abandoned'], default: 'created', index: true },
  startedAt: Date,
  completedAt: Date,
  durationSeconds: { type: Number, default: 0 },
  totalQuestions: { type: Number, default: 0 },
  answeredQuestions: { type: Number, default: 0 },
  currentQuestionIndex: { type: Number, default: 0 },
  overallScore: { type: Number, default: null },
  analysisStatus: { type: String, enum: ['not_started', 'pending', 'processing', 'completed', 'failed'], default: 'not_started' },
}, { timestamps: true })
InterviewSchema.index({ studentId: 1, createdAt: -1 })
module.exports = mongoose.models.Interview || mongoose.model('Interview', InterviewSchema)
