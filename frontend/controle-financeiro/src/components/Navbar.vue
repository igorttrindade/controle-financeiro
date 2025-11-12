<template>
  <nav class="navbar">
    <div class="navbar-left">
      <img src="@/assets/finance_logo.png" alt="Logo" class="logo" />
      <h1 class="app-name">FinanceFlow</h1>

      <ul class="nav-links">
        <li><RouterLink to="/dashboard">Dashboard</RouterLink></li>
        <li><RouterLink to="/transactions">Transações</RouterLink></li>
        <li><RouterLink to="/categories">Categorias</RouterLink></li>
        <li><RouterLink to="/reports">Relatórios</RouterLink></li>
      </ul>
    </div>

    <div class="navbar-right">
      <button @click="toggleTheme" class="theme-btn">
        {{ isDark ? '☀️' : '🌙' }}
      </button>

      <div class="user-menu" @click="toggleDropdown">
        <img src="@/assets/finance_logo.png" alt="Perfil" class="avatar" />
        <transition name="fade">
          <ul v-if="showDropdown" class="dropdown-menu">
            <li><RouterLink to="/profile">👤 Perfil</RouterLink></li>
            <li><RouterLink to="/settings">⚙️ Configurações</RouterLink></li>
            <li @click="logout">🚪 Sair</li>
          </ul>
        </transition>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()
const isDark = ref(localStorage.getItem("theme") === "dark")
const showDropdown = ref(false)

function toggleTheme() {
  isDark.value = !isDark.value
  const newTheme = isDark.value ? "dark" : "light"
  localStorage.setItem("theme", newTheme)
  document.documentElement.setAttribute("data-theme", newTheme)
}

function toggleDropdown() {
  showDropdown.value = !showDropdown.value
}

function closeDropdown(e) {
  if (!e.target.closest(".user-menu")) {
    showDropdown.value = false
  }
}

function logout() {
  localStorage.removeItem("token")
  router.push("/login")
}

onMounted(() => {
  document.addEventListener("click", closeDropdown)
})

onBeforeUnmount(() => {
  document.removeEventListener("click", closeDropdown)
})
</script>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--color-background-soft);
  color: var(--color-text);
  padding: 1rem 2rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
  transition: background 0.3s ease;
  position: fixed;
  z-index: 1000;
  top: 0;
  left: 0;
  width: 100%;         
}

.navbar-left {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.logo {
  width: 40px;
  height: 40px;
}

.app-name {
  font-size: 1.2rem;
  font-weight: 600;
}

.nav-links {
  display: flex;
  gap: 1rem;
  list-style: none;
}

.nav-links a {
  color: var(--color-text);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
}

.nav-links a:hover {
  color: var(--accent-light);
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.theme-btn {
  background: none;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 0.4rem 0.8rem;
  cursor: pointer;
  color: var(--color-text);
  transition: all 0.3s;
}

.theme-btn:hover {
  background: rgba(255,255,255,0.1);
}

.user-menu {
  position: relative;
  cursor: pointer;
}

.avatar {
  width: 35px;
  height: 35px;
  border-radius: 50%;
  border: 2px solid var(--color-border);
  transition: transform 0.2s ease;
}

.avatar:hover {
  transform: scale(1.05);
}

.dropdown-menu {
  position: absolute;
  top: 50px;
  right: 0;
  background: var(--color-background-soft);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
  list-style: none;
  padding: 0.5rem 0;
  width: 180px;
  z-index: 100;
}

.dropdown-menu li {
  padding: 0.8rem 1rem;
  color: var(--color-text);
  font-weight: 500;
  transition: background 0.3s ease;
}

.dropdown-menu li:hover {
  background: var(--accent-light);
  color: white;
}

.dropdown-menu a {
  color: inherit;
  text-decoration: none;
  display: block;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
