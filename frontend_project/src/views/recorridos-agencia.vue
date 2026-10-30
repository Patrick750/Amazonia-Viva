<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { onBeforeRouteLeave } from 'vue-router'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import clienteAxios from '@/api/axios'
import { paquetes as pedirPaquetes } from '@/composables/gestion-tours/paquetes'
import { useGrabacion } from '@/composables/recorridos/useGrabacion'
import { useMiUbicacion } from '@/composables/recorridos/useMiUbicacion'
import { listarRecorridos } from '@/composables/recorridos/almacenLocal'
import { reintentarRecorrido } from '@/composables/recorridos/sincronizacion'

const CLAVE_PAQUETES = 'recorridos_paquetes'

const misPaquetes = ref([])
const paqueteId = ref('')
const nombreRecorrido = ref('')
const remotos = ref([])
const locales = ref([])
const mensaje = ref('')
const errorLista = ref('')
const mapaEl = ref(null)

const cargarLista = async () => {
  locales.value = await listarRecorridos().catch(() => [])
  try {
    const { data } = await clienteAxios.get('api/recorridos/')
    remotos.value = data
    errorLista.value = ''
  } catch {
    errorLista.value = 'Sin conexión: se muestran solo los recorridos guardados en este dispositivo.'
  }
}

const grabacion = useGrabacion({ alSincronizar: cargarLista })
const { estado, recorrido, trazado, total, pendientes, precision, aviso, enLinea, sincronizando } = grabacion

// La ubicación en vivo se muestra siempre, no solo cuando se guarda un punto de la grabación.
const { posicion: miPosicion, estado: estadoUbicacion, iniciar: iniciarUbicacion } = useMiUbicacion()
const textoUbicacion = computed(() => ({
  buscando: 'Buscando tu ubicación… Acepta el permiso de ubicación si el navegador lo pide.',
  activa: `Tu ubicación está activa${miPosicion.value ? ` · precisión de ${miPosicion.value.precision} m` : ''}.`,
  denegada: 'El permiso de ubicación está denegado. Actívalo en el candado de la barra de direcciones y pulsa «Reintentar».',
  sin_gps: 'No se puede obtener la ubicación. Comprueba que el GPS del dispositivo esté activado y pulsa «Reintentar».',
  no_disponible: 'Este navegador no permite usar la ubicación aquí. Se necesita una conexión segura (https).',
}[estadoUbicacion.value]))

const nombreDelPaquete = (id) => misPaquetes.value.find(p => p.id === id)?.nombre || `Paquete ${id}`
const formatoFecha = (valor) => (valor ? new Date(valor).toLocaleString('es-CO', { dateStyle: 'medium', timeStyle: 'short' }) : '')

const recorridosMostrados = computed(() => {
  const porId = new Map(remotos.value.map(item => [item.id_cliente, { ...item }]))
  locales.value.forEach((local) => {
    const base = porId.get(local.id_cliente) || {
      id_cliente: local.id_cliente, paquete: local.paquete, nombre: local.nombre,
      iniciado_en: local.iniciado_en, finalizado_en: local.finalizado_en, publicado: false, total_puntos: null,
    }
    porId.set(local.id_cliente, { ...base, local: true, completo: local.completo, errorLocal: local.error })
  })
  return [...porId.values()].sort((a, b) => new Date(b.iniciado_en) - new Date(a.iniciado_en))
})

const etiquetaEstado = (item) => {
  if (item.errorLocal) return { texto: 'Rechazado por el servidor', clase: 'bg-rose-500/15 text-rose-200 border-rose-400/30' }
  if (item.local && !item.completo) {
    return item.finalizado_en
      ? { texto: 'Pendiente de sincronizar', clase: 'bg-amber-400/15 text-amber-200 border-amber-300/30' }
      : { texto: 'Sin terminar', clase: 'bg-sky-400/15 text-sky-200 border-sky-300/30' }
  }
  return item.publicado
    ? { texto: 'Publicado', clase: 'bg-emerald-400/15 text-emerald-200 border-emerald-300/30' }
    : { texto: 'Sincronizado, sin publicar', clase: 'bg-white/10 text-white/70 border-white/20' }
}

const puedePublicar = (item) => !!item.finalizado_en && (!item.local || item.completo) && !item.errorLocal

const cambiarPublicacion = async (item, publicar) => {
  mensaje.value = ''
  try {
    if (publicar) await clienteAxios.post(`api/recorridos/${item.id_cliente}/publicar/`)
    else await clienteAxios.delete(`api/recorridos/${item.id_cliente}/publicar/`)
    mensaje.value = publicar ? 'Recorrido publicado: ya se muestra en el mapa del paquete.' : 'Recorrido retirado del paquete.'
    await cargarLista()
  } catch (error) {
    mensaje.value = error.response?.data?.detail || 'No se pudo cambiar la publicación. Revisa tu conexión e inténtalo de nuevo.'
  }
}

