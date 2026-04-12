<template>
  <div class="min-h-screen bg-slate-50 font-sans">

    <!-- ═══ HEADER-PERFIL ═══ -->
    <div class="bg-gradient-to-r from-emerald-900 to-emerald-700 pt-10 pb-20 px-4">
      <div class="max-w-4xl mx-auto flex flex-col sm:flex-row items-center gap-6">

        <!-- Avatar / Logo — clickeable para subir foto -->
        <div class="relative shrink-0 group">
          <div
            @click="triggerFotoInput"
            class="w-24 h-24 rounded-2xl bg-white/20 border-2 border-white/40 flex items-center justify-center overflow-hidden shadow-xl cursor-pointer"
            title="Haz clic para cambiar el logotipo"
          >
            <!-- Mientras sube: spinner -->
            <div v-if="subiendoFoto" class="absolute inset-0 bg-black/50 rounded-2xl flex items-center justify-center z-10">
              <svg class="w-8 h-8 text-white animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
              </svg>
            </div>
            <!-- Overlay de edición al hover -->
            <div class="absolute inset-0 bg-black/40 rounded-2xl flex flex-col items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity z-10 gap-1">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
              <span class="text-white text-[10px] font-semibold">Cambiar</span>
            </div>
            <!-- Imagen o iniciales -->
            <img v-if="fotoPreview || perfil.foto_url" :src="fotoPreview || perfil.foto_url" alt="Logo empresa" class="w-full h-full object-cover" />
            <span v-else class="text-3xl font-bold text-white select-none">{{ iniciales }}</span>
          </div>

          <!-- Badge de rol -->
          <span class="absolute -bottom-2 -right-2 bg-amber-400 text-amber-900 text-xs font-bold px-2 py-0.5 rounded-full shadow">{{ rolLabel }}</span>

          <!-- Input file oculto -->
          <input
            ref="fotoInputRef"
            id="input-foto-perfil"
            type="file"
            accept="image/*"
            class="hidden"
            @change="onFotoSeleccionada"
          />
        </div>

        <!-- Nombre empresa + email -->
        <div class="text-center sm:text-left">
          <h1 class="text-2xl font-bold text-white">{{ nombreEmpresa }}</h1>
          <p class="text-emerald-200 text-sm mt-1">{{ perfil.email }}</p>
          <div class="flex items-center justify-center sm:justify-start gap-2 mt-2">
            <span class="inline-flex items-center gap-1 bg-emerald-600/60 border border-emerald-400/40 text-emerald-100 text-xs px-2.5 py-1 rounded-full">
              <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
              Perfil verificado
            </span>
          </div>
          <!-- Mensaje de foto subida -->
          <transition name="fade">
            <p v-if="fotoMsg" class="text-emerald-300 text-xs mt-2 font-medium">✓ {{ fotoMsg }}</p>
            <p v-else-if="fotoError" class="text-red-300 text-xs mt-2">{{ fotoError }}</p>
          </transition>
        </div>
      </div>
    </div>

    <!-- ═══ LAYOUT CON SIDEBAR ═══ -->
    <div class="max-w-6xl mx-auto px-4 -mt-10 pb-16 flex flex-col lg:flex-row gap-8">
      
      <!-- Menú Lateral -->
      <MenuLateralPerfil v-model="currentView" />

      <!-- CONTENIDO DINÁMICO -->
      <div class="flex-1">
        <transition name="fade" mode="out-in">
          
          <!-- ── INFORMACIÓN CUENTA (Consolida las tabs existentes) ── -->
          <div v-if="currentView === 'info'" key="info" class="bg-white rounded-3xl shadow-sm border border-slate-200 overflow-hidden">
            <!-- Tab Nav -->
            <div class="flex border-b border-slate-100 bg-slate-50/50">
              <button
                @click="activeTab = 'basica'"
                :class="[
                  'flex-1 py-4 px-6 text-xs font-bold uppercase tracking-widest transition-all duration-200 flex items-center justify-center gap-2',
                  activeTab === 'basica'
                    ? 'text-emerald-700 bg-white border-b-2 border-emerald-600'
                    : 'text-slate-400 hover:text-slate-600 hover:bg-slate-100/50'
                ]"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
                Info Básica
              </button>
              <button
                @click="handleTabChange('avanzada')"
                :class="[
                  'flex-1 py-4 px-6 text-xs font-bold uppercase tracking-widest transition-all duration-200 flex items-center justify-center gap-2',
                  activeTab === 'avanzada'
                    ? 'text-emerald-700 bg-white border-b-2 border-emerald-600'
                    : 'text-slate-400 hover:text-slate-600 hover:bg-slate-100/50'
                ]"
              >
                <svg v-if="!isUnlocked" class="w-4 h-4 text-emerald-600" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd"/></svg>
                <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
                Info Avanzada
              </button>
            </div>

            <!-- Tab Content -->
            <transition name="fade" mode="out-in">
              <div v-if="activeTab === 'basica'" key="basica" class="p-6 sm:p-8">
                <p class="text-slate-400 text-xs font-semibold mb-8 flex items-center gap-2">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                  Esta información es pública para los clientes que visiten tu catálogo.
                </p>

                <form @submit.prevent="guardar" class="space-y-6">
                  <!-- Nombre empresa -->
                  <div>
                    <label class="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-2 ml-1">
                      {{ rol === 'agencia' ? 'Nombre de la Agencia' : 'Nombre de la Empresa' }}
                    </label>
                    <input id="nombre-empresa" v-model="form.nombreEmpresa" type="text"
                      class="w-full rounded-2xl border border-slate-200 bg-slate-50/50 px-4 py-3 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all font-medium"
                      placeholder="Ej: Amazonia Tours S.A.S." />
                  </div>

                  <!-- Teléfono -->
                  <div>
                    <label class="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-2 ml-1">Teléfono de contacto</label>
                    <input id="telefono" v-model="form.numero_telefonico" type="tel"
                      class="w-full rounded-2xl border border-slate-200 bg-slate-50/50 px-4 py-3 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all font-medium"
                      placeholder="+57 300 123 4567" />
                  </div>

                  <!-- Descripción -->
                  <div>
                    <label class="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-2 ml-1">Descripción comercial</label>
                    <textarea id="descripcion" v-model="form.descripcion" rows="4"
                      class="w-full rounded-2xl border border-slate-200 bg-slate-50/50 px-4 py-3 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all font-medium resize-none shadow-inner"
                      placeholder="Cuéntale a los viajeros quiénes son...">
                    </textarea>
                    <div class="flex justify-end mt-2">
                      <span class="text-[10px] font-bold text-slate-400 bg-slate-100 px-2 py-0.5 rounded">{{ (form.descripcion || '').length }}/255</span>
                    </div>
                  </div>

                  <!-- Redes -->
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div v-for="red in redesDisponibles" :key="red.key" class="flex items-center gap-3 bg-slate-50 p-3 rounded-2xl border border-slate-100">
                      <span class="w-5 h-5 text-slate-400 shrink-0" v-html="red.icon"></span>
                      <input v-model="form.informacion_contacto[red.key]"
                        type="text" :placeholder="red.label"
                        class="bg-transparent border-none outline-none text-xs w-full text-slate-600 font-medium placeholder:text-slate-300" />
                    </div>
                  </div>

                  <!-- Botón guardar -->
                  <div class="pt-4 flex items-center gap-4">
                    <button id="btn-guardar-basica" type="submit" :disabled="isLoading"
                      class="inline-flex items-center gap-2 px-8 py-3 bg-slate-900 border border-slate-800 hover:bg-slate-800 text-white text-sm font-bold rounded-2xl shadow-xl shadow-slate-900/10 transition-all duration-300 disabled:opacity-60 disabled:cursor-not-allowed hover:-translate-y-0.5">
                      <svg v-if="isLoading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/></svg>
                      <span>Guardar perfil público</span>
                    </button>
                    <transition name="fade">
                      <p v-if="successMsg" class="text-emerald-600 text-xs font-black uppercase tracking-tighter flex items-center gap-1">
                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
                        ¡Sincronizado!
                      </p>
                    </transition>
                  </div>
                </form>
              </div>
              <div v-else-if="activeTab === 'avanzada'" key="avanzada" class="p-6 sm:p-8">
                <InformacionAvanzada v-model:perfil-data="perfil" :rol="normalizedRol" />
              </div>
            </transition>
          </div>

          <!-- ── VISTA PERFIL (PREVIEW SOCIAL COMMERCE) ── -->
          <VistaPerfilPublico 
            v-else 
            key="view" 
            :perfil="perfil" 
            :rol-label="rolLabel" 
          />
        </transition>
      </div>
    </div>
  </div>

  <!-- ═══ MODAL DE SEGURIDAD (CONTRASEÑA) ═══ -->
  <transition name="fade">
    <div v-if="showPasswordModal" class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
      <div class="bg-white rounded-3xl shadow-2xl w-full max-w-md overflow-hidden animate-in fade-in zoom-in duration-300">
        <div class="p-8 text-center">
          <div class="w-16 h-16 bg-amber-100 rounded-full flex items-center justify-center mx-auto mb-6 text-amber-600">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>
          </div>
          <h2 class="text-xl font-bold text-slate-800 mb-2">Área de Seguridad</h2>
          <p class="text-sm text-slate-500 mb-8">Por favor, ingresa tu contraseña para acceder a la información legal y avanzar.</p>
          
          <div class="space-y-4">
            <input 
              v-model="confirmPassword" 
              type="password" 
              placeholder="Tu contraseña"
              class="w-full px-5 py-3 rounded-2xl border border-slate-200 outline-none focus:ring-2 focus:ring-emerald-500 transition-all text-center"
              @keyup.enter="verificarAcceso"
            />
            <p v-if="passwordError" class="text-xs text-red-500 font-medium">{{ passwordError }}</p>
            
            <div class="flex gap-3 pt-2">
              <button @click="showPasswordModal = false" class="flex-1 py-3 px-6 rounded-2xl text-sm font-bold text-slate-500 hover:bg-slate-50 transition-colors">Cancelar</button>
              <button 
                @click="verificarAcceso" 
                :disabled="isVerifyingPassword"
                class="flex-1 py-3 px-6 rounded-2xl text-sm font-bold text-white bg-slate-800 hover:bg-slate-700 transition-all disabled:opacity-50"
              >
                {{ isVerifyingPassword ? 'Verificando...' : 'Confirmar' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import clienteAxios from '@/api/axios.js'
import InformacionAvanzada from '@/components/perfil/InformacionAvanzada.vue'
import MenuLateralPerfil from '@/components/perfil/MenuLateralPerfil.vue'
import VistaPerfilPublico from '@/components/perfil/VistaPerfilPublico.vue'


const route = useRoute()
const currentView = ref('info')
const showPasswordModal = ref(false)

// Sincronizar vista con el query parameter 'tab'
onMounted(() => {
})

watch(() => route.query.tab, (newTab) => {
})
const isUnlocked = ref(false)
const isVerifyingPassword = ref(false)
const confirmPassword = ref('')
const passwordError = ref('')

// ─── Manejo de Pestañas ────────────────────────────────────
function handleTabChange(tab) {
  if (tab === 'avanzada' && !isUnlocked.value) {
    showPasswordModal.value = true
    confirmPassword.value = ''
    passwordError.value = ''
  } else {
    activeTab.value = tab
  }
}

async function verificarAcceso() {
  if (!confirmPassword.value) return
  
  isVerifyingPassword.value = true
  passwordError.value = ''
  
  try {
    await clienteAxios.post('api/confirmar-password/', {
      password: confirmPassword.value
    })
    
    isUnlocked.value = true
    showPasswordModal.value = false
    activeTab.value = 'avanzada'
  } catch (error) {
    passwordError.value = error.response?.data?.error || 'No se pudo verificar la identidad.'
  } finally {
    isVerifyingPassword.value = false
  }
}

// ─── Lógica de Perfil Existente ─────────────────────────────
const rol = ref(localStorage.getItem('rol') || '')
const normalizedRol = computed(() => (rol.value || '').toLowerCase())

// ... restos del estado ...
const isLoading   = ref(false)
const successMsg  = ref(false)
const errorMsg    = ref('')
const activeTab   = ref('basica')

// Foto
const fotoInputRef  = ref(null)
const fotoPreview   = ref(null)
const subiendoFoto  = ref(false)
const fotoMsg       = ref('')
const fotoError     = ref('')

const perfil = reactive({
  id: null, username: '', email: '',
  first_name: '', last_name: '',
  nombre_agencia: '', nombre_empresa: '',
  numero_telefonico: '', descripcion: '',
  informacion_contacto: {}, horario_atencion: '',
  nit: '', rnt: '', rut: '',
  foto_url: null,
})

const form = reactive({
  nombreEmpresa: '',
  numero_telefonico: '',
  descripcion: '',
  logotipo: '',
  horario_atencion: '',
  nit: '',
  rnt: '',
  rut: '',
  informacion_contacto: { instagram: '', facebook: '', whatsapp: '', tiktok: '', web: '' },
})

const redesDisponibles = [
  {
    key: 'instagram', label: 'Instagram', placeholder: 'https://instagram.com/tuempresa',
    icon: `<svg viewBox="0 0 24 24" fill="currentColor" class="w-5 h-5"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>`
  },
  {
    key: 'facebook', label: 'Facebook', placeholder: 'https://facebook.com/tuempresa',
    icon: `<svg viewBox="0 0 24 24" fill="currentColor" class="w-5 h-5"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>`
  },
  {
    key: 'whatsapp', label: 'WhatsApp', placeholder: '+57 300 000 0000',
    icon: `<svg viewBox="0 0 24 24" fill="currentColor" class="w-5 h-5"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>`
  },
  {
    key: 'tiktok', label: 'TikTok', placeholder: 'https://tiktok.com/@tuempresa',
    icon: `<svg viewBox="0 0 24 24" fill="currentColor" class="w-5 h-5"><path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/></svg>`
  },
  {
    key: 'web', label: 'Sitio web', placeholder: 'https://tuempresa.com',
    icon: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="w-5 h-5"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 014 10 15.3 15.3 0 01-4 10 15.3 15.3 0 01-4-10 15.3 15.3 0 014-10z"/></svg>`
  },
]

const nombreEmpresa = computed(() =>
  rol.value === 'agencia' ? perfil.nombre_agencia : perfil.nombre_empresa
)
const iniciales = computed(() => {
  const n = nombreEmpresa.value || perfil.username || '?'
  return n.substring(0, 2).toUpperCase()
})
const rolLabel = computed(() => rol.value === 'agencia' ? 'Agencia' : 'Proveedor')

// ─── Carga inicial ─────────────────────────────────────────
onMounted(async () => {
  try {
    const { data } = await clienteAxios.get('api/perfil/')
    Object.assign(perfil, data)
    form.nombreEmpresa     = data.nombre_agencia || data.nombre_empresa || ''
    form.numero_telefonico = data.numero_telefonico || ''
    form.descripcion       = data.descripcion || ''
    form.horario_atencion  = data.horario_atencion || ''
    form.nit               = data.nit || ''
    form.rut               = data.rut || ''
    form.rnt               = data.rnt || ''
    const contacto = data.informacion_contacto || {}
    Object.keys(form.informacion_contacto).forEach(k => {
      form.informacion_contacto[k] = contacto[k] || ''
    })
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

  // Validar tipo y tamaño (max 5 MB)
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

  // Vista previa local inmediata
  fotoPreview.value = URL.createObjectURL(archivo)

  // Subir al backend → Cloudinary
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
    fotoPreview.value = null   // revertir preview
    fotoError.value = 'Error al subir la imagen. Inténtalo de nuevo.'
    setTimeout(() => { fotoError.value = '' }, 5000)
  } finally {
    subiendoFoto.value = false
    // Limpiar el input para que se pueda volver a seleccionar el mismo archivo
    event.target.value = ''
  }
}

// ─── Guardar datos básicos ─────────────────────────────────
async function guardar() {
  isLoading.value = true
  successMsg.value = false
  errorMsg.value = ''
  try {
    const payload = {
      numero_telefonico: form.numero_telefonico,
      descripcion: form.descripcion,
      // Usar perfil directamente para asegurar que los datos del validador se incluyan
      nit: perfil.nit,
      rut: perfil.rut,
      rnt: perfil.rnt,
    }
    if (normalizedRol.value === 'agencia' || normalizedRol.value === 'proveedor') {
      payload.horario_atencion    = form.horario_atencion
      payload.informacion_contacto = Object.fromEntries(
        Object.entries(form.informacion_contacto).filter(([, v]) => v.trim() !== '')
      )
      
      if (normalizedRol.value === 'agencia') {
        payload.nombre_agencia = form.nombreEmpresa
      } else {
        payload.nombre_empresa = form.nombreEmpresa
      }
    }
    const { data } = await clienteAxios.patch('api/perfil/', payload)
    Object.assign(perfil, data)
    // Sincronizar de vuelta al form por si acaso
    form.nit = data.nit
    form.rut = data.rut
    form.rnt = data.rnt
    // ── Actualizar header en tiempo real ──
    const nuevoNombre = form.nombreEmpresa
    const key = normalizedRol.value === 'agencia' ? 'nombre_agencia' : 'nombre_empresa'
    localStorage.setItem(key, nuevoNombre)
    
    window.dispatchEvent(new CustomEvent('perfil:nombre-actualizado', {
      detail: { nombre: nuevoNombre, rol: normalizedRol.value }
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
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}
.fade-enter-from { opacity: 0; transform: translateY(6px); }
.fade-leave-to   { opacity: 0; transform: translateY(-6px); }
</style>
