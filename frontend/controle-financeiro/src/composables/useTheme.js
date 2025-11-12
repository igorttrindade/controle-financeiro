import { ref, watchEffect } from "vue"

const isDark = ref(localStorage.getItem("theme") === "dark")

function toggleTheme() {
  isDark.value = !isDark.value
  const newTheme = isDark.value ? "dark" : "light"
  localStorage.setItem("theme", newTheme)
  document.documentElement.setAttribute("data-theme", newTheme)
}

watchEffect(() => {
  document.documentElement.setAttribute("data-theme", isDark.value ? "dark" : "light")
})

export function useTheme() {
  return { isDark, toggleTheme }
}