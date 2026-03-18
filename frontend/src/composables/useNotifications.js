import { ref } from "vue"

const notifications = ref([])

export function useNotifications() {
  function addNotification(message, type = "info", duration = 3000) {
    const id = Date.now()
    notifications.value.push({ id, message, type })

    setTimeout(() => {
      removeNotification(id)
    }, duration)
  }

  function removeNotification(id) {
    notifications.value = notifications.value.filter(n => n.id !== id)
  }

  return { notifications, addNotification, removeNotification }
}
