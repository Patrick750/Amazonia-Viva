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

      <div class="absolute inset-0 bg-black/85 backdrop-blur-md"></div>

      <!-- Modal Card -->
      <div class="relative bg-[#0d2114] border border-white/10 rounded-[2.5rem] shadow-2xl w-full max-w-3xl max-h-[95vh] flex flex-col overflow-hidden animate-fade-in-up">
        
        <!-- HEADER IMAGEN DE FONDO (Galería Carrusel) -->
        <div class="relative h-64 sm:h-80 flex-shrink-0 bg-black overflow-hidden group">
            
            <template v-if="images.length > 1">
                <!-- Track con clones -->
                <div class="slider-track" :style="trackStyle" @transitionend="onTransitionEnd">
                    <div v-for="(img, i) in trackImages" :key="'tr-'+i" class="slider-slide">
                        <img :src="img.url" :alt="producto.nombre" class="w-full h-full object-cover">
                    </div>
                </div>

                <!-- Flechas y Controles -->
                <button @click.stop="prevSlide" class="absolute left-4 top-1/2 -translate-y-1/2 z-10 w-11 h-11 rounded-2xl bg-black/40 hover:bg-emerald-500 backdrop-blur-xl flex items-center justify-center text-white transition-all hover:scale-110 shadow-2xl opacity-0 group-hover:opacity-100 border border-white/10">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/></svg>
                </button>
                <button @click.stop="nextSlide" class="absolute right-4 top-1/2 -translate-y-1/2 z-10 w-11 h-11 rounded-2xl bg-black/40 hover:bg-emerald-500 backdrop-blur-xl flex items-center justify-center text-white transition-all hover:scale-110 shadow-2xl opacity-0 group-hover:opacity-100 border border-white/10">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
                </button>

                <!-- Dots indicadores -->
                <div class="absolute bottom-6 sm:bottom-8 right-8 flex gap-2 z-10">
                    <button v-for="(img, i) in images" :key="'dot-'+i"
                        @click.stop="goToSlide(i)"
                        :class="['w-2.5 h-1 rounded-full transition-all duration-500', i === currentSlide ? 'bg-emerald-400 w-6 shadow-[0_0_10px_rgba(52,211,153,0.5)]' : 'bg-white/20 hover:bg-white/40']"
                    />
                </div>
            </template>
            
            <template v-else-if="images.length === 1">
                <img :src="images[0].url" 
                     class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" :alt="producto.nombre">
            </template>

            <svg v-else class="w-24 h-24 text-white/5 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
            
            <div class="absolute inset-0 bg-gradient-to-t from-[#0d2114] via-[#0d2114]/20 to-transparent"></div>
            
            <!-- Botón Cerrar -->
            <button @click="emit('cerrar')" class="absolute top-6 right-6 w-11 h-11 flex items-center justify-center rounded-2xl bg-black/40 hover:bg-rose-500 backdrop-blur-xl text-white border border-white/10 transition-all z-20">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="3" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
            
            <div class="absolute bottom-8 left-8 right-8">
                <!-- Badges -->
                <div class="flex items-center flex-wrap gap-2.5 mb-4">
                    <span :class="producto.disponible ? 'bg-emerald-400 text-black shadow-emerald-400/20' : 'bg-rose-400 text-black shadow-rose-400/20'" class="px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-[0.2em] shadow-xl">
                        {{ producto.disponible ? 'Activo' : 'Inactivo' }}
                    </span>
                    <span class="bg-white/10 backdrop-blur-md border border-white/10 text-white/80 px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-[0.2em] shadow-xl">
                        {{ nombreCategoria }}
                    </span>
                    <span v-if="producto.tipo_catalogo" class="bg-white/10 backdrop-blur-md border border-white/10 text-emerald-400/80 px-3 py-1 rounded-full text-[9px] font-black uppercase tracking-[0.2em] shadow-xl">
                        {{ producto.tipo_catalogo }}
                    </span>
                </div>
                <h2 class="text-3xl sm:text-5xl font-black text-white tracking-tighter drop-shadow-2xl mb-2">{{ producto.nombre }}</h2>
                <div class="flex items-center gap-2 text-white/40 text-[10px] font-black uppercase tracking-widest italic">
                    <span class="bg-white/5 px-2 py-0.5 rounded border border-white/5">SKU: {{ producto.sku }}</span>
                </div>
            </div>
        </div>

        <!-- CUERPO DEL DETALLE -->
        <div class="flex-1 overflow-y-auto custom-scroll p-8 sm:p-10 space-y-10 bg-[#0a1a0f]">
            
            <!-- Galería Miniaturas (Si hay múltiples) -->
            <div v-if="images.length > 1" class="flex items-center gap-4 overflow-x-auto pb-4 custom-scroll">
                <button v-for="(img, i) in images" :key="'thumb-'+i"
                        @click="goToSlide(i)"
                        :class="['w-20 h-20 rounded-2xl overflow-hidden flex-shrink-0 border-2 transition-all duration-300', currentSlide === i ? 'border-emerald-500 scale-105 shadow-2xl shadow-emerald-500/20' : 'border-white/5 opacity-30 hover:opacity-100 hover:border-white/20']">
                    <img :src="img.url" class="w-full h-full object-cover">
                </button>
            </div>

            <!-- Estadísticas principales -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div class="bg-white/5 border border-white/5 rounded-3xl p-6 flex flex-col items-center justify-center shadow-2xl md:col-span-2 group hover:bg-white/8 transition-colors">
                    <span class="text-[9px] font-black text-white/20 uppercase tracking-[0.2em] mb-3 flex items-center gap-2 font-mono">
                        <svg class="w-4 h-4 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                        Valor Comercial
                    </span>
                    <span class="text-4xl font-black text-white tabular-nums group-hover:scale-110 transition-transform duration-500">${{ formatedPrice }} <span class="text-xs text-white/20 font-black tracking-widest uppercase">COP</span></span>
                </div>
                <div class="bg-white/5 border border-white/5 rounded-3xl p-6 flex flex-col items-center justify-center shadow-2xl hover:bg-white/8 transition-colors">
                    <span class="text-[9px] font-black text-white/20 uppercase tracking-[0.2em] mb-3 flex items-center gap-2 font-mono">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/></svg>
                        Stock
                    </span>
                    <span class="text-3xl font-black tabular-nums" :class="producto.stock < 5 ? 'text-rose-400 animate-pulse' : 'text-white/70'">{{ producto.stock }}</span>
                </div>
                <div class="bg-white/5 border border-white/5 rounded-3xl p-6 flex flex-col items-center justify-center shadow-2xl hover:bg-white/8 transition-colors">
                    <span class="text-[9px] font-black text-white/20 uppercase tracking-[0.2em] mb-3 flex items-center gap-2 font-mono">
                        <svg class="w-4 h-4 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"/></svg>
                        Ventas
                    </span>
                    <span class="text-3xl font-black text-emerald-400 tabular-nums">{{ producto.ventas_totales || 0 }}</span>
                </div>
            </div>
            
            <!-- Atributos -->
            <div v-if="producto.caracteristicas && producto.caracteristicas.length > 0 && (producto.caracteristicas[0].clave || producto.caracteristicas[0].valor)" class="bg-white/5 rounded-[2.5rem] border border-white/5 overflow-hidden shadow-2xl">
                <div class="px-8 py-6 bg-white/3 border-b border-white/5 flex items-center gap-4">
                    <div class="w-1.5 h-6 bg-emerald-500 rounded-full"></div>
                    <h3 class="text-[10px] font-black text-white/40 uppercase tracking-[0.2em]">Ficha Técnica Especializada</h3>
                </div>
                <ul class="divide-y divide-white/5">
                    <li v-for="(carac, i) in producto.caracteristicas" :key="i" class="px-8 py-5 flex flex-col md:flex-row md:items-center justify-between gap-2 hover:bg-white/3 transition-all">
                        <span class="font-black text-white/20 text-[10px] uppercase tracking-[0.15em] font-mono">{{ carac.clave }}:</span>
                        <span class="text-emerald-400/80 font-black text-sm md:text-right tracking-tight">{{ carac.valor }}</span>
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
