<template>
  <div class="min-h-screen bg-gradient-to-br from-[#f7fbf7] via-white to-[#fff6ea] text-[#0a1628]">
    <header class="border-b border-[#0a1628]/8 bg-white/80 backdrop-blur-sm">
      <div class="mx-auto flex max-w-7xl items-center justify-between px-6 py-5 lg:px-8">
        <RouterLink to="/" class="flex items-center gap-3">
          <div class="flex h-11 w-11 items-center justify-center rounded-2xl bg-[#4caf50]/10">
            <DinoMascot :size="34" />
          </div>
          <span class="text-xl font-semibold tracking-tight">Dinance</span>
        </RouterLink>

        <RouterLink
          to="/login"
          class="inline-flex items-center rounded-full border border-[#4caf50]/20 bg-[#4caf50]/8 px-5 py-2.5 text-sm font-semibold text-[#4caf50] transition-colors hover:bg-[#4caf50]/14"
        >
          Já tenho conta
        </RouterLink>
      </div>
    </header>

    <main class="mx-auto grid max-w-7xl items-center gap-16 px-6 py-12 lg:grid-cols-[0.9fr_1.1fr] lg:px-8 lg:py-16">
      <section class="flex flex-col items-center text-center lg:items-start lg:text-left">
        <div class="rounded-[2.5rem] bg-white/75 p-6 shadow-xl shadow-[#0a1628]/5">
          <DinoMascot :size="270" />
        </div>

        <h1 class="mt-8 max-w-xl text-4xl font-bold tracking-tight text-[#0a1628] lg:text-5xl">
          Junte-se a uma rotina financeira mais organizada.
        </h1>
        <p class="mt-4 max-w-lg text-lg leading-8 text-[#0a1628]/65">
          Crie sua conta para centralizar lançamentos, acompanhar indicadores e construir uma visão mais confiável do seu dinheiro.
        </p>

        <div class="mt-8 space-y-4">
          <div v-for="benefit in benefits" :key="benefit" class="flex items-center gap-3 rounded-full bg-white px-4 py-3 text-sm text-[#0a1628]/75 shadow-sm">
            <span class="flex h-8 w-8 items-center justify-center rounded-full bg-[#4caf50] text-base font-bold text-white">✓</span>
            <span>{{ benefit }}</span>
          </div>
        </div>
      </section>

      <section>
        <div class="rounded-[2rem] border-2 border-[#0a1628]/6 bg-white p-8 shadow-2xl shadow-[#0a1628]/10 sm:p-10">
          <div>
            <h2 class="text-4xl font-bold tracking-tight text-[#0a1628]">Criar conta</h2>
            <p class="mt-3 text-base leading-7 text-[#0a1628]/65">
              Já tem uma conta?
              <RouterLink to="/login" class="font-semibold text-[#4caf50] transition-colors hover:text-[#449e48]">
                Faça login
              </RouterLink>
            </p>
          </div>

          <form class="mt-8 grid gap-5 md:grid-cols-2" @submit.prevent="handleRegister">
            <label class="block md:col-span-2">
              <span class="mb-2 block text-sm font-semibold">Nome completo</span>
              <div class="relative">
                <span class="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-[#0a1628]/35">
                  <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 12a4 4 0 1 0-4-4 4 4 0 0 0 4 4Z" />
                    <path stroke-linecap="round" stroke-linejoin="round" d="M5 20a7 7 0 0 1 14 0" />
                  </svg>
                </span>
                <input
                  v-model="nameUser"
                  type="text"
                  class="w-full rounded-full border-2 border-[#0a1628]/10 bg-white py-3.5 pl-12 pr-4 outline-none transition-colors placeholder:text-[#0a1628]/35 focus:border-[#4caf50]"
                  placeholder="Seu nome"
                  autocomplete="name"
                />
              </div>
            </label>

            <label class="block md:col-span-2">
              <span class="mb-2 block text-sm font-semibold">Email</span>
              <div class="relative">
                <span class="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-[#0a1628]/35">
                  <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16v12H4z" />
                    <path stroke-linecap="round" stroke-linejoin="round" d="m4 7 8 6 8-6" />
                  </svg>
                </span>
                <input
                  v-model="emailUser"
                  type="email"
                  class="w-full rounded-full border-2 border-[#0a1628]/10 bg-white py-3.5 pl-12 pr-4 outline-none transition-colors placeholder:text-[#0a1628]/35 focus:border-[#4caf50]"
                  placeholder="seu@email.com"
                  autocomplete="email"
                />
              </div>
            </label>

            <label class="block">
              <span class="mb-2 block text-sm font-semibold">Data de nascimento</span>
              <input
                v-model="dtNascimentoUser"
                type="date"
                class="w-full rounded-full border-2 border-[#0a1628]/10 bg-white px-4 py-3.5 outline-none transition-colors focus:border-[#4caf50]"
              />
            </label>

            <label class="block">
              <span class="mb-2 block text-sm font-semibold">Celular</span>
              <div class="relative">
                <span class="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-[#0a1628]/35">
                  <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                    <rect x="7" y="2.5" width="10" height="19" rx="2" />
                    <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 18.5h3" />
                  </svg>
                </span>
                <input
                  v-model="celUser"
                  type="text"
                  inputmode="numeric"
                  maxlength="11"
                  class="w-full rounded-full border-2 border-[#0a1628]/10 bg-white py-3.5 pl-12 pr-4 outline-none transition-colors placeholder:text-[#0a1628]/35 focus:border-[#4caf50]"
                  placeholder="DDD + número"
                  @input="normalizePhone"
                />
              </div>
            </label>

            <label class="block">
              <span class="mb-2 block text-sm font-semibold">Senha</span>
              <div class="relative">
                <span class="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-[#0a1628]/35">
                  <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M7 11V8a5 5 0 0 1 10 0v3" />
                    <rect x="5" y="11" width="14" height="10" rx="2" />
                  </svg>
                </span>
                <input
                  v-model="passwordUser"
                  :type="showPassword ? 'text' : 'password'"
                  class="w-full rounded-full border-2 border-[#0a1628]/10 bg-white py-3.5 pl-12 pr-12 outline-none transition-colors placeholder:text-[#0a1628]/35 focus:border-[#4caf50]"
                  placeholder="Mínimo 6 caracteres"
                  autocomplete="new-password"
                />
                <button
                  type="button"
                  class="absolute right-4 top-1/2 -translate-y-1/2 text-[#0a1628]/40 transition-colors hover:text-[#4caf50]"
                  @click="showPassword = !showPassword"
                >
                  <svg v-if="showPassword" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M3 3l18 18" />
                    <path stroke-linecap="round" stroke-linejoin="round" d="M10.6 10.7A3 3 0 0 0 13.3 13.4" />
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9.9 5.1A10.9 10.9 0 0 1 12 5c5.5 0 9.5 4.3 10 7-.2 1.1-1.1 2.9-2.8 4.5" />
                    <path stroke-linecap="round" stroke-linejoin="round" d="M6.2 6.2C4.1 7.6 2.6 9.7 2 12c.5 2.7 4.5 7 10 7 1.8 0 3.4-.4 4.8-1.1" />
                  </svg>
                  <svg v-else class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7-10-7-10-7Z" />
                    <circle cx="12" cy="12" r="3" />
                  </svg>
                </button>
              </div>
            </label>

            <label class="block">
              <span class="mb-2 block text-sm font-semibold">Confirmar senha</span>
              <div class="relative">
                <span class="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-[#0a1628]/35">
                  <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M7 11V8a5 5 0 0 1 10 0v3" />
                    <rect x="5" y="11" width="14" height="10" rx="2" />
                  </svg>
                </span>
                <input
                  v-model="confirmPassword"
                  :type="showConfirmPassword ? 'text' : 'password'"
                  class="w-full rounded-full border-2 border-[#0a1628]/10 bg-white py-3.5 pl-12 pr-12 outline-none transition-colors placeholder:text-[#0a1628]/35 focus:border-[#4caf50]"
                  placeholder="Repita a senha"
                  autocomplete="new-password"
                />
                <button
                  type="button"
                  class="absolute right-4 top-1/2 -translate-y-1/2 text-[#0a1628]/40 transition-colors hover:text-[#4caf50]"
                  @click="showConfirmPassword = !showConfirmPassword"
                >
                  <svg v-if="showConfirmPassword" class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M3 3l18 18" />
                    <path stroke-linecap="round" stroke-linejoin="round" d="M10.6 10.7A3 3 0 0 0 13.3 13.4" />
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9.9 5.1A10.9 10.9 0 0 1 12 5c5.5 0 9.5 4.3 10 7-.2 1.1-1.1 2.9-2.8 4.5" />
                    <path stroke-linecap="round" stroke-linejoin="round" d="M6.2 6.2C4.1 7.6 2.6 9.7 2 12c.5 2.7 4.5 7 10 7 1.8 0 3.4-.4 4.8-1.1" />
                  </svg>
                  <svg v-else class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7-10-7-10-7Z" />
                    <circle cx="12" cy="12" r="3" />
                  </svg>
                </button>
              </div>
            </label>

            <label class="md:col-span-2 flex items-start gap-3 rounded-[1.5rem] bg-[#f7fbf7] p-4 text-sm leading-6 text-[#0a1628]/65">
              <input
                v-model="acceptTerms"
                type="checkbox"
                class="mt-1 h-4 w-4 rounded border-[#0a1628]/20 text-[#4caf50] focus:ring-[#4caf50]"
              />
              <span>
                Eu aceito os
                <a href="#" class="font-semibold text-[#4caf50] transition-colors hover:text-[#449e48]" @click.prevent>Termos de Uso</a>
                e a
                <a href="#" class="font-semibold text-[#4caf50] transition-colors hover:text-[#449e48]" @click.prevent>Política de Privacidade</a>.
              </span>
            </label>

            <button
              type="submit"
              class="inline-flex w-full items-center justify-center rounded-full bg-[#4caf50] px-6 py-4 text-lg font-semibold text-white shadow-xl shadow-[#4caf50]/20 transition-all hover:-translate-y-0.5 hover:bg-[#449e48] disabled:cursor-not-allowed disabled:opacity-70 md:col-span-2"
              :disabled="isLoading"
            >
              {{ isLoading ? 'Criando conta...' : 'Criar conta grátis' }}
              <span v-if="!isLoading" class="ml-3 text-lg">→</span>
            </button>
          </form>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import DinoMascot from '@/components/branding/DinoMascot.vue'
