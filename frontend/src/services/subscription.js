import { apiRequest } from '@/services/http/api'

export async function getSubscription(options = {}) {
  return apiRequest('/api/subscription', 'GET', null, options)
}

export async function getSubscriptionLimits(options = {}) {
  return apiRequest('/api/subscription/limits', 'GET', null, options)
}
