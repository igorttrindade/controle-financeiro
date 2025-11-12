<template>
  <div class="toast-container">
    <div
      v-for="n in notifications"
      :key="n.id"
      class="toast"
      :class="n.type"
      @click="removeNotification(n.id)"
    >
      {{ n.message }}
    </div>
  </div>
</template>

<script setup>
import { useNotifications } from "@/composables/useNotifications"
const { notifications, removeNotification } = useNotifications()
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  z-index: 9999;
}

.toast {
  background-color: #333;
  color: white;
  padding: 12px 16px;
  border-radius: 8px;
  font-weight: 500;
  min-width: 200px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.3);
  cursor: pointer;
  transition: transform 0.2s ease, opacity 0.3s ease;
}

.toast:hover {
  transform: translateY(-2px);
  opacity: 0.9;
}

.toast.success {
  background-color: #28a745;
}

.toast.error {
  background-color: #dc3545;
}

.toast.info {
  background-color: #007bff;
}

.toast.warning {
  background-color: #ffc107;
  color: #000;
}
</style>
