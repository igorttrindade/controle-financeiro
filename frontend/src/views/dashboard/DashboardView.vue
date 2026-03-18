<template>
  <div class="min-h-screen bg-base-200 text-base-content">
    <Navbar />

    <main class="mx-auto w-full max-w-7xl px-4 pb-12 pt-24 sm:px-6">
      <header class="rounded-2xl border border-base-300 bg-base-100 p-6 shadow-sm">
        <div class="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <p class="text-sm font-medium text-base-content/70">{{ greetingMessage }}</p>
            <h1 class="mt-2 text-3xl font-bold tracking-tight md:text-4xl">{{ greetingTitle }}</h1>
            <p class="mt-2 text-sm text-base-content/70">Resumo financeiro consolidado para tomada de decisão.</p>
          </div>

          <label class="form-control w-full md:w-auto" aria-label="Filtro mensal da dashboard">
            <span class="label-text mb-1 text-xs text-base-content/70">Período analítico</span>
            <select v-model="selectedPeriod" class="select select-bordered select-sm w-full md:w-auto">
              <option value="este_mes">Este mês</option>
              <option value="mes_anterior">Mês anterior</option>
              <option value="3m">3 meses</option>
              <option value="6m">6 meses</option>
            </select>
          </label>
        </div>
      </header>

      <section class="mt-10 grid gap-4 md:grid-cols-3">
        <template v-if="isLoading">
          <article v-for="index in 3" :key="`kpi-skeleton-${index}`" class="rounded-2xl border border-base-300 bg-base-100 p-5 shadow-sm">
            <div class="skeleton mb-3 h-4 w-1/2"></div>
            <div class="skeleton h-8 w-2/3"></div>
          </article>
        </template>

        <template v-else>
          <article class="rounded-2xl border border-base-300 bg-base-100 p-5 shadow-sm">
            <p class="text-sm text-base-content/70">Receitas</p>
            <p class="mt-2 text-2xl font-semibold text-success">{{ formatCurrency(currentTotals.income) }}</p>
          </article>

          <article class="rounded-2xl border border-base-300 bg-base-100 p-5 shadow-sm">
            <p class="text-sm text-base-content/70">Despesas</p>
            <p class="mt-2 text-2xl font-semibold text-error">{{ formatCurrency(currentTotals.expense) }}</p>
          </article>

          <article class="rounded-2xl border border-base-300 bg-base-100 p-5 shadow-sm">
            <p class="text-sm text-base-content/70">Saldo</p>
            <p class="mt-2 text-2xl font-semibold" :class="currentTotals.balance >= 0 ? 'text-success' : 'text-error'">
              {{ formatCurrency(currentTotals.balance) }}
            </p>
          </article>
        </template>
      </section>

      <section v-if="errorMessage" class="mt-10">
        <div class="alert alert-error rounded-2xl border border-error/40 shadow-sm">
          <div>
            <h2 class="font-semibold">Não foi possível carregar a dashboard</h2>
            <p class="text-sm">{{ errorMessage }}</p>
          </div>
          <button class="btn btn-sm" @click="fetchDashboardData({ force: true })">Tentar novamente</button>
        </div>
      </section>

      <template v-else>
        <section class="mt-10 rounded-2xl border border-base-300 bg-base-100 p-6 shadow-sm">
          <div class="flex items-center justify-between gap-2">
            <div>
              <h2 class="text-xl font-semibold">Comparativo mensal</h2>
              <p class="text-sm text-base-content/70">{{ chartSubtitle }}</p>
            </div>
          </div>

          <div v-if="isLoading" class="mt-6 h-[320px] w-full rounded-2xl border border-base-300 p-4">
            <div class="skeleton h-full w-full"></div>
          </div>
          <div v-else ref="chartRef" class="mt-6 h-[320px] w-full" aria-label="Gráfico comparativo principal"></div>
        </section>

        <section class="mt-10 rounded-2xl border border-base-300 bg-base-100 p-6 shadow-sm">
          <h2 class="text-xl font-semibold">Insight inteligente</h2>
          <article class="mt-4 rounded-xl border p-4" :class="insightClass(primaryInsight.tone)">
            <p class="text-sm font-semibold">{{ primaryInsight.title }}</p>
            <p class="mt-1 text-sm text-base-content/80">{{ primaryInsight.description }}</p>
          </article>
        </section>

        <section class="mt-10 rounded-2xl border border-base-300 bg-base-100 p-6 shadow-sm">
          <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <h2 class="text-xl font-semibold">Meta mensal de despesas</h2>
              <p class="text-sm text-base-content/70">Defina seu limite mensal para acompanhar o progresso automaticamente.</p>
            </div>

            <form class="flex w-full flex-col gap-2 sm:flex-row lg:w-auto" @submit.prevent="saveMonthlyGoal">
              <label class="input input-bordered input-sm flex items-center gap-2">
                <span class="text-xs text-base-content/60">R$</span>
                <input
                  v-model="goalInput"
                  type="number"
                  step="0.01"
                  min="0"
                  placeholder="Ex.: 2500"
                  aria-label="Meta mensal de despesas"
                />
              </label>
              <button class="btn btn-primary btn-sm" :class="{ loading: isSavingGoal }" :disabled="isSavingGoal" type="submit">
                {{ isSavingGoal ? 'Salvando...' : 'Salvar meta' }}
              </button>
            </form>
          </div>

          <div class="mt-5">
            <div v-if="!goalProgress.isConfigured" class="alert rounded-xl border border-base-300 bg-base-200 text-sm">
              Meta ainda não configurada. Defina um valor para ativar a barra de progresso.
            </div>
            <template v-else>
              <div class="flex flex-col gap-1 text-sm sm:flex-row sm:items-center sm:justify-between">
                <p class="text-base-content/70 break-words">Progresso: {{ goalProgress.percent.toFixed(1) }}% da meta</p>
                <p :class="goalProgress.isExceeded ? 'text-error font-medium' : 'text-base-content/70'" class="break-words">
                  {{ goalProgress.isExceeded ? 'Meta excedida' : `Restante: ${formatCurrency(goalProgress.remaining)}` }}
                </p>
              </div>
              <progress class="progress mt-2 w-full" :class="goalProgress.isExceeded ? 'progress-error' : 'progress-success'" :value="goalProgress.percent" max="100"></progress>
            </template>
            <p v-if="goalError" class="mt-2 text-sm text-error">{{ goalError }}</p>
          </div>
        </section>
      </template>
    </main>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import Navbar from '@/components/layout/Navbar.vue'
