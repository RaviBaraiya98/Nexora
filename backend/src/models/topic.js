const mongoose = require('mongoose')

const TopicSchema = new mongoose.Schema({ name: { type: String, required: true, unique: true, trim: true }, skillId: String, difficulty: String, description: String, source: mongoose.Schema.Types.Mixed }, { timestamps: true })
module.exports = mongoose.models.Topic || mongoose.model('Topic', TopicSchema)
