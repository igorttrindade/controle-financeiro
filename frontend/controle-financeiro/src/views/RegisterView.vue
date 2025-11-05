<template>
  <div class="register-container" :class="{ 'light-mode': isLightMode }">
    <div class="theme-toggle">
      <button @click="toggleTheme">
        {{ isLightMode ? '🌙 Modo Escuro' : '☀️ Modo Claro' }}
      </button>
    </div>

    <div class="card">
      <img src="@/assets/finance_logo.png" alt="Logo" class="logo" />
      <h1>Criar Conta</h1>

      <form class="form-container">
        <label>Nome</label>
        <input type="text" placeholder="Seu nome" />

        <label>Email</label>
        <input type="email" placeholder="Seu email" />

        <label>Data de Nascimento</label>
        <input type="date" />

        <label>Celular</label>
        <input type="text" placeholder="Seu número de celular" maxlength="11" />

        <label>Senha</label>
        <input type="password" placeholder="Crie uma senha" />

        <button type="button">Registrar</button>

        <p class="login-link">
          Já possui conta?
          <router-link to="/login">Faça login</router-link>
        </p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const isLightMode = ref(localStorage.getItem('theme') === 'light')

function toggleTheme() {
  isLightMode.value = !isLightMode.value
  localStorage.setItem('theme', isLightMode.value ? 'light' : 'dark')
}

</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #0e0e0e, #1a1a1a);
  color: #fff;
  transition: background 0.4s, color 0.4s;
}

.register-container.light-mode {
  background: linear-gradient(135deg, #f0f0f0, #d9d9d9);
  color: #000;
}

.card {
  background-color: var(--color-background-soft, #1f1f1f);
  padding: 2.5rem;
  border-radius: 16px;
  box-shadow: 0 0 20px rgba(255, 255, 255, 0.05);
  width: 100%;
  max-width: 400px;
  text-align: center;
  transition: background-color 0.4s, box-shadow 0.4s;
}

.register-container.light-mode .card {
  background-color: #fff;
  box-shadow: 0 0 15px rgba(0, 0, 0, 0.15);
}

.logo {
  width: 90px;
  margin-bottom: 1.5rem;
}

h1 {
  margin-bottom: 1.5rem;
  font-weight: 600;
}

.form-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  text-align: left;
}

label {
  font-size: 0.9rem;
  color: #ccc;
  transition: color 0.4s;
}

.register-container.light-mode label {
  color: #333;
}

input {
  padding: 0.8rem;
  border-radius: 8px;
  border: 1px solid #333;
  background-color: #2a2a2a;
  color: #fff;
  outline: none;
  transition: all 0.4s;
}

input:focus {
  border-color: #555;
}

.register-container.light-mode input {
  background-color: #f5f5f5;
  border-color: #ccc;
  color: #000;
}

button {
  margin-top: 1rem;
  padding: 0.8rem;
  border: none;
  border-radius: 8px;
  background-color: #3a3a3a;
  color: #fff;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

button:hover {
  background-color: #505050;
}

.register-container.light-mode button {
  background-color: #ddd;
  color: #000;
}

.register-container.light-mode button:hover {
  background-color: #bbb;
}

.login-link {
  text-align: center;
  margin-top: 1rem;
  font-size: 0.9rem;
  color: #ccc;
}

.login-link a {
  color: #fff;
  font-weight: 500;
  text-decoration: none;
}

.login-link a:hover {
  text-decoration: underline;
}

.register-container.light-mode .login-link {
  color: #333;
}

.register-container.light-mode .login-link a {
  color: #000;
}

.theme-toggle {
  position: absolute;
  top: 20px;
  right: 20px;
}

.theme-toggle button {
  background: none;
  border: 1px solid #444;
  color: #fff;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s;
}

.theme-toggle button:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.register-container.light-mode .theme-toggle button {
  color: #000;
  border-color: #ccc;
}

.register-container.light-mode .theme-toggle button:hover {
  background-color: rgba(0, 0, 0, 0.05);
}
</style>