import { useTheme } from '@/composables/useTheme'
import { getMyProfile, updateMyProfile } from '@/services/profile/profile.service'
import { getTransactions } from '@/services/transactions/transaction.service'
import {
  buildInsights,
  computeGoalProgress,
  computeSavingsRate,
  computeVariationPercent,
  normalizeType,
  parseTransactionDate,
} from '@/utils/dashboardUtils'

const DASHBOARD_CACHE_TTL_MS = 60_000
const DASHBOARD_PERIOD_STORAGE_KEY = 'dashboard:selectedPeriod'
const ALLOWED_PERIODS = new Set(['este_mes', 'mes_anterior', '3m', '6m'])

const router = useRouter()
const { isDark } = useTheme()

const transactions = ref([])
const profile = ref({ name_user: '', monthly_goal_value: null })
const selectedPeriod = ref(resolveInitialPeriod())

const isLoading = ref(true)
const isSavingGoal = ref(false)
const errorMessage = ref('')
const goalError = ref('')
const goalInput = ref('')
const chartRef = ref(null)
const referenceNow = ref(new Date())

let chartInstance = null
let echartsModule = null
let fetchController = null
let latestRequestId = 0

function resolveInitialPeriod() {
  const saved = localStorage.getItem(DASHBOARD_PERIOD_STORAGE_KEY)
  if (saved && ALLOWED_PERIODS.has(saved)) return saved
  return 'este_mes'
}

function startOfMonth(date) {
  return new Date(date.getFullYear(), date.getMonth(), 1)
}

function endOfMonth(date) {
  return new Date(date.getFullYear(), date.getMonth() + 1, 0, 23, 59, 59, 999)
}

