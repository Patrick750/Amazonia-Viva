<script setup>
import { computed, nextTick, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import clienteAxios from '@/api/axios'
import AuthLayout from '@/components/auth/auth-layout.vue'
import CampoAuth from '@/components/auth/campo-auth.vue'
import { guardarSesion, mensajeDeConexion } from '@/composables/auth/useSesion'

const router = useRouter()

// Destino tras crear la cuenta. Se cambiará cuando el onboarding por rol de MEJ-002 esté definido.
const DESTINO_POSTERIOR_AL_REGISTRO = '/'

const roles = [
  { valor: 'turista', nombre: 'Turista', grupo: 1, descripcion: 'Quiero descubrir y reservar experiencias.', subtitulo: 'Únete a miles de viajeros y descubre experiencias inolvidables.' },
  { valor: 'agencia', nombre: 'Agencia', grupo: 2, descripcion: 'Ofrezco paquetes turísticos.', subtitulo: 'Registra tu agencia y conecta con viajeros de todo el mundo.' },
  { valor: 'proveedor', nombre: 'Proveedor', grupo: 3, descripcion: 'Vendo productos y servicios para viajeros.', subtitulo: 'Ofrece tus servicios y haz crecer tu negocio turístico.' },
]

const camposPorRol = {
  turista: ['first_name', 'last_name', 'fecha_nacimiento', 'numero_identidad', 'numero_telefonico', 'email', 'password', 'confirmPassword'],
  agencia: ['nombre_agencia', 'numero_telefonico', 'email', 'password', 'confirmPassword'],
  proveedor: ['nombre_empresa', 'numero_telefonico', 'email', 'password', 'confirmPassword'],
}

const rolActivo = ref('turista')
const rolActual = computed(() => roles.find(rol => rol.valor === rolActivo.value))
const campos = computed(() => camposPorRol[rolActivo.value])
const campoNombre = computed(() => ({ agencia: 'nombre_agencia', proveedor: 'nombre_empresa' })[rolActivo.value] || null)

// Un único objeto conserva lo escrito aunque la persona cambie de rol.
const formulario = reactive({
  first_name: '', last_name: '', username: '', fecha_nacimiento: '', numero_identidad: '',
  email: '', password: '', confirmPassword: '', nombre_agencia: '', ubicacion: '',
  numero_telefonico: '', nombre_empresa: '', group: '',
})
const errores = reactive(Object.fromEntries(Object.values(camposPorRol).flat().map(campo => [campo, ''])))
const errorGeneral = ref('')
const cargando = ref(false)
const bannerError = ref(null)

const soloDigitos = /^\d+$/
const formatoCorreo = /^\S+@\S+\.\S+$/
const hoy = new Date().toISOString().slice(0, 10)
const sinEspacios = valor => String(valor).replace(/\s+/g, '')

const reglas = {
  first_name: v => (v.trim() ? '' : 'Escribe tus nombres.'),
  last_name: v => (v.trim() ? '' : 'Escribe tus apellidos.'),
  fecha_nacimiento: v => (!v ? 'Indica tu fecha de nacimiento.' : v > hoy ? 'La fecha no puede ser futura.' : ''),
  numero_identidad: (v) => {
    const numero = v.trim()
    if (!numero) return 'Escribe tu número de identidad.'
    if (!soloDigitos.test(numero)) return 'Escribe solo números.'
    return numero.length === 10 ? '' : 'Debe tener exactamente 10 dígitos.'
  },
  numero_telefonico: (v, rol) => {
    if (rol === 'turista') return ''
    const numero = sinEspacios(v)
    if (!numero) return 'Escribe un teléfono de contacto.'
    if (!soloDigitos.test(numero)) return 'Escribe solo números.'
    return numero.length === 10 ? '' : 'Debe tener 10 dígitos.'
  },
  nombre_agencia: v => (v.trim() ? '' : 'Escribe el nombre de tu agencia.'),
  nombre_empresa: v => (v.trim() ? '' : 'Escribe el nombre de tu empresa.'),
  email: v => (!v.trim() ? 'Escribe tu correo electrónico.' : !formatoCorreo.test(v.trim()) ? 'Revisa el formato del correo, por ejemplo nombre@correo.com.' : ''),
  password: v => (v.length >= 8 ? '' : 'Usa al menos 8 caracteres.'),
  confirmPassword: v => (!v ? 'Repite la contraseña.' : v !== formulario.password ? 'Las contraseñas no coinciden.' : ''),
}

const validarCampo = (campo) => {
  errores[campo] = reglas[campo](formulario[campo], rolActivo.value)
}

const alEscribir = (campo) => {
  errores[campo] = ''
  errorGeneral.value = ''
}

const limpiarErrores = () => {
  Object.keys(errores).forEach((campo) => { errores[campo] = '' })
  errorGeneral.value = ''
}

watch(rolActivo, limpiarErrores)

const primerCampoConError = () => campos.value.find(campo => errores[campo])

const enfocarPrimerError = async () => {
  const campo = primerCampoConError()
  await nextTick()
  if (campo) document.getElementById(`signup-${campo}`)?.focus()
  else bannerError.value?.focus()
}

const nombreDeUsuario = () => {
  if (rolActivo.value === 'turista') {
    const nombre = formulario.first_name.replace(/\s+/g, '_')
    const apellido = formulario.last_name.replace(/\s+/g, '_')
    return `${nombre}${apellido}_${Date.now()}`.toLowerCase()
  }
  return formulario[campoNombre.value].replace(/\s+/g, '_')
}

// Los mismos datos que antes, sin modificar lo que la persona ve en el formulario.
const construirPayload = () => {
  const rol = rolActivo.value
  const datos = { ...formulario, group: rolActual.value.grupo, username: nombreDeUsuario() }
  if (rol !== 'turista') {
    datos.numero_telefonico = sinEspacios(datos.numero_telefonico)
    datos[campoNombre.value] = datos[campoNombre.value].toLowerCase()
  }
  return datos
}

// Si la consulta falla (red o límite de intentos), no se bloquea: el registro vuelve a validar en el servidor.
const existe = async (cuerpo, clave) => {
  try {
    const { data } = await clienteAxios.post('api/verificaremail/', cuerpo)
    return Boolean(data[clave])
  } catch {
    return false
  }
}

const verificarDuplicados = async () => {
  const consultas = [
    existe({ email: formulario.email }, 'email').then((repetido) => {
      if (repetido) errores.email = 'Este correo ya está registrado. Intenta iniciar sesión.'
    }),
  ]
  if (rolActivo.value === 'turista') {
    consultas.push(existe({ identidad: formulario.numero_identidad }, 'identidad').then((repetido) => {
      if (repetido) errores.numero_identidad = 'Este documento ya está registrado.'
    }))
  } else {
    consultas.push(existe({ username: nombreDeUsuario() }, 'username').then((repetido) => {
      if (repetido) errores[campoNombre.value] = 'Este nombre ya existe, intenta con otro.'
    }))
  }
  await Promise.all(consultas)
  return !primerCampoConError()
}

const mostrarErrorDelServidor = (error) => {
  const conexion = mensajeDeConexion(error)
  if (conexion) {
    errorGeneral.value = conexion
    return
  }
  const generales = []
  const detalle = error.response?.data
  if (detalle && typeof detalle === 'object') {
    Object.entries(detalle).forEach(([campo, mensajes]) => {
      const texto = Array.isArray(mensajes) ? mensajes.join(' ') : String(mensajes)
      const destino = campo === 'username' ? campoNombre.value : campo
      if (destino && campos.value.includes(destino)) errores[destino] = texto
      else generales.push(texto)
    })
  }
  errorGeneral.value = generales.length
    ? generales.join(' ')
    : primerCampoConError() ? 'Revisa los campos marcados para continuar.' : 'No pudimos crear tu cuenta. Revisa los datos e inténtalo de nuevo.'
}

const registrar = async () => {
  try {
    const { data } = await clienteAxios.post(`api/signup/${rolActivo.value}/`, construirPayload())
    if (data.exito) return true
    errorGeneral.value = 'No pudimos crear tu cuenta. Inténtalo de nuevo.'
  } catch (error) {
    console.error('No se pudo registrar la cuenta', error)
    mostrarErrorDelServidor(error)
  }
  return false
}

const iniciarSesion = async () => {
  try {
    const { data } = await clienteAxios.post('api/login/', { email: formulario.email, password: formulario.password })
    guardarSesion(data)
    window.location.href = DESTINO_POSTERIOR_AL_REGISTRO
  } catch (error) {
    // La cuenta ya existe; si el acceso automático falla, la persona inicia sesión desde su pantalla.
    console.error('No se pudo iniciar sesión tras el registro', error)
    router.push({ path: '/auth/login', query: { registro: 'ok' } })
  }
}

const enviar = async () => {
  if (cargando.value) return
  errorGeneral.value = ''
  campos.value.forEach(validarCampo)
  if (primerCampoConError()) {
    await enfocarPrimerError()
    return
  }

  cargando.value = true
  try {
    if (!(await verificarDuplicados()) || !(await registrar())) {
      await enfocarPrimerError()
      return
    }
    await iniciarSesion()
  } finally {
    cargando.value = false
  }
}
</script>

<template>
  <AuthLayout titulo="Empieza tu próxima aventura." texto="Explora destinos únicos, gestiona tu agencia o provee servicios turísticos en la región.">
    <div class="mx-auto w-full max-w-xl">
      <h1 class="mb-2 text-3xl font-extrabold tracking-tight text-gray-950">Crear cuenta</h1>
      <p class="mb-8 text-base text-gray-700">{{ rolActual.subtitulo }}</p>

      <fieldset class="mb-8">
        <legend class="mb-3 text-sm font-semibold text-gray-900">¿Cómo vas a usar Amazonia Viva?</legend>
        <div class="grid grid-cols-1 gap-3 sm:grid-cols-3">
          <label v-for="rol in roles" :key="rol.valor" class="relative cursor-pointer">
            <input v-model="rolActivo" type="radio" name="rol" :value="rol.valor" class="peer sr-only" />
            <span class="flex h-full flex-col gap-1 rounded-2xl border-2 border-gray-300 bg-white p-4 transition-colors hover:border-gray-400 peer-checked:border-teal-700 peer-checked:bg-teal-50 peer-focus-visible:ring-2 peer-focus-visible:ring-teal-700 peer-focus-visible:ring-offset-2">
              <span class="text-base font-bold text-gray-950">{{ rol.nombre }}</span>
              <span class="text-sm text-gray-700">{{ rol.descripcion }}</span>
            </span>
          </label>
        </div>
      </fieldset>

      <div v-if="errorGeneral" ref="bannerError" tabindex="-1" class="mb-6 flex items-start gap-2 rounded-xl border border-red-300 bg-red-50 px-4 py-3 text-sm font-medium text-red-800 outline-none focus-visible:ring-2 focus-visible:ring-red-700" role="alert">
        <svg class="mt-0.5 h-4 w-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
        <span>{{ errorGeneral }}</span>
      </div>

      <form novalidate class="space-y-8" @submit.prevent="enviar">
        <p class="text-sm text-gray-700">Todos los campos son obligatorios, salvo los marcados como opcionales.</p>

        <fieldset class="space-y-5">
          <legend class="mb-4 text-lg font-bold text-gray-950">{{ rolActivo === 'turista' ? 'Tus datos' : rolActivo === 'agencia' ? 'Datos de la agencia' : 'Datos de la empresa' }}</legend>

          <template v-if="rolActivo === 'turista'">
            <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
              <CampoAuth id="signup-first_name" v-model="formulario.first_name" label="Nombres" autocomplete="given-name" placeholder="Juan" :error="errores.first_name" @update:model-value="alEscribir('first_name')" @blur="validarCampo('first_name')" />
              <CampoAuth id="signup-last_name" v-model="formulario.last_name" label="Apellidos" autocomplete="family-name" placeholder="Pérez" :error="errores.last_name" @update:model-value="alEscribir('last_name')" @blur="validarCampo('last_name')" />
            </div>
            <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
              <CampoAuth id="signup-fecha_nacimiento" v-model="formulario.fecha_nacimiento" label="Fecha de nacimiento" type="date" autocomplete="bday" :max="hoy" :error="errores.fecha_nacimiento" @update:model-value="alEscribir('fecha_nacimiento')" @blur="validarCampo('fecha_nacimiento')" />
              <CampoAuth id="signup-numero_identidad" v-model="formulario.numero_identidad" label="Número de identidad" inputmode="numeric" :maxlength="10" placeholder="1234567890" ayuda="10 dígitos, sin puntos ni espacios." :error="errores.numero_identidad" @update:model-value="alEscribir('numero_identidad')" @blur="validarCampo('numero_identidad')" />
            </div>
            <CampoAuth id="signup-numero_telefonico" v-model="formulario.numero_telefonico" label="Teléfono" type="tel" autocomplete="tel" inputmode="tel" placeholder="300 123 4567" opcional :error="errores.numero_telefonico" @update:model-value="alEscribir('numero_telefonico')" />
          </template>

          <template v-else>
            <CampoAuth
              v-if="rolActivo === 'agencia'"
              id="signup-nombre_agencia" v-model="formulario.nombre_agencia" label="Nombre de la agencia" autocomplete="organization" placeholder="Aventuras Colombia Tours"
              :error="errores.nombre_agencia" @update:model-value="alEscribir('nombre_agencia')" @blur="validarCampo('nombre_agencia')"
            />
            <CampoAuth
              v-else
              id="signup-nombre_empresa" v-model="formulario.nombre_empresa" label="Nombre de la empresa" autocomplete="organization" placeholder="Equipos de Aventura SA"
              :error="errores.nombre_empresa" @update:model-value="alEscribir('nombre_empresa')" @blur="validarCampo('nombre_empresa')"
            />
            <CampoAuth id="signup-numero_telefonico" v-model="formulario.numero_telefonico" label="Teléfono de contacto" type="tel" autocomplete="tel" inputmode="tel" placeholder="300 123 4567" ayuda="Puedes escribirlo con espacios. Debe tener 10 dígitos." :error="errores.numero_telefonico" @update:model-value="alEscribir('numero_telefonico')" @blur="validarCampo('numero_telefonico')" />
          </template>
        </fieldset>

        <fieldset class="space-y-5">
          <legend class="mb-4 text-lg font-bold text-gray-950">Acceso a tu cuenta</legend>
          <CampoAuth id="signup-email" v-model="formulario.email" label="Correo electrónico" type="email" autocomplete="email" placeholder="nombre@correo.com" :error="errores.email" @update:model-value="alEscribir('email')" @blur="validarCampo('email')" />
          <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
            <CampoAuth id="signup-password" v-model="formulario.password" label="Contraseña" type="password" autocomplete="new-password" ayuda="Mínimo 8 caracteres." :error="errores.password" @update:model-value="alEscribir('password')" @blur="validarCampo('password')" />
            <CampoAuth id="signup-confirmPassword" v-model="formulario.confirmPassword" label="Confirmar contraseña" type="password" autocomplete="new-password" :error="errores.confirmPassword" @update:model-value="alEscribir('confirmPassword')" @blur="validarCampo('confirmPassword')" />
          </div>
        </fieldset>

        <button
          type="submit"
          :disabled="cargando"
          class="flex w-full items-center justify-center rounded-xl bg-emerald-700 px-4 py-3.5 text-base font-bold text-white outline-none transition-colors hover:bg-emerald-800 focus-visible:ring-2 focus-visible:ring-emerald-700 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-70"
        >
          <svg v-if="cargando" class="mr-3 h-5 w-5 motion-safe:animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" aria-hidden="true">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ cargando ? 'Creando tu cuenta…' : 'Crear mi cuenta' }}
        </button>
      </form>

      <p class="mt-8 text-center text-sm text-gray-700">
        ¿Ya tienes cuenta?
        <router-link to="/auth/login" class="font-bold text-teal-700 underline-offset-4 hover:underline focus-visible:outline-2 focus-visible:outline-teal-700">Iniciar sesión</router-link>
      </p>
    </div>
  </AuthLayout>
</template>
