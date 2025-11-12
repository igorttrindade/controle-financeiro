<script setup>
import { RouterView, useRoute, RouterLink } from 'vue-router'
import { computed } from 'vue'
import NotificationToast from "@/components/NotificationToast.vue"

const route = useRoute() 

const isFullLayout = computed(() => route.meta.fullLayout ?? true)
</script>

<template>
  <div id="main-layout">
    
    <div v-if="isFullLayout">
      <header>
        <nav>
          <RouterLink to="/dashboard">Dashboard</RouterLink>
          <RouterLink to="/transactions">Transações</RouterLink>
          <RouterLink to="/logout">Sair</RouterLink>
        </nav>
      </header>
      
      <main>
        <RouterView />
        <NotificationToast />
      </main>

      <footer>
        <p>&copy; 2025 App Controle Financeiro</p>
      </footer>
    </div>

    <div v-else>
      <main>
        <RouterView />
      </main>
    </div>
    
  </div>
</template>

<style>

body {
  background-color: #121212;
  color: #ededed; 
  margin: 0;
  font-family: sans-serif;
}
#main-layout {
  min-height: 100vh;
}
</style>