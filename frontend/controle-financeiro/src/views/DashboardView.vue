<template>
  <div class="dashboard">
    <Navbar />

    <main class="dashboard-content">
      <h1>📊 Dashboard Financeiro</h1>
      <p>Bem-vindo ao seu painel de controle!</p>

      <section class="stats-grid">
        <div class="card">
          <h3>Saldo Atual</h3>
          <p>R$ 12.540,00</p>
        </div>
        <div class="card">
          <h3>Receitas do mês</h3>
          <p>R$ 8.420,00</p>
        </div>
        <div class="card">
          <h3>Despesas do mês</h3>
          <p>R$ 5.210,00</p>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import Navbar from "@/components/Navbar.vue"
</script>

<style scoped>
.dashboard {
  background: var(--color-background);
  min-height: 100vh;
  color: var(--color-text);
}

.dashboard-content {
  padding: 100px 2rem 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.stats-grid {
  margin-top: 2rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.card {
  background: var(--color-background-soft);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 20px rgba(0,0,0,0.15);
}

h1 {
  font-size: 1.8rem;
  margin-bottom: 1rem;
}
</style>