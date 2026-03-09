<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import Header from './header.vue';

const router = useRouter()
const cargando = ref(false)

const formulario = ref({
  email: '',
  password: ''
});

const Redirigir = () => {
  router.push(`/panel`)
} 

const errorCredenciales = ref('') 

const procesarLogin = async () => {
  cargando.value = true
  try{
    const response = await axios.post('http://127.0.0.1:8000/api/login/',{
      email: formulario.value.email,
      password: formulario.value.password
    })

    localStorage.setItem('token', response.data.access)
    localStorage.setItem('nombre', response.data.usuario.nombre)
    localStorage.setItem('apellido', response.data.usuario.apellido)
    localStorage.setItem('nombre_usuario', response.data.usuario.username)
    localStorage.setItem('nombre_empresa', response.data.usuario.nombre_empresa)
    localStorage.setItem('nombre_agencia', response.data.usuario.nombre_agencia)
    localStorage.setItem('rol', response.data.usuario.group)

    Redirigir()
    
  }catch(error){
    errorCredenciales.value = 'Correo o contraseña incorrectas'
    console.error('Hubo un error' + error)
  }finally{
    cargando.value = false
  }
}
</script>

<template>
  <Header></Header>
  <div 
    class="min-h-screen flex items-center justify-center p-4 font-sans relative bg-cover bg-center bg-no-repeat"
    style="background-image: url('https://images.unsplash.com/photo-1499678329028-101435549a4e?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=80');"
  >
    <div class="absolute inset-0 bg-black/30"></div>
    
    <div class="relative bg-white/70 backdrop-blur-lg border border-white/40 p-8 sm:p-10 rounded-3xl shadow-[0_8px_32px_rgba(0,0,0,0.15)] w-full max-w-[420px] transition-all">
      
      <div class="text-center mb-8">
        <div class="bg-gradient-to-br from-teal-400 to-emerald-600 text-white w-14 h-14 rounded-2xl flex items-center justify-center mx-auto mb-5 shadow-lg transform -rotate-3 hover:rotate-0 transition-transform duration-300">
          <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="2" y1="12" x2="22" y2="12"></line>
            <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
          </svg>
        </div>
        <h2 class="text-3xl font-bold text-gray-800 tracking-tight mb-2">Tu próximo viaje</h2>
        <p class="text-sm text-gray-600 font-medium">Inicia sesión para planificar tu aventura</p>
        
        <div v-if="errorCredenciales" class="mt-4 p-3 bg-red-100/80 border border-red-200 text-red-600 rounded-xl text-sm font-semibold flex items-center justify-center space-x-2">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
          <span>{{ errorCredenciales }}</span>
        </div>
      </div>

      <form @submit.prevent="procesarLogin">
        
        <div class="mb-5 flex flex-col relative">
          <label for="email" class="text-xs font-bold text-gray-700 uppercase tracking-wider mb-2 ml-1">Correo Electrónico</label>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>
            </div>
            <input 
              type="email" 
              id="email" 
              v-model="formulario.email" 
              placeholder="viajero@ejemplo.com" 
              required 
              class="w-full pl-11 pr-4 py-3.5 border border-white/50 rounded-xl bg-white/50 text-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:bg-white/80 transition-all placeholder-gray-500 shadow-sm"
            />
          </div>
        </div>

        <div class="mb-6 flex flex-col relative">
          <label for="password" class="text-xs font-bold text-gray-700 uppercase tracking-wider mb-2 ml-1">Contraseña</label>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <svg class="h-5 w-5 text-gray-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
            </div>
            <input 
              type="password" 
              id="password" 
              v-model="formulario.password" 
              placeholder="••••••••" 
              required 
              class="w-full pl-11 pr-4 py-3.5 border border-white/50 rounded-xl bg-white/50 text-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:bg-white/80 transition-all placeholder-gray-500 shadow-sm"
            />
          </div>
        </div>

        <button
          type="submit"
          :disabled="cargando"
          class="w-full py-3.5 bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-600 hover:to-emerald-600 text-white rounded-xl text-base font-bold tracking-wide transition-all duration-300 mt-2 flex items-center justify-center shadow-lg shadow-teal-500/30 hover:shadow-teal-500/50 hover:-translate-y-0.5 disabled:opacity-70 disabled:cursor-not-allowed disabled:transform-none"
        >
          <template v-if="!cargando">
            Comenzar Viaje
          </template>

          <template v-else>
            <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Preparando maletas...
          </template>
        </button>
      </form>

      <div class="text-center mt-8 text-sm text-gray-700">
        <p>¿Aún no eres parte del club? <br/>
          <router-link to="/auth/signup" class="text-teal-700 font-bold hover:text-teal-500 transition-colors hover:underline underline-offset-4">Regístrate y viaja con nosotros</router-link>
        </p>
      </div>

    </div>
  </div>
</template>

<style>
/* Si deseas, el estilo está manejado enteramente con Tailwind, no necesitas CSS extra aquí */
</style>