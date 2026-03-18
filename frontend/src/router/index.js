import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/auth/LoginView.vue'
import HomeView  from '../views/marketing/HomeView.vue'
import RegisterView from '@/views/auth/RegisterView.vue'
import DashboardView from '@/views/dashboard/DashboardView.vue'
import TransactionsView from '@/views/transactions/TransactionsView.vue'
import CreateTransactionView from '@/views/transactions/CreateTransactionView.vue'
import EditTransactionView from '@/views/transactions/EditTransactionView.vue'
import ProfileView from '@/views/profile/ProfileView.vue'

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
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView,
      meta:{ 
        requiresAuth: true,
      }
    },
    {
      path: '/transactions',
      name: 'transactions',
      component: TransactionsView,
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/transactions/new',
      name: 'transaction-create',
      component: CreateTransactionView,
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/transactions/:id/edit',
      name: 'transaction-edit',
      component: EditTransactionView,
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
      meta: {
        requiresAuth: true,
      },
    },
  ],
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')

  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if ((to.name === 'login' || to.name === 'register') && token) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
