const crypto = require('node:crypto')
const { z } = require('zod')
const { nodeEnv } = require('../config/env')
const { createUser, findUserByEmail, findUserById, setRefreshTokenHash, validatePassword, sanitize } = require('../repositories/user-repository')
const { hashToken, signAccessToken, signRefreshToken, verifyRefreshToken } = require('../utils/jwt')

const registerSchema = z.object({ name: z.string().trim().min(2).max(80), email: z.string().trim().email().transform((value) => value.toLowerCase()), password: z.string().min(8).max(128) })
const loginSchema = z.object({ email: z.string().trim().email().transform((value) => value.toLowerCase()), password: z.string().min(1).max(128) })
const refreshCookieName = 'nexora_refresh_token'

function cookieOptions() {
  return { httpOnly: true, secure: nodeEnv === 'production', sameSite: 'lax', path: '/api/auth', maxAge: 30 * 24 * 60 * 60 * 1000 }
}

function clearSessionCookie(res) {
  res.clearCookie(refreshCookieName, { ...cookieOptions(), maxAge: undefined })
}

async function issueSession(res, user) {
  const safeUser = sanitize(user)
  const refreshToken = signRefreshToken(safeUser)
  await setRefreshTokenHash(safeUser.id, hashToken(refreshToken))
  res.cookie(refreshCookieName, refreshToken, cookieOptions())
  return { user: safeUser, accessToken: signAccessToken(safeUser) }
}

async function register(req, res) {
  const input = registerSchema.parse(req.body)
  if (await findUserByEmail(input.email)) return res.status(409).json({ error: 'An account with this email already exists' })
  try {
    const user = await createUser(input)
    return res.status(201).json(await issueSession(res, user))
  } catch (error) {
    if (error.code === 11000) return res.status(409).json({ error: 'An account with this email already exists' })
    throw error
  }
}

async function login(req, res) {
  const input = loginSchema.parse(req.body)
  const user = await findUserByEmail(input.email)
  if (!user || !(await validatePassword(user, input.password))) return res.status(401).json({ error: 'Invalid email or password' })
  res.json(await issueSession(res, user))
}

async function refresh(req, res) {
  const token = req.cookies?.[refreshCookieName]
  if (!token) return res.status(401).json({ error: 'Refresh session missing' })
  try {
    const payload = verifyRefreshToken(token)
    const user = await findUserById(payload.sub)
    const presentedHash = hashToken(token)
    const storedHash = user?.refreshTokenHash || ''
    const valid = storedHash.length === presentedHash.length && crypto.timingSafeEqual(Buffer.from(storedHash), Buffer.from(presentedHash))
    if (!valid) throw new Error('Refresh session revoked')
    res.json(await issueSession(res, user))
  } catch {
    clearSessionCookie(res)
    return res.status(401).json({ error: 'Refresh session expired or revoked' })
  }
}

async function currentUser(req, res) {
  const user = await findUserById(req.user.sub)
  if (!user) return res.status(404).json({ error: 'User not found' })
  res.json({ user: sanitize(user) })
}

async function logout(req, res) {
  const token = req.cookies?.[refreshCookieName]
  if (token) {
    try {
      const payload = verifyRefreshToken(token)
      await setRefreshTokenHash(payload.sub, null)
    } catch {
      // The cookie is cleared even when its token is already expired.
    }
  }
  clearSessionCookie(res)
  res.status(204).end()
}

module.exports = { currentUser, login, logout, refresh, register }
