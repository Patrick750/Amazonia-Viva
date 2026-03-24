import { createRouter, createWebHistory } from 'vue-router'
import signup from '@/views/signup.vue'
import login from '@/views/login.vue'
import paneles from '@/components/paneles.vue'
import dashboard from '@/components/dashboard.vue'
import paquetes from '@/views/paquetes.vue'
import productos from '@/views/productos.vue'

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
    {
      path:'/panel/gestion-paquetes',
      name:'gestionpaqutes',
      component: paquetes,
    },
    {
      path:'/panel/productos',
      name:'productos',
      component: productos,
    },
  ],
})


router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const rol = localStorage.getItem('rol')

  const urlAuth = ['/auth/login','/auth/signup'] 
  const urlMenus = ['/panel/dashboard','/panel/gestion-paquetes','/panel/productos']

  if(urlMenus.includes(to.path)){
    if(!token || !rol){
      return next('/panel')
    }
  } 

  if (to.path === '/panel/gestion-paquetes') {
    if (rol !== 'agencia') {
      return next('/panel')
    }
  }

  if (to.path === '/panel/productos') {
    if (rol !== 'proveedor') {
      return next('/panel')
    }
  }

  if (urlAuth.includes(to.path)) {
    
    if (token && rol) {
      return next(`/panel`)
    }
  }

  return next()
})

export default router
