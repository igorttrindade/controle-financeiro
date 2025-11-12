<template>
  <div class="login-page" :class="{ dark: isDark }">
    <div class="theme-toggle">
      <button @click="toggleTheme">
        {{ isDark ? '☀️ Modo Claro' : '🌙 Modo Escuro' }}
      </button>
    </div>
    <div class="login-card" data-aos="zoom-in">
      <img :src="logo" alt="Logo FinanceFlow" class="logo-img" />

      <h1>Entrar</h1>

      <form @submit.prevent="handleLoginUser" class="login-form">
        <label for="email">Email</label>
        <input id="email" type="email" v-model="emailUser" placeholder="Digite seu email" />

        <label for="password">Senha</label>
        <input id="password" type="password" v-model="passwordUser" placeholder="Digite sua senha" />

        <button type="submit" class="login-btn" :disabled="isLoading">
          {{ isLoading ? 'Entrando...' : 'Entrar' }}
        </button>
      </form>

      <p class="register-text">
        Não possui conta?
        <RouterLink to="/register" class="register-link">Crie uma</RouterLink>
      </p>
    </div>
  </div>
  <NotificationToast/>
</template>

<script setup>
import AOS from "aos"
import "aos/dist/aos.css"
import { ref, onMounted } from "vue"
import logo from "@/assets/finance_logo.png"
import { loginUser } from "@/services/authServices"
import NotificationToast from "@/components/NotificationToast.vue"
import { useNotifications } from "@/composables/useNotifications"

const { addNotification } = useNotifications()

const emailUser = ref('')
const passwordUser = ref('')
const isLoading = ref(false)

async function handleLoginUser() {
  if (!emailUser.value || !passwordUser.value) {
    addNotification("⚠️ Preencha seu e-mail e senha para continuar.", "warning")
    return
  }
  isLoading.value = true
  try{
    const resolve = await  loginUser({
      email_user: emailUser.value,
      password: passwordUser.value,
    })
    addNotification("🎉 Login realizado com sucesso! Seja bem-vindo(a) à plataforma.", "success")
    console.log(resolve)
  }catch(err){
    addNotification("❌ Ocorreu um erro ao entrar. Tente novamente em alguns instantes.", "error")
    console.error(err)
  }finally {
    isLoading.value = false
  }
}

const theme = ref(localStorage.getItem("theme") || "light")
const isDark = ref(theme.value === "dark")

function toggleTheme() {
  isDark.value = !isDark.value
  const newTheme = isDark.value ? "dark" : "light"
  localStorage.setItem("theme", newTheme)
  document.documentElement.setAttribute("data-theme", newTheme)
}

onMounted(() => {
  AOS.init({ duration: 1000, once: true })
  document.documentElement.setAttribute("data-theme", theme.value)
})
</script>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: var(--color-background);
  transition: background 0.3s ease, color 0.3s ease;
}

.login-page.dark {
  background: var(--bg-dark);
  color: var(--text-dark);
}

.login-card {
  background: var(--color-background-soft);
  padding: 2.5rem 3rem;
  border-radius: 16px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 400px;
  text-align: center;
  transition: 0.3s ease;
}

.login-page.dark .login-card {
  background: #1c1e24;
}

.logo-img {
  width: 70px;
  height: 70px;
  margin-bottom: 1rem;
  object-fit: contain;
}

h1 {
  margin-bottom: 1.5rem;
  font-size: 1.8rem;
  color: var(--color-text);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

label {
  text-align: left;
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--color-text);
}

input {
  padding: 0.7rem;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  outline: none;
  background: transparent;
  color: var(--color-text);
  transition: border 0.2s ease;
}

input:focus {
  border-color: var(--accent-dark);
}

.login-btn {
  background: var(--color-text);
  color: var(--color-background-soft);
  border: none;
  padding: 0.8rem;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  transition: 0.3s;
}

.login-btn:hover {
  opacity: 0.9;
  transform: translateY(-2px);
}

.register-text {
  margin-top: 1.5rem;
  font-size: 0.9rem;
  color: var(--color-text);
}

.register-link {
  text-decoration: none;
  color: var(--accent-light);
  font-weight: 600;
  margin-left: 4px;
}

.register-link:hover {
  text-decoration: underline;
}

.theme-toggle {
  position: absolute;
  top: 20px;
  right: 20px;
}

.theme-toggle button {
  background: none;
  border: 1px solid var(--color-border);
  color: var(--color-text);
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.theme-toggle button:hover {
  background: rgba(255, 255, 255, 0.1);
}

.login-page.dark .theme-toggle button {
  border-color: #444;
  color: #fff;
}

.login-page.dark .theme-toggle button:hover {
  background: rgba(255, 255, 255, 0.1);
}
</style>
