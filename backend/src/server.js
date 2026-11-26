const app = require('./app')
const { port } = require('./config/env')
const { connectDatabase } = require('./config/database')
const { cloudinary } = require('./config/env')

connectDatabase().then(() => {
  if (!cloudinary.cloudName || !cloudinary.apiKey || !cloudinary.apiSecret) console.warn('Cloudinary is not configured. Add CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET to backend/.env.')
  app.listen(port, () => console.log(`Nexora API listening on http://127.0.0.1:${port}`))
})
