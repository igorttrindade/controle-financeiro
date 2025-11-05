import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import HomeView  from '../views/HomeView.vue'
import RegisterView from '@/views/RegisterView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,  
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
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
      meta:{ 
        requiresAuth: false,
        fullLayout: false
      }
    },
  ],
})

export default router
