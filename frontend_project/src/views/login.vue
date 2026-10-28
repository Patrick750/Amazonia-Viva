<script setup>
import { reactive, ref } from 'vue'
import { useRoute } from 'vue-router'
import clienteAxios from '@/api/axios'
import AuthLayout from '@/components/auth/auth-layout.vue'
import CampoAuth from '@/components/auth/campo-auth.vue'
import { guardarSesion, mensajeDeConexion } from '@/composables/auth/useSesion'

const route = useRoute()
const cargando = ref(false)
const errorGeneral = ref('')
const registroReciente = route.query.registro === 'ok'

const formulario = reactive({ email: '', password: '' })
const errores = reactive({ email: '', password: '' })

const formatoCorreo = /^\S+@\S+\.\S+$/

const validar = () => {
  errores.email = !formulario.email.trim()
    ? 'Escribe tu correo electrónico.'
    : !formatoCorreo.test(formulario.email.trim()) ? 'Revisa el formato del correo, por ejemplo nombre@correo.com.' : ''
  errores.password = formulario.password ? '' : 'Escribe tu contraseña.'
  const primerError = ['email', 'password'].find(campo => errores[campo])
  if (primerError) document.getElementById(`login-${primerError}`)?.focus()
  return !primerError
}

const limpiarError = (campo) => {
  errores[campo] = ''
  errorGeneral.value = ''
}

const procesarLogin = async () => {
  if (cargando.value) return
  errorGeneral.value = ''
  if (!validar()) return

  cargando.value = true
  try {
    const { data } = await clienteAxios.post('api/login/', {
      email: formulario.email,
      password: formulario.password,
    })
    guardarSesion(data)
    window.location.href = '/'
  } catch (error) {
    errorGeneral.value = mensajeDeConexion(error) || 'El correo o la contraseña no son correctos. Revísalos e inténtalo de nuevo.'
    console.error('No se pudo iniciar sesión', error)
  } finally {
    cargando.value = false
  }
}
</script>

<template>
  <AuthLayout titulo="Tu próximo viaje te espera." texto="Accede a tu cuenta para reservar experiencias, gestionar tu agencia o administrar tus productos.">
    <div class="mx-auto w-full max-w-md">
      <h1 class="mb-2 text-3xl font-extrabold tracking-tight text-gray-950">Iniciar sesión</h1>
      <p class="mb-8 text-base text-gray-700">Ingresa con tu correo y tu contraseña.</p>

      <p v-if="registroReciente && !errorGeneral" class="mb-6 rounded-xl border border-emerald-300 bg-emerald-50 px-4 py-3 text-sm font-medium text-emerald-900" role="status">
        Tu cuenta fue creada. Inicia sesión para continuar.
      </p>

      <div v-if="errorGeneral" class="mb-6 flex items-start gap-2 rounded-xl border border-red-300 bg-red-50 px-4 py-3 text-sm font-medium text-red-800" role="alert">
        <svg class="mt-0.5 h-4 w-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
        <span>{{ errorGeneral }}</span>
      </div>

      <form novalidate class="space-y-5" @submit.prevent="procesarLogin">
        <CampoAuth
          id="login-email"
          v-model="formulario.email"
          label="Correo electrónico"
          type="email"
          autocomplete="email"
          placeholder="nombre@correo.com"
          :error="errores.email"
          @update:model-value="limpiarError('email')"
        />
        <CampoAuth
          id="login-password"
          v-model="formulario.password"
          label="Contraseña"
          type="password"
          autocomplete="current-password"
          :error="errores.password"
          @update:model-value="limpiarError('password')"
        />

        <button
          type="submit"
          :disabled="cargando"
          class="flex w-full items-center justify-center rounded-xl bg-emerald-700 px-4 py-3.5 text-base font-bold text-white outline-none transition-colors hover:bg-emerald-800 focus-visible:ring-2 focus-visible:ring-emerald-700 focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-70"
        >
          <svg v-if="cargando" class="mr-3 h-5 w-5 motion-safe:animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" aria-hidden="true">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ cargando ? 'Verificando…' : 'Iniciar sesión' }}
        </button>
      </form>

      <p class="mt-8 text-center text-sm text-gray-700">
        ¿Aún no tienes cuenta?
        <router-link to="/auth/signup" class="font-bold text-teal-700 underline-offset-4 hover:underline focus-visible:outline-2 focus-visible:outline-teal-700">Crear cuenta</router-link>
      </p>
    </div>
  </AuthLayout>
</template>
