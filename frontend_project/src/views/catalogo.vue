<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import TarjetaTour from '@/components/catalogo/tarjeta-tour.vue';
import TarjetaProducto from '@/components/catalogo/tarjeta-producto.vue';
import { useCatalogo } from '@/composables/useCatalogo';

const rol = localStorage.getItem('rol');
const route = useRoute();
const router = useRouter();

// --- TABS ---
const tabActivo = computed(() => route.path.includes('/productos') ? 'productos' : 'tours');

// --- DATOS ---
const {
  tours, productos, categoriasTours,
  cargandoTours, cargandoProductos,
  cargarTours, cargarProductos, cargarCategorias
} = useCatalogo();

const ultimoScrollY = ref(0);
const headerOculto = ref(false);

// --- PAGINACIÓN ---
const paginaActual = ref(1);
const ITEMS_POR_PAGINA = 20;

const toursMostrados = computed(() => {
  const inicio = (paginaActual.value - 1) * ITEMS_POR_PAGINA;
  return toursFiltrados.value.slice(inicio, inicio + ITEMS_POR_PAGINA);
});

const productosMostrados = computed(() => {
  const inicio = (paginaActual.value - 1) * ITEMS_POR_PAGINA;
  return productosFiltrados.value.slice(inicio, inicio + ITEMS_POR_PAGINA);
});

const totalPaginas = computed(() => {
  const total = tabActivo.value === 'tours' ? toursFiltrados.value.length : productosFiltrados.value.length;
  return Math.ceil(total / ITEMS_POR_PAGINA);
});

const cambiarPagina = (p) => {
  if (p < 1 || p > totalPaginas.value) return;
  paginaActual.value = p;
  window.scrollTo({ top: 400, behavior: 'smooth' });
};

const handleScroll = () => {
  const actual = window.scrollY;
  if (actual > ultimoScrollY.value && actual > 200) {
    headerOculto.value = true;
  } else {
    headerOculto.value = false;
  }
  ultimoScrollY.value = actual;
};

onMounted(() => {
  cargarTours();
  cargarProductos();
  cargarCategorias();
  window.addEventListener('scroll', handleScroll);
});

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll);
});

// --- BUSCADOR ---
const busqueda = ref(route.query.q || '');

// --- ORDENAMIENTO ---
const orden = ref(route.query.orden || '');
const filtroUbicacion = ref(route.query.ubicacion || '');
const filtroDuracion = ref(route.query.duracion || '');
const filtroCategoria = ref(route.query.cat || '');
const grupoSeleccionado = ref(route.query.grupo || '');
const filtroRating = ref(Number(route.query.rating) || 0);
const filtroTipo = ref(route.query.tipo || '');  // 'fijo' | 'flexible' | ''
const opcionesDuracion = [
  { value: 'menos4', label: 'Menos de 4h' },
  { value: '4a8',    label: '4h – 8h' },
  { value: 'mas8',   label: 'Más de 8h' },
  { value: 'mas1dia',label: 'Más de 1 día' },
];
const opcionesOrden = [
  { value: '', label: 'Relevancia' },
  { value: 'precio_asc', label: 'Precio: menor a mayor' },
  { value: 'precio_desc', label: 'Precio: mayor a menor' },
  { value: 'rating_desc', label: 'Mejor calificados' },
  { value: 'ventas_desc', label: 'Más vendidos' },
  { value: 'ubicacion', label: 'Por ubicación' },
  { value: 'duracion', label: 'Por duración' },
];
const mostrarMenuOrden = ref(false);
const labelOrden = computed(() => opcionesOrden.find(o => o.value === orden.value)?.label || 'Ordenar');

const parsearHoras = (duracion) => {
  if (!duracion) return null;
  const str = String(duracion).toLowerCase();
  const diasMatch = str.match(/(\d+(?:\.\d+)?)\s*día/);
  if (diasMatch) return parseFloat(diasMatch[1]) * 24;
  const horasMatch = str.match(/(\d+(?:\.\d+)?)/);
  return horasMatch ? parseFloat(horasMatch[1]) : null;
};

