const { aiServiceUrl } = require('../config/env')

async function analyzeAnswer({ company, role, question, answer }) {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), 10000)

  try {
    const response = await fetch(`${aiServiceUrl}/v1/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ company, role, question, answer }),
      signal: controller.signal,
    })

    if (!response.ok) {
      throw new Error(`AI service returned HTTP ${response.status}`)
    }

    return await response.json()
  } finally {
    clearTimeout(timeout)
  }
}

module.exports = { analyzeAnswer }