const { v2: cloudinary } = require('cloudinary')
const { cloudinary: config } = require('./env')

const isConfigured = Boolean(config.cloudName && config.apiKey && config.apiSecret)

if (isConfigured) {
  cloudinary.config({
    cloud_name: config.cloudName,
    api_key: config.apiKey,
    api_secret: config.apiSecret,
    secure: true,
  })
}

module.exports = { cloudinary, isConfigured }