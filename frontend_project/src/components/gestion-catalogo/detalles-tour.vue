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
      <div class="absolute inset-0 bg-[#06120b]/90 backdrop-blur-md"></div>

      <!-- Modal Card -->
      <div class="relative bg-[#0d2114] rounded-[2.5rem] shadow-[0_0_100px_rgba(0,0,0,0.8)] w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden animate-slide-up border border-white/10">
        
        <!-- Header / Portada -->
        <div class="relative w-full h-56 sm:h-80 bg-black/40 flex-shrink-0 overflow-hidden">

            <!-- CARRUSEL INFINITO -->
            <template v-if="images.length > 1">
                <div class="slider-track" :style="trackStyle" @transitionend="onTransitionEnd">
                    <div v-for="(img, i) in trackImages" :key="i" class="slider-slide">
                        <img :src="img.url" :alt="img.nombre || 'Imagen del Tour'" class="w-full h-full object-cover transition-transform duration-[2000ms] group-hover:scale-110" />
                    </div>
                </div>

                <!-- Flechas -->
                <div class="absolute inset-x-4 top-1/2 -translate-y-1/2 flex justify-between pointer-events-none z-20">
                    <button @click.stop="prevSlide"
                        class="pointer-events-auto w-12 h-12 rounded-2xl bg-black/40 hover:bg-emerald-500 hover:text-black backdrop-blur-xl flex items-center justify-center text-white transition-all hover:scale-110 shadow-2xl border border-white/5">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/></svg>
                    </button>
                    <button @click.stop="nextSlide"
                        class="pointer-events-auto w-12 h-12 rounded-2xl bg-black/40 hover:bg-emerald-500 hover:text-black backdrop-blur-xl flex items-center justify-center text-white transition-all hover:scale-110 shadow-2xl border border-white/5">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
                    </button>
                </div>

                <!-- Dots e Indicador -->
                <div class="absolute bottom-10 left-1/2 -translate-x-1/2 flex items-center gap-4 z-20">
                    <div class="flex gap-2 p-2 rounded-full bg-black/40 backdrop-blur-xl border border-white/5">
                        <button v-for="(img, i) in images" :key="'dot-'+i"
                            @click.stop="goToSlide(i)"
                            :class="['w-2 h-2 rounded-full transition-all duration-500', i === currentSlide ? 'bg-emerald-400 w-6' : 'bg-white/20 hover:bg-white/40']"
                        />
                    </div>
                </div>

                <!-- Contador Premium -->
                <div class="absolute top-6 left-6 z-20 px-4 py-2 bg-black/60 backdrop-blur-xl rounded-xl border border-white/10 text-white font-black text-[10px] uppercase tracking-[0.2em] shadow-2xl">
                    {{ currentSlide + 1 }} <span class="text-white/30 px-1">/</span> {{ images.length }}
                </div>
            </template>

            <!-- IMAGEN ÚNICA -->
            <template v-else-if="paquete?.imagen_paquete && paquete.imagen_paquete.length === 1">
                <img :src="paquete.imagen_paquete[0].url" alt="Portada del Tour" class="w-full h-full object-cover" />
            </template>

            <!-- SIN IMAGEN -->
            <div v-else class="w-full h-full flex flex-col items-center justify-center bg-[#0a1a0f]">
                <div class="w-20 h-20 rounded-3xl bg-emerald-500/5 border border-emerald-500/10 flex items-center justify-center mb-4">
                  <svg class="w-10 h-10 text-emerald-500/40" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                </div>
                <span class="text-[10px] font-black text-emerald-500/20 uppercase tracking-[0.3em]">Sin Registro Visual</span>
            </div>

            <!-- Gradientes Overlay -->
            <div class="absolute inset-0 bg-gradient-to-t from-[#0d2114] via-transparent to-black/40 pointer-events-none"></div>
            <div class="absolute inset-0 bg-gradient-to-r from-[#0d2114]/60 via-transparent to-transparent pointer-events-none"></div>

            <!-- Boton de cerrar -->
            <button @click="emit('cerrar')" class="absolute top-6 right-6 w-12 h-12 bg-white/10 hover:bg-rose-500 text-white backdrop-blur-xl rounded-2xl flex items-center justify-center transition-all hover:rotate-90 z-30 border border-white/10 shadow-2xl">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>

            <!-- Titulo Overlay -->
            <div class="absolute bottom-0 left-0 w-full p-8 sm:px-10 pointer-events-none z-20">
                <div class="flex flex-wrap items-center gap-3 mb-4">
                    <span :class="['px-4 py-2 text-[9px] font-black uppercase tracking-widest rounded-xl border-2 shadow-2xl backdrop-blur-xl', 
                      paquete?.activo ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border-rose-500/20']">
                        <div class="flex items-center gap-2">
                          <span class="w-1.5 h-1.5 rounded-full animate-pulse" :class="paquete?.activo ? 'bg-emerald-400' : 'bg-rose-400'"></span>
                          {{ paquete?.activo ? 'Servicio Operativo' : 'Servicio Suspendido' }}
                        </div>
                    </span>
                    <span class="px-4 py-2 text-[9px] font-black uppercase tracking-widest rounded-xl bg-white/5 text-white/60 border border-white/10 backdrop-blur-xl">
                        {{ paquete?.duracion }} HS DURACIÓN
                    </span>
                </div>
                <h2 class="text-4xl sm:text-5xl font-black text-white leading-tight tracking-tight drop-shadow-[0_4px_10px_rgba(0,0,0,0.5)]">
                  {{ paquete?.nombre }}
                </h2>
            </div>
        </div>

        <!-- Body Scrollable -->
        <div class="flex-1 overflow-y-auto detail-scroll p-8 sm:p-10 bg-[#0d2114]">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-10">
                
                <!-- Columna Principal -->
                <div class="md:col-span-2 space-y-12">
                    
                    <!-- Descripcion -->
                    <section class="relative">
                        <div class="flex items-center gap-4 mb-6">
                            <div class="w-10 h-10 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center flex-shrink-0 shadow-lg shadow-emerald-500/5">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h7"/></svg>
                            </div>
                            <h3 class="text-xs font-black text-white/40 uppercase tracking-[0.2em]">Crónica y Experiencia</h3>
                            <div class="flex-1 h-px bg-gradient-to-r from-white/10 to-transparent"></div>
                        </div>
                        <p class="text-white/60 leading-relaxed font-medium text-sm sm:text-base selection:bg-emerald-500 selection:text-black">
                          {{ paquete?.descripcion || 'Esta travesía espera ser documentada pronto.' }}
                        </p>
                    </section>

                    <!-- Galeria Miniaturas -->
                    <section v-if="images.length > 1" class="pt-4">
                        <div class="flex gap-4 overflow-x-auto pb-4 form-scroll">
                            <button v-for="(img, i) in images" :key="img.id" @click="goToSlide(i)"
                                :class="['relative w-24 h-24 rounded-[1.5rem] overflow-hidden flex-shrink-0 border-2 transition-all duration-500', 
                                i === currentSlide ? 'border-emerald-500 scale-105 shadow-[0_0_20px_rgba(16,185,129,0.3)]' : 'border-white/5 hover:border-white/10 grayscale hover:grayscale-0']">
                                <img :src="img.url" class="w-full h-full object-cover" />
                            </button>
                        </div>
                    </section>

                    <!-- Beneficios (Incluido) -->
                    <section v-if="paquete?.incluido && paquete.incluido.length > 0 && paquete.incluido[0].item !== ''">
                        <div class="flex items-center gap-4 mb-8">
                            <div class="w-10 h-10 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center flex-shrink-0">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>
                            </div>
                            <h3 class="text-xs font-black text-white/40 uppercase tracking-[0.2em]">Servicios de Altura</h3>
                            <div class="flex-1 h-px bg-gradient-to-r from-white/10 to-transparent"></div>
                        </div>
                        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                            <div v-for="(inc, index) in paquete.incluido" :key="'inc-'+index" class="flex items-center gap-4 bg-white/5 p-5 rounded-3xl border border-white/5 hover:border-white/10 transition-all group">
                                <div class="w-8 h-8 rounded-xl bg-emerald-500/20 flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                                    <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="3.5"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>
                                </div>
                                <span class="text-white/80 text-sm font-black tracking-tight">{{ inc.item }}</span>
                            </div>
                        </div>
                    </section>

                    <!-- Itinerario -->
                    <section v-if="paquete?.itinerario && paquete.itinerario.length > 0 && (paquete.itinerario[0].activity !== '' || paquete.itinerario[0].time !== '')">
                        <div class="flex items-center gap-4 mb-10">
                            <div class="w-10 h-10 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center flex-shrink-0">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                            </div>
                            <h3 class="text-xs font-black text-white/40 uppercase tracking-[0.2em]">Hoja de Ruta</h3>
                            <div class="flex-1 h-px bg-gradient-to-r from-white/10 to-transparent"></div>
                        </div>
                        <div class="space-y-10 pl-5 border-l-4 border-white/5 relative">
                            <div v-for="(it, index) in paquete.itinerario" :key="'it-'+index" class="relative">
                                <div class="absolute -left-[30px] top-1 w-6 h-6 rounded-xl bg-[#0d2114] border-4 border-emerald-500 shadow-[0_0_15px_rgba(16,185,129,0.5)] z-10 flex items-center justify-center overflow-hidden">
                                    <div class="w-1 h-1 rounded-full bg-white animate-ping"></div>
                                </div>
                                
                                <div class="bg-white/5 p-6 rounded-3xl border border-white/5 ml-6 hover:bg-white/10 hover:border-emerald-500/30 transition-all group scale-100 hover:scale-[1.02]">
                                    <div class="flex items-center justify-between mb-3">
                                      <span v-if="it.time" class="inline-flex px-3 py-1 bg-emerald-500 text-black font-black text-[10px] rounded-lg shadow-xl uppercase tracking-widest font-mono">
                                          {{ it.time }}
                                      </span>
                                      <span class="text-[9px] font-black text-white/10 uppercase tracking-[0.3em]">Hito {{ index + 1 }}</span>
                                    </div>
                                    <p class="text-white/80 font-bold text-sm group-hover:text-white transition-colors">{{ it.activity }}</p>
                                </div>
                            </div>
                        </div>
                    </section>
                </div>

                <!-- Barra Lateral (Info Rapida) -->
                <div class="space-y-6">
                    <!-- Tarjeta Info Principal -->
                    <div class="bg-emerald-500/5 rounded-[2.5rem] border border-emerald-500/10 p-8 text-center relative overflow-hidden group">
                        <div class="absolute inset-0 bg-emerald-500/5 blur-3xl opacity-0 group-hover:opacity-100 transition-opacity"></div>
                        
                        <div class="relative z-10">
                          <div class="text-[10px] text-emerald-500/60 font-black uppercase tracking-[0.3em] mb-4">Valor de Expedición</div>
                          <div class="text-5xl font-black text-white mb-2 tabular-nums">{{ formatPrice(paquete?.precio) }}</div>
                          <p class="text-[9px] text-white/30 font-black uppercase tracking-widest mb-10 pb-10 border-b border-white/5">Inversión por explorador</p>

                          <div class="space-y-6 text-left">
                              <div class="flex items-center gap-4">
                                  <div class="w-10 h-10 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center flex-shrink-0">
                                      <svg class="w-5 h-5 text-white/40" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/></svg>
                                  </div>
                                  <div>
                                      <p class="text-[9px] font-black text-white/20 uppercase tracking-widest leading-none mb-1">Capacidad Máxima</p>
                                      <p class="text-sm font-black text-white">{{ paquete?.capacidad }} Exploradores</p>
                                  </div>
                              </div>

                              <div class="flex items-center gap-4">
                                  <div class="w-10 h-10 rounded-2xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center flex-shrink-0">
                                      <svg class="w-5 h-5 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"/></svg>
                                  </div>
                                  <div>
                                      <p class="text-[9px] font-black text-emerald-500/40 uppercase tracking-widest leading-none mb-1">Impacto en Mercado</p>
                                      <p class="text-sm font-black text-emerald-400">{{ paquete?.reservas_totales || 0 }} Adquisiciones</p>
                                  </div>
                              </div>

                              <div class="flex items-center gap-4">
                                  <div class="w-10 h-10 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center flex-shrink-0">
                                      <svg class="w-5 h-5 text-white/40" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/><path stroke-linecap="round" stroke-linejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                                  </div>
                                  <div class="flex-1">
                                      <p class="text-[9px] font-black text-white/20 uppercase tracking-widest leading-none mb-1">Punto de Encuentro</p>
                                      <p class="text-xs font-black text-white leading-tight italic truncate w-40">{{ paquete?.ubicacion }}</p>
                                      <div class="mt-2 text-[8px] font-mono text-emerald-500/40 bg-emerald-500/5 px-2 py-1 rounded-lg inline-block border border-emerald-500/10">
                                          GPS: {{ Number(paquete?.latitud).toFixed(5) }}, {{ Number(paquete?.longitud).toFixed(5) }}
                                      </div>
                                  </div>
                              </div>
                          </div>
                        </div>
                    </div>

                    <!-- Actividades Badge -->
                    <div v-if="paquete?.actividades && paquete.actividades.length > 0" class="bg-emerald-600 rounded-[2.5rem] p-8 shadow-[0_20px_50px_rgba(5,150,105,0.2)] text-black relative overflow-hidden group">
                        <div class="absolute -right-10 -bottom-10 w-40 h-40 bg-black/10 rounded-full blur-3xl group-hover:scale-150 transition-transform duration-1000"></div>
                        
                        <h4 class="font-black text-xs uppercase tracking-[0.2em] mb-6 flex items-center gap-3 relative z-10">
                            <svg class="w-5 h-5 transform group-hover:rotate-12 transition-transform" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"/></svg>
                            Categorías de Aventura
                        </h4>
                        <div class="flex flex-wrap gap-2 relative z-10">
                            <span v-for="act_id in paquete.actividades" :key="'act-'+act_id" class="text-[10px] font-black bg-black/10 px-4 py-2 rounded-xl backdrop-blur-xl border border-black/5 uppercase tracking-widest hover:bg-black/20 transition-all cursor-default">
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
.animate-fade-in { animation: fadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
.animate-slide-up { animation: slideUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards; }

@keyframes fadeIn { from { opacity: 0; backdrop-filter: blur(0px); } to { opacity: 1; backdrop-filter: blur(8px); } }
@keyframes slideUp { from { opacity: 0; transform: translateY(40px) scale(0.95); } to { opacity: 1; transform: translateY(0) scale(1); } }

.detail-scroll::-webkit-scrollbar { width: 5px; }
.detail-scroll::-webkit-scrollbar-track { background: transparent; }
.detail-scroll::-webkit-scrollbar-thumb { background-color: rgba(255, 255, 255, 0.05); border-radius: 20px; }
.detail-scroll::-webkit-scrollbar-thumb:hover { background-color: rgba(16, 185, 129, 0.2); }

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
