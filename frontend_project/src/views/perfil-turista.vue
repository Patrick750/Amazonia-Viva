<template>
  <div class="min-h-screen bg-slate-50 font-sans">

    <!-- ═══ HEADER ═══ -->
    <div class="bg-gradient-to-r from-emerald-900 to-emerald-700 pt-10 pb-20 px-4">
      <div class="max-w-2xl mx-auto flex flex-col sm:flex-row items-center gap-6">

        <!-- Avatar clickeable para subir foto -->
        <div class="relative shrink-0 group">
          <div
            @click="triggerFotoInput"
            class="w-20 h-20 rounded-full bg-white/20 border-2 border-white/40 flex items-center justify-center shadow-xl cursor-pointer overflow-hidden"
            title="Haz clic para cambiar tu foto de perfil"
          >
            <!-- Spinner durante upload -->
            <div v-if="subiendoFoto" class="absolute inset-0 bg-black/50 rounded-full flex items-center justify-center z-10">
              <svg class="w-7 h-7 text-white animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
              </svg>
            </div>
            <!-- Overlay de edición -->
            <div class="absolute inset-0 bg-black/40 rounded-full flex flex-col items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity z-10 gap-1">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
              <span class="text-white text-[10px] font-semibold">Cambiar</span>
            </div>
            <!-- Foto o iniciales -->
            <img v-if="fotoPreview || perfil.foto_url" :src="fotoPreview || perfil.foto_url" alt="Foto de perfil" class="w-full h-full object-cover" />
            <span v-else class="text-2xl font-bold text-white select-none">{{ iniciales }}</span>
          </div>

          <!-- Input file oculto -->
          <input
            ref="fotoInputRef"
            id="input-foto-turista"
            type="file"
            accept="image/*"
            class="hidden"
            @change="onFotoSeleccionada"
          />
        </div>

        <div class="text-center sm:text-left">
          <h1 class="text-2xl font-bold text-white">{{ perfil.first_name }} {{ perfil.last_name }}</h1>
          <p class="text-emerald-200 text-sm mt-1">{{ perfil.email }}</p>
          <span class="inline-flex items-center gap-1 mt-2 bg-emerald-600/60 border border-emerald-400/40 text-emerald-100 text-xs px-2.5 py-1 rounded-full">
            <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
            Viajero Verificado
          </span>
          <!-- Mensajes de foto -->
          <transition name="fade">
            <p v-if="fotoMsg" class="text-emerald-300 text-xs mt-2 font-medium">✓ {{ fotoMsg }}</p>
            <p v-else-if="fotoError" class="text-red-300 text-xs mt-2">{{ fotoError }}</p>
          </transition>
        </div>
      </div>
    </div>

    <!-- ═══ CARD PRINCIPAL ═══ -->
    <div class="max-w-2xl mx-auto px-4 -mt-10 pb-16">
      <div class="bg-white rounded-2xl shadow-md border border-slate-200 overflow-hidden">

        <div class="px-6 sm:px-8 pt-6 pb-4 border-b border-slate-100">
          <h2 class="text-base font-semibold text-slate-800 flex items-center gap-2">
            <svg class="w-4 h-4 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
            Mis datos personales
          </h2>
          <p class="text-slate-500 text-sm mt-0.5">Mantén tu información actualizada para una mejor experiencia.</p>
        </div>

        <form @submit.prevent="guardar" class="p-6 sm:p-8 space-y-5">

          <!-- Nombre + Apellido -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1.5">Nombre</label>
              <input id="first-name" v-model="form.first_name" type="text"
                class="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition"
                placeholder="Tu nombre" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 mb-1.5">Apellido</label>
              <input id="last-name" v-model="form.last_name" type="text"
                class="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition"
                placeholder="Tu apellido" />
            </div>
          </div>

          <!-- Email (bloqueado) -->
          <div>
            <div class="flex items-center gap-2 mb-1.5">
              <label class="text-sm font-medium text-slate-700">Correo electrónico</label>
              <svg class="w-3.5 h-3.5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
            </div>
            <input id="email" :value="perfil.email" type="email" disabled
              class="w-full rounded-lg border border-slate-200 bg-slate-100 px-4 py-2.5 text-sm text-slate-400 cursor-not-allowed" />
            <p class="text-xs text-slate-400 mt-1">El correo está vinculado a tu cuenta y no puede modificarse aquí.</p>
          </div>

          <!-- Fecha nacimiento -->
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1.5">Fecha de nacimiento</label>
            <input id="fecha-nacimiento" v-model="form.fecha_nacimiento" type="date"
              class="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition" />
          </div>

          <!-- Número de identidad -->
          <div>
            <div class="flex items-center gap-2 mb-1.5">
              <label class="text-sm font-medium text-slate-700">Número de identidad</label>
              <svg class="w-3.5 h-3.5" :class="perfil.numero_identidad ? 'text-amber-500' : 'text-emerald-500'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path v-if="perfil.numero_identidad" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
              </svg>
            </div>
            <div class="relative">
              <!-- Solo lectura si ya existe -->
              <template v-if="perfil.numero_identidad">
                <input id="campo-identidad" :value="perfil.numero_identidad" type="text" disabled
                  class="w-full rounded-lg border border-slate-200 bg-slate-100 px-4 py-2.5 text-sm text-slate-400 cursor-not-allowed pr-10" />
                <svg class="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
              </template>
              <!-- Editable si está vacío -->
              <template v-else>
                <input id="edit-identidad" v-model="form.numero_identidad" type="text"
                  placeholder="Ingresa tu número de identidad"
                  class="w-full rounded-lg border border-slate-300 px-4 py-2.5 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500 transition" />
              </template>
            </div>
            <p v-if="perfil.numero_identidad" class="text-xs text-slate-400 mt-1">Dato legal registrado. Contáctanos en soporte@amazoniaviva.co para corregirlo.</p>
            <p v-else class="text-xs text-emerald-600 mt-1">Este dato se bloqueará una vez guardado.</p>
          </div>

          <!-- Botón guardar -->
          <div class="pt-2 flex items-center gap-4">
            <button id="btn-guardar-turista" type="submit" :disabled="isLoading"
              class="inline-flex items-center gap-2 px-6 py-2.5 bg-emerald-700 hover:bg-emerald-600 text-white text-sm font-semibold rounded-lg shadow transition-all duration-200 disabled:opacity-60 disabled:cursor-not-allowed">
              <svg v-if="isLoading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/></svg>
              <span>{{ isLoading ? 'Guardando...' : 'Guardar cambios' }}</span>
            </button>
            <transition name="fade">
              <p v-if="successMsg" class="text-emerald-600 text-sm font-medium flex items-center gap-1">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
                ¡Datos actualizados!
              </p>
              <p v-else-if="errorMsg" class="text-red-500 text-sm">{{ errorMsg }}</p>
            </transition>
          </div>

        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import clienteAxios from '@/api/axios.js'

