<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import TarjetaTour from '@/components/catalogo/tarjeta-tour.vue';
import TarjetaProducto from '@/components/catalogo/tarjeta-producto.vue';
import { useCatalogo } from '@/composables/useCatalogo';

const rol = localStorage.getItem('rol');

// --- TABS ---
const tabActivo = ref('tours'); // 'tours' | 'productos'

// --- DATOS ---
const { 
  tours, productos, categoriasTours, 
  cargandoTours, cargandoProductos, 
  cargarTours, cargarProductos, cargarCategorias 
} = useCatalogo();

const ultimoScrollY = ref(0);
const headerOculto = ref(false);

const handleScroll = () => {
  const actual = window.scrollY;
  // Ocultar si bajamos y pasamos un umbral, mostrar si subimos
  if (actual > ultimoScrollY.value && actual > 150) {
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
const busqueda = ref('');

// --- ORDENAMIENTO ---
const orden = ref('');
const filtroUbicacion = ref('');
const filtroDuracion = ref(''); // '' | 'menos4' | '4a8' | 'mas8' | 'mas1dia'
const filtroCategoria = ref(''); // ID de la subcategoría
const grupoSeleccionado = ref(''); // Para navegar grupos de categorías
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
  { value: 'ubicacion', label: 'Ubicación' },
  { value: 'duracion', label: 'Duración' },
];
const mostrarMenuOrden = ref(false);
const labelOrden = computed(() => opcionesOrden.find(o => o.value === orden.value)?.label || 'Ordenar por');

// Parsear duración: acepta '3', '3h', '3 h', '2 días', '2 dias', etc. → número de horas
const parsearHoras = (duracion) => {
  if (!duracion) return null;
  const str = String(duracion).toLowerCase();
  const diasMatch = str.match(/(\d+(?:\.\d+)?)\s*día/);
  if (diasMatch) return parseFloat(diasMatch[1]) * 24;
  const horasMatch = str.match(/(\d+(?:\.\d+)?)/);
  return horasMatch ? parseFloat(horasMatch[1]) : null;
};

// --- CATEGORÍAS/FILTROS POR TABS ---
const categoriasToursRel = computed(() => {
  const cats = new Set();
  tours.value.forEach(t => { if(t.categoria_paquete_nombre) cats.add(t.categoria_paquete_nombre) });
  return [{ value: '', label: 'Todos' }, ...[...cats].sort().map(c => ({ value: c, label: c }))];
});

const categoriasProductosRel = computed(() => {
  const cats = new Set();
  productos.value.forEach(p => { if(p.nombre_categoria) cats.add(p.nombre_categoria) });
  return [{ value: '', label: 'Todos' }, ...[...cats].sort().map(c => ({ value: c, label: c }))];
});

const categoriaActiva = ref('');

// --- FILTRADO Y ORDENAMIENTO ---
const nivelRiesgoMax = { bajo: [0,3], moderado: [4,6], alto: [7,8], extremo: [9,10] };

const toursFiltrados = computed(() => {
  let lista = [...tours.value];
  if (busqueda.value.trim()) {
    const q = busqueda.value.trim().toLowerCase();
    lista = lista.filter(t => 
      t.nombre.toLowerCase().includes(q) || 
      (t.nombre_agencia && t.nombre_agencia.toLowerCase().includes(q)) || 
      (t.categoria_paquete_nombre && t.categoria_paquete_nombre.toLowerCase().includes(q))
    );
  }
  if (categoriaActiva.value) {
    lista = lista.filter(t => t.categoria_paquete_nombre === categoriaActiva.value);
  }
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
  // Filtro por Categorías (Nueva funcionalidad)
  if (filtroCategoria.value) {
    // Filtrado por subcategoría específica
    lista = lista.filter(t => t.categoria_paquete == filtroCategoria.value);
  } else if (grupoSeleccionado.value) {
    // Filtrado por grupo completo
    const idsEnGrupo = categoriasTours.value
      .filter(c => c.grupo === grupoSeleccionado.value)
      .map(c => c.id);
    lista = lista.filter(t => idsEnGrupo.includes(t.categoria_paquete));
  }
  if (orden.value === 'precio_asc') lista.sort((a,b) => a.precio - b.precio);
  else if (orden.value === 'precio_desc') lista.sort((a,b) => b.precio - a.precio);
  else if (orden.value === 'rating_desc') lista.sort((a,b) => b.rating - a.rating);
  return lista;
});

const productosFiltrados = computed(() => {
  let lista = [...productos.value];
  // Filtro por rol
  if (rol === 'agencia') lista = lista.filter(p => p.tipo_catalogo === 'agencias');
  else if (rol === 'turista' || !rol) lista = lista.filter(p => p.tipo_catalogo === 'turistas');
  // Filtro categoría
  if (categoriaActiva.value) lista = lista.filter(p => p.nombre_categoria === categoriaActiva.value);
  // Búsqueda
  if (busqueda.value.trim()) {
    const q = busqueda.value.trim().toLowerCase();
    lista = lista.filter(p => 
      p.nombre.toLowerCase().includes(q) || 
      (p.nombre_proveedor && p.nombre_proveedor.toLowerCase().includes(q)) || 
      (p.nombre_categoria && p.nombre_categoria.toLowerCase().includes(q))
    );
  }
  if (orden.value === 'precio_asc') lista.sort((a,b) => a.precio - b.precio);
  else if (orden.value === 'precio_desc') lista.sort((a,b) => b.precio - a.precio);
  else if (orden.value === 'rating_desc') lista.sort((a,b) => b.rating - a.rating);
  return lista;
});

const itemsActuales = computed(() => tabActivo.value === 'tours' ? toursFiltrados.value : productosFiltrados.value);
const cargando = computed(() => tabActivo.value === 'tours' ? cargandoTours.value : cargandoProductos.value);
const categoriasActuales = computed(() => tabActivo.value === 'tours' ? categoriasToursRel.value : categoriasProductosRel.value);

watch(tabActivo, () => {
  categoriaActiva.value = '';
  orden.value = '';
  filtroUbicacion.value = '';
  filtroDuracion.value = '';
  filtroCategoria.value = '';
  grupoSeleccionado.value = '';
});
</script>

<template>
  <div class="min-h-screen bg-gray-50 px-6 pb-10 max-w-7xl mx-auto" @click="mostrarMenuOrden = false">

    <!-- CONTENEDOR STICKY COMPONENTIZADO -->
    <div :class="['sticky top-[78px] z-40 bg-gray-50/95 backdrop-blur-md pt-6 pb-4 mb-6 -mx-6 px-6 border-b border-gray-200/60 shadow-sm transition-all duration-300 ease-in-out', 
      headerOculto ? '-translate-y-full opacity-0 pointer-events-none' : 'translate-y-0 opacity-100']">
      

    <!-- Tabs -->
    <div class="flex gap-2 mb-6">
      <button
        @click="tabActivo = 'tours'"
        :class="['flex items-center gap-2 px-5 py-2 rounded-full text-sm font-semibold transition-all duration-200 border',
          tabActivo === 'tours'
            ? 'bg-emerald-600 text-white border-emerald-600 shadow-sm'
            : 'bg-white text-gray-500 border-gray-200 hover:border-emerald-300 hover:text-emerald-700']"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
        </svg>
        Tours
      </button>
      <button
        @click="tabActivo = 'productos'"
        :class="['flex items-center gap-2 px-5 py-2 rounded-full text-sm font-semibold transition-all duration-200 border',
          tabActivo === 'productos'
            ? 'bg-teal-600 text-white border-teal-600 shadow-sm'
            : 'bg-white text-gray-500 border-gray-200 hover:border-teal-300 hover:text-teal-700']"
      >
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"/>
        </svg>
        Productos
      </button>
    </div>

    <!-- Barra de control: búsqueda + ordenamiento -->
    <div class="flex items-center gap-3 mb-5">
      <!-- Campo de búsqueda tipo píldora -->
      <div class="relative flex-1">
        <svg class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
        <input
          v-model="busqueda"
          type="text"
          :placeholder="tabActivo === 'tours' ? 'Buscar tours o agencias...' : 'Buscar productos o proveedores...'"
          class="w-full pl-12 pr-5 py-3 rounded-full border border-gray-200 bg-white text-sm text-gray-700 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-transparent shadow-sm transition"
        >
      </div>

      <!-- Botón ordenamiento tipo píldora con dropdown -->
      <div class="relative" @click.stop>
        <button
          @click="mostrarMenuOrden = !mostrarMenuOrden"
          class="flex items-center gap-2 px-5 py-3 rounded-full border border-gray-200 bg-white text-sm font-medium text-gray-600 hover:border-emerald-400 hover:text-emerald-700 shadow-sm transition whitespace-nowrap"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12"/>
          </svg>
          {{ labelOrden }}
          <svg class="w-4 h-4 transition-transform" :class="mostrarMenuOrden ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
          </svg>
        </button>
        <transition enter-active-class="transition ease-out duration-100" enter-from-class="opacity-0 scale-95" enter-to-class="opacity-100 scale-100" leave-active-class="transition ease-in duration-75" leave-from-class="opacity-100 scale-100" leave-to-class="opacity-0 scale-95">
          <div v-if="mostrarMenuOrden" class="absolute right-0 mt-2 w-52 bg-white border border-gray-100 rounded-2xl shadow-lg z-50 py-2 overflow-hidden">
            <button
              v-for="op in opcionesOrden" :key="op.value"
              @click="orden = op.value; mostrarMenuOrden = false"
              :class="['w-full text-left px-4 py-2.5 text-sm transition-colors', orden === op.value ? 'bg-emerald-50 text-emerald-700 font-semibold' : 'text-gray-600 hover:bg-gray-50']"
            >{{ op.label }}</button>
          </div>
        </transition>
      </div>
    </div>

    <!-- Campo de ciudad (visible solo cuando se selecciona Ubicación) -->
    <transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="opacity-0 -translate-y-1"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-1"
    >
      <div v-if="orden === 'ubicacion' && tabActivo === 'tours'" class="flex items-center gap-3 mb-5">
        <div class="relative flex-1 max-w-xs">
          <svg class="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
          </svg>
          <input
            v-model="filtroUbicacion"
            type="text"
            placeholder="Escribe una ciudad..."
            autofocus
            class="w-full pl-10 pr-4 py-2.5 rounded-full border border-emerald-300 bg-white text-sm text-gray-700 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:border-transparent shadow-sm transition"
          >
        </div>
        <button
          v-if="filtroUbicacion"
          @click="filtroUbicacion = ''"
          class="text-xs text-gray-400 hover:text-gray-600 transition"
        >Limpiar</button>
      </div>
    </transition>

    <!-- Chips de duración (visible solo cuando se selecciona Duración) -->
    <transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="opacity-0 -translate-y-1"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-1"
    >
      <div v-if="orden === 'duracion' && tabActivo === 'tours'" class="flex items-center gap-2 flex-wrap mb-5">
        <span class="flex items-center gap-1.5 text-sm text-gray-500 mr-1">
          <svg class="w-4 h-4 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <circle cx="12" cy="12" r="10" stroke-width="2"/>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6l4 2"/>
          </svg>
          Rango:
        </span>
        <button
          v-for="op in opcionesDuracion" :key="op.value"
          @click="filtroDuracion = filtroDuracion === op.value ? '' : op.value"
          :class="['px-4 py-1.5 rounded-full text-sm font-medium border transition-all duration-200',
            filtroDuracion === op.value
              ? 'bg-emerald-600 text-white border-emerald-600'
              : 'bg-white text-gray-500 border-gray-200 hover:border-emerald-300 hover:text-emerald-700']"
        >{{ op.label }}</button>
        <button
          v-if="filtroDuracion"
          @click="filtroDuracion = ''"
          class="text-xs text-gray-400 hover:text-gray-600 transition ml-1"
        >Limpiar</button>
      </div>
    </transition>

    <!-- PANEL DE CATEGORÍAS UNIFICADO (Promovido al frente) -->
    <section class="mb-8 space-y-4 bg-white/60 p-6 rounded-[2.5rem] border border-emerald-100/50 shadow-sm backdrop-blur-sm animate-fade-in-up">
      
      <!-- Lógica para TOURS (Grupos + Subcategorías) -->
      <div v-if="tabActivo === 'tours'" class="space-y-4">
        <!-- Grupos de Categorías -->
        <div class="flex items-center gap-3 flex-wrap">
          <span class="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] mr-2">Filtrar por Grupo:</span>
          <button
            v-for="grupo in [...new Set(categoriasTours.map(c => c.grupo))]" :key="grupo"
            @click="grupoSeleccionado = grupo === grupoSeleccionado ? '' : grupo; filtroCategoria = ''"
            :class="['px-5 py-2 rounded-full text-xs font-bold border transition-all duration-300 uppercase tracking-wider',
              grupoSeleccionado === grupo
                ? 'bg-emerald-600 text-white border-emerald-600 shadow-lg shadow-emerald-200/50 scale-105'
                : 'bg-white text-gray-500 border-gray-100 hover:border-emerald-300 hover:text-emerald-700 hover:shadow-md']"
          >{{ grupo }}</button>
        </div>

        <!-- Subcategorías (Mostradas al seleccionar un grupo) -->
        <div v-if="grupoSeleccionado" class="flex items-center gap-2 flex-wrap border-t border-emerald-50/50 pt-5 animate-slide-down">
          <span class="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] mr-2">Subcategoría:</span>
          <button
            v-for="cat in categoriasTours.filter(c => c.grupo === grupoSeleccionado)" :key="cat.id"
            @click="filtroCategoria = filtroCategoria === cat.id ? '' : cat.id"
            :class="['px-4 py-2 rounded-full text-[11px] font-bold border transition-all duration-200',
              filtroCategoria === cat.id
                ? 'bg-emerald-50 text-emerald-700 border-emerald-400 ring-2 ring-emerald-400/20'
                : 'bg-white text-gray-400 border-gray-100 hover:border-emerald-200 hover:text-emerald-600']"
          >{{ cat.nombre }}</button>
        </div>
      </div>

      <!-- Lógica para PRODUCTOS (Filtro por nombre de categoría similar a chips) -->
      <div v-else class="flex flex-wrap gap-2 items-center">
        <span class="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] mr-4">Categorías de Productos:</span>
        <button
          v-for="cat in categoriasActuales" :key="cat.value"
          @click="categoriaActiva = cat.value"
          :class="['flex items-center gap-2 px-5 py-2 rounded-full text-sm font-semibold border transition-all duration-300',
            categoriaActiva === cat.value
              ? 'bg-teal-600 text-white border-teal-600 shadow-lg shadow-teal-100 scale-105'
              : 'bg-white text-gray-500 border-gray-100 hover:border-teal-300 hover:text-teal-700 hover:shadow-sm']"
        >{{ cat.label }}</button>
      </div>
      
      <!-- Botón Limpiar para ambos -->
      <div v-if="filtroCategoria || grupoSeleccionado || categoriaActiva" class="flex justify-end pt-2">
        <button
          @click="filtroCategoria = ''; grupoSeleccionado = ''; categoriaActiva = ''"
          class="text-[10px] font-bold text-gray-400 hover:text-red-500 transition-colors uppercase tracking-[0.2em] flex items-center gap-1.5 px-3 py-1 rounded-full hover:bg-red-50"
        >
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
          Limpiar Filtros de Categoría
        </button>
      </div>
    </section>

    </div> <!-- CIERRE CONTENEDOR STICKY -->

    <!-- Contador de resultados -->
    <p class="text-sm text-gray-400 mb-6">
      <span class="font-semibold text-gray-600">{{ itemsActuales.length }}</span>
      {{ tabActivo === 'tours' ? ' tours' : ' productos' }} encontrados
      <span v-if="busqueda" class="text-emerald-600"> · "{{ busqueda }}"</span>
    </p>

    <!-- Estado de carga — skeletons -->
    <div v-if="cargando" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="n in 6" :key="n" class="bg-white rounded-2xl overflow-hidden shadow-sm animate-pulse">
        <div class="h-52 bg-gray-200"></div>
        <div class="p-5 space-y-3">
          <div class="flex gap-1"><div v-for="s in 5" :key="s" class="w-4 h-4 rounded bg-gray-200"></div></div>
          <div class="h-4 bg-gray-200 rounded w-3/4"></div>
          <div class="h-3 bg-gray-100 rounded w-full"></div>
          <div class="h-3 bg-gray-100 rounded w-5/6"></div>
          <div class="h-8 bg-gray-200 rounded-full w-full mt-4"></div>
        </div>
      </div>
    </div>

    <!-- Estado vacío / No encontrado -->
    <div v-else-if="itemsActuales.length === 0" class="flex flex-col items-center py-24 text-center">
      <div class="w-20 h-20 rounded-full bg-gray-100 flex items-center justify-center mb-5">
        <svg class="w-9 h-9 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
      </div>
      <h3 class="text-xl font-bold text-gray-500 mb-1">No encontrado</h3>
      <p class="text-gray-400 text-sm max-w-xs">Ningún resultado coincide con tu búsqueda. Prueba otros términos o cambia los filtros.</p>
      <button @click="busqueda = ''; categoriaActiva = ''" class="mt-5 px-5 py-2 rounded-full text-sm font-semibold border border-emerald-300 text-emerald-700 hover:bg-emerald-50 transition">Limpiar filtros</button>
    </div>

    <!-- Grid de tarjetas -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      <TarjetaTour v-if="tabActivo === 'tours'"
        v-for="tour in toursFiltrados" :key="'t-' + tour.id"
        :tour="tour" :rol="rol"
      />
      <TarjetaProducto v-if="tabActivo === 'productos'"
        v-for="prod in productosFiltrados" :key="'p-' + prod.id"
        :producto="prod" :rol="rol"
      />
    </div>

  </div>
</template>
