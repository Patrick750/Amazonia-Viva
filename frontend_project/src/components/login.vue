<script setup>
import { ref } from 'vue';
import axios from 'axios'

const formulario = ref({
  email: '',
  password: ''
});

const procesarLogin = async () => {
  try{
    const response = await axios.post('http://127.0.0.1:8000/api/login/',{
      username: formulario.value.email,
      password: formulario.value.password
    })

    console.log(response.data)
  }catch(error){
    console.error('Hubo un error' + error)
  }
};
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
          class="w-full py-3 bg-[#008c9e] hover:bg-[#007a8a] text-white rounded-md text-base font-medium transition-colors mt-2"
        >
          Iniciar Sesión
        </button>
      </form>

      <div class="text-center mt-6 text-sm text-gray-600">
        <p>¿No tienes una cuenta? 
          <router-link to="/auth/signup" class="text-[#1a73e8] font-medium hover:underline">Regístrate aquí</router-link>
        </p>
      </div>

    </div>
  </div>
</template>