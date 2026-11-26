const router = require('express').Router()
const multer = require('multer')
const { requireAuth } = require('../middleware/auth')
const { getProfile, patchProfile, reprocessResume, uploadResume } = require('../controllers/profile-controller')

const upload = multer({ storage: multer.memoryStorage(), limits: { fileSize: 5 * 1024 * 1024 }, fileFilter: (req, file, cb) => cb(null, /pdf|document/.test(file.mimetype)) })

router.use(requireAuth)
router.get('/', getProfile)
router.patch('/', patchProfile)
router.post('/resume/reprocess', reprocessResume)
router.post('/resume', upload.single('resume'), uploadResume)

module.exports = router
