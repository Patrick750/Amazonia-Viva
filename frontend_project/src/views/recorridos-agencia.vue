<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { onBeforeRouteLeave } from 'vue-router'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import clienteAxios from '@/api/axios'
import { paquetes as pedirPaquetes } from '@/composables/gestion-tours/paquetes'
import { PRECISION_MAXIMA_M, useGrabacion } from '@/composables/recorridos/useGrabacion'
import { useMiUbicacion } from '@/composables/recorridos/useMiUbicacion'
import { useNotificacion } from '@/composables/useNotificacion'
import { eliminarRecorrido as borrarLocal, listarRecorridos } from '@/composables/recorridos/almacenLocal'
import { reintentarRecorrido } from '@/composables/recorridos/sincronizacion'

const CLAVE_PAQUETES = 'recorridos_paquetes'

const misPaquetes = ref([])
const paqueteId = ref('')
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
    if (data[0]?.limite_m) limiteM.value = data[0].limite_m
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
    porId.set(local.id_cliente, { ...base, local: true, completo: local.completo, creadoSync: local.creado_sync, errorLocal: local.error })
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

const puedePublicar = (item) => !!item.finalizado_en && (!item.local || item.completo) && !item.errorLocal && item.coincide_con_paquete !== false

const cambiarPublicacion = async (item, publicar) => {
  mensaje.value = ''
  try {
    if (publicar) await clienteAxios.post(`api/recorridos/${item.id_cliente}/publicar/`)
    else await clienteAxios.delete(`api/recorridos/${item.id_cliente}/publicar/`)
    mensaje.value = publicar ? 'Recorrido publicado: ya se muestra en el mapa del paquete.' : 'Recorrido retirado del paquete.'
    mostrarNotificacion(mensaje.value, 'exito')
    await cargarLista()
  } catch (error) {
    mensaje.value = error.response?.data?.detail || 'No se pudo cambiar la publicación. Revisa tu conexión e inténtalo de nuevo.'
    mostrarNotificacion(mensaje.value, 'error', 8000)
  }
}

const reintentar = async (item) => {
  await reintentarRecorrido(item.id_cliente)
  await cargarLista()
}

// --- Eliminar ---
const porEliminar = ref(null)
const eliminando = ref(false)
const errorEliminar = ref('')
const botonCancelar = ref(null)

// La grabación en curso no se puede eliminar: primero hay que finalizarla.
const esActivo = (item) => recorrido.value?.id_cliente === item.id_cliente

const pedirEliminar = async (item) => {
  errorEliminar.value = ''
  porEliminar.value = item
  await nextTick()
  botonCancelar.value?.focus()
}

const cerrarEliminar = () => {
  if (!eliminando.value) porEliminar.value = null
}

const eliminarConfirmado = async () => {
  const item = porEliminar.value
  if (!item) return
  eliminando.value = true
  errorEliminar.value = ''
  try {
    // Un recorrido que nunca llegó al servidor solo existe en este dispositivo.
    const enServidor = remotos.value.some(remoto => remoto.id_cliente === item.id_cliente) || item.creadoSync
    if (enServidor) {
      try {
        await clienteAxios.delete(`api/recorridos/${item.id_cliente}/`)
      } catch (error) {
        if (error.response?.status !== 404) throw error // 404: ya no existe en el servidor
      }
    }
    if (item.local) await borrarLocal(item.id_cliente)
    porEliminar.value = null
    mensaje.value = 'Recorrido eliminado.'
    await cargarLista()
  } catch (error) {
    errorEliminar.value = !error.response
      ? 'Sin conexión: conéctate para eliminar un recorrido que ya se envió al servidor.'
      : error.response.data?.detail || 'No se pudo eliminar el recorrido. Inténtalo de nuevo.'
  } finally {
    eliminando.value = false
  }
}

