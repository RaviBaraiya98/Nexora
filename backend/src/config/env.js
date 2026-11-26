const dotenv = require('dotenv')
const path = require('node:path')

dotenv.config({ path: path.resolve(__dirname, '../../.env') })

const nodeEnv = process.env.NODE_ENV || 'development'
const jwtSecret = process.env.JWT_SECRET || (nodeEnv === 'production' ? '' : 'nexora-local-access-secret-change-me')
const jwtRefreshSecret = process.env.JWT_REFRESH_SECRET || (nodeEnv === 'production' ? '' : 'nexora-local-refresh-secret-change-me')

module.exports = {
  port: Number(process.env.PORT || 4000),
  clientOrigin: process.env.CLIENT_ORIGIN || 'http://localhost:5173',
  mongoUri: process.env.MONGODB_URI || '',
  jwtSecret,
  jwtRefreshSecret,
  nodeEnv,
  aiServiceUrl: process.env.AI_SERVICE_URL || 'http://127.0.0.1:8000',
  uploadDir: process.env.UPLOAD_DIR || 'uploads',
  cloudinary: {
    cloudName: process.env.CLOUDINARY_CLOUD_NAME || '',
    apiKey: process.env.CLOUDINARY_API_KEY || '',
    apiSecret: process.env.CLOUDINARY_API_SECRET || '',
  },
}
