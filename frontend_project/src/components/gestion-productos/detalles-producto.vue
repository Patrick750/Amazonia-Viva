<script setup>
import { computed, ref, watch, onUnmounted, nextTick } from 'vue';

const props = defineProps({
  abrir: Boolean,
  producto: Object,
  categoriasLista: Array
});
const emit = defineEmits(['cerrar']);

const nombreCategoria = computed(() => {
    if (!props.producto || !props.categoriasLista) return 'Sin categoría';
    const cat = props.categoriasLista.find(c => c.id === props.producto.categorias);
    return cat ? cat.nombre : 'Categoría ID: ' + props.producto.categorias;
});

const formatedPrice = computed(() => {
    if (!props.producto || !props.producto.precio) return '0';
    return parseFloat(props.producto.precio).toLocaleString('es-CO');
});

// --- Carrusel infinito (clone-and-jump) ---
const internalIndex = ref(1);
const isTransitioning = ref(true);
const currentSlide = ref(0);
let autoTimer = null;

const images = computed(() => props.producto?.imagen_producto || []);
const len = computed(() => images.value.length);

const trackImages = computed(() => {
    if (len.value <= 1) return images.value;
    return [images.value[len.value - 1], ...images.value, images.value[0]];
});

const trackStyle = computed(() => ({
    transform: `translateX(-${internalIndex.value * 100}%)`,
    transition: isTransitioning.value ? 'transform 0.55s cubic-bezier(0.4, 0, 0.2, 1)' : 'none',
}));

const onTransitionEnd = () => {
    if (len.value <= 1) return;
    if (internalIndex.value === 0) {
        isTransitioning.value = false;
        internalIndex.value = len.value;
        nextTick(() => { isTransitioning.value = true; });
    } else if (internalIndex.value === len.value + 1) {
        isTransitioning.value = false;
        internalIndex.value = 1;
        nextTick(() => { isTransitioning.value = true; });
    }
    currentSlide.value = internalIndex.value - 1;
};

const startAuto = () => {
    stopAuto();
    if (len.value > 1) {
        autoTimer = setInterval(() => { moveNext(); }, 4000);
    }
};

const stopAuto = () => {
    if (autoTimer) { clearInterval(autoTimer); autoTimer = null; }
};

const moveNext = () => { isTransitioning.value = true; internalIndex.value += 1; };
const movePrev = () => { isTransitioning.value = true; internalIndex.value -= 1; };
const prevSlide = () => { movePrev(); startAuto(); };
const nextSlide = () => { moveNext(); startAuto(); };

const goToSlide = (i) => {
    isTransitioning.value = true;
    internalIndex.value = i + 1;
    currentSlide.value = i;
    startAuto();
};

watch(() => props.producto, () => {
    isTransitioning.value = false;
    internalIndex.value = 1;
    currentSlide.value = 0;
    nextTick(() => {
        isTransitioning.value = true;
        startAuto();
    });
}, { immediate: true });

watch(() => props.abrir, (val) => {
    if (val) startAuto(); else stopAuto();
});
onUnmounted(stopAuto);

</script>

