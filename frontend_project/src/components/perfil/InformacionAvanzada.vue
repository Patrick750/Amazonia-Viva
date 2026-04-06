<template>
  <div class="space-y-6">
    <!-- ═══ SECCIÓN 1: VERIFICADOR DE CREDENCIALES (MOCK) ═══ -->
    <div class="bg-slate-50 border border-slate-200 rounded-2xl p-5 shadow-sm">
      <div class="flex items-center gap-3 mb-4">
        <div class="w-10 h-10 rounded-full bg-amber-100 flex items-center justify-center text-amber-600">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
          </svg>
        </div>
        <div>
          <h3 class="text-sm font-bold text-slate-800">Verificador RUES / RNT (Simulación)</h3>
          <p class="text-xs text-slate-500">Valida tus documentos legales contra la base de datos nacional.</p>
        </div>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <!-- Tipo de Documento -->
        <div>
          <label class="block text-xs font-semibold text-slate-600 mb-1">Tipo de Credencial</label>
          <select 
            v-model="verificationForm.tipo"
            class="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:ring-2 focus:ring-amber-500 outline-none bg-white"
          >
            <option value="NIT">NIT (Número de Identificación Tributaria)</option>
            <option value="RUT">RUT (Registro Único Tributario)</option>
          </select>
        </div>

        <!-- Número -->
        <div>
          <label class="block text-xs font-semibold text-slate-600 mb-1">Número de Documento</label>
          <input 
            v-model="verificationForm.numero"
            type="text"
            placeholder="Ej: 900123456"
            class="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:ring-2 focus:ring-amber-500 outline-none"
            @keyup.enter="verificar"
          />
        </div>
      </div>

      <!-- Botón de Verificación -->
      <div class="mt-4 flex flex-col gap-3">
        <button 
          @click="verificar"
          :disabled="isLoading || !verificationForm.numero"
          class="w-full sm:w-auto px-6 py-2.5 bg-slate-800 hover:bg-slate-700 text-white text-xs font-bold rounded-lg transition-all duration-200 disabled:opacity-50 flex items-center justify-center gap-2"
        >
          <svg v-if="isLoading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/></svg>
          {{ isLoading ? 'Consultando RUES...' : 'Verificar Identidad' }}
        </button>

        <!-- Alertas de Estado -->
        <transition name="fade">
          <div v-if="statusMsg" :class="[
            'p-3 rounded-lg text-xs font-medium flex items-center gap-2 border',
            statusType === 'success' ? 'bg-emerald-50 border-emerald-200 text-emerald-700' : 'bg-red-50 border-red-200 text-red-700'
          ]">
            <svg v-if="statusType === 'success'" class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" /></svg>
            <svg v-else class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" /></svg>
            {{ statusMsg }}
          </div>
        </transition>
      </div>
    </div>

    <!-- ═══ SECCIÓN 2: DATOS LEGALES DEL PERFIL ═══ -->
    <div class="space-y-5">
      <div class="flex items-center justify-between mb-2">
        <label class="text-xs font-bold text-slate-400 uppercase tracking-wider">Registro Legal en Plataforma</label>
        <span v-if="camposVerificados.nit || camposVerificados.rnt" class="text-[10px] bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded font-bold uppercase animate-pulse">
          Cambios pendientes de guardar
        </span>
      </div>
      
      <!-- NIT -->
      <div class="group">
        <label class="block text-sm font-medium text-slate-700 mb-1 flex items-center gap-2">
          NIT
          <span v-if="camposVerificados.nit || perfilData.nit" class="text-[10px] text-emerald-600 font-bold flex items-center gap-0.5">
            <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>
            Verificado
          </span>
        </label>
        <div class="relative">
          <input 
            v-model="perfilData.nit" 
            type="text" 
            :disabled="esCampoBloqueado('nit')"
            :placeholder="esCampoBloqueado('nit') ? '' : 'Pendiente de registrar...'"
            :class="[
              'w-full rounded-lg border px-4 py-2.5 text-sm transition-all duration-300',
              esCampoBloqueado('nit') 
                ? 'border-slate-200 bg-slate-100 text-slate-400 cursor-not-allowed pr-10' 
                : 'border-slate-300 text-slate-800 focus:ring-2 focus:ring-emerald-500 focus:border-transparent'
            ]"
          />
          <svg v-if="esCampoBloqueado('nit')" class="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
          </svg>
        </div>
      </div>

      <!-- RNT (solo agencia) -->
      <div v-if="roleLower === 'agencia'">
        <label class="block text-sm font-medium text-slate-700 mb-1 flex items-center gap-2">
          RNT (Registro Nacional de Turismo)
          <span v-if="camposVerificados.rnt || perfilData.rnt" :class="[
            'text-[10px] font-bold flex items-center gap-0.5',
            rntJustReverified ? 'text-emerald-700' : (isRNTExpired ? 'text-amber-600' : 'text-emerald-600')
          ]">
            <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>
            {{ rntJustReverified ? 'Verificación Anual Renovada' : (isRNTExpired ? 'Documento por Renovar' : 'Vigente') }}
          </span>
        </label>
        <div class="relative flex items-center gap-2">
          <input 
            v-model="perfilData.rnt" 
            type="text" 
            :disabled="esCampoBloqueado('rnt')"
            placeholder="Pendiente de registrar..."
            :class="[
              'w-full flex-1 rounded-lg border px-4 py-2.5 text-sm transition-all duration-300',
              esCampoBloqueado('rnt') 
                ? 'border-slate-200 bg-slate-100 text-slate-400 cursor-not-allowed pr-10' 
                : 'border-slate-300 text-slate-800 focus:ring-2 focus:ring-emerald-500 focus:border-transparent'
            ]"
          />
          <button 
            v-if="isRNTExpired && perfilData.rnt && !rntJustReverified" 
            @click="reverificarRNT"
            :disabled="isLoading"
            class="whitespace-nowrap px-3 py-2 bg-emerald-100 hover:bg-emerald-200 text-emerald-800 text-[10px] font-bold rounded-lg transition-all border border-emerald-200"
          >
            Actualizar Verificación
          </button>
          <svg v-if="esCampoBloqueado('rnt')" class="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-emerald-500" :class="{'mr-28': isRNTExpired && !rntJustReverified}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
          </svg>
        </div>
      </div>

      <!-- RUT -->
      <div class="group">
        <label class="block text-sm font-medium text-slate-700 mb-1 flex items-center gap-2">
          RUT
          <span v-if="camposVerificados.rut || perfilData.rut" class="text-[10px] text-emerald-600 font-bold flex items-center gap-0.5">
            <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>
            Verificado
          </span>
        </label>
        <div class="relative">
          <input 
            v-model="perfilData.rut" 
            type="text" 
            :disabled="esCampoBloqueado('rut')"
            :placeholder="esCampoBloqueado('rut') ? '' : 'Ingresa tu RUT aquí...'"
            :class="[
              'w-full rounded-lg border px-4 py-2.5 text-sm transition-all duration-300',
              esCampoBloqueado('rut') 
                ? 'border-slate-200 bg-slate-100 text-slate-400 cursor-not-allowed pr-10' 
                : 'border-slate-300 text-slate-800 focus:ring-2 focus:ring-emerald-500 focus:border-transparent'
            ]"
          />
          <svg v-if="esCampoBloqueado('rut')" class="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
          </svg>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import clienteAxios from '@/api/axios.js'

