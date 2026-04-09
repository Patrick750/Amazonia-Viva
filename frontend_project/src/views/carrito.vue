<script setup>
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useCarrito } from '@/composables/useCarrito';

const router = useRouter();
const {
    tours, productos, itemsCarrito,
    itemsSeleccionados, todoSeleccionado, toursSeleccionados,
    subtotalTours, subtotalProductos, tarifaEcologica, totalFinal,
    eliminarItem, actualizarCantidad, actualizarFecha,
    toggleSeleccion, seleccionarTodos, deseleccionarTodos,
} = useCarrito();

import { useCatalogo } from '@/composables/useCatalogo';
import { useNotificacion } from '@/composables/useNotificacion';

const { obtenerCuposDisponibles } = useCatalogo();
const { mostrarNotificacion } = useNotificacion();

const fechaMinima = (() => {
    const d = new Date();
    d.setDate(d.getDate() + 8); // Bloquea hoy + 7 días futuros = 8 días en total
    return d.toISOString().split('T')[0];
})();

const cuposStatus = ref({}); // { uuid: { cupos: number, cargando: boolean } }

const manejarCambioFecha = async (item, nuevaFecha) => {
    actualizarFecha(item.uuid, nuevaFecha);
    if (!nuevaFecha) {
        if (cuposStatus.value[item.uuid]) delete cuposStatus.value[item.uuid];
        return;
    }
    
    cuposStatus.value[item.uuid] = { ...cuposStatus.value[item.uuid], cargando: true };
    try {
        const res = await obtenerCuposDisponibles(item.id, nuevaFecha);
        cuposStatus.value[item.uuid] = { cupos: res.cupos_disponibles, cargando: false };
    } catch {
        cuposStatus.value[item.uuid] = { cupos: null, cargando: false };
    }
};

const formatPrecio = (valor) =>
    new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(valor);

const totalPersonas = computed(() =>
    tours.value.reduce((sum, i) => sum + i.cantidad, 0)
);
const totalUnidades = computed(() =>
    productos.value.reduce((sum, i) => sum + i.cantidad, 0)
);

const toggleTodos = () => {
    if (todoSeleccionado.value) {
        deseleccionarTodos();
    } else {
        seleccionarTodos();
    }
};

const irAPago = () => {
    // 1. Validar que todos los tours SELECCIONADOS tengan fecha elegida
    const toursSinFecha = toursSeleccionados.value.filter(t => !t.fecha_reserva);
    if (toursSinFecha.length > 0) {
        mostrarNotificacion(`Debes elegir la fecha para: ${toursSinFecha[0].nombre}`, 'warning');
        return;
    }

    // 2. Validar que la fecha sea al menos 7 días a futuro (por seguridad si se manipuló el input)
    const hoyReferencia = new Date();
    hoyReferencia.setDate(hoyReferencia.getDate() + 7);
    hoyReferencia.setHours(0, 0, 0, 0);

    for (const tour of toursSeleccionados.value) {
        const f = new Date(tour.fecha_reserva + 'T00:00:00');
        if (f < hoyReferencia) {
            mostrarNotificacion(`La fecha de '${tour.nombre}' debe ser al menos 7 días a futuro.`, 'warning');
            return;
        }
        
        // 3. Validar cupos si ya se cargaron
        const status = cuposStatus.value[tour.id];
        if (status && status.cupos === 0) {
            mostrarNotificacion(`No hay cupos disponibles para '${tour.nombre}' en la fecha seleccionada.`, 'error');
            return;
        }
    }

    // Si hay tours seleccionados → registrar datos de viajeros primero
    if (toursSeleccionados.value.length > 0) {
        router.push('/checkout/viajeros');
    } else {
        // Solo productos → ir directamente al pago
        router.push('/pago');
    }
};
</script>

