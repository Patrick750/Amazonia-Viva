<script setup>
    import { ref, computed } from 'vue'
    import axios from 'axios'
    import { useRouter } from 'vue-router';

    const router = useRouter()

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
    first_name: '',
    last_name: '',
    username:'',
    fecha_nacimiento: '',
    numero_identidad: '',
    email: '',
    password: '',
    confirmPassword: '',
    nombre_agencia: '',
    ubicacion: '',
    numero_telefonico: '',
    nombre_empresa: '',
    group:''
    })
    const cargando = ref(false)
    const enviarRegistroAgencia = async (rol) => {
      cargando.value = true
      let registrado = false
        try{
            const respuesta = await axios.post(`http://127.0.0.1:8000/api/signup/${rol}/`, formulario.value);
            registrado = respuesta.data.exito

            console.log('Formulari enviado: ' + respuesta.data.mensaje)
        }catch (error){
            console.error("Hubo un error: " + error)
        }finally{
          cargando.value = false
        }
      return registrado
    }
    const VerificacionDatos = async () => {
        let existeEmail = false 
        try{
            const response = await axios.post('http://127.0.0.1:8000/api/verificaremail/',{
                email: formulario.value.email
            })
              existeEmail = response.data.email
        }catch(error){
            console.error("Error al conectar con el servidor", error)
        }
        return existeEmail
    }
    const VerificacionUsername = async () => {
        let existeUsername = false 
        try{
            const response = await axios.post('http://127.0.0.1:8000/api/verificaremail/',{
                username: formulario.value.username
            })
            existeUsername = response.data.username
          
        }catch(error){
            console.error("Error al conectar con el servidor", error)
        }
        return existeUsername
    }
    const VerificacionIdentidad = async () => {
      let identidadExiste = false
      try{
        const respuesta = await axios.post('http://127.0.0.1:8000/api/verificaremail/',{
          identidad: formulario.value.numero_identidad
        })
          identidadExiste = respuesta.data.identidad
      }catch (error){
        console.error('Error al consultar Identidad:', error)
      }
      return identidadExiste
    } 

    const MensajeErrorContraseña = ref("")
    const MensajeErrorTelefono = ref("")
    const MensejeErrorEmail = ref("")
    const MensejeErrorUsername = ref("")
    const MensajeErrorIdentidad = ref("")

    const validaciones = async (rol) => {
        MensajeErrorTelefono.value = ""
        MensajeErrorContraseña.value = ""
        MensejeErrorEmail.value = ""
        MensejeErrorUsername.value = ""
        MensajeErrorIdentidad.value = ""

        let valido = true

        if(formulario.value.password != formulario.value.confirmPassword){
            MensajeErrorContraseña.value = "Las contraseñas deben coincidir"
            valido = false
        }else if(formulario.value.password.length < 8){
            MensajeErrorContraseña.value = "La contraseña debe ser de almenos 8 digitos"
            valido = false
        }

        const emailExite = await VerificacionDatos() 
        if(emailExite){
          MensejeErrorEmail.value = "No se pudo completar el registro. Por favor, verifica tus credenciales sean correctas o intenta iniciar sesión."
          valido = false
        }

        if(['agencia','proveedor'].includes(rol)){
          const usernameExiste = await VerificacionUsername()
          if(usernameExiste){
            MensejeErrorUsername.value = "El nombre de empresa ya existe, intenta iniciar sesion"
            valido = false
          }
        }
        return valido
    }


    const secValidacion = async (rol) => {
        MensajeErrorIdentidad.value = ""

        const soloNumero = /^[0-9]+$/

        let valido = await validaciones(rol)
        if(rol == 'turista'){
          if(valido){
            const identidadExiste = await VerificacionIdentidad()
            if(identidadExiste){
              MensajeErrorIdentidad.value = "Este numero de  documento ya se encuentra registrado"
              valido = false
            }else if(!soloNumero.test(formulario.value.numero_identidad)){
              MensajeErrorIdentidad.value = "El campo identidad solo admite numeros"
              valido = false
            }else if(formulario.value.numero_identidad.length > 10){
              MensajeErrorIdentidad.value = "El numero de documento NO DEBE de contener más de 10 digitos"
              valido = false
            }else if(formulario.value.numero_identidad.length < 10){
              MensajeErrorIdentidad.value = "El numero de documento DEBE contener 10 digitos"
              valido = false
            }
          }
        }

        if(['proveedor','agencia'].includes(rol)){
          if(valido){
            if(formulario.value.numero_telefonico.length != 10){
                MensajeErrorTelefono.value = "El largo de tu telefono debe de ser de 10 digitos"
                valido = false 
            }else if(!soloNumero.test(formulario.value.numero_telefonico)){
                MensajeErrorTelefono.value = "Numero de telefono no valido"
                valido = false 
            }
          }
        }
        return valido
    }
    const pack = async (rol) => {
      const esValido = await secValidacion(rol)
      if(esValido){
        let h = await enviarRegistroAgencia(rol)          
        return h
      }
      return false
    }
    const Redirigir = (rol) => {
      router.push(`/panel/${rol}`)
    } 
    
    const saveTokens = async (pack, rol) => {
      if(pack){
        try{
          const response = await axios.post('http://127.0.0.1:8000/api/login/',{
            email: formulario.value.email,
            password: formulario.value.password
          })


          localStorage.setItem('token', response.data.access)
          localStorage.setItem('nombre_usuario', response.data.usuario.username)
          localStorage.setItem('rol', response.data.usuario.group)

          Redirigir(rol)

        }catch(error){
          router.push('/auth/signup')
        }
      }
    }

    
    const Validacion = async () => {
        console.log("¡El botón fue presionado!");

        if(tabActiva.value == 'turista'){
            const nombre = formulario.value.first_name.replace(/\s+/g,'_')
            const apellido = formulario.value.last_name.replace(/\s+/g,'_')
            let nombre_completo = `${nombre}${apellido}_${Date.now()}`.toLowerCase()
            formulario.value.username = nombre_completo
            formulario.value.group = 1
            
            const registroExitoso = await pack('turista')

            saveTokens(registroExitoso, 'turista')

        }else if(tabActiva.value == 'agencia'){
            formulario.value.group = 2
            formulario.value.username = formulario.value.nombre_agencia.replace(/\s+/g,'_')
            formulario.value.numero_telefonico = formulario.value.numero_telefonico.replaceAll(' ','')

            const registroExitoso = await pack('agencia')
            saveTokens(registroExitoso, 'agencia')

        }else if(tabActiva.value == 'proveedor'){
            formulario.value.group = 3
            formulario.value.username = formulario.value.nombre_empresa.replace(/\s+/g,'_')

            const registroExitoso = await pack('proveedor')
            saveTokens(registroExitoso, 'proveedor')
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
            <input v-model="formulario.first_name" type="text" placeholder="Juan" class="w-full bg-[#f4f7f9] border-none text-gray-900 text-sm rounded-md focus:ring-2 focus:ring-teal-500 block p-3 outline-none" required />
          </div>
          <div class="mb-4">
            <label class="block text-xs font-bold text-gray-700 mb-1">Apellidos *</label>
            <input v-model="formulario.last_name" type="text" placeholder="Pérez" class="w-full bg-[#f4f7f9] border-none text-gray-900 text-sm rounded-md focus:ring-2 focus:ring-teal-500 block p-3 outline-none" required />
            <p v-if="MensejeErrorUsername" class="errores">{{ MensejeErrorUsername }}</p>
          </div>
          <div class="mb-4">
            <label class="block text-xs font-bold text-gray-700 mb-1">Fecha de Nacimiento *</label>
            <input 
              v-model="formulario.fecha_nacimiento" 
              type="date" 
              class="w-full bg-[#f4f7f9] border-none text-gray-900 text-sm rounded-md focus:ring-2 focus:ring-teal-500 block p-3 outline-none" 
              required 
            />
          </div>
          <div class="mb-4">
            <label class="block text-xs font-bold text-gray-700 mb-1">N° Identidad *</label>
            <input v-model="formulario.numero_identidad" type="text" placeholder="1234567890" class="w-full bg-[#f4f7f9] border-none text-gray-900 text-sm rounded-md focus:ring-2 focus:ring-teal-500 block p-3 outline-none" required />
            <p v-if="MensajeErrorIdentidad" class="errores">{{ MensajeErrorIdentidad }}</p>
          </div>
          <div class="mb-4">
            <label class="block text-xs font-bold text-gray-700 mb-1">Correo Electrónico *</label>
            <input v-model="formulario.email" type="email" placeholder="usuario@ejemplo.com" class="w-full bg-[#f4f7f9] border-none text-gray-900 text-sm rounded-md focus:ring-2 focus:ring-teal-500 block p-3 outline-none" required />
            <p v-if="MensejeErrorEmail" class="errores">{{ MensejeErrorEmail }}</p>
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
            <p v-if="MensejeErrorUsername" class="errores">{{ MensejeErrorUsername }}</p>
          </div>
          <div class="mb-4">
            <label class="block text-xs font-bold text-gray-700 mb-1">Correo Electrónico *</label>
            <input v-model="formulario.email" type="email" placeholder="agencia@ejemplo.com" class="w-full bg-[#f4f7f9] border-none text-gray-900 text-sm rounded-md focus:ring-2 focus:ring-teal-500 block p-3 outline-none" required />
            <p v-if="MensejeErrorEmail" class="errores">{{ MensejeErrorEmail }}</p>
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
                <p v-if="MensejeErrorEmail" class="errores">{{ MensejeErrorEmail }}</p>
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
<button
        type="submit"
        :disabled="cargando"
        class="w-full py-3 bg-[#008c9e] hover:bg-[#007a8a] text-white rounded-md text-base font-medium transition-all mt-2 flex items-center justify-center disabled:opacity-70 disabled:cursor-not-allowed"
      >
        <template v-if="!cargando">
          Registrarse
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
    
      <div class="mt-6 text-center text-xs text-gray-500">
        ¿Ya tienes una cuenta? <router-link to="/auth/login" class="text-blue-600 hover:underline">Inicia sesión aquí</router-link>
      </div>
      
    </div>
  </div>
</template>
<style>
    .errores{
        color: rgb(248, 80, 80);
        text-align: left;
        margin: auto;
        font-size: 14px;
    }
</style>