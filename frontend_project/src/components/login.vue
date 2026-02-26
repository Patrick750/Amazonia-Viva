<script setup>
import { ref } from 'vue';
import axios from 'axios'
import { useRouter } from 'vue-router';

const router = useRouter()

const cargando = ref(false)

const formulario = ref({
  email: '',
  password: ''
});

const Redirigir = (rol) => {
  router.push(`/panel/${rol}`)
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
    localStorage.setItem('nombre_usuario', response.data.usuario.username)
    localStorage.setItem('rol', response.data.usuario.group)

    const rol = response.data.usuario.group
    Redirigir(rol)
    
  }catch(error){
    errorCredenciales.value = 'Correo o contraseña incorrectas'
    console.error('Hubo un error' + error)
  }finally{
    cargando.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-[#e8f0fe] flex items-center justify-center p-4 font-sans">
    
    <div class="bg-white p-8 sm:p-10 rounded-xl shadow-[0_4px_15px_rgba(0,0,0,0.05)] w-full max-w-[450px]">
      
      <div class="text-center mb-8">
        <div class="bg-[#0d47a1] text-white w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path>
            <polyline points="10 17 15 12 10 7"></polyline>
            <line x1="15" y1="12" x2="3" y2="12"></line>
          </svg>
        </div>
        <h2 class="text-2xl font-semibold text-gray-900 mb-2">Iniciar Sesión</h2>
        <p class="text-sm text-gray-500">Ingrese sus credenciales para acceder al sistema</p>
        <p v-if="errorCredenciales" class="text-[#f85050] text-center m-auto text-base font-semibold">
            {{ errorCredenciales }}
        </p>
      </div>
      <form @submit.prevent="procesarLogin">
        
        <div class="mb-5 flex flex-col">
          <label for="email" class="text-sm font-semibold text-gray-800 mb-2">Correo Electrónico</label>
          <input 
            type="email" 
            id="email" 
            v-model="formulario.email" 
            placeholder="usuario@ejemplo.com" 
            required 
            class="w-full p-3 border border-transparent rounded-md bg-[#f0fcf9] text-gray-800 text-sm focus:outline-none focus:border-[#008c9e] transition-colors placeholder-gray-400"
          />
        </div>

        <div class="mb-6 flex flex-col">
          <label for="password" class="text-sm font-semibold text-gray-800 mb-2">Contraseña</label>
          <input 
            type="password" 
            id="password" 
            v-model="formulario.password" 
            placeholder="••••••••" 
            required 
            class="w-full p-3 border border-transparent rounded-md bg-[#f0fcf9] text-gray-800 text-sm focus:outline-none focus:border-[#008c9e] transition-colors placeholder-gray-400"
          />
        </div>
<button
        type="submit"
        :disabled="cargando"
        class="w-full py-3 bg-[#008c9e] hover:bg-[#007a8a] text-white rounded-md text-base font-medium transition-all mt-2 flex items-center justify-center disabled:opacity-70 disabled:cursor-not-allowed"
      >
        <template v-if="!cargando">
          Iniciar Sesión
        </template>

        <template v-else>
          <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Procesando...
        </template>

      </button>
      </form>

      <div class="text-center mt-6 text-sm text-gray-600">
        <p>¿No tienes una cuenta? 
          <router-link to="/auth/signup" class="text-[#004c56] font-medium hover:underline">Regístrate aquí</router-link>
        </p>
      </div>

    </div>
  </div>
</template>
<style>
</style>