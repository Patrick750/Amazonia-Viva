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
import Pago from '@/views/pago.vue'
import home from '@/views/home.vue'
import MisReservas from '@/views/mis-reservas.vue'
import GestionReservasView from '@/views/gestion-reservas-view.vue'
import ExperienciasDashboard from '@/views/experiencias-dashboard.vue'
import FeedbackExperiencia from '@/views/feedback-experiencia.vue'
import MisExperiencias from '@/views/MisExperiencias.vue'
import MisProductosTurista from '@/views/mis-productos.vue'
import VentasProveedor from '@/components/perfil/VentasProveedor.vue'

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
      meta: { requiresAuth: true, roles: ['proveedor'] },
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
      path: '/pago',
      name: 'pago',
      component: Pago,
      meta: { requiresAuth: true, roles: ['turista', 'agencia'] },
    },
    {
      path: '/perfil',
      name: 'perfil_empresa',
      component: () => import('@/views/perfil-empresa.vue'),
      meta: { requiresAuth: true, roles: ['agencia', 'proveedor'] },
    },
    {
      path: '/perfil/:id',
      name: 'perfil_publico',
      component: () => import('@/views/perfil-publico.vue')
    },
    {
      path: '/mi-perfil',
      name: 'mi_perfil',
      component: () => import('@/views/perfil-turista.vue'),
      meta: { requiresAuth: true, roles: ['turista'] },
    },
    {
      path: '/panel/reservas',
      name: 'mis_reservas',
      component: MisReservas,
      meta: { requiresAuth: true, roles: ['turista'] },
    },
    {
      path: '/panel/gestion-reservas',
      name: 'gestion_reservas',
      component: GestionReservasView,
      meta: { requiresAuth: true, roles: ['agencia', 'proveedor'] },
    },
    {
      path: '/panel/experiencias',
      name: 'experiencias_dashboard',
      component: ExperienciasDashboard,
      meta: { requiresAuth: true, roles: ['agencia'] },
    },
    {
      path: '/feedback-experiencia/:id',
      name: 'feedback_experiencia',
      component: FeedbackExperiencia,
      meta: { requiresAuth: true, roles: ['turista'] },
    },
    {
      path: '/panel/mis-experiencias',
      name: 'mis_experiencias',
      component: MisExperiencias,
      meta: { requiresAuth: true, roles: ['turista'] },
    },
    {
      path: '/panel/compras',
      name: 'mis_compras_agencia',
      component: MisProductosTurista,
      meta: { requiresAuth: true },
    },
    {
      path: '/panel/mis-productos',
      name: 'mis_productos_turista',
      component: MisProductosTurista,
      meta: { requiresAuth: true },
    },
    {
      path: '/panel/gestion-ventas',
      name: 'gestion_ventas',
      component: VentasProveedor,
      meta: { requiresAuth: true, roles: ['proveedor'] },
    },
  ],
  scrollBehavior(to, from, savedPosition) {
    // Siempre desplazar al inicio de la página en cada navegación
    return { top: 0 }
  },
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
    
    // Verificación de roles insensible a mayúsculas
    if (to.meta.roles) {
      const allowedRoles = to.meta.roles.map(r => r.toLowerCase());
      if (!allowedRoles.includes(rol.toLowerCase())) {
        return next('/')
      }
    }
  }

  // Restricciones de Panel para usuarios autenticados
  const rolLower = rol.toLowerCase();
  
  if (to.path === '/panel' || to.path === '/panel/dashboard') {
    if (rolLower === 'turista') {
      return next('/')
    }
  }

  if (to.path === '/panel/gestion-paquetes' && rolLower !== 'agencia') {
    return next('/')
  }

  if (to.path === '/panel/productos' && rolLower !== 'proveedor') {
    return next('/')
  }

  if (to.path === '/panel/gestion-reservas' && !['agencia', 'proveedor'].includes(rolLower)) {
    return next('/')
  }

  return next()
})

export default router
