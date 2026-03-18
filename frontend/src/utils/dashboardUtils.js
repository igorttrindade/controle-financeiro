const INCOME_TYPES = new Set(['entrada', 'receita', 'income'])
const EXPENSE_TYPES = new Set(['saida', 'despesa', 'expense'])
const PERIOD_TO_DAYS = {
  '7d': 7,
  '30d': 30,
  '3m': 90,
  '6m': 180,
}

export function normalizeType(rawType) {
  const normalized = String(rawType || '').trim().toLowerCase()
  if (INCOME_TYPES.has(normalized)) return 'income'
  if (EXPENSE_TYPES.has(normalized)) return 'expense'
  return 'unknown'
}

export function parseTransactionDate(rawDate) {
  if (!rawDate) return null

  let normalized = rawDate
  if (typeof rawDate === 'string') {
    const trimmed = rawDate.trim()
    // Backend often returns "YYYY-MM-DD HH:mm:ss"; normalize for cross-browser parsing.
    normalized = trimmed.includes('T') ? trimmed : trimmed.replace(' ', 'T')
  }

  const date = new Date(normalized)
  if (Number.isNaN(date.getTime())) return null
  return date
}

function safeAmount(rawValue) {
  const value = Number(rawValue)
  if (!Number.isFinite(value)) return 0
  return value
}

function monthKey(date) {
  const month = String(date.getMonth() + 1).padStart(2, '0')
  return `${date.getFullYear()}-${month}`
}

function monthLabel(date) {
  return new Intl.DateTimeFormat('pt-BR', { month: 'short', year: '2-digit' }).format(date)
}

