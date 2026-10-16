<script setup>
import { ref } from 'vue'
import clienteAxios from '@/api/axios'
import AuthLayout from '@/components/auth/AuthLayout.vue'

const cargando = ref(false)
const mostrarPassword = ref(false)
const errorCredenciales = ref('')

const formulario = ref({
  email: '',
  password: '',
})

const procesarLogin = async () => {
  if (cargando.value) return

  cargando.value = true
  errorCredenciales.value = ''

  try {
    const response = await clienteAxios.post('api/login/', {
      email: formulario.value.email.trim(),
      password: formulario.value.password,
    })

    localStorage.setItem('token', response.data.access)
    localStorage.setItem('refresh_token', response.data.refresh)
    localStorage.setItem('nombre', response.data.usuario.nombre)
    localStorage.setItem('apellido', response.data.usuario.apellido)
    localStorage.setItem('nombre_usuario', response.data.usuario.username)
    localStorage.setItem('nombre_empresa', response.data.usuario.nombre_empresa)
    localStorage.setItem('nombre_agencia', response.data.usuario.nombre_agencia)
    localStorage.setItem('rol', response.data.usuario.group)

    window.location.assign('/')
  } catch (error) {
    errorCredenciales.value = error.response
      ? 'El correo o la contraseña no son correctos. Revisa los datos e inténtalo de nuevo.'
      : 'No pudimos conectar con el servicio. Comprueba tu conexión e inténtalo de nuevo.'
  } finally {
    cargando.value = false
  }
}
</script>

<template>
  <AuthLayout>
    <header class="auth-heading">
      <router-link to="/" class="back-link">
        <svg aria-hidden="true" viewBox="0 0 24 24"><path d="m15 18-6-6 6-6" /></svg>
        Volver al inicio
      </router-link>
      <h1>Inicia sesión</h1>
      <p>Accede a tu cuenta para continuar en Amazonia Viva.</p>
    </header>

    <div v-if="errorCredenciales" id="login-error" class="form-alert" role="alert" aria-live="polite">
      <svg aria-hidden="true" viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="9" />
        <path d="M12 7v6m0 4h.01" />
      </svg>
      <span>{{ errorCredenciales }}</span>
    </div>

    <form class="auth-form" @submit.prevent="procesarLogin">
      <div class="field-group">
        <label for="login-email">Correo electrónico</label>
        <input
          id="login-email"
          v-model="formulario.email"
          type="email"
          name="email"
          autocomplete="email"
          inputmode="email"
          placeholder="nombre@correo.com"
          :aria-describedby="errorCredenciales ? 'login-error' : undefined"
          required
        />
      </div>

      <div class="field-group">
        <label for="login-password">Contraseña</label>
        <div class="password-field">
          <input
            id="login-password"
            v-model="formulario.password"
            :type="mostrarPassword ? 'text' : 'password'"
            name="password"
            autocomplete="current-password"
            placeholder="Ingresa tu contraseña"
            :aria-describedby="errorCredenciales ? 'login-error' : undefined"
            required
          />
          <button
            type="button"
            class="password-toggle"
            :aria-label="mostrarPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'"
            :aria-pressed="mostrarPassword"
            @click="mostrarPassword = !mostrarPassword"
          >
            {{ mostrarPassword ? 'Ocultar' : 'Mostrar' }}
          </button>
        </div>
      </div>

      <button type="submit" class="primary-action" :disabled="cargando">
        <svg v-if="cargando" class="spinner" aria-hidden="true" viewBox="0 0 24 24">
          <circle cx="12" cy="12" r="9" />
          <path d="M21 12a9 9 0 0 0-9-9" />
        </svg>
        {{ cargando ? 'Ingresando…' : 'Iniciar sesión' }}
      </button>
    </form>

    <p class="auth-switch">
      ¿Aún no tienes una cuenta?
      <router-link to="/auth/signup">Crear una cuenta</router-link>
    </p>
  </AuthLayout>
