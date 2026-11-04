<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import clienteAxios from '@/api/axios'
import { useMiUbicacion } from '@/composables/recorridos/useMiUbicacion'
import { useGrupo } from '@/composables/recorridos/useGrupo'
import { useNotificacion } from '@/composables/useNotificacion'
import { OPCIONES_MOSAICOS, URL_MOSAICOS } from '@/config/mapa'
import { guardadosParaHoy, guardarPaquete, hoyEnColombia, obtenerGuardado } from '@/composables/recorridos/almacenOffline'

const route = useRoute()
const { mostrarNotificacion } = useNotificacion()

const cargando = ref(true)
const habilitados = ref([])
const seleccionado = ref(null)
const datos = ref(null)
const error = ref('')
// Sin conexión se usa la copia guardada en el dispositivo al abrir «Mis reservas» con internet.
const sinConexion = ref(false)
const guardadoEl = ref('')
// La ubicación se muestra por defecto: la persona llega aquí desde su reserva para orientarse en el recorrido.
const mostrarUbicacion = ref(true)
const mapaEl = ref(null)

const { posicion: miPosicion, estado: estadoUbicacion, detalle: detalleUbicacion, iniciar: iniciarUbicacion, detener: detenerUbicacion } = useMiUbicacion()

const { compartiendo, personas, error: errorGrupo, preparar: prepararGrupo, alternar: alternarGrupo } = useGrupo(() => miPosicion.value)
// Compartir es voluntario: la casilla empieza apagada y solo se enciende si la persona ya lo eligió hoy.
const compartirActivo = computed({
  get: () => compartiendo.value,
  set: (activo) => alternarGrupo(activo),
})

let mapa = null
let capaPersonas = null
let capa = null
let marcadorYo = null
let circuloYo = null
let encuadradoInicial = false
let siguiendo = true

const formatoFecha = (valor) => new Date(`${valor}T12:00:00`).toLocaleDateString('es-CO', { dateStyle: 'long' })

// Cada elemento del mapa tiene su propio color: el recorrido es verde, el inicio verde y el final rojo,
// el punto de encuentro ámbar, y la persona azul con un halo que pulsa.
const ICONO_YO = L.divIcon({
  className: 'marcador-yo',
  html: '<span class="marcador-yo__halo"></span><span class="marcador-yo__punto"></span>',
  iconSize: [30, 30],
  iconAnchor: [15, 15],
})
const PIN_PAQUETE = '<svg viewBox="0 0 24 32" width="34" height="44" aria-hidden="true"><path d="M12 0C5.4 0 0 5.2 0 11.7 0 20.5 12 32 12 32s12-11.5 12-20.3C24 5.2 18.6 0 12 0z" fill="#f59e0b" stroke="#fff" stroke-width="1.5"/><circle cx="12" cy="11.5" r="4.5" fill="#fff"/></svg>'

const distanciaM = (a, b) => {
  const rad = (g) => (g * Math.PI) / 180
  const h = Math.sin(rad(b[0] - a[0]) / 2) ** 2
    + Math.cos(rad(a[0])) * Math.cos(rad(b[0])) * Math.sin(rad(b[1] - a[1]) / 2) ** 2
  return 2 * 6371000 * Math.asin(Math.sqrt(h))
}

const puntoDeEncuentro = computed(() => {
  const ubicacion = datos.value?.ubicacion_paquete
  return ubicacion ? [ubicacion.latitud, ubicacion.longitud] : null
})

const textoDistancia = computed(() => {
  if (!puntoDeEncuentro.value || !miPosicion.value) return ''
  const metros = distanciaM([miPosicion.value.lat, miPosicion.value.lng], puntoDeEncuentro.value)
  if (metros < 100) return 'Estás en el punto de encuentro'
  return metros < 1000 ? `A ${Math.round(metros)} m del punto de encuentro` : `A ${(metros / 1000).toFixed(1)} km del punto de encuentro`
})

const textoUbicacion = computed(() => ({
  buscando: 'Buscando tu ubicación… Acepta el permiso de ubicación si el navegador lo pide.',
  activa: `Tu ubicación está activa · precisión de ${miPosicion.value?.precision ?? '—'} m.`,
  denegada: detalleUbicacion.value || 'El permiso de ubicación está denegado.',
  sin_gps: detalleUbicacion.value || 'No se puede obtener la ubicación. Comprueba que el GPS esté activado.',
  no_disponible: 'Este navegador no permite usar la ubicación aquí. Se necesita una conexión segura (https).',
}[estadoUbicacion.value]))

