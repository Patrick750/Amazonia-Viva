<script setup>
import { ref, computed } from 'vue'
import { navegacion } from '@/config/navigation';
import axios from 'axios';
// Si usas Vue Router, asegúrate de tenerlo instalado. 
// Aquí definimos el nombre de usuario de forma reactiva para que luego lo puedas 
// conectar con tu localStorage (como hicimos en el login).
const menuAbierto = ref(false)

const rol = ref(localStorage.getItem('rol')).value
const token = ref(localStorage.getItem('token')).value
const nombre_usuario = computed(() => {
  if(rol === 'turista') return localStorage.getItem('nombre')
  if(rol === 'agencia') return localStorage.getItem('nombre_agencia')
  if(rol === 'proveedor') return localStorage.getItem('nombre_empresa')
  return 'invitado'
})
const menu = computed(() => navegacion[rol])

</script>

<template>
  <nav class="bg-white border-b border-gray-100 px-6 py-4 flex items-center justify-between w-full sticky top-0 z-50 shadow-sm">
    
    <router-link to="/" class="flex items-center gap-3 hover:opacity-80 transition-opacity">
      <div class="bg-teal-500 text-white w-10 h-10 flex items-center justify-center rounded-xl font-bold text-xl shadow-sm">
        T
      </div>
      <span class="text-xl font-bold text-gray-950 tracking-tight">Amazonia viva</span>
    </router-link>

    <div v-if="token" class="hidden md:flex items-center gap-8">
      <router-link 
          v-for="items in menu"
          :to="items.path" :key="items.label" class="text-gray-900 font-medium hover:text-teal-600 transition-colors cursor-pointer">
          {{ items.label }}
      </router-link>
    </div>
    <div v-else class="hidden md:flex items-center gap-8">
      <router-link 
          to="" class="text-gray-900 font-medium hover:text-teal-600 transition-colors cursor-pointer">
          Inico
      </router-link>
      <router-link 
          to="" class="text-gray-900 font-medium hover:text-teal-600 transition-colors cursor-pointer">
          Catalogo
      </router-link>
    </div>


    <div v-if="token" class="flex items-center gap-6">
      
      <button v-if="rol != 'proveedor'" class="text-gray-700 hover:text-teal-600 transition-colors focus:outline-none">
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="9" cy="21" r="1"></circle>
          <circle cx="20" cy="21" r="1"></circle>
          <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
        </svg>
      </button>

      <button v-if="rol != 'proveedor'" class="text-gray-700 hover:text-teal-600 transition-colors focus:outline-none">
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
        </svg>
      </button>

      <template v-if="token"">
        <div class="relative ml-2">
          
          <button 
            @click="menuAbierto = !menuAbierto" 
            class="flex items-center gap-2 cursor-pointer group focus:outline-none"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-gray-700 group-hover:text-teal-600 transition-colors">
              <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
            <span class="font-medium text-gray-900 group-hover:text-teal-600 transition-colors">
              {{ nombre_usuario }}
            </span>
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4 text-gray-500 transition-transform duration-200" :class="{ 'rotate-180': menuAbierto }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
          </button>

          <div v-if="menuAbierto" @click="menuAbierto = false" class="fixed inset-0 z-40"></div>

          <transition 
            enter-active-class="transition ease-out duration-100" 
            enter-from-class="transform opacity-0 scale-95" 
            enter-to-class="transform opacity-100 scale-100" 
            leave-active-class="transition ease-in duration-75" 
            leave-from-class="transform opacity-100 scale-100" 
            leave-to-class="transform opacity-0 scale-95"
          >
            <div v-if="menuAbierto" class="absolute right-0 mt-4 w-52 bg-white rounded-xl shadow-lg border border-gray-100 z-50 py-2 overflow-hidden">
              
              <div class="px-4 py-2 text-xs font-semibold text-gray-400 uppercase tracking-wider border-b border-gray-50 mb-1">
                Mi Cuenta
              </div>

              <router-link to="/perfil" @click="menuAbierto = false" class="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 hover:text-teal-600 transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
                Perfil
              </router-link>
              
              <router-link to="/configuraciones" @click="menuAbierto = false" class="flex items-center gap-3 px-4 py-2.5 text-sm text-gray-700 hover:bg-gray-50 hover:text-teal-600 transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
                Configuraciones
              </router-link>
              
              <div class="border-t border-gray-100 my-1"></div>
              
              <button @click="cerrarSesion" class="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 transition-colors text-left font-medium">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
                Cerrar sesión
              </button>
            </div>
          </transition>
        </div>
      </template>
    </div>

    <div v-else class="flex items-center gap-6">
      <router-link 
        to="/auth/login" 
        class="text-gray-800 hover:text-[#00a8b5] transition-colors font-medium"
      >
        Iniciar Sesión
      </router-link>
      <router-link 
        to="/auth/signup" 
        class="bg-[#0091a3] hover:bg-[#007f8f] text-white px-5 py-2.5 rounded-lg font-medium transition-colors shadow-sm inline-block"
      >
        Registrarse
      </router-link>
    </div>

  </nav>

</template>
