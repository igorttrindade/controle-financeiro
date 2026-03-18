<template>
  <div class="min-h-screen overflow-x-hidden bg-[#fffdf8] text-[#0a1628]">
    <div class="pointer-events-none absolute inset-0 overflow-hidden">
      <div class="absolute left-[-8rem] top-[-6rem] h-72 w-72 rounded-full bg-[#4caf50]/15 blur-3xl"></div>
      <div class="absolute right-[-5rem] top-20 h-64 w-64 rounded-full bg-[#ffa726]/15 blur-3xl"></div>
      <div class="absolute bottom-10 left-1/3 h-48 w-48 rounded-full bg-[#0a1628]/10 blur-3xl"></div>
    </div>

    <header class="relative z-10 border-b border-[#0a1628]/8 bg-white/80 backdrop-blur-sm">
      <div class="mx-auto flex max-w-7xl items-center justify-between px-6 py-5 lg:px-8">
        <RouterLink to="/" class="flex items-center gap-3">
          <div class="flex h-11 w-11 items-center justify-center">
            <DinoMascot :size="34" />
          </div>
          <span class="text-xl font-semibold tracking-tight text-[#0a1628]">Dinance</span>
        </RouterLink>

        <nav class="hidden items-center gap-8 text-sm font-medium lg:flex">
          <a href="#recursos" class="transition-colors hover:text-[#4caf50]">Recursos</a>
          <a href="#como-funciona" class="transition-colors hover:text-[#4caf50]">Como funciona</a>
          <a href="#precos" class="transition-colors hover:text-[#4caf50]">Preços</a>
        </nav>

        <div class="flex items-center gap-3">
          <RouterLink
            to="/login"
            class="hidden rounded-full px-5 py-2.5 text-sm font-semibold text-[#0a1628] transition-colors hover:text-[#4caf50] sm:inline-flex"
          >
            Entrar
          </RouterLink>
          <RouterLink
            to="/register"
            class="inline-flex items-center rounded-full bg-[#4caf50] px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-[#4caf50]/20 transition-all hover:-translate-y-0.5 hover:bg-[#449e48]"
          >
            Criar conta
          </RouterLink>
        </div>
      </div>
    </header>

    <main class="relative z-10">
      <section class="mx-auto max-w-7xl px-6 py-16 lg:px-8 lg:py-24">
        <div class="grid items-center gap-14 lg:grid-cols-[1.05fr_0.95fr]">
          <div>
            <span class="inline-flex rounded-full border border-[#4caf50]/20 bg-[#4caf50]/8 px-4 py-1.5 text-sm font-semibold text-[#4caf50]">
              Controle financeiro simples e inteligente
            </span>

            <h1 class="mt-6 max-w-3xl text-5xl font-bold leading-tight tracking-tight text-[#0a1628] lg:text-6xl">
              Organize seu dinheiro com um painel
              <span class="text-[#4caf50]"> mais claro</span>
              e decisões
              <span class="text-[#ffa726]"> mais rápidas</span>.
            </h1>

            <p class="mt-6 max-w-2xl text-lg leading-8 text-[#0a1628]/70">
              Acompanhe entradas, despesas e metas em uma experiência visual feita para uso recorrente.
              O Dinance transforma registros do dia a dia em visão prática para agir melhor.
            </p>

            <div class="mt-8 flex flex-col gap-4 sm:flex-row">
              <RouterLink
                to="/register"
                class="inline-flex items-center justify-center rounded-full bg-[#4caf50] px-8 py-4 text-base font-semibold text-white shadow-xl shadow-[#4caf50]/20 transition-all hover:-translate-y-0.5 hover:bg-[#449e48]"
              >
                Começar grátis
                <span class="ml-3 text-lg">→</span>
              </RouterLink>
              <RouterLink
                to="/login"
                class="inline-flex items-center justify-center rounded-full border-2 border-[#0a1628]/10 bg-white px-8 py-4 text-base font-semibold text-[#0a1628] transition-all hover:border-[#4caf50]/40 hover:text-[#4caf50]"
              >
                Já tenho conta
              </RouterLink>
            </div>
          </div>

          <div class="relative">
            <div class="absolute inset-0 flex items-center justify-center">
              <div class="h-80 w-80 rounded-full bg-[#4caf50]/12 blur-3xl"></div>
            </div>

            <div class="relative flex justify-center">
              <DinoMascot :size="350" />
            </div>
          </div>
        </div>

        <div class="mt-10 grid gap-4 sm:grid-cols-3">
          <article class="rounded-3xl border border-[#0a1628]/8 bg-white p-5 shadow-sm">
            <p class="text-3xl font-bold text-[#4caf50]">10k+</p>
            <p class="mt-2 text-sm leading-6 text-[#0a1628]/65">usuários acompanhando movimentações com mais clareza</p>
          </article>
          <article class="rounded-3xl border border-[#0a1628]/8 bg-white p-5 shadow-sm">
            <p class="text-3xl font-bold text-[#4caf50]">R$2M+</p>
            <p class="mt-2 text-sm leading-6 text-[#0a1628]/65">em fluxos monitorados mensalmente dentro da plataforma</p>
          </article>
          <article class="rounded-3xl border border-[#0a1628]/8 bg-white p-5 shadow-sm">
            <p class="text-3xl font-bold text-[#ffa726]">4.9</p>
            <p class="mt-2 text-sm leading-6 text-[#0a1628]/65">de satisfação entre pessoas que usam o app de forma recorrente</p>
          </article>
        </div>
      </section>

      <section class="bg-gradient-to-b from-[#f7fbf7] to-[#fffdf8] py-16">
        <div class="mx-auto max-w-7xl px-6 lg:px-8">
          <div class="grid gap-6 md:grid-cols-3">
            <article class="rounded-[2rem] border border-[#0a1628]/8 bg-white p-8 shadow-sm">
              <div class="flex h-14 w-14 items-center justify-center rounded-2xl bg-[#4caf50]/10 text-[#4caf50]">
                <svg class="h-7 w-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h10M4 18h7" />
                </svg>
              </div>
              <h3 class="mt-6 text-2xl font-semibold">Controle de gastos</h3>
              <p class="mt-3 text-base leading-7 text-[#0a1628]/65">
                Registre cada saída com contexto e acompanhe padrões para decidir com mais segurança.
              </p>
            </article>

            <article class="rounded-[2rem] border border-[#0a1628]/8 bg-white p-8 shadow-sm">
              <div class="flex h-14 w-14 items-center justify-center rounded-2xl bg-[#ffa726]/12 text-[#ffa726]">
                <svg class="h-7 w-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M4 19h16M7 15l3-3 3 2 4-6" />
                </svg>
              </div>
              <h3 class="mt-6 text-2xl font-semibold">Dashboard inteligente</h3>
              <p class="mt-3 text-base leading-7 text-[#0a1628]/65">
                Veja tendências, resultados e comparativos sem depender de planilhas dispersas.
              </p>
            </article>

            <article class="rounded-[2rem] border border-[#0a1628]/8 bg-white p-8 shadow-sm">
              <div class="flex h-14 w-14 items-center justify-center rounded-2xl bg-[#0a1628]/8 text-[#0a1628]">
                <svg class="h-7 w-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 3l7 4v5c0 4.6-2.9 7.8-7 9-4.1-1.2-7-4.4-7-9V7l7-4Z" />
                  <path stroke-linecap="round" stroke-linejoin="round" d="m9.5 12 1.7 1.7L14.8 10" />
                </svg>
              </div>
              <h3 class="mt-6 text-2xl font-semibold">Segurança da conta</h3>
              <p class="mt-3 text-base leading-7 text-[#0a1628]/65">
                Autenticação por usuário e separação de dados para manter o histórico confiável.
              </p>
            </article>
          </div>
        </div>
      </section>

      <section id="recursos" class="mx-auto max-w-7xl px-6 py-20 lg:px-8">
        <div class="flex flex-col gap-5 lg:max-w-3xl">
          <span class="text-sm font-semibold uppercase tracking-[0.24em] text-[#4caf50]">Recursos</span>
          <h2 class="text-4xl font-bold tracking-tight text-[#0a1628] lg:text-5xl">
            Um fluxo direto para registrar, analisar e agir.
          </h2>
          <p class="text-lg leading-8 text-[#0a1628]/65">
            O produto continua simples para lançar movimentações, mas entrega leitura visual suficiente para tomada de decisão.
          </p>
        </div>

        <div class="mt-12 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
          <div class="grid gap-6 md:grid-cols-2">
            <article v-for="feature in features" :key="feature.title" class="rounded-[2rem] border border-[#0a1628]/8 bg-white p-8 shadow-sm">
              <div :class="feature.badgeClass" class="flex h-12 w-12 items-center justify-center rounded-2xl">
                <svg class="h-6 w-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
                  <path :d="feature.icon[0]" stroke-linecap="round" stroke-linejoin="round" />
                  <path v-if="feature.icon[1]" :d="feature.icon[1]" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
              </div>
              <h3 class="mt-5 text-xl font-semibold text-[#0a1628]">{{ feature.title }}</h3>
              <p class="mt-3 leading-7 text-[#0a1628]/65">{{ feature.description }}</p>
            </article>
          </div>

          <aside class="rounded-[2rem] bg-[#0a1628] p-8 text-white shadow-2xl shadow-[#0a1628]/15">
            <div class="flex items-center justify-between gap-4">
              <div>
                <p class="text-sm font-semibold uppercase tracking-[0.24em] text-[#8ed98f]">Visão consolidada</p>
                <h3 class="mt-3 text-3xl font-bold">Rotina financeira mais previsível</h3>
              </div>
              <DinoMascot :size="84" class-name="shrink-0" />
            </div>
            <ul class="mt-8 space-y-4 text-sm leading-7 text-white/80">
              <li class="flex items-start gap-3">
                <span class="mt-1 h-2.5 w-2.5 rounded-full bg-[#4caf50]"></span>
                Indicadores mensais para receitas, despesas e saldo.
              </li>
              <li class="flex items-start gap-3">
                <span class="mt-1 h-2.5 w-2.5 rounded-full bg-[#ffa726]"></span>
                Classificação por categoria e operação para leitura mais rápida.
              </li>
              <li class="flex items-start gap-3">
                <span class="mt-1 h-2.5 w-2.5 rounded-full bg-white"></span>
                Fluxos de autenticação e perfil já integrados ao backend atual.
              </li>
            </ul>
            <RouterLink
              to="/register"
              class="mt-10 inline-flex items-center rounded-full bg-white px-6 py-3 text-sm font-semibold text-[#4caf50] transition-transform hover:-translate-y-0.5"
            >
              Experimentar agora
            </RouterLink>
          </aside>
        </div>
      </section>

      <section id="como-funciona" class="bg-gradient-to-b from-[#f7fbf7] to-[#fffdf8] py-20">
        <div class="mx-auto max-w-5xl px-6 lg:px-8">
          <div class="text-center">
            <span class="text-sm font-semibold uppercase tracking-[0.24em] text-[#4caf50]">Como funciona</span>
            <h2 class="mt-4 text-4xl font-bold tracking-tight lg:text-5xl">Comece em três passos simples</h2>
          </div>

          <div class="mt-14 space-y-6">
            <article
              v-for="step in steps"
              :key="step.number"
              class="flex flex-col gap-5 rounded-[2rem] border border-[#0a1628]/8 bg-white p-8 shadow-sm md:flex-row md:items-start"
            >
              <div :class="step.colorClass" class="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl text-2xl font-bold text-white shadow-lg">
                {{ step.number }}
              </div>
              <div>
                <h3 class="text-2xl font-semibold text-[#0a1628]">{{ step.title }}</h3>
                <p class="mt-3 text-base leading-8 text-[#0a1628]/65">{{ step.description }}</p>
              </div>
            </article>
          </div>
        </div>
      </section>

      <section id="precos" class="mx-auto max-w-7xl px-6 py-20 lg:px-8">
        <div class="text-center">
          <span class="text-sm font-semibold uppercase tracking-[0.24em] text-[#4caf50]">Planos</span>
          <h2 class="mt-4 text-4xl font-bold tracking-tight text-[#0a1628] lg:text-5xl">Uma entrada simples, espaço para crescer</h2>
          <p class="mx-auto mt-5 max-w-2xl text-lg leading-8 text-[#0a1628]/65">
            O produto já nasce pronto para controle pessoal e evolui com recursos premium conforme a experiência amadurece.
          </p>
        </div>

        <div class="mt-14 grid gap-6 lg:grid-cols-2">
          <article class="rounded-[2rem] border-2 border-[#0a1628]/10 bg-white p-10 shadow-sm">
            <h3 class="text-2xl font-semibold text-[#0a1628]">Essencial</h3>
            <div class="mt-5">
              <span class="text-5xl font-bold text-[#0a1628]">R$0</span>
              <span class="text-lg text-[#0a1628]/60">/mês</span>
            </div>
            <ul class="mt-8 space-y-4 text-[#0a1628]/70">
              <li v-for="item in freePlan" :key="item" class="flex items-start gap-3">
                <span class="mt-1 flex h-6 w-6 items-center justify-center rounded-full bg-[#4caf50]/10 text-[#4caf50]">✓</span>
                <span>{{ item }}</span>
              </li>
            </ul>
            <RouterLink
              to="/register"
              class="mt-10 inline-flex w-full items-center justify-center rounded-full bg-[#f2f5f7] px-6 py-3.5 text-sm font-semibold text-[#0a1628] transition-colors hover:bg-[#e8edf0]"
            >
              Começar grátis
            </RouterLink>
          </article>

          <article class="relative overflow-hidden rounded-[2rem] bg-gradient-to-br from-[#4caf50] to-[#449e48] p-10 text-white shadow-2xl shadow-[#4caf50]/20">
            <span class="absolute right-6 top-6 rounded-full bg-[#ffa726] px-4 py-1 text-sm font-semibold text-white">Popular</span>
            <h3 class="text-2xl font-semibold">Premium</h3>
            <div class="mt-5">
              <span class="text-5xl font-bold">R$19</span>
              <span class="text-lg text-white/80">/mês</span>
            </div>
            <ul class="mt-8 space-y-4 text-white/90">
              <li v-for="item in premiumPlan" :key="item" class="flex items-start gap-3">
                <span class="mt-1 flex h-6 w-6 items-center justify-center rounded-full bg-white/15 text-white">✓</span>
                <span>{{ item }}</span>
              </li>
            </ul>
            <RouterLink
              to="/register"
              class="mt-10 inline-flex w-full items-center justify-center rounded-full bg-white px-6 py-3.5 text-sm font-semibold text-[#4caf50] transition-transform hover:-translate-y-0.5"
            >
              Começar teste grátis
            </RouterLink>
          </article>
        </div>
      </section>

      <section class="bg-[#0a1628] py-20">
        <div class="mx-auto flex max-w-5xl flex-col items-center px-6 text-center lg:px-8">
          <div class="rounded-[2rem] bg-white/6 p-4">
            <DinoMascot :size="88" />
          </div>
          <h2 class="mt-8 text-4xl font-bold tracking-tight text-white lg:text-5xl">Pronto para assumir o controle das suas finanças?</h2>
          <p class="mt-5 max-w-2xl text-lg leading-8 text-white/75">
            Cadastre-se, registre suas primeiras movimentações e acompanhe a evolução no dashboard.
          </p>
          <div class="mt-8 flex flex-col gap-4 sm:flex-row">
            <RouterLink
              to="/register"
              class="inline-flex items-center justify-center rounded-full bg-[#4caf50] px-8 py-4 text-base font-semibold text-white shadow-xl shadow-[#4caf50]/20 transition-transform hover:-translate-y-0.5"
            >
              Criar conta grátis
            </RouterLink>
            <RouterLink
              to="/login"
              class="inline-flex items-center justify-center rounded-full border border-white/20 px-8 py-4 text-base font-semibold text-white transition-colors hover:bg-white/8"
            >
              Entrar agora
            </RouterLink>
          </div>
        </div>
      </section>
    </main>

    <footer class="bg-[#07111f] py-12">
      <div class="mx-auto max-w-7xl px-6 lg:px-8">
        <div class="grid gap-10 border-b border-white/10 pb-10 md:grid-cols-4">
          <div class="md:col-span-1">
            <div class="flex items-center gap-3">
              <div class="flex h-11 w-11 items-center justify-center rounded-2xl bg-white/8">
                <DinoMascot :size="34" />
              </div>
              <span class="text-lg font-semibold text-white">Dinance</span>
            </div>
            <p class="mt-4 text-sm leading-7 text-white/60">
              Controle financeiro pessoal com foco em clareza, recorrência e segurança de uso.
            </p>
          </div>

          <div>
            <h3 class="text-sm font-semibold uppercase tracking-[0.24em] text-white/90">Produto</h3>
            <div class="mt-4 flex flex-col gap-3 text-sm text-white/60">
              <a href="#recursos" class="transition-colors hover:text-white">Recursos</a>
              <a href="#precos" class="transition-colors hover:text-white">Planos</a>
              <RouterLink to="/login" class="transition-colors hover:text-white">Entrar</RouterLink>
            </div>
          </div>

          <div>
            <h3 class="text-sm font-semibold uppercase tracking-[0.24em] text-white/90">Conta</h3>
            <div class="mt-4 flex flex-col gap-3 text-sm text-white/60">
              <RouterLink to="/register" class="transition-colors hover:text-white">Criar conta</RouterLink>
              <a href="#" class="transition-colors hover:text-white" @click.prevent>Termos</a>
              <a href="#" class="transition-colors hover:text-white" @click.prevent>Privacidade</a>
            </div>
          </div>

          <div>
            <h3 class="text-sm font-semibold uppercase tracking-[0.24em] text-white/90">Contato</h3>
            <p class="mt-4 text-sm leading-7 text-white/60">
              Dinance acompanha sua rotina financeira com uma experiência objetiva e pronta para evoluir.
            </p>
          </div>
        </div>

        <p class="pt-8 text-center text-sm text-white/45">© {{ currentYear }} Dinance. Todos os direitos reservados.</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import DinoMascot from '@/components/branding/DinoMascot.vue'

