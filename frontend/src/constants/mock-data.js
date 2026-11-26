export const dashboardStats = [
  { label: 'Readiness Score', value: 82, suffix: '%', delta: '+6.2%' },
  { label: 'Interviews Completed', value: 19, suffix: '', delta: '+3 this week' },
  { label: 'Target Roles Mapped', value: 7, suffix: '', delta: '2 newly added' },
  { label: 'AI Confidence', value: 91, suffix: '%', delta: 'High' },
]

export const progressSeries = [
  { week: 'W1', score: 58 },
  { week: 'W2', score: 64 },
  { week: 'W3', score: 69 },
  { week: 'W4', score: 72 },
  { week: 'W5', score: 78 },
  { week: 'W6', score: 82 },
]

export const topicReadiness = [
  { topic: 'DSA', readiness: 76 },
  { topic: 'System Design', readiness: 63 },
  { topic: 'DBMS', readiness: 71 },
  { topic: 'OS', readiness: 66 },
  { topic: 'Behavioral', readiness: 85 },
]

export const recentInterviews = [
  { company: 'Google', role: 'SWE Intern', score: 81, date: 'Aug 03, 2026' },
  { company: 'Atlassian', role: 'Backend Intern', score: 77, date: 'Aug 01, 2026' },
  { company: 'Razorpay', role: 'Full Stack Intern', score: 84, date: 'Jul 29, 2026' },
]

export const targetCompanies = [
  { name: 'Stripe', role: 'Software Engineer', rounds: 5, focus: 'API, System Design' },
  { name: 'Notion', role: 'Frontend Engineer', rounds: 4, focus: 'React, UX thinking' },
  { name: 'Vercel', role: 'Product Engineer', rounds: 4, focus: 'JS runtime, web perf' },
  { name: 'Linear', role: 'Full Stack Engineer', rounds: 5, focus: 'Product sense, backend' },
  { name: 'Anthropic', role: 'Software Engineer', rounds: 6, focus: 'Algorithms, ML basics' },
  { name: 'Perplexity', role: 'Frontend Engineer', rounds: 5, focus: 'Search UX, architecture' },
]

export const recommendedTopics = ['Monotonic Stack', 'Caching Strategies', 'REST API Security', 'Rate Limiting', 'Concurrency Basics']

export const upcomingInterviews = [
  { company: 'Stripe', role: 'Software Engineer', date: 'Aug 08, 2026', type: 'Technical' },
  { company: 'Vercel', role: 'Product Engineer', date: 'Aug 10, 2026', type: 'System Design' },
]

export const reportSummary = {
  technicalScore: 84,
  communicationScore: 79,
  companyReadiness: 81,
  strengths: ['Clear problem decomposition', 'Strong API design explanations', 'Good tradeoff articulation'],
  weaknesses: ['Edge-case handling consistency', 'Timing in final summary', 'Latency optimization depth'],
  gaps: [
    { area: 'Distributed caching', impact: 'High' },
    { area: 'Queue-based retries', impact: 'Medium' },
    { area: 'Memory tuning', impact: 'Low' },
  ],
}
