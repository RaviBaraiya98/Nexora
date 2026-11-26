const router = require('express').Router()
const { answer, build, get, list, reports, start } = require('../controllers/interview-controller')
const { requireAuth } = require('../middleware/auth')

router.use(requireAuth)
router.post('/build', build)
router.post('/', build)
router.get('/', list)
router.get('/reports', reports)
router.post('/:id/start', start)
router.post('/:id/questions/:questionId/answer', answer)
router.get('/:id', get)

module.exports = router
