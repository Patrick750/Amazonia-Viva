<script setup>
import { ref } from 'vue'
import axios from 'axios';
// Si usas Vue Router, asegúrate de tenerlo instalado. 
// Aquí definimos el nombre de usuario de forma reactiva para que luego lo puedas 
// conectar con tu localStorage (como hicimos en el login).
const rol = localStorage.getItem('rol')
const nombreUsuario = localStorage.getItem('nombre')
</script>

<template>
  <nav class="bg-white border-b border-gray-100 px-6 py-4 flex items-center justify-between w-full sticky top-0 z-50 shadow-sm">
    
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
        Tours
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
          {{ nombreUsuario }}
        </span>
      </div>

    </div>
    
  </nav>
</template>