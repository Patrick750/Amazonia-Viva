import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import signup from '@/components/signup.vue'
import login from '@/components/login.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path:'/',
      redirect: '/auth/login',
    },
    {
      path:'/auth/signup',
      name:'auth_signup',
      component: signup,
    },
    {
      path:'/auth/login',
      name:'auth_login',
      component: login,
    }
  ],
})

export default router
