<script setup>
import { ref, onMounted, watch } from 'vue';
import axios from 'axios';
import TablaProductos from '@/components/gestion-productos/tabla-productos.vue';
import FormularioProducto from '@/components/gestion-productos/formulario.vue';
import DetallesProducto from '@/components/gestion-productos/detalles-producto.vue';

const API_URL = 'http://localhost:8000/api/productos/';

const vistaActiva = ref('turistas'); // 'turistas' o 'agencias'

const categoriasLista = [
    { id: 1, nombre: 'Artesanías' },
    { id: 2, nombre: 'Arte y Decoración' },
    { id: 3, nombre: 'Salud y Bienestar' },
    { id: 4, nombre: 'Souvenirs y Recuerdos' },
    { id: 5, nombre: 'Ropa y Textiles' }
];

const listadoProductos = ref([]);

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

const eliminarProducto = (id) => {
    if(confirm("¿Estás seguro de que quieres eliminar este producto?")) {
        listadoProductos.value = listadoProductos.value.filter(p => p.id !== id);
    }
};
</script>

<template>
  <div class="min-h-screen bg-[#e8f4f1] p-6 md:p-10 relative z-0 flex flex-col items-center">
    <div class="max-w-7xl w-full">

      <!-- HEADER PRINCIPAL -->
      <header class="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4 animate-fade-in-down">
        <div>
          <h1 class="text-3xl font-bold text-emerald-900 tracking-tight">Gestión de Productos</h1>
          <p class="text-slate-600 mt-1">Administra la oferta de inventario en tus diferentes catálogos</p>
        </div>
        <button @click="abrirModalNuevo" 
                class="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold py-2.5 px-5 rounded-xl transition-all shadow-sm hover:shadow-md hover:-translate-y-0.5 w-fit">
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
          Nuevo Producto
        </button>
      </header>
      
      <div class="grid grid-cols-1 lg:grid-cols-4 gap-6 animate-fade-in-up" style="animation-delay: 0.1s;">
        <!-- SIDEBAR -->
        <aside class="lg:col-span-1 bg-white/65 backdrop-blur-xl border border-white/80 rounded-2xl p-6 shadow-sm h-fit">
          <h2 class="text-sm font-semibold text-emerald-900 uppercase tracking-wider mb-4 border-b border-white/80 pb-3">Catálogos</h2>
          <nav class="flex flex-col gap-2">
            <button @click="vistaActiva = 'turistas'" 
                    class="text-left px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 flex items-center gap-3"
                    :class="vistaActiva === 'turistas' ? 'bg-emerald-600 text-white shadow-md' : 'text-slate-600 hover:bg-white/50 hover:text-emerald-700'">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
              Para turistas
            </button>
            <button @click="vistaActiva = 'agencias'" 
                    class="text-left px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 flex items-center gap-3"
                    :class="vistaActiva === 'agencias' ? 'bg-emerald-600 text-white shadow-md' : 'text-slate-600 hover:bg-white/50 hover:text-emerald-700'">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path></svg>
              Para agencias
            </button>
          </nav>
        </aside>

        <!-- CONTENIDO PRINCIPAL (Tabla) -->
        <main class="lg:col-span-3">
          <TablaProductos 
             :datos="listadoProductos" 
             :tipo-catalogo="vistaActiva"
             @editar="editarProducto"
             @eliminar="eliminarProducto"
             @verDetalles="verDetallesProducto"
          />
        </main>
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
