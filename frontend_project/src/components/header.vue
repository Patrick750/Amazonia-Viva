<script setup>
import { ref } from 'vue'
import axios from 'axios';
// Si usas Vue Router, asegúrate de tenerlo instalado. 
// Aquí definimos el nombre de usuario de forma reactiva para que luego lo puedas 
// conectar con tu localStorage (como hicimos en el login).
const rol = ref(localStorage.getItem('rol')).value
const nombreTurista = ref(localStorage.getItem('nombre')).value
const nombreProveedor = ref(localStorage.getItem('nombre_empresa')).value
const nombreAgencia = ref(localStorage.getItem('nombre_agencia')).value
console.log(nombreAgencia)
</script>

<template>
  <nav v-if="rol == 'turista'" class="bg-white border-b border-gray-100 px-6 py-4 flex items-center justify-between w-full sticky top-0 z-50 shadow-sm">
    
    <router-link to="/" class="flex items-center gap-3 hover:opacity-80 transition-opacity">
      <div class="bg-teal-500 text-white w-10 h-10 flex items-center justify-center rounded-xl font-bold text-xl shadow-sm">
        T
      </div>
      <span class="text-xl font-bold text-gray-950 tracking-tight">Amazonia viva</span>
    </router-link>

    <div class="hidden md:flex items-center gap-8">
      <router-link to="#" class="text-gray-900 font-medium hover:text-teal-600 transition-colors cursor-pointer">
        Inicio
      </router-link>
      <router-link to="#" class="text-gray-900 font-medium hover:text-teal-600 transition-colors cursor-pointer">
        Catalogo
      </router-link>
      <router-link to="#" class="text-gray-900 font-medium hover:text-teal-600 transition-colors cursor-pointer">
        Mis Reservas
      </router-link>
      <router-link to="#" class="text-gray-900 font-medium hover:text-teal-600 transition-colors cursor-pointer">
        Mis Experiencias
      </router-link>
    </div>

    <div class="flex items-center gap-6">
      
      <button class="text-gray-700 hover:text-teal-600 transition-colors focus:outline-none">
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="9" cy="21" r="1"></circle>
          <circle cx="20" cy="21" r="1"></circle>
          <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
        </svg>
      </button>

      <button class="text-gray-700 hover:text-teal-600 transition-colors focus:outline-none">
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
        </svg>
      </button>

      <div class="flex items-center gap-2 cursor-pointer group ml-2">
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-gray-700 group-hover:text-teal-600 transition-colors">
          <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path>
          <circle cx="12" cy="7" r="4"></circle>
        </svg>
        <span class="font-medium text-gray-900 group-hover:text-teal-600 transition-colors">
          {{ nombreTurista }}
        </span>
      </div>
    </div>
  </nav>

  <nav v-else-if="rol == 'agencia'" class="bg-white border-b border-gray-100 px-6 py-4 flex items-center justify-between w-full sticky top-0 z-50 shadow-sm">
    
    <router-link to="/" class="flex items-center gap-3 hover:opacity-80 transition-opacity">
      <div class="bg-teal-500 text-white w-10 h-10 flex items-center justify-center rounded-xl font-bold text-xl shadow-sm">
        T
      </div>
      <span class="text-xl font-bold text-gray-950 tracking-tight">Amazonia viva</span>
    </router-link>

    <div class="hidden md:flex items-center gap-8">
      <router-link to="#" class="text-gray-900 font-medium hover:text-teal-600 transition-colors cursor-pointer">
        Inicio
      </router-link>
      <router-link to="#" class="text-gray-900 font-medium hover:text-teal-600 transition-colors cursor-pointer">
        Catalogo
      </router-link>
      <router-link to="#" class="text-gray-900 font-medium hover:text-teal-600 transition-colors cursor-pointer">
        Mis compras
      </router-link>
      <router-link to="#" class="text-gray-900 font-medium hover:text-teal-600 transition-colors cursor-pointer">
        Dashboard
      </router-link>
    </div>

    <div class="flex items-center gap-6">
      
      <button class="text-gray-700 hover:text-teal-600 transition-colors focus:outline-none">
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="9" cy="21" r="1"></circle>
          <circle cx="20" cy="21" r="1"></circle>
          <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path>
        </svg>
      </button>

      <button class="text-gray-700 hover:text-teal-600 transition-colors focus:outline-none">
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
        </svg>
      </button>

      <div class="flex items-center gap-2 cursor-pointer group ml-2">
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-gray-700 group-hover:text-teal-600 transition-colors">
          <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path>
          <circle cx="12" cy="7" r="4"></circle>
        </svg>
        <span class="font-medium text-gray-900 group-hover:text-teal-600 transition-colors">
          {{ nombreAgencia }}
        </span>
      </div>
    </div>
  </nav>
  <nav v-else-if="rol == 'proveedor'" class="bg-white border-b border-gray-100 px-6 py-4 flex items-center justify-between w-full sticky top-0 z-50 shadow-sm">
    
    <router-link to="/" class="flex items-center gap-3 hover:opacity-80 transition-opacity">
      <div class="bg-teal-500 text-white w-10 h-10 flex items-center justify-center rounded-xl font-bold text-xl shadow-sm">
        T
      </div>
      <span class="text-xl font-bold text-gray-950 tracking-tight">Amazonia viva</span>
    </router-link>

    <div class="hidden md:flex items-center gap-8">
      <router-link to="#" class="text-gray-900 font-medium hover:text-teal-600 transition-colors cursor-pointer">
        Inicio
      </router-link>
      <router-link to="#" class="text-gray-900 font-medium hover:text-teal-600 transition-colors cursor-pointer">
        Catalogo
      </router-link>
      <router-link to="#" class="text-gray-900 font-medium hover:text-teal-600 transition-colors cursor-pointer">
        Dashboard
      </router-link>
    </div>

    <div class="flex items-center gap-6">
      <div class="flex items-center gap-2 cursor-pointer group ml-2">
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-gray-700 group-hover:text-teal-600 transition-colors">
          <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path>
          <circle cx="12" cy="7" r="4"></circle>
        </svg>
        <span class="font-medium text-gray-900 group-hover:text-teal-600 transition-colors">
          {{ nombreProveedor }}
        </span>
      </div>
    </div>
  </nav>

    <nav v-else class="bg-white border-b border-gray-100 px-6 py-4 flex items-center justify-between w-full sticky top-0 z-50 shadow-sm">
    
    <router-link to="#" class="flex items-center gap-3 hover:opacity-80 transition-opacity">
      <div class="bg-teal-500 text-white w-10 h-10 flex items-center justify-center rounded-xl font-bold text-xl shadow-sm">
        T
      </div>
      <span class="text-xl font-bold text-gray-950 tracking-tight">Amazonia viva</span>
    </router-link>

    <div class="hidden md:flex items-center gap-8">
      <router-link to="#" class="text-gray-900 font-medium hover:text-teal-600 transition-colors cursor-pointer">
        Inicio
      </router-link>
      <router-link to="#" class="text-gray-900 font-medium hover:text-teal-600 transition-colors cursor-pointer">
        Catalogo
      </router-link>
    </div>

    <div class="flex items-center gap-6">
      <div class="flex items-center gap-6">
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
    </div>
  </nav>

</template>
