const path = require('node:path')
const pdfParser = require('pdf-parse')
const mammoth = require('mammoth')

const skillDictionary = [
  'JavaScript', 'TypeScript', 'React', 'Node.js', 'Express', 'MongoDB', 'SQL', 'Python', 'Java', 'C++', 'C#',
  'HTML', 'CSS', 'Git', 'Docker', 'AWS', 'System Design', 'Data Structures', 'Algorithms', 'DSA', 'Machine Learning',
]

function cleanLines(text) {
  return text.split(/\r?\n/).map((line) => line.replace(/[•|]/g, ' ').replace(/\s+/g, ' ').trim()).filter(Boolean)
}

function sectionText(lines, headings) {
  const start = lines.findIndex((line) => headings.some((heading) => line.toLowerCase() === heading || line.toLowerCase().startsWith(`${heading}:`)))
  if (start < 0) return ''
  const nextHeading = /^(experience|education|skills|technical skills|projects|summary|objective|certifications|achievements|profile|contact)$/i
  return lines.slice(start + 1).filter((line) => !nextHeading.test(line)).slice(0, 8).join(' ')
}

function extractSections(lines) {
  const headings = {
    summary: ['summary', 'objective', 'profile', 'about'],
    experience: ['experience', 'work experience', 'employment'],
    education: ['education', 'academic background'],
    projects: ['projects', 'personal projects', 'academic projects'],
    certifications: ['certifications', 'certificates'],
    achievements: ['achievements', 'awards'],
  }
  const allHeadings = Object.values(headings).flat()
  const sections = {}
  for (const [section, names] of Object.entries(headings)) {
    const start = lines.findIndex((line) => names.includes(line.toLowerCase()))
    if (start < 0) continue
    const end = lines.findIndex((line, index) => index > start && allHeadings.includes(line.toLowerCase()))
    sections[section] = lines.slice(start + 1, end < 0 ? lines.length : end).join('\n').trim()
  }
  return sections
}

function extractFields(text) {
  const lines = cleanLines(text)
  const sections = extractSections(lines)
  const email = text.match(/[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}/)?.[0] || ''
  const phone = text.match(/(?:\+?\d[\d\s().-]{8,}\d)/)?.[0]?.trim() || ''
  const name = lines.find((line) => !line.includes('@') && !/\d{5,}/.test(line) && line.split(' ').length <= 4) || ''
  const lowerText = text.toLowerCase()
  const skills = skillDictionary.filter((skill) => lowerText.includes(skill.toLowerCase()))
  const projectsText = sections.projects || sectionText(lines, ['projects', 'personal projects', 'academic projects'])
  const summary = sections.summary || sectionText(lines, ['summary', 'objective', 'profile', 'about'])
  const projects = projectsText ? [projectsText] : []
  const careerGoal = summary || (skills.length ? `Preparing for roles using ${skills.slice(0, 4).join(', ')}.` : '')
  return { name, email, phone, skills, projects, careerGoal, sections }
}

async function extractResumeData(file) {
  const extension = path.extname(file.originalname).toLowerCase()
  let text = ''
  if (extension === '.pdf' || file.mimetype === 'application/pdf') {
    if (typeof pdfParser === 'function') {
      const parsed = await pdfParser(file.buffer)
      text = parsed.text
    } else if (pdfParser.PDFParse) {
      const parser = new pdfParser.PDFParse({ data: file.buffer })
      try {
        const parsed = await parser.getText()
        text = parsed.text || ''
      } finally {
        await parser.destroy()
      }
    }
  } else if (extension === '.docx' || file.mimetype.includes('wordprocessingml')) {
    const parsed = await mammoth.extractRawText({ buffer: file.buffer })
    text = parsed.value
  }
  if (!text.trim()) return { fields: {}, rawText: '', textAvailable: false }
  return { fields: extractFields(text), rawText: text.slice(0, 200000), textAvailable: true }
}

module.exports = { extractResumeData }
