const crypto = require('node:crypto')

const stores = new Map()

function collection(name) {
  if (!stores.has(name)) stores.set(name, [])
  return stores.get(name)
}

function createRecord(name, data) {
  const record = { _id: crypto.randomUUID(), createdAt: new Date(), updatedAt: new Date(), ...data }
  collection(name).push(record)
  return record
}

function findOne(name, predicate) {
  return collection(name).find(predicate) || null
}

function findMany(name, predicate = () => true) {
  return collection(name).filter(predicate)
}

module.exports = { collection, createRecord, findOne, findMany }
