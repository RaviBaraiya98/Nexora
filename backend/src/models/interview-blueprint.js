const mongoose = require('mongoose')

const BlueprintSchema = new mongoose.Schema({ companyId: String, roleId: String, companyNameSnapshot: String, roleNameSnapshot: String, jobDescription: String, difficulty: String, durationMinutes: Number, totalQuestions: Number, sections: [mongoose.Schema.Types.Mixed], generationSource: mongoose.Schema.Types.Mixed }, { timestamps: true })
module.exports = mongoose.models.InterviewBlueprint || mongoose.model('InterviewBlueprint', BlueprintSchema)
