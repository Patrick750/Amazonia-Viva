<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useCatalogo } from '@/composables/useCatalogo';
import TarjetaTour from '@/components/catalogo/tarjeta-tour.vue';

const router = useRouter();
const { tours, cargandoTours, cargarTours } = useCatalogo();
const rol = ref(localStorage.getItem('rol')).value;

// Formateo del buscador Hero
const queryDestino = ref('');
const queryFecha = ref('');
const queryPlan = ref('');

const buscarAventura = () => {
    // Redigir al catálogo con parámetros (simplificado para esta versión)
    router.push({ 
        path: '/catalogo/tours', 
        query: { q: queryDestino.value, grupo: queryPlan.value } 
    });
};

onMounted(() => {
    cargarTours();
});

const categorias = [
    { id: 1, titulo: 'Inmersión Cultural', desc: 'Vive la esencia de las comunidades.', icon: 'M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-5-9h10v2H7z' },
    { id: 2, titulo: 'Safari de Fauna', desc: 'Encuentra delfines y jaguares.', icon: 'M12 2L4.5 20.29l.71.71L12 18l6.79 3 .71-.71z' },
    { id: 3, titulo: 'Trekking & Selva', desc: 'Rutas por el pulmón del mundo.', icon: 'M14 6l-3.75 5 2.85 3.8-1.6 1.2C9.81 13.75 7 10 7 10l-6 8h22L14 6z' },
    { id: 4, titulo: 'Eco-Lodge & Relax', desc: 'Desconéctate en el paraíso.', icon: 'M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z' },
    { id: 5, titulo: 'Aventura Extrema', desc: 'Desafíos en río abierto.', icon: 'M13 10V3L4 14h7v7l9-11h-7z' }
];

const propuestasValor = [
    { titulo: 'Impacto Positivo', desc: 'Reservas que apoyan la conservación y comunidades locales.', icon: 'M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z' },
    { titulo: 'Guías Expertos', desc: 'Conocimiento ancestral y certificación profesional.', icon: 'M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z' },
    { titulo: 'Seguridad Total', desc: 'Protocolos rigurosos y alianzas con los mejores operadores.', icon: 'M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z' }
];
</script>

