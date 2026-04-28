<script setup>
    import { ref, onMounted } from 'vue';
    import Tours from '@/components/gestion-catalogo/tours.vue';
    import Formulario from '@/components/gestion-catalogo/formulario.vue';
    import ConfirmarEliminar from '@/components/gestion-catalogo/delete.vue';
    import DetallesTour from '@/components/gestion-catalogo/detalles-tour.vue';
    import CargaMasiva from '@/components/gestion-catalogo/carga-masiva.vue';
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

    // --- ESTADO DEL MODAL CARGA MASIVA ---
    const isModalCargaMasivaOpen = ref(false);

    const abrirModalCargaMasiva = () => {
        isModalCargaMasivaOpen.value = true;
    };

    const cerrarModalCargaMasiva = () => {
        isModalCargaMasivaOpen.value = false;
    };

    const onCargaMasivaExitosa = async () => {
        paquetesTraidos.value = await paquetes();
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
  <div class="min-h-screen bg-[#0a1a0f] text-white p-6 md:p-10 relative z-0">
    
    <main class="max-w-6xl mx-auto">
      <header class="flex flex-col md:flex-row md:items-center justify-between mb-10 gap-6">
        <div>
          <router-link to="/panel/dashboard" class="group inline-flex items-center gap-2.5 text-[11px] font-black uppercase tracking-[0.2em] text-emerald-500/60 hover:text-emerald-400 mb-4 transition-all">
            <div class="w-8 h-8 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center group-hover:-translate-x-1 transition-transform">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
            </div>
            Volver al Dashboard
          </router-link>
          <h1 class="text-4xl sm:text-5xl font-black text-white tracking-tighter drop-shadow-2xl">Gestión de <span class="text-emerald-500">Tours</span></h1>
          <p class="text-white/40 mt-2 font-bold italic text-sm">Administra tu oferta de experiencias turísticas premium</p>
        </div>
        <div class="flex items-center gap-3">
          <button @click="abrirModalCargaMasiva" 
                  class="flex items-center gap-2 bg-emerald-500/10 border border-emerald-500/30 hover:bg-emerald-500/20 text-emerald-400 font-black py-4 px-6 rounded-2xl transition-all shadow-lg hover:-translate-y-0.5 active:scale-95 w-fit uppercase tracking-widest text-[11px]">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"/></svg>
            Carga Masiva
          </button>
          <button @click="abrirModalNuevo" 
                  class="group flex items-center gap-3 bg-emerald-600 hover:bg-emerald-500 text-black font-black uppercase tracking-widest text-[11px] py-4 px-8 rounded-2xl transition-all shadow-xl shadow-emerald-900/20 hover:-translate-y-1 active:translate-y-0 w-fit">
            <div class="w-6 h-6 rounded-lg bg-black/10 flex items-center justify-center group-hover:rotate-90 transition-transform">
              <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
            </div>
            Nuevo Tour
          </button>
        </div>
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

    <CargaMasiva 
      :abrir="isModalCargaMasivaOpen"
      @cerrar="cerrarModalCargaMasiva"
      @cargaExitosa="onCargaMasivaExitosa"
    />

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