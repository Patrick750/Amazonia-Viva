import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import signup from '@/components/signup.vue'
import login from '@/components/login.vue'
import paneles from '@/components/paneles.vue'
import dashboard from '@/components/dashboard.vue'

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
    },
    {
      path:'/panel',
      name:'panel',
      component: paneles,
    },
    {
      path:'/panel/dashboard',
      name:'dashboard',
      component: dashboard,
    },
  ],
})


router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const rol = localStorage.getItem('rol')

  if(to.path === '/panel'){
    if(!token){
      next('/panel')
    }
  }

  if (to.path === '/auth/login' || to.path === '/auth/signup') {
    
    if (token && rol) {
      next(`/panel`)
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