function shiftMonth(date, amount) {
  return new Date(date.getFullYear(), date.getMonth() + amount, 1)
}

function monthLabel(date) {
  return new Intl.DateTimeFormat('pt-BR', { month: 'long', year: 'numeric' }).format(date)
}

function monthShortLabel(date) {
  return new Intl.DateTimeFormat('pt-BR', { month: 'short' }).format(date).replace('.', '')
}

function monthKey(date) {
  const month = String(date.getMonth() + 1).padStart(2, '0')
  return `${date.getFullYear()}-${month}`
}

function buildRollingRange(monthCount, endOffsetMonths, now = new Date()) {
  const currentMonthDate = new Date(now.getFullYear(), now.getMonth(), 1)
  const endMonth = shiftMonth(currentMonthDate, endOffsetMonths)
  const startMonth = shiftMonth(endMonth, -(monthCount - 1))
  return {
    start: startOfMonth(startMonth),
    end: endOfMonth(endMonth),
  }
}

function toPeriodRange(period, now = new Date()) {
  const currentMonthDate = new Date(now.getFullYear(), now.getMonth(), 1)

  if (period === 'mes_anterior') {
    const target = shiftMonth(currentMonthDate, -1)
    return {
      start: startOfMonth(target),
      end: endOfMonth(target),
      label: monthLabel(target),
    }
  }

  if (period === '3m') {
    return {
      ...buildRollingRange(3, 0, now),
      label: 'Últimos 3 meses',
    }
  }

  if (period === '6m') {
    return {
      ...buildRollingRange(6, 0, now),
      label: 'Últimos 6 meses',
    }
  }

  const target = currentMonthDate
  return {
    start: startOfMonth(target),
    end: endOfMonth(target),
    label: monthLabel(target),
  }
}

const currentRange = computed(() => toPeriodRange(selectedPeriod.value, referenceNow.value))
const comparisonRange = computed(() => {
  if (selectedPeriod.value === 'mes_anterior') {
    return toPeriodRange('este_mes', referenceNow.value)
  }

  if (selectedPeriod.value === '3m') {
    return {
      ...buildRollingRange(3, -3, referenceNow.value),
      label: '3 meses anteriores',
    }
  }

  if (selectedPeriod.value === '6m') {
    return {
      ...buildRollingRange(6, -6, referenceNow.value),
      label: '6 meses anteriores',
    }
  }

  return toPeriodRange('mes_anterior', referenceNow.value)
})

const isMultiMonthPeriod = computed(() => selectedPeriod.value === '3m' || selectedPeriod.value === '6m')

function filterByRange(source, range) {
  return source.filter((item) => {
    const date = parseTransactionDate(item?.data)
    if (!date) return false
    const time = date.getTime()
    return time >= range.start.getTime() && time <= range.end.getTime()
  })
}

function totalsFromList(source) {
  return source.reduce(
    (acc, item) => {
      const amount = Number(item?.valor) || 0
      const type = normalizeType(item?.tipo)
      if (type === 'income') acc.income += amount
      if (type === 'expense') acc.expense += amount
      acc.balance = acc.income - acc.expense
      return acc
    },
    { income: 0, expense: 0, balance: 0 },
  )
}

const currentTransactions = computed(() => filterByRange(transactions.value, currentRange.value))
const comparisonTransactions = computed(() => filterByRange(transactions.value, comparisonRange.value))

const currentTotals = computed(() => totalsFromList(currentTransactions.value))
const comparisonTotals = computed(() => totalsFromList(comparisonTransactions.value))

const savingsRate = computed(() => computeSavingsRate(currentTotals.value))
const balanceVariation = computed(() =>
  computeVariationPercent(currentTotals.value.balance, comparisonTotals.value.balance),
)
const topCategory = computed(() => {
  const bucket = new Map()
  for (const transaction of currentTransactions.value) {
    if (normalizeType(transaction?.tipo) !== 'expense') continue
    const name = String(transaction?.nome || '').trim() || 'Sem categoria'
    const amount = Number(transaction?.valor) || 0
    const current = bucket.get(name) || { amount: 0, count: 0 }
    current.amount += amount
    current.count += 1
    bucket.set(name, current)
  }

  let top = null
  for (const [name, stats] of bucket.entries()) {
    if (!top || stats.amount > top.amount) {
      top = { name, amount: stats.amount, count: stats.count }
    }
  }
  return top
})
const goalProgress = computed(() =>
  computeGoalProgress({ monthlyExpense: currentTotals.value.expense, monthlyGoal: profile.value.monthly_goal_value }),
)

