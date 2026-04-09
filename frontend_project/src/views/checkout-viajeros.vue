<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { useCarrito } from '@/composables/useCarrito';

const router = useRouter();
const { toursSeleccionados, totalFinal, subtotalTours, subtotalProductos, tarifaEcologica } = useCarrito();

// ── Cálculo del total de personas ──────────────────────────────────────────
const totalPersonas = computed(() =>
    toursSeleccionados.value.reduce((sum, t) => sum + t.cantidad, 0)
);

// ── Datos del usuario logueado (para auto-rellenar Viajero 1) ───────────────
const datosUsuario = {
    nombres: localStorage.getItem('nombre') || '',
    apellidos: localStorage.getItem('apellido') || '',
};

// ── Estado de los viajeros ─────────────────────────────────────────────────
const viajeroActivo = ref(0);
const viajeros = ref([]);

const crearViajero = () => ({
    nombres: '',
    apellidos: '',
    tipo_doc: 'Cédula de Ciudadanía',
    num_doc: '',
    edad: '',
    novedades: '',
    completado: false,
});

const tiposDoc = [
    'Cédula de Ciudadanía',
    'Tarjeta de Identidad',
    'Cédula de Extranjería',
    'Pasaporte',
];

onMounted(() => {
    const n = totalPersonas.value;
    if (n === 0) {
        // No hay tours seleccionados — volver al carrito
        router.push('/carrito');
        return;
    }
    
    // Intentar recuperar si existen datos previos (usuario dio click a 'Volver' desde Pago)
    const guardados = sessionStorage.getItem('checkout_viajeros');
    if (guardados) {
        try {
            const parsed = JSON.parse(guardados);
            // Asegurarnos que la cant de personas sigue siendo igual antes de cargar ciegamente
            if (Array.isArray(parsed) && parsed.length === n) {
                viajeros.value = parsed;
                return;
            }
        } catch (e) {
            console.error("Error leyendo cache de viajeros:", e);
        }
    }

    // Si no hay guardados o cambió la cantidad, iniciar limpios.
    viajeros.value = Array.from({ length: n }, crearViajero);
});

// Guardar reactivamente cada cambio a sessionStorage por si el usuario navega fuera inesperadamente
watch(viajeros, (nuevosViajeros) => {
    sessionStorage.setItem('checkout_viajeros', JSON.stringify(nuevosViajeros));
}, { deep: true });

// Si el carrito cambia externamente, recalcular
watch(totalPersonas, (nuevo) => {
    if (nuevo === 0) {
        router.push('/carrito');
    }
});

// ── Lógica de acordeones ───────────────────────────────────────────────────
const toggleAcordeon = (index) => {
    viajeroActivo.value = viajeroActivo.value === index ? -1 : index;
};

// ── Validación ─────────────────────────────────────────────────────────────
const esValido = (v) =>
    v.nombres.trim().length >= 2 &&
    v.apellidos.trim().length >= 2 &&
    v.tipo_doc !== '' &&
    v.num_doc.trim().length >= 5 &&
    Number(v.edad) >= 1 && Number(v.edad) <= 120;

const onCampoChange = (index) => {
    const v = viajeros.value[index];
    v.completado = esValido(v);
};

const completarYAvanzar = (index) => {
    onCampoChange(index);
    if (viajeros.value[index].completado) {
        if (index < viajeros.value.length - 1) {
            viajeroActivo.value = index + 1;
        } else {
            viajeroActivo.value = -1; // Colapsar todos al terminar
        }
    }
};

// ── Autorellenar con datos del usuario ─────────────────────────────────────
const usarMisDatos = () => {
    if (viajeros.value.length > 0) {
        viajeros.value[0].nombres = datosUsuario.nombres;
        viajeros.value[0].apellidos = datosUsuario.apellidos;
        onCampoChange(0);
    }
};

// ── CTA Final ──────────────────────────────────────────────────────────────
const todosCompletos = computed(() =>
    viajeros.value.length > 0 && viajeros.value.every(v => v.completado)
);

const viajerosCompletados = computed(() =>
    viajeros.value.filter(v => v.completado).length
);

const irAlPago = () => {
    if (!todosCompletos.value) return;
    sessionStorage.setItem('checkout_viajeros', JSON.stringify(viajeros.value));
    router.push('/pago');
};

// ── Helpers de UI ──────────────────────────────────────────────────────────
const formatPrecio = (valor) =>
    new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(valor);

const nombreViajero = (v, idx) => {
    if (v.nombres && v.apellidos) return `${v.nombres} ${v.apellidos}`;
    if (idx === 0) return 'Titular de la Reserva';
    return `Viajero ${idx + 1}`;
};

