<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import clienteAxios from '@/api/axios'

const route = useRoute()
const cargando = ref(true)
const viajero = ref(null)
const error = ref('')

onMounted(async () => {
  try {
    const { data } = await clienteAxios.get(`api/turista/grupo/viajeros/${route.params.id}/`)
    viajero.value = data
  } catch (fallo) {
    error.value = fallo.response?.status === 404
      ? 'Este perfil no está disponible. Solo se puede ver a quien comparte su ubicación hoy en un paquete que tú también haces.'
      : 'No pudimos cargar este perfil. Revisa tu conexión e inténtalo de nuevo.'
  } finally {
    cargando.value = false
  }
})
</script>

<template>
  <div class="min-h-screen bg-[#0a1a0f] px-4 pb-10 pt-24 text-white sm:px-6">
    <main class="mx-auto max-w-md">
      <p v-if="cargando" class="text-white/60" role="status">Cargando…</p>
      <p v-else-if="error" class="rounded-2xl border border-amber-300/30 bg-amber-300/10 p-4 text-sm text-amber-100" role="alert">{{ error }}</p>
      <section v-else class="rounded-3xl border border-white/10 bg-white/5 p-6 text-center">
        <img v-if="viajero.foto" :src="viajero.foto" :alt="`Foto de ${viajero.nombre}`" class="mx-auto h-24 w-24 rounded-full object-cover ring-4 ring-violet-500/60" />
        <div v-else class="mx-auto flex h-24 w-24 items-center justify-center rounded-full bg-violet-600 text-3xl font-black ring-4 ring-violet-500/60" aria-hidden="true">{{ viajero.nombre.charAt(0) }}</div>
        <h1 class="mt-4 text-2xl font-black">{{ viajero.nombre }}</h1>
        <p class="mt-1 text-sm text-white/60">Viajero en Amazonia Viva desde {{ viajero.miembro_desde }}</p>
        <p class="mt-4 rounded-xl bg-violet-500/15 p-3 text-sm text-violet-100">Hoy hace contigo: <strong>{{ viajero.viaja_en }}</strong></p>
      </section>
    </main>
  </div>
</template>
