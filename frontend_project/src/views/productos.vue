<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import axios from '@/api/axios';
import TablaProductos from '@/components/gestion-productos/tabla-productos.vue';
import FormularioProducto from '@/components/gestion-productos/formulario.vue';
import DetallesProducto from '@/components/gestion-productos/detalles-producto.vue';
import EliminarProducto from '@/components/gestion-productos/eliminar-producto.vue';

const API_URL = 'api/productos/';

const vistaActiva = ref('turistas'); // 'turistas' o 'agencias'

const categoriasLista = [
    { id: 1, nombre: 'Equipos de Supervivencia' },
    { id: 2, nombre: 'Seguridad y Primeros Auxilios' },
    { id: 3, nombre: 'Indumentaria Outdoor' },
    { id: 4, nombre: 'Accesorios de Viaje' },
    { id: 5, nombre: 'Tecnología y Navegación' },
    { id: 6, nombre: 'Campamento y pernocta' },
    { id: 7, nombre: 'Actividades acuáticas' },
    { id: 8, nombre: 'Senderismo y exploración' },
    { id: 9, nombre: 'Observación de flora y fauna' },
    { id: 10, nombre: 'Seguridad y primeros aux' },
    { id: 11, nombre: 'Indumentaria y calzado' },
    { id: 12, nombre: 'Alimentación e hidratación' },
    { id: 13, nombre: 'Fotografía y óptica' },
    { id: 14, nombre: 'Comunicaciones y orientación' },
    { id: 15, nombre: 'Transporte y logística' },
    { id: 16, nombre: 'Supervivencia y herramientas' }
];

const listadoProductos = ref([]);
const searchQuery = ref('');

const listadoFiltrado = computed(() => {
    let filtrado = listadoProductos.value;
    if (searchQuery.value.trim()) {
        const q = searchQuery.value.toLowerCase();
        filtrado = filtrado.filter(p => 
            p.nombre.toLowerCase().includes(q) || 
            p.sku.toLowerCase().includes(q)
        );
    }
    return filtrado;
});

const productosAlertaStock = computed(() => {
    return listadoProductos.value.filter(p => p.stock >= 0 && p.stock <= 5).sort((a,b) => a.stock - b.stock);
});

const fetchProductos = async () => {
    try {
        const response = await axios.get(`${API_URL}?tipo_catalogo=${vistaActiva.value}`);
        listadoProductos.value = response.data;
    } catch (error) {
        console.error('Error cargando productos:', error);
    }
};

onMounted(() => {
    fetchProductos();
});

watch(vistaActiva, () => {
    fetchProductos();
});

// --- ESTADO DEL MODAL FORMULARIO ---
const isModalOpen = ref(false);
const productoSeleccionado = ref(null);

// --- ESTADO DEL MODAL DETALLES ---
const isModalDetalleOpen = ref(false);
const productoParaDetalle = ref(null);

const abrirModalNuevo = () => {
    productoSeleccionado.value = null;
    isModalOpen.value = true;
};

const editarProducto = (prod) => {
    productoSeleccionado.value = prod;
    isModalOpen.value = true;
};

const cerrarModal = () => {
    isModalOpen.value = false;
    productoSeleccionado.value = null;
};

const verDetallesProducto = (prod) => {
    productoParaDetalle.value = prod;
    isModalDetalleOpen.value = true;
};

const cerrarModalDetalles = () => {
    isModalDetalleOpen.value = false;
    setTimeout(() => { productoParaDetalle.value = null; }, 300); // Wait logic
};

const onGuardadoExitoso = () => {
    cerrarModal();
    fetchProductos(); // Refresh list after complete
};

// --- ESTADO DEL MODAL ELIMINAR ---
const isModalEliminarOpen = ref(false);
const productoParaEliminar = ref(null);

const abrirModalEliminar = (id) => {
    const prod = listadoProductos.value.find(p => p.id === id);
    if (prod) {
        productoParaEliminar.value = prod;
        isModalEliminarOpen.value = true;
    }
};

const cerrarModalEliminar = () => {
    isModalEliminarOpen.value = false;
    setTimeout(() => { productoParaEliminar.value = null; }, 300);
};

const onEliminadoExitoso = (id) => {
    listadoProductos.value = listadoProductos.value.filter(p => p.id !== id);
    cerrarModalEliminar();
};

const eliminarProducto = (id) => {
    abrirModalEliminar(id);
};
</script>