const insights = computed(() =>
  buildInsights({
    kpis: currentTotals.value,
    variation: balanceVariation.value,
    savingsRate: savingsRate.value,
    topCategory: topCategory.value,
    goalProgress: goalProgress.value,
  }),
)

const primaryInsight = computed(
  () =>
    insights.value[0] || {
      tone: 'info',
      title: 'Sem insights disponíveis',
      description: 'Adicione transações para gerar análises automáticas.',
    },
)

const currentLabel = computed(() => currentRange.value.label)
const comparisonLabel = computed(() => comparisonRange.value.label)
const chartSubtitle = computed(() =>
  isMultiMonthPeriod.value ? currentLabel.value : `${currentLabel.value} vs ${comparisonLabel.value}`,
)

function buildMonthSequence(startDate, endDate) {
  const sequence = []
  let cursor = new Date(startDate.getFullYear(), startDate.getMonth(), 1)
  const end = new Date(endDate.getFullYear(), endDate.getMonth(), 1)

  while (cursor <= end) {
    sequence.push(new Date(cursor))
    cursor = new Date(cursor.getFullYear(), cursor.getMonth() + 1, 1)
  }

  return sequence
}

const monthlyChartSeries = computed(() => {
  if (!isMultiMonthPeriod.value) return null

  const months = buildMonthSequence(currentRange.value.start, currentRange.value.end)
  const buckets = new Map()
  for (const month of months) {
    buckets.set(monthKey(month), { income: 0, expense: 0 })
  }

  for (const transaction of currentTransactions.value) {
    const date = parseTransactionDate(transaction?.data)
    if (!date) continue
    const key = monthKey(date)
    if (!buckets.has(key)) continue

    const bucket = buckets.get(key)
    const amount = Number(transaction?.valor) || 0
    const type = normalizeType(transaction?.tipo)
    if (type === 'income') bucket.income += amount
    if (type === 'expense') bucket.expense += amount
  }

  return {
    labels: months.map((month) => monthShortLabel(month)),
    income: months.map((month) => buckets.get(monthKey(month)).income),
    expense: months.map((month) => buckets.get(monthKey(month)).expense),
  }
})

const chartTimeline = computed(() => {
  const points = [
    { label: currentLabel.value, start: currentRange.value.start.getTime(), totals: currentTotals.value },
    { label: comparisonLabel.value, start: comparisonRange.value.start.getTime(), totals: comparisonTotals.value },
  ]

  points.sort((left, right) => left.start - right.start)
  return points
})

const greetingTitle = computed(() => {
  const name = String(profile.value?.name_user || '').trim()
  if (!name) return 'Dashboard Financeiro'
  return `Olá, ${name.split(' ')[0]}`
})

const greetingMessage = computed(() => {
  const hour = new Date().getHours()
  if (hour < 12) return 'Bom dia'
  if (hour < 18) return 'Boa tarde'
  return 'Boa noite'
})

function getCacheKey() {
  const userId = localStorage.getItem('userId') || 'anonymous'
  return `dashboard-cache:${userId}:${selectedPeriod.value}`
}

function readDashboardCache() {
  try {
    const rawCache = localStorage.getItem(getCacheKey())
    if (!rawCache) return null
    const parsed = JSON.parse(rawCache)
    if (!parsed?.updatedAt) return null
    if (Date.now() - Number(parsed.updatedAt) > DASHBOARD_CACHE_TTL_MS) return null
    return parsed
  } catch {
    return null
  }
}

function writeDashboardCache(payload) {
  localStorage.setItem(
    getCacheKey(),
    JSON.stringify({ ...payload, updatedAt: Date.now() }),
  )
}

