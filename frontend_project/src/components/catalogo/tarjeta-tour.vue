<script setup>
import { useRouter } from 'vue-router';
const router = useRouter();

const props = defineProps({
    tour: { type: Object, required: true },
    rol: { type: String, default: null }
});
const emit = defineEmits(['verDetalles']);

const estrellas = (rating) => {
    const r = Math.min(5, Math.max(0, Number(rating)));
    const llenas = Math.floor(r);
    const media = r - llenas >= 0.5 ? 1 : 0;
    const vacias = 5 - llenas - media;
    return [
        ...Array(llenas).fill('full'),
        ...Array(media).fill('half'),
        ...Array(vacias).fill('empty'),
    ];
};

const nivelRiesgo = (n) => {
    if (n <= 3) return { label: 'Bajo', class: 'bg-emerald-100 text-emerald-700' };
    if (n <= 6) return { label: 'Moderado', class: 'bg-amber-100 text-amber-700' };
    if (n <= 8) return { label: 'Alto', class: 'bg-orange-100 text-orange-700' };
    return { label: 'Extremo', class: 'bg-red-100 text-red-700' };
};

const puedeComprar = props.rol !== 'proveedor';

const formatFecha = (fecha) => {
    if (!fecha) return '';
    const [y, m, d] = fecha.split('-');
    const meses = ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic'];
    return `${d} ${meses[parseInt(m)-1]}. ${y}`;
};

const alertaCupos = (cupos) => cupos !== null && cupos !== undefined && cupos <= 5;
</script>

