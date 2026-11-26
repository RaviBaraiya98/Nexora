const router = require('express').Router()
const { currentUser, login, logout, refresh, register } = require('../controllers/auth-controller')
const { requireAuth } = require('../middleware/auth')

router.post('/register', register)
router.post('/login', login)
router.post('/refresh', refresh)
router.post('/logout', logout)
router.get('/me', requireAuth, currentUser)

module.exports = router