function sanitizeTransactions(source) {
  if (!Array.isArray(source)) return []
  return source
    .map((item) => {
      const date = parseTransactionDate(item?.data)
      return {
        id: Number(item?.id) || item?.id,
        nome: String(item?.nome || '').trim(),
        tipo: String(item?.tipo || '').trim(),
        valor: Number(item?.valor) || 0,
        data: date ? date.toISOString() : null,
      }
    })
    .filter((item) => item.data)
}

function applyPayload({ sourceTransactions, sourceProfile, sourceNow }) {
  transactions.value = sanitizeTransactions(sourceTransactions)
  profile.value = {
    name_user: String(sourceProfile?.name_user || '').trim(),
    monthly_goal_value:
      sourceProfile?.monthly_goal_value === null || sourceProfile?.monthly_goal_value === undefined
        ? null
        : Number(sourceProfile.monthly_goal_value),
  }
  goalInput.value =
    profile.value.monthly_goal_value && Number.isFinite(profile.value.monthly_goal_value)
      ? String(profile.value.monthly_goal_value)
      : ''
  referenceNow.value = sourceNow ? new Date(sourceNow) : new Date()
}

function clearSessionAndRedirect() {
  localStorage.removeItem('token')
  localStorage.removeItem('userId')
  router.push('/login')
}

function isCanceledRequest(error) {
  return error?.name === 'AbortError' || error?.name === 'CanceledError' || error?.code === 'ERR_CANCELED'
}

async function ensureChartModule() {
  if (!echartsModule) {
    echartsModule = await import('echarts')
  }
  return echartsModule
}

function formatCurrency(value) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(Number(value) || 0)
}

function insightClass(tone) {
  if (tone === 'success') return 'border-success/40 bg-success/5'
  if (tone === 'warning') return 'border-warning/40 bg-warning/5'
  if (tone === 'error') return 'border-error/40 bg-error/5'
  return 'border-info/40 bg-info/5'
}

function buildChartOption() {
  const axisColor = isDark.value ? '#a1a1aa' : '#52525b'
  const splitColor = isDark.value ? '#27272a' : '#e4e4e7'

  const xAxisData = isMultiMonthPeriod.value
    ? monthlyChartSeries.value?.labels || []
    : chartTimeline.value.map((point) => point.label)

  const incomeData = isMultiMonthPeriod.value
    ? monthlyChartSeries.value?.income || []
    : chartTimeline.value.map((point) => point.totals.income)

  const expenseData = isMultiMonthPeriod.value
    ? monthlyChartSeries.value?.expense || []
    : chartTimeline.value.map((point) => point.totals.expense)

  return {
    tooltip: {
      trigger: 'axis',
      formatter(params) {
        const lines = params.map((item) => `${item.marker} ${item.seriesName}: <strong>${formatCurrency(item.value)}</strong>`)
        return [`<strong>${params?.[0]?.axisValue || ''}</strong>`, ...lines].join('<br/>')
      },
    },
    legend: { top: 0, textStyle: { color: axisColor } },
    grid: { left: 12, right: 12, top: 40, bottom: 12, containLabel: true },
    xAxis: {
      type: 'category',
      data: xAxisData,
      axisTick: { show: false },
      axisLabel: { color: axisColor },
      axisLine: { lineStyle: { color: splitColor } },
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      axisTick: { show: false },
      splitLine: { lineStyle: { color: splitColor } },
      axisLabel: {
        color: axisColor,
        formatter(value) {
          return formatCurrency(value)
        },
      },
    },
    series: [
      {
        name: 'Receitas',
        type: 'bar',
        data: incomeData,
        itemStyle: { color: '#16a34a', borderRadius: [8, 8, 0, 0] },
        barMaxWidth: 30,
      },
      {
        name: 'Despesas',
        type: 'bar',
        data: expenseData,
        itemStyle: { color: '#dc2626', borderRadius: [8, 8, 0, 0] },
        barMaxWidth: 30,
      },
    ],
  }
}

async function initChart() {
  if (!chartRef.value || errorMessage.value || isLoading.value) return

  const echarts = await ensureChartModule()
  if (!chartInstance) {
    chartInstance = echarts.init(chartRef.value)
  }

  chartInstance.setOption(buildChartOption(), true)
}