function dayKey(date) {
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${date.getFullYear()}-${month}-${day}`
}

function dayLabel(date) {
  return new Intl.DateTimeFormat('pt-BR', { day: '2-digit', month: '2-digit' }).format(date)
}

function buildLastMonths(baseDate, size) {
  const months = []
  const cursor = new Date(baseDate.getFullYear(), baseDate.getMonth(), 1)
  for (let i = size - 1; i >= 0; i -= 1) {
    months.push(new Date(cursor.getFullYear(), cursor.getMonth() - i, 1))
  }
  return months
}

function resolvePeriodDays(period) {
  return PERIOD_TO_DAYS[period] || PERIOD_TO_DAYS['30d']
}

function startOfDay(date) {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate())
}

function endOfDay(date) {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate(), 23, 59, 59, 999)
}

function shiftDateByDays(date, days) {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate() + days, date.getHours(), date.getMinutes(), date.getSeconds(), date.getMilliseconds())
}

function ensureTransactions(transactions) {
  return Array.isArray(transactions) ? transactions : []
}

export function computeDashboardKpis(transactions, now = new Date()) {
  const safeTransactions = ensureTransactions(transactions)
  const currentMonth = now.getMonth()
  const currentYear = now.getFullYear()
  let totalIncome = 0
  let totalExpense = 0
  let monthlyIncome = 0
  let monthlyExpense = 0

  for (const transaction of safeTransactions) {
    const amount = safeAmount(transaction?.valor)
    const type = normalizeType(transaction?.tipo)
    const date = parseTransactionDate(transaction?.data)

    if (type === 'income') totalIncome += amount
    if (type === 'expense') totalExpense += amount

    if (!date) continue
    if (date.getMonth() !== currentMonth || date.getFullYear() !== currentYear) continue

    if (type === 'income') monthlyIncome += amount
    if (type === 'expense') monthlyExpense += amount
  }

  return {
    balance: totalIncome - totalExpense,
    monthlyIncome,
    monthlyExpense,
  }
}

export function filterTransactionsByPeriod(transactions, period = '30d', now = new Date()) {
  const safeTransactions = ensureTransactions(transactions)
  const days = resolvePeriodDays(period)
  const end = endOfDay(now).getTime()
  const start = startOfDay(shiftDateByDays(now, -(days - 1))).getTime()

  return safeTransactions.filter((transaction) => {
    const date = parseTransactionDate(transaction?.data)
    if (!date) return false
    const timestamp = date.getTime()
    return timestamp >= start && timestamp <= end
  })
}

export function computeSavingsRate(kpis) {
  const income = safeAmount(kpis?.income ?? kpis?.monthlyIncome)
  const expense = safeAmount(kpis?.expense ?? kpis?.monthlyExpense)
  if (income <= 0) return 0

  const rate = ((income - expense) / income) * 100
  return Number.isFinite(rate) ? rate : 0
}

export function computeVariationPercent(current, previous) {
  const currentValue = safeAmount(current)
  const previousValue = safeAmount(previous)

  if (previousValue === 0) {
    if (currentValue === 0) return 0
    return 100
  }

  const variation = ((currentValue - previousValue) / Math.abs(previousValue)) * 100
  return Number.isFinite(variation) ? variation : 0
}

export function computeAverageExpense(transactions, now = new Date(), period = '30d') {
  const filtered = filterTransactionsByPeriod(transactions, period, now)
  const expenses = filtered.filter((transaction) => normalizeType(transaction?.tipo) === 'expense')
  if (expenses.length === 0) return 0

  const total = expenses.reduce((acc, transaction) => acc + safeAmount(transaction?.valor), 0)
  return total / expenses.length
}

export function computeTopCategory(transactions, now = new Date(), period = '30d') {
  const filtered = filterTransactionsByPeriod(transactions, period, now)
  const bucket = new Map()

  for (const transaction of filtered) {
    if (normalizeType(transaction?.tipo) !== 'expense') continue
    const name = String(transaction?.nome || '').trim() || 'Sem categoria'
    const amount = safeAmount(transaction?.valor)
    const current = bucket.get(name) || { amount: 0, count: 0 }
    current.amount += amount
    current.count += 1
    bucket.set(name, current)
  }

  let topCategory = null
  for (const [name, stats] of bucket.entries()) {
    if (!topCategory || stats.amount > topCategory.amount) {
      topCategory = {
        name,
        amount: stats.amount,
        count: stats.count,
      }
    }
  }

  return topCategory
}

export function computeGoalProgress({ monthlyExpense, monthlyGoal }) {
  const expense = safeAmount(monthlyExpense)
  const goal = safeAmount(monthlyGoal)

  if (goal <= 0) {
    return {
      isConfigured: false,
      percent: 0,
      remaining: 0,
      isExceeded: false,
    }
  }

  const percent = (expense / goal) * 100
  return {
    isConfigured: true,
    percent: Math.max(0, Math.min(100, percent)),
    remaining: Math.max(0, goal - expense),
    isExceeded: expense > goal,
  }
}

export function buildInsights({ kpis, variation, savingsRate, topCategory, goalProgress }) {
  const insights = []

  if ((kpis?.income || 0) === 0 && (kpis?.expense || 0) === 0) {
    insights.push({
      id: 'no-movement',
      tone: 'info',
      title: 'Sem movimentações no período',
      description: 'Cadastre uma nova transação para começar a gerar métricas automáticas.',
    })
    return insights
  }

  if ((kpis?.balance || 0) >= 0) {
    insights.push({
      id: 'positive-balance',
      tone: 'success',
      title: 'Saldo positivo no período',
      description: 'Você está mantendo as receitas acima das despesas no recorte selecionado.',
    })
  } else {
    insights.push({
      id: 'negative-balance',
      tone: 'warning',
      title: 'Saldo negativo no período',
      description: 'As despesas superaram as receitas. Priorize cortes em categorias recorrentes.',
    })
  }

  insights.push({
    id: 'savings-rate',
    tone: savingsRate >= 20 ? 'success' : 'info',
    title: 'Taxa de economia',
    description: `Sua taxa está em ${savingsRate.toFixed(1)}% no período atual.`,
  })

  insights.push({
    id: 'variation',
    tone: variation >= 0 ? 'info' : 'warning',
    title: 'Variação vs período anterior',
    description: `${variation >= 0 ? 'Crescimento' : 'Queda'} de ${Math.abs(variation).toFixed(1)}% no saldo comparado ao período anterior.`,
  })

  if (topCategory) {
    insights.push({
      id: 'top-category',
      tone: 'warning',
      title: 'Maior categoria de gasto',
      description: `${topCategory.name} representa ${topCategory.count} lançamento(s), totalizando ${topCategory.amount.toFixed(2)}.`,
    })
  }

  if (goalProgress?.isConfigured) {
    insights.push({
      id: 'goal-progress',
      tone: goalProgress.isExceeded ? 'error' : 'success',
      title: 'Progresso da meta mensal',
      description: goalProgress.isExceeded
        ? 'Você excedeu a meta mensal definida. Ajuste os próximos lançamentos.'
        : 'Meta mensal dentro do planejado até o momento.',
    })
  }

  return insights.slice(0, 4)
}

function buildDayBuckets(baseDate, days) {
  const buckets = []
  const start = startOfDay(shiftDateByDays(baseDate, -(days - 1)))
  for (let offset = 0; offset < days; offset += 1) {
    buckets.push(shiftDateByDays(start, offset))
  }
  return buckets
}

function buildPeriodRange(period, now = new Date()) {
  const safePeriod = PERIOD_TO_DAYS[period] ? period : '30d'
  const days = resolvePeriodDays(safePeriod)

  if (safePeriod === '3m') {
    const months = buildLastMonths(now, 3)
    return { granularity: 'month', current: months }
  }

  if (safePeriod === '6m') {
    const months = buildLastMonths(now, 6)
    return { granularity: 'month', current: months }
  }

  return {
    granularity: 'day',
    current: buildDayBuckets(now, days),
  }
}

function buildPreviousRange(range) {
  const { granularity, current } = range

  if (granularity === 'month') {
    const first = current[0]
    const size = current.length
    const previousLast = new Date(first.getFullYear(), first.getMonth() - 1, 1)
    return {
      granularity,
      previous: buildLastMonths(previousLast, size),
    }
  }

  const first = current[0]
  const size = current.length
  const previousEnd = shiftDateByDays(first, -1)
  return {
    granularity,
    previous: buildDayBuckets(previousEnd, size),
  }
}

function buildBuckets(points, granularity) {
  const buckets = new Map()

  for (const point of points) {
    const key = granularity === 'month' ? monthKey(point) : dayKey(point)
    buckets.set(key, { income: 0, expense: 0 })
  }

  return buckets
}

function fillBuckets(transactions, buckets, granularity) {
  for (const transaction of ensureTransactions(transactions)) {
    const date = parseTransactionDate(transaction?.data)
    if (!date) continue
    const key = granularity === 'month' ? monthKey(date) : dayKey(date)
    if (!buckets.has(key)) continue

    const type = normalizeType(transaction?.tipo)
    const amount = safeAmount(transaction?.valor)
    const bucket = buckets.get(key)

    if (type === 'income') bucket.income += amount
    if (type === 'expense') bucket.expense += amount
  }
}

function mapBucketValues(points, buckets, granularity, key) {
  return points.map((point) => {
    const bucketKey = granularity === 'month' ? monthKey(point) : dayKey(point)
    return buckets.get(bucketKey)?.[key] || 0
  })
}

export function aggregateLineSeriesWithPreviousPeriod(transactions, period = '30d', now = new Date()) {
  const currentRange = buildPeriodRange(period, now)
  const { previous } = buildPreviousRange(currentRange)

  const currentBuckets = buildBuckets(currentRange.current, currentRange.granularity)
  const previousBuckets = buildBuckets(previous, currentRange.granularity)

  fillBuckets(transactions, currentBuckets, currentRange.granularity)
  fillBuckets(transactions, previousBuckets, currentRange.granularity)

  const income = mapBucketValues(currentRange.current, currentBuckets, currentRange.granularity, 'income')
  const expense = mapBucketValues(currentRange.current, currentBuckets, currentRange.granularity, 'expense')
  const previousIncome = mapBucketValues(previous, previousBuckets, currentRange.granularity, 'income')
  const previousExpense = mapBucketValues(previous, previousBuckets, currentRange.granularity, 'expense')

  const incomeTotal = income.reduce((acc, value) => acc + value, 0)
  const expenseTotal = expense.reduce((acc, value) => acc + value, 0)
  const previousIncomeTotal = previousIncome.reduce((acc, value) => acc + value, 0)
  const previousExpenseTotal = previousExpense.reduce((acc, value) => acc + value, 0)

  return {
    labels: currentRange.current.map((point) =>
      currentRange.granularity === 'month' ? monthLabel(point) : dayLabel(point),
    ),
    income,
    expense,
    previousIncome,
    previousExpense,
    totals: {
      income: incomeTotal,
      expense: expenseTotal,
      balance: incomeTotal - expenseTotal,
    },
    previousTotals: {
      income: previousIncomeTotal,
      expense: previousExpenseTotal,
      balance: previousIncomeTotal - previousExpenseTotal,
    },
  }
}

export function aggregateMonthlySeries(transactions, baseDate = new Date(), size = 6) {
  const months = buildLastMonths(baseDate, size)
  const buckets = new Map()

  for (const month of months) {
    buckets.set(monthKey(month), { income: 0, expense: 0 })
  }

  for (const transaction of ensureTransactions(transactions)) {
    const date = parseTransactionDate(transaction?.data)
    if (!date) continue
    const key = monthKey(date)
    if (!buckets.has(key)) continue

    const bucket = buckets.get(key)
    const type = normalizeType(transaction?.tipo)
    const amount = safeAmount(transaction?.valor)
    if (type === 'income') bucket.income += amount
    if (type === 'expense') bucket.expense += amount
  }

  return {
    labels: months.map((month) => monthLabel(month)),
    income: months.map((month) => buckets.get(monthKey(month)).income),
    expense: months.map((month) => buckets.get(monthKey(month)).expense),
  }
}
