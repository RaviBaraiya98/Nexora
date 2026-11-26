const jwt = require('jsonwebtoken')
const crypto = require('node:crypto')
const { jwtRefreshSecret, jwtSecret } = require('../config/env')

function ensureSecrets() {
  if (!jwtSecret || !jwtRefreshSecret) throw new Error('JWT_SECRET and JWT_REFRESH_SECRET must be configured')
}

function userPayload(user) {
  return { sub: String(user.id || user._id), email: user.email, role: user.role }
}

function signAccessToken(user) {
  ensureSecrets()
  return jwt.sign({ ...userPayload(user), type: 'access' }, jwtSecret, { expiresIn: '15m' })
}

function signRefreshToken(user) {
  ensureSecrets()
  return jwt.sign({ ...userPayload(user), type: 'refresh' }, jwtRefreshSecret, { expiresIn: '30d' })
}

function verifyAccessToken(token) {
  ensureSecrets()
  const payload = jwt.verify(token, jwtSecret)
  if (payload.type !== 'access') throw new Error('Invalid access token')
  return payload
}

function verifyRefreshToken(token) {
  ensureSecrets()
  const payload = jwt.verify(token, jwtRefreshSecret)
  if (payload.type !== 'refresh') throw new Error('Invalid refresh token')
  return payload
}

function hashToken(token) {
  return crypto.createHash('sha256').update(token).digest('hex')
}

module.exports = { hashToken, signAccessToken, signRefreshToken, verifyAccessToken, verifyRefreshToken }
