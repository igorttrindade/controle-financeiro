import './assets/tailwind.css'
import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import { useTheme } from './composables/useTheme'

useTheme().initTheme()

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
