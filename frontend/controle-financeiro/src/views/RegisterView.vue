<template>
  <div class="register-container" :class="{ dark: !isLightMode }">
    <div class="theme-toggle">
      <button @click="toggleTheme">
        {{ isLightMode ? '🌙 Modo Escuro' : '☀️ Modo Claro' }}
      </button>
    </div>

    <div class="card" data-aos="zoom-in">
      <img src="@/assets/finance_logo.png" alt="Logo" class="logo" />
      <h1>Criar Conta</h1>

      <form @submit.prevent = "handleRegister" class="form-container">
        <label>Nome</label>
        <input type="text" v-model="nameUser" placeholder="Seu nome" />

        <label>Email</label>
        <input type="email" v-model="emailUser" placeholder="Seu email" />

        <label>Data de Nascimento</label>
        <input type="date" v-model="dtNascimentoUser"/>

        <label>Celular</label>
        <input type="text" v-model="celUser" placeholder="Seu número de celular" maxlength="11" />

        <label>Senha</label>
        <input type="password" v-model="passwordUser" placeholder="Crie uma senha" />

        <button type="submit">Registrar</button>

        <p class="login-link">
          Já possui conta?
          <router-link to="/login">Faça login</router-link>
        </p>
      </form>
    </div>
  </div>
  <NotificationToast />
</template>

<script setup>
import { ref, onMounted } from "vue"
import AOS from "aos"
import "aos/dist/aos.css"
import { registerUser } from "@/services/authServices"
import NotificationToast from "@/components/NotificationToast.vue"
import { useNotifications } from "@/composables/useNotifications"

const { addNotification } = useNotifications()

const nameUser = ref('')
const emailUser = ref('')
const dtNascimentoUser = ref('')
const celUser = ref('')
const passwordUser = ref('')

async function handleRegister() {
  if (!nameUser.value || !emailUser.value || !dtNascimentoUser.value || !celUser.value || !passwordUser.value) {
    addNotification("⚠️ Por favor, preencha todos os campos antes de continuar.", "warning")
    return
  }

  if (passwordUser.value.length < 6) {
    addNotification("🔒 A senha deve conter pelo menos 6 caracteres.", "warning")
    return
  }

  if (!/^\d{11}$/.test(celUser.value)) {
    addNotification("📱 O número de celular deve conter 11 dígitos (DDD + número).", "warning")
    return
  }

  try{
    const result = await registerUser({
      name_user: nameUser.value,
      email_user: emailUser.value,
      dt_nascimento_user: dtNascimentoUser.value,
      tel_user: celUser.value,
      password: passwordUser.value,
    })
    addNotification("🎉 Conta criada com sucesso! Seja bem-vindo(a) à plataforma.", "success")
    console.log(result)
  } catch (err) {
    if (err.response && err.response.status === 409) {
      addNotification("⚠️ Este e-mail já está cadastrado. Tente outro ou faça login.", "warning")
    } else {
      addNotification("❌ Ocorreu um erro ao criar sua conta. Tente novamente em alguns instantes.", "error")
    }
    console.error(err)
  }
}

const isLightMode = ref(localStorage.getItem("theme") === "light")

function toggleTheme() {
  isLightMode.value = !isLightMode.value
  const newTheme = isLightMode.value ? "light" : "dark"
  localStorage.setItem("theme", newTheme)
  document.documentElement.setAttribute("data-theme", newTheme)
}

onMounted(() => {
  AOS.init({ duration: 1000, once: true })
  const savedTheme = localStorage.getItem("theme") || "light"
  document.documentElement.setAttribute("data-theme", savedTheme)
  isLightMode.value = savedTheme === "light"
})


</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: var(--color-background);
  transition: background 0.4s, color 0.4s;
  color: var(--color-text);
}

.register-container.light-mode {
  background: var(--bg-light);
  color: var(--text-light);
}

.card {
  background: var(--color-background-soft);
  padding: 2.5rem 3rem;
  border-radius: 16px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 400px;
  text-align: center;
  transition: background 0.3s ease, color 0.3s ease;
}

.register-container:not(.light-mode) .card {
  background: var(--bg-light);
  color: var(--text-light);
}

.register-container.light-mode .card {
  background: #ffffff;
  color: #000;
}

.logo {
  width: 70px;
  height: 70px;
  margin-bottom: 1rem;
  object-fit: contain;
}

h1 {
  margin-bottom: 1.5rem;
  font-size: 1.8rem;
  font-weight: 600;
  color: inherit;
}

.form-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  text-align: left;
}

label {
  font-size: 0.9rem;
  font-weight: 600;
  color: inherit;
}

input {
  padding: 0.7rem;
  border: 1px solid var(--color-border, #333);
  border-radius: 8px;
  outline: none;
  background: transparent;
  color: inherit;
  transition: border 0.2s ease;
}

input:focus {
  border-color: var(--accent-dark, #888);
}

button {
  margin-top: 1rem;
  background: var(--color-text);
  color: var(--color-background-soft);
  border: none;
  padding: 0.8rem;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 600;
  transition: 0.3s;
}

button:hover {
  opacity: 0.9;
  transform: translateY(-2px);
}

.login-link {
  text-align: center;
  margin-top: 1rem;
  font-size: 0.9rem;
  color: inherit;
}

.login-link a {
  color: var(--accent-light);
  font-weight: 600;
  text-decoration: none;
}

.login-link a:hover {
  text-decoration: underline;
}

.theme-toggle {
  position: absolute;
  top: 20px;
  right: 20px;
}

.theme-toggle button {
  background: none;
  border: 1px solid var(--color-border, #444);
  color: var(--color-text, #fff);
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.theme-toggle button:hover {
  background: rgba(255, 255, 255, 0.1);
}

.register-container.dark .theme-toggle button {
  border-color: #444;
  color: #fff;
}

.register-container.light-mode .theme-toggle button {
  border-color: #ccc;
  color: #000;
}

.register-container.light-mode .theme-toggle button:hover {
  background-color: rgba(0, 0, 0, 0.05);
}
</style>
