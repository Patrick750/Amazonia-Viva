<script setup>
    import { ref, computed } from 'vue'
    import axios from 'axios'
    import { useRouter } from 'vue-router';
    

    const router = useRouter()

    // Estado para controlar qué pestaña está activa
    const tabActiva = ref('turista')

    // Textos dinámicos según el rol seleccionado
    const subtitulos = {
    turista: 'Únete a miles de viajeros y descubre experiencias inolvidables.', 
    agencia: 'Registra tu Agencia y conecta con viajeros de todo el mundo.',
    proveedor: 'Ofrece tus servicios y haz crecer tu negocio turístico.'
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
            MensajeErrorContraseña.value = "Debe tener almenos 8 caracteres"
            valido = false
        }

        const emailExite = await VerificacionDatos() 
        if(emailExite){
          MensejeErrorEmail.value = "Este correo ya está registrado. Intenta iniciar sesión."
          valido = false
        }

        if(['agencia','proveedor'].includes(rol)){
          const usernameExiste = await VerificacionUsername()
          if(usernameExiste){
            MensejeErrorUsername.value = "Este nombre ya existe, intenta con otro."
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
              MensajeErrorIdentidad.value = "Este documento ya está registrado"
              valido = false
            }else if(!soloNumero.test(formulario.value.numero_identidad)){
              MensajeErrorIdentidad.value = "Solo se admiten números"
              valido = false
            }else if(formulario.value.numero_identidad.length != 10){
              MensajeErrorIdentidad.value = "Debe contener exactamente 10 dígitos"
              valido = false
            }
          }
        }

        if(['proveedor','agencia'].includes(rol)){
          if(valido){
            if(formulario.value.numero_telefonico.length != 10){
                MensajeErrorTelefono.value = "Debe tener 10 dígitos"
                valido = false 
            }else if(!soloNumero.test(formulario.value.numero_telefonico)){
                MensajeErrorTelefono.value = "Número no válido"
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
    const Redirigir = () => {
      router.push(`/panel`)
    } 
    
    const saveTokens = async (pack) => {
      if(pack){
        try{
          const response = await axios.post('http://127.0.0.1:8000/api/login/',{
            email: formulario.value.email,
            password: formulario.value.password
          })

          localStorage.setItem('token', response.data.access)
          localStorage.setItem('nombre',response.data.usuario.nombre)
          localStorage.setItem('apellido', response.data.usuario.apellido)
          localStorage.setItem('nombre_usuario', response.data.usuario.username)
          localStorage.setItem('nombre_empresa', response.data.usuario.nombre_empresa)
          localStorage.setItem('nombre_agencia', response.data.usuario.nombre_agencia)
          localStorage.setItem('rol', response.data.usuario.group)

          window.location.href = '/panel'
          Redirigir()

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
            formulario.value.nombre_agencia = formulario.value.nombre_agencia.toLowerCase()
            formulario.value.numero_telefonico = formulario.value.numero_telefonico.replaceAll(' ','')

            const registroExitoso = await pack('agencia')
            saveTokens(registroExitoso, 'agencia')

        }else if(tabActiva.value == 'proveedor'){
            formulario.value.group = 3
            formulario.value.username = formulario.value.nombre_empresa.replace(/\s+/g,'_')
            formulario.value.nombre_empresa = formulario.value.nombre_empresa.toLowerCase()

            const registroExitoso = await pack('proveedor')
            saveTokens(registroExitoso, 'proveedor')
        }
    }
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex items-center justify-center p-0 md:p-6 font-sans relative overflow-hidden">
    
    <div class="absolute -top-40 -left-40 w-80 h-80 bg-teal-100 rounded-full opacity-50 blur-3xl"></div>
    <div class="absolute -bottom-40 -right-40 w-80 h-80 bg-emerald-100 rounded-full opacity-50 blur-3xl"></div>

    <div class="bg-white rounded-none md:rounded-3xl shadow-[0_10px_40px_rgba(0,0,0,0.08)] w-full max-w-6xl flex overflow-hidden min-h-[90vh] md:min-h-[auto] z-10">
      
      <div class="hidden lg:flex lg:w-1/2 relative bg-gray-900 p-12 flex-col justify-between text-white">
        <img 
          src="https://images.unsplash.com/photo-1527631746610-bca00a040d60?ixlib=rb-4.0.3&auto=format&fit=crop&w=1000&q=80" 
          alt="Viaje" 
          class="absolute inset-0 w-full h-full object-cover opacity-60"
        />
        <div class="absolute inset-0 bg-gradient-to-t from-gray-900 via-gray-900/20 to-transparent"></div>

        <div class="relative z-10">
          <div class="flex items-center gap-2 mb-10">
            <div class="bg-white/20 p-2.5 rounded-xl backdrop-blur-sm">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="text-white"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>
            </div>
            <span class="text-xl font-bold tracking-tight">Travel<span class="text-teal-300">Hub</span></span>
          </div>
        </div>

        <div class="relative z-10 mb-10">
          <h2 class="text-5xl font-extrabold leading-tight tracking-tight mb-4">Empieza tu <br/>próxima <span class="text-teal-300">aventura</span>.</h2>
          <p class="text-lg text-gray-200 max-w-md font-medium opacity-90">Explora destinos únicos, gestiona tu agencia o provee servicios turísticos en la plataforma líder de la región.</p>
        </div>
        
        <div class="relative z-10 text-sm text-gray-400">
            © 2026 TravelHub Global. Todos los derechos reservados.
        </div>
      </div>

      <div class="w-full lg:w-1/2 p-6 sm:p-10 md:p-14 flex flex-col justify-center">
        
        <div class="text-center lg:text-left mb-8">
          <h1 class="text-3xl sm:text-4xl font-extrabold text-gray-950 tracking-tighter mb-2.5">Crear Cuenta</h1>
          <p class="text-base text-gray-600 font-medium max-w-md mx-auto lg:mx-0">{{ subtituloActual }}</p>
        </div>

        <div class="flex bg-gray-100 p-1.5 rounded-full mb-9 shadow-inner border border-gray-200/50">
          <button 
            @click="tabActiva = 'turista'"
            :class="['flex-1 flex items-center justify-center gap-2.5 py-3 px-4 text-sm font-semibold rounded-full transition-all duration-300', 
                     tabActiva === 'turista' ? 'bg-white text-teal-700 shadow-md shadow-gray-200/50' : 'text-gray-600 hover:text-gray-900']"
          >
            <svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
            Turista
          </button>

          <button 
            @click="tabActiva = 'agencia'"
            :class="['flex-1 flex items-center justify-center gap-2.5 py-3 px-4 text-sm font-semibold rounded-full transition-all duration-300', 
                     tabActiva === 'agencia' ? 'bg-white text-teal-700 shadow-md shadow-gray-200/50' : 'text-gray-600 hover:text-gray-900']"
          >
            <svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>
            Agencia
          </button>

          <button 
            @click="tabActiva = 'proveedor'"
            :class="['flex-1 flex items-center justify-center gap-2.5 py-3 px-4 text-sm font-semibold rounded-full transition-all duration-300', 
                     tabActiva === 'proveedor' ? 'bg-white text-teal-700 shadow-md shadow-gray-200/50' : 'text-gray-600 hover:text-gray-900']"
          >
            <svg class="w-4.5 h-4.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>
            Proveedor
          </button>
        </div>

        <form @submit.prevent="Validacion" class="space-y-5">
          
          <template v-if="tabActiva === 'turista'">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
                <div class="flex flex-col">
                    <label class="block text-xs font-bold text-gray-800 mb-1.5 ml-1 uppercase tracking-wider opacity-90">Nombres *</label>
                    <input v-model="formulario.first_name" type="text" placeholder="Juan" class="w-full bg-slate-100/70 border border-gray-200/50 text-gray-950 text-sm rounded-xl focus:ring-2 focus:ring-teal-300 focus:border-teal-400 block p-3.5 outline-none transition-all duration-200 placeholder:text-gray-400 shadow-inner" required />
                </div>
                <div class="flex flex-col">
                    <label class="block text-xs font-bold text-gray-800 mb-1.5 ml-1 uppercase tracking-wider opacity-90">Apellidos *</label>
                    <input v-model="formulario.last_name" type="text" placeholder="Pérez" class="w-full bg-slate-100/70 border border-gray-200/50 text-gray-950 text-sm rounded-xl focus:ring-2 focus:ring-teal-300 focus:border-teal-400 block p-3.5 outline-none transition-all duration-200 placeholder:text-gray-400 shadow-inner" required />
                </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
                <div class="flex flex-col">
                    <label class="block text-xs font-bold text-gray-800 mb-1.5 ml-1 uppercase tracking-wider opacity-90">Fecha de Nacimiento *</label>
                    <input v-model="formulario.fecha_nacimiento" type="date" class="w-full bg-slate-100/70 border border-gray-200/50 text-gray-950 text-sm rounded-xl focus:ring-2 focus:ring-teal-300 focus:border-teal-400 block p-3.5 outline-none transition-all duration-200 placeholder:text-gray-400 shadow-inner" required />
                </div>
                <div class="flex flex-col relative">
                    <label class="block text-xs font-bold text-gray-800 mb-1.5 ml-1 uppercase tracking-wider opacity-90">N° Identidad *</label>
                    <input v-model="formulario.numero_identidad" type="text" placeholder="1234567890" class="w-full bg-slate-100/70 border border-gray-200/50 text-gray-950 text-sm rounded-xl focus:ring-2 focus:ring-teal-300 focus:border-teal-400 block p-3.5 outline-none transition-all duration-200 placeholder:text-gray-400 shadow-inner" :class="{'border-red-300 bg-red-50': MensajeErrorIdentidad}" required />
                    <div v-if="MensajeErrorIdentidad" class="text-red-600 text-xs font-semibold mt-1.5 ml-1 flex items-center gap-1.5 animate-pulse">
                        <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                        <span>{{ MensajeErrorIdentidad }}</span>
                    </div>
                </div>
            </div>
          </template>

          <template v-if="tabActiva === 'agencia'">
            <div class="flex flex-col relative">
              <label class="block text-xs font-bold text-gray-800 mb-1.5 ml-1 uppercase tracking-wider opacity-90">Nombre de la Agencia *</label>
              <input v-model="formulario.nombre_agencia" type="text" placeholder="Aventuras Colombia Tours" class="w-full bg-slate-100/70 border border-gray-200/50 text-gray-950 text-sm rounded-xl focus:ring-2 focus:ring-teal-300 focus:border-teal-400 block p-3.5 outline-none transition-all duration-200 placeholder:text-gray-400 shadow-inner" :class="{'border-red-300 bg-red-50': MensejeErrorUsername}" required />
              <div v-if="MensejeErrorUsername" class="text-red-600 text-xs font-semibold mt-1.5 ml-1 flex items-center gap-1.5 animate-pulse">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                <span>{{ MensejeErrorUsername }}</span>
              </div>
            </div>
            <div class="flex flex-col relative">
              <label class="block text-xs font-bold text-gray-800 mb-1.5 ml-1 uppercase tracking-wider opacity-90">Telefóno *</label>
              <input v-model="formulario.numero_telefonico" type="tel" placeholder="300 123 4567" class="w-full bg-slate-100/70 border border-gray-200/50 text-gray-950 text-sm rounded-xl focus:ring-2 focus:ring-teal-300 focus:border-teal-400 block p-3.5 outline-none transition-all duration-200 placeholder:text-gray-400 shadow-inner" :class="{'border-red-300 bg-red-50': MensajeErrorTelefono}" required />
              <div v-if="MensajeErrorTelefono" class="text-red-600 text-xs font-semibold mt-1.5 ml-1 flex items-center gap-1.5 animate-pulse">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                <span>{{ MensajeErrorTelefono }}</span>
              </div>
            </div>
          </template>

          <template v-if="tabActiva === 'proveedor'">
            <div class="flex flex-col relative">
                <label class="block text-xs font-bold text-gray-800 mb-1.5 ml-1 uppercase tracking-wider opacity-90">Nombre de Empresa *</label>
                <input v-model="formulario.nombre_empresa" type="text" placeholder="Equipos de Aventura SA" class="w-full bg-slate-100/70 border border-gray-200/50 text-gray-950 text-sm rounded-xl focus:ring-2 focus:ring-teal-300 focus:border-teal-400 block p-3.5 outline-none transition-all duration-200 placeholder:text-gray-400 shadow-inner" :class="{'border-red-300 bg-red-50': MensejeErrorUsername}" required />
                <div v-if="MensejeErrorUsername" class="text-red-600 text-xs font-semibold mt-1.5 ml-1 flex items-center gap-1.5 animate-pulse">
                    <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                    <span>{{ MensejeErrorUsername }}</span>
                </div>
            </div>
            <div class="flex flex-col relative">
                <label class="block text-xs font-bold text-gray-800 mb-1.5 ml-1 uppercase tracking-wider opacity-90">Teléfono *</label>
                <input v-model="formulario.numero_telefonico" type="tel" placeholder="300 987 6543" class="w-full bg-slate-100/70 border border-gray-200/50 text-gray-950 text-sm rounded-xl focus:ring-2 focus:ring-teal-300 focus:border-teal-400 block p-3.5 outline-none transition-all duration-200 placeholder:text-gray-400 shadow-inner" :class="{'border-red-300 bg-red-50': MensajeErrorTelefono}" required />
                <div v-if="MensajeErrorTelefono" class="text-red-600 text-xs font-semibold mt-1.5 ml-1 flex items-center gap-1.5 animate-pulse">
                    <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                    <span>{{ MensajeErrorTelefono }}</span>
                </div>
            </div>
          </template>

          <div class="flex flex-col relative">
            <label class="block text-xs font-bold text-gray-800 mb-1.5 ml-1 uppercase tracking-wider opacity-90">Correo Electrónico *</label>
            <input v-model="formulario.email" type="email" placeholder="usuario@ejemplo.com" class="w-full bg-slate-100/70 border border-gray-200/50 text-gray-950 text-sm rounded-xl focus:ring-2 focus:ring-teal-300 focus:border-teal-400 block p-3.5 outline-none transition-all duration-200 placeholder:text-gray-400 shadow-inner" :class="{'border-red-300 bg-red-50': MensejeErrorEmail}" required />
            <div v-if="MensejeErrorEmail" class="text-red-600 text-xs font-semibold mt-1.5 ml-1 flex items-center gap-1.5 animate-pulse">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                <span>{{ MensejeErrorEmail }}</span>
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-5 relative">
              <div class="flex flex-col">
                <label class="block text-xs font-bold text-gray-800 mb-1.5 ml-1 uppercase tracking-wider opacity-90">Contraseña *</label>
                <input v-model="formulario.password" type="password" placeholder="••••••••" class="w-full bg-slate-100/70 border border-gray-200/50 text-gray-950 text-sm rounded-xl focus:ring-2 focus:ring-teal-300 focus:border-teal-400 block p-3.5 outline-none transition-all duration-200 placeholder:text-gray-400 shadow-inner" :class="{'border-red-300 bg-red-50': MensajeErrorContraseña}" required />
              </div>
              <div class="flex flex-col">
                <label class="block text-xs font-bold text-gray-800 mb-1.5 ml-1 uppercase tracking-wider opacity-90">Confirmar Contraseña *</label>
                <input v-model="formulario.confirmPassword" type="password" placeholder="••••••••" class="w-full bg-slate-100/70 border border-gray-200/50 text-gray-950 text-sm rounded-xl focus:ring-2 focus:ring-teal-300 focus:border-teal-400 block p-3.5 outline-none transition-all duration-200 placeholder:text-gray-400 shadow-inner" :class="{'border-red-300 bg-red-50': MensajeErrorContraseña}" required />
              </div>
              <div v-if="MensajeErrorContraseña" class="text-red-600 text-xs font-semibold mt-1.5 ml-1 flex items-center gap-1.5 animate-pulse sm:col-span-2">
                <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                <span>{{ MensajeErrorContraseña }}</span>
              </div>
          </div>

          <button
            type="submit"
            :disabled="cargando"
            class="w-full py-4 bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-600 hover:to-emerald-600 text-white rounded-full text-base font-bold tracking-wide transition-all duration-300 mt-6 flex items-center justify-center shadow-lg shadow-teal-500/30 hover:shadow-teal-500/50 hover:-translate-y-0.5 disabled:opacity-70 disabled:cursor-not-allowed disabled:transform-none"
          >
            <template v-if="!cargando">
              Crear mi cuenta
            </template>
            <template v-else>
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Procesando registro...
            </template>
          </button>
        </form>
    
        <div class="mt-10 text-center text-sm text-gray-600 font-medium">
          ¿Ya eres parte de TravelHub? 
          <router-link to="/auth/login" class="text-teal-700 font-bold hover:text-teal-500 transition-colors hover:underline underline-offset-4">Inicia sesión aquí</router-link>
        </div>
        
      </div>
    </div>
  </div>
</template>