const iniciar = () => {
  mensaje.value = ''
  const paquete = paqueteDelMapa.value
  if (paquete && !ubicacionPaquete.value) {
    mostrarNotificacion('Este paquete no tiene ubicación registrada, así que no se podrá comprobar que el recorrido coincide con él.', 'aviso', 7000)
  } else if (lejosDelPaquete.value) {
    // Se pide confirmación: grabar lejos del paquete casi siempre es un error de paquete o de lugar.
    alertaLejos.value = { nombre: paquete.nombre, texto: textoDistanciaCorta.value }
    nextTick(() => botonCambiarPaquete.value?.focus())
    return
  }
  return comenzarGrabacion()
}

const confirmarInicioLejos = () => {
  alertaLejos.value = null
  return comenzarGrabacion()
}

const comenzarGrabacion = async () => {
  // El recorrido se identifica por su paquete: no lleva un nombre propio.
  await grabacion.iniciar(Number(paqueteId.value))
  await cargarLista()
}

const finalizar = async () => {
  const cercania = distanciaMinimaDelTrazoM()
  await grabacion.finalizar()
  if (cercania !== null && cercania > limiteM.value) {
    mostrarNotificacion(`El recorrido que grabaste queda a ${(cercania / 1000).toFixed(1)} km de la ubicación del paquete: no se podrá publicar. Revisa el paquete elegido.`, 'aviso', 9000)
  }
  mensaje.value = enLinea.value
    ? 'Recorrido finalizado. Ya puedes publicarlo desde la lista cuando termine de sincronizarse.'
    : 'Recorrido finalizado y guardado en este dispositivo. Se enviará cuando recuperes la conexión.'
  await cargarLista()
}

// --- Mapa ---
// En móvil el mapa ocupa toda la pantalla bajo la barra superior; la lista de recorridos va en otra vista.
const vistaMovil = ref('mapa') // mapa | lista
const alturaCabecera = ref(70)
const seguir = ref(true)

let mapa = null
let lineaBorde = null
let linea = null
let marcador = null
let circulo = null
let centradoInicial = false
let observadorMapa = null
let observadorCabecera = null

const medirCabecera = () => { alturaCabecera.value = document.querySelector('header')?.offsetHeight || 70 }

const iniciarMapa = () => {
  if (!mapaEl.value || mapa) return
  mapa = L.map(mapaEl.value, { zoomControl: false }).setView([-4.2153, -69.9406], 13)
  // En móvil se hace zoom con los dedos; los botones +/- solo estorbarían a los controles.
  if (window.matchMedia('(min-width: 1024px)').matches) L.control.zoom({ position: 'topleft' }).addTo(mapa)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '&copy; OpenStreetMap contributors' }).addTo(mapa)
  // Borde blanco bajo la línea verde para que el trazo se distinga sobre cualquier fondo.
  lineaBorde = L.polyline([], { color: '#ffffff', weight: 10, opacity: 0.9, lineCap: 'round', lineJoin: 'round' }).addTo(mapa)
  linea = L.polyline([], { color: '#059669', weight: 6, lineCap: 'round', lineJoin: 'round' }).addTo(mapa)
  // Si la persona arrastra el mapa, deja de seguirla hasta que pulse «Mi ubicación».
  mapa.on('dragstart', () => { seguir.value = false })
  observadorMapa = new ResizeObserver(() => mapa?.invalidateSize())
  observadorMapa.observe(mapaEl.value)
}

watch(trazado, (puntos) => {
  if (!mapa) return
  lineaBorde.setLatLngs(puntos)
  linea.setLatLngs(puntos)
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
  } else if (seguir.value) {
    mapa.panTo(punto)
  }
})

const centrarEnMiUbicacion = () => {
  seguir.value = true
  if (mapa && miPosicion.value) mapa.setView([miPosicion.value.lat, miPosicion.value.lng], Math.max(mapa.getZoom(), 17))
}

const precisionBaja = computed(() => !!miPosicion.value && miPosicion.value.precision > PRECISION_MAXIMA_M)

// --- Ubicación del paquete y alertas ---
const { mostrarNotificacion } = useNotificacion()
// El servidor informa el límite real con cada recorrido; este es el valor por defecto.
const limiteM = ref(3000)