const reintentar = async (item) => {
  await reintentarRecorrido(item.id_cliente)
  await cargarLista()
}

const iniciar = async () => {
  mensaje.value = ''
  await grabacion.iniciar(Number(paqueteId.value), nombreRecorrido.value)
  nombreRecorrido.value = ''
  await cargarLista()
}

const finalizar = async () => {
  await grabacion.finalizar()
  mensaje.value = enLinea.value
    ? 'Recorrido finalizado. Ya puedes publicarlo desde la lista cuando termine de sincronizarse.'
    : 'Recorrido finalizado y guardado en este dispositivo. Se enviará cuando recuperes la conexión.'
  await cargarLista()
}

// --- Mapa ---
let mapa = null
let linea = null
let marcador = null
let circulo = null
let centradoInicial = false

const iniciarMapa = () => {
  if (!mapaEl.value || mapa) return
  mapa = L.map(mapaEl.value).setView([-4.2153, -69.9406], 13)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '&copy; OpenStreetMap contributors' }).addTo(mapa)
  linea = L.polyline([], { color: '#10b981', weight: 5 }).addTo(mapa)
}

watch(trazado, (puntos) => {
  if (mapa) linea.setLatLngs(puntos)
})

// Marcador azul con el círculo de precisión del GPS: sigue al dispositivo antes y durante la grabación.
watch(miPosicion, (actual) => {
  if (!mapa || !actual) return
  const punto = [actual.lat, actual.lng]
  if (!marcador) {
    circulo = L.circle(punto, { radius: actual.precision, color: '#0ea5e9', weight: 1, fillColor: '#0ea5e9', fillOpacity: 0.15 }).addTo(mapa)
    marcador = L.circleMarker(punto, { radius: 9, color: '#fff', weight: 3, fillColor: '#0ea5e9', fillOpacity: 1 }).bindTooltip('Estás aquí').addTo(mapa)
  } else {
    marcador.setLatLng(punto)
    circulo.setLatLng(punto).setRadius(actual.precision)
  }
  if (!centradoInicial) {
    centradoInicial = true
    // Si se recuperó una grabación, el mapa ya enmarca su trazado.
    if (!trazado.value.length) mapa.setView(punto, 17)
  } else if (estado.value === 'grabando') {
    mapa.panTo(punto)
  }
})

const centrarEnMiUbicacion = () => {
  if (mapa && miPosicion.value) mapa.setView([miPosicion.value.lat, miPosicion.value.lng], Math.max(mapa.getZoom(), 17))
}

onMounted(async () => {
  await nextTick()
  iniciarMapa()
  iniciarUbicacion()
  const cache = JSON.parse(localStorage.getItem(CLAVE_PAQUETES) || '[]')
  const traidos = await pedirPaquetes().catch(() => null)
  if (Array.isArray(traidos) && traidos.length) {
    misPaquetes.value = traidos.map(p => ({ id: p.id, nombre: p.nombre }))
    localStorage.setItem(CLAVE_PAQUETES, JSON.stringify(misPaquetes.value))
  } else {
    misPaquetes.value = cache
  }
  await cargarLista()
  if (await grabacion.recuperarPendiente()) {
    mensaje.value = 'Recuperamos una grabación sin terminar de este dispositivo. Puedes reanudarla o finalizarla.'
    if (mapa && trazado.value.length) mapa.fitBounds(L.latLngBounds(trazado.value), { maxZoom: 17 })
  }
  grabacion.sincronizar()
})

onBeforeUnmount(() => {
  mapa?.remove()
  mapa = null
})

onBeforeRouteLeave(() => {
  if (estado.value === 'grabando') {
    return window.confirm('Hay una grabación en curso. Si sales de esta pantalla se pausará. ¿Quieres salir?')
  }
})
</script>

