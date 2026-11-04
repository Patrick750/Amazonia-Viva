<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'

// Visor a pantalla completa de una foto de perfil o portada, como al abrir una foto en una red social.
defineProps({
  url: { type: String, required: true },
  titulo: { type: String, default: 'Imagen' },
})
const emit = defineEmits(['cerrar'])

const botonCerrar = ref(null)
const alTeclado = (evento) => { if (evento.key === 'Escape') emit('cerrar') }

onMounted(async () => {
  document.addEventListener('keydown', alTeclado)
  document.body.style.overflow = 'hidden'
  await nextTick()
  botonCerrar.value?.focus()
})
onBeforeUnmount(() => {
  document.removeEventListener('keydown', alTeclado)
  document.body.style.overflow = ''
})
</script>

<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-[3000] flex items-center justify-center bg-black/90 p-3 sm:p-8" role="dialog" aria-modal="true" :aria-label="titulo" @click.self="emit('cerrar')">
      <button ref="botonCerrar" type="button" class="absolute right-3 top-3 flex h-11 w-11 items-center justify-center rounded-full bg-white/15 text-white outline-none hover:bg-white/25 focus-visible:ring-2 focus-visible:ring-white sm:right-6 sm:top-6" aria-label="Cerrar" @click="emit('cerrar')">
        <svg class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="2.4" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" d="M6 6l12 12M18 6L6 18" /></svg>
      </button>
      <img :src="url" :alt="titulo" class="max-h-full max-w-full rounded-lg object-contain shadow-2xl" />
    </div>
  </Teleport>
</template>