<template>
  <div class="min-h-screen bg-[#0a1a0f]">

    <!-- ── Hero / Header ───────────────────────────────────────────── -->
    <section class="relative pt-28 pb-12 overflow-hidden">
      <div class="absolute inset-0 bg-gradient-to-b from-[#0f2318] via-[#0a1a0f] to-[#0a1a0f]"></div>
      <div class="absolute top-20 left-1/4 w-72 h-72 rounded-full bg-emerald-500/5 blur-3xl pointer-events-none"></div>
      <div class="absolute bottom-0 right-1/4 w-48 h-48 rounded-full bg-teal-400/5 blur-3xl pointer-events-none"></div>
      <svg class="absolute top-10 right-12 text-emerald-400/10 pointer-events-none" width="120" height="120" viewBox="0 0 100 100" fill="currentColor">
        <path d="M50 5 C80 5,95 35,95 50 C95 75,70 95,50 95 C30 95,5 75,5 50 C5 25,20 5,50 5Z"/>
      </svg>

      <div class="relative z-10 max-w-6xl mx-auto px-6 text-center">
        <div class="inline-flex items-center gap-2 bg-emerald-500/15 backdrop-blur border border-emerald-400/25 text-emerald-300 text-xs font-bold uppercase tracking-widest px-5 py-2 rounded-full mb-6">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"/>
          </svg>
          Paso final antes de tu aventura
        </div>
        <h1 class="text-4xl sm:text-5xl font-black text-white mb-4 leading-tight">
          Resumen de
          <span class="text-transparent bg-clip-text bg-gradient-to-r from-emerald-300 via-teal-200 to-lime-300"> tu Expedición</span>
        </h1>
        <p class="text-white/50 text-base max-w-xl mx-auto">
          Revisa los detalles de tu próximo gran viaje a la selva antes de asegurar tus cupos.
        </p>

        <!-- Contadores resumen header -->
        <div v-if="itemsCarrito.length > 0" class="mt-8 flex justify-center gap-6">
          <div class="bg-white/5 border border-white/10 rounded-2xl px-6 py-3 text-center">
            <p class="text-2xl font-black text-emerald-400">{{ tours.length }}</p>
            <p class="text-white/40 text-xs mt-0.5">Expediciones</p>
          </div>
          <div class="bg-white/5 border border-white/10 rounded-2xl px-6 py-3 text-center">
            <p class="text-2xl font-black text-teal-400">{{ productos.length }}</p>
            <p class="text-white/40 text-xs mt-0.5">Productos</p>
          </div>
          <div class="bg-white/5 border border-white/10 rounded-2xl px-6 py-3 text-center">
            <p class="text-2xl font-black text-lime-400">{{ itemsCarrito.length }}</p>
            <p class="text-white/40 text-xs mt-0.5">Total ítems</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Contenido principal ─────────────────────────────────────── -->
    <section class="max-w-6xl mx-auto px-6 pb-28">

      <!-- ══ ESTADO VACÍO ══════════════════════════════════════════════ -->
      <div v-if="itemsCarrito.length === 0" class="flex flex-col items-center justify-center py-24 text-center">
        <div class="relative mb-8">
          <div class="w-32 h-32 rounded-full bg-emerald-500/10 flex items-center justify-center">
            <svg class="w-16 h-16 text-emerald-400/30" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"/>
            </svg>
          </div>
          <div class="absolute -bottom-2 -right-2 w-10 h-10 rounded-full bg-emerald-600/30 flex items-center justify-center">
            <svg class="w-5 h-5 text-emerald-300" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
            </svg>
          </div>
        </div>
        <h2 class="text-2xl font-black text-white/70 mb-3">Tu mochila aún está vacía</h2>
        <p class="text-white/35 text-base max-w-sm mb-10 leading-relaxed">
          La selva te espera. Empieza a planear tu próxima aventura hoy mismo y asegura tus cupos antes de que se agoten.
        </p>
        <button
          @click="router.push('/catalogo/tours')"
          class="px-10 py-4 bg-gradient-to-r from-emerald-600 to-teal-600 text-white font-bold rounded-xl hover:from-emerald-500 hover:to-teal-500 transition-all shadow-lg shadow-emerald-500/25 flex items-center gap-2.5 text-base"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
          Descubrir Amazonía
        </button>
      </div>

      <!-- ══ CARRITO CON ÍTEMS ══════════════════════════════════════════ -->
      <div v-else class="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">

        <!-- ── Barra “Seleccionar todo” ────────────────────────────────────── -->
        <div class="lg:col-span-2 flex items-center justify-between bg-white/5 border border-white/10 rounded-2xl px-5 py-3.5">
          <label class="flex items-center gap-3 cursor-pointer group select-none">
            <button
              @click="toggleTodos"
              :class="[
                'w-5 h-5 rounded-md border-2 flex items-center justify-center flex-shrink-0 transition-all',
                todoSeleccionado
                  ? 'bg-emerald-500 border-emerald-500'
                  : 'bg-transparent border-white/30 group-hover:border-emerald-400'
              ]"
            >
              <svg v-if="todoSeleccionado" class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="3">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
              </svg>
              <!-- — Indeterminate icon: algunos seleccionados -->
              <svg v-else-if="itemsSeleccionados.length > 0" class="w-3 h-3 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="3">
                <line x1="5" y1="12" x2="19" y2="12"/>
              </svg>
            </button>
            <span class="text-white/70 text-sm font-semibold">
              Seleccionar todo
            </span>
          </label>
          <span class="text-white/40 text-xs">
            <span class="text-emerald-300 font-bold">{{ itemsSeleccionados.length }}</span>
            de {{ itemsCarrito.length }} ítem{{ itemsCarrito.length !== 1 ? 's' : '' }} seleccionado{{ itemsSeleccionados.length !== 1 ? 's' : '' }}
          </span>
        </div>

        <!-- ── Lista de ítems (columna principal) ─────────────────────── -->
        <div class="lg:col-span-2 space-y-8">

          <!-- ── Sección: Expediciones y Tours ───────────────────────── -->
          <div v-if="tours.length > 0">
            <div class="flex items-center gap-3 mb-5">
              <div class="w-8 h-8 rounded-xl bg-emerald-600/20 border border-emerald-500/30 flex items-center justify-center">
                <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064"/>
                </svg>
              </div>
              <div>
                <h2 class="text-white font-black text-lg leading-none">Expediciones & Paquetes</h2>
                <p class="text-white/40 text-xs mt-0.5">{{ tours.length }} ítem{{ tours.length > 1 ? 's' : '' }} · {{ totalPersonas }} persona{{ totalPersonas > 1 ? 's' : '' }}</p>
              </div>
              <span class="ml-auto bg-emerald-500/15 text-emerald-300 text-xs font-bold px-3 py-1 rounded-full border border-emerald-500/25">{{ formatPrecio(subtotalTours) }}</span>
            </div>

            <div class="space-y-4">
              <div
                v-for="item in tours"
                :key="item.uuid"
                :class="[
                  'group relative border rounded-2xl overflow-hidden transition-all duration-300',
                  item.seleccionado
                    ? 'bg-white/5 border-emerald-500/30 shadow-lg shadow-emerald-500/5'
                    : 'bg-white/3 border-white/8 opacity-60'
                ]"
              >
                <div class="flex gap-4 p-4">
                  <!-- Checkbox de selección -->
                  <div class="flex-shrink-0 self-center">
                    <button
                      @click="toggleSeleccion(item.uuid)"
                      :class="[
                        'w-5 h-5 rounded-md border-2 flex items-center justify-center transition-all',
                        item.seleccionado
                          ? 'bg-emerald-500 border-emerald-500'
                          : 'bg-transparent border-white/30 hover:border-emerald-400'
                      ]"
                    >
                      <svg v-if="item.seleccionado" class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="3">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
                      </svg>
                    </button>
                  </div>
                  <!-- Imagen -->
                  <div class="relative w-24 h-24 rounded-xl overflow-hidden bg-[#0f2318] flex-shrink-0">
                    <img v-if="item.imagen" :src="item.imagen" :alt="item.nombre" class="w-full h-full object-cover"/>
                    <div v-else class="w-full h-full flex items-center justify-center">
                      <svg class="w-10 h-10 text-emerald-400/20" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945"/>
                      </svg>
                    </div>
                  </div>
                    <!-- Info -->
                    <div class="flex-1 min-w-0">
                      <p class="text-emerald-400/70 text-xs font-medium mb-0.5">Expedición</p>
                      <h3 class="text-white font-bold text-sm leading-snug mb-1 line-clamp-1">{{ item.nombre }}</h3>
                      
                      <!-- Selector de Fecha / Info de Fecha -->
                      <div class="mt-3 bg-white/5 border border-white/10 rounded-xl p-2.5">
                        <div v-if="item.tipo_paquete === 'flexible'">
                          <p class="text-[10px] text-emerald-400 font-bold uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
                            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                             Elige fecha de inicio
                          </p>
                          <input
                            type="date"
                            :value="item.fecha_reserva"
                            :min="fechaMinima"
                            @change="(e) => manejarCambioFecha(item, e.target.value)"
                            class="w-full bg-[#0a1a0f] border border-white/10 rounded-lg px-3 py-1.5 text-xs font-bold text-white focus:outline-none focus:border-emerald-500/50 transition-all"
                          >
                          <!-- Cupos feedback -->
                          <div v-if="cuposStatus[item.uuid]" class="mt-1.5 px-2 py-1 rounded-md text-[10px] font-bold inline-flex items-center gap-1.5"
                            :class="cuposStatus[item.uuid].cupos === 0 ? 'bg-red-500/10 text-red-400' : (cuposStatus[item.uuid].cupos <= 5 ? 'bg-amber-500/10 text-amber-400' : 'bg-emerald-500/10 text-emerald-400')">
                            <span v-if="cuposStatus[item.uuid].cargando" class="animate-pulse">Verificando...</span>
                            <span v-else-if="cuposStatus[item.uuid].cupos === 0">Sin cupos</span>
                            <span v-else>{{ cuposStatus[item.uuid].cupos }} cupos disponibles</span>
                          </div>
                        </div>
                        <div v-else class="flex items-center gap-2">
                          <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                          <div>
                            <p class="text-[9px] text-white/30 uppercase tracking-tighter">Fecha fija de salida</p>
                            <p class="text-xs font-black text-emerald-300">{{ item.fecha_realizacion }}</p>
                          </div>
                        </div>
                      </div>

                      <p class="text-white/40 text-[10px] mt-2 italic shadow-sm" v-if="item.tipo_paquete === 'flexible' && !item.fecha_reserva">
                        * Debes elegir una fecha antes de pagar
                      </p>
                    </div>
                  <!-- Controles derecha -->
                  <div class="flex flex-col items-end justify-between gap-2 flex-shrink-0">
                    <!-- Eliminar -->
                    <button
                      @click="eliminarItem(item.uuid)"
                      class="w-7 h-7 rounded-full bg-red-500/10 hover:bg-red-500/20 flex items-center justify-center text-red-400 hover:text-red-300 transition-all opacity-0 group-hover:opacity-100"
                      title="Eliminar del carrito"
                    >
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                      </svg>
                    </button>
                    <!-- Selector personas -->
                    <div class="flex flex-col items-end gap-1">
                      <span class="text-white/30 text-[10px] uppercase tracking-wider">Acompañantes</span>
                      <div class="flex items-center gap-1 bg-white/8 border border-white/15 rounded-lg p-0.5">
                        <button
                          @click="actualizarCantidad(item.uuid, item.cantidad - 1)"
                          class="w-7 h-7 rounded-md bg-white/10 hover:bg-white/20 flex items-center justify-center text-white transition-all"
                        >
                          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><line x1="5" y1="12" x2="19" y2="12"/></svg>
                        </button>
                        <span class="w-8 text-center text-white font-black text-sm">{{ item.cantidad }}</span>
                        <button
                          @click="actualizarCantidad(item.uuid, item.cantidad + 1)"
                          class="w-7 h-7 rounded-md bg-white/10 hover:bg-white/20 flex items-center justify-center text-white transition-all"
                        >
                          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                        </button>
                      </div>
                      <!-- Total item -->
                      <p class="text-emerald-300 font-black text-sm">{{ formatPrecio(Number(item.precio) * item.cantidad) }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- ── Sección: Equipo y Accesorios ────────────────────────── -->
          <div v-if="productos.length > 0">
            <div class="flex items-center gap-3 mb-5">
              <div class="w-8 h-8 rounded-xl bg-teal-600/20 border border-teal-500/30 flex items-center justify-center">
                <svg class="w-4 h-4 text-teal-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
                </svg>
              </div>
              <div>
                <h2 class="text-white font-black text-lg leading-none">Equipo & Accesorios</h2>
                <p class="text-white/40 text-xs mt-0.5">{{ productos.length }} ítem{{ productos.length > 1 ? 's' : '' }} · {{ totalUnidades }} unidad{{ totalUnidades > 1 ? 'es' : '' }}</p>
              </div>
              <span class="ml-auto bg-teal-500/15 text-teal-300 text-xs font-bold px-3 py-1 rounded-full border border-teal-500/25">{{ formatPrecio(subtotalProductos) }}</span>
            </div>

            <div class="space-y-4">
              <div
                v-for="item in productos"
                :key="item.uuid"
                :class="[
                  'group relative border rounded-2xl overflow-hidden transition-all duration-300',
                  item.seleccionado
                    ? 'bg-white/5 border-teal-500/30 shadow-lg shadow-teal-500/5'
                    : 'bg-white/3 border-white/8 opacity-60'
                ]"
              >
                <div class="flex gap-4 p-4">
                  <!-- Checkbox de selección -->
                  <div class="flex-shrink-0 self-center">
                    <button
                      @click="toggleSeleccion(item.uuid)"
                      :class="[
                        'w-5 h-5 rounded-md border-2 flex items-center justify-center transition-all',
                        item.seleccionado
                          ? 'bg-teal-500 border-teal-500'
                          : 'bg-transparent border-white/30 hover:border-teal-400'
                      ]"
                    >
                      <svg v-if="item.seleccionado" class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="3">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
                      </svg>
                    </button>
                  </div>
                  <!-- Imagen -->
                  <div class="relative w-24 h-24 rounded-xl overflow-hidden bg-[#0f2318] flex-shrink-0">
                    <img v-if="item.imagen" :src="item.imagen" :alt="item.nombre" class="w-full h-full object-cover"/>
                    <div v-else class="w-full h-full flex items-center justify-center">
                      <svg class="w-10 h-10 text-teal-400/20" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
                      </svg>
                    </div>
                  </div>
                  <!-- Info -->
                  <div class="flex-1 min-w-0">
                    <p class="text-teal-400/70 text-xs font-medium mb-0.5">{{ item.subtitulo || 'Producto' }}</p>
                    <h3 class="text-white font-bold text-sm leading-snug mb-1 line-clamp-2">{{ item.nombre }}</h3>
                    <p class="text-white/50 text-xs mt-2">{{ formatPrecio(item.precio) }} / unidad</p>
                  </div>
                  <!-- Controles derecha -->
                  <div class="flex flex-col items-end justify-between gap-2 flex-shrink-0">
                    <!-- Eliminar -->
                    <button
                      @click="eliminarItem(item.uuid)"
                      class="w-7 h-7 rounded-full bg-red-500/10 hover:bg-red-500/20 flex items-center justify-center text-red-400 hover:text-red-300 transition-all opacity-0 group-hover:opacity-100"
                      title="Eliminar del carrito"
                    >
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                      </svg>
                    </button>
                    <!-- Selector cantidad -->
                    <div class="flex flex-col items-end gap-1">
                      <span class="text-white/30 text-[10px] uppercase tracking-wider">Cantidad</span>
                      <div class="flex items-center gap-1 bg-white/8 border border-white/15 rounded-lg p-0.5">
                        <button
                          @click="actualizarCantidad(item.uuid, item.cantidad - 1)"
                          class="w-7 h-7 rounded-md bg-white/10 hover:bg-white/20 flex items-center justify-center text-white transition-all"
                        >
                          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><line x1="5" y1="12" x2="19" y2="12"/></svg>
                        </button>
                        <span class="w-8 text-center text-white font-black text-sm">{{ item.cantidad }}</span>
                        <button
                          @click="actualizarCantidad(item.uuid, item.cantidad + 1)"
                          class="w-7 h-7 rounded-md bg-white/10 hover:bg-white/20 flex items-center justify-center text-white transition-all"
                        >
                          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                        </button>
                      </div>
                      <!-- Total item -->
                      <p class="text-teal-300 font-black text-sm">{{ formatPrecio(Number(item.precio) * item.cantidad) }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Seguir explorando -->
          <button
            @click="router.push('/catalogo/tours')"
            class="flex items-center gap-2 text-white/40 hover:text-emerald-300 text-sm font-semibold transition-colors group"
          >
            <svg class="w-4 h-4 group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
            </svg>
            Seguir explorando
          </button>
        </div>

        <!-- ── Panel lateral: Resumen de compra ───────────────────────── -->
        <div class="lg:col-span-1">
          <div class="sticky top-24 bg-white/5 border border-white/10 rounded-3xl overflow-hidden">

            <!-- Header panel -->
            <div class="bg-gradient-to-r from-emerald-900/60 to-teal-900/60 px-6 py-5 border-b border-white/10">
              <h3 class="text-white font-black text-lg flex items-center gap-2">
                <svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 11h.01M12 11h.01M15 11h.01M4 19h16a2 2 0 002-2V7a2 2 0 00-2-2H4a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                </svg>
                Resumen de Compra
              </h3>
            </div>

            <!-- Desglose -->
            <div class="p-6 space-y-4">

              <!-- Subtotal expediciones -->
              <div v-if="tours.length > 0" class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <div class="w-2 h-2 rounded-full bg-emerald-400"></div>
                  <span class="text-white/60 text-sm">Expediciones ({{ tours.length }})</span>
                </div>
                <span class="text-white font-semibold text-sm">{{ formatPrecio(subtotalTours) }}</span>
              </div>

              <!-- Subtotal productos -->
              <div v-if="productos.length > 0" class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <div class="w-2 h-2 rounded-full bg-teal-400"></div>
                  <span class="text-white/60 text-sm">Equipo & Accesorios ({{ productos.length }})</span>
                </div>
                <span class="text-white font-semibold text-sm">{{ formatPrecio(subtotalProductos) }}</span>
              </div>

              <!-- Tarifa ecológica -->
              <div class="flex items-start justify-between">
                <div class="flex items-start gap-2">
                  <div class="w-2 h-2 rounded-full bg-lime-400 mt-1.5 flex-shrink-0"></div>
                  <div>
                    <span class="text-white/60 text-sm">Aporte Ecológico</span>
                    <p class="text-white/25 text-[10px]">1% del subtotal de expediciones</p>
                  </div>
                </div>
                <span class="text-lime-300 font-semibold text-sm">{{ formatPrecio(tarifaEcologica) }}</span>
              </div>

              <!-- Divisor -->
              <div class="border-t border-white/10 pt-4">
                <div class="flex items-center justify-between">
                  <span class="text-white font-black text-base">Total a pagar</span>
                  <span class="text-white font-black text-xl">{{ formatPrecio(totalFinal) }}</span>
                </div>
                <p class="text-white/25 text-xs mt-1">COP · Precio final con todos los aportes</p>
              </div>

              <!-- CTA principal -->
              <button
                @click="irAPago"
                :disabled="itemsSeleccionados.length === 0"
                :class="[
                  'w-full py-4 font-black text-base rounded-xl shadow-lg flex items-center justify-center gap-2.5 mt-2 transition-all',
                  itemsSeleccionados.length > 0
                    ? 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white hover:shadow-emerald-500/30 hover:scale-[1.02] active:scale-[0.98] shadow-emerald-500/20'
                    : 'bg-white/10 text-white/30 cursor-not-allowed'
                ]"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                </svg>
                {{ itemsSeleccionados.length === 0 ? 'Selecciona al menos un ítem' : 'Proceder al pago seguro' }}
              </button>

              <!-- Trust Badges -->
              <div class="pt-4 border-t border-white/8 space-y-3">
                <div class="flex items-center gap-2.5 text-white/40">
                  <svg class="w-4 h-4 text-emerald-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
                  </svg>
                  <span class="text-xs">Transacción encriptada y 100% segura</span>
                </div>
                <div class="flex items-center gap-2.5 text-white/40">
                  <svg class="w-4 h-4 text-emerald-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                  </svg>
                  <span class="text-xs">Cancelación flexible hasta 24h antes</span>
                </div>
                <div class="flex items-center gap-2.5 text-white/40">
                  <svg class="w-4 h-4 text-emerald-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z"/>
                  </svg>
                  <span class="text-xs">Soporte ágil antes y durante tu viaje</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.line-clamp-1 {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  overflow: hidden;
  -webkit-line-clamp: 1;
}
</style>
