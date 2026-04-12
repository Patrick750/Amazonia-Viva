<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from '@/api/axios';

// ── Estado ──────────────────────────────────────────────────────────────────
const reservas        = ref([]);
const cargando        = ref(true);
const error           = ref('');
const tabActiva       = ref('Confirmado');
const mostrarModal    = ref(false);
const reservaACanc    = ref(null);
const cancelando      = ref(false);
const mensajeExito    = ref('');
const viajeroAbierto  = ref({}); // { [reserva.id]: boolean }

const toggleViajeros = (id) => {
  viajeroAbierto.value[id] = !viajeroAbierto.value[id];
};

// ── Helpers ──────────────────────────────────────────────────────────────────
const formatPrecio = (v) =>
  new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(v || 0);

const formatFecha = (iso) => {
  if (!iso) return 'Sin fecha definida';
  const [y, m, d] = iso.split('-');
  const meses = ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic'];
  return `${d} ${meses[parseInt(m)-1]} ${y}`;
};

const diasHastaActividad = (fechaIso) => {
  if (!fechaIso) return null;
  const hoy  = new Date();
  hoy.setHours(0,0,0,0);
  const act  = new Date(fechaIso + 'T00:00:00');
  return Math.round((act - hoy) / 86400000);
};

// ── Carga de datos ───────────────────────────────────────────────────────────
async function cargarReservas() {
  cargando.value = true;
  error.value    = '';
  try {
    const { data } = await axios.get('api/mis-reservas/');
    reservas.value = data;
  } catch (e) {
    error.value = 'No pudimos cargar tus reservas. Intenta recargar la página.';
    console.error(e);
  } finally {
    cargando.value = false;
  }
}

onMounted(cargarReservas);

// ── Filtrado y conteos ───────────────────────────────────────────────────────
const confirmadas = computed(() => reservas.value.filter(r => r.estado === 'Confirmado'));
const rechazadas   = computed(() => reservas.value.filter(r => r.estado === 'Rechazado'));
const canceladas  = computed(() => reservas.value.filter(r => r.estado === 'Cancelado'));

const reservasFiltradas = computed(() => {
  if (tabActiva.value === 'Confirmado') return confirmadas.value;
  if (tabActiva.value === 'Rechazado')  return rechazadas.value;
  return canceladas.value;
});

// ── Cancelación ──────────────────────────────────────────────────────────────
function abrirModal(reserva) {
  reservaACanc.value  = reserva;
  mostrarModal.value  = true;
  mensajeExito.value  = '';
}

function cerrarModal() {
  mostrarModal.value = false;
  reservaACanc.value = null;
}

async function confirmarCancelacion() {
  if (!reservaACanc.value) return;
  cancelando.value = true;
  try {
    const { data } = await axios.patch(`api/mis-reservas/${reservaACanc.value.id}/cancelar/`);
    mensajeExito.value = data.mensaje || 'Reserva cancelada.';
    // Actualizar estado localmente sin recargar todo
    const idx = reservas.value.findIndex(r => r.id === reservaACanc.value.id);
    if (idx !== -1) reservas.value[idx].estado = 'Cancelado';
    setTimeout(cerrarModal, 2200);
  } catch (e) {
    const msg = e.response?.data?.error || 'Ocurrió un error al cancelar.';
    mensajeExito.value = '⚠ ' + msg;
  } finally {
    cancelando.value = false;
  }
}

// ── Badge de estado ──────────────────────────────────────────────────────────
const badgeClasses = {
  Confirmado: 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/30',
  Rechazado:  'bg-amber-500/15 text-amber-400 border border-amber-500/30 font-black',
  Cancelado:  'bg-red-500/15 text-red-300 border border-red-500/30',
};

// ── Política de cancelación según días ───────────────────────────────────────
function politicaCancelacion(dias) {
  if (dias === null) return { texto: 'Sin fecha conocida', color: 'text-white/40' };
  if (dias > 30)  return { texto: 'Reembolso del 100%',  color: 'text-emerald-400' };
  if (dias >= 15) return { texto: 'Reembolso del 80%',   color: 'text-emerald-400' };
  if (dias >= 7)  return { texto: 'Reembolso del 40%',   color: 'text-yellow-400'  };
  if (dias >= 0)  return { texto: 'Sin reembolso',        color: 'text-red-400'     };
  return { texto: 'Actividad ya realizada', color: 'text-white/40' };
}
</script>

