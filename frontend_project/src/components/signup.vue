<script setup>
    import { ref, computed } from 'vue'
    import axios from 'axios'

    // Estado para controlar qué pestaña está activa
    const tabActiva = ref('turista')

    // Textos dinámicos según el rol seleccionado
    const subtitulos = {
    turista: 'Complete el formulario para registrarse como Turista.', 
    agencia: 'Registre su Agencia. El sistema validará que el nombre no exista previamente.',
    proveedor: 'Complete la información de su empresa proveedora.'
    }

    const subtituloActual = computed(() => subtitulos[tabActiva.value])

    // Objeto para almacenar todos los datos del formulario
    const formulario = ref({
    nombres: '',
    apellidos: '',
    username:'',
    edad: '',
    identidad: '',
    email: '',
    password: '',
    confirmPassword: '',
    nombre_agencia: '',
    ubicacion: '',
    numero_telefonico: '',
    nombre_empresa: '',
    group:''
    })

    
    const enviarRegistroAgencia = async (rol) => {
        try{
            const respuesta = await axios.post(`http://127.0.0.1:8000/api/signup/${rol}/`, formulario.value);
            console.log('Formulari enviado')
            formulario.value = ''
        }catch (error){
            console.error("Hubo un error")
        }
    }
   
    const existeEmail = false
    const VerificacionEmail = async () => {
        try{
            const response = await axios.post('http://127.0.0.1:8000/api/verificaremail/',{
                email: formulario.value.email
            })
            if(respuesta.data.existe){
                existeEmail = true
            }
        }catch(error){
            console.error("Error al conectar con el servidor", error)
        }
    }

    const MensajeErrorContraseña = ref("")
    const MensajeErrorTelefono = ref("")
    const MensejeErrorEmail = ref("")

    const secValidacion = () => {
        MensajeErrorTelefono.value = ""
        MensajeErrorContraseña.value = ""
        MensejeErrorEmail.value = ""
        let valido = true

        if(formulario.value.numero_telefonico.length != 10){
            MensajeErrorTelefono.value = "El largo de tu telefono debe de ser de 10 digitos"
            valido = false 
        }
        if(formulario.value.password != formulario.value.confirmPassword){
            MensajeErrorContraseña.value = "Las contraseñas deben conincidir"
            valido = false
        } 
        if(existeEmail){
            MensejeErrorEmail.value = "No se pudo completar el registro. Por favor, verifica que los datos sean correctos o intenta iniciar sesión."
            valido = false
        }
        return valido
    }
    const pack = (rol) => {
        if(secValidacion()){
            enviarRegistroAgencia(rol)
        }
    }
    
    const Validacion = () => {
        console.log("¡El botón fue presionado!");
        if(tabActiva.value == 'turista'){
            formulario.value.group = 1
            enviarRegistroAgencia('turista')

        }else if(tabActiva.value == 'agencia'){
            formulario.value.group = 2
            formulario.value.username = formulario.value.nombre_agencia 
            pack('agencia')

        }else{
            formulario.value.group = 3
            formulario.value.username = formulario.value.nombre_empresa 
            pack('proveedor')
        }
    }
</script>

