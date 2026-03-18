<template>
  <nav class="navbar fixed left-0 top-0 z-50 border-b border-base-300 bg-base-100/90 px-4 backdrop-blur md:px-6">
    <div class="navbar-start gap-2">
      <RouterLink to="/" class="btn btn-ghost px-2 text-lg font-semibold normal-case">
        <img src="@/assets/finance_logo.png" alt="FinanceFlow" class="h-8 w-8" />
        <span>FinanceFlow</span>
      </RouterLink>

      <ul class="menu menu-horizontal hidden gap-1 px-1 md:flex">
        <li><RouterLink to="/" active-class="active">Início</RouterLink></li>
        <li><RouterLink to="/dashboard" active-class="active">Dashboard</RouterLink></li>
        <li><RouterLink to="/transactions" active-class="active">Transações</RouterLink></li>
      </ul>
    </div>

    <div class="navbar-end gap-2">
      <button
        v-if="showSubscriptionAlert"
        type="button"
        class="btn btn-sm"
        :class="isAtLimit ? 'btn-error btn-outline' : 'btn-warning btn-outline'"
        :aria-label="subscriptionAlertLabel"
        @click="goToSubscriptionTab"
      >
        {{ subscriptionAlertLabel }}
      </button>

      <div class="dropdown dropdown-end">
        <button tabindex="0" class="btn btn-ghost btn-circle avatar">
          <div class="w-9 rounded-full bg-base-300 p-0.5">
            <img :src="avatarSrc" alt="Perfil" />
          </div>
        </button>
        <ul
          tabindex="0"
          class="menu dropdown-content z-[60] mt-3 w-56 rounded-box border border-base-300 bg-base-100 p-2 shadow"
        >
          <li class="menu-title"><span>Sessão ativa</span></li>
          <li><button type="button" @click="goToProfile('overview')">Perfil</button></li>
          <li><button type="button" @click="goToProfile('settings')">Configurações</button></li>
          <li><button type="button" @click="goToProfile('security')">Segurança</button></li>
          <li><button type="button" @click="goToProfile('subscription')">Assinatura</button></li>
          <li><button type="button" @click="logout">Sair</button></li>
        </ul>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useSubscription } from '@/composables/useSubscription'
import { fetchMyAvatarObjectUrl, getMyProfile } from '@/services/profile/profile.service'

defineOptions({ name: 'AppNavbar' })

const router = useRouter()
const {
  limits,
  hasLoaded,
  isPro,
  isNearLimit,
  isAtLimit,
  fetchLimits,
} = useSubscription()
const hasAvatar = ref(false)
const avatarObjectUrl = ref('')
const avatarFallback = 'data:image/svg+xml;charset=UTF-8,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 120 120%22%3E%3Crect width=%22120%22 height=%22120%22 fill=%22%230f172a%22/%3E%3Ctext x=%2250%25%22 y=%2254%25%22 dominant-baseline=%22middle%22 text-anchor=%22middle%22 font-family=%22Arial,sans-serif%22 font-size=%2252%22 fill=%22%23fff%22%3E%3F%3C/text%3E%3C/svg%3E'

const avatarSrc = computed(() => {
  if (hasAvatar.value && avatarObjectUrl.value) return avatarObjectUrl.value
  return avatarFallback
})

const showSubscriptionAlert = computed(() => {
  if (!hasLoaded.value || !limits.value) return false
  if (isPro.value) return false
  return isNearLimit.value || isAtLimit.value
})

const subscriptionAlertLabel = computed(() => (isAtLimit.value ? 'Limite atingido' : 'Próximo do limite'))

function goToProfile(tab) {
  router.push({ path: '/profile', query: { tab } })
}

function goToSubscriptionTab() {
  router.push({ path: '/profile', query: { tab: 'subscription' } })
}

async function refreshAvatar() {
  const token = localStorage.getItem('token')
  if (!token) {
    hasAvatar.value = false
    return
  }

  try {
    const profile = await getMyProfile()
    hasAvatar.value = Boolean(profile?.has_avatar)
    if (!hasAvatar.value) {
      if (avatarObjectUrl.value) {
        URL.revokeObjectURL(avatarObjectUrl.value)
      }
      avatarObjectUrl.value = ''
      return
    }

    const nextObjectUrl = await fetchMyAvatarObjectUrl()
    if (avatarObjectUrl.value) {
      URL.revokeObjectURL(avatarObjectUrl.value)
    }
    avatarObjectUrl.value = nextObjectUrl || ''
  } catch {
    hasAvatar.value = false
    if (avatarObjectUrl.value) {
      URL.revokeObjectURL(avatarObjectUrl.value)
    }
    avatarObjectUrl.value = ''
  }
}

function onAvatarUpdated() {
  refreshAvatar()
}

function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('userId')
  router.push('/login')
}

onMounted(() => {
  refreshAvatar()
  const token = localStorage.getItem('token')
  if (token) {
    fetchLimits().catch(() => undefined)
  }
  window.addEventListener('profile-avatar-updated', onAvatarUpdated)
})

onBeforeUnmount(() => {
  window.removeEventListener('profile-avatar-updated', onAvatarUpdated)
  if (avatarObjectUrl.value) {
    URL.revokeObjectURL(avatarObjectUrl.value)
  }
})
</script>
