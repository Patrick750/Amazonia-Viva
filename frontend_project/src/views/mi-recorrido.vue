<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import clienteAxios from '@/api/axios'

const cargando = ref(true)
const habilitados = ref([])
const seleccionado = ref(null)
const datos = ref(null)
const error = ref('')
const verMiUbicacion = ref(false)
const avisoUbicacion = ref('')
const mapaEl = ref(null)

let mapa = null
let capa = null
let miPosicion = null
let idVigilancia = null

const formatoFecha = (valor) => new Date(`${valor}T12:00:00`).toLocaleDateString('es-CO', { dateStyle: 'long' })

const dibujar = () => {
  if (!mapa) return
  mapa.invalidateSize()
  capa.clearLayers()
  if (datos.value?.disponible && datos.value.puntos.length > 1) {
    const linea = L.polyline(datos.value.puntos, { color: '#10b981', weight: 5 }).addTo(capa)
    L.circleMarker(datos.value.puntos[0], { radius: 7, color: '#fff', weight: 2, fillColor: '#16a34a', fillOpacity: 1 }).bindTooltip('Inicio').addTo(capa)
    L.circleMarker(datos.value.puntos.at(-1), { radius: 7, color: '#fff', weight: 2, fillColor: '#dc2626', fillOpacity: 1 }).bindTooltip('Final').addTo(capa)
    mapa.fitBounds(linea.getBounds(), { padding: [30, 30] })
  }
}

const cargarRecorrido = async (paquete) => {
  seleccionado.value = paquete
  datos.value = null
  error.value = ''
  try {
    const { data } = await clienteAxios.get(`api/turista/paquetes/${paquete}/recorrido/`)
    datos.value = data
    await nextTick()
    dibujar()
  } catch (fallo) {
    error.value = fallo.response?.data?.detail || 'No pudimos cargar el recorrido. Revisa tu conexión e inténtalo de nuevo.'
  }
}

const detenerUbicacion = () => {
  if (idVigilancia !== null) navigator.geolocation.clearWatch(idVigilancia)
  idVigilancia = null
  miPosicion?.remove()
  miPosicion = null
}

// La ubicación del turista solo se muestra en su pantalla: no se guarda ni se envía.
watch(verMiUbicacion, (activo) => {
  avisoUbicacion.value = ''
  if (!activo) {
    detenerUbicacion()
    return
  }
  if (!('geolocation' in navigator)) {
    avisoUbicacion.value = 'Este dispositivo no permite usar el GPS desde el navegador.'
    verMiUbicacion.value = false
    return
  }
  idVigilancia = navigator.geolocation.watchPosition(
    ({ coords }) => {
      const punto = [coords.latitude, coords.longitude]
      if (!miPosicion) miPosicion = L.circleMarker(punto, { radius: 9, color: '#fff', weight: 3, fillColor: '#0ea5e9', fillOpacity: 1 }).bindTooltip('Tú').addTo(mapa)
      else miPosicion.setLatLng(punto)
    },
    () => {
      avisoUbicacion.value = 'No pudimos obtener tu ubicación. Revisa el permiso del navegador.'
      verMiUbicacion.value = false
    },
    { enableHighAccuracy: true, maximumAge: 5000, timeout: 20000 },
  )
})

onMounted(async () => {
  await nextTick()
  mapa = L.map(mapaEl.value).setView([-4.2153, -69.9406], 12)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '&copy; OpenStreetMap contributors' }).addTo(mapa)
  capa = L.layerGroup().addTo(mapa)
  try {
    const { data } = await clienteAxios.get('api/turista/recorridos-habilitados/')
    habilitados.value = data
    if (data.length) await cargarRecorrido(data[0].paquete)
  } catch {
    error.value = 'No pudimos consultar tus reservas. Revisa tu conexión e inténtalo de nuevo.'
  } finally {
    cargando.value = false
  }
})

onBeforeUnmount(() => {
  detenerUbicacion()
  mapa?.remove()
  mapa = null
})
</script>

<template>
  <div class="min-h-screen bg-[#0a1a0f] px-6 pb-12 pt-28 text-white md:px-10">
    <main class="mx-auto max-w-5xl">
      <router-link to="/panel/reservas" class="mb-4 inline-flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-emerald-400/70 hover:text-emerald-300 focus:outline-none focus:ring-2 focus:ring-emerald-300">← Mis reservas</router-link>
      <h1 class="text-4xl font-black tracking-tight sm:text-5xl">Recorrido de <span class="text-emerald-500">hoy</span></h1>
      <p class="mt-2 text-sm text-white/60">Disponible el día de realización de los paquetes que compraste y están confirmados.</p>

      <p v-if="cargando" class="mt-8 text-white/60" role="status">Cargando…</p>

      <p v-else-if="!habilitados.length && !error" class="mt-8 rounded-2xl border border-white/10 bg-white/5 p-6 text-sm text-white/70">
        Hoy no tienes un paquete confirmado para realizar. Cuando llegue la fecha de tu experiencia, el recorrido aparecerá aquí.
      </p>

      <p v-if="error" class="mt-8 rounded-2xl border border-rose-300/30 bg-rose-400/10 p-4 text-sm text-rose-100" role="alert">{{ error }}</p>

      <div v-if="habilitados.length" class="mt-8">
        <div v-if="habilitados.length > 1" class="mb-4 flex flex-wrap gap-2" role="group" aria-label="Paquetes de hoy">
          <button v-for="item in habilitados" :key="item.paquete" type="button" class="min-h-11 rounded-xl border px-4 text-sm font-bold focus:outline-none focus:ring-2 focus:ring-emerald-300" :class="seleccionado === item.paquete ? 'border-emerald-400 bg-emerald-500/20' : 'border-white/20 hover:bg-white/10'" :aria-pressed="seleccionado === item.paquete" @click="cargarRecorrido(item.paquete)">{{ item.nombre }}</button>
        </div>

        <div v-if="datos" class="mb-4">
          <h2 class="text-xl font-black">{{ datos.nombre_paquete }}</h2>
          <p class="text-sm text-white/60">{{ formatoFecha(datos.fecha) }}<template v-if="datos.disponible"> · {{ datos.distancia_km }} km</template></p>
          <p v-if="!datos.disponible" class="mt-3 rounded-xl border border-amber-300/25 bg-amber-300/10 p-3 text-sm text-amber-100">La agencia aún no ha publicado el recorrido de este paquete.</p>
        </div>
      </div>

      <label v-if="habilitados.length" class="mb-3 inline-flex min-h-11 cursor-pointer items-center gap-3 text-sm font-semibold">
        <input v-model="verMiUbicacion" type="checkbox" class="h-5 w-5 accent-emerald-500" />
        Mostrar mi ubicación en el mapa
      </label>
      <p v-if="avisoUbicacion" class="mb-3 text-sm text-amber-200" role="alert">{{ avisoUbicacion }}</p>

      <div ref="mapaEl" class="h-[26rem] w-full overflow-hidden rounded-3xl border border-white/10" :class="{ 'hidden': !habilitados.length }" aria-label="Mapa del recorrido"></div>
    </main>
  </div>
</template>
