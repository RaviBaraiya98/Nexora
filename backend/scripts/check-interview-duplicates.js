const mongoose = require('mongoose')
const { mongoUri } = require('../src/config/env')
const InterviewQuestion = require('../src/models/interview-question')
const Question = require('../src/models/question')

async function main() {
  await mongoose.connect(mongoUri)
  const attached = await InterviewQuestion.aggregate([{ $group: { _id: { interviewId: '$interviewId', questionId: '$questionId' }, count: { $sum: 1 } } }, { $match: { count: { $gt: 1 } } }])
  const questionTextDuplicates = await Question.aggregate([{ $group: { _id: { $toLower: '$question' }, count: { $sum: 1 } } }, { $match: { count: { $gt: 1 } } }])
  console.log(JSON.stringify({ duplicateInterviewQuestionPairs: attached.length, duplicateKnowledgeQuestionTexts: questionTextDuplicates.length }, null, 2))
  await mongoose.disconnect()
}

main().catch((error) => { console.error(error.message); process.exit(1) })
