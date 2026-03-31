<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useCatalogo } from '@/composables/useCatalogo';
import TarjetaTour from '@/components/catalogo/tarjeta-tour.vue';

const router = useRouter();
const { tours, cargandoTours, cargarTours } = useCatalogo();
const rol = ref(localStorage.getItem('rol')).value;

const queryDestino = ref('');
const queryPlan = ref('');

const buscarAventura = () => {
    router.push({ path: '/catalogo/tours', query: { q: queryDestino.value, grupo: queryPlan.value } });
};

// Scroll-based animation tracker
const scrollY = ref(0);
const handleScroll = () => { scrollY.value = window.scrollY; };
const isVisible = ref({});
const observer = ref(null);

onMounted(() => {
    cargarTours();
    window.addEventListener('scroll', handleScroll);

    observer.value = new IntersectionObserver((entries) => {
        entries.forEach(e => {
            if (e.isIntersecting) isVisible.value[e.target.dataset.id] = true;
        });
    }, { threshold: 0.15 });

    document.querySelectorAll('[data-id]').forEach(el => observer.value.observe(el));
});

onUnmounted(() => {
    window.removeEventListener('scroll', handleScroll);
    if (observer.value) observer.value.disconnect();
});

const experiencias = [
    {
        titulo: 'Safari Fluvial',
        subtitulo: 'Ríos que susurran historias',
        desc: 'Navega por los ríos más vírgenes del mundo, encuentra delfines rosados y la magia del atardecer amazónico.',
        img: 'https://images.unsplash.com/photo-1590523741831-ab7e8b8f9c7f?q=80&w=1200&auto=format&fit=crop',
        badge: 'Más popular',
        color: 'from-cyan-500 to-emerald-600',
        icon: 'M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z',
    },
    {
        titulo: 'Trekking Selvático',
        subtitulo: 'El pulmón verde del planeta',
        desc: 'Adéntrate en senderos únicos con guías indígenas, descubre plantas medicinales y la biodiversidad más rica del planeta.',
        img: 'https://images.unsplash.com/photo-1448375240586-882707db888b?q=80&w=1200&auto=format&fit=crop',
        badge: 'Aventura pura',
        color: 'from-emerald-500 to-teal-700',
        icon: 'M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
    },
    {
        titulo: 'Eco-Lodge en la Cima',
        subtitulo: 'Dormir entre las copas',
        desc: 'Pernota sobre el dosel de la selva en refugios sostenibles. Despierta con el canto de guacamayas y monos.',
        img: 'https://images.unsplash.com/photo-1470770903676-69b98201ea1c?q=80&w=1200&auto=format&fit=crop',
        badge: 'Exclusivo',
        color: 'from-amber-500 to-orange-600',
        icon: 'M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z',
    },
    {
        titulo: 'Inmersión Cultural',
        subtitulo: 'Memoria ancestral viva',
        desc: 'Comparte ceremonias, rituales y la sabiduría milenaria de las comunidades yukuna, tikuna y huitoto.',
        img: 'https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?q=80&w=1200&auto=format&fit=crop',
        badge: 'Auténtico',
        color: 'from-purple-500 to-indigo-700',
        icon: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z',
    },
];