// --- CATEGORÍAS ---
const categoriasToursRel = computed(() => {
  const cats = new Set();
  tours.value.forEach(t => { if(t.categoria_paquete_nombre) cats.add(t.categoria_paquete_nombre); });
  return [{ value: '', label: 'Todos' }, ...[...cats].sort().map(c => ({ value: c, label: c }))];
});

const categoriasProductosRel = computed(() => {
  const cats = new Set();
  productos.value.forEach(p => { if(p.nombre_categoria) cats.add(p.nombre_categoria); });
  return [{ value: '', label: 'Todos' }, ...[...cats].sort().map(c => ({ value: c, label: c }))];
});

const categoriaActiva = ref(route.query.seccion || '');

// --- FILTRADO ---
const toursFiltrados = computed(() => {
  let lista = [...tours.value];
  if (busqueda.value.trim()) {
    const terms = busqueda.value.trim().toLowerCase().split(/\s+/);
    lista = lista.filter(t => {
      const s = `${t.nombre} ${t.nombre_agencia} ${t.categoria_paquete_nombre} ${t.ciudad}`.toLowerCase();
      return terms.every(term => s.includes(term));
    });
  }
  if (filtroTipo.value) lista = lista.filter(t => t.tipo_paquete === filtroTipo.value);
  if (categoriaActiva.value) lista = lista.filter(t => t.categoria_paquete_nombre === categoriaActiva.value);
  if (orden.value === 'ubicacion' && filtroUbicacion.value.trim()) {
    const ciudad = filtroUbicacion.value.trim().toLowerCase();
    lista = lista.filter(t => t.ciudad && t.ciudad.toLowerCase().includes(ciudad));
  }
  if (orden.value === 'duracion' && filtroDuracion.value) {
    lista = lista.filter(t => {
      const h = parsearHoras(t.duracion);
      if (h === null) return false;
      if (filtroDuracion.value === 'menos4')  return h < 4;
      if (filtroDuracion.value === '4a8')     return h >= 4 && h <= 8;
      if (filtroDuracion.value === 'mas8')    return h > 8 && h < 24;
      if (filtroDuracion.value === 'mas1dia') return h >= 24;
      return true;
    });
  }
  if (filtroCategoria.value) {
    lista = lista.filter(t => t.categoria_paquete == filtroCategoria.value);
  } else if (grupoSeleccionado.value) {
    const idsEnGrupo = categoriasTours.value
      .filter(c => c.grupo === grupoSeleccionado.value)
      .map(c => c.id);
    lista = lista.filter(t => idsEnGrupo.includes(t.categoria_paquete));
  }
  if (filtroRating.value > 0) {
    lista = lista.filter(t => (t.rating || 0) >= filtroRating.value);
  }
  if (orden.value === 'precio_asc')   lista.sort((a,b) => a.precio - b.precio);
  else if (orden.value === 'precio_desc') lista.sort((a,b) => b.precio - a.precio);
  else if (orden.value === 'rating_desc') lista.sort((a,b) => b.rating - a.rating);
  else if (orden.value === 'ventas_desc') lista.sort((a,b) => (b.reservas_totales || 0) - (a.reservas_totales || 0));
  return lista;
});

const productosFiltrados = computed(() => {
  let lista = [...productos.value];
  if (rol === 'agencia') lista = lista.filter(p => p.tipo_catalogo === 'agencias');
  else if (rol === 'turista') lista = lista.filter(p => p.tipo_catalogo === 'turistas');
  if (categoriaActiva.value) lista = lista.filter(p => p.nombre_categoria === categoriaActiva.value);
  if (busqueda.value.trim()) {
    const terms = busqueda.value.trim().toLowerCase().split(/\s+/);
    lista = lista.filter(p => {
      const s = `${p.nombre} ${p.marca} ${p.modelo} ${p.nombre_proveedor} ${p.nombre_categoria}`.toLowerCase();
      return terms.every(term => s.includes(term));
    });
  }
  if (filtroRating.value > 0) {
    lista = lista.filter(p => (p.rating || 0) >= filtroRating.value);
  }
  if (orden.value === 'precio_asc')   lista.sort((a,b) => a.precio - b.precio);
  else if (orden.value === 'precio_desc') lista.sort((a,b) => b.precio - a.precio);
  else if (orden.value === 'rating_desc') lista.sort((a,b) => b.rating - a.rating);
  else if (orden.value === 'ventas_desc') lista.sort((a,b) => (b.ventas_totales || 0) - (a.ventas_totales || 0));
  return lista;
});