const isLoading  = ref(false)
const successMsg = ref(false)
const errorMsg   = ref('')

// Foto
const fotoInputRef = ref(null)
const fotoPreview  = ref(null)
const subiendoFoto = ref(false)
const fotoMsg      = ref('')
const fotoError    = ref('')

const perfil = reactive({
  first_name: '', last_name: '',
  email: '', fecha_nacimiento: '',
  numero_identidad: '', foto_url: null,
})

const form = reactive({
  first_name: '',
  last_name: '',
  fecha_nacimiento: '',
  numero_identidad: '',
})

const iniciales = computed(() => {
  const n = (perfil.first_name || '').charAt(0)
  const a = (perfil.last_name  || '').charAt(0)
  return (n + a).toUpperCase() || '?'
})

onMounted(async () => {
  try {
    const { data } = await clienteAxios.get('api/perfil/')
    Object.assign(perfil, data)
    form.first_name       = data.first_name || ''
    form.last_name        = data.last_name  || ''
    form.fecha_nacimiento = data.fecha_nacimiento || ''
    form.numero_identidad = data.numero_identidad || ''
  } catch (err) {
    console.error('Error cargando perfil:', err)
  }
})

// ─── Upload de foto ────────────────────────────────────────
function triggerFotoInput() {
  fotoInputRef.value?.click()
}

async function onFotoSeleccionada(event) {
  const archivo = event.target.files[0]
  if (!archivo) return

  if (!archivo.type.startsWith('image/')) {
    fotoError.value = 'Solo se permiten archivos de imagen.'
    setTimeout(() => { fotoError.value = '' }, 4000)
    return
  }
  if (archivo.size > 5 * 1024 * 1024) {
    fotoError.value = 'La imagen no puede superar los 5 MB.'
    setTimeout(() => { fotoError.value = '' }, 4000)
    return
  }

  fotoPreview.value = URL.createObjectURL(archivo)
  subiendoFoto.value = true
  fotoMsg.value = ''
  fotoError.value = ''

  try {
    const fd = new FormData()
    fd.append('foto', archivo)
    const { data } = await clienteAxios.post('api/perfil/foto/', fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    perfil.foto_url = data.foto_url
    // ── Actualizar header en tiempo real ──
    localStorage.setItem('foto_url', data.foto_url)
    window.dispatchEvent(new CustomEvent('perfil:foto-actualizada', {
      detail: { foto_url: data.foto_url }
    }))
    fotoMsg.value = 'Foto actualizada correctamente'
    setTimeout(() => { fotoMsg.value = '' }, 4000)
  } catch (err) {
    console.error('Error subiendo foto:', err)
    fotoPreview.value = null
    fotoError.value = 'Error al subir la imagen. Inténtalo de nuevo.'
    setTimeout(() => { fotoError.value = '' }, 5000)
  } finally {
    subiendoFoto.value = false
    event.target.value = ''
  }
}

// ─── Guardar datos ─────────────────────────────────────────
async function guardar() {
  isLoading.value = true
  successMsg.value = false
  errorMsg.value = ''
  try {
    const { data } = await clienteAxios.patch('api/perfil/', {
      first_name: form.first_name,
      last_name: form.last_name,
      fecha_nacimiento: form.fecha_nacimiento,
      numero_identidad: form.numero_identidad,
    })
    Object.assign(perfil, data)
    // ── Actualizar header en tiempo real ──
    localStorage.setItem('nombre', form.first_name)
    window.dispatchEvent(new CustomEvent('perfil:nombre-actualizado', {
      detail: { nombre: form.first_name, rol: 'turista' }
    }))
    successMsg.value = true
    setTimeout(() => { successMsg.value = false }, 3000)
  } catch (err) {
    console.error('Error guardando perfil:', err)
    errorMsg.value = 'Ocurrió un error. Inténtalo de nuevo.'
    setTimeout(() => { errorMsg.value = '' }, 4000)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.18s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