<template>
  <div class="min-h-screen bg-white">
    
    <!-- ── SECTION 1: HERO (Impacto e Inmediatez) ── -->
    <section class="relative h-[90vh] flex items-center justify-center overflow-hidden">
      <!-- Fondo: Gradiente Premium con superposición de naturaleza -->
      <div class="absolute inset-0 bg-gradient-to-br from-[#004d40] via-[#00695c] to-[#009688]">
        <div class="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1518709268805-4e9042af9f23?q=80&w=2600&auto=format&fit=crop')] mix-blend-overlay opacity-40 bg-cover bg-center"></div>
        <div class="absolute inset-0 bg-black/20"></div>
      </div>

      <!-- Contenido Hero -->
      <div class="relative z-10 w-full max-w-7xl px-6 text-center text-white space-y-8 animate-fade-in">
        <div class="space-y-4 max-w-4xl mx-auto">
          <h1 class="text-5xl md:text-7xl font-black leading-tight tracking-tight drop-shadow-2xl">
            Donde el corazón del mundo <span class="text-emerald-300">late más fuerte.</span>
          </h1>
          <p class="text-xl md:text-2xl text-emerald-50/90 font-medium max-w-2xl mx-auto">
            Descubre la Amazonía de forma auténtica. Conectamos viajeros con experiencias responsables y guías locales.
          </p>
        </div>

        <!-- Widget de Búsqueda -->
        <div class="bg-white/95 backdrop-blur-md p-3 rounded-[32px] shadow-2xl max-w-4xl mx-auto flex flex-col md:flex-row items-center gap-2 border border-white/20">
          <div class="flex-1 w-full relative">
            <span class="absolute left-6 top-1/2 -translate-y-1/2 text-emerald-600">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
              </svg>
            </span>
            <input v-model="queryDestino" type="text" placeholder="¿A dónde vas?" class="w-full pl-12 pr-6 py-4 bg-transparent text-gray-800 placeholder-gray-400 focus:outline-none font-medium">
          </div>
          <div class="hidden md:block w-px h-10 bg-gray-200"></div>
          <div class="flex-1 w-full relative">
            <span class="absolute left-6 top-1/2 -translate-y-1/2 text-emerald-600">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                <line x1="16" y1="2" x2="16" y2="6"/>
                <line x1="8" y1="2" x2="8" y2="6"/>
                <line x1="3" y1="10" x2="21" y2="10"/>
              </svg>
            </span>
            <input v-model="queryFecha" type="date" class="w-full pl-12 pr-6 py-4 bg-transparent text-gray-800 focus:outline-none font-medium">
          </div>
          <div class="hidden md:block w-px h-10 bg-gray-200"></div>
          <div class="flex-1 w-full relative">
            <span class="absolute left-6 top-1/2 -translate-y-1/2 text-emerald-600">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v1m0 16v1m9-9h1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707m0-11.314l.707.707m11.314 11.314l.707-.707M12 8a4 4 0 100 8 4 4 0 000-8z"/>
              </svg>
            </span>
            <select v-model="queryPlan" class="w-full pl-12 pr-6 py-4 bg-transparent text-gray-800 appearance-none focus:outline-none font-medium cursor-pointer">
              <option value="">Tipo de Plan</option>
              <option value="aventura">Aventura</option>
              <option value="cultural">Cultural</option>
              <option value="relax">Relax</option>
            </select>
          </div>
          <button @click="buscarAventura" class="w-full md:w-auto px-10 py-4 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-[24px] transition-all transform hover:scale-105 active:scale-95 shadow-lg">
            Buscar Aventura
          </button>
        </div>
      </div>
      
      <!-- Indicador de Scroll -->
      <div class="absolute bottom-10 left-1/2 -translate-x-1/2 animate-bounce">
        <svg class="w-6 h-6 text-white/60" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M19 14l-7 7-7-7m14-8l-7 7-7-7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>
      </div>
    </section>

    <!-- ── SECTION 2: CATEGORÍAS ── -->
    <section class="py-24 px-6 max-w-7xl mx-auto text-center">
      <h2 class="text-3xl font-bold text-gray-900 mb-4">¿Cómo quieres vivir la selva?</h2>
      <p class="text-gray-500 mb-16 max-w-xl mx-auto uppercase tracking-widest text-xs font-bold">Explora por categorías</p>
      
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-8">
        <div v-for="cat in categorias" :key="cat.id" class="group cursor-pointer">
          <div class="w-20 h-20 mx-auto mb-6 bg-emerald-50 text-emerald-600 rounded-3xl flex items-center justify-center transition-all group-hover:bg-emerald-600 group-hover:text-white group-hover:rotate-6 group-hover:shadow-xl group-hover:shadow-emerald-100">
            <svg class="w-10 h-10" fill="currentColor" viewBox="0 0 24 24"><path :d="cat.icon"></path></svg>
          </div>
          <h3 class="font-bold text-gray-900 mb-2">{{ cat.titulo }}</h3>
          <p class="text-xs text-gray-500 leading-relaxed">{{ cat.desc }}</p>
        </div>
      </div>
    </section>

    <!-- ── SECTION 3: DESTACADOS (Tours) ── -->
    <section class="py-24 bg-gray-50 px-6">
      <div class="max-w-7xl mx-auto">
        <div class="flex flex-col md:flex-row justify-between items-end mb-16 gap-6">
          <div class="text-left space-y-2">
            <span class="text-emerald-600 font-bold text-sm tracking-widest uppercase">Favoritos de la comunidad</span>
            <h2 class="text-4xl font-black text-gray-900">Expediciones Imperdibles</h2>
          </div>
          <router-link to="/catalogo" class="text-emerald-700 font-bold flex items-center gap-2 group border-b-2 border-transparent hover:border-emerald-700 transition-all pb-1">
            Ver todo el catálogo
            <svg class="w-5 h-5 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M14 5l7 7m0 0l-7 7m7-7H3" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>
          </router-link>
        </div>

        <div v-if="cargandoTours" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          <div v-for="n in 3" :key="n" class="h-96 bg-gray-200 rounded-3xl animate-pulse"></div>
        </div>
        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          <TarjetaTour v-for="tour in tours.slice(0, 3)" :key="tour.id" :tour="tour" :rol="rol" />
        </div>
      </div>
    </section>

    <!-- ── SECTION 4: PROPUESTA DE VALOR ── -->
    <section class="py-24 px-6 max-w-6xl mx-auto text-center">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-16">
        <div v-for="prop in propuestasValor" :key="prop.titulo" class="space-y-6">
          <div class="w-16 h-16 mx-auto bg-emerald-50 rounded-full flex items-center justify-center text-emerald-600 shadow-inner">
            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path :d="prop.icon" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>
          </div>
          <h3 class="text-xl font-bold text-gray-900">{{ prop.titulo }}</h3>
          <p class="text-gray-500 text-sm leading-relaxed">{{ prop.desc }}</p>
        </div>
      </div>
    </section>

    <!-- ── SECTION 5: PRUEBA SOCIAL / CONFIANZA ── -->
    <section class="py-24 border-t border-gray-100 px-6">
      <div class="max-w-7xl mx-auto text-center">
        <h2 class="text-3xl font-bold text-gray-900 mb-12">Nuestros aliados en el paraíso</h2>
        <div class="flex flex-wrap justify-center items-center gap-12 opacity-40 grayscale hover:grayscale-0 transition-all duration-700">
           <!-- Placeholder Logos -->
           <div class="text-lg font-black tracking-tighter">MINCOMERCIO</div>
           <div class="text-lg font-black tracking-tighter italic">ProColombia</div>
           <div class="text-lg font-black tracking-tighter">FONTUR</div>
           <div class="text-lg font-black tracking-tighter">COCORA</div>
           <div class="text-lg font-black tracking-tighter">SATENA</div>
        </div>
      </div>
    </section>

  </div>
</template>

<style scoped>
.animate-fade-in {
  animation: fadeIn 1.2s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

input[type="date"]::-webkit-calendar-picker-indicator {
  cursor: pointer;
  filter: invert(0.5);
}
</style>