<template>
  <div class="min-h-screen bg-[#f0f4f8] flex items-center justify-center p-4 font-sans">
    <div class="bg-white rounded-2xl shadow-lg w-full max-w-md p-8">
      
      <div class="text-center mb-6">
        <h1 class="text-2xl font-bold text-gray-900 mb-2">Crear Cuenta</h1>
        <p class="text-sm text-gray-500">{{ subtituloActual }}</p>
      </div>

      <div class="flex bg-gray-100 p-1 rounded-lg mb-8">
        <button 
          @click="tabActiva = 'turista'"
          :class="['flex-1 flex items-center justify-center gap-2 py-2 text-sm font-medium rounded-md transition-all', 
                   tabActiva === 'turista' ? 'bg-white text-gray-900 shadow-sm border border-gray-200' : 'text-gray-500 hover:text-gray-700']"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
          Turista
        </button>

        <button 
          @click="tabActiva = 'agencia'"
          :class="['flex-1 flex items-center justify-center gap-2 py-2 text-sm font-medium rounded-md transition-all', 
                   tabActiva === 'agencia' ? 'bg-white text-gray-900 shadow-sm border border-gray-200' : 'text-gray-500 hover:text-gray-700']"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>
          Agencia
        </button>

        <button 
          @click="tabActiva = 'proveedor'"
          :class="['flex-1 flex items-center justify-center gap-2 py-2 text-sm font-medium rounded-md transition-all', 
                   tabActiva === 'proveedor' ? 'bg-white text-gray-900 shadow-sm border border-gray-900' : 'text-gray-500 hover:text-gray-700']"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>
          Proveedor
        </button>
      </div>

      <form @submit.prevent="Validacion">
        
        <template v-if="tabActiva === 'turista'">
          <div class="mb-4">
            <label class="block text-xs font-bold text-gray-700 mb-1">Nombres *</label>
            <input v-model="formulario.nombres" type="text" placeholder="Juan" class="w-full bg-[#f4f7f9] border-none text-gray-900 text-sm rounded-md focus:ring-2 focus:ring-teal-500 block p-3 outline-none" required />
          </div>
          <div class="mb-4">
            <label class="block text-xs font-bold text-gray-700 mb-1">Apellidos *</label>
            <input v-model="formulario.apellidos" type="text" placeholder="Pérez" class="w-full bg-[#f4f7f9] border-none text-gray-900 text-sm rounded-md focus:ring-2 focus:ring-teal-500 block p-3 outline-none" required />
          </div>
          <div class="mb-4">
            <label class="block text-xs font-bold text-gray-700 mb-1">Edad *</label>
            <input v-model="formulario.edad" type="number" placeholder="25" class="w-full bg-[#f4f7f9] border-none text-gray-900 text-sm rounded-md focus:ring-2 focus:ring-teal-500 block p-3 outline-none" required />
          </div>
          <div class="mb-4">
            <label class="block text-xs font-bold text-gray-700 mb-1">N° Identidad *</label>
            <input v-model="formulario.identidad" type="text" placeholder="1234567890" class="w-full bg-[#f4f7f9] border-none text-gray-900 text-sm rounded-md focus:ring-2 focus:ring-teal-500 block p-3 outline-none" required />
          </div>
          <div class="mb-4">
            <label class="block text-xs font-bold text-gray-700 mb-1">Correo Electrónico *</label>
            <input v-model="formulario.email" type="email" placeholder="usuario@ejemplo.com" class="w-full bg-[#f4f7f9] border-none text-gray-900 text-sm rounded-md focus:ring-2 focus:ring-teal-500 block p-3 outline-none" required />
          </div>
          <div class="mb-4">
            <label class="block text-xs font-bold text-gray-700 mb-1">Contraseña *</label>
            <input v-model="formulario.password" type="password" placeholder="••••••••" class="w-full bg-[#f4f7f9] border-none text-gray-900 text-sm rounded-md focus:ring-2 focus:ring-teal-500 block p-3 outline-none" required />
            <p v-if="MensajeErrorContraseña" class="errores">{{ MensajeErrorContraseña }}</p>
          </div>
          <div class="mb-6">
            <label class="block text-xs font-bold text-gray-700 mb-1">Confirmación de Contraseña *</label>
            <input v-model="formulario.confirmPassword" type="password" placeholder="••••••••" class="w-full bg-[#f4f7f9] border-none text-gray-900 text-sm rounded-md focus:ring-2 focus:ring-teal-500 block p-3 outline-none" required />
            <p v-if="MensajeErrorContraseña" class="errores">{{ MensajeErrorContraseña }}</p>
          </div>
        </template>

        <template v-if="tabActiva === 'agencia'">
          <div class="mb-4">
            <label class="block text-xs font-bold text-gray-700 mb-1">Nombre de la Agencia *</label>
            <input v-model="formulario.nombre_agencia" type="text" placeholder="Aventuras Colombia Tours" class="w-full bg-[#f4f7f9] border-none text-gray-900 text-sm rounded-md focus:ring-2 focus:ring-teal-500 block p-3 outline-none" required />
          </div>
          <div class="mb-4">
            <label class="block text-xs font-bold text-gray-700 mb-1">Correo Electrónico *</label>
            <input v-model="formulario.email" type="email" placeholder="agencia@ejemplo.com" class="w-full bg-[#f4f7f9] border-none text-gray-900 text-sm rounded-md focus:ring-2 focus:ring-teal-500 block p-3 outline-none" required />
            <p class="errores">{{ MensejeErrorEmail }}</p>
          </div>
          <div class="mb-4">
            <label class="block text-xs font-bold text-gray-700 mb-1">Telefóno *</label>
            <input v-model="formulario.numero_telefonico" type="tel" placeholder="+57 300 123 4567" class="w-full bg-[#f4f7f9] border-none text-gray-900 text-sm rounded-md focus:ring-2 focus:ring-teal-500 block p-3 outline-none" required />
            <p v-if="MensajeErrorTelefono" class="errores">{{ MensajeErrorTelefono }}</p>
          </div>
          <div class="mb-4">
   
            <label class="block text-xs font-bold text-gray-700 mb-1">Contraseña *</label>
            <input v-model="formulario.password" type="password" placeholder="••••••••" class="w-full bg-[#f4f7f9] border-none text-gray-900 text-sm rounded-md focus:ring-2 focus:ring-teal-500 block p-3 outline-none" required />
            <p v-if="MensajeErrorContraseña" class="errores">{{ MensajeErrorContraseña }}</p>
          </div>
          <div class="mb-6">
            <label class="block text-xs font-bold text-gray-700 mb-1">Confirmación de Contraseña *</label>
            <input v-model="formulario.confirmPassword" type="password" placeholder="••••••••" class="w-full bg-[#f4f7f9] border-none text-gray-900 text-sm rounded-md focus:ring-2 focus:ring-teal-500 block p-3 outline-none" required />
            <p v-if="MensajeErrorContraseña" class="errores">{{ MensajeErrorContraseña }}</p>
          </div>
        </template>

        <template v-if="tabActiva === 'proveedor'">
            <div class="mb-4">
                <label class="block text-xs font-bold text-gray-700 mb-1">Nombre de Empresa *</label>
                <input v-model="formulario.nombre_empresa" type="text" placeholder="Equipos de Aventura SA" class="w-full bg-[#f4f7f9] border-none text-gray-900 text-sm rounded-md focus:ring-2 focus:ring-teal-500 block p-3 outline-none" required />
            </div>
            <div class="mb-4">
                <label class="block text-xs font-bold text-gray-700 mb-1">Correo Electrónico *</label>
                <input v-model="formulario.email" type="email" placeholder="proveedor@ejemplo.com" class="w-full bg-[#f4f7f9] border-none text-gray-900 text-sm rounded-md focus:ring-2 focus:ring-teal-500 block p-3 outline-none" required />
            </div>
            <div class="mb-4">
                <label class="block text-xs font-bold text-gray-700 mb-1">Teléfono *</label>
                <input v-model="formulario.numero_telefonico" type="tel" placeholder="+57 300 987 6543" class="w-full bg-[#f4f7f9] border-none text-gray-900 text-sm rounded-md focus:ring-2 focus:ring-teal-500 block p-3 outline-none" required />
                <p v-if="MensajeErrorTelefono" class="errores">{{ MensajeErrorTelefono }}</p>
            </div>
           
            <div class="mb-6">
                <label class="block text-xs font-bold text-gray-700 mb-1">Contraseña *</label>
                <input v-model="formulario.password" type="password" placeholder="••••••••" class="w-full bg-[#f4f7f9] border-none text-gray-900 text-sm rounded-md focus:ring-2 focus:ring-teal-500 block p-3 outline-none" required />
                <p v-if="MensajeErrorContraseña" class="errores">{{ MensajeErrorContraseña }}</p>
            </div>
            <div class="mb-6">
                <label class="block text-xs font-bold text-gray-700 mb-1">Confirmación de Contraseña *</label>
                <input v-model="formulario.confirmPassword" type="password" placeholder="••••••••" class="w-full bg-[#f4f7f9] border-none text-gray-900 text-sm rounded-md focus:ring-2 focus:ring-teal-500 block p-3 outline-none" required />
                <p v-if="MensajeErrorContraseña" class="errores">{{ MensajeErrorContraseña }}</p>
            </div>
        </template>
        <button type="submit" class="w-full bg-[#008b8b] hover:bg-teal-700 text-white font-medium rounded-md text-sm px-5 py-3 text-center transition-colors">
          Registrarse
        </button>
      </form>
    
      <div class="mt-6 text-center text-xs text-gray-500">
        ¿Ya tienes una cuenta? <a href="#" class="text-blue-600 hover:underline">Inicia sesión aquí</a>
      </div>
      
    </div>
  </div>
</template>
<style>
    .errores{
        color: rgb(248, 80, 80);
        text-shadow: 0px 0px 3px red;
        text-align: left;
        margin: auto;
        font-size: 14px;
    }

</style>