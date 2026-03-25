<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import TarjetaTour from '@/components/catalogo/tarjeta-tour.vue';
import TarjetaProducto from '@/components/catalogo/tarjeta-producto.vue';
import { useCatalogo } from '@/composables/useCatalogo';

const rol = localStorage.getItem('rol');

// --- TABS ---
const tabActivo = ref('tours'); // 'tours' | 'productos'

// --- DATOS ---
const { tours, productos, cargandoTours, cargandoProductos, cargarTours, cargarProductos } = useCatalogo();
onMounted(() => { cargarTours(); cargarProductos(); });

// --- BUSCADOR ---
const busqueda = ref('');

// --- ORDENAMIENTO ---
const orden = ref('');
const opcionesOrden = [
  { value: '', label: 'Relevancia' },
  { value: 'precio_asc', label: 'Precio: menor a mayor' },
  { value: 'precio_desc', label: 'Precio: mayor a menor' },
  { value: 'rating_desc', label: 'Mejor calificados' },
];
const mostrarMenuOrden = ref(false);
const labelOrden = computed(() => opcionesOrden.find(o => o.value === orden.value)?.label || 'Ordenar por');

// --- CATEGORÍAS/FILTROS POR TABS ---
// TOURS: filtrar por nivel de riesgo (categoría funcional)
const categoriasTours = [
  { value: '', label: 'Todos', color: null },
  { value: 'bajo', label: 'Bajo riesgo', color: '#10b981' },
  { value: 'moderado', label: 'Moderado', color: '#f59e0b' },
  { value: 'alto', label: 'Alto', color: '#f97316' },
  { value: 'extremo', label: 'Extremo', color: '#ef4444' },
];

// PRODUCTOS: filtrar por nombre_categoria (dinámico)
const categoriasProductos = computed(() => {
  const cats = [...new Set(productos.value.map(p => p.nombre_categoria).filter(Boolean))];
  return [{ value: '', label: 'Todos' }, ...cats.map(c => ({ value: c, label: c }))];
});

const categoriaActiva = ref('');

// --- FILTRADO Y ORDENAMIENTO ---
const nivelRiesgoMax = { bajo: [0,3], moderado: [4,6], alto: [7,8], extremo: [9,10] };

const toursFiltrados = computed(() => {
  let lista = [...tours.value];
  if (busqueda.value.trim()) {
    const q = busqueda.value.trim().toLowerCase();
    lista = lista.filter(t => t.nombre.toLowerCase().includes(q) || (t.nombre_agencia && t.nombre_agencia.toLowerCase().includes(q)));
  }
  if (categoriaActiva.value) {
    const [min, max] = nivelRiesgoMax[categoriaActiva.value] || [0,10];
    lista = lista.filter(t => t.nivel_riesgo >= min && t.nivel_riesgo <= max);
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
    lista = lista.filter(p => p.nombre.toLowerCase().includes(q) || (p.nombre_proveedor && p.nombre_proveedor.toLowerCase().includes(q)));
  }
  if (orden.value === 'precio_asc') lista.sort((a,b) => a.precio - b.precio);
  else if (orden.value === 'precio_desc') lista.sort((a,b) => b.precio - a.precio);
  else if (orden.value === 'rating_desc') lista.sort((a,b) => b.rating - a.rating);
  return lista;
});

const itemsActuales = computed(() => tabActivo.value === 'tours' ? toursFiltrados.value : productosFiltrados.value);
const cargando = computed(() => tabActivo.value === 'tours' ? cargandoTours.value : cargandoProductos.value);
const categoriasActuales = computed(() => tabActivo.value === 'tours' ? categoriasTours : categoriasProductos.value);

watch(tabActivo, () => {
  busqueda.value = '';
  orden.value = '';
  categoriaActiva.value = '';
});
</script>

<template>
  <div class="min-h-screen bg-gray-50 px-6 py-10 max-w-7xl mx-auto" @click="mostrarMenuOrden = false">

    <!-- Título principal -->
    <div class="mb-8">
      <p class="text-sm font-semibold text-emerald-600 mb-1 uppercase tracking-widest">Explora</p>
      <h1 class="text-3xl font-black text-gray-900 tracking-tight">Catálogo Amazonia Viva</h1>
    </div>

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

    <!-- Fila de etiquetas de categoría (chips) -->
    <div class="flex flex-wrap gap-2 mb-8">
      <button
        v-for="cat in categoriasActuales" :key="cat.value"
        @click="categoriaActiva = cat.value"
        :class="['flex items-center gap-1.5 px-4 py-1.5 rounded-full text-sm font-medium border transition-all duration-200',
          categoriaActiva === cat.value
            ? (tabActivo === 'tours' ? 'bg-emerald-600 text-white border-emerald-600' : 'bg-teal-600 text-white border-teal-600')
            : 'bg-white text-gray-500 border-gray-200 hover:border-gray-300 hover:text-gray-700']"
      >
        <!-- Dot de color para niveles de riesgo (tours) -->
        <span
          v-if="cat.color"
          class="inline-block w-2 h-2 rounded-full flex-shrink-0"
          :style="{ backgroundColor: categoriaActiva === cat.value ? 'white' : cat.color }"
        ></span>
        {{ cat.label }}
      </button>
    </div>

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