import { registerUser } from '@/services/auth/auth.service'
import { useNotifications } from '@/composables/useNotifications'

const { addNotification } = useNotifications()
const router = useRouter()

const benefits = [
  '100% gratuito para começar',
  'Sem cartão de crédito nesta etapa',
  'Fluxo preparado para acompanhar sua rotina desde o primeiro dia',
]

const nameUser = ref('')
const emailUser = ref('')
const dtNascimentoUser = ref('')
const celUser = ref('')
const passwordUser = ref('')
const confirmPassword = ref('')
const acceptTerms = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const isLoading = ref(false)

function normalizePhone(event) {
  celUser.value = event.target.value.replace(/\D/g, '').slice(0, 11)
}

async function handleRegister() {
  if (!nameUser.value || !emailUser.value || !dtNascimentoUser.value || !celUser.value || !passwordUser.value || !confirmPassword.value) {
    addNotification('Preencha todos os campos antes de continuar.', 'warning')
    return
  }

  if (passwordUser.value.length < 6) {
    addNotification('A senha deve conter pelo menos 6 caracteres.', 'warning')
    return
  }

  if (passwordUser.value !== confirmPassword.value) {
    addNotification('As senhas informadas não coincidem.', 'warning')
    return
  }

  if (!/^\d{11}$/.test(celUser.value)) {
    addNotification('O celular deve conter 11 dígitos (DDD + número).', 'warning')
    return
  }

  if (!acceptTerms.value) {
    addNotification('Você precisa aceitar os termos para criar a conta.', 'warning')
    return
  }

  isLoading.value = true

  try {
    await registerUser({
      name_user: nameUser.value,
      email_user: emailUser.value,
      dt_nascimento_user: dtNascimentoUser.value,
      tel_user: celUser.value,
      password: passwordUser.value,
    })

    addNotification('Conta criada com sucesso. Redirecionando para login...', 'success')
    setTimeout(() => router.push('/login'), 1400)
  } catch (err) {
    if (err.response?.status === 409) {
      addNotification('Este e-mail já está cadastrado.', 'warning')
    } else {
      addNotification('Erro ao criar conta. Tente novamente.', 'error')
    }
    console.error(err)
  } finally {
    isLoading.value = false
  }
}
</script>
