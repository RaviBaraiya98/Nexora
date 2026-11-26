const mongoose = require('mongoose')

const SkillSchema = new mongoose.Schema({ name: { type: String, required: true, unique: true, trim: true }, category: String, description: String, source: mongoose.Schema.Types.Mixed }, { timestamps: true })
module.exports = mongoose.models.Skill || mongoose.model('Skill', SkillSchema)
