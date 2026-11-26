const bcrypt = require('bcryptjs')
const User = require('../models/user')
const { createRecord, findOne } = require('../utils/memory-store')

function sanitize(user) {
  if (!user) return null
  return { id: user.id || user._id, name: user.name, email: user.email, role: user.role, profile: user.profile || {} }
}

async function createUser({ name, email, password }) {
  const passwordHash = await bcrypt.hash(password, 12)
  if (User.db?.readyState === 1) return sanitize(await User.create({ name, email, passwordHash }))
  return sanitize(createRecord('users', { name, email, passwordHash, role: 'student', profile: {} }))
}

async function findUserByEmail(email) {
  if (User.db?.readyState === 1) return User.findOne({ email })
  return findOne('users', (user) => user.email === email)
}

async function findUserById(id) {
  if (User.db?.readyState === 1) return User.findById(id)
  return findOne('users', (user) => user._id === id)
}

async function setRefreshTokenHash(userId, refreshTokenHash) {
  if (User.db?.readyState === 1) return User.findByIdAndUpdate(userId, { refreshTokenHash }, { returnDocument: 'after' })
  const user = findOne('users', (item) => item._id === userId)
  if (user) user.refreshTokenHash = refreshTokenHash
  return user
}

async function validatePassword(user, password) {
  return bcrypt.compare(password, user.passwordHash)
}

module.exports = { createUser, findUserByEmail, findUserById, setRefreshTokenHash, validatePassword, sanitize }