function resizeChart() {
  if (chartInstance) chartInstance.resize()
}

async function fetchDashboardData({ force = false } = {}) {
  const cached = readDashboardCache()
  if (!force && cached) {
    applyPayload({
      sourceTransactions: cached.transactions,
      sourceProfile: cached.profile,
      sourceNow: cached.referenceNow,
    })
    isLoading.value = false
    await nextTick()
    await initChart()
    void fetchDashboardData({ force: true })
    return
  }

  if (fetchController) fetchController.abort()
  const requestId = ++latestRequestId
  fetchController = new AbortController()
  isLoading.value = true
  errorMessage.value = ''

  try {
    const [transactionsResult, profileResult] = await Promise.allSettled([
      getTransactions({ signal: fetchController.signal }),
      getMyProfile({ signal: fetchController.signal }),
    ])

    if (requestId !== latestRequestId) return
    if (transactionsResult.status === 'rejected' && isCanceledRequest(transactionsResult.reason)) return
    if (profileResult.status === 'rejected' && isCanceledRequest(profileResult.reason)) return

    const txStatus = transactionsResult.status === 'rejected' ? transactionsResult.reason?.response?.status : null
    const profileStatus = profileResult.status === 'rejected' ? profileResult.reason?.response?.status : null
    if (txStatus === 401 || profileStatus === 401) {
      clearSessionAndRedirect()
      return
    }

    if (transactionsResult.status === 'rejected') throw transactionsResult.reason

    const payload = {
      sourceTransactions: Array.isArray(transactionsResult.value) ? transactionsResult.value : [],
      sourceProfile: profileResult.status === 'fulfilled' ? profileResult.value || {} : {},
      sourceNow: new Date().toISOString(),
    }

    applyPayload(payload)
    writeDashboardCache({
      transactions: payload.sourceTransactions,
      profile: payload.sourceProfile,
      referenceNow: payload.sourceNow,
    })
  } catch (error) {
    if (requestId !== latestRequestId || isCanceledRequest(error)) return
    if (error?.response?.status === 401) {
      clearSessionAndRedirect()
      return
    }
    errorMessage.value = 'Tivemos um problema ao buscar seus dados. Tente novamente.'
  } finally {
    if (requestId === latestRequestId) {
      isLoading.value = false
      await nextTick()
      await initChart()
    }
  }
}

async function saveMonthlyGoal() {
  goalError.value = ''

  let parsedGoal = null
  const normalized = String(goalInput.value || '').trim().replace(',', '.')
  if (normalized) {
    parsedGoal = Number(normalized)
    if (!Number.isFinite(parsedGoal) || parsedGoal <= 0) {
      goalError.value = 'Informe uma meta válida maior que zero.'
      return
    }
  }

  isSavingGoal.value = true
  try {
    const response = await updateMyProfile({ monthly_goal_value: parsedGoal })
    profile.value = {
      ...profile.value,
      monthly_goal_value:
        response?.monthly_goal_value === null || response?.monthly_goal_value === undefined
          ? null
          : Number(response.monthly_goal_value),
    }

    goalInput.value = profile.value.monthly_goal_value ? String(profile.value.monthly_goal_value) : ''

    writeDashboardCache({
      transactions: transactions.value,
      profile: { ...profile.value },
      referenceNow: referenceNow.value.toISOString(),
    })
  } catch (error) {
    if (error?.response?.status === 401) {
      clearSessionAndRedirect()
      return
    }
    goalError.value = 'Não foi possível salvar sua meta agora. Tente novamente.'
  } finally {
    isSavingGoal.value = false
  }
}

onMounted(async () => {
  await fetchDashboardData()
  window.addEventListener('resize', resizeChart)
})

watch([selectedPeriod, currentTotals, comparisonTotals, isDark], async () => {
  await nextTick()
  await initChart()
})

watch(selectedPeriod, (period) => {
  if (ALLOWED_PERIODS.has(period)) {
    localStorage.setItem(DASHBOARD_PERIOD_STORAGE_KEY, period)
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeChart)
  if (fetchController) {
    fetchController.abort()
    fetchController = null
  }
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})
</script>