const productosTuristas = computed(() => productosFiltrados.value.filter(p => p.tipo_catalogo === 'turistas'));
const productosAgencias = computed(() => productosFiltrados.value.filter(p => p.tipo_catalogo === 'agencias'));

const itemsActuales = computed(() => tabActivo.value === 'tours' ? toursFiltrados.value : productosFiltrados.value);
const cargando      = computed(() => tabActivo.value === 'tours' ? cargandoTours.value : cargandoProductos.value);
const categoriasActuales = computed(() => tabActivo.value === 'tours' ? categoriasToursRel.value : categoriasProductosRel.value);

const productosTuristasMostrados = computed(() => productosMostrados.value.filter(p => p.tipo_catalogo === 'turistas'));
const productosAgenciasMostrados = computed(() => productosMostrados.value.filter(p => p.tipo_catalogo === 'agencias'));

const hayFiltrosActivos = computed(() =>
  busqueda.value || categoriaActiva.value || filtroCategoria.value ||
  grupoSeleccionado.value || filtroUbicacion.value || filtroDuracion.value || 
  orden.value || filtroRating.value > 0 || filtroTipo.value
);

watch([tabActivo, busqueda, orden, filtroUbicacion, filtroDuracion, filtroCategoria, grupoSeleccionado, categoriaActiva, filtroRating, filtroTipo], () => {
  paginaActual.value = 1; // Resetear página al filtrar
  const query = {
    q: busqueda.value || undefined,
    orden: orden.value || undefined,
    ubicacion: filtroUbicacion.value || undefined,
    duracion: filtroDuracion.value || undefined,
    cat: filtroCategoria.value || undefined,
    grupo: grupoSeleccionado.value || undefined,
    seccion: categoriaActiva.value || undefined,
    rating: filtroRating.value || undefined,
    tipo: filtroTipo.value || undefined,
  };
  router.replace({ query });
});

const limpiarTodosLosFiltros = () => {
  busqueda.value = '';
  categoriaActiva.value = '';
  orden.value = '';
  filtroUbicacion.value = '';
  filtroDuracion.value = '';
  filtroCategoria.value = '';
  grupoSeleccionado.value = '';
  filtroRating.value = 0;
  filtroTipo.value = '';
  router.replace({ query: {} });
};
</script>