</template>

<style scoped>
.auth-heading { margin-bottom: 30px; }
.back-link { display: inline-flex; align-items: center; gap: 4px; margin-bottom: 32px; color: #47604e; font-size: .88rem; font-weight: 700; text-decoration: none; }
.back-link:hover { color: #17652d; text-decoration: underline; text-underline-offset: 4px; }
.back-link:focus-visible, .auth-switch a:focus-visible { border-radius: 4px; outline: 3px solid rgba(45, 141, 65, .3); outline-offset: 3px; }
.back-link svg { width: 18px; height: 18px; fill: none; stroke: currentColor; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
.auth-heading h1 { margin: 0 0 10px; color: #13271a; font-size: clamp(2rem, 4vw, 2.65rem); font-weight: 800; line-height: 1.08; letter-spacing: -.035em; }
.auth-heading p { margin: 0; color: #5a685e; font-size: .98rem; line-height: 1.6; }
.auth-form { display: grid; gap: 20px; }
.field-group { display: grid; gap: 8px; }
.field-group label { color: #233e2a; font-size: .88rem; font-weight: 750; }
.field-group input { width: 100%; min-height: 50px; border: 1px solid #cbd8ce; border-radius: 12px; background: #fbfcfb; padding: 0 14px; color: #17221a; font-size: 1rem; outline: none; transition: border-color 160ms ease, box-shadow 160ms ease, background-color 160ms ease; }
.field-group input::placeholder { color: #79867d; }
.field-group input:hover { border-color: #9fb3a3; }
.field-group input:focus { border-color: #2d8d41; background: #fff; box-shadow: 0 0 0 4px rgba(45, 141, 65, .13); }
.password-field { position: relative; }
.password-field input { padding-right: 84px; }
.password-toggle { position: absolute; top: 50%; right: 7px; min-height: 36px; transform: translateY(-50%); border: 0; border-radius: 8px; background: transparent; padding: 0 9px; color: #246a35; font-size: .78rem; font-weight: 800; cursor: pointer; }
.password-toggle:hover { background: #edf6ef; }
.password-toggle:focus-visible, .primary-action:focus-visible { outline: 3px solid rgba(45, 141, 65, .32); outline-offset: 3px; }
.primary-action { min-height: 52px; display: inline-flex; align-items: center; justify-content: center; gap: 10px; margin-top: 8px; border: 0; border-radius: 12px; background: #17652d; padding: 0 20px; color: #fff; font-size: .96rem; font-weight: 800; cursor: pointer; transition: background-color 160ms ease, transform 160ms ease; }
.primary-action:hover:not(:disabled) { background: #104d22; transform: translateY(-1px); }
.primary-action:disabled { cursor: wait; opacity: .72; }
.spinner { width: 20px; height: 20px; animation: spin 750ms linear infinite; fill: none; stroke: currentColor; stroke-width: 2.5; stroke-linecap: round; opacity: .9; }
.spinner circle { opacity: .25; }
.form-alert { display: flex; align-items: flex-start; gap: 10px; margin-bottom: 22px; border: 1px solid #efc1bc; border-radius: 12px; background: #fff4f2; padding: 12px 14px; color: #8b2921; font-size: .88rem; line-height: 1.45; }
.form-alert svg { flex: 0 0 auto; width: 20px; height: 20px; fill: none; stroke: currentColor; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
.auth-switch { margin: 28px 0 0; color: #5a685e; font-size: .9rem; text-align: center; }
.auth-switch a { margin-left: 4px; color: #17652d; font-weight: 800; text-decoration: none; }
.auth-switch a:hover { text-decoration: underline; text-underline-offset: 4px; }
@keyframes spin { to { transform: rotate(360deg); } }
@media (prefers-reduced-motion: reduce) { *, *::before, *::after { transition-duration: .01ms !important; animation-duration: .01ms !important; animation-iteration-count: 1 !important; } }
</style>
