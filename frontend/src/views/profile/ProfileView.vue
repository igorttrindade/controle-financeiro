<template>
  <div class="min-h-screen bg-base-200 text-base-content">
    <Navbar />

    <main class="mx-auto w-full max-w-6xl px-4 pb-10 pt-24 md:px-8">
      <header class="mb-6">
        <h1 class="text-3xl font-bold">Configuração de Conta</h1>
        <p class="mt-1 text-sm text-base-content/70">
          Gerencie seu perfil, preferências visuais e segurança da conta.
        </p>
      </header>

      <div v-if="loadError" class="alert alert-error mb-4">
        <span>{{ loadError }}</span>
      </div>

      <div class="tabs tabs-boxed mb-5 w-fit bg-base-100">
        <button class="tab" :class="{ 'tab-active': currentTab === 'overview' }" @click="setTab('overview')">Perfil</button>
        <button class="tab" :class="{ 'tab-active': currentTab === 'settings' }" @click="setTab('settings')">Configurações</button>
        <button class="tab" :class="{ 'tab-active': currentTab === 'security' }" @click="setTab('security')">Segurança</button>
        <button class="tab" :class="{ 'tab-active': currentTab === 'subscription' }" @click="setTab('subscription')">Assinatura</button>
      </div>

      <section v-if="isLoading" class="card border border-base-300 bg-base-100 shadow-card">
        <div class="card-body gap-3">
          <div class="skeleton h-6 w-48"></div>
          <div class="skeleton h-12 w-full"></div>
          <div class="skeleton h-12 w-full"></div>
        </div>
      </section>

      <section v-else>
        <div v-if="currentTab === 'overview'" class="grid gap-4 lg:grid-cols-[340px,1fr]">
          <article class="card border border-base-300 bg-base-100 shadow-card">
            <div class="card-body">
              <h2 class="card-title">Foto de perfil</h2>

              <div class="mt-2 flex items-center gap-4">
                <div class="avatar">
                  <div class="w-20 rounded-full border border-base-300 bg-base-200">
                    <img :src="avatarDisplay" alt="Avatar do usuário" />
                  </div>
                </div>

                <div class="text-sm text-base-content/70">
                  <p>Formatos: JPG, PNG ou WebP</p>
                  <p>Tamanho máximo: 2MB</p>
                </div>
              </div>

              <input type="file" accept="image/jpeg,image/png,image/webp" class="file-input file-input-bordered mt-4" @change="onAvatarChange" />

              <p v-if="avatarError" class="mt-2 text-sm text-error">{{ avatarError }}</p>

              <div class="mt-4 flex flex-wrap gap-2">
                <button class="btn btn-primary" :class="{ loading: avatarSaving }" :disabled="avatarSaving || !selectedAvatarFile" @click="saveAvatar">
                  {{ avatarSaving ? 'Salvando...' : 'Salvar foto' }}
                </button>
                <button class="btn btn-outline" :class="{ loading: avatarRemoving }" :disabled="avatarRemoving || !profile.has_avatar" @click="removeAvatar">
                  {{ avatarRemoving ? 'Removendo...' : 'Remover foto' }}
                </button>
              </div>
            </div>
          </article>

          <article class="card border border-base-300 bg-base-100 shadow-card">
            <div class="card-body">
              <h2 class="card-title">Dados básicos</h2>

              <label class="form-control mt-2">
                <div class="label"><span class="label-text">Nome</span></div>
                <input v-model="profileForm.name_user" class="input input-bordered" type="text" />
                <div v-if="profileErrors.name_user" class="label"><span class="label-text-alt text-error">{{ profileErrors.name_user }}</span></div>
              </label>

              <label class="form-control mt-2">
                <div class="label"><span class="label-text">E-mail</span></div>
                <input :value="profile.email_user" class="input input-bordered" type="email" disabled />
              </label>

              <label class="form-control mt-2">
                <div class="label"><span class="label-text">Telefone</span></div>
                <input v-model="profileForm.tel_user" class="input input-bordered" type="text" placeholder="(11) 99999-9999" />
                <div v-if="profileErrors.tel_user" class="label"><span class="label-text-alt text-error">{{ profileErrors.tel_user }}</span></div>
              </label>

              <div class="mt-4">
                <button class="btn btn-primary" :class="{ loading: profileSaving }" :disabled="profileSaving" @click="saveProfile">
                  {{ profileSaving ? 'Salvando...' : 'Salvar dados' }}
                </button>
              </div>
            </div>
          </article>
        </div>

        <article v-else-if="currentTab === 'settings'" class="card border border-base-300 bg-base-100 shadow-card">
          <div class="card-body max-w-lg">
            <h2 class="card-title">Preferências visuais</h2>

            <label class="form-control mt-2">
              <div class="label"><span class="label-text">Tema</span></div>
              <select v-model="settingsForm.theme" class="select select-bordered">
                <option value="light">Claro</option>
                <option value="dark">Escuro</option>
              </select>
            </label>

            <div class="mt-4">
              <button class="btn btn-primary" :class="{ loading: settingsSaving }" :disabled="settingsSaving" @click="saveSettings">
                {{ settingsSaving ? 'Salvando...' : 'Salvar preferências' }}
              </button>
            </div>
          </div>
        </article>

        <article v-else-if="currentTab === 'security'" class="grid gap-4 lg:grid-cols-2">
          <section class="card border border-base-300 bg-base-100 shadow-card">
            <div class="card-body">
              <h2 class="card-title">Alterar e-mail</h2>

              <label class="form-control mt-2">
                <div class="label"><span class="label-text">Novo e-mail</span></div>
                <input v-model="securityForm.new_email" class="input input-bordered" type="email" placeholder="novo@email.com" />
              </label>

              <p v-if="securityErrors.new_email" class="mt-2 text-sm text-error">{{ securityErrors.new_email }}</p>

              <button class="btn btn-primary mt-4" :class="{ loading: securityRequestingEmail }" :disabled="securityRequestingEmail" @click="requestEmailChange">
                {{ securityRequestingEmail ? 'Gerando...' : 'Solicitar alteração de e-mail' }}
              </button>
            </div>
          </section>

          <section class="card border border-base-300 bg-base-100 shadow-card">
            <div class="card-body">
              <h2 class="card-title">Alterar senha</h2>

              <label class="form-control mt-2">
                <div class="label"><span class="label-text">Nova senha</span></div>
                <input v-model="securityForm.new_password" class="input input-bordered" type="password" />
              </label>

              <p v-if="securityErrors.new_password" class="mt-2 text-sm text-error">{{ securityErrors.new_password }}</p>

              <button class="btn btn-primary mt-4" :class="{ loading: securityRequestingPassword }" :disabled="securityRequestingPassword" @click="requestPasswordChange">
                {{ securityRequestingPassword ? 'Gerando...' : 'Solicitar alteração de senha' }}
              </button>
            </div>
          </section>

          <section class="card border border-base-300 bg-base-100 shadow-card lg:col-span-2">
            <div class="card-body">
              <h2 class="card-title">Confirmação de segurança (mock)</h2>
              <p class="text-sm text-base-content/70">Cole o token recebido ou use o token gerado automaticamente nesta tela.</p>

              <label class="form-control mt-2 max-w-md">
                <div class="label"><span class="label-text">Token de confirmação</span></div>
                <input v-model="securityForm.token" class="input input-bordered" type="text" placeholder="token" />
              </label>

              <p v-if="securityMockUrl" class="mt-3 text-sm text-base-content/70 break-all">
                Link mock: {{ securityMockUrl }}
              </p>

              <div class="mt-4">
                <button class="btn btn-primary" :class="{ loading: securityConfirming }" :disabled="securityConfirming || !securityForm.token" @click="confirmSecurity">
                  {{ securityConfirming ? 'Confirmando...' : 'Confirmar alteração' }}
                </button>
              </div>
            </div>
          </section>
        </article>

        <SubscriptionSection v-else />
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Navbar from '@/components/layout/Navbar.vue'
import { useNotifications } from '@/composables/useNotifications'
import { useSubscription } from '@/composables/useSubscription'
import { useTheme } from '@/composables/useTheme'
import {
  confirmSecurityChange,
  deleteMyAvatar,
  fetchMyAvatarObjectUrl,
  getMyProfile,
  requestSecurityChange,
  updateMyProfile,
  uploadMyAvatar,
} from '@/services/profile/profile.service'
import {
  validateAvatarFile,
  validateEmailChange,
  validatePasswordChange,
  validateProfileBasics,
} from '@/utils/profileValidators'
import SubscriptionSection from '@/views/profile/components/SubscriptionSection.vue'

