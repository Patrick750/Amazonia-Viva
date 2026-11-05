<script setup>
import { computed, nextTick, ref } from 'vue'
import clienteAxios from '@/api/axios'
import AuthLayout from '@/components/auth/AuthLayout.vue'

const roles = [
  { id: 'turista', nombre: 'Turista', descripcion: 'Quiero descubrir y reservar experiencias.' },
  { id: 'agencia', nombre: 'Agencia', descripcion: 'Quiero crear y gestionar paquetes turísticos.' },
  { id: 'proveedor', nombre: 'Proveedor', descripcion: 'Quiero ofrecer productos y servicios.' },
]

const tabActiva = ref('turista')
const cargando = ref(false)
const mostrarPassword = ref(false)
const mostrarConfirmacion = ref(false)
const errorGeneral = ref('')

const formulario = ref({
  first_name: '',
  last_name: '',
  username: '',
  fecha_nacimiento: '',
  numero_identidad: '',
  email: '',
  password: '',
  confirmPassword: '',
  nombre_agencia: '',
  ubicacion: '',
  numero_telefonico: '',
  nombre_empresa: '',
  group: '',
})

const MensajeErrorContraseña = ref('')
const MensajeErrorTelefono = ref('')
const MensejeErrorEmail = ref('')
const MensejeErrorUsername = ref('')
const MensajeErrorIdentidad = ref('')

const rolActual = computed(() => roles.find((rol) => rol.id === tabActiva.value))
const nombreOrganizacion = computed({
  get: () => tabActiva.value === 'agencia'
    ? formulario.value.nombre_agencia
    : formulario.value.nombre_empresa,
  set: (valor) => {
    if (tabActiva.value === 'agencia') formulario.value.nombre_agencia = valor
    else formulario.value.nombre_empresa = valor
  },
})

const limpiarErrores = () => {
  MensajeErrorContraseña.value = ''
  MensajeErrorTelefono.value = ''
  MensejeErrorEmail.value = ''
  MensejeErrorUsername.value = ''
  MensajeErrorIdentidad.value = ''
  errorGeneral.value = ''
}

const seleccionarRol = (rol) => {
  tabActiva.value = rol
  limpiarErrores()
}

const verificarEmail = async () => {
  const response = await clienteAxios.post('api/verificaremail/', {
    email: formulario.value.email.trim(),
  })
  return response.data.email
}

const verificarUsername = async (username) => {
  const response = await clienteAxios.post('api/verificaremail/', { username })
  return response.data.username
}

const verificarIdentidad = async () => {
  const response = await clienteAxios.post('api/verificaremail/', {
    identidad: formulario.value.numero_identidad.trim(),
  })
  return response.data.identidad
}

const prepararDatos = (rol) => {
  const datos = {
    ...formulario.value,
    email: formulario.value.email.trim(),
    numero_telefonico: formulario.value.numero_telefonico.replace(/\s/g, ''),
  }

  if (rol === 'turista') {
    const nombre = formulario.value.first_name.trim().replace(/\s+/g, '_')
    const apellido = formulario.value.last_name.trim().replace(/\s+/g, '_')
    datos.username = `${nombre}${apellido}_${Date.now()}`.toLowerCase()
    datos.group = 1
  }

  if (rol === 'agencia') {
    datos.nombre_agencia = formulario.value.nombre_agencia.trim().toLowerCase()
    datos.username = datos.nombre_agencia.replace(/\s+/g, '_')
    datos.group = 2
  }

  if (rol === 'proveedor') {
    datos.nombre_empresa = formulario.value.nombre_empresa.trim().toLowerCase()
    datos.username = datos.nombre_empresa.replace(/\s+/g, '_')
    datos.group = 3
  }

  return datos
}