const distanciaM = (a, b) => {
  const rad = (g) => (g * Math.PI) / 180
  const h = Math.sin(rad(b[0] - a[0]) / 2) ** 2
    + Math.cos(rad(a[0])) * Math.cos(rad(b[0])) * Math.sin(rad(b[1] - a[1]) / 2) ** 2
  return 2 * 6371000 * Math.asin(Math.sqrt(h))
}

// Paquete que se muestra en el mapa: el que se está grabando o, si no, el elegido en la lista.
const paqueteDelMapa = computed(() => {
  const id = estado.value !== 'inactivo' ? recorrido.value?.paquete : Number(paqueteId.value)
  return misPaquetes.value.find(paquete => paquete.id === id) || null
})
const ubicacionPaquete = computed(() => {
  const paquete = paqueteDelMapa.value
  return paquete && paquete.latitud != null && paquete.longitud != null ? [Number(paquete.latitud), Number(paquete.longitud)] : null
})
const distanciaAlPaqueteM = computed(() => (
  ubicacionPaquete.value && miPosicion.value ? distanciaM([miPosicion.value.lat, miPosicion.value.lng], ubicacionPaquete.value) : null
))
const textoDistanciaCorta = computed(() => {
  const metros = distanciaAlPaqueteM.value
  if (metros === null) return ''
  return metros < 1000 ? `${Math.round(metros)} m` : `${(metros / 1000).toFixed(1)} km`
})
const textoDistancia = computed(() => (
  distanciaAlPaqueteM.value === null ? '' : distanciaAlPaqueteM.value < 150 ? 'Estás en el punto del paquete' : `A ${textoDistanciaCorta.value} del punto del paquete`
))
const lejosDelPaquete = computed(() => distanciaAlPaqueteM.value !== null && distanciaAlPaqueteM.value > limiteM.value)

// Menor distancia entre lo grabado y la ubicación del paquete (null si no se puede calcular).
const distanciaMinimaDelTrazoM = () => {
  if (!ubicacionPaquete.value || !trazado.value.length) return null
  return Math.min(...trazado.value.map(punto => distanciaM(punto, ubicacionPaquete.value)))
}

const alertaLejos = ref(null)
const botonCambiarPaquete = ref(null)

// Pin ámbar con el punto de encuentro del paquete elegido.
const PIN_HTML = '<svg viewBox="0 0 24 32" width="34" height="44" aria-hidden="true"><path d="M12 0C5.4 0 0 5.2 0 11.7 0 20.5 12 32 12 32s12-11.5 12-20.3C24 5.2 18.6 0 12 0z" fill="#f59e0b" stroke="#fff" stroke-width="1.5"/><circle cx="12" cy="11.5" r="4.5" fill="#fff"/></svg>'
let pin = null
const dibujarPin = () => {
  if (!mapa) return
  pin?.remove()
  pin = null
  if (!ubicacionPaquete.value) return
  pin = L.marker(ubicacionPaquete.value, { icon: L.divIcon({ className: '', html: PIN_HTML, iconSize: [34, 44], iconAnchor: [17, 44] }), keyboard: false })
    .bindTooltip(`Punto del paquete: ${paqueteDelMapa.value.nombre}`)
    .addTo(mapa)
}

// Al elegir un paquete se enmarcan a la vez la persona y el punto del paquete.
watch(() => ubicacionPaquete.value?.join(','), () => {
  dibujarPin()
  if (!mapa || !ubicacionPaquete.value || estado.value !== 'inactivo') return
  seguir.value = false
  if (miPosicion.value) mapa.fitBounds(L.latLngBounds([[miPosicion.value.lat, miPosicion.value.lng], ubicacionPaquete.value]), { padding: [60, 60], maxZoom: 17 })
  else mapa.setView(ubicacionPaquete.value, 15)
})

