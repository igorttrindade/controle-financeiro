<template>
  <div class="toast toast-end toast-top z-[1200]">
    <div
      v-for="notification in notifications"
      :key="notification.id"
      class="alert cursor-pointer shadow-lg"
      :class="resolveAlertClass(notification.type)"
      @click="removeNotification(notification.id)"
    >
      <span>{{ notification.message }}</span>
    </div>
  </div>
</template>

<script setup>
import { useNotifications } from '@/composables/useNotifications'

const { notifications, removeNotification } = useNotifications()

function resolveAlertClass(type) {
  if (type === 'success') return 'alert-success'
  if (type === 'error') return 'alert-error'
  if (type === 'warning') return 'alert-warning'
  return 'alert-info'
}
</script>