const validarDatos = async (rol, datos) => {
  limpiarErrores()
  const soloNumeros = /^[0-9]+$/
  let valido = true

  if (formulario.value.password.length < 8) {
    MensajeErrorContraseña.value = 'La contraseña debe tener al menos 8 caracteres.'
    valido = false
  } else if (formulario.value.password !== formulario.value.confirmPassword) {
    MensajeErrorContraseña.value = 'Las contraseñas no coinciden.'
    valido = false
  }

  if (rol === 'turista') {
    const identidad = formulario.value.numero_identidad.trim()
    if (!soloNumeros.test(identidad)) {
      MensajeErrorIdentidad.value = 'Ingresa únicamente números.'
      valido = false
    } else if (identidad.length !== 10) {
      MensajeErrorIdentidad.value = 'El documento debe contener exactamente 10 dígitos.'
      valido = false
    }
  }

  if (['agencia', 'proveedor'].includes(rol)) {
    const telefono = datos.numero_telefonico
    if (!soloNumeros.test(telefono) || telefono.length !== 10) {
      MensajeErrorTelefono.value = 'Ingresa un teléfono válido de 10 dígitos.'
      valido = false
    }
  }

  if (!valido) return false

  const comprobaciones = [verificarEmail()]
  if (rol === 'turista') comprobaciones.push(verificarIdentidad())
  if (['agencia', 'proveedor'].includes(rol)) comprobaciones.push(verificarUsername(datos.username))

  const resultados = await Promise.all(comprobaciones)
  if (resultados[0]) {
    MensejeErrorEmail.value = 'Este correo ya está registrado. Puedes iniciar sesión.'
    valido = false
  }
  if (rol === 'turista' && resultados[1]) {
    MensajeErrorIdentidad.value = 'Este documento ya está registrado.'
    valido = false
  }
  if (['agencia', 'proveedor'].includes(rol) && resultados[1]) {
    MensejeErrorUsername.value = 'Este nombre ya está registrado. Intenta con otro.'
    valido = false
  }

  return valido
}

const iniciarSesion = async () => {
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
}

const enfocarPrimerError = async () => {
  await nextTick()
  document.querySelector('[aria-invalid="true"]')?.focus()
}

const registrarCuenta = async () => {
  if (cargando.value) return

  cargando.value = true
  errorGeneral.value = ''
  const rol = tabActiva.value
  const datos = prepararDatos(rol)

  try {
    const esValido = await validarDatos(rol, datos)
    if (!esValido) {
      await enfocarPrimerError()
      return
    }

    const respuesta = await clienteAxios.post(`api/signup/${rol}/`, datos)
    if (!respuesta.data.exito) {
      errorGeneral.value = respuesta.data.mensaje || 'No fue posible crear la cuenta. Revisa los datos e inténtalo de nuevo.'
      return
    }

    await iniciarSesion()
    window.location.assign('/')
  } catch (error) {
    errorGeneral.value = error.response?.data?.mensaje
      || (error.response
        ? 'No fue posible crear la cuenta. Revisa la información e inténtalo de nuevo.'
        : 'No pudimos conectar con el servicio. Comprueba tu conexión e inténtalo de nuevo.')
  } finally {
    cargando.value = false
  }
}
</script>

