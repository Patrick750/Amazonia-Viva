<script setup>
import { useRouter } from 'vue-router';

const props = defineProps({
    producto: { type: Object, required: true },
    rol: { type: String, default: null }
});
const router = useRouter();

const estrellas = (rating) => {
    const r = Math.round(Number(rating) * 2) / 2;
    return Array.from({ length: 5 }, (_, i) => {
        if (i + 1 <= r) return 'full';
        if (i + 0.5 === r) return 'half';
        return 'empty';
    });
};
const puedeComprar = props.rol !== 'proveedor';
</script>

<template>
  <article class="group bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-xl border border-slate-100 transition-all duration-300 hover:-translate-y-1 flex flex-col">
    <!-- Imagen -->
    <div class="relative h-48 bg-slate-100 overflow-hidden flex-shrink-0">
      <img v-if="producto.imagen_portada" :src="producto.imagen_portada" :alt="producto.nombre"
           class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500">
      <div v-else class="w-full h-full flex items-center justify-center bg-gradient-to-br from-teal-50 to-emerald-100">
        <svg class="w-14 h-14 text-emerald-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2" stroke-width="1.5"/>
          <circle cx="8.5" cy="8.5" r="1.5" stroke-width="1.5"/>
          <polyline points="21 15 16 10 5 21" stroke-width="1.5"/>
        </svg>
      </div>
      <!-- Badge categoria -->
      <span class="absolute top-3 left-3 text-xs font-semibold px-2.5 py-1 rounded-full bg-teal-100 text-teal-700">
        {{ producto.nombre_categoria || 'Producto' }}
      </span>
    </div>

    <!-- Contenido -->
    <div class="p-5 flex flex-col flex-1 gap-3">
      <!-- Proveedor -->
      <div class="flex items-center gap-1.5 text-xs text-slate-400">
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/></svg>
        <span class="font-medium text-slate-500">{{ producto.nombre_proveedor }}</span>
      </div>

      <!-- Nombre -->
      <h3 class="font-bold text-slate-800 text-base leading-snug group-hover:text-teal-700 transition-colors line-clamp-2">
        {{ producto.nombre }}
        <span v-if="producto.marca || producto.modelo" class="text-slate-400 font-medium"> - {{ [producto.marca, producto.modelo].filter(Boolean).join(' ') }}</span>
      </h3>

      <!-- Descripción -->
      <p class="text-sm text-slate-500 line-clamp-2 flex-1">{{ producto.descripcion_corta }}</p>

      <!-- Rating -->
      <div class="flex items-center gap-1.5">
        <div class="flex gap-0.5">
          <template v-for="(tipo, i) in estrellas(producto.rating)" :key="i">
            <svg v-if="tipo === 'full'" class="w-4 h-4 text-amber-400" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>
            <svg v-else-if="tipo === 'half'" class="w-4 h-4 text-amber-300" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>
            <svg v-else class="w-4 h-4 text-slate-200" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>
          </template>
        </div>
        <span class="text-xs text-slate-400">{{ Number(producto.rating).toFixed(1) }} ({{ producto.num_calificaciones }})</span>
      </div>

      <!-- Stock info -->
      <div class="flex items-center gap-1.5 text-xs border-t border-slate-100 pt-3"
           :class="producto.stock < 5 ? 'text-rose-500' : 'text-slate-400'">
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/></svg>
        {{ producto.stock < 5 ? `¡Solo ${producto.stock} disponibles!` : `Stock: ${producto.stock}` }}
      </div>

      <!-- Precio + Acciones -->
      <div class="flex items-center justify-between pt-1">
        <div>
          <span class="text-xs text-slate-400">Precio</span>
          <p class="text-xl font-bold text-teal-700">${{ Number(producto.precio).toLocaleString('es-CO') }}</p>
        </div>
        <div class="flex gap-2">
          <button @click="router.push(`/catalogo/producto/${producto.id}`)"
            class="px-3 py-2 text-sm border border-teal-200 text-teal-700 rounded-xl hover:bg-teal-50 transition-colors font-medium">
            Ver +
          </button>
          <button v-if="puedeComprar"
            class="px-3 py-2 text-sm bg-teal-600 hover:bg-teal-700 text-white rounded-xl transition-colors font-medium shadow-sm">
            Añadir
          </button>
        </div>
      </div>
    </div>
  </article>
</template>
