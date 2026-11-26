const User = require('../models/user')
const { findOne } = require('../utils/memory-store')

async function updateProfile(userId, profile) {
  if (User.db?.readyState === 1) {
    const updates = Object.fromEntries(Object.entries(profile).map(([key, value]) => [`profile.${key}`, value]))
    const user = await User.findByIdAndUpdate(userId, { $set: updates }, { returnDocument: 'after', runValidators: true })
    return user
  }
  const user = findOne('users', (item) => item._id === userId)
  if (!user) return null
  user.profile = { ...(user.profile || {}), ...profile }
  user.updatedAt = new Date()
  return user
}

async function findProfile(userId) {
  if (User.db?.readyState === 1) return User.findById(userId)
  return findOne('users', (item) => item._id === userId)
}

module.exports = { updateProfile, findProfile }
