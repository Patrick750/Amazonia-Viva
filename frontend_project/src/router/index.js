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
import MisFavoritos from '@/views/favoritos.vue'
import Carrito from '@/views/carrito.vue'
import CheckoutViajeros from '@/views/checkout-viajeros.vue'
import home from '@/views/home.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path:'/',
      name: 'home',
      component: home,
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
      redirect: '/catalogo/tours'
    },
    {
      path: '/catalogo/tours',
      name: 'catalogo_tours',
      component: catalogo,
    },
    {
      path: '/catalogo/productos',
      name: 'catalogo_productos',
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
    {
      path: '/mis-favoritos',
      name: 'mis_favoritos',
      component: MisFavoritos,
      meta: { requiresAuth: true }
    },
    {
      path: '/carrito',
      name: 'carrito',
      component: Carrito,
      meta: { requiresAuth: true, roles: ['turista', 'agencia'] },
    },
    {
      path: '/checkout/viajeros',
      name: 'checkout_viajeros',
      component: CheckoutViajeros,
      meta: { requiresAuth: true, roles: ['turista', 'agencia'] },
    },
    {
      path: '/perfil',
      name: 'perfil_empresa',
      component: () => import('@/views/perfil-empresa.vue'),
      meta: { requiresAuth: true, roles: ['agencia', 'proveedor'] },
    },
    {
      path: '/mi-perfil',
      name: 'mi_perfil',
      component: () => import('@/views/perfil-turista.vue'),
      meta: { requiresAuth: true, roles: ['turista'] },
    },
  ],
})


router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const rol = localStorage.getItem('rol')

  const publicPaths = ['/', '/auth/login', '/auth/signup', '/catalogo']
  const isPublic = publicPaths.includes(to.path) || to.path.startsWith('/catalogo/')

  // Si no está autenticado y no es una ruta pública, al inicio
  if (!token || !rol) {
    if (!isPublic) {
      return next('/')
    }
    return next()
  }

  // Si está autenticado e intenta ir a login/signup, al inicio
  if (['/auth/login', '/auth/signup'].includes(to.path)) {
    return next('/')
  }

  // Restricciones de rutas con meta.requiresAuth
  if (to.meta?.requiresAuth) {
    if (!token || !rol) return next('/')
    if (to.meta.roles && !to.meta.roles.includes(rol)) return next('/')
  }

  // Restricciones de Panel para usuarios autenticados
  if (to.path === '/panel' || to.path === '/panel/dashboard') {
    if (rol === 'turista') {
      return next('/')
    }
  }

  if (to.path === '/panel/gestion-paquetes' && rol !== 'agencia') {
    return next('/')
  }

  if (to.path === '/panel/productos' && rol !== 'proveedor') {
    return next('/')
  }

  return next()
})

export default router
