import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue'),  
      meta:{ 
        requiresAuth: false,
        fullLayout: false
      }
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta:{ 
        requiresAuth: false,
        fullLayout: false
      }
    },
  ],
})

export default router
