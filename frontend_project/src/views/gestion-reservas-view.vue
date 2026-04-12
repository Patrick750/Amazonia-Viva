<script setup>
import { ref, onMounted } from 'vue';
import axios from '@/api/axios';
import GestionReservas from '@/components/perfil/GestionReservas.vue';

const perfil = ref({});
const isLoading = ref(true);

const fetchPerfil = async () => {
    try {
        const { data } = await axios.get('api/perfil/');
        perfil.value = data;
    } catch (error) {
        console.error('Error cargando perfil:', error);
    } finally {
        isLoading.value = false;
    }
};

onMounted(() => {
    fetchPerfil();
});
</script>

<template>
  <div class="min-h-screen bg-[#050a09] flex flex-col">
    <!-- El componente GestionReservas ahora maneja su propia navegación y header -->
    <main class="flex-1 flex flex-col overflow-hidden">
      <GestionReservas v-if="!isLoading" :perfil="perfil" />
      <div v-else class="flex-1 flex justify-center items-center">
          <div class="flex flex-col items-center gap-4">
            <svg class="w-12 h-12 text-[#00f5d4] animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
            </svg>
            <span class="text-[10px] font-black text-[#00f5d4] uppercase tracking-[0.3em] animate-pulse">Sincronizando Terminal...</span>
          </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* Optimizamos para que no haya scroll en el contenedor principal si no es necesario */
:deep(.h-full) {
  height: 100vh;
}
</style>
