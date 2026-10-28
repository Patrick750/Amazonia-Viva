<script setup>
import { nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { useInstalarPwa } from '@/composables/useInstalarPwa'

// "boton": acción destacada en la barra superior (desde 640 px).
// "banner": aviso a todo el ancho bajo la barra, solo en móvil, para no saturar la barra superior.
defineProps({ variante: { type: String, default: 'boton' } })

const { disponible, puedeInstalar, instalar } = useInstalarPwa()

const leerCerrado = () => {
  try { return sessionStorage.getItem('pwa_banner_cerrado') === '1' } catch { return false }
}
const bannerCerrado = ref(leerCerrado())
const cerrarBanner = () => {
  bannerCerrado.value = true
  try { sessionStorage.setItem('pwa_banner_cerrado', '1') } catch { /* sin almacenamiento: se oculta solo en esta visita */ }
}

const guiaAbierta = ref(false)
const botonCerrarGuia = ref(null)

const alPulsar = async () => {
  if (puedeInstalar.value) await instalar()
  else guiaAbierta.value = true
}

const alTeclear = (evento) => { if (evento.key === 'Escape') guiaAbierta.value = false }

watch(guiaAbierta, async (abierta) => {
  if (abierta) {
    window.addEventListener('keydown', alTeclear)
    await nextTick()
    botonCerrarGuia.value?.focus()
  } else {
    window.removeEventListener('keydown', alTeclear)
  }
})

onBeforeUnmount(() => window.removeEventListener('keydown', alTeclear))
</script>

<template>
  <template v-if="disponible">
    <button
      v-if="variante === 'boton'"
      type="button"
      class="relative hidden items-center gap-2 rounded-full bg-gradient-to-r from-emerald-700 to-teal-700 px-4 py-2.5 text-sm font-bold text-white shadow-lg shadow-emerald-500/30 ring-1 ring-emerald-300/40 outline-none transition hover:from-emerald-600 hover:to-teal-600 focus-visible:ring-2 focus-visible:ring-white sm:inline-flex"
      @click="alPulsar"
    >
      <span class="absolute -right-1 -top-1 flex h-3 w-3" aria-hidden="true">
        <span class="absolute inline-flex h-full w-full rounded-full bg-amber-300 opacity-75 motion-safe:animate-ping"></span>
        <span class="relative inline-flex h-3 w-3 rounded-full bg-amber-300"></span>
      </span>
      <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.2" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M12 3v12m0 0 4-4m-4 4-4-4M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" /></svg>
      Instalar app
    </button>

    <div v-else-if="variante === 'banner' && !bannerCerrado" class="flex items-center gap-2 bg-emerald-700 px-4 py-2 text-white sm:hidden" role="region" aria-label="Instalar la aplicación">
      <svg class="h-5 w-5 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.2" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M12 3v12m0 0 4-4m-4 4-4-4M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" /></svg>
      <p class="min-w-0 flex-1 text-xs font-semibold leading-tight">Instala Amazonia Viva en tu dispositivo</p>
      <button type="button" class="min-h-11 shrink-0 rounded-lg bg-white px-4 text-xs font-black uppercase tracking-wider text-emerald-800 outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-emerald-700" @click="alPulsar">Instalar</button>
      <button type="button" class="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg text-white/90 outline-none hover:bg-white/10 focus-visible:ring-2 focus-visible:ring-white" aria-label="Cerrar aviso de instalación" @click="cerrarBanner">
        <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" /></svg>
      </button>
    </div>

    <Teleport to="body">
      <div v-if="guiaAbierta" class="fixed inset-0 z-[100] flex items-end justify-center bg-black/70 p-4 sm:items-center" @click.self="guiaAbierta = false">
        <div class="w-full max-w-sm rounded-3xl bg-[#0f2318] p-6 text-white shadow-2xl ring-1 ring-white/10" role="dialog" aria-modal="true" aria-labelledby="titulo-guia-instalar">
          <h2 id="titulo-guia-instalar" class="mb-1 text-lg font-black">Instalar en iPhone o iPad</h2>
          <p class="mb-4 text-sm text-white/70">Safari no permite instalar con un solo toque. Sigue estos pasos:</p>
          <ol class="mb-6 space-y-3 text-sm">
            <li class="flex gap-3"><span class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-emerald-600 text-xs font-black">1</span><span>Toca el botón <strong>Compartir</strong> de la barra de Safari.</span></li>
            <li class="flex gap-3"><span class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-emerald-600 text-xs font-black">2</span><span>Elige <strong>Añadir a pantalla de inicio</strong>.</span></li>
            <li class="flex gap-3"><span class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-emerald-600 text-xs font-black">3</span><span>Confirma con <strong>Añadir</strong>.</span></li>
          </ol>
          <button ref="botonCerrarGuia" type="button" class="min-h-12 w-full rounded-xl bg-emerald-600 px-4 text-sm font-black uppercase tracking-widest text-black outline-none hover:bg-emerald-500 focus-visible:ring-2 focus-visible:ring-white" @click="guiaAbierta = false">Entendido</button>
        </div>
      </div>
    </Teleport>
  </template>
</template>