<template>
  <div class="min-h-screen bg-[#0a1a0f] text-white font-sans">

    <!-- ── HERO / CABECERA ─────────────────────────────────────────────── -->
    <section class="relative pt-28 pb-10 overflow-hidden">
      <div class="absolute inset-0 bg-gradient-to-b from-[#0f2318] via-[#0a1a0f] to-[#0a1a0f]"></div>
      <div class="absolute top-24 left-1/4 w-96 h-96 rounded-full bg-emerald-500/4 blur-3xl pointer-events-none"></div>
      <div class="absolute bottom-0 right-1/4 w-72 h-72 rounded-full bg-teal-400/4 blur-3xl pointer-events-none"></div>

      <div class="relative z-10 max-w-5xl mx-auto px-6">
        <!-- Breadcrumb etiqueta -->
        <div class="inline-flex items-center gap-2 bg-emerald-500/10 border border-emerald-400/20 text-emerald-300 text-[11px] font-bold uppercase tracking-widest px-4 py-1.5 rounded-full mb-6">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
          </svg>
          Gestión de reservas
        </div>
        <h1 class="text-4xl sm:text-5xl font-black text-white leading-tight mb-3">
          Mis Reservas
        </h1>
        <p class="text-white/45 text-base max-w-xl leading-relaxed">
          Consulta el estado y detalle de tus servicios contratados.
        </p>
      </div>
    </section>

    <!-- ── CONTENIDO PRINCIPAL ────────────────────────────────────────── -->
    <main class="max-w-5xl mx-auto px-6 pb-24 relative z-10">

      <!-- ── TABS TIPO PÍLDORA ───────────────────────────────────────── -->
      <div class="flex items-center gap-2 mb-8 flex-wrap">
        <button
          v-for="(tab, key) in {
            Confirmado: { label: 'Confirmadas', count: confirmadas.length },
            Rechazado:  { label: 'Rechazadas',  count: rechazadas.length  },
            Cancelado:  { label: 'Canceladas',  count: canceladas.length  },
          }"
          :key="key"
          @click="tabActiva = key"
          :class="[
            'flex items-center gap-2 px-5 py-2 rounded-full text-sm font-bold border transition-all duration-200',
            tabActiva === key
              ? 'bg-emerald-500 text-white border-emerald-500 shadow-lg shadow-emerald-500/20'
              : 'bg-transparent text-white/50 border-white/15 hover:border-white/30 hover:text-white/80'
          ]"
        >
          {{ tab.label }}
          <span
            :class="[
              'text-[11px] font-black px-1.5 py-0.5 rounded-full min-w-[20px] text-center',
              tabActiva === key ? 'bg-white/20' : 'bg-white/8'
            ]"
          >{{ tab.count }}</span>
        </button>
      </div>

      <!-- ── LOADING ─────────────────────────────────────────────────── -->
      <div v-if="cargando" class="space-y-4">
        <div v-for="i in 3" :key="i" class="bg-white/5 rounded-2xl border border-white/8 p-6 animate-pulse">
          <div class="flex gap-5">
            <div class="w-28 h-28 rounded-xl bg-white/8 flex-shrink-0"></div>
            <div class="flex-1 space-y-3 py-1">
              <div class="h-4 bg-white/8 rounded-lg w-2/3"></div>
              <div class="h-3 bg-white/6 rounded-lg w-1/2"></div>
              <div class="h-3 bg-white/6 rounded-lg w-1/3"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- ── ERROR ───────────────────────────────────────────────────── -->
      <div v-else-if="error" class="bg-red-500/10 border border-red-500/20 rounded-2xl p-6 text-red-300 text-sm font-medium flex items-center gap-3">
        <svg class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
        {{ error }}
      </div>

      <!-- ── LISTA DE RESERVAS ────────────────────────────────────────── -->
      <div v-else-if="reservasFiltradas.length > 0" class="space-y-5">
        <div
          v-for="r in reservasFiltradas"
          :key="r.id"
          class="group bg-white/4 hover:bg-white/6 border border-white/8 hover:border-white/14 rounded-2xl overflow-hidden shadow-sm transition-all duration-300"
        >
          <div class="flex flex-col sm:flex-row gap-0">

            <!-- Imagen thumbnail -->
            <div class="relative sm:w-44 h-44 sm:h-auto flex-shrink-0 overflow-hidden bg-[#0f2318]">
              <img
                v-if="r.imagen"
                :src="r.imagen"
                :alt="r.nombre"
                class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
              />
              <div v-else class="w-full h-full flex items-center justify-center bg-emerald-500/5">
                <svg class="w-12 h-12 text-emerald-500/30" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3 21l6.75-6.75 1.5 1.5M21 3l-9 9"/>
                </svg>
              </div>
              <!-- Overlay degradado -->
              <div class="absolute inset-0 bg-gradient-to-r from-transparent to-[#0a1a0f]/20 sm:block hidden"></div>
            </div>

            <!-- Información principal -->
            <div class="flex-1 p-5 sm:p-6 flex flex-col gap-4 relative">

              <!-- Badge de estado (esquina sup derecha) -->
              <div class="absolute top-5 right-5">
                <span :class="['text-[11px] font-bold px-3 py-1 rounded-full', badgeClasses[r.estado] || 'bg-white/10 text-white/60']">
                  {{ r.estado }}
                </span>
              </div>

              <!-- Nombre del tour -->
              <div class="pr-24">
                <h3 class="text-lg font-bold text-white leading-snug">{{ r.nombre }}</h3>
                <p class="text-xs text-white/35 mt-1">Comprada el {{ formatFecha(r.fecha_compra) }}</p>
              </div>

              <!-- Metadata: agencia, fecha, personas -->
              <ul class="space-y-2">
                <li class="flex items-center gap-2.5 text-sm text-white/55">
                  <svg class="w-4 h-4 text-emerald-400/70 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                    <path stroke-linecap="round" stroke-linejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
                  </svg>
                  <span>{{ r.agencia || r.ubicacion || 'Sin operador' }}</span>
                </li>
                <li class="flex items-center gap-2.5 text-sm text-white/55">
                  <svg class="w-4 h-4 text-emerald-400/70 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                  </svg>
                  <span>{{ formatFecha(r.fecha_actividad) }}</span>
                </li>
                <li class="flex items-center gap-2.5 text-sm text-white/55">
                  <svg class="w-4 h-4 text-emerald-400/70 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0"/>
                  </svg>
                  <span>{{ r.cantidad }} {{ r.cantidad === 1 ? 'persona' : 'personas' }}</span>
                </li>
              </ul>

              <!-- Requerimientos especiales -->
              <div v-if="r.requerimientos" class="bg-white/4 border border-white/8 rounded-xl px-4 py-3 text-sm">
                <span class="font-bold text-white/70">Requerimientos especiales: </span>
                <span class="text-white/50">{{ r.requerimientos }}</span>
              </div>

              <!-- ── SECCIÓN VIAJEROS ──────────────────────────────────── -->
              <div v-if="r.viajeros && r.viajeros.length > 0" class="border border-white/8 rounded-xl overflow-hidden">
                <!-- Cabecera acordeón -->
                <button
                  @click="toggleViajeros(r.id)"
                  class="w-full flex items-center justify-between px-4 py-3 hover:bg-white/4 transition-colors text-left"
                >
                  <div class="flex items-center gap-2.5">
                    <svg class="w-4 h-4 text-emerald-400/80 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0"/>
                    </svg>
                    <span class="text-sm font-bold text-white/70">Expedicionarios</span>
                    <span class="text-[11px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      {{ r.viajeros.length }} {{ r.viajeros.length === 1 ? 'persona' : 'personas' }}
                    </span>
                  </div>
                  <svg
                    :class="['w-4 h-4 text-white/30 transition-transform duration-200', viajeroAbierto[r.id] ? 'rotate-180' : '']"
                    fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
                  </svg>
                </button>

                <!-- Lista desplegable -->
                <div v-if="viajeroAbierto[r.id]" class="border-t border-white/8 divide-y divide-white/6">
                  <div
                    v-for="(v, idx) in r.viajeros"
                    :key="idx"
                    class="px-4 py-3.5"
                  >
                    <!-- Encabezado viajero -->
                    <div class="flex items-center gap-2.5 mb-2">
                      <div class="w-7 h-7 rounded-full bg-emerald-500/15 border border-emerald-500/25 flex items-center justify-center text-emerald-400 text-[11px] font-black flex-shrink-0">
                        {{ idx + 1 }}
                      </div>
                      <div>
                        <p class="text-white font-bold text-sm leading-tight">
                          {{ v.nombres || '—' }} {{ v.apellidos || '' }}
                        </p>
                        <p class="text-[10px] text-white/35 font-medium">
                          {{ idx === 0 ? 'Titular de la Reserva' : `Expedicionario ${idx + 1}` }}
                        </p>
                      </div>
                    </div>
                    <!-- Datos del viajero en grid -->  
                    <div class="grid grid-cols-2 sm:grid-cols-3 gap-x-4 gap-y-1.5 pl-9">
                      <div v-if="v.tipo_doc || v.num_doc">
                        <p class="text-[10px] text-white/30 uppercase tracking-wider font-semibold">Documento</p>
                        <p class="text-xs text-white/65 font-medium">{{ v.tipo_doc }} {{ v.num_doc }}</p>
                      </div>
                      <div v-if="v.edad">
                        <p class="text-[10px] text-white/30 uppercase tracking-wider font-semibold">Edad</p>
                        <p class="text-xs text-white/65 font-medium">{{ v.edad }} años</p>
                      </div>
                      <div v-if="v.novedades" class="col-span-2 sm:col-span-3 mt-1">
                        <p class="text-[10px] text-white/30 uppercase tracking-wider font-semibold mb-0.5">Novedades</p>
                        <p class="text-xs text-white/55 italic leading-relaxed">{{ v.novedades }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Footer: precio + acción -->
              <div class="flex items-center justify-between pt-1 mt-auto flex-wrap gap-3">
                <div>
                  <p class="text-[11px] text-white/30 uppercase tracking-wider font-semibold mb-0.5">Total pagado</p>
                  <p class="text-2xl font-black text-emerald-400 leading-none">{{ formatPrecio(r.precio_total) }}</p>
                  <p class="text-[10px] text-white/30 mt-0.5">{{ formatPrecio(r.precio_unitario) }} × {{ r.cantidad }}</p>
                </div>

                <!-- Botón cancelar (solo Confirmadas) -->
                <button
                  v-if="r.estado === 'Confirmado'"
                  @click="abrirModal(r)"
                  class="flex items-center gap-2 px-4 py-2.5 rounded-xl border border-red-500/25 text-red-400 hover:bg-red-500/10 hover:border-red-400/40 hover:text-red-300 text-sm font-bold transition-all duration-200"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
                  </svg>
                  Cancelar reserva
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ── ESTADO VACÍO ─────────────────────────────────────────────── -->
      <div v-else class="text-center py-20">
        <div class="mx-auto w-20 h-20 rounded-2xl bg-white/5 border border-white/8 flex items-center justify-center mb-5">
          <svg class="w-10 h-10 text-white/20" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
          </svg>
        </div>
        <p class="text-white/40 font-semibold mb-1">Sin reservas{{ tabActiva === 'Confirmado' ? ' confirmadas' : tabActiva === 'Rechazado' ? ' rechazadas' : ' canceladas' }}</p>
        <p class="text-white/25 text-sm">
          <template v-if="tabActiva === 'Confirmado'">Explora el catálogo y reserva tu próxima experiencia amazónica.</template>
          <template v-else-if="tabActiva === 'Rechazado'">Tus reservas rechazadas por el operador aparecerán aquí para auditoría.</template>
          <template v-else>No tienes ninguna reserva cancelada todavía.</template>
        </p>
        <router-link
          v-if="tabActiva === 'Confirmado'"
          to="/catalogo/tours"
          class="inline-flex items-center gap-2 mt-6 px-6 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-sm transition-all shadow-lg shadow-emerald-500/20"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
          Explorar tours
        </router-link>
      </div>

    </main>

    <!-- ══ MODAL DE CANCELACIÓN ════════════════════════════════════════ -->
    <Transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="mostrarModal" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
        <!-- Overlay -->
        <div class="absolute inset-0 bg-[#0a1a0f]/85 backdrop-blur-md" @click="cerrarModal"></div>

        <!-- Panel -->
        <Transition
          enter-active-class="transition ease-out duration-200"
          enter-from-class="opacity-0 scale-95 translate-y-2"
          enter-to-class="opacity-100 scale-100 translate-y-0"
        >
          <div v-if="mostrarModal" class="relative bg-[#0f2318] border border-white/10 rounded-3xl shadow-2xl w-full max-w-lg overflow-hidden">

            <!-- Header del modal -->
            <div class="px-7 pt-7 pb-5 border-b border-white/8 flex items-start justify-between gap-4">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-red-500/15 border border-red-500/25 flex items-center justify-center flex-shrink-0">
                  <svg class="w-5 h-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                  </svg>
                </div>
                <div>
                  <h3 class="text-lg font-black text-white">Cancelar reserva</h3>
                  <p class="text-sm text-white/40 mt-0.5 leading-tight">{{ reservaACanc?.nombre }}</p>
                </div>
              </div>
              <button @click="cerrarModal" class="text-white/30 hover:text-white transition-colors mt-0.5">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            </div>

            <!-- Cuerpo del modal -->
            <div class="px-7 py-6 space-y-5">

              <!-- Políticas de cancelación -->
              <div>
                <p class="text-[11px] font-bold uppercase tracking-widest text-emerald-400 mb-3">Políticas de cancelación</p>
                <div class="space-y-2">
                  <div v-for="p in [
                    { rango: 'Más de 30 días', reembolso: 'Sin penalización (100%)', punto: 'bg-emerald-500' },
                    { rango: '29 a 15 días',   reembolso: 'Reembolso del 80%',       punto: 'bg-emerald-400' },
                    { rango: '14 a 7 días',    reembolso: 'Reembolso del 40%',       punto: 'bg-yellow-400'  },
                    { rango: 'Menos de 3 días',reembolso: 'Sin reembolso',           punto: 'bg-red-500'     },
                  ]" :key="p.rango" class="flex items-center gap-3 text-sm">
                    <div :class="['w-1.5 h-1.5 rounded-full flex-shrink-0', p.punto]"></div>
                    <span class="text-white font-semibold min-w-[130px]">{{ p.rango }}:</span>
                    <span class="text-white/55">{{ p.reembolso }}</span>
                  </div>
                </div>
              </div>

              <!-- Situación actual de esta reserva -->
              <div v-if="reservaACanc" class="bg-white/4 border border-white/8 rounded-2xl p-4">
                <div class="flex items-center justify-between">
                  <div>
                    <p class="text-xs text-white/40 font-medium mb-1">Fecha de actividad</p>
                    <p class="text-white font-bold text-sm">{{ formatFecha(reservaACanc.fecha_actividad) }}</p>
                  </div>
                  <div class="text-right">
                    <p class="text-xs text-white/40 font-medium mb-1">Tu reembolso estimado</p>
                    <p :class="['font-black text-base', politicaCancelacion(diasHastaActividad(reservaACanc.fecha_actividad)).color]">
                      {{ politicaCancelacion(diasHastaActividad(reservaACanc.fecha_actividad)).texto }}
                    </p>
                  </div>
                </div>
                <!-- Alerta cupos cuando aplica -->
                <div
                  v-if="reservaACanc.fecha_actividad && diasHastaActividad(reservaACanc.fecha_actividad) >= 8"
                  class="mt-3 flex items-start gap-2 text-emerald-300 text-xs bg-emerald-500/8 border border-emerald-500/15 rounded-xl px-3 py-2"
                >
                  <svg class="w-4 h-4 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  </svg>
                  Los cupos reservados serán liberados y estarán disponibles nuevamente para otros viajeros.
                </div>
              </div>

              <!-- Mensaje de resultado -->
              <div
                v-if="mensajeExito"
                :class="[
                  'flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-semibold',
                  mensajeExito.startsWith('⚠')
                    ? 'bg-red-500/10 border border-red-500/20 text-red-300'
                    : 'bg-emerald-500/10 border border-emerald-500/20 text-emerald-300'
                ]"
              >
                <svg v-if="!mensajeExito.startsWith('⚠')" class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
                </svg>
                <svg v-else class="w-5 h-5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                {{ mensajeExito.replace('⚠ ', '') }}
              </div>

            </div>

            <!-- Footer del modal -->
            <div class="px-7 pb-7 flex gap-3">
              <button
                @click="cerrarModal"
                class="flex-1 px-6 py-3.5 rounded-xl border border-white/10 text-white/60 font-bold hover:bg-white/5 hover:text-white transition-all text-sm"
              >
                Volver
              </button>
              <button
                @click="confirmarCancelacion"
                :disabled="cancelando || !!mensajeExito"
                :class="[
                  'flex-1 px-6 py-3.5 rounded-xl font-black text-sm transition-all flex items-center justify-center gap-2',
                  (cancelando || mensajeExito)
                    ? 'bg-white/8 text-white/30 cursor-not-allowed border border-white/8'
                    : 'bg-red-500/80 hover:bg-red-500 text-white border border-red-400/40 shadow-lg shadow-red-500/15'
                ]"
              >
                <svg v-if="cancelando" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                </svg>
                <template v-if="cancelando">Cancelando...</template>
                <template v-else-if="mensajeExito">Procesado</template>
                <template v-else>Confirmar cancelación</template>
              </button>
            </div>

          </div>
        </Transition>
      </div>
    </Transition>

  </div>
</template>

<style scoped>
/* Scrollbar minimalista */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,.12); border-radius: 4px; }
</style>
