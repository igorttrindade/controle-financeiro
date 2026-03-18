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
          to="/register"
          class="inline-flex items-center rounded-full border border-[#4caf50]/20 bg-[#4caf50]/8 px-5 py-2.5 text-sm font-semibold text-[#4caf50] transition-colors hover:bg-[#4caf50]/14"
        >
          Criar conta
        </RouterLink>
      </div>
    </header>

    <main class="mx-auto grid min-h-[calc(100vh-84px)] max-w-7xl items-center gap-16 px-6 py-12 lg:grid-cols-2 lg:px-8 lg:py-16">
      <section class="order-2 flex flex-col items-center text-center lg:order-1 lg:items-start lg:text-left">
        <div class="rounded-[2.5rem] bg-white/75 p-6/5">
          <DinoMascot :size="270" />
        </div>

        <h1 class="mt-8 max-w-xl text-4xl font-bold tracking-tight text-[#0a1628] lg:text-5xl">
          Bem-vindo de volta ao seu controle financeiro.
        </h1>
        <p class="mt-4 max-w-lg text-lg leading-8 text-[#0a1628]/65">
          Entre para acompanhar lançamentos, revisar indicadores e continuar organizando sua rotina com clareza.
        </p>

        <div class="mt-8 grid w-full max-w-xl gap-4 sm:grid-cols-2">
          <article class="rounded-[1.75rem] border border-[#0a1628]/8 bg-white p-5 shadow-sm">
            <p class="text-sm font-semibold uppercase tracking-[0.24em] text-[#4caf50]">Saldo</p>
            <p class="mt-2 text-2xl font-bold">Visão mensal</p>
            <p class="mt-2 text-sm leading-6 text-[#0a1628]/60">Receitas e despesas reunidas em uma leitura rápida.</p>
          </article>
          <article class="rounded-[1.75rem] border border-[#0a1628]/8 bg-white p-5 shadow-sm">
            <p class="text-sm font-semibold uppercase tracking-[0.24em] text-[#ffa726]">Rotina</p>
            <p class="mt-2 text-2xl font-bold">Lançamentos claros</p>
            <p class="mt-2 text-sm leading-6 text-[#0a1628]/60">Categorias e transações no mesmo fluxo operacional.</p>
          </article>
        </div>
      </section>

      <section class="order-1 lg:order-2">
        <div class="rounded-[2rem] border-2 border-[#0a1628]/6 bg-white p-8 shadow-2xl shadow-[#0a1628]/10 sm:p-10">
          <div>
            <h2 class="text-4xl font-bold tracking-tight text-[#0a1628]">Entrar</h2>
            <p class="mt-3 text-base leading-7 text-[#0a1628]/65">
              Não tem uma conta?
              <RouterLink to="/register" class="font-semibold text-[#4caf50] transition-colors hover:text-[#449e48]">
                Cadastre-se grátis
              </RouterLink>
            </p>
          </div>

          <form class="mt-8 space-y-6" @submit.prevent="handleLoginUser">
            <label class="block">
              <span class="mb-2 block text-sm font-semibold text-[#0a1628]">Email</span>
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
                  class="w-full rounded-full border-2 border-[#0a1628]/10 bg-white py-3.5 pl-12 pr-4 text-[#0a1628] outline-none transition-colors placeholder:text-[#0a1628]/35 focus:border-[#4caf50]"
                  placeholder="seu@email.com"
                  autocomplete="email"
                />
              </div>
            </label>

            <label class="block">
              <span class="mb-2 block text-sm font-semibold text-[#0a1628]">Senha</span>
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
                  class="w-full rounded-full border-2 border-[#0a1628]/10 bg-white py-3.5 pl-12 pr-12 text-[#0a1628] outline-none transition-colors placeholder:text-[#0a1628]/35 focus:border-[#4caf50]"
                  placeholder="Digite sua senha"
                  autocomplete="current-password"
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

            <button
              type="submit"
              class="inline-flex w-full items-center justify-center rounded-full bg-[#4caf50] px-6 py-4 text-lg font-semibold text-white shadow-xl shadow-[#4caf50]/20 transition-all hover:-translate-y-0.5 hover:bg-[#449e48] disabled:cursor-not-allowed disabled:opacity-70"
              :disabled="isLoading"
            >
              {{ isLoading ? 'Entrando...' : 'Entrar' }}
              <span v-if="!isLoading" class="ml-3 text-lg">→</span>
            </button>
          </form>

          <div class="mt-8 rounded-[1.5rem] bg-[#f7fbf7] p-5 text-sm leading-7 text-[#0a1628]/65">
            Você continuará usando o fluxo atual de autenticação do sistema, com token salvo localmente e redirecionamento para a dashboard.
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import DinoMascot from '@/components/branding/DinoMascot.vue'
import { loginUser } from '@/services/auth/auth.service'
import { useNotifications } from '@/composables/useNotifications'

const { addNotification } = useNotifications()
const router = useRouter()

const emailUser = ref('')
const passwordUser = ref('')
const showPassword = ref(false)
const isLoading = ref(false)

async function handleLoginUser() {
  if (!emailUser.value || !passwordUser.value) {
    addNotification('Preencha seu e-mail e senha para continuar.', 'warning')
    return
  }

  isLoading.value = true

  try {
    const response = await loginUser({
      email_user: emailUser.value,
      password: passwordUser.value,
    })

    const token = response.token || response.data?.token
    const userId = response.user_id || response.data?.user_id

    localStorage.setItem('token', token)
    localStorage.setItem('userId', userId)

    addNotification('Login realizado com sucesso.', 'success')
    router.push('/dashboard')
  } catch (err) {
    addNotification('Ocorreu um erro ao entrar. Tente novamente.', 'error')
    console.error(err)
  } finally {
    isLoading.value = false
  }
}
</script>