<template>
  <div class="min-h-screen bg-[#0a1a0f]" @click="mostrarMenuOrden = false">

    <!-- ═══════════════════════════════════
         HERO COMPACTO DEL CATÁLOGO
    ═══════════════════════════════════ -->
    <section class="relative pt-24 pb-14 px-6 overflow-hidden">
      <!-- Fondo imagen sutil -->
      <div class="absolute inset-0">
        <img
          :src="tabActivo === 'tours'
            ? 'https://images.unsplash.com/photo-1448375240586-882707db888b?q=80&w=2000&auto=format&fit=crop'
            : 'https://images.unsplash.com/photo-1486325212027-8081e485255e?q=80&w=2000&auto=format&fit=crop'"
          alt="Catálogo"
          class="w-full h-full object-cover object-center opacity-15 transition-all duration-700"
        />
        <div class="absolute inset-0 bg-gradient-to-b from-[#0a1a0f]/60 via-transparent to-[#0a1a0f]"></div>
      </div>

      <!-- Hojas decorativas -->
      <svg class="absolute top-8 right-12 w-24 text-emerald-500/10" viewBox="0 0 100 100" fill="currentColor">
        <path d="M50 5 C80 5, 95 35, 95 50 C95 75, 70 95, 50 95 C30 95, 5 75, 5 50 C5 25, 20 5, 50 5Z"/>
      </svg>
      <svg class="absolute bottom-4 left-8 w-16 text-teal-400/10" viewBox="0 0 100 60" fill="currentColor">
        <path d="M20 80 C20 80, 80 20, 90 10 C95 5, 100 10, 95 20 C85 50, 30 90, 20 80Z"/>
      </svg>

      <div class="relative max-w-7xl mx-auto">
        <!-- Breadcrumb -->
        <div class="flex items-center gap-2 text-xs text-white/30 mb-6">
          <router-link to="/" class="hover:text-emerald-400 transition-colors">Inicio</router-link>
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
          <span class="text-white/50">Catálogo</span>
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
          <span class="text-emerald-400 font-semibold capitalize">{{ tabActivo }}</span>
        </div>

        <div class="flex flex-col md:flex-row md:items-end justify-between gap-6">
          <div>
            <span class="inline-block text-emerald-400 text-xs font-bold uppercase tracking-[0.25em] bg-emerald-400/10 px-4 py-1.5 rounded-full border border-emerald-400/20 mb-4">
              {{ tabActivo === 'tours' ? '🌿 Expediciones Amazónicas' : '🎒 Equipamiento y Productos' }}
            </span>
            <h1 class="text-4xl md:text-5xl font-black text-white leading-tight">
              {{ tabActivo === 'tours' ? 'Explora la' : 'Todo lo que' }} <br>
              <span class="text-transparent bg-clip-text bg-gradient-to-r from-emerald-300 to-teal-300">
                {{ tabActivo === 'tours' ? 'Selva Amazónica.' : 'necesitas.' }}
              </span>
            </h1>
          </div>

          <!-- Tabs grandes -->
          <div class="flex gap-3 flex-shrink-0">
            <router-link to="/catalogo/tours"
              :class="['flex items-center gap-2.5 px-6 py-3 rounded-2xl text-sm font-bold border transition-all duration-300',
                tabActivo === 'tours'
                  ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white border-transparent shadow-lg shadow-emerald-500/25'
                  : 'bg-white/5 backdrop-blur-sm text-white/50 border-white/10 hover:border-emerald-400/40 hover:text-white']"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"/>
              </svg>
              Tours
              <span :class="['text-xs px-2 py-0.5 rounded-full font-black', tabActivo === 'tours' ? 'bg-white/20' : 'bg-white/10']">
                {{ tours.length }}
              </span>
            </router-link>
            <router-link to="/catalogo/productos"
              :class="['flex items-center gap-2.5 px-6 py-3 rounded-2xl text-sm font-bold border transition-all duration-300',
                tabActivo === 'productos'
                  ? 'bg-gradient-to-r from-teal-500 to-cyan-500 text-white border-transparent shadow-lg shadow-teal-500/25'
                  : 'bg-white/5 backdrop-blur-sm text-white/50 border-white/10 hover:border-teal-400/40 hover:text-white']"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"/>
              </svg>
              Productos
              <span :class="['text-xs px-2 py-0.5 rounded-full font-black', tabActivo === 'productos' ? 'bg-white/20' : 'bg-white/10']">
                {{ productos.length }}
              </span>
            </router-link>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════════════════════════════
         BARRA DE CONTROLES STICKY
    ═══════════════════════════════════ -->
    <div :class="['sticky top-[72px] z-40 transition-all duration-300',
      headerOculto ? '-translate-y-full opacity-0 pointer-events-none' : 'translate-y-0 opacity-100']">
      <div class="bg-[#0d2016]/95 backdrop-blur-xl border-b border-emerald-500/10 shadow-xl shadow-black/30">
        <div class="max-w-7xl mx-auto px-6 py-4 space-y-4">

          <!-- Row 1: búsqueda + ordenar -->
          <div class="flex items-center gap-3">
            <!-- Campo de búsqueda -->
            <div class="relative flex-1">
              <svg class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-emerald-400/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
              </svg>
              <input
                v-model="busqueda"
                type="text"
                :placeholder="tabActivo === 'tours' ? 'Buscar tours, agencias, destinos...' : 'Buscar productos o proveedores...'"
                class="w-full pl-11 pr-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white text-sm placeholder-white/25 focus:outline-none focus:border-emerald-400/50 focus:bg-white/10 transition-all"
              >
              <button v-if="busqueda" @click="busqueda = ''" class="absolute right-4 top-1/2 -translate-y-1/2 text-white/30 hover:text-white/60 transition-colors">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
              </button>
            </div>

            <!-- Dropdown Ordenar -->
            <div class="relative" @click.stop>
              <button
                @click="mostrarMenuOrden = !mostrarMenuOrden"
                :class="['flex items-center gap-2 px-4 py-2.5 rounded-xl border text-sm font-medium transition-all whitespace-nowrap',
                  orden
                    ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-300'
                    : 'bg-white/5 border-white/10 text-white/50 hover:border-white/25 hover:text-white/80']"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12"/>
                </svg>
                {{ labelOrden }}
                <svg :class="['w-3 h-3 transition-transform', mostrarMenuOrden ? 'rotate-180' : '']" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                </svg>
              </button>
              <transition enter-active-class="transition ease-out duration-100" enter-from-class="opacity-0 scale-95" enter-to-class="opacity-100 scale-100" leave-active-class="transition ease-in duration-75" leave-from-class="opacity-100 scale-100" leave-to-class="opacity-0 scale-95">
                <div v-if="mostrarMenuOrden" class="absolute right-0 mt-2 w-56 bg-[#0d2016] border border-emerald-500/20 rounded-2xl shadow-2xl shadow-black/60 z-50 py-2 overflow-hidden">
                  <button
                    v-for="op in opcionesOrden" :key="op.value"
                    @click="orden = op.value; mostrarMenuOrden = false"
                    :class="['w-full text-left px-4 py-2.5 text-sm transition-colors',
                      orden === op.value ? 'bg-emerald-500/20 text-emerald-300 font-semibold' : 'text-white/60 hover:bg-white/5 hover:text-white']"
                  >{{ op.label }}</button>
                </div>
              </transition>
            </div>

            <!-- Limpiar todo -->
            <button v-if="hayFiltrosActivos" @click="limpiarTodosLosFiltros"
              class="flex items-center gap-1.5 px-4 py-2.5 rounded-xl text-xs font-bold text-red-400/70 border border-red-500/20 hover:bg-red-500/10 hover:text-red-400 hover:border-red-500/40 transition-all whitespace-nowrap">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
              Limpiar
            </button>
          </div>

          <!-- Sub-filtro Ubicación -->
          <transition enter-active-class="transition ease-out duration-200" enter-from-class="opacity-0 -translate-y-2" enter-to-class="opacity-100 translate-y-0" leave-active-class="transition ease-in duration-150" leave-from-class="opacity-100 translate-y-0" leave-to-class="opacity-0 -translate-y-2">
            <div v-if="orden === 'ubicacion' && tabActivo === 'tours'" class="flex items-center gap-3">
              <div class="relative max-w-xs w-full">
                <svg class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-emerald-400/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                </svg>
                <input v-model="filtroUbicacion" type="text" placeholder="Escribe una ciudad..." autofocus
                  class="w-full pl-10 pr-4 py-2 rounded-xl bg-white/5 border border-emerald-500/30 text-white text-sm placeholder-white/25 focus:outline-none focus:border-emerald-400/60 transition-all">
              </div>
            </div>
          </transition>

          <!-- Sub-filtro Duración -->
          <transition enter-active-class="transition ease-out duration-200" enter-from-class="opacity-0 -translate-y-2" enter-to-class="opacity-100 translate-y-0" leave-active-class="transition ease-in duration-150" leave-from-class="opacity-100 translate-y-0" leave-to-class="opacity-0 -translate-y-2">
            <div v-if="orden === 'duracion' && tabActivo === 'tours'" class="flex items-center gap-2 flex-wrap">
              <span class="text-xs text-white/30 mr-1">Rango:</span>
              <button
                v-for="op in opcionesDuracion" :key="op.value"
                @click="filtroDuracion = filtroDuracion === op.value ? '' : op.value"
                :class="['px-3.5 py-1.5 rounded-lg text-xs font-semibold border transition-all duration-200',
                  filtroDuracion === op.value
                    ? 'bg-emerald-500/30 text-emerald-300 border-emerald-500/50'
                    : 'bg-white/5 text-white/50 border-white/10 hover:border-emerald-400/30 hover:text-white/80']"
              >{{ op.label }}</button>
            </div>
          </transition>

          <!-- Filtro Estrellas -->
          <div class="flex items-center gap-2 flex-wrap">
            <span class="text-[10px] font-bold text-white/25 uppercase tracking-widest mr-1">Calificación:</span>
            <button
              v-for="star in [4, 3, 2]" :key="star"
              @click="filtroRating = filtroRating === star ? 0 : star"
              :class="['flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[11px] font-bold border transition-all duration-200',
                filtroRating === star
                  ? 'bg-amber-500/25 text-amber-300 border-amber-500/40 shadow-lg shadow-amber-500/10'
                  : 'bg-white/5 text-white/40 border-white/10 hover:border-amber-400/30 hover:text-white/70']"
            >
              <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>
              {{ star }}+ Estrellas
            </button>
          </div>

          <!-- Filtro Tipo de Paquete (solo Tours) -->
          <div v-if="tabActivo === 'tours'" class="flex items-center gap-2 flex-wrap">
            <span class="text-[10px] font-bold text-white/25 uppercase tracking-widest mr-1">Tipo:</span>
            
            <button
              @click="filtroTipo = filtroTipo === '' ? '' : ''"
              :class="['px-3.5 py-1.5 rounded-lg text-xs font-bold border transition-all duration-200 flex items-center gap-1.5',
                filtroTipo === '' ? 'bg-white/15 text-white border-white/30' : 'bg-white/5 text-white/40 border-white/10 hover:border-white/25 hover:text-white/70']"
            >
              Todos
            </button>

            <button
              @click="filtroTipo = filtroTipo === 'fijo' ? '' : 'fijo'"
              :class="['px-3.5 py-1.5 rounded-lg text-xs font-bold border transition-all duration-200 flex items-center gap-1.5',
                filtroTipo === 'fijo' ? 'bg-blue-500/25 text-blue-300 border-blue-500/40' : 'bg-white/5 text-white/40 border-white/10 hover:border-white/25 hover:text-white/70']"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
              Fijo
            </button>

            <button
              @click="filtroTipo = filtroTipo === 'flexible' ? '' : 'flexible'"
              :class="['px-3.5 py-1.5 rounded-lg text-xs font-bold border transition-all duration-200 flex items-center gap-1.5',
                filtroTipo === 'flexible' ? 'bg-emerald-500/25 text-emerald-300 border-emerald-500/40' : 'bg-white/5 text-white/40 border-white/10 hover:border-white/25 hover:text-white/70']"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
              Flexible
            </button>
          </div>

          <!-- CATEGORÍAS / GRUPOS -->
          <div class="space-y-3">
            <!-- Tours: grupos -->
            <div v-if="tabActivo === 'tours'" class="space-y-3">
              <div class="flex items-center gap-2 flex-wrap">
                <span class="text-[10px] font-bold text-white/25 uppercase tracking-widest mr-1">Grupos:</span>
                <button
                  v-for="grupo in [...new Set(categoriasTours.map(c => c.grupo))]" :key="grupo"
                  @click="grupoSeleccionado = (grupo === grupoSeleccionado ? '' : grupo); filtroCategoria = ''"
                  :class="['px-4 py-1.5 rounded-lg text-xs font-bold border transition-all duration-200',
                    grupoSeleccionado === grupo
                      ? 'bg-emerald-500/25 text-emerald-300 border-emerald-500/40'
                      : 'bg-white/5 text-white/40 border-white/10 hover:border-emerald-400/30 hover:text-white/70']"
                >{{ grupo }}</button>
              </div>
              <transition enter-active-class="transition ease-out duration-200" enter-from-class="opacity-0 -translate-y-1" enter-to-class="opacity-100 translate-y-0">
                <div v-if="grupoSeleccionado" class="flex items-center gap-2 flex-wrap border-t border-white/5 pt-3">
                  <span class="text-[10px] font-bold text-white/20 uppercase tracking-widest mr-1">Subcategoría:</span>
                  <button
                    v-for="cat in categoriasTours.filter(c => c.grupo === grupoSeleccionado)" :key="cat.id"
                    @click="filtroCategoria = filtroCategoria === cat.id ? '' : cat.id"
                    :class="['px-3 py-1.5 rounded-lg text-[11px] font-semibold border transition-all duration-200',
                      filtroCategoria === cat.id
                        ? 'bg-teal-500/25 text-teal-300 border-teal-500/40'
                        : 'bg-white/5 text-white/35 border-white/10 hover:border-teal-400/30 hover:text-white/60']"
                  >{{ cat.nombre }}</button>
                </div>
              </transition>
            </div>

            <!-- Productos: categorías -->
            <div v-else class="flex items-center gap-2 flex-wrap">
              <span class="text-[10px] font-bold text-white/25 uppercase tracking-widest mr-1">Categorías:</span>
              <button
                v-for="cat in categoriasActuales" :key="cat.value"
                @click="categoriaActiva = cat.value"
                :class="['px-4 py-1.5 rounded-lg text-xs font-semibold border transition-all duration-200',
                  categoriaActiva === cat.value
                    ? 'bg-teal-500/25 text-teal-300 border-teal-500/40'
                    : 'bg-white/5 text-white/40 border-white/10 hover:border-teal-400/30 hover:text-white/70']"
              >{{ cat.label }}</button>
            </div>
          </div>

        </div>
      </div>
    </div>

    <!-- ═══════════════════════════════════
         CONTENIDO PRINCIPAL
    ═══════════════════════════════════ -->
    <main class="max-w-7xl mx-auto px-6 py-10">

      <!-- Contador de resultados -->
      <div class="flex items-center justify-between mb-8">
        <p class="text-sm text-white/40">
          <span class="font-bold text-emerald-400 text-lg">{{ itemsActuales.length }}</span>
          <span class="ml-1.5">{{ tabActivo === 'tours' ? 'tours' : 'productos' }} encontrados</span>
          <span v-if="busqueda" class="ml-1.5 text-emerald-400/70 italic">"{{ busqueda }}"</span>
        </p>
        <!-- Info tabs -->
        <span class="hidden sm:flex items-center gap-2 text-xs text-white/20">
          <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          Actualizando en tiempo real
        </span>
      </div>

      <!-- Loading skeletons -->
      <div v-if="cargando" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="n in 6" :key="n" class="rounded-3xl overflow-hidden border border-white/5 animate-pulse">
          <div class="h-52 bg-emerald-900/30"></div>
          <div class="p-5 space-y-3 bg-white/5">
            <div class="h-4 bg-white/10 rounded-full w-3/4"></div>
            <div class="h-3 bg-white/5 rounded-full w-full"></div>
            <div class="h-3 bg-white/5 rounded-full w-5/6"></div>
            <div class="h-9 bg-emerald-900/40 rounded-2xl w-full mt-4"></div>
          </div>
        </div>
      </div>

      <!-- Estado vacío -->
      <div v-else-if="itemsActuales.length === 0 && !(!rol && tabActivo === 'productos')"
        class="flex flex-col items-center py-32 text-center">
        <div class="relative w-28 h-28 mb-8">
          <div class="absolute inset-0 rounded-full bg-emerald-500/10 animate-ping"></div>
          <div class="relative w-28 h-28 rounded-full bg-emerald-900/50 border border-emerald-500/20 flex items-center justify-center">
            <svg class="w-12 h-12 text-emerald-500/50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
            </svg>
          </div>
        </div>
        <h3 class="text-2xl font-bold text-white/60 mb-2">Sin resultados</h3>
        <p class="text-white/30 text-sm max-w-xs mb-8">Ningún {{ tabActivo === 'tours' ? 'tour' : 'producto' }} coincide con tu búsqueda. Prueba con otros términos o elimina los filtros.</p>
        <button @click="limpiarTodosLosFiltros"
          class="px-6 py-3 rounded-2xl text-sm font-bold border border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/10 transition-all hover:border-emerald-400/60">
          Quitar todos los filtros
        </button>
      </div>

      <!-- TOURS GRID -->
      <div v-else-if="tabActivo === 'tours'" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <TarjetaTour v-for="tour in toursMostrados" :key="'t-' + tour.id" :tour="tour" :rol="rol" />
      </div>

      <!-- PRODUCTOS GRID (usuario con rol) -->
      <div v-else-if="tabActivo === 'productos' && rol" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <TarjetaProducto v-for="prod in productosMostrados" :key="'p-' + prod.id" :producto="prod" :rol="rol" />
      </div>

      <!-- PRODUCTOS GRID (sin rol — secciones divididas) -->
      <div v-else-if="tabActivo === 'productos' && !rol" class="space-y-16">
        <div v-if="productosTuristasMostrados.length > 0">
          <div class="flex items-center gap-4 mb-8">
            <div class="w-10 h-10 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center text-white shadow-lg shadow-emerald-500/25">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
              </svg>
            </div>
            <div>
              <h2 class="text-2xl font-black text-white">Para Turistas</h2>
              <p class="text-xs text-white/30">{{ productosTuristas.length }} productos disponibles</p>
            </div>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            <TarjetaProducto v-for="prod in productosTuristasMostrados" :key="'pt-' + prod.id" :producto="prod" :rol="rol" />
          </div>
        </div>

        <div v-if="productosAgenciasMostrados.length > 0">
          <div class="flex items-center gap-4 mb-8">
            <div class="w-10 h-10 rounded-2xl bg-gradient-to-br from-teal-500 to-cyan-500 flex items-center justify-center text-white shadow-lg shadow-teal-500/25">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
              </svg>
            </div>
            <div>
              <h2 class="text-2xl font-black text-white">Para Agencias</h2>
              <p class="text-xs text-white/30">{{ productosAgencias.length }} productos disponibles</p>
            </div>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            <TarjetaProducto v-for="prod in productosAgenciasMostrados" :key="'pa-' + prod.id" :producto="prod" :rol="rol" />
          </div>
        </div>
      </div>

      <!-- PAGINACIÓN UI -->
      <div v-if="totalPaginas > 1" class="mt-16 flex justify-center items-center gap-2">
        <button
          @click="cambiarPagina(paginaActual - 1)"
          :disabled="paginaActual === 1"
          class="p-2.5 rounded-xl border border-white/10 text-white/50 hover:bg-white/5 hover:text-white disabled:opacity-20 disabled:cursor-not-allowed transition-all"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
          </svg>
        </button>

        <div class="flex items-center gap-1.5 px-2">
          <button
            v-for="p in totalPaginas" :key="p"
            @click="cambiarPagina(p)"
            :class="['w-10 h-10 rounded-xl text-sm font-bold transition-all duration-300',
              paginaActual === p
                ? 'bg-gradient-to-br from-emerald-500 to-teal-500 text-white shadow-lg shadow-emerald-500/30 scale-110'
                : 'bg-white/5 text-white/40 border border-white/5 hover:border-emerald-500/30 hover:text-white']"
          >
            {{ p }}
          </button>
        </div>

        <button
          @click="cambiarPagina(paginaActual + 1)"
          :disabled="paginaActual === totalPaginas"
          class="p-2.5 rounded-xl border border-white/10 text-white/50 hover:bg-white/5 hover:text-white disabled:opacity-20 disabled:cursor-not-allowed transition-all"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
          </svg>
        </button>
      </div>

    </main>

    <!-- Separador de ola al fondo -->
    <div class="h-px bg-gradient-to-r from-transparent via-emerald-500/20 to-transparent my-8"></div>

  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
</style>
