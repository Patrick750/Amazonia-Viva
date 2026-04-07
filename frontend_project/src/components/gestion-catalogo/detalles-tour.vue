<script setup>
import { ref, computed, watch, onUnmounted, nextTick } from 'vue';

const props = defineProps({
  abrir: Boolean,
  paquete: Object,
  actividades: Array
});

const emit = defineEmits(['cerrar']);

// --- Carrusel infinito (clone-and-jump) ---
// El track tiene: [clon_último, slide0, slide1, ..., slideN-1, clon_primero]
// El índice interno empieza en 1 (apuntando al slide real 0).

const internalIndex = ref(1);   // posición real en el track (incluye clones)
const isTransitioning = ref(true);
const currentSlide = ref(0);    // índice lógico 0-based (para dots y miniaturas)
let autoTimer = null;

const images = computed(() => props.paquete?.imagen_paquete || []);
const len = computed(() => images.value.length);

// Track = [último, ...originales, primero]
const trackImages = computed(() => {
    if (len.value <= 1) return images.value;
    return [images.value[len.value - 1], ...images.value, images.value[0]];
});

const trackStyle = computed(() => ({
    transform: `translateX(-${internalIndex.value * 100}%)`,
    transition: isTransitioning.value ? 'transform 0.55s cubic-bezier(0.4, 0, 0.2, 1)' : 'none',
}));

