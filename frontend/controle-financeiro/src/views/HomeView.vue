<template>
  <div class="home">
    <header class="header">
      <div class="logo">
        <!--<img src="/logo.png" alt="Logo" class="logo-img" />-->
        <h1>FinanceFlow</h1>
      </div>
      <RouterLink to="/login" class="login-btn">Entrar</RouterLink>
    </header>

    <section class="hero" data-aos="fade-up">
      <h2>Controle suas finanças de forma inteligente</h2>
      <p>Monitore suas receitas, despesas e metas com facilidade e segurança.</p>
      <RouterLink to="/login" class="cta-btn">Começar agora</RouterLink>
    </section>

    <section class="features">
      <div class="feature" data-aos="fade-right">
        <h3>📊 Dashboard intuitivo</h3>
        <p>Visualize rapidamente seus gastos e ganhos em tempo real.</p>
      </div>
      <div class="feature" data-aos="fade-up">
        <h3>🔒 Segurança de dados</h3>
        <p>Seus dados são criptografados e armazenados de forma segura.</p>
      </div>
      <div class="feature" data-aos="fade-left">
        <h3>💡 Planejamento financeiro</h3>
        <p>Defina metas e acompanhe seu progresso de maneira simples.</p>
      </div>
    </section>

    <!-- Rodapé -->
    <footer class="footer">
      <p>&copy; 2025 FinanceFlow — Seu controle financeiro simplificado</p>
    </footer>
  </div>
</template>

<script setup>
import AOS from "aos"
import "aos/dist/aos.css"
import { onMounted } from "vue"

onMounted(() => {
  AOS.init({
    duration: 1000,
    once: true,
  })
})
</script>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
}

:root {
  --bg: #ffffff;
  --text: #222;
  --accent: #007bff;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #121212;
    --text: #ededed;
    --accent: #4dabf7;
  }
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  position: sticky;
  top: 0;
  z-index: 10;
  background: var(--bg);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.logo-img {
  width: 40px;
  height: 40px;
}
.login-btn {
  text-decoration: none;
  background: var(--accent);
  color: white;
  padding: 0.6rem 1rem;
  border-radius: 8px;
  transition: 0.2s;
}
.login-btn:hover {
  opacity: 0.8;
}

.hero {
  padding: 5rem 2rem 3rem;
  text-align: center;
  max-width: 900px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  flex-direction: column;
}

.hero h2 {
  font-size: 2.8rem;
  margin-bottom: 1rem;
}
.hero p {
  font-size: 1.2rem;
  margin-bottom: 2rem;
  max-width: 600px;
}
.cta-btn {
  text-decoration: none;
  background: var(--accent);
  color: white;
  padding: 0.8rem 1.8rem;
  border-radius: 10px;
  font-weight: 600;
  transition: 0.3s;
}
.cta-btn:hover {
  opacity: 0.85;
}

.features {
  display: flex;
  justify-content: center;
  align-items: stretch;
  flex-wrap: wrap;
  gap: 2rem;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 4rem 1rem;
  box-sizing: border-box;
}

.feature {
  flex: 1 1 300px;
  max-width: 350px;
  min-height: 180px;
  background: rgba(255,255,255,0.05);
  border-radius: 12px;
  padding: 1.8rem;
  text-align: center;
  backdrop-filter: blur(5px);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.feature:hover {
  transform: translateY(-8px);
  box-shadow: 0 4px 15px rgba(0,0,0,0.3);
}
.feature h3 {
  margin-bottom: 0.8rem;
  font-size: 1.2rem;
}

.footer {
  text-align: center;
  padding: 1.8rem;
  margin-top: auto;
  font-size: 0.9rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  opacity: 0.8;
}

@media (max-width: 768px) {
  .features {
    flex-direction: column;
    align-items: center;
  }
  .feature {
    width: 90%;
  }
}

</style>