// Alertas de eventos que la persona necesita saber mientras marca el recorrido.
watch(enLinea, (conectado) => {
  if (conectado) mostrarNotificacion('Conexión recuperada. Enviando los puntos guardados…', 'exito')
  else mostrarNotificacion('Sin conexión: sigues marcando el recorrido y se enviará cuando vuelva internet.', 'aviso', 6000)
})
let huboPendientes = false
watch(pendientes, (cantidad) => { if (cantidad > 0) huboPendientes = true })
watch(sincronizando, (ahora, antes) => {
  if (antes && !ahora && huboPendientes && pendientes.value === 0) {
    huboPendientes = false
    mostrarNotificacion('Todos los puntos del recorrido se enviaron al servidor.', 'exito')
  }
})
watch(precisionBaja, (baja) => {
  if (baja && estado.value === 'grabando') mostrarNotificacion(`Señal GPS débil (peor de ${PRECISION_MAXIMA_M} m): no se están marcando puntos. Sal a un lugar abierto.`, 'aviso', 7000)
})
watch(estadoUbicacion, (nuevo) => {
  if (nuevo === 'denegada') mostrarNotificacion('El permiso de ubicación está denegado: no se puede marcar el recorrido.', 'error', 8000)
  else if (nuevo === 'sin_gps') mostrarNotificacion('No se puede obtener la ubicación. Comprueba que el GPS esté activado.', 'aviso', 6000)
})

// Al empezar a grabar se muestra el mapa y se vuelve a seguir a la persona.
watch(estado, (nuevo) => {
  if (nuevo === 'grabando') {
    vistaMovil.value = 'mapa'
    seguir.value = true
  }
})