// Clases dinámicas para organizar mejor el estilo del botón
const btnClasses = computed(() => {
  const base = 'w-full py-4.5 font-black text-[15px] rounded-2xl flex items-center justify-center gap-3 mt-4 transition-all duration-300 relative overflow-hidden group border';
  
  if (todosCompletos.value) {
    return `${base} bg-gradient-to-br from-emerald-500 via-emerald-600 to-teal-700 text-white border-emerald-400/30 shadow-[0_10px_40px_-10px_rgba(16,185,129,0.5)] hover:shadow-[0_15px_50px_-10px_rgba(16,185,129,0.6)] hover:scale-[1.02] active:scale-[0.98]`;
  }
  
  return `${base} bg-white/5 text-white/20 cursor-not-allowed border-white/10`;
});

</script>

<template>
  <div class="min-h-screen bg-[#0a1a0f]">

    <!-- ── Hero / Header ─────────────────────────────────────────────── -->
    <section class="relative pt-28 pb-10 overflow-hidden">
      <div class="absolute inset-0 bg-gradient-to-b from-[#0f2318] via-[#0a1a0f] to-[#0a1a0f]"></div>
      <div class="absolute top-20 left-1/4 w-80 h-80 rounded-full bg-emerald-500/5 blur-3xl pointer-events-none"></div>
      <div class="absolute bottom-0 right-1/4 w-56 h-56 rounded-full bg-teal-400/5 blur-3xl pointer-events-none"></div>

      <div class="relative z-10 max-w-4xl mx-auto px-6">

        <!-- Botón volver -->
        <button
          @click="router.push('/carrito')"
          class="group flex items-center gap-2 text-white/40 hover:text-emerald-300 text-sm font-semibold transition-all mb-8"
        >
          <svg class="w-4 h-4 group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
          </svg>
          Volver al carrito
        </button>

        <!-- Contenido centrado -->
        <div class="text-center">

          <!-- Breadcrumb pasos -->
          <div class="flex items-center justify-center gap-2 mb-8">
            <div class="flex items-center gap-2">
              <div class="w-7 h-7 rounded-full bg-emerald-500/30 flex items-center justify-center">
                <svg class="w-3.5 h-3.5 text-emerald-300" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>
              </div>
              <span class="text-white/40 text-xs font-medium">Carrito</span>
            </div>
            <div class="w-10 h-px bg-white/15"></div>
            <div class="flex items-center gap-2">
              <div class="w-7 h-7 rounded-full bg-emerald-500 flex items-center justify-center shadow-lg shadow-emerald-500/30">
                <span class="text-white text-xs font-black">2</span>
              </div>
              <span class="text-emerald-300 text-xs font-bold">Viajeros</span>
            </div>
            <div class="w-10 h-px bg-white/15"></div>
            <div class="flex items-center gap-2">
              <div class="w-7 h-7 rounded-full bg-white/10 border border-white/15 flex items-center justify-center">
                <span class="text-white/30 text-xs font-bold">3</span>
              </div>
              <span class="text-white/30 text-xs font-medium">Pago</span>
            </div>
          </div>

          <!-- Título -->
          <div class="inline-flex items-center gap-2 bg-emerald-500/15 backdrop-blur border border-emerald-400/25 text-emerald-300 text-xs font-bold uppercase tracking-widest px-5 py-2 rounded-full mb-6">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
            Preparativos de Expedición
          </div>
          <h1 class="text-4xl sm:text-5xl font-black text-white mb-4 leading-tight">
            Registro de
            <span class="text-transparent bg-clip-text bg-gradient-to-r from-emerald-300 via-teal-200 to-lime-300"> Expedicionarios</span>
          </h1>
          <p class="text-white/50 text-base max-w-xl mx-auto mb-6 leading-relaxed">
            Falta poco para vivir la selva. Necesitamos los datos de cada uno de tus
            <span class="text-emerald-300 font-bold">{{ totalPersonas }} expedicionarios</span>
            para gestionar seguros y cumplir normativas de las zonas naturales protegidas.
          </p>

          <!-- Trust badge -->
          <div class="inline-flex items-center gap-2.5 bg-white/5 border border-white/10 text-white/50 text-xs px-5 py-2.5 rounded-2xl">
            <svg class="w-4 h-4 text-emerald-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
            </svg>
            <span>Tus datos están encriptados. Solo se usan para el manifiesto de pasajeros y el seguro de aventura.</span>
          </div>

        </div><!-- /text-center -->
      </div><!-- /container -->
    </section>

    <!-- ── Contenido ────────────────────────────────────────────────────── -->
    <section class="max-w-4xl mx-auto px-6 pb-28">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">

        <!-- ── Formularios de Viajeros (2/3) ─────────────────────────── -->
        <div class="lg:col-span-2 space-y-4">

          <!-- Barra de progreso -->
          <div class="bg-white/5 border border-white/10 rounded-2xl px-5 py-4 flex items-center justify-between gap-4 mb-6">
            <div class="flex-1">
              <div class="flex justify-between text-xs mb-1.5">
                <span class="text-white/50 font-medium">Progreso de registro</span>
                <span class="font-bold" :class="todosCompletos ? 'text-emerald-400' : 'text-white/50'">
                  {{ viajerosCompletados }} / {{ viajeros.length }}
                </span>
              </div>
              <div class="h-1.5 bg-white/10 rounded-full overflow-hidden">
                <div
                  class="h-full bg-gradient-to-r from-emerald-500 to-teal-400 rounded-full transition-all duration-500"
                  :style="{ width: viajeros.length > 0 ? `${(viajerosCompletados / viajeros.length) * 100}%` : '0%' }"
                ></div>
              </div>
            </div>
            <div v-if="todosCompletos" class="flex-shrink-0 w-10 h-10 rounded-full bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center">
              <svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
              </svg>
            </div>
          </div>

          <!-- Acordeones de viajeros -->
          <div
            v-for="(viajero, idx) in viajeros"
            :key="idx"
            :class="[
              'border rounded-2xl overflow-hidden transition-all duration-300',
              viajeroActivo === idx
                ? 'border-emerald-500/40 shadow-lg shadow-emerald-500/10'
                : viajero.completado
                  ? 'border-emerald-500/20 bg-emerald-500/5'
                  : 'border-white/10 bg-white/3'
            ]"
          >
            <!-- Cabecera del acordeón -->
            <button
              @click="toggleAcordeon(idx)"
              class="w-full flex items-center gap-4 px-5 py-4 text-left transition-colors hover:bg-white/5"
            >
              <!-- Indicador número / check -->
              <div :class="[
                'w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0 font-black text-sm transition-all',
                viajero.completado
                  ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-500/30'
                  : viajeroActivo === idx
                    ? 'bg-emerald-500/20 border-2 border-emerald-400 text-emerald-300'
                    : 'bg-white/10 border border-white/20 text-white/50'
              ]">
                <svg v-if="viajero.completado" class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
                </svg>
                <span v-else>{{ idx + 1 }}</span>
              </div>

              <!-- Texto cabecera -->
              <div class="flex-1 min-w-0">
                <p class="text-[10px] font-bold uppercase tracking-widest mb-0.5" :class="viajero.completado ? 'text-emerald-400' : 'text-white/30'">
                  {{ idx === 0 ? 'Titular de la Reserva' : `Expedicionario ${idx + 1}` }}
                </p>
                <p class="text-sm font-semibold truncate" :class="viajero.completado ? 'text-white' : 'text-white/50'">
                  {{ viajero.completado ? nombreViajero(viajero, idx) : 'Pendiente de registro' }}
                </p>
              </div>

              <!-- Badge estado -->
              <div class="flex items-center gap-2 flex-shrink-0">
                <span v-if="viajero.completado" class="hidden sm:block bg-emerald-500/15 text-emerald-300 text-[10px] font-bold px-2.5 py-1 rounded-full border border-emerald-500/25">
                  ✓ Completo
                </span>
                <span v-else class="hidden sm:block bg-white/5 text-white/30 text-[10px] font-medium px-2.5 py-1 rounded-full border border-white/10">
                  Pendiente
                </span>
                <!-- Chevron -->
                <svg
                  :class="['w-4 h-4 text-white/40 transition-transform duration-300', viajeroActivo === idx ? 'rotate-180' : '']"
                  fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/>
                </svg>
              </div>
            </button>

            <!-- Formulario (expandido) -->
            <transition
              enter-active-class="transition-all duration-300 ease-out"
              enter-from-class="opacity-0 max-h-0"
              enter-to-class="opacity-100 max-h-[600px]"
              leave-active-class="transition-all duration-200 ease-in"
              leave-from-class="opacity-100 max-h-[600px]"
              leave-to-class="opacity-0 max-h-0"
            >
              <div v-if="viajeroActivo === idx" class="overflow-hidden">
                <div class="px-5 pb-5 border-t border-white/8 pt-5">

                  <!-- Botón "Usar mis datos" solo para Viajero 0 -->
                  <div v-if="idx === 0 && (datosUsuario.nombres || datosUsuario.apellidos)" class="mb-5">
                    <button
                      @click="usarMisDatos"
                      class="w-full flex items-center justify-center gap-2 py-3 border border-dashed border-emerald-500/40 text-emerald-300 text-sm font-semibold rounded-xl hover:bg-emerald-500/10 hover:border-emerald-500/60 transition-all"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                      </svg>
                      Soy el Expedicionario Principal — Usar mis datos
                    </button>
                  </div>

                  <!-- Grid de campos -->
                  <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">

                    <!-- Nombres -->
                    <div>
                      <label class="block text-white/50 text-xs font-semibold mb-1.5 uppercase tracking-wider">
                        Nombres <span class="text-red-400">*</span>
                      </label>
                      <input
                        v-model="viajero.nombres"
                        @input="onCampoChange(idx)"
                        type="text"
                        placeholder="Ej: Juan Carlos"
                        class="w-full bg-white/8 border border-white/15 text-white placeholder-white/25 rounded-xl px-4 py-3 text-sm outline-none focus:border-emerald-500/60 focus:bg-white/10 transition-all"
                      />
                    </div>

                    <!-- Apellidos -->
                    <div>
                      <label class="block text-white/50 text-xs font-semibold mb-1.5 uppercase tracking-wider">
                        Apellidos <span class="text-red-400">*</span>
                      </label>
                      <input
                        v-model="viajero.apellidos"
                        @input="onCampoChange(idx)"
                        type="text"
                        placeholder="Ej: Pérez Gómez"
                        class="w-full bg-white/8 border border-white/15 text-white placeholder-white/25 rounded-xl px-4 py-3 text-sm outline-none focus:border-emerald-500/60 focus:bg-white/10 transition-all"
                      />
                    </div>

                    <!-- Tipo de documento -->
                    <div>
                      <label class="block text-white/50 text-xs font-semibold mb-1.5 uppercase tracking-wider">
                        Tipo de Documento <span class="text-red-400">*</span>
                      </label>
                      <select
                        v-model="viajero.tipo_doc"
                        @change="onCampoChange(idx)"
                        class="w-full bg-white/8 border border-white/15 text-white rounded-xl px-4 py-3 text-sm outline-none focus:border-emerald-500/60 focus:bg-white/10 transition-all appearance-none cursor-pointer"
                      >
                        <option v-for="tipo in tiposDoc" :key="tipo" :value="tipo" class="bg-[#0f2318] text-white">{{ tipo }}</option>
                      </select>
                    </div>

                    <!-- Número de documento -->
                    <div>
                      <label class="block text-white/50 text-xs font-semibold mb-1.5 uppercase tracking-wider">
                        N° de Documento <span class="text-red-400">*</span>
                      </label>
                      <input
                        v-model="viajero.num_doc"
                        @input="onCampoChange(idx)"
                        type="text"
                        placeholder="Sin puntos ni guiones"
                        class="w-full bg-white/8 border border-white/15 text-white placeholder-white/25 rounded-xl px-4 py-3 text-sm outline-none focus:border-emerald-500/60 focus:bg-white/10 transition-all"
                      />
                    </div>

                    <!-- Edad -->
                    <div class="sm:col-span-2">
                      <label class="block text-white/50 text-xs font-semibold mb-1.5 uppercase tracking-wider">
                        Edad <span class="text-red-400">*</span>
                      </label>
                      <div class="flex gap-3 items-center">
                        <input
                          v-model="viajero.edad"
                          @input="onCampoChange(idx)"
                          type="number"
                          min="1"
                          max="120"
                          placeholder="Años cumplidos"
                          class="w-40 bg-white/8 border border-white/15 text-white placeholder-white/25 rounded-xl px-4 py-3 text-sm outline-none focus:border-emerald-500/60 focus:bg-white/10 transition-all"
                        />
                        <p class="text-white/25 text-xs leading-snug">
                          Requerido para el seguro médico de aventura en zonas protegidas.
                        </p>
                      </div>
                    </div>
                    
                    <!-- Novedades / Observaciones -->
                    <div class="sm:col-span-2 mt-2">
                      <label class="block text-white/50 text-xs font-semibold mb-1.5 uppercase tracking-wider">
                        Novedades u Observaciones
                      </label>
                      <textarea
                        v-model="viajero.novedades"
                        @input="onCampoChange(idx)"
                        placeholder="Alergias, condiciones médicas, restricciones alimentarias..."
                        rows="3"
                        class="w-full bg-white/8 border border-white/15 text-white placeholder-white/25 rounded-xl px-4 py-3 text-sm outline-none focus:border-emerald-500/60 focus:bg-white/10 transition-all resize-none"
                      ></textarea>
                    </div>
                  </div>

                  <!-- Botón confirmar viajero -->
                  <div class="mt-5">
                    <button
                      @click="completarYAvanzar(idx)"
                      :disabled="!esValido(viajero)"
                      :class="[
                        'w-full py-3.5 rounded-xl font-bold text-sm flex items-center justify-center gap-2 transition-all',
                        esValido(viajero)
                          ? 'bg-emerald-600/30 hover:bg-emerald-600/50 border border-emerald-500/40 text-emerald-300 hover:border-emerald-500/60'
                          : 'bg-white/5 border border-white/10 text-white/25 cursor-not-allowed'
                      ]"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
                      </svg>
                      {{ idx === viajeros.length - 1 ? 'Confirmar y Revisar Todo' : `Confirmar Viajero ${idx + 1}` }}
                    </button>
                  </div>

                </div>
              </div>
            </transition>
          </div>

          <!-- Volver al carrito -->
          <button
            @click="router.push('/carrito')"
            class="flex items-center gap-2 text-white/40 hover:text-emerald-300 text-sm font-semibold transition-colors group mt-2"
          >
            <svg class="w-4 h-4 group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
            </svg>
            Volver al carrito
          </button>
        </div>

        <!-- ── Panel lateral: Resumen ─────────────────────────────────── -->
        <div class="lg:col-span-1">
          <div class="sticky top-24 bg-white/5 border border-white/10 rounded-3xl overflow-hidden">

            <!-- Header panel -->
            <div class="bg-gradient-to-r from-emerald-900/60 to-teal-900/60 px-6 py-5 border-b border-white/10">
              <h3 class="text-white font-black text-base flex items-center gap-2">
                <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
                </svg>
                Tu Expedición
              </h3>
            </div>

            <div class="p-5 space-y-4">

              <!-- Tours seleccionados -->
              <div v-for="tour in toursSeleccionados" :key="tour.id" class="flex items-start gap-3">
                <div class="w-10 h-10 rounded-xl overflow-hidden bg-[#0f2318] flex-shrink-0">
                  <img v-if="tour.imagen" :src="tour.imagen" :alt="tour.nombre" class="w-full h-full object-cover"/>
                  <div v-else class="w-full h-full flex items-center justify-center">
                    <svg class="w-5 h-5 text-emerald-400/30" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1"><path stroke-linecap="round" stroke-linejoin="round" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2"/></svg>
                  </div>
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-white/80 text-xs font-semibold leading-snug line-clamp-2">{{ tour.nombre }}</p>
                  <p class="text-white/35 text-[10px] mt-0.5">{{ tour.cantidad }} persona{{ tour.cantidad > 1 ? 's' : '' }} · {{ formatPrecio(tour.precio) }} c/u</p>
                </div>
              </div>

              <!-- Divisor -->
              <div class="border-t border-white/10 pt-4 space-y-2">
                <div class="flex justify-between text-sm">
                  <span class="text-white/50">Tours & Expediciones</span>
                  <span class="text-white font-semibold">{{ formatPrecio(subtotalTours) }}</span>
                </div>
                <div v-if="subtotalProductos > 0" class="flex justify-between text-sm">
                  <span class="text-white/50">Equipo & Accesorios</span>
                  <span class="text-white font-semibold">{{ formatPrecio(subtotalProductos) }}</span>
                </div>
                <div class="flex justify-between text-sm">
                  <span class="text-white/40">Aporte Ecológico</span>
                  <span class="text-lime-400 font-semibold">{{ formatPrecio(tarifaEcologica) }}</span>
                </div>
                <div class="flex justify-between text-base pt-2 border-t border-white/10">
                  <span class="text-white font-black">Total</span>
                  <span class="text-white font-black">{{ formatPrecio(totalFinal) }}</span>
                </div>
              </div>

              <!-- CTA Final -->
              <button
                @click="irAlPago"
                :disabled="!todosCompletos"
                :class="btnClasses"
              >
                <svg class="w-4 h-4 transition-transform duration-300 group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                </svg>
                <span class="relative">
                  {{ todosCompletos ? 'Continuar al Pago Seguro' : `Faltan ${viajeros.length - viajerosCompletados} expedicionarios` }}
                </span>
              </button>

              <!-- Microcopy trust -->
              <p class="text-center text-white/20 text-[10px] leading-relaxed pt-2">
                Al continuar aceptas las condiciones de reserva y el manifiesto de pasajeros de Amazonia Viva.
              </p>
            </div>
          </div>
        </div>

      </div>
    </section>
  </div>
</template>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
select option {
  background-color: #0f2318;
  color: white;
}
</style>