<template>
  <Teleport to="body">
    <!-- Overlay + Modal -->
    <div v-if="abrir && producto"
      class="fixed inset-0 z-[70] flex items-center justify-center p-4 sm:p-6"
      @click.self="emit('cerrar')">

      <div class="absolute inset-0 bg-slate-950/70 backdrop-blur-md"></div>

      <!-- Modal Card -->
      <div class="relative bg-white rounded-3xl shadow-2xl w-full max-w-3xl max-h-[95vh] flex flex-col overflow-hidden animate-fade-in-up">
        
        <!-- HEADER IMAGEN DE FONDO (Galería Carrusel) -->
        <div class="relative h-56 sm:h-72 flex-shrink-0 bg-slate-900 overflow-hidden group">
            
            <template v-if="images.length > 1">
                <!-- Track con clones -->
                <div class="slider-track" :style="trackStyle" @transitionend="onTransitionEnd">
                    <div v-for="(img, i) in trackImages" :key="'tr-'+i" class="slider-slide">
                        <img :src="img.url" :alt="producto.nombre" class="w-full h-full object-cover">
                    </div>
                </div>

                <!-- Flechas y Controles -->
                <button @click.stop="prevSlide" class="absolute left-3 top-1/2 -translate-y-1/2 z-10 w-9 h-9 rounded-full bg-black/40 hover:bg-black/65 backdrop-blur-sm flex items-center justify-center text-white transition-all hover:scale-110 shadow-lg opacity-0 group-hover:opacity-100">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7"/></svg>
                </button>
                <button @click.stop="nextSlide" class="absolute right-3 top-1/2 -translate-y-1/2 z-10 w-9 h-9 rounded-full bg-black/40 hover:bg-black/65 backdrop-blur-sm flex items-center justify-center text-white transition-all hover:scale-110 shadow-lg opacity-0 group-hover:opacity-100">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7"/></svg>
                </button>

                <!-- Dots indicadores -->
                <div class="absolute bottom-6 sm:bottom-8 right-6 flex gap-1.5 z-10">
                    <button v-for="(img, i) in images" :key="'dot-'+i"
                        @click.stop="goToSlide(i)"
                        :class="['w-2 h-2 rounded-full transition-all duration-300', i === currentSlide ? 'bg-white scale-125 shadow-md' : 'bg-white/45 hover:bg-white/70']"
                    />
                </div>
            </template>
            
            <template v-else-if="images.length === 1">
                <img :src="images[0].url" 
                     class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105" :alt="producto.nombre">
            </template>

            <svg v-else class="w-20 h-20 text-slate-700 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
            
            <div class="absolute inset-0 bg-gradient-to-t from-slate-950/90 via-slate-950/20 to-transparent"></div>
            
            <!-- Botón Cerrar -->
            <button @click="emit('cerrar')" class="absolute top-4 right-4 w-10 h-10 flex items-center justify-center rounded-full bg-slate-950/30 hover:bg-red-500 backdrop-blur-md text-white border border-white/20 transition-all z-20">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
            
            <div class="absolute bottom-6 left-6 right-6">
                <!-- Badges -->
                <div class="flex items-center flex-wrap gap-2 mb-2">
                    <span :class="producto.disponible ? 'bg-emerald-500 text-white' : 'bg-red-500 text-white'" class="px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-widest shadow-sm">
                        {{ producto.disponible ? 'ACTIVO' : 'INACTIVO' }}
                    </span>
                    <span class="bg-white/20 backdrop-blur-md border border-white/30 text-white px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-widest shadow-sm">
                        {{ nombreCategoria }}
                    </span>
                    <span v-if="producto.tipo_catalogo" class="bg-blue-500/80 backdrop-blur-md text-white px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-widest shadow-sm">
                        Catálogo: {{ producto.tipo_catalogo }}
                    </span>
                </div>
                <h2 class="text-3xl sm:text-4xl font-bold text-white tracking-tight drop-shadow-md">{{ producto.nombre }}</h2>
                <div class="flex items-center gap-3 mt-1.5 text-slate-300 text-sm font-mono drop-shadow-sm">
                    SKU / Código: {{ producto.sku }}
                </div>
            </div>
        </div>

        <!-- CUERPO DEL DETALLE -->
        <div class="flex-1 overflow-y-auto form-scroll p-6 sm:p-8 space-y-8 bg-slate-50">
            
            <!-- Galería Miniaturas (Si hay múltiples) -->
            <div v-if="images.length > 1" class="flex items-center gap-3 overflow-x-auto pb-2 form-scroll">
                <button v-for="(img, i) in images" :key="'thumb-'+i"
                        @click="goToSlide(i)"
                        :class="['w-16 h-16 rounded-xl overflow-hidden flex-shrink-0 border-2 transition-all', currentSlide === i ? 'border-emerald-500 ring-2 ring-emerald-500/30' : 'border-transparent opacity-70 hover:opacity-100 hover:border-emerald-300']">
                    <img :src="img.url" class="w-full h-full object-cover">
                </button>
            </div>

            <!-- Estadísticas principales -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="bg-white border-2 border-slate-100 rounded-2xl p-4 flex flex-col items-center justify-center shadow-sm md:col-span-2">
                    <span class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1.5 flex items-center gap-1.5">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                        Precio de Venta
                    </span>
                    <span class="text-3xl font-black text-emerald-600">${{ formatedPrice }} <span class="text-sm text-emerald-600/60 font-medium">COP</span></span>
                </div>
                <div class="bg-white border-2 border-slate-100 rounded-2xl p-4 flex flex-col items-center justify-center shadow-sm">
                    <span class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1.5 flex items-center gap-1.5">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/></svg>
                        Stock
                    </span>
                    <span class="text-2xl font-black text-slate-700">{{ producto.stock }}</span>
                </div>
                <div class="bg-white border-2 border-slate-100 rounded-2xl p-4 flex flex-col items-center justify-center shadow-sm">
                    <span class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1.5 flex items-center gap-1.5">
                        <svg class="w-4 h-4 text-teal-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"/></svg>
                        Ventas
                    </span>
                    <span class="text-2xl font-black text-teal-700">{{ producto.ventas_totales || 0 }}</span>
                </div>
            </div>
            
            <!-- Atributos -->
            <div v-if="producto.caracteristicas && producto.caracteristicas.length > 0 && producto.caracteristicas[0].clave" class="bg-white rounded-2xl border-2 border-slate-100 overflow-hidden shadow-sm">
                <div class="px-6 py-4 bg-slate-50 border-b-2 border-slate-100 flex items-center gap-2">
                    <svg class="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                    <h3 class="text-sm font-bold text-slate-700 uppercase tracking-widest">Ficha Técnica Especializada</h3>
                </div>
                <ul class="divide-y divide-slate-100">
                    <li v-for="(carac, i) in producto.caracteristicas" :key="i" class="px-6 py-4 flex flex-col md:flex-row md:items-center justify-between gap-1.5 hover:bg-slate-50 transition-colors">
                        <span class="font-bold text-slate-500 text-sm uppercase tracking-wide">{{ carac.clave }}:</span>
                        <span class="text-slate-800 font-medium text-sm md:text-right">{{ carac.valor }}</span>
                    </li>
                </ul>
            </div>
            
        </div>

      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.animate-fade-in-up {
  animation: fadeInUp 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(16px) scale(0.98); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}
.form-scroll::-webkit-scrollbar { width: 5px; height: 5px; }
.form-scroll::-webkit-scrollbar-track { background: transparent; }
.form-scroll::-webkit-scrollbar-thumb { background-color: #cbd5e1; border-radius: 20px; }

/* Slider Styles */
.slider-track {
    display: flex;
    width: 100%;
    height: 100%;
    transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    will-change: transform;
}
.slider-slide {
    min-width: 100%;
    height: 100%;
    flex-shrink: 0;
}
</style>
