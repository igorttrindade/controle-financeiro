<template>
  <article class="card border border-base-300 bg-base-100 shadow-card">
    <div class="card-body">
      <div class="flex items-start justify-between gap-3">
        <div>
          <h2 class="card-title">Assinatura</h2>
          <p class="text-sm text-base-content/70">Acompanhe seu plano e o uso mensal de transações.</p>
        </div>
        <button class="btn btn-ghost btn-sm" :class="{ loading }" :disabled="loading" @click="retryFetch">
          Atualizar
        </button>
      </div>

      <div v-if="loading" class="mt-4 space-y-3">
        <div class="skeleton h-6 w-40"></div>
        <div class="skeleton h-4 w-full"></div>
        <div class="skeleton h-4 w-3/4"></div>
        <div class="skeleton h-24 w-full"></div>
      </div>

      <div v-else-if="error" class="mt-4 alert alert-error">
        <span>{{ error }}</span>
        <button class="btn btn-sm" @click="retryFetch">Tentar novamente</button>
      </div>

      <div v-else-if="normalizedLimits" class="mt-4 space-y-4">
        <section class="rounded-xl border border-base-300 p-4">
          <div class="flex items-center justify-between">
            <h3 class="font-semibold">Plano atual</h3>
            <span class="badge" :class="planBadgeClass">{{ isPro ? 'Pro' : 'Gratuito' }}</span>
          </div>
          <p class="mt-2 text-sm text-base-content/80">
            {{ isPro ? 'Você está no plano Pro' : 'Você está no plano gratuito' }}
          </p>
          <p v-if="isPro" class="text-sm text-base-content/70">Transações ilimitadas ativas.</p>
        </section>

        <section class="rounded-xl border border-base-300 p-4">
          <h3 class="font-semibold">Uso mensal</h3>

          <template v-if="isPro">
            <p class="mt-2 text-sm text-base-content/80">
              {{ normalizedLimits.current_month_transactions }} transações realizadas este mês.
            </p>
          </template>

          <template v-else>
            <p class="mt-2 text-sm text-base-content/80">Transações este mês</p>
            <progress
              class="progress mt-2 w-full"
              :class="progressClass"
              :value="progressValue"
              max="100"
            ></progress>
            <p class="mt-2 text-sm text-base-content/70">
              {{ normalizedLimits.current_month_transactions }} de {{ normalizedLimits.monthly_transaction_limit }} transações utilizadas.
            </p>
            <p v-if="isAtLimit" class="mt-2 text-sm font-medium text-error">
              Limite atingido. Novas transações estão bloqueadas.
            </p>
            <p v-else-if="isNearLimit" class="mt-2 text-sm font-medium text-warning">
              Você está próximo do limite.
            </p>
          </template>
        </section>

        <section v-if="!isPro" class="rounded-xl border border-primary/30 bg-primary/5 p-4">
          <h3 class="font-semibold text-primary">Upgrade para o Pro</h3>
          <ul class="mt-3 space-y-1 text-sm text-base-content/80">
            <li>✓ Transações ilimitadas</li>
            <li>✓ Exportação de relatórios PDF e CSV</li>
            <li>✓ Dashboard inteligente avançado</li>
            <li>✓ Suporte prioritário</li>
          </ul>
          <button class="btn btn-primary mt-4" @click="handleUpgradeClick">Fazer upgrade</button>
          <p class="mt-2 text-xs text-base-content/70">
            Você será redirecionado para o checkout seguro da Cakto. Após o pagamento, seu plano será ativado automaticamente.
          </p>
        </section>

        <section v-else class="rounded-xl border border-success/30 bg-success/5 p-4">
          <p class="text-sm text-success">Obrigado por apoiar o projeto 🙌</p>
        </section>
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'
import { useNotifications } from '@/composables/useNotifications'
import { useSubscription } from '@/composables/useSubscription'

const { addNotification } = useNotifications()
const checkoutUrl = (import.meta.env.VITE_CAKTO_CHECKOUT_URL || '').trim()
const {
  limits,
  loading,
  error,
  isPro,
  usagePercent,
  isNearLimit,
  isAtLimit,
  fetchLimits,
} = useSubscription()

const normalizedLimits = computed(() => limits.value)

const progressValue = computed(() => Math.min(100, Math.max(0, usagePercent.value)))

const progressClass = computed(() => {
  if (isAtLimit.value) return 'progress-error'
  if (isNearLimit.value) return 'progress-warning'
  return 'progress-success'
})

const planBadgeClass = computed(() => {
  if (isPro.value) return 'badge-accent'
  return 'badge-neutral'
})

function handleUpgradeClick() {
  if (checkoutUrl) {
    window.open(checkoutUrl, '_blank', 'noopener,noreferrer')
    return
  }
  addNotification('Checkout indisponível no momento. Verifique VITE_CAKTO_CHECKOUT_URL.', 'error')
}

function retryFetch() {
  fetchLimits({ force: true }).catch(() => undefined)
}
</script>
