<script setup>
    import { ref, onMounted } from 'vue';
    import Tours from '@/components/gestion-catalogo/tours.vue';
    import Formulario from '@/components/gestion-catalogo/formulario.vue';
    import ConfirmarEliminar from '@/components/gestion-catalogo/delete.vue';
    import DetallesTour from '@/components/gestion-catalogo/detalles-tour.vue';
    import Notificacion from '@/components/notificacion.vue';
    import { pedirActividades } from '@/composables/gestion-tours/actividades';
    import { paquetes } from '@/composables/gestion-tours/paquetes';

    // --- ESTADO DEL MODAL ---
    const isModalOpen = ref(false);
    const paqueteSeleccionado = ref(null);

    const abrirModalNuevo = () => {
        paqueteSeleccionado.value = null;
        isModalOpen.value = true;
    };

    const editarTour = (tour) => {
        paqueteSeleccionado.value = tour;
        isModalOpen.value = true;
    };

    const cerrarModal = () => {
        isModalOpen.value = false;
        paqueteSeleccionado.value = null;
    };

    // --- ESTADO DEL MODAL ELIMINAR ---
    const isDeleteModalOpen = ref(false);
    const paqueteAEliminar = ref(null);

    const abrirModalEliminar = (id) => {
        const tour = paquetesTraidos.value.find(p => p.id === id);
        if (tour) {
            paqueteAEliminar.value = tour;
            isDeleteModalOpen.value = true;
        }
    };

    const cerrarModalEliminar = () => {
        isDeleteModalOpen.value = false;
        paqueteAEliminar.value = null;
    };

    const onEliminadoExitoso = (id) => {
        paquetesTraidos.value = paquetesTraidos.value.filter(p => p.id !== id);
        cerrarModalEliminar();
    };

    // --- ESTADO DEL MODAL DETALLES ---
    const isDetallesModalOpen = ref(false);
    const paqueteADetallar = ref(null);

    const abrirModalDetalles = (tour) => {
        paqueteADetallar.value = tour;
        isDetallesModalOpen.value = true;
    };

    const cerrarModalDetalles = () => {
        isDetallesModalOpen.value = false;
        paqueteADetallar.value = null;
    };

    const onGuardadoExitoso = (paqueteActualizado) => {
        if (paqueteSeleccionado.value) {
            // EDICIÓN: reemplazar el elemento en el array local
            const index = paquetesTraidos.value.findIndex(p => p.id === paqueteActualizado.id);
            if (index !== -1) {
                paquetesTraidos.value[index] = paqueteActualizado;
            }
        } else {
            // CREACIÓN: agregar al inicio del array
            paquetesTraidos.value.unshift(paqueteActualizado);
        }
        cerrarModal();
    };

    // --- DATOS ---
    const listado = ref([]);
    onMounted(async () => {
        listado.value = await pedirActividades();
    });

    const paquetesTraidos = ref([]);
    onMounted(async () => {
        paquetesTraidos.value = await paquetes();
    });

</script>

<template>
  <div class="min-h-screen bg-[#e8f4f1] text-slate-900 p-6 md:p-10 relative z-0">
    
    <main class="max-w-6xl mx-auto">
      <header class="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
        <div>
          <router-link to="/panel/dashboard" class="group inline-flex items-center gap-2 text-sm font-bold text-emerald-600 hover:text-emerald-800 mb-3 transition-colors">
            <svg class="w-4 h-4 transform group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
            Volver al Dashboard
          </router-link>
          <h1 class="text-3xl font-bold text-emerald-900 tracking-tight">Gestión de Tours</h1>
          <p class="text-slate-600 mt-1">Administra tu oferta de experiencias turísticas</p>
        </div>
        <button @click="abrirModalNuevo" 
                class="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold py-2.5 px-5 rounded-xl transition-all shadow-sm hover:shadow-md hover:-translate-y-0.5 w-fit">
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
          Nuevo Tour
        </button>
      </header>
      <Tours
        :datos="paquetesTraidos"
        @editar="editarTour"
        @eliminar="abrirModalEliminar"
        @verDetalles="abrirModalDetalles"
      ></Tours>
    </main>
    <Formulario
      :abrir="isModalOpen"
      @cerrar="cerrarModal"
      :actividades="listado"
      :paquete="paqueteSeleccionado"
      @guardadoExitoso="onGuardadoExitoso"
    ></Formulario>

    <ConfirmarEliminar
      :abrir="isDeleteModalOpen"
      :paquete="paqueteAEliminar"
      @cerrar="cerrarModalEliminar"
      @eliminadoExitoso="onEliminadoExitoso"
    ></ConfirmarEliminar>

    <DetallesTour
      :abrir="isDetallesModalOpen"
      :paquete="paqueteADetallar"
      :actividades="listado"
      @cerrar="cerrarModalDetalles"
    ></DetallesTour>

    <Notificacion />
  </div>
</template>

<style scoped>
/* Animación simple para la entrada del modal (opcional, pero mejora la UX) */
.animate-fade-in-up {
  animation: fadeInUp 0.3s ease-out forwards;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Personalización sutil del scrollbar para el modal */
.form-scroll::-webkit-scrollbar {
  width: 6px;
}
.form-scroll::-webkit-scrollbar-track {
  background: transparent;
}
.form-scroll::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 20px;
}
</style>