<script setup>
import { ref } from 'vue'
import VisorImagen from './VisorImagen.vue'
import { useImagenPerfil } from '@/composables/useImagenPerfil'
import { useNotificacion } from '@/composables/useNotificacion'

// Capa para poner sobre una foto de perfil o portada (el contenedor debe ser `relative`):
// al tocarla se ve en grande y, si es de quien tiene la sesión, un botón de cámara permite agregar, cambiar o eliminar.
const props = defineProps({
  url: { type: String, default: null },
  tipo: { type: String, required: true }, // 'perfil' | 'portada'
  editable: { type: Boolean, default: false },
  redondeo: { type: String, default: '' }, // clase de borde redondeado para que la capa siga la forma de la imagen
  posicionBoton: { type: String, default: 'bottom-2 right-2' },
})
const emit = defineEmits(['cambio'])

const { ocupado, subir, eliminar } = useImagenPerfil()
const { mostrarNotificacion } = useNotificacion()

const etiqueta = props.tipo === 'portada' ? 'portada' : 'foto de perfil'
const titulo = etiqueta.charAt(0).toUpperCase() + etiqueta.slice(1)
const viendo = ref(false)
const menuAbierto = ref(false)
const confirmando = ref(false)
const entrada = ref(null)

const elegirArchivo = () => {
  menuAbierto.value = false
  entrada.value?.click()
}

const alSeleccionar = async (evento) => {
  const archivo = evento.target.files?.[0]
  evento.target.value = ''
  if (!archivo) return
  const resultado = await subir(props.tipo, archivo)
  if (resultado.error) return mostrarNotificacion(resultado.error, 'error', 6000)
  emit('cambio', resultado.url)
  mostrarNotificacion(`Tu ${etiqueta} se guardó.`)
}

const alEliminar = async () => {
  const resultado = await eliminar(props.tipo)
  if (resultado.error) return mostrarNotificacion(resultado.error, 'error', 6000)
  confirmando.value = false
  menuAbierto.value = false
  emit('cambio', null)
  mostrarNotificacion(`Tu ${etiqueta} se eliminó.`)
}

const cerrarMenu = () => {
  if (ocupado.value) return
  menuAbierto.value = false
  confirmando.value = false
}
</script>

<template>
  <!-- Tocar la imagen la abre en grande. Solo existe si hay imagen que ver. -->
  <button v-if="url" type="button" class="absolute inset-0 z-[1] cursor-zoom-in outline-none focus-visible:ring-4 focus-visible:ring-emerald-400" :class="redondeo" :aria-label="`Ver ${etiqueta} en grande`" @click="viendo = true"></button>

  <div v-if="ocupado" class="absolute inset-0 z-[3] flex items-center justify-center bg-black/50" :class="redondeo" role="status" aria-label="Guardando…">
    <svg class="h-8 w-8 animate-spin text-white" fill="none" viewBox="0 0 24 24" aria-hidden="true"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" /><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" /></svg>
  </div>

  <template v-if="editable">
    <button type="button" class="absolute z-[2] flex h-10 min-w-10 items-center justify-center gap-1.5 rounded-full bg-white px-2.5 text-xs font-bold text-slate-800 shadow-lg outline-none ring-1 ring-black/10 hover:bg-slate-100 focus-visible:ring-2 focus-visible:ring-emerald-500" :class="posicionBoton" :aria-label="url ? `Editar ${etiqueta}` : `Agregar ${etiqueta}`" @click="menuAbierto = true">
      <svg class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" /><path stroke-linecap="round" stroke-linejoin="round" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
      <span v-if="tipo === 'portada'" class="hidden sm:inline">{{ url ? 'Editar portada' : 'Agregar portada' }}</span>
    </button>
    <input ref="entrada" type="file" accept="image/jpeg,image/png,image/webp,image/gif" class="hidden" @change="alSeleccionar" />

    <Teleport to="body">
      <div v-if="menuAbierto" class="fixed inset-0 z-[2900] flex items-end justify-center bg-black/60 p-3 sm:items-center" @click.self="cerrarMenu" @keydown.esc="cerrarMenu">
        <div class="w-full max-w-sm overflow-hidden rounded-2xl bg-white text-slate-800 shadow-2xl" role="dialog" aria-modal="true" :aria-label="`Opciones de ${etiqueta}`">
          <h2 class="border-b border-slate-100 px-5 py-4 text-base font-black">{{ titulo }}</h2>

          <div v-if="!confirmando" class="p-2">
            <button v-if="url" type="button" class="flex min-h-12 w-full items-center gap-3 rounded-xl px-3 text-left text-sm font-bold hover:bg-slate-100 focus-visible:bg-slate-100 focus-visible:outline-none" @click="menuAbierto = false; viendo = true">Ver {{ etiqueta }}</button>
            <button type="button" class="flex min-h-12 w-full items-center gap-3 rounded-xl px-3 text-left text-sm font-bold hover:bg-slate-100 focus-visible:bg-slate-100 focus-visible:outline-none" @click="elegirArchivo">{{ url ? 'Subir otra imagen' : 'Agregar imagen' }}</button>
            <button v-if="url" type="button" class="flex min-h-12 w-full items-center gap-3 rounded-xl px-3 text-left text-sm font-bold text-rose-600 hover:bg-rose-50 focus-visible:bg-rose-50 focus-visible:outline-none" @click="confirmando = true">Eliminar {{ etiqueta }}</button>
            <button type="button" class="mt-1 flex min-h-12 w-full items-center justify-center rounded-xl px-3 text-sm font-bold text-slate-500 hover:bg-slate-100 focus-visible:bg-slate-100 focus-visible:outline-none" @click="cerrarMenu">Cancelar</button>
          </div>

          <div v-else class="p-5">
            <p class="text-sm text-slate-600">¿Eliminar tu {{ etiqueta }}? Esta acción no se puede deshacer.</p>
            <div class="mt-4 flex gap-2">
              <button type="button" class="min-h-11 flex-1 rounded-xl border border-slate-200 text-sm font-bold hover:bg-slate-100 disabled:opacity-60" :disabled="ocupado" @click="confirmando = false">Cancelar</button>
              <button type="button" class="min-h-11 flex-1 rounded-xl bg-rose-600 text-sm font-bold text-white hover:bg-rose-700 disabled:opacity-60" :disabled="ocupado" @click="alEliminar">{{ ocupado ? 'Eliminando…' : 'Sí, eliminar' }}</button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </template>

  <VisorImagen v-if="viendo && url" :url="url" :titulo="titulo" @cerrar="viendo = false" />
</template>