const route = useRoute()
const router = useRouter()
const { addNotification } = useNotifications()
const { setTheme } = useTheme()
const { fetchLimits, hasLoaded } = useSubscription()

const isLoading = ref(true)
const loadError = ref('')
const profileSaving = ref(false)
const settingsSaving = ref(false)
const avatarSaving = ref(false)
const avatarRemoving = ref(false)
const securityRequestingEmail = ref(false)
const securityRequestingPassword = ref(false)
const securityConfirming = ref(false)

const profile = ref({
  name_user: '',
  email_user: '',
  tel_user: '',
  theme: 'light',
  has_avatar: false,
  avatar_updated_at: null,
})

const profileForm = ref({
  name_user: '',
  tel_user: '',
})

const settingsForm = ref({
  theme: 'light',
})

const securityForm = ref({
  new_email: '',
  new_password: '',
  token: '',
})

const profileErrors = ref({})
const securityErrors = ref({})
const avatarError = ref('')
const selectedAvatarFile = ref(null)
const avatarPreviewUrl = ref('')
const avatarObjectUrl = ref('')
const securityMockUrl = ref('')

const currentTab = computed(() => {
  const tab = String(route.query.tab || 'overview')
  if (tab === 'settings' || tab === 'security' || tab === 'subscription') return tab
  return 'overview'
})