const emit = defineEmits(['update:perfilData'])

const props = defineProps({
  perfilData: Object,
  rol: String
})

// Normalizar el rol para comparaciones seguras
const roleLower = computed(() => (props.rol || '').toLowerCase())

// Estado del Verificador Mock
const isLoading = ref(false)
const statusMsg = ref('')
const statusType = ref('success')
const rntJustReverified = ref(false)

// Calcular si el RNT ha "vencido" (300 segundos para la prueba)
const isRNTExpired = computed(() => {
  const joinDate = props.perfilData.rnt_registrado_at || props.perfilData.date_joined
  if (!joinDate) return false
  
  const startTime = new Date(joinDate).getTime()
  const now = Date.now()
  return (now - startTime) > 2592000000 // 30 días (1 mes)
})

// Rastrear qué campos han sido verificados satisfactoriamente en esta sesión
const camposVerificados = reactive({
  nit: false,
  rnt: false,
  rut: false
})

const verificationForm = reactive({
  tipo: 'NIT',
  numero: ''
})

// Función para determinar si un campo debe estar deshabilitado
const esCampoBloqueado = (campo) => {
  // NIT, RNT y RUT siempre bloqueados (solo se llenan via verificador/botón)
  if (['nit', 'rnt', 'rut'].includes(campo)) return true
  
  return !!props.perfilData[campo]
}

async function verificar() {
  if (!verificationForm.numero) return
  
  isLoading.value = true
  statusMsg.value = ''
  
  try {
    const campo = verificationForm.tipo.toLowerCase()
    
    // SEGURIDAD: Evitar que el verificador sobrescriba datos ya existentes (inmutables)
    if (props.perfilData[campo] && props.perfilData[campo] !== verificationForm.numero) {
      statusMsg.value = `No se puede cambiar el ${verificationForm.tipo} una vez registrado.`
      statusType.value = 'error'
      isLoading.value = false
      return
    }

    const { data } = await clienteAxios.post('api/verificar-credenciales/', {
      tipo: verificationForm.tipo,
      numero: verificationForm.numero
    })
    
    // Si la verificación es exitosa:
    statusMsg.value = data.mensaje
    statusType.value = 'success'

    // 1. Asignar el valor al perfil (esto se refleja en el padre)
    const nuevoPerfil = { ...props.perfilData, [campo]: verificationForm.numero }
    emit('update:perfilData', nuevoPerfil)
    
    // 2. Persistir inmediatamente en la Base de Datos para evitar doble acción del usuario
    try {
      await clienteAxios.patch('api/perfil/', { [campo]: verificationForm.numero })
      statusMsg.value = `${data.mensaje} (Dato registrado permanentemente)`
    } catch (saveError) {
      // Si el backend rechaza (ej: duplicado), revertir localmente
      statusMsg.value = saveError.response?.data?.mensaje || 'Error al registrar el dato en el servidor.'
      statusType.value = 'error'
      return
    }

    // 3. Marcar como verificado para bloquear el campo
    camposVerificados[campo] = true

  } catch (error) {
    if (error.response && error.response.status === 404) {
      statusMsg.value = error.response.data.mensaje || 'Credencial no encontrada en el sistema estatal.'
    } else {
      statusMsg.value = 'Error de conexión con el servicio de verificación.'
    }
    statusType.value = 'error'
  } finally {
    isLoading.value = false
    setTimeout(() => { statusMsg.value = '' }, 8000)
  }
}

async function reverificarRNT() {
  if (!props.perfilData.rnt) return
  
  verificationForm.tipo = 'RNT'
  verificationForm.numero = props.perfilData.rnt
  
  await verificar()
  
  if (statusType.value === 'success') {
    rntJustReverified.value = true
    // En una app real, esto actualizaría una fecha 'rnt_last_verified' en la DB
  }
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(-5px);
}
</style>
