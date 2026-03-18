import { beforeEach, describe, expect, it } from 'vitest'
import { useSubscription } from '@/composables/useSubscription'

describe('useSubscription', () => {
  const subscription = useSubscription()

  beforeEach(() => {
    subscription.limits.value = null
    subscription.subscription.value = null
    subscription.error.value = ''
    subscription.loading.value = false
    subscription.hasLoaded.value = false
  })

  it('usagePercent retorna 64 quando current=32 e limit=50', () => {
    subscription.limits.value = {
      plan: 'free',
      is_pro: false,
      monthly_transaction_limit: 50,
      current_month_transactions: 32,
      allowed: true,
    }

    expect(subscription.usagePercent.value).toBe(64)
  })

  it('usagePercent retorna 0 quando isPro=true', () => {
    subscription.limits.value = {
      plan: 'pro',
      is_pro: true,
      monthly_transaction_limit: null,
      current_month_transactions: 200,
      allowed: true,
    }

    expect(subscription.usagePercent.value).toBe(0)
  })

  it('isNearLimit retorna true quando usagePercent=85', () => {
    subscription.limits.value = {
      plan: 'free',
      is_pro: false,
      monthly_transaction_limit: 100,
      current_month_transactions: 85,
      allowed: true,
    }

    expect(subscription.isNearLimit.value).toBe(true)
  })

  it('isNearLimit retorna false quando usagePercent=50', () => {
    subscription.limits.value = {
      plan: 'free',
      is_pro: false,
      monthly_transaction_limit: 100,
      current_month_transactions: 50,
      allowed: true,
    }

    expect(subscription.isNearLimit.value).toBe(false)
  })

  it('isAtLimit retorna true quando current=50 e limit=50', () => {
    subscription.limits.value = {
      plan: 'free',
      is_pro: false,
      monthly_transaction_limit: 50,
      current_month_transactions: 50,
      allowed: false,
    }

    expect(subscription.isAtLimit.value).toBe(true)
  })

  it('isAtLimit retorna false para usuário pro', () => {
    subscription.limits.value = {
      plan: 'pro',
      is_pro: true,
      monthly_transaction_limit: null,
      current_month_transactions: 300,
      allowed: true,
    }

    expect(subscription.isAtLimit.value).toBe(false)
  })
})