<template>
  <article class="bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-lg border border-gray-100 transition-all duration-300 hover:-translate-y-0.5 flex flex-col">

    <!-- ── MITAD SUPERIOR: Fotografía ── -->
    <div class="relative h-52 bg-gray-100 overflow-hidden flex-shrink-0">
      <img
        v-if="tour.imagen_portada"
        :src="tour.imagen_portada"
        :alt="tour.nombre"
        class="w-full h-full object-cover hover:scale-105 transition-transform duration-500"
      >
      <div v-else class="w-full h-full flex items-center justify-center bg-gradient-to-br from-emerald-50 to-teal-100">
        <svg class="w-16 h-16 text-emerald-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/>
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/>
        </svg>
      </div>

      <!-- Badge nivel de riesgo -->
      <span :class="['absolute top-3 left-3 flex items-center gap-1 text-xs font-semibold px-2.5 py-1 rounded-full', nivelRiesgo(tour.nivel_riesgo).class]">
        <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clip-rule="evenodd"/>
        </svg>
        {{ nivelRiesgo(tour.nivel_riesgo).label }}
      </span>

      <!-- Badge Fijo / Flexible (arriba derecha) -->
      <span v-if="tour.tipo_paquete === 'fijo'"
        class="absolute top-3 right-3 flex items-center gap-1 text-xs font-bold px-2.5 py-1 rounded-full bg-blue-600/90 text-white backdrop-blur-sm shadow">
        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
        Fijo
      </span>
      <span v-else-if="tour.tipo_paquete === 'flexible'"
        class="absolute top-3 right-3 flex items-center gap-1 text-xs font-bold px-2.5 py-1 rounded-full bg-emerald-600/90 text-white backdrop-blur-sm shadow">
        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
        Flexible
      </span>
    </div>

    <!-- ── MITAD INFERIOR: Info ── -->
    <div class="flex flex-col flex-1 p-5 gap-2.5">

      <!-- Agencia -->
      <div class="flex items-center justify-between">
        <router-link :to="{ name: 'perfil_publico', params: { id: tour.agencia_id }, query: { tipo: 'agencia' } }" class="flex items-center gap-1.5 text-xs text-gray-400 hover:text-emerald-600 transition-colors w-max">
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>
          <span class="font-medium text-gray-500 hover:text-emerald-700 transition-colors">{{ tour.nombre_agencia }}</span>
        </router-link>
        
        <span v-if="tour.proveedor_validado" class="flex items-center gap-1 text-[9px] uppercase font-bold tracking-wider text-emerald-600 bg-emerald-50 border border-emerald-100 px-2 py-0.5 rounded-full" title="Toda la documentación legal de esta agencia está verificada.">
          <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>
          Verificación legal
        </span>
        <span v-else class="flex items-center gap-1 text-[9px] uppercase font-bold tracking-wider text-rose-500 bg-rose-50 border border-rose-100 px-2 py-0.5 rounded-full" title="Esta agencia aún no adjunta su RNT o RUT oficial.">
          <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/></svg>
          Sin verificar
        </span>
      </div>

      <!-- 1. Calificación con estrellas -->
      <div class="flex items-center gap-1.5">
        <div class="flex gap-0.5">
          <template v-for="(tipo, i) in estrellas(tour.rating)" :key="i">
            <!-- Estrella llena -->
            <svg v-if="tipo === 'full'" class="w-4 h-4 text-amber-400" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
            </svg>
            <!-- Media estrella -->
            <svg v-else-if="tipo === 'half'" class="w-4 h-4 text-amber-300" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
            </svg>
            <!-- Estrella vacía -->
            <svg v-else class="w-4 h-4 text-gray-200" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
            </svg>
          </template>
        </div>
        <span class="text-xs text-gray-400">{{ Number(tour.rating).toFixed(1) }} · {{ tour.num_calificaciones }} reseñas</span>
        
        <!-- Contador de Ventas (Social Proof) -->
        <span class="ml-auto flex items-center gap-1 text-[10px] font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-100">
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"/></svg>
          {{ tour.ventas_totales || 0 }} vendidos
        </span>
      </div>

      <!-- 2. Título destacado -->
      <h3 class="font-bold text-gray-900 text-base leading-snug line-clamp-2">{{ tour.nombre }}</h3>

      <!-- 3. Breve descripción -->
      <p class="text-sm text-gray-500 line-clamp-2 leading-relaxed">{{ tour.descripcion }}</p>

      <!-- Fecha (paquete fijo) + Cupos disponibles -->
      <div class="flex flex-wrap items-center gap-2">
        <!-- Fecha del tour fijo -->
        <span v-if="tour.tipo_paquete === 'fijo' && tour.fecha_realizacion"
          class="inline-flex items-center gap-1 text-[11px] font-semibold text-blue-600 bg-blue-50 border border-blue-100 px-2.5 py-1 rounded-full">
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
          {{ formatFecha(tour.fecha_realizacion) }}
        </span>
        <!-- Paquete flexible -->
        <span v-else-if="tour.tipo_paquete === 'flexible'"
          class="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-600 bg-emerald-50 border border-emerald-100 px-2.5 py-1 rounded-full">
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
          Tú eliges la fecha
        </span>
        <!-- Cupos: alerta si quedan pocos -->
        <span v-if="tour.tipo_paquete === 'fijo' && tour.cupos_disponibles !== undefined"
          :class="['inline-flex items-center gap-1 text-[11px] font-bold px-2.5 py-1 rounded-full border',
            alertaCupos(tour.cupos_disponibles)
              ? 'text-red-600 bg-red-50 border-red-100 animate-pulse'
              : 'text-slate-500 bg-slate-50 border-slate-100'
          ]">
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
          {{ tour.cupos_disponibles === 0 ? '¡Sin cupos!' : `${tour.cupos_disponibles} cupos` }}
        </span>
      </div>

      <!-- 4. Íconos: Ubicación y Duración -->
      <div class="flex items-center gap-4 text-xs text-gray-500 pt-1 border-t border-gray-50">
        <span class="flex items-center gap-1.5">
          <svg class="w-4 h-4 text-gray-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
          </svg>
          <span class="truncate max-w-[120px]">{{ tour.ciudad }}</span>
        </span>
        <span class="flex items-center gap-1.5">
          <svg class="w-4 h-4 text-gray-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" stroke-width="2"/>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6l4 2"/>
          </svg>
          {{ tour.duracion }}h
        </span>
      </div>

      <!-- 5. Pie de tarjeta: Precio + Botón -->
      <div class="flex items-center justify-between pt-3 mt-auto border-t border-gray-100">
        <div>
          <span class="text-xs text-gray-400 block">Desde</span>
          <span class="text-xl font-black text-emerald-700">${{ Number(tour.precio).toLocaleString('es-CO') }}</span>
        </div>
        <button
          @click="router.push({ name: 'detalle_tour', params: { id: tour.id } })"
          class="px-5 py-2.5 rounded-full bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-semibold transition-colors shadow-sm"
        >
          Ver detalles
        </button>
      </div>
    </div>

  </article>
</template>
