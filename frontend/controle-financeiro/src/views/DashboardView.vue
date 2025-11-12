<template>
  <div>
    <Navbar />
    <main class="dashboard-content">
      <h2>Bem-vindo ao Dashboard 👋</h2>
      <p>Aqui será o conteúdo principal da aplicação.</p>
    </main>
  </div>
</template>

<script setup>
import Navbar from "@/components/Navbar.vue"
</script>

<style scoped>
.dashboard-content {
  padding: 2rem;
  color: var(--color-text);
  background: var(--color-background);
  min-height: calc(100vh - 60px);
  transition: background 0.3s ease;
}
</style>