const stats = [
    { num: '120+', label: 'Experiencias únicas', icon: 'M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z' },
    { num: '4,800+', label: 'Viajeros satisfechos', icon: 'M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z' },
    { num: '38', label: 'Comunidades aliadas', icon: 'M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z' },
    { num: '98%', label: 'Recomendación', icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' },
];

const valores = [
    { titulo: 'Turismo Responsable', desc: 'Cada reserva contribuye directamente a la conservación del ecosistema y al sustento de las familias locales.', gradient: 'from-emerald-400 to-teal-500', icon: 'M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z' },
    { titulo: 'Guías Certificados', desc: 'Nuestros guías combinan conocimiento ancestral con formación profesional en seguridad y ecoturismo.', gradient: 'from-amber-400 to-orange-500', icon: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z' },
    { titulo: 'Seguridad Garantizada', desc: 'Protocolos estrictos, equipos de emergencia y coordinación con las autoridades locales en cada expedición.', gradient: 'from-blue-400 to-indigo-500', icon: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z' },
];
</script>

<template>
  <div class="min-h-screen bg-[#0a1a0f] overflow-x-hidden font-sans">

    <!-- ══════════════════════════════════════════
         HERO SECTION — Portada épica amazónica
    ══════════════════════════════════════════ -->
    <section class="relative min-h-[100svh] flex flex-col items-center justify-center overflow-hidden">

      <!-- Fondo: imagen saturada con overlay gradient profundo -->
      <div class="absolute inset-0">
        <img
          src="https://images.unsplash.com/photo-1518709268805-4e9042af9f23?q=90&w=2600&auto=format&fit=crop"
          alt="Selva amazónica"
          class="absolute inset-0 w-full h-full object-cover object-center"
        />
        <!-- Gradiente multicapa: oscuro abajo, verde al centro -->
        <div class="absolute inset-0 bg-gradient-to-b from-black/60 via-emerald-950/40 to-[#0a1a0f]"></div>
        <div class="absolute inset-0 bg-gradient-to-r from-black/30 to-transparent"></div>
      </div>

      <!-- Partículas flotantes decorativas (SVG hojas) -->
      <div class="absolute inset-0 pointer-events-none overflow-hidden">
        <svg class="leaf leaf-1 absolute top-[15%] left-[8%] text-emerald-400/30" width="60" height="60" viewBox="0 0 100 100" fill="currentColor">
          <path d="M50 5 C80 5, 95 35, 95 50 C95 75, 70 95, 50 95 C30 95, 5 75, 5 50 C5 25, 20 5, 50 5Z"/>
        </svg>
        <svg class="leaf leaf-2 absolute top-[60%] left-[4%] text-teal-400/20" width="40" height="40" viewBox="0 0 100 100" fill="currentColor">
          <path d="M20 80 C20 80, 80 20, 90 10 C95 5, 100 10, 95 20 C85 50, 30 90, 20 80Z"/>
        </svg>
        <svg class="leaf leaf-3 absolute top-[25%] right-[6%] text-lime-400/25" width="50" height="50" viewBox="0 0 100 100" fill="currentColor">
          <path d="M50 5 C80 5, 95 35, 95 50 C95 75, 70 95, 50 95 C30 95, 5 75, 5 50 C5 25, 20 5, 50 5Z"/>
        </svg>
        <svg class="leaf leaf-4 absolute top-[70%] right-[10%] text-emerald-500/20" width="70" height="70" viewBox="0 0 100 100" fill="currentColor">
          <path d="M20 80 C20 80, 80 20, 90 10 C95 5, 100 10, 95 20 C85 50, 30 90, 20 80Z"/>
        </svg>
        <!-- Círculos de luz / bokeh -->
        <div class="bokeh bokeh-1 absolute top-[30%] left-[20%] w-40 h-40 rounded-full bg-emerald-400/5 blur-3xl"></div>
        <div class="bokeh bokeh-2 absolute bottom-[25%] right-[15%] w-64 h-64 rounded-full bg-teal-300/8 blur-3xl"></div>
      </div>

      <!-- Contenido Hero -->
      <div class="relative z-10 w-full max-w-6xl mx-auto px-6 text-center">

        <!-- Badge superior -->
        <div class="inline-flex items-center gap-2 bg-emerald-500/20 backdrop-blur-md border border-emerald-400/30 text-emerald-300 text-xs font-bold uppercase tracking-[0.2em] px-5 py-2.5 rounded-full mb-8 animate-fade-in">
          <span class="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></span>
          Turismo Amazónico Responsable · Colombia
        </div>

        <h1 class="text-5xl sm:text-7xl md:text-8xl font-black leading-[0.9] tracking-tight text-white mb-6 animate-fade-in delay-100">
          Donde el mundo<br>
          <span class="relative inline-block">
            <span class="text-transparent bg-clip-text bg-gradient-to-r from-emerald-300 via-teal-200 to-lime-300">aún respira.</span>
            <!-- Subrayado decorativo -->
            <svg class="absolute -bottom-2 left-0 w-full" height="8" viewBox="0 0 300 8" preserveAspectRatio="none">
              <path d="M0 6 Q75 0 150 4 Q225 8 300 2" stroke="url(#heroUnderline)" stroke-width="3" fill="none" stroke-linecap="round"/>
              <defs>
                <linearGradient id="heroUnderline" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stop-color="#34d399"/>
                  <stop offset="100%" stop-color="#a3e635"/>
                </linearGradient>
              </defs>
            </svg>
          </span>
        </h1>

        <p class="text-lg md:text-xl text-white/70 max-w-2xl mx-auto mb-12 leading-relaxed animate-fade-in delay-200">
          Expediciones auténticas por la Amazonía colombiana. Conectamos viajeros con comunidades locales, naturaleza virgen y experiencias que transforman.
        </p>

        <!-- Buscador premium -->
        <div class="animate-fade-in delay-300 max-w-3xl mx-auto">
          <div class="bg-white/10 backdrop-blur-xl border border-white/20 rounded-3xl p-2 flex flex-col sm:flex-row gap-2 shadow-2xl shadow-black/40">
            <div class="flex-1 flex items-center gap-3 bg-white/10 rounded-2xl px-5 py-4">
              <svg class="w-5 h-5 text-emerald-300 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
              </svg>
              <input v-model="queryDestino" type="text" placeholder="¿A dónde quieres ir?" class="w-full bg-transparent text-white placeholder-white/40 font-medium focus:outline-none text-sm">
            </div>
            <div class="flex items-center gap-3 bg-white/10 rounded-2xl px-5 py-4 sm:w-48">
              <svg class="w-5 h-5 text-emerald-300 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"/>
              </svg>
              <select v-model="queryPlan" class="w-full bg-transparent text-white/70 font-medium focus:outline-none text-sm appearance-none cursor-pointer">
                <option value="" class="bg-gray-900 text-white">Tipo de plan</option>
                <option value="safari" class="bg-gray-900">Safari / Fauna</option>
                <option value="trekking" class="bg-gray-900">Trekking</option>
                <option value="cultural" class="bg-gray-900">Cultural</option>
                <option value="ecolodge" class="bg-gray-900">Eco-Lodge</option>
              </select>
            </div>
            <button @click="buscarAventura" class="btn-hero-search px-8 py-4 bg-gradient-to-r from-emerald-500 to-teal-500 text-white font-bold rounded-2xl hover:from-emerald-400 hover:to-teal-400 transition-all shadow-lg shadow-emerald-500/30 flex items-center gap-2 justify-center whitespace-nowrap">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
              </svg>
              Explorar
            </button>
          </div>
        </div>

        <!-- Chips sugeridos de búsqueda rápida -->
        <div class="mt-4 flex flex-wrap justify-center gap-2 animate-fade-in delay-400">
          <span class="text-white/40 text-xs mr-1">Populares:</span>
          <button v-for="tag in ['Leticia', 'Puerto Nariño', 'Amazonas', 'Lago Tarapoto']" :key="tag"
            @click="queryDestino = tag; buscarAventura()"
            class="px-3 py-1 text-xs font-medium text-white/60 border border-white/20 rounded-full hover:border-emerald-400/60 hover:text-emerald-300 transition-colors">
            {{ tag }}
          </button>
        </div>
      </div>

      <!-- Scroll indicator -->
      <div class="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2">
        <span class="text-white/30 text-[10px] uppercase tracking-widest">Descubre</span>
        <div class="w-px h-12 bg-gradient-to-b from-white/20 to-transparent relative overflow-hidden">
          <div class="absolute top-0 w-full h-1/2 bg-white/60 animate-scroll-line"></div>
        </div>
      </div>
    </section>

    <!-- ══════════════════════════════════════════
         STATS BAR — Números que generan confianza
    ══════════════════════════════════════════ -->
    <section class="relative bg-gradient-to-r from-emerald-900/80 via-teal-900/80 to-emerald-900/80 border-y border-emerald-500/20 py-10 px-6">
      <!-- SVG decorativo de selva en la base -->
      <div class="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-emerald-400/40 to-transparent"></div>
      <div class="max-w-6xl mx-auto grid grid-cols-2 lg:grid-cols-4 gap-8">
        <div v-for="stat in stats" :key="stat.label" class="text-center group" data-id="stats">
          <div class="w-12 h-12 mx-auto mb-3 rounded-2xl bg-emerald-500/20 border border-emerald-400/20 flex items-center justify-center text-emerald-400 group-hover:scale-110 transition-transform">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" :d="stat.icon"/>
            </svg>
          </div>
          <p class="text-3xl font-black text-white mb-1">{{ stat.num }}</p>
          <p class="text-xs text-emerald-300/70 font-medium uppercase tracking-wider">{{ stat.label }}</p>
        </div>
      </div>
    </section>

    <!-- ══════════════════════════════════════════
         EXPERIENCIAS — Cards inmersivas
    ══════════════════════════════════════════ -->
    <section class="py-28 px-6 relative">
      <!-- Fondo con textura verde oscura -->
      <div class="absolute inset-0 bg-[#0a1a0f]">
        <div class="absolute inset-0 opacity-[0.03]" style="background-image: url('data:image/svg+xml,%3Csvg width=60 height=60 viewBox=0 0 60 60 xmlns=http://www.w3.org/2000/svg%3E%3Cg fill=%22%2310b981%22 fill-rule=evenodd%3E%3Ccircle cx=30 cy=30 r=1/%3E%3C/g%3E%3C/svg%3E')"></div>
      </div>

      <div class="relative max-w-7xl mx-auto">
        <!-- Título de sección -->
        <div class="text-center mb-16" data-id="exp-title">
          <span class="inline-block text-emerald-400 text-xs font-bold uppercase tracking-[0.25em] mb-4 bg-emerald-400/10 px-4 py-2 rounded-full border border-emerald-400/20">Nuestras Experiencias</span>
          <h2 class="text-4xl md:text-6xl font-black text-white leading-tight">
            Cada ruta,<br>
            <span class="text-transparent bg-clip-text bg-gradient-to-r from-emerald-300 to-lime-300">una historia.</span>
          </h2>
          <p class="mt-4 text-white/50 max-w-xl mx-auto">Diseñadas con comunidades locales para una experiencia que honra la selva y sus guardianes.</p>
        </div>

        <!-- Grid de experiencias -->
        <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-6">
          <div v-for="(exp, i) in experiencias" :key="exp.titulo"
            :data-id="`exp-${i}`"
            class="experience-card group relative rounded-3xl overflow-hidden cursor-pointer"
            :class="{ 'visible': isVisible[`exp-${i}`] }"
            :style="{ transitionDelay: `${i * 100}ms` }"
            @click="router.push('/catalogo/tours')">

            <!-- Imagen de fondo -->
            <div class="aspect-[3/4] relative overflow-hidden">
              <img :src="exp.img" :alt="exp.titulo" class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110">
              <!-- Overlay degradado -->
              <div :class="`absolute inset-0 bg-gradient-to-t from-black/90 via-black/30 to-transparent`"></div>
              <!-- Overlay de color al hover -->
              <div :class="`absolute inset-0 bg-gradient-to-br ${exp.color} opacity-0 group-hover:opacity-20 transition-opacity duration-500`"></div>
            </div>

            <!-- Badge -->
            <div class="absolute top-4 left-4">
              <span :class="`px-3 py-1.5 text-[10px] font-black uppercase tracking-widest rounded-full bg-gradient-to-r ${exp.color} text-white shadow-lg`">
                {{ exp.badge }}
              </span>
            </div>

            <!-- Contenido abajo -->
            <div class="absolute bottom-0 left-0 right-0 p-6">
              <div class="mb-3 w-10 h-10 rounded-2xl bg-white/10 backdrop-blur-sm flex items-center justify-center text-white border border-white/20 group-hover:scale-110 transition-transform">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
                  <path stroke-linecap="round" stroke-linejoin="round" :d="exp.icon"/>
                </svg>
              </div>
              <p class="text-white/50 text-xs font-medium uppercase tracking-wider mb-1">{{ exp.subtitulo }}</p>
              <h3 class="text-xl font-black text-white mb-2 leading-tight">{{ exp.titulo }}</h3>
              <p class="text-white/60 text-xs leading-relaxed max-h-0 overflow-hidden group-hover:max-h-24 transition-all duration-500">{{ exp.desc }}</p>
              <div class="mt-4 flex items-center gap-2 text-emerald-300 text-xs font-bold opacity-0 group-hover:opacity-100 translate-y-2 group-hover:translate-y-0 transition-all duration-300">
                Explorar tours
                <svg class="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"/>
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════════════════════════════════════
         TOURS DESTACADOS — Los mejores paquetes
    ══════════════════════════════════════════ -->
    <section class="py-24 px-6 bg-gradient-to-b from-[#0a1a0f] to-[#0d2016]">
      <div class="max-w-7xl mx-auto">
        <div class="flex flex-col md:flex-row justify-between items-end mb-14 gap-6" data-id="tours-header">
          <div>
            <span class="text-emerald-400 font-bold text-xs tracking-[0.2em] uppercase bg-emerald-400/10 px-4 py-2 rounded-full border border-emerald-400/20">Expediciones activas</span>
            <h2 class="text-4xl md:text-5xl font-black text-white mt-4 leading-tight">
              Tours que <span class="text-transparent bg-clip-text bg-gradient-to-r from-emerald-300 to-teal-300">enamoran.</span>
            </h2>
          </div>
          <router-link to="/catalogo/tours" class="flex items-center gap-2 text-emerald-400 font-bold text-sm hover:text-emerald-300 transition-colors border border-emerald-500/30 hover:border-emerald-400/60 rounded-2xl px-5 py-3 group">
            Ver catálogo completo
            <svg class="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"/>
            </svg>
          </router-link>
        </div>

        <!-- Skeleton loading -->
        <div v-if="cargandoTours" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          <div v-for="n in 3" :key="n" class="h-96 bg-emerald-900/30 rounded-3xl animate-pulse border border-emerald-500/10"></div>
        </div>

        <!-- Cards de tours reales -->
        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          <TarjetaTour v-for="tour in tours.slice(0, 3)" :key="tour.id" :tour="tour" :rol="rol" />
        </div>
      </div>
    </section>

    <!-- ══════════════════════════════════════════
         PROPUESTA DE VALOR — Por qué elegirnos
    ══════════════════════════════════════════ -->
    <section class="relative py-28 px-6 overflow-hidden">
      <!-- Fondo: imagen de selva con overlay muy oscuro -->
      <div class="absolute inset-0">
        <img src="https://images.unsplash.com/photo-1448375240586-882707db888b?q=80&w=2000&auto=format&fit=crop" class="w-full h-full object-cover opacity-20" alt="Selva amazónica">
        <div class="absolute inset-0 bg-gradient-to-br from-emerald-950 via-teal-950/90 to-emerald-950"></div>
      </div>

      <!-- Decoración SVG fondo -->
      <svg class="absolute left-0 top-0 h-full w-1/3 text-emerald-900/30" viewBox="0 0 200 800" fill="currentColor" preserveAspectRatio="xMidYMid slice">
        <path d="M-50 900 Q100 600 0 300 Q-80 100 50 0 L0 0 L0 900Z"/>
      </svg>
      <svg class="absolute right-0 bottom-0 h-full w-1/3 text-teal-900/20" viewBox="0 0 200 800" fill="currentColor" preserveAspectRatio="xMidYMid slice">
        <path d="M250 0 Q100 200 200 500 Q280 700 150 800 L200 800 L200 0Z"/>
      </svg>

      <div class="relative max-w-6xl mx-auto">
        <div class="text-center mb-16">
          <span class="text-teal-400 text-xs font-bold uppercase tracking-[0.25em] bg-teal-400/10 px-4 py-2 rounded-full border border-teal-400/20">Nuestro compromiso</span>
          <h2 class="text-4xl md:text-5xl font-black text-white mt-5 leading-tight">
            Más que turismo,<br>
            <span class="text-transparent bg-clip-text bg-gradient-to-r from-teal-300 to-emerald-300">una causa.</span>
          </h2>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div v-for="(val, i) in valores" :key="val.titulo"
            :data-id="`val-${i}`"
            class="valor-card relative bg-white/5 backdrop-blur-sm border border-white/10 rounded-3xl p-8 hover:border-emerald-400/30 transition-all hover:-translate-y-2 hover:shadow-2xl hover:shadow-emerald-900/30 group"
            :class="{ 'visible': isVisible[`val-${i}`] }"
            :style="{ transitionDelay: `${i * 150}ms` }">

            <!-- Icono con gradiente -->
            <div :class="`w-14 h-14 rounded-2xl bg-gradient-to-br ${val.gradient} flex items-center justify-center text-white mb-6 shadow-lg group-hover:scale-110 transition-transform`">
              <svg class="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" :d="val.icon"/>
              </svg>
            </div>

            <!-- Número decorativo -->
            <div class="absolute top-6 right-6 text-6xl font-black text-white/5 select-none">{{ String(i + 1).padStart(2, '0') }}</div>

            <h3 class="text-xl font-bold text-white mb-3">{{ val.titulo }}</h3>
            <p class="text-white/50 text-sm leading-relaxed">{{ val.desc }}</p>

            <!-- Línea activa -->
            <div :class="`mt-6 h-0.5 w-0 group-hover:w-full bg-gradient-to-r ${val.gradient} transition-all duration-500 rounded-full`"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════════════════════════════════════
         CITA / TESTIMONIO inspiracional
    ══════════════════════════════════════════ -->
    <section class="py-20 px-6 relative overflow-hidden">
      <div class="absolute inset-0 bg-gradient-to-r from-emerald-800 via-teal-700 to-emerald-800"></div>
      <!-- Pattern de ondas -->
      <svg class="absolute top-0 left-0 w-full" viewBox="0 0 1440 60" preserveAspectRatio="none" fill="none">
        <path d="M0 0 Q360 60 720 30 Q1080 0 1440 40 L1440 0 Z" fill="#0a1a0f"/>
      </svg>
      <svg class="absolute bottom-0 left-0 w-full" viewBox="0 0 1440 60" preserveAspectRatio="none" fill="none">
        <path d="M0 60 Q360 0 720 30 Q1080 60 1440 20 L1440 60 Z" fill="#0d2016"/>
      </svg>

      <div class="relative max-w-4xl mx-auto text-center py-10">
        <!-- SVG pájaros decorativos -->
        <svg class="absolute top-0 right-10 text-white/10 w-24" viewBox="0 0 100 60" fill="currentColor">
          <path d="M10 30 Q25 10 40 20 Q55 30 70 15 Q85 5 90 20 Q75 25 60 35 Q45 45 30 40 Q15 35 10 30Z"/>
        </svg>
        <svg class="absolute bottom-5 left-10 text-white/10 w-16" viewBox="0 0 100 60" fill="currentColor">
          <path d="M10 30 Q25 10 40 20 Q55 30 70 15 Q85 5 90 20 Q75 25 60 35 Q45 45 30 40 Q15 35 10 30Z"/>
        </svg>

        <svg class="w-12 h-12 mx-auto mb-6 text-white/40" fill="currentColor" viewBox="0 0 24 24">
          <path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.983zm-14.017 0v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151c-2.433.917-3.996 3.638-3.996 5.849h3.983v10h-9.983z"/>
        </svg>

        <p class="text-2xl md:text-3xl font-bold text-white italic leading-relaxed mb-8">
          "La Amazonia no es solo un destino. Es un recordatorio de que hay lugares en el mundo donde la naturaleza todavía manda."
        </p>

        <div class="flex items-center justify-center gap-3">
          <div class="w-10 h-10 rounded-full bg-white/20 border-2 border-white/30 flex items-center justify-center text-white font-bold">A</div>
          <div class="text-left">
            <p class="text-white font-bold text-sm">Amazonia Viva</p>
            <p class="text-white/50 text-xs">Desde el corazón del Amazonas, Colombia</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ══════════════════════════════════════════
         CTA FINAL — Llamado a la acción cinematográfico
    ══════════════════════════════════════════ -->
    <section class="relative py-32 px-6 overflow-hidden">
      <!-- Imagen de fondo con parallax simulado -->
      <div class="absolute inset-0">
        <img src="https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?q=80&w=2000&auto=format&fit=crop" alt="Comunidad amazónica" class="w-full h-full object-cover object-top opacity-30">
        <div class="absolute inset-0 bg-gradient-to-br from-[#0a1a0f] via-emerald-950/70 to-[#0a1a0f]"></div>
      </div>

      <!-- SVG ola superior -->
      <svg class="absolute top-0 left-0 w-full text-[#0d2016]" viewBox="0 0 1440 100" preserveAspectRatio="none" fill="currentColor">
        <path d="M0 0 Q360 80 720 50 Q1080 20 1440 70 L1440 0 Z"/>
      </svg>

      <div class="relative max-w-4xl mx-auto text-center z-10">
        <!-- Decoración: punto verde pulsante -->
        <div class="flex items-center justify-center gap-3 mb-6">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping opacity-75"></span>
          <span class="text-emerald-400 text-xs font-bold uppercase tracking-[0.25em]">Tours disponibles ahora mismo</span>
        </div>

        <h2 class="text-5xl md:text-7xl font-black text-white leading-tight mb-8">
          Tu aventura<br>
          <span class="text-transparent bg-clip-text bg-gradient-to-r from-emerald-300 via-teal-200 to-lime-300">
            empieza hoy.
          </span>
        </h2>

        <p class="text-white/60 text-lg max-w-xl mx-auto mb-12 leading-relaxed">
          Más de 120 experiencias únicas en la selva amazónica. Reserva con una comunidad local y vive algo que nunca olvidarás.
        </p>

        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <router-link to="/catalogo/tours" class="group px-10 py-5 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-white font-bold text-lg rounded-2xl transition-all shadow-2xl shadow-emerald-500/30 flex items-center gap-3 justify-center hover:scale-105">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"/>
            </svg>
            Explorar todos los tours
          </router-link>
          <router-link to="/auth/register" class="px-10 py-5 bg-white/10 backdrop-blur-sm border border-white/20 text-white font-bold text-lg rounded-2xl hover:bg-white/20 hover:border-white/40 transition-all flex items-center gap-3 justify-center">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
            </svg>
            Crear mi cuenta
          </router-link>
        </div>
      </div>
    </section>

  </div>
</template>

<style scoped>
/* ─── Google Fonts ─── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

/* ─── Animations ─── */
.animate-fade-in {
  animation: fadeInUp 0.9s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  opacity: 0;
}
.animate-fade-in.delay-100 { animation-delay: 0.1s; }
.animate-fade-in.delay-200 { animation-delay: 0.2s; }
.animate-fade-in.delay-300 { animation-delay: 0.3s; }
.animate-fade-in.delay-400 { animation-delay: 0.5s; }

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(28px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ─── Scroll Line ─── */
@keyframes scrollLine {
  0%   { top: -50%; }
  100% { top: 150%; }
}
.animate-scroll-line {
  animation: scrollLine 2s ease-in-out infinite;
}

/* ─── Floating Leaves ─── */
.leaf { animation: floatLeaf 8s ease-in-out infinite; }
.leaf-1 { animation-delay: 0s; animation-duration: 9s; }
.leaf-2 { animation-delay: 2s; animation-duration: 11s; }
.leaf-3 { animation-delay: 4s; animation-duration: 8s; }
.leaf-4 { animation-delay: 6s; animation-duration: 12s; }

@keyframes floatLeaf {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  33%       { transform: translateY(-18px) rotate(8deg); }
  66%       { transform: translateY(10px) rotate(-5deg); }
}

/* ─── Bokeh circles ─── */
.bokeh { animation: bokehPulse 6s ease-in-out infinite; }
.bokeh-2 { animation-delay: 3s; }
@keyframes bokehPulse {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50%       { transform: scale(1.3); opacity: 1; }
}

/* ─── Experience Card - entrance animation ─── */
.experience-card {
  opacity: 0;
  transform: translateY(30px);
  transition: opacity 0.7s ease, transform 0.7s ease, box-shadow 0.3s ease;
}
.experience-card.visible {
  opacity: 1;
  transform: translateY(0);
}
.experience-card:hover {
  box-shadow: 0 30px 60px -12px rgba(0, 0, 0, 0.6);
}

/* ─── Valor card entrance ─── */
.valor-card {
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.6s ease, transform 0.6s ease, border-color 0.3s ease, box-shadow 0.3s ease, translate 0.3s ease;
}
.valor-card.visible {
  opacity: 1;
  transform: translateY(0);
}

/* ─── Hero search button ─── */
.btn-hero-search {
  position: relative;
  overflow: hidden;
}
.btn-hero-search::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(to right, transparent, rgba(255,255,255,0.15), transparent);
  transform: translateX(-100%);
  transition: transform 0.5s ease;
}
.btn-hero-search:hover::after {
  transform: translateX(100%);
}

input[type="date"]::-webkit-calendar-picker-indicator {
  filter: invert(1) opacity(0.4);
  cursor: pointer;
}
</style>