const currentYear = computed(() => new Date().getFullYear())

const features = [
  {
    title: 'Lançamentos organizados',
    description: 'Crie transações com descrição, valor e categoria sem misturar regra de negócio com a interface.',
    badgeClass: 'bg-[#4caf50]/10 text-[#4caf50]',
    icon: ['M4 7h16M4 12h16M4 17h10'],
  },
  {
    title: 'Comparativos mensais',
    description: 'A dashboard resume receitas versus despesas para facilitar leitura rápida do período.',
    badgeClass: 'bg-[#ffa726]/12 text-[#ffa726]',
    icon: ['M5 18h14', 'M7 14l3-3 3 2 4-6'],
  },
  {
    title: 'Operações rápidas',
    description: 'Categorias e tipos ajudam a registrar movimentações sem fricção no fluxo do dia a dia.',
    badgeClass: 'bg-[#0a1628]/8 text-[#0a1628]',
    icon: ['M12 6v12M6 12h12'],
  },
  {
    title: 'Conta protegida',
    description: 'Sessão com JWT e isolamento por usuário mantêm o histórico individual mais confiável.',
    badgeClass: 'bg-[#4caf50]/10 text-[#4caf50]',
    icon: ['M12 3l7 4v5c0 4.6-2.9 7.8-7 9-4.1-1.2-7-4.4-7-9V7l7-4Z', 'm9.5 12 1.7 1.7L14.8 10'],
  },
]

const steps = [
  {
    number: '1',
    title: 'Crie sua conta',
    description: 'Abra seu acesso gratuitamente e prepare sua base financeira em poucos minutos.',
    colorClass: 'bg-[#4caf50]',
  },
  {
    number: '2',
    title: 'Registre entradas e despesas',
    description: 'Adicione movimentações com os campos essenciais para manter tudo categorizado.',
    colorClass: 'bg-[#ffa726]',
  },
  {
    number: '3',
    title: 'Acompanhe os indicadores',
    description: 'Use a dashboard para enxergar saldo, tendência mensal e prioridades com mais clareza.',
    colorClass: 'bg-[#4caf50]',
  },
]

const freePlan = [
  'Até 100 transações por mês',
  'Categorias essenciais',
  'Resumo mensal no dashboard',
  'Suporte por email',
]

const premiumPlan = [
  'Transações ilimitadas',
  'Categorias e operações avançadas',
  'Relatórios personalizados',
  'Metas e alertas inteligentes',
  'Experiência ampliada para rotinas recorrentes',
]
</script>
