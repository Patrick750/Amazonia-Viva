<script setup>
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
    </div>

    <!-- ── MITAD INFERIOR: Info ── -->
    <div class="flex flex-col flex-1 p-5 gap-2.5">

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
      </div>

      <!-- 2. Título destacado -->
      <h3 class="font-bold text-gray-900 text-base leading-snug line-clamp-2">{{ tour.nombre }}</h3>

      <!-- 3. Breve descripción -->
      <p class="text-sm text-gray-500 line-clamp-2 leading-relaxed flex-1">{{ tour.descripcion }}</p>

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
          @click="emit('verDetalles', tour)"
          class="px-5 py-2.5 rounded-full bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-semibold transition-colors shadow-sm"
        >
          Ver detalles
        </button>
      </div>
    </div>

  </article>
</template>
