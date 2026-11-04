<template>
  <div class="min-h-screen bg-slate-50 font-sans">

    <!-- ═══ HEADER ═══ -->
    <div class="bg-gradient-to-r from-emerald-900 to-emerald-700 pt-10 pb-20 px-4">
      <div class="max-w-2xl mx-auto flex flex-col sm:flex-row items-center gap-6">

        <!-- Foto de perfil: tocarla la abre en grande; el botón de cámara permite agregarla, cambiarla o eliminarla -->
        <div class="relative shrink-0">
          <div class="relative w-20 h-20 rounded-full bg-white/20 border-2 border-white/40 flex items-center justify-center shadow-xl overflow-hidden">
            <img v-if="perfil.foto_url" :src="perfil.foto_url" alt="Foto de perfil" class="w-full h-full object-cover" />
            <span v-else class="text-2xl font-bold text-white select-none">{{ iniciales }}</span>
          </div>
          <ControlesImagen tipo="perfil" :url="perfil.foto_url" editable redondeo="rounded-full" posicion-boton="-bottom-1 -right-1" @cambio="perfil.foto_url = $event" />
        </div>

        <div class="text-center sm:text-left">
          <h1 class="text-2xl font-bold text-white">{{ perfil.first_name }} {{ perfil.last_name }}</h1>
          <p class="text-emerald-200 text-sm mt-1">{{ perfil.email }}</p>
          <span class="inline-flex items-center gap-1 mt-2 bg-emerald-600/60 border border-emerald-400/40 text-emerald-100 text-xs px-2.5 py-1 rounded-full">
            <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
            Viajero Verificado
          </span>
        </div>
      </div>
    </div>

    <!-- ═══ LAYOUT CON SIDEBAR ═══ -->
    <div class="max-w-5xl mx-auto px-4 -mt-10 pb-16 flex flex-col lg:flex-row gap-8">
      
      <!-- Menú Lateral -->
      <MenuLateralPerfil v-model="currentView" />

      <!-- CONTENIDO DINÁMICO -->
      <div class="flex-1 min-w-0">
        <transition name="fade" mode="out-in">
          
          <!-- ── INFORMACIÓN CUENTA ── -->
          <div v-if="currentView === 'info'" key="info" class="bg-white rounded-3xl shadow-sm border border-slate-200 overflow-hidden">
            <div class="px-6 sm:px-8 pt-6 pb-4 border-b border-slate-100">
              <h2 class="text-lg font-extrabold text-slate-800 flex items-center gap-2">
                <svg class="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
                Configuración de cuenta
              </h2>
              <p class="text-slate-500 text-sm mt-0.5">Gestiona tus datos personales y preferencias de seguridad.</p>
            </div>

            <form @submit.prevent="guardar" class="p-6 sm:p-8 space-y-6">
              <!-- Nombre + Apellido -->
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
                <div>
                  <label class="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-2 ml-1">Nombre</label>
                  <input id="first-name" v-model="form.first_name" type="text"
                    class="w-full rounded-2xl border border-slate-200 bg-slate-50/50 px-4 py-3 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all font-medium"
                    placeholder="Tu nombre" />
                </div>
                <div>
                  <label class="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-2 ml-1">Apellido</label>
                  <input id="last-name" v-model="form.last_name" type="text"
                    class="w-full rounded-2xl border border-slate-200 bg-slate-50/50 px-4 py-3 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all font-medium"
                    placeholder="Tu apellido" />
                </div>
              </div>

              <!-- Email (bloqueado) -->
              <div>
                <div class="flex items-center gap-2 mb-2 ml-1">
                  <label class="text-xs font-bold text-slate-500 uppercase tracking-widest">Correo electrónico</label>
                  <span class="text-[10px] bg-slate-100 text-slate-400 px-1.5 py-0.5 rounded uppercase font-bold tracking-tighter">Privado</span>
                </div>
                <div class="relative group">
                  <input id="email" :value="perfil.email" type="email" disabled
                    class="w-full rounded-2xl border border-slate-200 bg-slate-100/50 px-4 py-3 text-sm text-slate-400 cursor-not-allowed font-medium" />
                  <div class="absolute right-4 top-1/2 -translate-y-1/2">
                    <svg class="w-4 h-4 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
                  </div>
                </div>
              </div>

              <!-- Fecha nacimiento -->
              <div>
                <label class="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-2 ml-1">Fecha de nacimiento</label>
                <input id="fecha-nacimiento" v-model="form.fecha_nacimiento" type="date"
                  class="w-full rounded-2xl border border-slate-200 bg-slate-50/50 px-4 py-3 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all font-medium" />
              </div>

              <!-- Número de identidad -->
              <div>
                <label class="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-2 ml-1">Número de identidad</label>
                <div class="relative">
                  <template v-if="perfil.numero_identidad">
                    <input id="campo-identidad" :value="perfil.numero_identidad" type="text" disabled
                      class="w-full rounded-2xl border border-slate-200 bg-slate-100/50 px-4 py-3 text-sm text-slate-400 cursor-not-allowed pr-10 font-medium" />
                    <svg class="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
                  </template>
                  <template v-else>
                    <input id="edit-identidad" v-model="form.numero_identidad" type="text"
                      placeholder="Ingresa tu número de identidad"
                      class="w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all font-medium shadow-inner" />
                  </template>
                </div>
                <p v-if="perfil.numero_identidad" class="text-[11px] text-slate-400 mt-2 font-medium">Este dato ha sido verificado y no puede cambiarse. Si hay un error, contacta a soporte.</p>
                <p v-else class="text-[11px] text-emerald-600 mt-2 font-bold animate-pulse">✓ Este dato se bloqueará una vez sea guardado.</p>
              </div>

              <!-- Teléfono -->
              <div>
                <label class="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-2 ml-1">Número de teléfono</label>
                <input id="numero-telefono" v-model="form.numero_telefonico" type="tel"
                  class="w-full rounded-2xl border border-slate-200 bg-slate-50/50 px-4 py-3 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all font-medium"
                  placeholder="Ej: 300 123 4567" />
              </div>

              <!-- Botón guardar -->
              <div class="pt-4 flex items-center gap-4">
                <button id="btn-guardar-turista" type="submit" :disabled="isLoading"
                  class="inline-flex items-center gap-2 px-8 py-3 bg-slate-900 border border-slate-800 hover:bg-slate-800 text-white text-sm font-bold rounded-2xl shadow-xl shadow-slate-900/10 transition-all duration-300 disabled:opacity-60 disabled:cursor-not-allowed hover:-translate-y-0.5 active:translate-y-0">
                  <svg v-if="isLoading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/></svg>
                  <span>{{ isLoading ? 'Guardando...' : 'Aplicar cambios' }}</span>
                </button>
                <transition name="fade">
                  <div v-if="successMsg" class="flex items-center gap-2 text-emerald-600 font-bold text-sm">
                    <div class="w-2 h-2 bg-emerald-500 rounded-full animate-ping"></div>
                    ¡Actualizado!
                  </div>
                  <p v-else-if="errorMsg" class="text-red-500 text-sm font-bold">{{ errorMsg }}</p>
                </transition>
              </div>
            </form>
          </div>

          <!-- ── VISTA PERFIL (PREVIEW SOCIAL COMMERCE) ── -->
          <VistaPerfilPublico 
            v-else 
            key="view" 
            :perfil="perfil" 
            rol-label="Turista" 
            @imagen-cambiada="({ tipo, url }) => perfil[tipo === 'perfil' ? 'foto_url' : 'foto_portada_url'] = url"
          />
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import clienteAxios from '@/api/axios.js'
import MenuLateralPerfil from '@/components/perfil/MenuLateralPerfil.vue'
import VistaPerfilPublico from '@/components/perfil/VistaPerfilPublico.vue'
import ControlesImagen from '@/components/perfil/ControlesImagen.vue'

const currentView = ref('info')
const isLoading  = ref(false)
const successMsg = ref(false)
const errorMsg   = ref('')

const perfil = reactive({
  first_name: '', last_name: '',
  email: '', fecha_nacimiento: '',
  numero_identidad: '', foto_url: null, foto_portada_url: null,
  numero_telefonico: '',
})

const form = reactive({
  first_name: '',
  last_name: '',
  fecha_nacimiento: '',
  numero_identidad: '',
  numero_telefonico: '',
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
    form.numero_telefonico = data.numero_telefonico || ''
  } catch (err) {
    console.error('Error cargando perfil:', err)
  }
})

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
      numero_telefonico: form.numero_telefonico,
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
