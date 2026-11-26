function errorHandler(error, req, res, next) {
  console.error(error)
  if (error.name === 'ZodError') return res.status(400).json({ error: 'Invalid request data', details: error.issues })
  if (error.name === 'MulterError') return res.status(400).json({ error: error.message })
  if (error.name === 'ValidationError') return res.status(400).json({ error: 'Invalid request data', details: error.errors })
  const status = error.statusCode || 500
  res.status(status).json({ error: status === 500 ? 'Internal server error' : error.message })
}

module.exports = { errorHandler }