onMounted(async () => {
  await nextTick()
  medirCabecera()
  const cabecera = document.querySelector('header')
  if (cabecera) {
    observadorCabecera = new ResizeObserver(medirCabecera)
    observadorCabecera.observe(cabecera)
  }
  iniciarMapa()
  dibujarPin()
  iniciarUbicacion()
  const cache = JSON.parse(localStorage.getItem(CLAVE_PAQUETES) || '[]')
  const traidos = await pedirPaquetes().catch(() => null)
  if (Array.isArray(traidos) && traidos.length) {
    misPaquetes.value = traidos.map(p => ({ id: p.id, nombre: p.nombre, latitud: p.latitud ?? null, longitud: p.longitud ?? null }))
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
  observadorMapa?.disconnect()
  observadorCabecera?.disconnect()
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
  <div class="min-h-screen bg-[#0a1a0f] text-white" :style="{ '--cab': alturaCabecera + 'px' }">
    <main class="mx-auto max-w-6xl p-6 md:p-10" :class="{ 'max-lg:p-0': vistaMovil === 'mapa' }">
      <header class="mb-8" :class="{ 'max-lg:hidden': vistaMovil === 'mapa' }">
        <router-link to="/panel/gestion-paquetes" class="mb-4 inline-flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-emerald-400/70 hover:text-emerald-300 focus:outline-none focus:ring-2 focus:ring-emerald-300">
          ← Volver a Gestión de Tours
        </router-link>
        <h1 class="text-4xl font-black tracking-tight sm:text-5xl">Recorridos <span class="text-emerald-500">GPS</span></h1>
        <p class="mt-2 text-sm text-white/60">Graba el trayecto real de un paquete, incluso sin internet, y publícalo para que se vea en su mapa.</p>
      </header>

      <p class="mb-6 rounded-2xl border border-amber-300/25 bg-amber-300/10 p-4 text-sm text-amber-100" :class="{ 'max-lg:hidden': vistaMovil === 'mapa' }">
        Mantén la pantalla encendida y esta aplicación abierta mientras grabas. Los navegadores pueden pausar el GPS cuando el teléfono se bloquea; la aplicación intenta evitar que la pantalla se apague, pero no puede garantizarlo en todos los dispositivos.
      </p>

      <div class="grid gap-6 lg:grid-cols-[22rem_1fr]">
        <!-- Controles: hoja inferior sobre el mapa en móvil, tarjeta lateral en escritorio -->
        <section
          class="rounded-3xl border border-white/10 bg-white/5 p-6"
          :class="vistaMovil === 'mapa'
            ? 'max-lg:fixed max-lg:inset-x-0 max-lg:bottom-0 max-lg:z-[45] max-lg:max-h-[50dvh] max-lg:overflow-y-auto max-lg:rounded-b-none max-lg:border-x-0 max-lg:border-b-0 max-lg:border-white/15 max-lg:bg-[#0f2318]/95 max-lg:p-4 max-lg:backdrop-blur'
            : 'max-lg:hidden'"
          aria-labelledby="titulo-grabacion"
        >
          <h2 id="titulo-grabacion" class="mb-4 text-lg font-black max-lg:sr-only">Grabación</h2>

          <p v-if="mensaje" class="mb-4 rounded-xl border border-emerald-300/25 bg-emerald-400/10 p-3 text-sm text-emerald-100" role="status">{{ mensaje }}</p>

          <template v-if="estado === 'inactivo'">
            <label for="paquete-recorrido" class="mb-1.5 block text-sm font-semibold">Paquete</label>
            <select id="paquete-recorrido" v-model="paqueteId" class="mb-4 w-full rounded-xl border border-white/20 bg-[#0b1c12] px-4 py-3 text-base text-white focus:outline-none focus:ring-2 focus:ring-emerald-400">
              <option value="" disabled>Selecciona un paquete</option>
              <option v-for="paquete in misPaquetes" :key="paquete.id" :value="paquete.id">{{ paquete.nombre }}</option>
            </select>
            <p v-if="!misPaquetes.length" class="-mt-1 mb-3 text-xs text-amber-200">No hay paquetes disponibles. Conéctate una vez para cargar tu lista.</p>


            <button type="button" :disabled="!paqueteId" class="min-h-12 w-full rounded-xl bg-emerald-600 px-4 py-3 text-sm font-black uppercase tracking-widest text-black transition hover:bg-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-300 disabled:cursor-not-allowed disabled:opacity-50" @click="iniciar">
              Iniciar recorrido
            </button>
            <p class="mt-3 text-xs text-white/60 lg:hidden">Mantén la pantalla encendida mientras grabas.</p>
          </template>

          <template v-else>
            <p class="mb-1 truncate text-sm text-white/60">{{ nombreDelPaquete(recorrido.paquete) }}</p>
            <p class="mb-3 text-base font-bold" aria-live="polite">{{ estado === 'grabando' ? 'Grabando…' : 'En pausa' }}</p>
            <dl class="mb-4 grid grid-cols-3 gap-2 text-center">
              <div class="rounded-xl bg-black/25 p-2"><dt class="text-[11px] uppercase text-white/50">Puntos</dt><dd class="text-xl font-black">{{ total }}</dd></div>
              <div class="rounded-xl bg-black/25 p-2"><dt class="text-[11px] uppercase text-white/50">Sin enviar</dt><dd class="text-xl font-black">{{ pendientes }}</dd></div>
              <div class="rounded-xl bg-black/25 p-2"><dt class="text-[11px] uppercase text-white/50">Precisión</dt><dd class="text-xl font-black">{{ precision === null ? '—' : precision + ' m' }}</dd></div>
            </dl>
            <div class="grid grid-cols-2 gap-3 lg:grid-cols-1">
              <button v-if="estado === 'grabando'" type="button" class="min-h-12 rounded-xl border border-white/25 px-4 py-3 text-sm font-black uppercase tracking-widest hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-emerald-300" @click="grabacion.pausar">Pausar</button>
              <button v-else type="button" class="min-h-12 rounded-xl bg-emerald-600 px-4 py-3 text-sm font-black uppercase tracking-widest text-black hover:bg-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-300" @click="grabacion.reanudar">Reanudar</button>
              <button type="button" class="min-h-12 rounded-xl bg-rose-500 px-4 py-3 text-sm font-black uppercase tracking-widest text-white hover:bg-rose-400 focus:outline-none focus:ring-2 focus:ring-rose-300" @click="finalizar">Finalizar</button>
            </div>
          </template>

          <p v-if="aviso" class="mt-3 rounded-xl border border-amber-300/30 bg-amber-300/10 p-3 text-sm text-amber-100" role="alert">{{ aviso }}</p>
        </section>

        <!-- Mapa: pantalla completa bajo la barra superior en móvil -->
        <section
          class="relative lg:h-[34rem]"
          :class="vistaMovil === 'mapa' ? 'max-lg:fixed max-lg:inset-x-0 max-lg:bottom-0 max-lg:top-[var(--cab)] max-lg:z-40' : 'max-lg:hidden'"
          aria-label="Mapa del recorrido"
        >
          <div ref="mapaEl" class="h-full w-full overflow-hidden bg-[#0b1c12] lg:rounded-3xl lg:border lg:border-white/10"></div>

          <!-- Estado sobre el mapa -->
          <div class="pointer-events-none absolute left-3 right-16 top-3 z-[1000] flex flex-col items-start gap-2">
            <div class="pointer-events-auto flex flex-wrap items-center gap-2" aria-live="polite">
              <span class="inline-flex items-center gap-2 rounded-full bg-black/75 px-3 py-1.5 text-xs font-bold backdrop-blur" :class="enLinea ? 'text-emerald-200' : 'text-amber-200'">
                <span class="h-2 w-2 rounded-full" :class="enLinea ? 'bg-emerald-400' : 'bg-amber-300'"></span>
                {{ enLinea ? 'En línea' : 'Sin conexión' }}
              </span>
              <span v-if="sincronizando" class="rounded-full bg-black/75 px-3 py-1.5 text-xs font-bold text-sky-200 backdrop-blur">Sincronizando…</span>
              <span v-if="miPosicion" class="rounded-full bg-black/75 px-3 py-1.5 text-xs font-bold backdrop-blur" :class="precisionBaja ? 'text-amber-200' : 'text-sky-100'">Precisión {{ miPosicion.precision }} m</span>
            </div>
            <span v-if="textoDistancia" class="pointer-events-auto rounded-full bg-black/75 px-3 py-1.5 text-xs font-bold backdrop-blur" :class="lejosDelPaquete ? 'text-amber-200' : 'text-amber-100'">{{ textoDistancia }}</span>
            <p v-if="lejosDelPaquete" class="pointer-events-auto max-w-xs rounded-xl bg-black/75 px-3 py-2 text-xs text-amber-100 backdrop-blur" role="alert">Estás lejos del punto del paquete. Un recorrido que no pase a menos de {{ (limiteM / 1000).toFixed(1) }} km de ese punto no se podrá publicar.</p>
            <p v-if="!enLinea" class="pointer-events-auto max-w-xs rounded-xl bg-black/75 px-3 py-2 text-xs text-amber-100 backdrop-blur">Sin internet: los puntos se guardan en este dispositivo y el mapa puede verse incompleto, pero el recorrido se marca igual.</p>
            <p v-if="precisionBaja" class="pointer-events-auto max-w-xs rounded-xl bg-black/75 px-3 py-2 text-xs text-amber-100 backdrop-blur" role="status">Señal débil: no se marcan puntos con precisión peor de {{ PRECISION_MAXIMA_M }} m. Sal a un lugar abierto.</p>
            <p v-if="estadoUbicacion !== 'activa'" class="pointer-events-auto max-w-xs rounded-xl bg-black/75 px-3 py-2 text-xs backdrop-blur" :class="estadoUbicacion === 'buscando' ? 'text-white/80' : 'text-amber-100'" role="status">
              {{ textoUbicacion }}
              <button v-if="estadoUbicacion === 'denegada' || estadoUbicacion === 'sin_gps'" type="button" class="ml-1 font-black underline" @click="iniciarUbicacion">Reintentar</button>
            </p>
          </div>

          <!-- Botones flotantes -->
          <div class="absolute right-3 top-3 z-[1000] flex flex-col gap-2">
            <button type="button" class="flex h-12 w-12 items-center justify-center rounded-full bg-black/75 text-white shadow-lg outline-none backdrop-blur focus-visible:ring-2 focus-visible:ring-sky-300" :class="seguir ? 'ring-2 ring-sky-400 text-sky-300' : ''" :disabled="!miPosicion" :aria-pressed="seguir" aria-label="Centrar el mapa en mi ubicación y seguirme" @click="centrarEnMiUbicacion">
              <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="3.5"/><path stroke-linecap="round" d="M12 2v3m0 14v3M2 12h3m14 0h3"/><circle cx="12" cy="12" r="8"/></svg>
            </button>
            <button type="button" class="flex h-12 w-12 items-center justify-center rounded-full bg-black/75 text-white shadow-lg outline-none backdrop-blur focus-visible:ring-2 focus-visible:ring-emerald-300 lg:hidden" aria-label="Ver mis recorridos" @click="vistaMovil = 'lista'">
              <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/></svg>
            </button>
          </div>
        </section>
      </div>

      <section class="mt-10" :class="{ 'max-lg:hidden': vistaMovil === 'mapa' }" aria-labelledby="titulo-lista">
        <div class="mb-4 flex items-center justify-between gap-3">
          <h2 id="titulo-lista" class="text-lg font-black">Mis recorridos</h2>
          <button type="button" class="min-h-11 rounded-xl border border-emerald-300/40 bg-emerald-400/10 px-4 text-xs font-black uppercase tracking-widest text-emerald-100 hover:bg-emerald-400/20 focus:outline-none focus:ring-2 focus:ring-emerald-300 lg:hidden" @click="vistaMovil = 'mapa'">Ver mapa</button>
        </div>
        <p v-if="mensaje" class="mb-4 rounded-xl border border-emerald-300/25 bg-emerald-400/10 p-3 text-sm text-emerald-100 lg:hidden" role="status">{{ mensaje }}</p>
        <p v-if="errorLista" class="mb-4 text-sm text-amber-200">{{ errorLista }}</p>
        <p v-if="!recorridosMostrados.length" class="rounded-2xl border border-white/10 bg-white/5 p-6 text-sm text-white/60">Aún no has grabado recorridos.</p>
        <ul class="space-y-3">
          <li v-for="item in recorridosMostrados" :key="item.id_cliente" class="flex flex-col gap-3 rounded-2xl border border-white/10 bg-white/5 p-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p class="font-bold">{{ nombreDelPaquete(item.paquete) }}</p>
              <p class="mt-1 text-xs text-white/50">{{ formatoFecha(item.iniciado_en) }}<template v-if="item.total_puntos !== null"> · {{ item.total_puntos }} puntos</template></p>
              <p v-if="item.errorLocal" class="mt-1 text-xs text-rose-200">{{ item.errorLocal }}</p>
              <p v-if="item.coincide_con_paquete === false" class="mt-1 text-xs font-semibold text-amber-200" role="alert">⚠ Queda a {{ (item.distancia_paquete_m / 1000).toFixed(1) }} km de la ubicación del paquete (máximo {{ (item.limite_m / 1000).toFixed(1) }} km): no se puede publicar.</p>
            </div>
            <div class="flex flex-wrap items-center gap-3">
              <span class="rounded-full border px-3 py-1 text-xs font-bold" :class="etiquetaEstado(item).clase">{{ etiquetaEstado(item).texto }}</span>
              <button v-if="item.errorLocal" type="button" class="min-h-11 rounded-xl border border-white/25 px-4 text-xs font-black uppercase tracking-widest hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-emerald-300" @click="reintentar(item)">Reintentar</button>
              <button v-else-if="puedePublicar(item) && !item.publicado" type="button" class="min-h-11 rounded-xl bg-emerald-600 px-4 text-xs font-black uppercase tracking-widest text-black hover:bg-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-300" @click="cambiarPublicacion(item, true)">Publicar</button>
              <button v-else-if="item.publicado" type="button" class="min-h-11 rounded-xl border border-white/25 px-4 text-xs font-black uppercase tracking-widest hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-emerald-300" @click="cambiarPublicacion(item, false)">Retirar</button>
              <button v-if="!esActivo(item)" type="button" class="min-h-11 rounded-xl border border-rose-400/40 px-4 text-xs font-black uppercase tracking-widest text-rose-200 hover:bg-rose-500/15 focus:outline-none focus:ring-2 focus:ring-rose-300" :aria-label="`Eliminar el recorrido de ${nombreDelPaquete(item.paquete)}`" @click="pedirEliminar(item)">Eliminar</button>
              <span v-else class="text-xs font-bold text-sky-200">En grabación</span>
            </div>
          </li>
        </ul>
      </section>
    </main>

    <div v-if="alertaLejos" class="fixed inset-0 z-[100] flex items-end justify-center bg-black/70 p-4 sm:items-center" @click.self="alertaLejos = null" @keydown.esc="alertaLejos = null">
      <div class="w-full max-w-sm rounded-3xl bg-[#0f2318] p-6 text-white shadow-2xl ring-1 ring-white/10" role="alertdialog" aria-modal="true" aria-labelledby="titulo-lejos" aria-describedby="detalle-lejos">
        <h2 id="titulo-lejos" class="mb-2 text-lg font-black">Estás lejos del paquete</h2>
        <p id="detalle-lejos" class="mb-2 text-sm text-white/80">Estás a <strong>{{ alertaLejos.texto }}</strong> del punto de «{{ alertaLejos.nombre }}».</p>
        <p class="mb-4 text-sm text-amber-200">Un recorrido que no pase a menos de {{ (limiteM / 1000).toFixed(1) }} km de ese punto no se podrá publicar. Comprueba que elegiste el paquete correcto.</p>
        <div class="grid grid-cols-2 gap-3">
          <button ref="botonCambiarPaquete" type="button" class="min-h-12 rounded-xl bg-emerald-600 px-4 text-sm font-black uppercase tracking-widest text-black outline-none hover:bg-emerald-500 focus-visible:ring-2 focus-visible:ring-white" @click="alertaLejos = null">Cambiar paquete</button>
          <button type="button" class="min-h-12 rounded-xl border border-white/25 px-4 text-sm font-black uppercase tracking-widest outline-none hover:bg-white/10 focus-visible:ring-2 focus-visible:ring-white" @click="confirmarInicioLejos">Grabar igual</button>
        </div>
      </div>
    </div>

    <div v-if="porEliminar" class="fixed inset-0 z-[100] flex items-end justify-center bg-black/70 p-4 sm:items-center" @click.self="cerrarEliminar" @keydown.esc="cerrarEliminar">
      <div class="w-full max-w-sm rounded-3xl bg-[#0f2318] p-6 text-white shadow-2xl ring-1 ring-white/10" role="alertdialog" aria-modal="true" aria-labelledby="titulo-eliminar" aria-describedby="detalle-eliminar">
        <h2 id="titulo-eliminar" class="mb-2 text-lg font-black">¿Eliminar este recorrido?</h2>
        <p id="detalle-eliminar" class="mb-1 text-sm text-white/80">
          Se borrarán el recorrido de «{{ nombreDelPaquete(porEliminar.paquete) }}» y todos sus puntos GPS.
        </p>
        <p v-if="porEliminar.publicado" class="mb-1 text-sm font-semibold text-amber-200">Está publicado: dejará de verse en el mapa del paquete.</p>
        <p class="mb-4 text-sm text-white/60">Esta acción no se puede deshacer.</p>
        <p v-if="errorEliminar" class="mb-4 rounded-xl border border-rose-300/30 bg-rose-400/10 p-3 text-sm text-rose-100" role="alert">{{ errorEliminar }}</p>
        <div class="grid grid-cols-2 gap-3">
          <button ref="botonCancelar" type="button" class="min-h-12 rounded-xl border border-white/25 px-4 text-sm font-black uppercase tracking-widest outline-none hover:bg-white/10 focus-visible:ring-2 focus-visible:ring-white disabled:opacity-50" :disabled="eliminando" @click="cerrarEliminar">Cancelar</button>
          <button type="button" class="min-h-12 rounded-xl bg-rose-500 px-4 text-sm font-black uppercase tracking-widest text-white outline-none hover:bg-rose-400 focus-visible:ring-2 focus-visible:ring-white disabled:opacity-60" :disabled="eliminando" @click="eliminarConfirmado">{{ eliminando ? 'Eliminando…' : 'Eliminar' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>
