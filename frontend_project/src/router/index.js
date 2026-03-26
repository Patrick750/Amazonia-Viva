import { createRouter, createWebHistory } from 'vue-router'
import signup from '@/views/signup.vue'
import login from '@/views/login.vue'
import paneles from '@/components/paneles.vue'
import dashboard from '@/components/dashboard.vue'
import paquetes from '@/views/paquetes.vue'
import productos from '@/views/productos.vue'
import catalogo from '@/views/catalogo.vue'
import DetallePaquete from '@/views/detalle-paquete.vue'
import DetalleProducto from '@/views/detalle-producto.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path:'/',
      redirect: '/catalogo',
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
    {
      path: '/catalogo',
      name: 'catalogo',
      component: catalogo,
    },
    {
      path: '/catalogo/tour/:id',
      name: 'detalle_tour',
      component: DetallePaquete,
    },
    {
      path: '/catalogo/producto/:id',
      name: 'detalle_producto',
      component: DetalleProducto,
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