// Al terminar la transición, salta silenciosamente si estamos en un clon
const onTransitionEnd = () => {
    if (len.value <= 1) return;
    if (internalIndex.value === 0) {
        // Salto silencioso: clon del último → real último
        isTransitioning.value = false;
        internalIndex.value = len.value;
        nextTick(() => { isTransitioning.value = true; });
    } else if (internalIndex.value === len.value + 1) {
        // Salto silencioso: clon del primero → real primero
        isTransitioning.value = false;
        internalIndex.value = 1;
        nextTick(() => { isTransitioning.value = true; });
    }
    currentSlide.value = internalIndex.value - 1; // actualiza dot activo
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

const moveNext = () => {
    isTransitioning.value = true;
    internalIndex.value += 1;
};

const movePrev = () => {
    isTransitioning.value = true;
    internalIndex.value -= 1;
};

const prevSlide = () => { movePrev(); startAuto(); };
const nextSlide = () => { moveNext(); startAuto(); };

const goToSlide = (i) => {
    isTransitioning.value = true;
    internalIndex.value = i + 1;  // +1 por el clon del inicio
    currentSlide.value = i;
    startAuto();
};

// Reset al cambiar de paquete
watch(() => props.paquete, () => {
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

// Formatear precio
const formatPrice = (price) => {
    return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        maximumFractionDigits: 0
    }).format(price || 0);
};

const getNombreActividad = (id) => {
    if (!props.actividades) return `Actividad #${id}`;
    const act = props.actividades.find(a => a.id === id);
    return act ? act.nombre : `Actividad #${id}`;
};

</script>

<template>
  <Teleport to="body">
    <div v-if="abrir" class="fixed inset-0 z-[80] flex items-center justify-center p-4 sm:p-6 animate-fade-in" @click.self="emit('cerrar')">
      
      <!-- Backdrop -->
      <div class="absolute inset-0 bg-slate-900/60 backdrop-blur-sm"></div>

      <!-- Modal Card -->
      <div class="relative bg-white rounded-3xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden animate-slide-up border-2 border-slate-100">
        
        <!-- Header / Portada -->
        <div class="relative w-full h-48 sm:h-64 bg-slate-100 flex-shrink-0 overflow-hidden">

            <!-- CARRUSEL INFINITO: más de 1 imagen -->
            <template v-if="images.length > 1">
                <!-- Track con clones: [últimoClón, ...originales, primerClón] -->
                <div class="slider-track" :style="trackStyle" @transitionend="onTransitionEnd">
                    <div v-for="(img, i) in trackImages" :key="i" class="slider-slide">
                        <img :src="img.url" :alt="img.nombre || 'Imagen del Tour'" class="w-full h-full object-cover" />
                    </div>
                </div>

                <!-- Flecha izquierda -->
                <button @click.stop="prevSlide"
                    class="absolute left-3 top-1/2 -translate-y-1/2 z-10 w-9 h-9 rounded-full bg-black/40 hover:bg-black/65 backdrop-blur-sm flex items-center justify-center text-white transition-all hover:scale-110 shadow-lg">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7"/></svg>
                </button>

                <!-- Flecha derecha -->
                <button @click.stop="nextSlide"
                    class="absolute right-3 top-1/2 -translate-y-1/2 z-10 w-9 h-9 rounded-full bg-black/40 hover:bg-black/65 backdrop-blur-sm flex items-center justify-center text-white transition-all hover:scale-110 shadow-lg">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7"/></svg>
                </button>

                <!-- Dots indicadores -->
                <div class="absolute bottom-14 left-1/2 -translate-x-1/2 flex gap-1.5 z-10">
                    <button v-for="(img, i) in images" :key="'dot-'+i"
                        @click.stop="goToSlide(i)"
                        :class="['w-2 h-2 rounded-full transition-all duration-300', i === currentSlide ? 'bg-white scale-125 shadow-md' : 'bg-white/45 hover:bg-white/70']"
                    />
                </div>

                <!-- Contador -->
                <div class="absolute top-4 left-4 z-10 px-2.5 py-1 bg-black/40 backdrop-blur-sm rounded-full text-white text-xs font-semibold">
                    {{ currentSlide + 1 }} / {{ images.length }}
                </div>
            </template>


            <!-- IMAGEN ÚNICA -->
            <template v-else-if="paquete?.imagen_paquete && paquete.imagen_paquete.length === 1">
                <img :src="paquete.imagen_paquete[0].url" alt="Portada del Tour" class="w-full h-full object-cover" />
            </template>

            <!-- SIN IMAGEN -->
            <div v-else class="w-full h-full flex items-center justify-center bg-emerald-50">
                <svg class="w-16 h-16 text-emerald-200" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
            </div>

            <!-- Gradiente para texto overlay -->
            <div class="absolute inset-0 bg-gradient-to-t from-slate-900/80 via-transparent to-transparent pointer-events-none"></div>

            <!-- Boton de cerrar -->
            <button @click="emit('cerrar')" class="absolute top-4 right-4 w-10 h-10 bg-white/20 hover:bg-white/40 backdrop-blur-md rounded-full flex items-center justify-center text-white transition-all hover:rotate-90 z-10">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>

            <!-- Titulo Overlay -->
            <div class="absolute bottom-0 left-0 w-full p-6 sm:px-8 pointer-events-none z-10">
                <div class="flex items-center gap-2 mb-2">
                    <span :class="['px-3 py-1 text-xs font-bold rounded-full border backdrop-blur-sm', paquete?.activo ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30' : 'bg-red-500/20 text-red-300 border-red-500/30']">
                        {{ paquete?.activo ? 'Activo' : 'Inactivo' }}
                    </span>
                    <span class="px-3 py-1 text-xs font-bold rounded-full bg-slate-800/50 text-slate-300 border border-slate-600/50 backdrop-blur-sm">
                        {{ paquete?.duracion }} h
                    </span>
                </div>
                <h2 class="text-3xl sm:text-4xl font-bold text-white drop-shadow-md leading-tight">{{ paquete?.nombre }}</h2>
            </div>
        </div>

        <!-- Body Scrollable -->
        <div class="flex-1 overflow-y-auto detail-scroll p-6 sm:p-8 bg-slate-50/50">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
                
                <!-- Columna Principal -->
                <div class="md:col-span-2 space-y-8">
                    
                    <!-- Descripcion -->
                    <section>
                        <h3 class="text-lg font-bold text-slate-800 mb-3 flex items-center gap-2">
                            <svg class="w-5 h-5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7"/></svg>
                            Acerca del Tour
                        </h3>
                        <p class="text-slate-600 leading-relaxed text-sm sm:text-base">{{ paquete?.descripcion || 'Sin descripción detallada.' }}</p>
                    </section>

                    <!-- Galeria Miniaturas (thumbnails del slider) -->
                    <section v-if="images.length > 1">
                        <div class="flex gap-3 overflow-x-auto pb-2 form-scroll">
                            <button v-for="(img, i) in images" :key="img.id" @click="goToSlide(i)"
                                :class="['relative w-20 h-20 rounded-xl overflow-hidden flex-shrink-0 border-2 transition-all', i === currentSlide ? 'border-emerald-500 scale-105' : 'border-transparent hover:border-emerald-300']">
                                <img :src="img.url" class="w-full h-full object-cover" />
                            </button>
                        </div>
                    </section>

                    <!-- Beneficios (Incluido) -->
                    <section v-if="paquete?.incluido && paquete.incluido.length > 0 && paquete.incluido[0].item !== ''">
                        <h3 class="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
                            <svg class="w-5 h-5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                            ¿Qué incluye?
                        </h3>
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                            <div v-for="(inc, index) in paquete.incluido" :key="'inc-'+index" class="flex items-start gap-3 bg-white p-3.5 rounded-2xl border border-slate-100 shadow-sm">
                                <div class="w-6 h-6 rounded-full bg-emerald-50 flex items-center justify-center flex-shrink-0 mt-0.5">
                                    <svg class="w-3.5 h-3.5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg>
                                </div>
                                <span class="text-slate-700 text-sm font-medium leading-tight">{{ inc.item }}</span>
                            </div>
                        </div>
                    </section>

                    <!-- Itinerario -->
                    <section v-if="paquete?.itinerario && paquete.itinerario.length > 0 && (paquete.itinerario[0].activity !== '' || paquete.itinerario[0].time !== '')">
                        <h3 class="text-lg font-bold text-slate-800 mb-6 flex items-center gap-2">
                            <svg class="w-5 h-5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                            Itinerario
                        </h3>
                        <div class="space-y-6 pl-4 border-l-2 border-emerald-100 relative">
                            <div v-for="(it, index) in paquete.itinerario" :key="'it-'+index" class="relative">
                                <!-- Bullet point -->
                                <div class="absolute -left-[21px] top-1 w-3 h-3 rounded-full bg-emerald-500 border-2 border-white shadow-sm ring-2 ring-emerald-50"></div>
                                
                                <div class="bg-white p-4 rounded-2xl border border-slate-100 shadow-sm ml-4 hover:shadow-md transition-shadow">
                                    <span v-if="it.time" class="inline-block px-2.5 py-1 bg-emerald-50 text-emerald-700 font-bold text-xs rounded-lg mb-2">
                                        {{ it.time }}
                                    </span>
                                    <p class="text-slate-700 font-medium text-sm">{{ it.activity }}</p>
                                </div>
                            </div>
                        </div>
                    </section>
                </div>

                <!-- Barra Lateral (Info Rapida) -->
                <div class="space-y-4">
                    <!-- Tarjeta Info Principal -->
                    <div class="bg-white p-5 rounded-3xl border border-slate-100 shadow-sm">
                        <div class="text-3xl font-black text-emerald-600 mb-1">{{ formatPrice(paquete?.precio) }}</div>
                        <p class="text-xs text-slate-400 font-semibold uppercase tracking-wider mb-6">Precio por persona</p>

                        <div class="space-y-4">
                            <div class="flex items-start gap-3">
                                <div class="w-8 h-8 rounded-xl bg-slate-50 flex items-center justify-center flex-shrink-0">
                                    <svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/></svg>
                                </div>
                                <div>
                                    <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">Capacidad Máxima</p>
                                    <p class="text-sm font-semibold text-slate-800">{{ paquete?.capacidad }} personas</p>
                                </div>
                            </div>

                            <div class="flex items-start gap-3">
                                <div class="w-8 h-8 rounded-xl bg-emerald-50 flex items-center justify-center flex-shrink-0">
                                    <svg class="w-4 h-4 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"/></svg>
                                </div>
                                <div class="flex flex-col">
                                    <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest leading-none mb-1">Éxito en Ventas</p>
                                    <p class="text-sm font-black text-emerald-700">{{ paquete?.ventas_totales || 0 }} unidades</p>
                                </div>
                            </div>

                            <div class="flex items-start gap-3">
                                <div class="w-8 h-8 rounded-xl bg-slate-50 flex items-center justify-center flex-shrink-0">
                                    <svg class="w-4 h-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                                </div>
                                <div>
                                    <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">Punto de encuentro</p>
                                    <p class="text-sm font-semibold text-slate-800 leading-tight">{{ paquete?.ubicacion }}</p>
                                </div>
                            </div>
                            
                            <div v-if="paquete?.latitud && paquete?.longitud" class="flex items-start gap-3 mt-1">
                                <div class="w-8 h-8 flex-shrink-0 pt-0.5"></div>
                                <div class="text-[10px] text-slate-400 font-mono bg-slate-100 px-2 py-1 rounded inline-block">
                                    Lat: {{ Number(paquete.latitud).toFixed(4) }}, Lng: {{ Number(paquete.longitud).toFixed(4) }}
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Actividades Badge -->
                    <div v-if="paquete?.actividades && paquete.actividades.length > 0" class="bg-emerald-600 p-5 rounded-3xl shadow-lg shadow-emerald-200 text-white">
                        <h4 class="font-bold mb-3 flex items-center gap-2">
                            <svg class="w-5 h-5 opacity-80" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"/></svg>
                            Tipos de Aventura
                        </h4>
                        <div class="flex flex-wrap gap-2">
                            <span v-for="act_id in paquete.actividades" :key="'act-'+act_id" class="text-xs font-bold bg-white/20 px-3 py-1.5 rounded-xl backdrop-blur-sm">
                                {{ getNombreActividad(act_id) }}
                            </span>
                        </div>
                    </div>

                </div>
            </div>
        </div>

      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.animate-fade-in { animation: fadeIn 0.25s ease-out forwards; }
.animate-slide-up { animation: slideUp 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards; }

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideUp { from { opacity: 0; transform: translateY(20px) scale(0.98); } to { opacity: 1; transform: translateY(0) scale(1); } }

.detail-scroll::-webkit-scrollbar { width: 6px; }
.detail-scroll::-webkit-scrollbar-track { background: transparent; }
.detail-scroll::-webkit-scrollbar-thumb { background-color: #cbd5e1; border-radius: 20px; }

/* Slider */
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