// Encuadra a la vez el recorrido, el punto de encuentro y la persona.
const encuadrar = () => {
  if (!mapa) return
  const puntos = [...(datos.value?.puntos || [])]
  if (puntoDeEncuentro.value) puntos.push(puntoDeEncuentro.value)
  if (miPosicion.value && mostrarUbicacion.value) puntos.push([miPosicion.value.lat, miPosicion.value.lng])
  if (puntos.length > 1) mapa.fitBounds(L.latLngBounds(puntos), { padding: [40, 40], maxZoom: 17 })
  else if (puntos.length === 1) mapa.setView(puntos[0], 17)
}

const dibujar = () => {
  if (!mapa) return
  mapa.invalidateSize()
  capa.clearLayers()
  const puntos = datos.value?.disponible ? datos.value.puntos : []
  if (puntos.length > 1) {
    L.polyline(puntos, { color: '#ffffff', weight: 10, opacity: 0.9, lineCap: 'round', lineJoin: 'round' }).addTo(capa)
    L.polyline(puntos, { color: '#059669', weight: 6, lineCap: 'round', lineJoin: 'round' }).addTo(capa)
    L.circleMarker(puntos[0], { radius: 7, color: '#fff', weight: 2, fillColor: '#16a34a', fillOpacity: 1 }).bindTooltip('Inicio del recorrido').addTo(capa)
    L.circleMarker(puntos.at(-1), { radius: 7, color: '#fff', weight: 2, fillColor: '#dc2626', fillOpacity: 1 }).bindTooltip('Final del recorrido').addTo(capa)
  }
  if (puntoDeEncuentro.value) {
    L.marker(puntoDeEncuentro.value, { icon: L.divIcon({ className: '', html: PIN_PAQUETE, iconSize: [34, 44], iconAnchor: [17, 44] }), keyboard: false })
      .bindTooltip(`Punto de encuentro: ${datos.value.nombre_paquete}`)
      .addTo(capa)
  }
  encuadrar()
}

const haceCuanto = (segundos) => (segundos < 60 ? 'ahora mismo' : `hace ${Math.round(segundos / 60)} min`)

// El contenido de la tarjeta se arma con nodos de texto: el nombre lo escribe otra persona y nunca se interpreta como HTML.
const contenidoPersona = (persona) => {
  const caja = document.createElement('div')
  caja.className = 'persona-popup'
  const nombre = document.createElement('strong')
  nombre.textContent = persona.nombre
  const cuando = document.createElement('span')
  cuando.textContent = `Ubicación ${haceCuanto(persona.hace_segundos)}`
  const enlace = document.createElement('a')
  enlace.href = `/perfil/${persona.id}?tipo=turista`
  enlace.target = '_blank'
  enlace.rel = 'noopener'
  enlace.textContent = 'Ver perfil'
  caja.append(nombre, cuando, enlace)
  return caja
}

// Pin de ubicación con la foto de la persona (o su inicial) dentro de la cabeza del pin.
const iconoPin = (persona) => {
  const pin = document.createElement('span')
  pin.className = 'pin-persona'
  const cara = document.createElement('span')
  cara.className = 'pin-persona__cara'
  if (persona.foto) {
    const foto = document.createElement('img')
    foto.src = persona.foto
    foto.alt = ''
    cara.append(foto)
  } else {
    cara.textContent = persona.nombre.charAt(0).toUpperCase()
  }
  pin.append(cara)
  return L.divIcon({ className: '', html: pin, iconSize: [44, 52], iconAnchor: [22, 50], popupAnchor: [0, -50] })
}

let personaElegida = null
let pinPersona = null

const quitarPin = () => {
  pinPersona?.remove()
  pinPersona = null
}

// Al tocar el punto de otra persona aparece su pin con la tarjeta de su perfil.
const mostrarPin = (persona) => {
  quitarPin()
  personaElegida = persona.id
  pinPersona = L.marker([persona.latitud, persona.longitud], { icon: iconoPin(persona), zIndexOffset: 2000, keyboard: false })
    .bindPopup(() => contenidoPersona(persona), { offset: [0, 0] })
    .addTo(mapa)
    .openPopup()
  pinPersona.on('popupclose', () => { if (pinPersona) { quitarPin(); personaElegida = null } })
}

