const mongoose = require('mongoose')
const { mongoUri } = require('./env')

async function connectDatabase() {
  if (!mongoUri) {
    console.warn('MongoDB URI not configured. Running with in-memory development repositories.')
    return false
  }

  try {
    await mongoose.connect(mongoUri)
    console.log('MongoDB connected')
    return true
  } catch (error) {
    console.warn(`MongoDB unavailable: ${error.message}`)
    console.warn('Continuing with in-memory development repositories.')
    return false
  }
}

module.exports = { connectDatabase }
