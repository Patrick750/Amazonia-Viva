import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import signup from '@/components/signup.vue'
import login from '@/components/login.vue'
import turista from '@/components/panelturista.vue'
import agencia from '@/components/panelagencia.vue'
import proveedor from '@/components/panelproveedor.vue'

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
      path:'/panel/turista',
      name:'pane_turista',
      component: turista,
    },
    {
      path:'/panel/agencia',
      name:'pane_agencia',
      component: agencia,
    },
    {
      path:'/panel/proveedor',
      name:'pane_proveedor',
      component: proveedor,
    }
  ],
})

export default router
