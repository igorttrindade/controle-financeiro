import { parseTransactionDate } from './dashboardUtils'

function ensureArray(value) {
  return Array.isArray(value) ? value : []
}

function startOfDay(date) {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate())
}

function endOfDay(date) {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate(), 23, 59, 59, 999)
}

function parseDateInputAsLocal(rawDate) {
  const value = String(rawDate || '').trim()
  const match = value.match(/^(\d{4})-(\d{2})-(\d{2})$/)
  if (!match) return new Date(value)

  const year = Number(match[1])
  const month = Number(match[2]) - 1
  const day = Number(match[3])
  return new Date(year, month, day)
}

function containsTerm(source, term) {
  return String(source || '').toLowerCase().includes(term)
}

export function filterTransactionsByPresetPeriod(transactions, preset = 'este_mes', now = new Date()) {
  const safe = ensureArray(transactions)
  const current = new Date(now)

  if (preset === 'hoje') {
    const start = startOfDay(current).getTime()
    const end = endOfDay(current).getTime()
    return safe.filter((item) => {
      const date = parseTransactionDate(item?.data)
      if (!date) return false
      const time = date.getTime()
      return time >= start && time <= end
    })
  }

  if (preset === 'mes_anterior') {
    const year = current.getFullYear()
    const month = current.getMonth() - 1
    const target = new Date(year, month, 1)
    return safe.filter((item) => {
      const date = parseTransactionDate(item?.data)
      if (!date) return false
      return date.getFullYear() === target.getFullYear() && date.getMonth() === target.getMonth()
    })
  }

  // default: este_mes
  return safe.filter((item) => {
    const date = parseTransactionDate(item?.data)
    if (!date) return false
    return date.getFullYear() === current.getFullYear() && date.getMonth() === current.getMonth()
  })
}

export function filterTransactionsByCustomRange(transactions, startDate, endDate) {
  const safe = ensureArray(transactions)
  if (!startDate || !endDate) return safe

  const start = startOfDay(parseDateInputAsLocal(startDate)).getTime()
  const end = endOfDay(parseDateInputAsLocal(endDate)).getTime()
  if (Number.isNaN(start) || Number.isNaN(end) || start > end) return []

  return safe.filter((item) => {
    const date = parseTransactionDate(item?.data)
    if (!date) return false
    const time = date.getTime()
    return time >= start && time <= end
  })
}

export function searchTransactions(transactions, query = '') {
  const safe = ensureArray(transactions)
  const term = String(query || '').trim().toLowerCase()
  if (!term) return safe

  return safe.filter((item) =>
    containsTerm(item?.nome, term) ||
    containsTerm(item?.descricao, term) ||
    containsTerm(item?.tipo, term),
  )
}

export function sortTransactions(transactions, sortBy = 'data_desc') {
  const safe = [...ensureArray(transactions)]

  const byDateDesc = (a, b) => {
    const left = parseTransactionDate(a?.data)?.getTime() || 0
    const right = parseTransactionDate(b?.data)?.getTime() || 0
    return right - left
  }

  const byDateAsc = (a, b) => {
    const left = parseTransactionDate(a?.data)?.getTime() || 0
    const right = parseTransactionDate(b?.data)?.getTime() || 0
    return left - right
  }

  const byValueDesc = (a, b) => (Number(b?.valor) || 0) - (Number(a?.valor) || 0)
  const byValueAsc = (a, b) => (Number(a?.valor) || 0) - (Number(b?.valor) || 0)

  if (sortBy === 'data_asc') return safe.sort(byDateAsc)
  if (sortBy === 'valor_desc') return safe.sort(byValueDesc)
  if (sortBy === 'valor_asc') return safe.sort(byValueAsc)
  return safe.sort(byDateDesc)
}

export function paginateTransactions(transactions, page = 1, pageSize = 10) {
  const safe = ensureArray(transactions)
  const normalizedPageSize = Number(pageSize) > 0 ? Number(pageSize) : 10
  const totalItems = safe.length
  const totalPages = Math.max(1, Math.ceil(totalItems / normalizedPageSize))
  const normalizedPage = Math.min(Math.max(1, Number(page) || 1), totalPages)
  const start = (normalizedPage - 1) * normalizedPageSize
  const end = start + normalizedPageSize

  return {
    items: safe.slice(start, end),
    page: normalizedPage,
    pageSize: normalizedPageSize,
    totalItems,
    totalPages,
    hasPrevious: normalizedPage > 1,
    hasNext: normalizedPage < totalPages,
  }
}
