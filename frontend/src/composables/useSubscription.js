import { computed, ref } from 'vue'
import { getSubscription, getSubscriptionLimits } from '@/services/subscription'

const subscription = ref(null)
const limits = ref(null)
const loading = ref(false)
const error = ref('')
const hasLoaded = ref(false)

function toNumber(value, fallback = 0) {
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : fallback
}

function normalizeLimits(payload) {
  if (!payload || typeof payload !== 'object') return null

  const plan = String(payload.plan || payload.plan_name || 'free').toLowerCase()
  const isPro = Boolean(payload.is_pro) || plan === 'pro'

  const limitRaw = payload.monthly_transaction_limit
  const limit = isPro || limitRaw === null || limitRaw === undefined ? null : toNumber(limitRaw, 0)

  const currentCount = toNumber(
    payload.current_month_transactions ?? payload.current_count,
    0,
  )

  const allowed = payload.allowed !== undefined ? Boolean(payload.allowed) : true

  return {
    plan,
    is_pro: isPro,
    monthly_transaction_limit: limit,
    current_month_transactions: currentCount,
    allowed,
  }
}

async function fetchLimits(options = {}) {
  const { force = false } = options
  if (loading.value) return limits.value
  if (!force && hasLoaded.value && limits.value) return limits.value

  loading.value = true
  error.value = ''

  try {
    const [subscriptionData, limitsData] = await Promise.all([
      getSubscription(),
      getSubscriptionLimits(),
    ])

    subscription.value = subscriptionData || null
    limits.value = normalizeLimits(limitsData)
    hasLoaded.value = true
    return limits.value
  } catch (err) {
    error.value = err?.response?.data?.error || 'Não foi possível carregar assinatura.'
    throw err
  } finally {
    loading.value = false
  }
}

const isPro = computed(() => {
  if (!limits.value) return false
  return Boolean(limits.value.is_pro)
})

const usagePercent = computed(() => {
  if (!limits.value || isPro.value) return 0

  const current = toNumber(limits.value.current_month_transactions, 0)
  const limit = toNumber(limits.value.monthly_transaction_limit, 0)

  if (limit <= 0) return 0
  return (current / limit) * 100
})

const isNearLimit = computed(() => {
  if (isPro.value) return false
  return usagePercent.value >= 80
})

const isAtLimit = computed(() => {
  if (isPro.value) return false
  return usagePercent.value >= 100
})

export function useSubscription() {
  return {
    subscription,
    limits,
    loading,
    error,
    hasLoaded,
    isPro,
    usagePercent,
    isNearLimit,
    isAtLimit,
    fetchLimits,
  }
}
