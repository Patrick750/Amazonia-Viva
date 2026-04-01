<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from '@/api/axios';
import { useNotificacion } from '@/composables/useNotificacion';
import { useUserStats } from '@/composables/useUserStats';

const router = useRouter();
const { mostrarNotificacion } = useNotificacion();
const { updateStats } = useUserStats();

const tabActivo = ref('paquetes');
const favoritos = ref([]);
const cargando = ref(true);
const eliminando = ref(null);

const paquetesFavoritos = computed(() => favoritos.value.filter(f => f.tipo === 'paquete'));
const productosFavoritos = computed(() => favoritos.value.filter(f => f.tipo === 'producto'));

const cargarFavoritos = async () => {
    cargando.value = true;
    try {
        const res = await axios.get('api/favoritos/');
        favoritos.value = res.data;
    } catch (e) {
        mostrarNotificacion('No se pudieron cargar los favoritos.', 'error');
    } finally {
        cargando.value = false;
    }
};

const eliminarFavorito = async (id) => {
    eliminando.value = id;
    try {
        await axios.delete(`api/favoritos/${id}/`);
        favoritos.value = favoritos.value.filter(f => f.id !== id);
        mostrarNotificacion('Eliminado de favoritos.', 'exito');
        updateStats();
    } catch (e) {
        mostrarNotificacion('No se pudo eliminar el favorito.', 'error');
    } finally {
        eliminando.value = null;
    }
};

const verDetalle = (item) => {
    if (item.tipo === 'paquete') {
        router.push({ name: 'detalle_tour', params: { id: item.item_id } });
    } else {
        router.push({ name: 'detalle_producto', params: { id: item.item_id } });
    }
};

const formatPrecio = (precio) => {
    return new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(precio);
};

onMounted(cargarFavoritos);
</script>