<template>
  <div class="min-h-screen bg-[#0a1a0f] p-6 text-white md:p-10">
    <main class="mx-auto max-w-6xl">
      <header class="mb-8">
        <router-link to="/panel/gestion-paquetes" class="mb-4 inline-flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-emerald-400/70 hover:text-emerald-300 focus:outline-none focus:ring-2 focus:ring-emerald-300">
          ← Volver a Gestión de Tours
        </router-link>
        <h1 class="text-4xl font-black tracking-tight sm:text-5xl">Recorridos <span class="text-emerald-500">GPS</span></h1>
        <p class="mt-2 text-sm text-white/60">Graba el trayecto real de un paquete, incluso sin internet, y publícalo para que se vea en su mapa.</p>
        <div class="mt-4 flex flex-wrap items-center gap-3" aria-live="polite">
          <span class="inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-bold" :class="enLinea ? 'border-emerald-300/30 bg-emerald-400/10 text-emerald-200' : 'border-amber-300/30 bg-amber-400/10 text-amber-200'">
            <span class="h-2 w-2 rounded-full" :class="enLinea ? 'bg-emerald-400' : 'bg-amber-300'"></span>
            {{ enLinea ? 'En línea' : 'Sin conexión: los puntos se guardan en este dispositivo' }}
          </span>
          <span v-if="sincronizando" class="text-xs font-bold text-sky-200">Sincronizando…</span>
        </div>
      </header>

      <p class="mb-6 rounded-2xl border border-amber-300/25 bg-amber-300/10 p-4 text-sm text-amber-100">
        Mantén la pantalla encendida y esta aplicación abierta mientras grabas. Los navegadores pueden pausar el GPS cuando el teléfono se bloquea; la aplicación intenta evitar que la pantalla se apague, pero no puede garantizarlo en todos los dispositivos.
      </p>

      <p v-if="mensaje" class="mb-6 rounded-2xl border border-emerald-300/25 bg-emerald-400/10 p-4 text-sm text-emerald-100" role="status">{{ mensaje }}</p>

      <div class="grid gap-6 lg:grid-cols-[22rem_1fr]">
        <section class="rounded-3xl border border-white/10 bg-white/5 p-6" aria-labelledby="titulo-grabacion">
          <h2 id="titulo-grabacion" class="mb-4 text-lg font-black">Grabación</h2>

          <template v-if="estado === 'inactivo'">
            <label for="paquete-recorrido" class="mb-1.5 block text-sm font-semibold">Paquete</label>
            <select id="paquete-recorrido" v-model="paqueteId" class="mb-4 w-full rounded-xl border border-white/20 bg-[#0b1c12] px-4 py-3 text-base text-white focus:outline-none focus:ring-2 focus:ring-emerald-400">
              <option value="" disabled>Selecciona un paquete</option>
              <option v-for="paquete in misPaquetes" :key="paquete.id" :value="paquete.id">{{ paquete.nombre }}</option>
            </select>
            <p v-if="!misPaquetes.length" class="-mt-2 mb-4 text-xs text-amber-200">No hay paquetes disponibles. Conéctate una vez para cargar tu lista.</p>

            <label for="nombre-recorrido" class="mb-1.5 block text-sm font-semibold">Nombre <span class="font-normal text-white/60">(opcional)</span></label>
            <input id="nombre-recorrido" v-model="nombreRecorrido" type="text" maxlength="120" placeholder="Ruta del día" class="mb-5 w-full rounded-xl border border-white/20 bg-[#0b1c12] px-4 py-3 text-base text-white placeholder:text-white/40 focus:outline-none focus:ring-2 focus:ring-emerald-400" />

            <button type="button" :disabled="!paqueteId" class="min-h-12 w-full rounded-xl bg-emerald-600 px-4 py-3 text-sm font-black uppercase tracking-widest text-black transition hover:bg-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-300 disabled:cursor-not-allowed disabled:opacity-50" @click="iniciar">
              Iniciar recorrido
            </button>
          </template>

          <template v-else>
            <p class="mb-1 text-sm text-white/60">{{ nombreDelPaquete(recorrido.paquete) }}</p>
            <p class="mb-4 text-base font-bold" aria-live="polite">{{ estado === 'grabando' ? 'Grabando…' : 'En pausa' }}</p>
            <dl class="mb-5 grid grid-cols-3 gap-3 text-center">
              <div class="rounded-xl bg-black/25 p-3"><dt class="text-[11px] uppercase text-white/50">Puntos</dt><dd class="text-xl font-black">{{ total }}</dd></div>
              <div class="rounded-xl bg-black/25 p-3"><dt class="text-[11px] uppercase text-white/50">Sin enviar</dt><dd class="text-xl font-black">{{ pendientes }}</dd></div>
              <div class="rounded-xl bg-black/25 p-3"><dt class="text-[11px] uppercase text-white/50">Precisión</dt><dd class="text-xl font-black">{{ precision === null ? '—' : precision + ' m' }}</dd></div>
            </dl>
            <div class="flex flex-col gap-3">
              <button v-if="estado === 'grabando'" type="button" class="min-h-12 rounded-xl border border-white/25 px-4 py-3 text-sm font-black uppercase tracking-widest hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-emerald-300" @click="grabacion.pausar">Pausar</button>
              <button v-else type="button" class="min-h-12 rounded-xl bg-emerald-600 px-4 py-3 text-sm font-black uppercase tracking-widest text-black hover:bg-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-300" @click="grabacion.reanudar">Reanudar</button>
              <button type="button" class="min-h-12 rounded-xl bg-rose-500 px-4 py-3 text-sm font-black uppercase tracking-widest text-white hover:bg-rose-400 focus:outline-none focus:ring-2 focus:ring-rose-300" @click="finalizar">Finalizar recorrido</button>
            </div>
          </template>

          <p v-if="aviso" class="mt-4 rounded-xl border border-amber-300/30 bg-amber-300/10 p-3 text-sm text-amber-100" role="alert">{{ aviso }}</p>
        </section>

        <section aria-label="Mapa del recorrido">
          <div ref="mapaEl" class="h-80 w-full overflow-hidden rounded-3xl border border-white/10 lg:h-[calc(100%-4.5rem)] lg:min-h-[22rem]"></div>
          <div class="mt-3 flex flex-wrap items-center justify-between gap-3">
            <p class="min-w-0 flex-1 text-sm" :class="estadoUbicacion === 'activa' ? 'text-emerald-200' : estadoUbicacion === 'buscando' ? 'text-white/70' : 'text-amber-200'" role="status">{{ textoUbicacion }}</p>
            <button v-if="estadoUbicacion === 'activa'" type="button" class="min-h-11 shrink-0 rounded-xl border border-sky-300/40 bg-sky-400/10 px-4 text-xs font-black uppercase tracking-widest text-sky-100 hover:bg-sky-400/20 focus:outline-none focus:ring-2 focus:ring-sky-300" @click="centrarEnMiUbicacion">Mi ubicación</button>
            <button v-else-if="estadoUbicacion !== 'buscando' && estadoUbicacion !== 'no_disponible'" type="button" class="min-h-11 shrink-0 rounded-xl border border-amber-300/40 bg-amber-300/10 px-4 text-xs font-black uppercase tracking-widest text-amber-100 hover:bg-amber-300/20 focus:outline-none focus:ring-2 focus:ring-amber-300" @click="iniciarUbicacion">Reintentar</button>
          </div>
        </section>
      </div>

      <section class="mt-10" aria-labelledby="titulo-lista">
        <h2 id="titulo-lista" class="mb-4 text-lg font-black">Mis recorridos</h2>
        <p v-if="errorLista" class="mb-4 text-sm text-amber-200">{{ errorLista }}</p>
        <p v-if="!recorridosMostrados.length" class="rounded-2xl border border-white/10 bg-white/5 p-6 text-sm text-white/60">Aún no has grabado recorridos.</p>
        <ul class="space-y-3">
          <li v-for="item in recorridosMostrados" :key="item.id_cliente" class="flex flex-col gap-3 rounded-2xl border border-white/10 bg-white/5 p-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p class="font-bold">{{ item.nombre || 'Recorrido sin nombre' }} <span class="font-normal text-white/60">· {{ nombreDelPaquete(item.paquete) }}</span></p>
              <p class="mt-1 text-xs text-white/50">{{ formatoFecha(item.iniciado_en) }}<template v-if="item.total_puntos !== null"> · {{ item.total_puntos }} puntos</template></p>
              <p v-if="item.errorLocal" class="mt-1 text-xs text-rose-200">{{ item.errorLocal }}</p>
            </div>
            <div class="flex flex-wrap items-center gap-3">
              <span class="rounded-full border px-3 py-1 text-xs font-bold" :class="etiquetaEstado(item).clase">{{ etiquetaEstado(item).texto }}</span>
              <button v-if="item.errorLocal" type="button" class="min-h-11 rounded-xl border border-white/25 px-4 text-xs font-black uppercase tracking-widest hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-emerald-300" @click="reintentar(item)">Reintentar</button>
              <button v-else-if="puedePublicar(item) && !item.publicado" type="button" class="min-h-11 rounded-xl bg-emerald-600 px-4 text-xs font-black uppercase tracking-widest text-black hover:bg-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-300" @click="cambiarPublicacion(item, true)">Publicar</button>
              <button v-else-if="item.publicado" type="button" class="min-h-11 rounded-xl border border-white/25 px-4 text-xs font-black uppercase tracking-widest hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-emerald-300" @click="cambiarPublicacion(item, false)">Retirar</button>
            </div>
          </li>
        </ul>
      </section>
    </main>
  </div>
</template>