<template>
  <AuthLayout wide>
    <header class="auth-heading">
      <router-link to="/" class="back-link">
        <svg aria-hidden="true" viewBox="0 0 24 24"><path d="m15 18-6-6 6-6" /></svg>
        Volver al inicio
      </router-link>
      <h1>Crea tu cuenta</h1>
      <p>Selecciona cómo usarás Amazonia Viva y completa tus datos.</p>
    </header>

    <fieldset class="role-selector">
      <legend>¿Cómo quieres usar la plataforma?</legend>
      <div class="role-selector__options">
        <label v-for="rol in roles" :key="rol.id" :class="['role-option', { 'role-option--active': tabActiva === rol.id }]">
          <input
            type="radio"
            name="tipo-cuenta"
            :value="rol.id"
            :checked="tabActiva === rol.id"
            @change="seleccionarRol(rol.id)"
          />
          <span class="role-option__check" aria-hidden="true"></span>
          <span>
            <strong>{{ rol.nombre }}</strong>
            <small>{{ rol.descripcion }}</small>
          </span>
        </label>
      </div>
    </fieldset>

    <div v-if="errorGeneral" id="signup-error" class="form-alert" role="alert" aria-live="polite">
      <svg aria-hidden="true" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9" /><path d="M12 7v6m0 4h.01" /></svg>
      <span>{{ errorGeneral }}</span>
    </div>

    <form class="signup-form" @submit.prevent="registrarCuenta">
      <section class="form-section" aria-labelledby="profile-section-title">
        <div class="section-heading">
          <div>
            <h2 id="profile-section-title">Datos de {{ rolActual.nombre.toLowerCase() }}</h2>
            <p>Los campos marcados con * son obligatorios.</p>
          </div>
        </div>

        <div v-if="tabActiva === 'turista'" class="form-grid">
          <div class="field-group">
            <label for="first-name">Nombres *</label>
            <input id="first-name" v-model="formulario.first_name" type="text" name="given-name" autocomplete="given-name" placeholder="Ej. Laura" required />
          </div>
          <div class="field-group">
            <label for="last-name">Apellidos *</label>
            <input id="last-name" v-model="formulario.last_name" type="text" name="family-name" autocomplete="family-name" placeholder="Ej. Gómez" required />
          </div>
          <div class="field-group">
            <label for="birth-date">Fecha de nacimiento *</label>
            <input id="birth-date" v-model="formulario.fecha_nacimiento" type="date" name="bday" autocomplete="bday" required />
          </div>
          <div class="field-group">
            <label for="identity-number">Número de identidad *</label>
            <input
              id="identity-number"
              v-model="formulario.numero_identidad"
              type="text"
              inputmode="numeric"
              maxlength="10"
              placeholder="10 dígitos"
              :aria-invalid="Boolean(MensajeErrorIdentidad)"
              :aria-describedby="MensajeErrorIdentidad ? 'identity-error' : 'identity-help'"
              required
            />
            <small v-if="!MensajeErrorIdentidad" id="identity-help" class="field-help">Sin puntos ni espacios.</small>
            <small v-else id="identity-error" class="field-error">{{ MensajeErrorIdentidad }}</small>
          </div>
          <div class="field-group form-grid__full">
            <label for="tourist-phone">Teléfono <span>(opcional)</span></label>
            <input id="tourist-phone" v-model="formulario.numero_telefonico" type="tel" name="tel" autocomplete="tel" inputmode="tel" placeholder="Ej. 300 123 4567" />
          </div>
        </div>

        <div v-else class="form-grid">
          <div class="field-group form-grid__full">
            <label :for="tabActiva === 'agencia' ? 'agency-name' : 'company-name'">
              {{ tabActiva === 'agencia' ? 'Nombre de la agencia' : 'Nombre de la empresa' }} *
            </label>
            <input
              :id="tabActiva === 'agencia' ? 'agency-name' : 'company-name'"
              v-model="nombreOrganizacion"
              type="text"
              name="organization"
              autocomplete="organization"
              :placeholder="tabActiva === 'agencia' ? 'Ej. Senderos del Amazonas' : 'Ej. Equipos Selva'"
              :aria-invalid="Boolean(MensejeErrorUsername)"
              :aria-describedby="MensejeErrorUsername ? 'organization-error' : undefined"
              required
            />
            <small v-if="MensejeErrorUsername" id="organization-error" class="field-error">{{ MensejeErrorUsername }}</small>
          </div>
          <div class="field-group form-grid__full">
            <label for="organization-phone">Teléfono *</label>
            <input
              id="organization-phone"
              v-model="formulario.numero_telefonico"
              type="tel"
              name="tel"
              autocomplete="tel"
              inputmode="numeric"
              placeholder="Ej. 300 123 4567"
              :aria-invalid="Boolean(MensajeErrorTelefono)"
              :aria-describedby="MensajeErrorTelefono ? 'phone-error' : 'phone-help'"
              required
            />
            <small v-if="!MensajeErrorTelefono" id="phone-help" class="field-help">Número colombiano de 10 dígitos.</small>
            <small v-else id="phone-error" class="field-error">{{ MensajeErrorTelefono }}</small>
          </div>
        </div>
      </section>

      <section class="form-section" aria-labelledby="access-section-title">
        <div class="section-heading">
          <div>
            <h2 id="access-section-title">Datos de acceso</h2>
            <p>Usarás este correo y contraseña para ingresar.</p>
          </div>
        </div>

        <div class="field-group">
          <label for="signup-email">Correo electrónico *</label>
          <input
            id="signup-email"
            v-model="formulario.email"
            type="email"
            name="email"
            autocomplete="email"
            inputmode="email"
            placeholder="nombre@correo.com"
            :aria-invalid="Boolean(MensejeErrorEmail)"
            :aria-describedby="MensejeErrorEmail ? 'email-error' : undefined"
            required
          />
          <small v-if="MensejeErrorEmail" id="email-error" class="field-error">{{ MensejeErrorEmail }}</small>
        </div>

        <div class="form-grid password-grid">
          <div class="field-group">
            <label for="signup-password">Contraseña *</label>
            <div class="password-field">
              <input
                id="signup-password"
                v-model="formulario.password"
                :type="mostrarPassword ? 'text' : 'password'"
                name="new-password"
                autocomplete="new-password"
                placeholder="Mínimo 8 caracteres"
                :aria-invalid="Boolean(MensajeErrorContraseña)"
                :aria-describedby="MensajeErrorContraseña ? 'password-error' : 'password-help'"
                minlength="8"
                required
              />
              <button type="button" class="password-toggle" :aria-label="mostrarPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'" :aria-pressed="mostrarPassword" @click="mostrarPassword = !mostrarPassword">
                {{ mostrarPassword ? 'Ocultar' : 'Mostrar' }}
              </button>
            </div>
            <small v-if="!MensajeErrorContraseña" id="password-help" class="field-help">Usa al menos 8 caracteres.</small>
          </div>
          <div class="field-group">
            <label for="confirm-password">Confirma la contraseña *</label>
            <div class="password-field">
              <input
                id="confirm-password"
                v-model="formulario.confirmPassword"
                :type="mostrarConfirmacion ? 'text' : 'password'"
                name="confirm-password"
                autocomplete="new-password"
                placeholder="Repite la contraseña"
                :aria-invalid="Boolean(MensajeErrorContraseña)"
                :aria-describedby="MensajeErrorContraseña ? 'password-error' : undefined"
                required
              />
              <button type="button" class="password-toggle" :aria-label="mostrarConfirmacion ? 'Ocultar confirmación' : 'Mostrar confirmación'" :aria-pressed="mostrarConfirmacion" @click="mostrarConfirmacion = !mostrarConfirmacion">
                {{ mostrarConfirmacion ? 'Ocultar' : 'Mostrar' }}
              </button>
            </div>
          </div>
          <small v-if="MensajeErrorContraseña" id="password-error" class="field-error form-grid__full">{{ MensajeErrorContraseña }}</small>
        </div>
      </section>

      <button type="submit" class="primary-action" :disabled="cargando" :aria-describedby="errorGeneral ? 'signup-error' : undefined">
        <svg v-if="cargando" class="spinner" aria-hidden="true" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9" /><path d="M21 12a9 9 0 0 0-9-9" /></svg>
        {{ cargando ? 'Creando cuenta…' : `Crear cuenta de ${rolActual.nombre.toLowerCase()}` }}
      </button>
    </form>

    <p class="auth-switch">
      ¿Ya tienes una cuenta?
      <router-link to="/auth/login">Iniciar sesión</router-link>
    </p>
  </AuthLayout>