<template>
  <div class="min-h-screen bg-[#0a1a0f]">

    <!-- ── Hero / Header ─────────────────────────────────── -->
    <section class="relative pt-28 pb-16 overflow-hidden">
      <!-- Degradado fondo -->
      <div class="absolute inset-0 bg-gradient-to-b from-[#0f2318] via-[#0a1a0f] to-[#0a1a0f]"></div>
      <!-- Bokeh decorativo -->
      <div class="absolute top-20 left-1/4 w-72 h-72 rounded-full bg-emerald-500/5 blur-3xl pointer-events-none"></div>
      <div class="absolute bottom-0 right-1/4 w-48 h-48 rounded-full bg-teal-400/5 blur-3xl pointer-events-none"></div>
      <!-- SVG hoja decorativo -->
      <svg class="absolute top-10 right-12 text-emerald-400/10 pointer-events-none" width="120" height="120" viewBox="0 0 100 100" fill="currentColor">
        <path d="M50 5 C80 5,95 35,95 50 C95 75,70 95,50 95 C30 95,5 75,5 50 C5 25,20 5,50 5Z"/>
      </svg>

      <div class="relative z-10 max-w-5xl mx-auto px-6 text-center">
        <!-- Badge -->
        <div class="inline-flex items-center gap-2 bg-emerald-500/15 backdrop-blur border border-emerald-400/25 text-emerald-300 text-xs font-bold uppercase tracking-widest px-5 py-2 rounded-full mb-6">
          <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>
          Tu Colección
        </div>
        <h1 class="text-4xl sm:text-5xl font-black text-white mb-4 leading-tight">
          Tus Próximas
          <span class="text-transparent bg-clip-text bg-gradient-to-r from-emerald-300 via-teal-200 to-lime-300"> Aventuras</span>
        </h1>
        <p class="text-white/50 text-base max-w-xl mx-auto">
          Explora la selección de experiencias y esenciales que has guardado. Tu viaje al corazón de la selva comienza aquí.
        </p>

        <!-- Contadores -->
        <div class="mt-8 flex justify-center gap-6">
          <div class="bg-white/5 border border-white/10 rounded-2xl px-6 py-3 text-center">
            <p class="text-2xl font-black text-emerald-400">{{ paquetesFavoritos.length }}</p>
            <p class="text-white/40 text-xs mt-0.5">Expediciones</p>
          </div>
          <div class="bg-white/5 border border-white/10 rounded-2xl px-6 py-3 text-center">
            <p class="text-2xl font-black text-teal-400">{{ productosFavoritos.length }}</p>
            <p class="text-white/40 text-xs mt-0.5">Productos</p>
          </div>
          <div class="bg-white/5 border border-white/10 rounded-2xl px-6 py-3 text-center">
            <p class="text-2xl font-black text-lime-400">{{ favoritos.length }}</p>
            <p class="text-white/40 text-xs mt-0.5">Total</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Tabs + Contenido ──────────────────────────────── -->
    <section class="max-w-5xl mx-auto px-6 pb-24">

      <!-- Tabs -->
      <div class="flex gap-2 bg-white/5 border border-white/10 rounded-2xl p-1.5 mb-10 w-fit mx-auto">
        <button
          @click="tabActivo = 'paquetes'"
          :class="[
            'relative flex items-center gap-2 px-6 py-3 rounded-xl font-semibold text-sm transition-all duration-300',
            tabActivo === 'paquetes'
              ? 'bg-gradient-to-r from-emerald-600 to-teal-600 text-white shadow-lg shadow-emerald-500/20'
              : 'text-white/50 hover:text-white/80'
          ]"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064"/>
          </svg>
          Paquetes y Expediciones
          <span class="bg-white/20 text-white text-xs font-bold px-1.5 py-0.5 rounded-full">{{ paquetesFavoritos.length }}</span>
        </button>

        <button
          @click="tabActivo = 'productos'"
          :class="[
            'relative flex items-center gap-2 px-6 py-3 rounded-xl font-semibold text-sm transition-all duration-300',
            tabActivo === 'productos'
              ? 'bg-gradient-to-r from-teal-600 to-cyan-600 text-white shadow-lg shadow-teal-500/20'
              : 'text-white/50 hover:text-white/80'
          ]"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
          </svg>
          Accesorios y Productos
          <span class="bg-white/20 text-white text-xs font-bold px-1.5 py-0.5 rounded-full">{{ productosFavoritos.length }}</span>
        </button>
      </div>

      <!-- Estado de carga -->
      <div v-if="cargando" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="i in 6" :key="i" class="bg-white/5 rounded-3xl overflow-hidden animate-pulse">
          <div class="h-52 bg-white/10"></div>
          <div class="p-5 space-y-3">
            <div class="h-3 bg-white/10 rounded-full w-1/3"></div>
            <div class="h-5 bg-white/10 rounded-full w-3/4"></div>
            <div class="h-3 bg-white/10 rounded-full w-1/2"></div>
            <div class="h-10 bg-white/10 rounded-xl mt-4"></div>
          </div>
        </div>
      </div>

      <!-- Tab: Paquetes -->
      <transition name="fade-tab" mode="out-in">
        <div v-if="!cargando && tabActivo === 'paquetes'" key="paquetes">

          <!-- Descripción de la pestaña -->
          <p class="text-white/40 text-sm text-center mb-8 italic">
            Tus itinerarios soñados y escapadas inmersivas por la Amazonía colombiana.
          </p>

          <!-- Empty State Paquetes -->
          <div v-if="paquetesFavoritos.length === 0" class="flex flex-col items-center justify-center py-20 text-center">
            <div class="relative mb-6">
              <div class="w-28 h-28 rounded-full bg-emerald-500/10 flex items-center justify-center">
                <svg class="w-14 h-14 text-emerald-400/40" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064"/>
                </svg>
              </div>
              <div class="absolute -bottom-2 -right-2 w-8 h-8 rounded-full bg-emerald-600/30 flex items-center justify-center">
                <svg class="w-4 h-4 text-emerald-300" fill="currentColor" viewBox="0 0 24 24"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>
              </div>
            </div>
            <h3 class="text-xl font-bold text-white/70 mb-3">El horizonte te espera</h3>
            <p class="text-white/35 text-base max-w-sm mb-8 leading-relaxed">
              Tu lista de expediciones está vacía. Encuentra lodges, caminatas y safaris que despertarán tu espíritu aventurero.
            </p>
            <button @click="router.push('/catalogo/tours')" class="px-8 py-3.5 bg-gradient-to-r from-emerald-600 to-teal-600 text-white font-bold rounded-xl hover:from-emerald-500 hover:to-teal-500 transition-all shadow-lg shadow-emerald-500/25 flex items-center gap-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
              Explorar Expediciones
            </button>
          </div>

          <!-- Grid de tarjetas de paquetes -->
          <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            <div
              v-for="item in paquetesFavoritos"
              :key="item.id"
              class="group relative bg-white/5 border border-white/10 rounded-3xl overflow-hidden hover:border-emerald-500/30 transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl hover:shadow-emerald-500/10 flex flex-col"
            >
              <!-- Imagen -->
              <div class="relative h-52 overflow-hidden bg-[#0f2318] flex-shrink-0">
                <img
                  v-if="item.imagen_portada"
                  :src="item.imagen_portada"
                  :alt="item.nombre"
                  class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
                <div v-else class="w-full h-full flex items-center justify-center">
                  <svg class="w-16 h-16 text-emerald-400/20" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1"><path stroke-linecap="round" stroke-linejoin="round" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945"/></svg>
                </div>
                <!-- Badge tipo -->
                <div class="absolute top-3 left-3">
                  <span class="bg-emerald-600/90 backdrop-blur text-white text-xs font-bold px-3 py-1 rounded-full">{{ item.badge }}</span>
                </div>
                <!-- Botón eliminar -->
                <button
                  @click.stop="eliminarFavorito(item.id)"
                  :disabled="eliminando === item.id"
                  class="absolute top-3 right-3 w-8 h-8 bg-black/50 backdrop-blur rounded-full flex items-center justify-center text-white/60 hover:text-red-400 hover:bg-red-500/20 transition-all opacity-0 group-hover:opacity-100"
                  title="Eliminar de favoritos"
                >
                  <svg v-if="eliminando !== item.id" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                  <svg v-else class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                </button>
              </div>

              <!-- Contenido -->
              <div class="p-5 flex flex-col flex-1">
                <p class="text-emerald-400/70 text-xs font-medium mb-1.5">{{ item.subtitulo }}</p>
                <h3 class="text-white font-bold text-base leading-snug mb-2 line-clamp-2">{{ item.nombre }}</h3>
                <p class="text-white/40 text-xs leading-relaxed line-clamp-2 mb-4">{{ item.descripcion }}</p>
                <div class="mt-auto flex items-center justify-between gap-2">
                  <p class="text-emerald-300 font-black text-lg">{{ formatPrecio(item.precio) }}</p>
                  <button
                    @click="verDetalle(item)"
                    class="px-4 py-2 bg-emerald-600/20 hover:bg-emerald-600/40 border border-emerald-500/30 text-emerald-300 text-xs font-semibold rounded-xl transition-all flex items-center gap-1.5"
                  >
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
                    Explorar itinerario
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </transition>

      <!-- Tab: Productos -->
      <transition name="fade-tab" mode="out-in">
        <div v-if="!cargando && tabActivo === 'productos'" key="productos">

          <!-- Descripción de la pestaña -->
          <p class="text-white/40 text-sm text-center mb-8 italic">
            Equipamiento, artesanías y accesorios listos para tu expedición amazónica.
          </p>

          <!-- Empty State Productos -->
          <div v-if="productosFavoritos.length === 0" class="flex flex-col items-center justify-center py-20 text-center">
            <div class="relative mb-6">
              <div class="w-28 h-28 rounded-full bg-teal-500/10 flex items-center justify-center">
                <svg class="w-14 h-14 text-teal-400/40" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
                </svg>
              </div>
              <div class="absolute -bottom-2 -right-2 w-8 h-8 rounded-full bg-teal-600/30 flex items-center justify-center">
                <svg class="w-4 h-4 text-teal-300" fill="currentColor" viewBox="0 0 24 24"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>
              </div>
            </div>
            <h3 class="text-xl font-bold text-white/70 mb-3">Aún no preparas tu mochila</h3>
            <p class="text-white/35 text-base max-w-sm mb-8 leading-relaxed">
              Explora artículos locales y equipamiento para tu próxima inmersión en la selva y guarda los que más te gusten.
            </p>
            <button @click="router.push('/catalogo/productos')" class="px-8 py-3.5 bg-gradient-to-r from-teal-600 to-cyan-600 text-white font-bold rounded-xl hover:from-teal-500 hover:to-cyan-500 transition-all shadow-lg shadow-teal-500/25 flex items-center gap-2">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
              Descubrir Productos
            </button>
          </div>

          <!-- Grid de tarjetas de productos -->
          <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            <div
              v-for="item in productosFavoritos"
              :key="item.id"
              class="group relative bg-white/5 border border-white/10 rounded-3xl overflow-hidden hover:border-teal-500/30 transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl hover:shadow-teal-500/10 flex flex-col"
            >
              <!-- Imagen -->
              <div class="relative h-52 overflow-hidden bg-[#0f2318] flex-shrink-0">
                <img
                  v-if="item.imagen_portada"
                  :src="item.imagen_portada"
                  :alt="item.nombre"
                  class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
                <div v-else class="w-full h-full flex items-center justify-center">
                  <svg class="w-16 h-16 text-teal-400/20" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1"><path stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/></svg>
                </div>
                <div class="absolute top-3 left-3">
                  <span class="bg-teal-600/90 backdrop-blur text-white text-xs font-bold px-3 py-1 rounded-full">{{ item.badge }}</span>
                </div>
                <button
                  @click.stop="eliminarFavorito(item.id)"
                  :disabled="eliminando === item.id"
                  class="absolute top-3 right-3 w-8 h-8 bg-black/50 backdrop-blur rounded-full flex items-center justify-center text-white/60 hover:text-red-400 hover:bg-red-500/20 transition-all opacity-0 group-hover:opacity-100"
                  title="Eliminar de favoritos"
                >
                  <svg v-if="eliminando !== item.id" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                  <svg v-else class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                </button>
              </div>

              <!-- Contenido -->
              <div class="p-5 flex flex-col flex-1">
                <p class="text-teal-400/70 text-xs font-medium mb-1.5">{{ item.subtitulo }}</p>
                <h3 class="text-white font-bold text-base leading-snug mb-2 line-clamp-2">{{ item.nombre }}</h3>
                <p class="text-white/40 text-xs leading-relaxed line-clamp-2 mb-4">{{ item.descripcion }}</p>
                <div class="mt-auto flex items-center justify-between gap-2">
                  <p class="text-teal-300 font-black text-lg">{{ formatPrecio(item.precio) }}</p>
                  <button
                    @click="verDetalle(item)"
                    class="px-4 py-2 bg-teal-600/20 hover:bg-teal-600/40 border border-teal-500/30 text-teal-300 text-xs font-semibold rounded-xl transition-all flex items-center gap-1.5"
                  >
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
                    Ver detalle
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </transition>

    </section>
  </div>
</template>

<style scoped>
.fade-tab-enter-active,
.fade-tab-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}
.fade-tab-enter-from,
.fade-tab-leave-to {
  opacity: 0;
  transform: translateY(8px);
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