const defaultAvatar = computed(() => {
  const initial = String(profile.value.name_user || '?').trim().charAt(0).toUpperCase() || '?'
  const svg = `<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 120 120'><rect width='120' height='120' fill='#0f172a'/><text x='50%' y='54%' dominant-baseline='middle' text-anchor='middle' font-family='Arial, sans-serif' font-size='52' fill='#ffffff'>${initial}</text></svg>`
  return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`
})

const avatarDisplay = computed(() => {
  if (avatarPreviewUrl.value) return avatarPreviewUrl.value
  if (profile.value.has_avatar && avatarObjectUrl.value) return avatarObjectUrl.value
  return defaultAvatar.value
})

function setTab(tab) {
  router.replace({ query: { ...route.query, tab } })
}

function handleUnauthorized(error) {
  if (error?.response?.status !== 401) return false
  localStorage.removeItem('token')
  localStorage.removeItem('userId')
  router.push('/login')
  return true
}

async function loadProfile() {
  isLoading.value = true
  loadError.value = ''
  try {
    const data = await getMyProfile()
    profile.value = {
      name_user: data.name_user || '',
      email_user: data.email_user || '',
      tel_user: data.tel_user || '',
      theme: data.theme || 'light',
      has_avatar: Boolean(data.has_avatar),
      avatar_updated_at: data.avatar_updated_at || null,
    }

    profileForm.value.name_user = profile.value.name_user
    profileForm.value.tel_user = profile.value.tel_user
    settingsForm.value.theme = profile.value.theme
    setTheme(profile.value.theme, { persist: false })
    if (profile.value.has_avatar) {
      const nextObjectUrl = await fetchMyAvatarObjectUrl()
      if (avatarObjectUrl.value) {
        URL.revokeObjectURL(avatarObjectUrl.value)
      }
      avatarObjectUrl.value = nextObjectUrl || ''
    } else {
      if (avatarObjectUrl.value) {
        URL.revokeObjectURL(avatarObjectUrl.value)
      }
      avatarObjectUrl.value = ''
    }
  } catch (error) {
    if (handleUnauthorized(error)) return
    loadError.value = error?.response?.data?.error || 'Não foi possível carregar seu perfil.'
  } finally {
    isLoading.value = false
  }
}

function onAvatarChange(event) {
  avatarError.value = ''
  const [file] = event.target.files || []
  const validation = validateAvatarFile(file)
  if (!validation.isValid) {
    selectedAvatarFile.value = null
    avatarPreviewUrl.value = ''
    avatarError.value = validation.error
    return
  }

  selectedAvatarFile.value = file
  avatarPreviewUrl.value = URL.createObjectURL(file)
}

async function saveAvatar() {
  avatarError.value = ''
  const validation = validateAvatarFile(selectedAvatarFile.value)
  if (!validation.isValid) {
    avatarError.value = validation.error
    return
  }

  avatarSaving.value = true
  try {
    await uploadMyAvatar(selectedAvatarFile.value)
    profile.value.has_avatar = true
    profile.value.avatar_updated_at = new Date().toISOString()
    const nextObjectUrl = await fetchMyAvatarObjectUrl()
    if (avatarObjectUrl.value) {
      URL.revokeObjectURL(avatarObjectUrl.value)
    }
    avatarObjectUrl.value = nextObjectUrl || ''
    selectedAvatarFile.value = null
    avatarPreviewUrl.value = ''
    window.dispatchEvent(new Event('profile-avatar-updated'))
    addNotification('Avatar atualizado com sucesso.', 'success')
  } catch (error) {
    if (handleUnauthorized(error)) return
    avatarError.value = error?.response?.data?.error || 'Falha ao enviar avatar.'
  } finally {
    avatarSaving.value = false
  }
}

async function removeAvatar() {
  avatarRemoving.value = true
  avatarError.value = ''
  try {
    await deleteMyAvatar()
    profile.value.has_avatar = false
    profile.value.avatar_updated_at = null
    avatarPreviewUrl.value = ''
    selectedAvatarFile.value = null
    if (avatarObjectUrl.value) {
      URL.revokeObjectURL(avatarObjectUrl.value)
    }
    avatarObjectUrl.value = ''
    window.dispatchEvent(new Event('profile-avatar-updated'))
    addNotification('Avatar removido com sucesso.', 'success')
  } catch (error) {
    if (handleUnauthorized(error)) return
    avatarError.value = error?.response?.data?.error || 'Não foi possível remover o avatar.'
  } finally {
    avatarRemoving.value = false
  }
}

async function saveProfile() {
  profileErrors.value = {}
  const validation = validateProfileBasics(profileForm.value)
  if (!validation.isValid) {
    profileErrors.value = validation.errors
    return
  }

  profileSaving.value = true
  try {
    const payload = {
      name_user: validation.normalized.name_user,
      tel_user: validation.normalized.tel_user,
    }
    await updateMyProfile(payload)
    profile.value.name_user = payload.name_user
    profile.value.tel_user = payload.tel_user
    addNotification('Dados atualizados com sucesso.', 'success')
  } catch (error) {
    if (handleUnauthorized(error)) return
    addNotification(error?.response?.data?.error || 'Falha ao salvar dados.', 'error')
  } finally {
    profileSaving.value = false
  }
}

async function saveSettings() {
  settingsSaving.value = true
  try {
    await updateMyProfile({ theme: settingsForm.value.theme })
    setTheme(settingsForm.value.theme)
    profile.value.theme = settingsForm.value.theme
    addNotification('Tema atualizado com sucesso.', 'success')
  } catch (error) {
    if (handleUnauthorized(error)) return
    addNotification(error?.response?.data?.error || 'Falha ao salvar preferências.', 'error')
  } finally {
    settingsSaving.value = false
  }
}

async function requestEmailChange() {
  securityErrors.value = {}
  const validation = validateEmailChange(securityForm.value.new_email)
  if (!validation.isValid) {
    securityErrors.value.new_email = validation.error
    return
  }

  securityRequestingEmail.value = true
  try {
    const response = await requestSecurityChange({
      change_type: 'email_change',
      new_email: validation.value,
    })
    securityForm.value.token = response.token
    securityMockUrl.value = response.confirmation_url
    addNotification('Solicitação criada. Confirme usando o token mock.', 'info')
  } catch (error) {
    if (handleUnauthorized(error)) return
    addNotification(error?.response?.data?.error || 'Falha ao solicitar alteração de e-mail.', 'error')
  } finally {
    securityRequestingEmail.value = false
  }
}

async function requestPasswordChange() {
  securityErrors.value = {}
  const validation = validatePasswordChange(securityForm.value.new_password)
  if (!validation.isValid) {
    securityErrors.value.new_password = validation.error
    return
  }

  securityRequestingPassword.value = true
  try {
    const response = await requestSecurityChange({
      change_type: 'password_change',
      new_password: validation.value,
    })
    securityForm.value.token = response.token
    securityMockUrl.value = response.confirmation_url
    securityForm.value.new_password = ''
    addNotification('Solicitação criada. Confirme usando o token mock.', 'info')
  } catch (error) {
    if (handleUnauthorized(error)) return
    addNotification(error?.response?.data?.error || 'Falha ao solicitar alteração de senha.', 'error')
  } finally {
    securityRequestingPassword.value = false
  }
}

async function confirmSecurity() {
  securityConfirming.value = true
  try {
    await confirmSecurityChange({ token: securityForm.value.token })
    securityMockUrl.value = ''
    securityForm.value.token = ''
    securityForm.value.new_email = ''
    addNotification('Alteração de segurança confirmada.', 'success')
    await loadProfile()
  } catch (error) {
    if (handleUnauthorized(error)) return
    addNotification(error?.response?.data?.error || 'Falha ao confirmar alteração.', 'error')
  } finally {
    securityConfirming.value = false
  }
}

onMounted(async () => {
  const tokenFromQuery = String(route.query.token || '').trim()
  if (tokenFromQuery) {
    securityForm.value.token = tokenFromQuery
    setTab('security')
  }

  await loadProfile()
})

watch(
  currentTab,
  async (tab) => {
    if (tab !== 'subscription' || hasLoaded.value) return
    try {
      await fetchLimits()
    } catch (error) {
      handleUnauthorized(error)
    }
  },
  { immediate: true },
)

onBeforeUnmount(() => {
  if (avatarPreviewUrl.value) {
    URL.revokeObjectURL(avatarPreviewUrl.value)
  }
  if (avatarObjectUrl.value) {
    URL.revokeObjectURL(avatarObjectUrl.value)
  }
})
</script>
