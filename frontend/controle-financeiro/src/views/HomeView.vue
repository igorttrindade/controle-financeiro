<template>
  <div class="home" :class="{ dark: isDark }">
    <header class="header" data-aos="fade-down">
      <div class="logo">
        <h1>💸 FinanceFlow</h1>
      </div>
      <nav class="nav">
        <RouterLink to="/" class="nav-link">Início</RouterLink>
        <RouterLink to="/sobre" class="nav-link">Sobre</RouterLink>
        <RouterLink to="/contato" class="nav-link">Contato</RouterLink>
        <button @click="toggleTheme" class="theme-toggle">
          <span v-if="isDark">🌙</span>
          <span v-else>☀️</span>
        </button>
        <RouterLink to="/login" class="login-btn">Entrar</RouterLink>
      </nav>
    </header>

    <section class="hero" data-aos="zoom-in">
      <div class="hero-content">
        <h2>Controle suas finanças de forma inteligente</h2>
        <p>Organize seus gastos, acompanhe metas e alcance estabilidade financeira com poucos cliques.</p>
        <RouterLink to="/login" class="cta-btn">Começar agora</RouterLink>
      </div>
      <div class="hero-image">
        <!--<img src="/finance-dashboard.png" alt="Dashboard financeiro" />-->
      </div>
    </section>

    <section class="features">
      <div class="feature" data-aos="fade-right">
        <h3>📊 Dashboard intuitivo</h3>
        <p>Visualize seus ganhos, despesas e progresso financeiro em tempo real.</p>
      </div>
      <div class="feature" data-aos="fade-up">
        <h3>🔒 Segurança total</h3>
        <p>Suas informações são protegidas com autenticação e criptografia de ponta.</p>
      </div>
      <div class="feature" data-aos="fade-left">
        <h3>💡 Planejamento inteligente</h3>
        <p>Crie metas, acompanhe resultados e melhore seus hábitos financeiros.</p>
      </div>
    </section>

    <section class="cta-section" data-aos="zoom-in-up">
      <h2>Pronto para transformar suas finanças?</h2>
      <RouterLink to="/login" class="cta-btn-large">Começar grátis</RouterLink>
    </section>

    <footer class="footer">
      <p>&copy; 2025 FinanceFlow — Todos os direitos reservados</p>
    </footer>
  </div>
</template>

<script setup>
import AOS from "aos"
import "aos/dist/aos.css"
import { onMounted, ref } from "vue"

const theme = ref(localStorage.getItem("theme") || "light")

const toggleTheme = () => {
  theme.value = theme.value === "dark" ? "light" : "dark"
  localStorage.setItem("theme", theme.value)
  document.documentElement.setAttribute("data-theme", theme.value)
}

onMounted(() => {
  AOS.init({ duration: 1000, once: true })
  document.documentElement.setAttribute("data-theme", theme.value)
})
</script>


<style scoped>
:root {
  --bg-light: #ffffff;
  --text-light: #222;
  --accent-light: #007bff;
  --bg-dark: #0f1115;
  --text-dark: #f0f0f0;
  --accent-dark: #4dabf7;
}

.home {
  min-height: 100vh;
  background: var(--color-background);
  color: var(--color-text);
  transition: background 0.3s ease, color 0.3s ease;
}

.home.dark {
  background: var(--bg-dark);
  color: var(--text-dark);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.2rem 3rem;
  position: sticky;
  top: 0;
  z-index: 10;
  background: var(--color-background-soft);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  transition: background 0.3s ease;
  border-bottom: 1px solid var(--color-border); 
}

.home.dark .header {
  background: var(--bg-dark);
}

.logo h1 {
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--accent-light);
}

.home.dark .logo h1 {
  color: var(--accent-dark);
}

.nav {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.nav-link {
  text-decoration: none;
  color: inherit;
  font-weight: 500;
  transition: 0.3s;
}

.home.dark .nav-link:hover {
  background-color: var(--accent-light);
  padding: 5px;
  border-radius: 15%;
}

.login-btn {
  text-decoration: none;
  background: var(--color-background-soft);
  color: var(--color-text);
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  font-weight: 600;
  transition: 0.3s;
}

.home.dark .login-btn:hover {
  opacity: 0.85;
  color: var(--accent-dark);
}

.theme-toggle {
  background: none;
  border: none;
  font-size: 1.3rem;
  cursor: pointer;
  color: inherit;
  transition: transform 0.2s ease;
}

.theme-toggle:hover {
  transform: scale(1.2);
}

.hero {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  gap: 2rem;
}

.hero-content {
  flex: 1 1 400px;
  max-width: 500px;
}

.hero-content h2 {
  font-size: 2.6rem;
  margin-bottom: 1rem;
}

.hero-content p {
  font-size: 1.1rem;
  margin-bottom: 2rem;
}

.cta-btn {
  text-decoration: none;
  background: var(--color-background-soft);
  color: var(--color-text);
  padding: 0.9rem 1.6rem;
  border-radius: 10px;
  font-weight: 600;
  transition: 0.3s;
}

.cta-btn:hover {
  opacity: 0.85;
}

.hero-image {
  flex: 1 1 350px;
  display: flex;
  justify-content: center;
}

.hero-image img {
  width: 100%;
  max-width: 480px;
  border-radius: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.features {
  display: flex;
  justify-content: center;
  align-items: stretch;
  flex-wrap: wrap;
  gap: 2rem;
  padding: 5rem 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.feature {
  flex: 1 1 300px;
  max-width: 350px;
  background: var(--color-background);
  border-radius: 15px;
  padding: 2rem;
  text-align: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  backdrop-filter: blur(5px);
}

.feature:hover {
  transform: translateY(-8px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.cta-section {
  text-align: center;
  padding: 5rem 2rem;
  background: var(--color-background-soft);
  color: var(--color-text);
}

.home.dark .cta-section {
  background: var(--accent-dark);
}

.cta-btn-large {
  display: inline-block;
  margin-top: 1.5rem;
  background: var(--color-text);
  color: var(--color-background-soft);
  padding: 1rem 2rem;
  border-radius: 12px;
  font-weight: 700;
  text-decoration: none;
  transition: 0.3s;
}

.home.dark .cta-btn-large {
  color: var(--accent-dark);
}

.cta-btn-large:hover {
  opacity: 0.9;
}

.footer {
  text-align: center;
  padding: 2rem;
  font-size: 0.9rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  opacity: 0.8;
}
</style>