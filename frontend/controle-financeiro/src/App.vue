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
      
      <main class="main-content">
        <RouterView />
        <NotificationToast />
      </main>
    </div>

    <div v-else>
      <main>
        <RouterView />
      </main>
    </div>
    
  </div>
</template>

<style>

.main-content {
  padding-top: 60px;
}

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