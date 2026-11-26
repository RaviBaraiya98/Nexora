const { connectDatabase } = require('../src/config/database')
const { importKnowledge } = require('../src/services/knowledge-importer')

connectDatabase().then(async (connected) => {
  if (!connected) throw new Error('MongoDB must be connected before importing knowledge')
  const counts = await importKnowledge()
  console.log(JSON.stringify(counts, null, 2))
  process.exit(0)
}).catch((error) => { console.error(error.message); process.exit(1) })
