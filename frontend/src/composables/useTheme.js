import { computed, ref } from 'vue'
import { API_URL } from '@/services/http/api'

const STORAGE_KEY = 'theme'
const allowedThemes = new Set(['light', 'dark'])

function resolveInitialTheme() {
  const savedTheme = localStorage.getItem(STORAGE_KEY)
  if (allowedThemes.has(savedTheme)) {
    return savedTheme
  }

  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

const theme = ref(resolveInitialTheme())

function applyTheme(value) {
  document.documentElement.setAttribute('data-theme', value)
}

async function persistThemeOnBackend(nextTheme) {
  const token = localStorage.getItem('token')
  if (!token) return

  try {
    await fetch(`${API_URL}/api/users/me/profile`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ theme: nextTheme }),
    })
  } catch {
    // Falha de rede não deve bloquear troca local de tema.
  }
}

function setTheme(value, { persist = true } = {}) {
  const nextTheme = allowedThemes.has(value) ? value : 'light'
  theme.value = nextTheme
  localStorage.setItem(STORAGE_KEY, nextTheme)
  applyTheme(nextTheme)

  if (persist) {
    persistThemeOnBackend(nextTheme)
  }
}

function toggleTheme() {
  setTheme(theme.value === 'dark' ? 'light' : 'dark')
}

async function initTheme() {
  applyTheme(theme.value)

  const token = localStorage.getItem('token')
  if (!token) return

  try {
    const response = await fetch(`${API_URL}/api/users/me/profile`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!response.ok) return

    const payload = await response.json()
    const backendTheme = payload?.theme
    if (allowedThemes.has(backendTheme) && backendTheme !== theme.value) {
      setTheme(backendTheme, { persist: false })
    }
  } catch {
    // Fallback local já aplicado.
  }
}

const isDark = computed(() => theme.value === 'dark')

export function useTheme() {
  return {
    theme,
    isDark,
    setTheme,
    toggleTheme,
    initTheme,
  }
}
