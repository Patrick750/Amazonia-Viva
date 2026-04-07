<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import clienteAxios from '@/api/axios'
import VistaPerfilPublico from '@/components/perfil/VistaPerfilPublico.vue'

const route = useRoute()
const router = useRouter()
const perfilData = ref(null)
const cargando = ref(true)
const error = ref(false)

const cargarPerfil = async () => {
  cargando.value = true
  error.value = false
  const idStr = route.params.id
  
  if (!idStr) {
    error.value = true
    cargando.value = false
    return
  }

  try {
    // Intentar obtener el perfil público
    // Opcionalmente podemos pasar el tipo si lo tenemos desde la tarjeta, 
    // pero el backend intentará buscar en ambos si no se pasa.
    const tipoQuery = route.query.tipo ? `?tipo=${route.query.tipo}` : ''
    const { data } = await clienteAxios.get(`/api/perfil/publico/${idStr}/${tipoQuery}`)
    perfilData.value = data
  } catch (err) {
    console.error('Error cargando perfil público:', err)
    error.value = true
  } finally {
    cargando.value = false
  }
}

onMounted(cargarPerfil)

// Si la ruta cambia de ID estando en la misma vista, recargar.
watch(() => route.params.id, cargarPerfil)

</script>

<template>
  <div class="bg-slate-50 flex flex-col w-full h-full">
    <main class="flex-1 w-full max-w-[1200px] mx-auto py-6 px-4 sm:px-6 lg:px-8 mt-[72px]">
      <div v-if="cargando" class="flex flex-col items-center justify-center min-h-[50vh] gap-4">
        <svg class="w-12 h-12 text-emerald-600 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p class="text-slate-500 font-medium">Cargando perfil...</p>
      </div>

      <div v-else-if="error || !perfilData" class="flex flex-col items-center justify-center min-h-[50vh] text-center max-w-md mx-auto">
        <div class="w-20 h-20 bg-rose-50 text-rose-500 rounded-full flex items-center justify-center mb-6">
          <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
        </div>
        <h2 class="text-2xl font-black text-slate-800 mb-2">Perfil no encontrado</h2>
        <p class="text-slate-500 mb-6">El perfil que buscas no existe o no está disponible públicamente.</p>
        <button @click="router.push('/catalogo')" class="px-6 py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold shadow-sm transition-colors">
          Volver al catálogo
        </button>
      </div>

      <div v-else>
        <!-- Reutilizamos el componente del perfil, pasando el prop esPropietario=false -->
        <VistaPerfilPublico 
          :perfil="perfilData" 
          :esPropietario="false"
          :rolLabel="perfilData.es_agencia ? 'Agencia' : (perfilData.es_proveedor ? 'Proveedor' : 'Usuario')"
        />
      </div>
    </main>
  </div>
</template>