// Las demás personas se dibujan como círculos morados, distintos del azul de «tú».
const dibujarPersonas = () => {
  if (!mapa || !capaPersonas) return
  capaPersonas.clearLayers()
  for (const persona of personas.value) {
    L.circleMarker([persona.latitud, persona.longitud], { radius: 11, color: '#fff', weight: 3, fillColor: '#9333ea', fillOpacity: 1 })
      .on('click', () => mostrarPin(persona))
      .addTo(capaPersonas)
  }
  // Si hay un pin abierto, sigue a la persona; si dejó de compartir, desaparece.
  const elegida = personas.value.find(persona => persona.id === personaElegida)
  if (!elegida) {
    if (personaElegida !== null) { quitarPin(); personaElegida = null }
  } else if (pinPersona) {
    pinPersona.setLatLng([elegida.latitud, elegida.longitud])
  }
}

watch(personas, dibujarPersonas)

const quitarMiMarcador = () => {
  marcadorYo?.remove()
  circuloYo?.remove()
  marcadorYo = null
  circuloYo = null
}

// El marcador de la persona se actualiza en vivo con cada lectura del GPS.
const dibujarYo = () => {
  if (!mapa || !mostrarUbicacion.value || !miPosicion.value) return
  const punto = [miPosicion.value.lat, miPosicion.value.lng]
  if (!marcadorYo) {
    circuloYo = L.circle(punto, { radius: miPosicion.value.precision, color: '#2563eb', weight: 1, fillColor: '#2563eb', fillOpacity: 0.12, interactive: false }).addTo(mapa)
    marcadorYo = L.marker(punto, { icon: ICONO_YO, zIndexOffset: 1000, keyboard: false })
      .bindTooltip('Estás aquí', { permanent: true, direction: 'top', offset: [0, -16], className: 'etiqueta-yo' })
      .addTo(mapa)
  } else {
    marcadorYo.setLatLng(punto)
    circuloYo.setLatLng(punto).setRadius(miPosicion.value.precision)
  }
  if (!encuadradoInicial) {
    encuadradoInicial = true
    encuadrar()
  } else if (siguiendo) {
    mapa.panTo(punto)
  }
}

watch(miPosicion, dibujarYo)

watch(mostrarUbicacion, (activa) => {
  if (activa) {
    encuadradoInicial = false
    iniciarUbicacion()
  } else {
    detenerUbicacion()
    quitarMiMarcador()
  }
})

watch(estadoUbicacion, (estado) => {
  if (estado === 'denegada') mostrarNotificacion('No se pudo usar tu ubicación: el permiso está denegado. Lee el mensaje bajo el mapa.', 'aviso', 7000)
  else if (estado === 'sin_gps') mostrarNotificacion('No se puede obtener tu ubicación. Lee el mensaje bajo el mapa.', 'aviso', 7000)
})

const centrarEnMi = () => {
  siguiendo = true
  if (mapa && miPosicion.value) mapa.setView([miPosicion.value.lat, miPosicion.value.lng], Math.max(mapa.getZoom(), 17))
}

const aDatos = (guardado) => ({
  disponible: guardado.disponible,
  puntos: guardado.puntos,
  distancia_km: guardado.distancia_km,
  nombre_paquete: guardado.nombre,
  fecha: guardado.fecha,
  ubicacion_paquete: guardado.ubicacion_paquete,
})

// Sin internet solo se muestra lo guardado para HOY; el servidor no puede validar la compra, pero lo guardado
// salió de una reserva confirmada de este turista y el recorrido publicado es público.
const mostrarCopiaGuardada = (paquete) => {
  const guardado = obtenerGuardado(paquete)
  if (!guardado || guardado.fecha !== hoyEnColombia()) {
    error.value = 'Sin conexión: este mapa no está guardado en el dispositivo. Abre «Mis reservas» con internet, antes de salir, para guardarlo.'
    return
  }
  sinConexion.value = true
  guardadoEl.value = new Date(guardado.guardado_en).toLocaleString('es-CO', { dateStyle: 'medium', timeStyle: 'short' })
  datos.value = aDatos(guardado)
}

