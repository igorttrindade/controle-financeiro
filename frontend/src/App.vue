<script setup>
import { RouterView } from 'vue-router'
import NotificationToast from '@/components/feedback/NotificationToast.vue'
</script>

<template>
  <div class="min-h-screen bg-base-200 text-base-content">
    <RouterView />
    <NotificationToast />
  </div>
</template>