<template>
  <div class="min-h-screen bg-[#0a1a0f] p-6 md:p-8 relative z-0 flex flex-col items-center selection:bg-emerald-500/30">
    <div class="max-w-[90rem] w-full">

      <!-- HEADER PRINCIPAL -->
      <header class="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4 animate-fade-in-down">
        <div>
          <router-link to="/panel/dashboard" class="group inline-flex items-center gap-2 text-[10px] font-bold text-emerald-400/80 hover:text-emerald-400 mb-3 transition-colors tracking-widest uppercase">
            <svg class="w-4 h-4 transform group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
            Volver al Dashboard
          </router-link>
          <h1 class="text-3xl font-black text-white tracking-tight">Gestión de Productos</h1>
          <p class="text-white/45 mt-1 font-medium italic">Administra la oferta de inventario en tus diferentes catálogos</p>
        </div>
        <button @click="abrirModalNuevo" 
                class="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-black font-black py-3 px-6 rounded-xl transition-all shadow-lg shadow-emerald-500/20 hover:-translate-y-0.5 active:scale-95 w-fit">
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
          Nuevo Producto
        </button>
      </header>
      
      <div class="grid grid-cols-1 lg:grid-cols-5 gap-6 animate-fade-in-up" style="animation-delay: 0.1s;">
        <!-- SIDEBAR IZQUIERDO: Catálogos -->
        <aside class="lg:col-span-1 bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-sm h-fit">
          <h2 class="text-[10px] font-black text-white/40 uppercase tracking-[0.2em] mb-4 border-b border-white/5 pb-3">Catálogos</h2>
          <nav class="flex flex-col gap-2">
            <button @click="vistaActiva = 'turistas'" 
                    class="text-left px-4 py-3.5 rounded-xl text-xs font-bold transition-all duration-200 flex items-center gap-3 border shadow-sm"
                    :class="vistaActiva === 'turistas' ? 'bg-emerald-500/15 border-emerald-500/40 text-emerald-400' : 'bg-white/5 border-white/5 text-white/50 hover:bg-white/10 hover:text-white'">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
              Para turistas
            </button>
            <button @click="vistaActiva = 'agencias'" 
                    class="text-left px-4 py-3.5 rounded-xl text-xs font-bold transition-all duration-200 flex items-center gap-3 border shadow-sm"
                    :class="vistaActiva === 'agencias' ? 'bg-emerald-500/15 border-emerald-500/40 text-emerald-400' : 'bg-white/5 border-white/5 text-white/50 hover:bg-white/10 hover:text-white'">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path></svg>
              Para agencias
            </button>
          </nav>
        </aside>

        <!-- CONTENIDO PRINCIPAL (Tabla + Buscador) -->
        <main class="lg:col-span-3 flex flex-col gap-5">
          
          <!-- BÚSQUEDA Y FILTRO -->
          <div class="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-4 shadow-sm flex flex-col sm:flex-row items-center gap-4">
            <div class="relative flex-1 w-full">
              <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-white/20" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
              <input v-model="searchQuery" type="text" placeholder="Buscar por nombre, SKU..." class="w-full bg-white/5 border border-white/10 rounded-xl pl-10 pr-4 py-3 text-sm text-white font-medium focus:outline-none focus:border-emerald-500/50 focus:bg-white/10 transition-all placeholder:text-white/20">
            </div>
            
            <div class="flex items-center gap-3 flex-shrink-0 bg-emerald-500/10 px-4 py-3 rounded-xl border border-emerald-500/20">
               <span class="text-[10px] font-black text-emerald-400 uppercase tracking-widest">Resultados:</span>
               <span class="text-white text-base font-black">{{ listadoFiltrado.length }}</span>
            </div>
          </div>

          <TablaProductos 
             :datos="listadoFiltrado" 
             :tipo-catalogo="vistaActiva"
             @editar="editarProducto"
             @eliminar="eliminarProducto"
             @verDetalles="verDetallesProducto"
          />
        </main>

        <!-- SIDEBAR DERECHO: Alertas de Stock -->
        <aside class="lg:col-span-1 bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-5 shadow-sm h-fit">
          <h2 class="text-[10px] font-black text-rose-400 uppercase tracking-[0.2em] mb-4 border-b border-rose-500/20 pb-3 flex items-center gap-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
            Alertas Críticas
          </h2>
          <div v-if="productosAlertaStock.length === 0" class="text-[11px] text-white/30 text-center py-8 bg-white/3 rounded-xl font-bold border border-dashed border-white/5 italic">
            🌱 Inventario saludable
          </div>
          <ul v-else class="space-y-3 max-h-[60vh] overflow-y-auto pr-1 custom-scroll">
            <li v-for="prod in productosAlertaStock" :key="prod.id" class="p-4 bg-rose-500/10 hover:bg-rose-500/20 rounded-xl border border-rose-500/20 flex justify-between items-start gap-4 transition-all cursor-pointer group/item" @click="verDetallesProducto(prod)">
              <div class="overflow-hidden">
                <p class="text-xs font-black text-rose-100 leading-tight truncate group-hover/item:text-white transition-colors">{{ prod.nombre }}</p>
                <p class="text-[9px] text-rose-300 font-black tracking-widest mt-1.5 bg-rose-900/40 inline-block px-1.5 py-0.5 rounded border border-rose-500/20 uppercase">{{ prod.sku }}</p>
              </div>
              <span class="w-8 h-8 bg-rose-500 text-black rounded-lg text-xs font-black shadow-lg shadow-rose-900/40 flex-shrink-0 flex items-center justify-center">
                {{ prod.stock }}
              </span>
            </li>
          </ul>
        </aside>
      </div>

      <!-- MODAL DEL FORMULARIO -->
      <FormularioProducto 
        :abrir="isModalOpen"
        :producto="productoSeleccionado"
        :tipo-catalogo="vistaActiva"
        @cerrar="cerrarModal"
        @guardadoExitoso="onGuardadoExitoso"
      />

      <!-- MODAL DE DETALLES -->
      <DetallesProducto 
        :abrir="isModalDetalleOpen"
        :producto="productoParaDetalle"
        :categorias-lista="categoriasLista"
        @cerrar="cerrarModalDetalles"
      />

      <!-- MODAL DE ELIMINAR -->
      <EliminarProducto 
        :abrir="isModalEliminarOpen"
        :producto="productoParaEliminar"
        @cerrar="cerrarModalEliminar"
        @eliminadoExitoso="onEliminadoExitoso"
      />

    </div>
  </div>
</template>

<style scoped>
.animate-fade-in-down {
  animation: fadeInDown 0.6s ease-out forwards;
}
.animate-fade-in-up {
  opacity: 0;
  transform: translateY(20px);
  animation: fadeInUp 0.5s ease-out forwards;
}

@keyframes fadeInDown {
  from { opacity: 0; transform: translateY(-15px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(15px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