const cargarRecorrido = async (paquete) => {
  seleccionado.value = paquete
  datos.value = null
  personas.value = []
  error.value = ''
  encuadradoInicial = false
  try {
    const { data } = await clienteAxios.get(`api/turista/paquetes/${paquete}/recorrido/`)
    datos.value = data
    // Si ya había una copia guardada, se renueva con lo último del servidor.
    const copia = obtenerGuardado(paquete)
    if (copia) {
      guardarPaquete({ ...copia, nombre: data.nombre_paquete, fecha: data.fecha, disponible: data.disponible, puntos: data.puntos || [], distancia_km: data.distancia_km || 0, ubicacion_paquete: data.ubicacion_paquete, guardado_en: new Date().toISOString() })
    }
  } catch (fallo) {
    if (!fallo.response) mostrarCopiaGuardada(paquete)
    else error.value = fallo.response?.data?.detail || 'No pudimos cargar el recorrido. Revisa tu conexión e inténtalo de nuevo.'
  }
  if (datos.value) {
    await nextTick()
    dibujar()
    dibujarYo()
    if (!sinConexion.value) prepararGrupo(paquete, datos.value.fecha)
  }
}

onMounted(async () => {
  await nextTick()
  // En móvil el zoom se hace con los dedos; los botones +/- solo estorbarían al resto de controles.
  mapa = L.map(mapaEl.value, { zoomControl: false }).setView([-4.2153, -69.9406], 12)
  if (window.matchMedia('(min-width: 640px)').matches) L.control.zoom({ position: 'topleft' }).addTo(mapa)
  L.tileLayer(URL_MOSAICOS, OPCIONES_MOSAICOS).addTo(mapa)
  capa = L.layerGroup().addTo(mapa)
  capaPersonas = L.layerGroup().addTo(mapa)
  // Si la persona arrastra el mapa, deja de seguirla hasta que pulse «Mi ubicación».
  mapa.on('dragstart', () => { siguiendo = false })
  if (mostrarUbicacion.value) iniciarUbicacion()
  try {
    const { data } = await clienteAxios.get('api/turista/recorridos-habilitados/')
    habilitados.value = data
    // Desde la reserva se llega con ?paquete=<id> y se abre directamente el mapa de ese paquete.
    const pedido = Number(route.query.paquete)
    const elegido = data.find(item => item.paquete === pedido) || data[0]
    if (elegido) await cargarRecorrido(elegido.paquete)
  } catch (fallo) {
    if (!fallo.response) {
      // Sin conexión: se usan los mapas guardados para hoy.
      sinConexion.value = true
      habilitados.value = guardadosParaHoy().map(item => ({ paquete: item.paquete, nombre: item.nombre, fecha: item.fecha, tiene_recorrido: item.disponible }))
      const elegido = habilitados.value.find(item => item.paquete === Number(route.query.paquete)) || habilitados.value[0]
      if (elegido) await cargarRecorrido(elegido.paquete)
      else error.value = 'Sin conexión: no hay un mapa guardado para hoy en este dispositivo. Abre «Mis reservas» con internet, antes de salir, para guardarlo.'
    } else {
      error.value = 'No pudimos consultar tus reservas. Revisa tu conexión e inténtalo de nuevo.'
    }
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
  <div class="min-h-screen bg-[#0a1a0f] px-4 pb-10 pt-20 text-white sm:px-6 sm:pt-24 md:px-10">
    <main class="mx-auto max-w-5xl">
      <router-link to="/panel/reservas" class="mb-3 inline-flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-emerald-400/70 hover:text-emerald-300 focus:outline-none focus:ring-2 focus:ring-emerald-300">← Mis reservas</router-link>
      <h1 class="text-2xl font-black tracking-tight sm:text-5xl">Recorrido de <span class="text-emerald-500">hoy</span></h1>
      <p class="mt-2 hidden text-sm text-white/60 sm:block">Disponible el día de realización de los paquetes que compraste y están confirmados.</p>

      <p v-if="sinConexion" class="mt-3 rounded-xl border border-amber-300/30 bg-amber-300/10 p-3 text-xs text-amber-100" role="status">
        Sin conexión: estás viendo el recorrido guardado en este dispositivo<span v-if="guardadoEl"> (guardado el {{ guardadoEl }})</span>. Tu ubicación sigue funcionando con el GPS.
      </p>

      <p v-if="cargando" class="mt-6 text-white/60" role="status">Cargando…</p>

      <p v-else-if="!habilitados.length && !error" class="mt-6 rounded-2xl border border-white/10 bg-white/5 p-6 text-sm text-white/70">
        Hoy no tienes un paquete confirmado para realizar. Cuando llegue la fecha de tu experiencia, el recorrido aparecerá aquí.
      </p>

      <p v-if="error" class="mt-6 rounded-2xl border border-rose-300/30 bg-rose-400/10 p-4 text-sm text-rose-100" role="alert">{{ error }}</p>

      <div v-if="habilitados.length" class="mt-3 sm:mt-5">
        <div v-if="habilitados.length > 1" class="mb-4 flex flex-wrap gap-2" role="group" aria-label="Paquetes de hoy">
          <button v-for="item in habilitados" :key="item.paquete" type="button" class="min-h-11 rounded-xl border px-4 text-sm font-bold focus:outline-none focus:ring-2 focus:ring-emerald-300" :class="seleccionado === item.paquete ? 'border-emerald-400 bg-emerald-500/20' : 'border-white/20 hover:bg-white/10'" :aria-pressed="seleccionado === item.paquete" @click="cargarRecorrido(item.paquete)">{{ item.nombre }}</button>
        </div>

        <div v-if="datos" class="mb-3">
          <h2 class="text-xl font-black">{{ datos.nombre_paquete }}</h2>
          <p class="text-sm text-white/60">{{ formatoFecha(datos.fecha) }}<template v-if="datos.disponible"> · recorrido de {{ datos.distancia_km }} km</template></p>
          <p v-if="!datos.disponible" class="mt-2 rounded-xl border border-amber-300/25 bg-amber-300/10 p-3 text-xs text-amber-100 sm:text-sm">La agencia aún no publicó el recorrido. Mientras tanto ves el punto de encuentro y dónde estás.</p>
        </div>
      </div>

      <div v-show="habilitados.length" class="relative">
        <div ref="mapaEl" class="h-[62dvh] min-h-[22rem] w-full overflow-hidden rounded-3xl border border-white/10 sm:h-[30rem]" aria-label="Mapa del recorrido"></div>

        <!-- Estado sobre el mapa -->
        <div class="pointer-events-none absolute left-3 right-16 top-3 z-[1000] flex flex-col items-start gap-2 sm:left-14">
          <span v-if="textoDistancia" class="pointer-events-auto rounded-full bg-black/75 px-3 py-1.5 text-xs font-bold text-amber-200 backdrop-blur">{{ textoDistancia }}</span>
        </div>
        <button type="button" class="absolute right-3 top-3 z-[1000] flex h-12 w-12 items-center justify-center rounded-full bg-white text-sky-700 shadow-lg outline-none ring-1 ring-black/10 hover:bg-sky-50 focus-visible:ring-2 focus-visible:ring-sky-500 disabled:opacity-50" :disabled="!miPosicion || !mostrarUbicacion" aria-label="Centrar el mapa en mi ubicación" @click="centrarEnMi">
          <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.2" aria-hidden="true"><circle cx="12" cy="12" r="3.5"/><path stroke-linecap="round" d="M12 2v3m0 14v3M2 12h3m14 0h3"/><circle cx="12" cy="12" r="8"/></svg>
        </button>
      </div>

      <div v-if="habilitados.length" class="mt-3 space-y-3">
        <!-- Leyenda de colores -->
        <ul class="flex flex-wrap gap-x-5 gap-y-1.5 text-xs text-white/70" aria-label="Leyenda del mapa">
          <li class="flex items-center gap-2"><span class="inline-block h-3 w-3 rounded-full bg-blue-600 ring-2 ring-white"></span>Tú (estás aquí)</li>
          <li class="flex items-center gap-2"><span class="inline-block h-1.5 w-6 rounded bg-emerald-600"></span>Recorrido</li>
          <li class="flex items-center gap-2"><span class="inline-block h-3 w-3 rounded-full bg-green-600 ring-2 ring-white"></span>Inicio</li>
          <li class="flex items-center gap-2"><span class="inline-block h-3 w-3 rounded-full bg-red-600 ring-2 ring-white"></span>Final</li>
          <li class="flex items-center gap-2"><span class="inline-block h-3 w-3 rounded-full bg-amber-500 ring-2 ring-white"></span>Punto de encuentro</li>
          <li class="flex items-center gap-2"><span class="inline-block h-3 w-3 rounded-full bg-purple-600 ring-2 ring-white"></span>Otras personas</li>
        </ul>

        <label class="inline-flex min-h-11 cursor-pointer items-center gap-3 text-sm font-semibold">
          <input v-model="mostrarUbicacion" type="checkbox" class="h-5 w-5 accent-blue-500" />
          Mostrar mi ubicación en el mapa
        </label>

        <div v-if="!sinConexion" class="rounded-xl border border-violet-300/25 bg-violet-400/10 p-3">
          <label class="flex min-h-11 cursor-pointer items-center gap-3 text-sm font-semibold">
            <input v-model="compartirActivo" type="checkbox" class="h-5 w-5 accent-violet-500" :disabled="!mostrarUbicacion" />
            Ver y compartir mi ubicación con quienes hacen este paquete hoy
          </label>
          <p class="mt-1 text-xs text-white/60">Es voluntario y recíproco: solo ves a quien también comparte, y solo ven tu nombre, tu foto y tu posición mientras esté activo. Se borra al apagarlo o al cerrar el mapa.</p>
          <p v-if="compartiendo" class="mt-2 text-xs font-bold text-violet-200" role="status">{{ personas.length ? `Ves a ${personas.length} ${personas.length === 1 ? 'persona' : 'personas'}. Toca un círculo morado para ver su información.` : 'Aún no hay otras personas compartiendo. Aparecerán aquí.' }}</p>
          <p v-if="errorGrupo" class="mt-2 text-xs text-amber-200" role="alert">{{ errorGrupo }}</p>
        </div>

        <p v-if="mostrarUbicacion && estadoUbicacion !== 'activa'" class="rounded-xl border p-3 text-xs" :class="estadoUbicacion === 'buscando' ? 'border-white/15 bg-white/5 text-white/70' : 'border-amber-300/30 bg-amber-300/10 text-amber-100'" role="status">
          {{ textoUbicacion }}
          <button v-if="estadoUbicacion === 'denegada' || estadoUbicacion === 'sin_gps'" type="button" class="ml-1 font-black underline" @click="iniciarUbicacion">Reintentar</button>
        </p>
        <p v-else-if="mostrarUbicacion" class="text-xs text-sky-200" role="status">{{ textoUbicacion }}</p>
      </div>
    </main>
  </div>
</template>

<style>
/* Marcador de la persona: punto azul con un halo que pulsa (no es scoped porque Leaflet crea este HTML fuera del componente). */
.marcador-yo { position: relative; }
.marcador-yo__halo { position: absolute; inset: 0; border-radius: 9999px; background: rgba(37, 99, 235, 0.35); animation: pulso-yo 1.8s ease-out infinite; }
.marcador-yo__punto { position: absolute; inset: 6px; border-radius: 9999px; background: #2563eb; border: 3px solid #fff; box-shadow: 0 0 0 2px #2563eb, 0 2px 8px rgba(0, 0, 0, 0.5); }
.etiqueta-yo { background: #2563eb; color: #fff; border: 0; border-radius: 9999px; padding: 2px 10px; font-weight: 800; font-size: 12px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4); }
.etiqueta-yo::before { border-top-color: #2563eb !important; }
@keyframes pulso-yo { 0% { transform: scale(0.6); opacity: 1; } 100% { transform: scale(2.2); opacity: 0; } }
@media (prefers-reduced-motion: reduce) { .marcador-yo__halo { animation: none; opacity: 0.5; } }
.persona-popup { display: flex; flex-direction: column; gap: 2px; min-width: 8rem; font-size: 13px; }
.persona-popup span { color: #4b5563; }
.persona-popup a { margin-top: 4px; font-weight: 800; color: #7e22ce; text-decoration: underline; }
/* Pin de ubicación de otra persona: gota morada con su foto dentro. */
.pin-persona { position: relative; display: block; width: 44px; height: 52px; }
.pin-persona::before { content: ''; position: absolute; left: 2px; top: 0; width: 40px; height: 40px; background: #9333ea; border: 3px solid #fff; border-radius: 50% 50% 50% 0; transform: rotate(-45deg); transform-origin: 50% 50%; box-shadow: 0 3px 10px rgba(0, 0, 0, 0.45); }
.pin-persona__cara { position: absolute; left: 8px; top: 6px; width: 28px; height: 28px; border-radius: 9999px; overflow: hidden; background: #fff; color: #7e22ce; font-weight: 900; font-size: 15px; display: flex; align-items: center; justify-content: center; }
.pin-persona__cara img { width: 100%; height: 100%; object-fit: cover; }
</style>