</template>

<style scoped>
.auth-heading { margin-bottom: 28px; }
.back-link { display: inline-flex; align-items: center; gap: 4px; margin-bottom: 26px; color: #47604e; font-size: .88rem; font-weight: 700; text-decoration: none; }
.back-link:hover { color: #17652d; text-decoration: underline; text-underline-offset: 4px; }
.back-link:focus-visible, .auth-switch a:focus-visible { border-radius: 4px; outline: 3px solid rgba(45, 141, 65, .3); outline-offset: 3px; }
.back-link svg { width: 18px; height: 18px; fill: none; stroke: currentColor; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
.auth-heading h1 { margin: 0 0 9px; color: #13271a; font-size: clamp(2rem, 4vw, 2.65rem); font-weight: 800; line-height: 1.08; letter-spacing: -.035em; }
.auth-heading p { margin: 0; color: #5a685e; font-size: .96rem; line-height: 1.55; }
.role-selector { margin: 0 0 30px; border: 0; padding: 0; }
.role-selector legend { margin-bottom: 11px; color: #233e2a; font-size: .88rem; font-weight: 800; }
.role-selector__options { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.role-option { position: relative; display: flex; align-items: flex-start; gap: 10px; min-height: 94px; border: 1px solid #d5dfd6; border-radius: 13px; background: #fbfcfb; padding: 13px; cursor: pointer; transition: border-color 160ms ease, background-color 160ms ease, box-shadow 160ms ease; }
.role-option:hover { border-color: #92ae98; }
.role-option--active { border-color: #2d8d41; background: #f0f8f2; box-shadow: 0 0 0 1px #2d8d41; }
.role-option input { position: absolute; width: 1px; height: 1px; overflow: hidden; opacity: 0; }
.role-option:has(input:focus-visible) { outline: 3px solid rgba(45, 141, 65, .3); outline-offset: 3px; }
.role-option__check { flex: 0 0 auto; width: 18px; height: 18px; margin-top: 1px; border: 2px solid #9bad9e; border-radius: 50%; background: #fff; box-shadow: inset 0 0 0 4px #fff; }
.role-option--active .role-option__check { border-color: #2d8d41; background: #2d8d41; }
.role-option strong, .role-option small { display: block; }
.role-option strong { margin-bottom: 4px; color: #203925; font-size: .86rem; }
.role-option small { color: #637268; font-size: .72rem; line-height: 1.35; }
.signup-form { display: grid; gap: 28px; }
.form-section { display: grid; gap: 18px; }
.form-section + .form-section { border-top: 1px solid #e4eae5; padding-top: 26px; }
.section-heading { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; }
.section-heading h2 { margin: 0 0 4px; color: #1b3221; font-size: 1.05rem; font-weight: 800; }
.section-heading p { margin: 0; color: #6b796f; font-size: .78rem; }
.form-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; }
.form-grid__full { grid-column: 1 / -1; }
.field-group { display: grid; align-content: start; gap: 7px; }
.field-group label { color: #29432f; font-size: .83rem; font-weight: 750; }
.field-group label span { color: #738078; font-weight: 500; }
.field-group input { width: 100%; min-height: 48px; border: 1px solid #cbd8ce; border-radius: 11px; background: #fbfcfb; padding: 0 13px; color: #17221a; font-size: .93rem; outline: none; transition: border-color 160ms ease, box-shadow 160ms ease, background-color 160ms ease; }
.field-group input::placeholder { color: #7d8980; }
.field-group input:hover { border-color: #9fb3a3; }
.field-group input:focus { border-color: #2d8d41; background: #fff; box-shadow: 0 0 0 4px rgba(45, 141, 65, .13); }
.field-group input[aria-invalid="true"] { border-color: #c75449; background: #fffafa; }
.field-group input[aria-invalid="true"]:focus { box-shadow: 0 0 0 4px rgba(185, 65, 54, .12); }
.field-help, .field-error { font-size: .74rem; line-height: 1.4; }
.field-help { color: #6b796f; }
.field-error { color: #a33027; font-weight: 650; }
.password-field { position: relative; }
.password-field input { padding-right: 82px; }
.password-toggle { position: absolute; top: 50%; right: 6px; min-height: 34px; transform: translateY(-50%); border: 0; border-radius: 8px; background: transparent; padding: 0 8px; color: #246a35; font-size: .75rem; font-weight: 800; cursor: pointer; }
.password-toggle:hover { background: #edf6ef; }
.password-toggle:focus-visible, .primary-action:focus-visible { outline: 3px solid rgba(45, 141, 65, .32); outline-offset: 3px; }
.primary-action { min-height: 52px; display: inline-flex; align-items: center; justify-content: center; gap: 10px; border: 0; border-radius: 12px; background: #17652d; padding: 0 20px; color: #fff; font-size: .95rem; font-weight: 800; cursor: pointer; transition: background-color 160ms ease, transform 160ms ease; }
.primary-action:hover:not(:disabled) { background: #104d22; transform: translateY(-1px); }
.primary-action:disabled { cursor: wait; opacity: .72; }
.spinner { width: 20px; height: 20px; animation: spin 750ms linear infinite; fill: none; stroke: currentColor; stroke-width: 2.5; stroke-linecap: round; }
.spinner circle { opacity: .25; }
.form-alert { display: flex; align-items: flex-start; gap: 10px; margin-bottom: 24px; border: 1px solid #efc1bc; border-radius: 12px; background: #fff4f2; padding: 12px 14px; color: #8b2921; font-size: .86rem; line-height: 1.45; }
.form-alert svg { flex: 0 0 auto; width: 20px; height: 20px; fill: none; stroke: currentColor; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
.auth-switch { margin: 26px 0 0; color: #5a685e; font-size: .88rem; text-align: center; }
.auth-switch a { margin-left: 4px; color: #17652d; font-weight: 800; text-decoration: none; }
.auth-switch a:hover { text-decoration: underline; text-underline-offset: 4px; }
@keyframes spin { to { transform: rotate(360deg); } }
@media (max-width: 650px) { .role-selector__options, .form-grid { grid-template-columns: 1fr; } .role-option { min-height: auto; } .form-grid__full { grid-column: auto; } .password-grid { gap: 14px; } }
@media (prefers-reduced-motion: reduce) { *, *::before, *::after { transition-duration: .01ms !important; animation-duration: .01ms !important; animation-iteration-count: 1 !important; } }
</style>
