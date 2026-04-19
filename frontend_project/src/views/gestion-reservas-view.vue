<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from '@/api/axios';
import GestionReservas from '@/components/perfil/GestionReservas.vue';
import VentasProveedor from '@/components/perfil/VentasProveedor.vue';

const perfil     = ref({});
const isLoading  = ref(true);
const userRole   = ref(localStorage.getItem('rol') || 'agencia');
const isProveedor = computed(() => userRole.value === 'proveedor');

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

onMounted(fetchPerfil);
</script>

<template>
  <!-- Loading -->
  <div v-if="isLoading" class="loading-shell">
    <div class="loading-inner">
      <svg class="spin-icon" viewBox="0 0 24 24" fill="none">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
      </svg>
      <span class="loading-label">Sincronizando...</span>
    </div>
  </div>

  <!-- Proveedor → nuevo diseño "Ver Ventas" -->
  <VentasProveedor
    v-else-if="isProveedor"
    :perfil="perfil"
  />

  <!-- Agencia → diseño existente -->
  <div v-else class="min-h-screen bg-[#050a09] flex flex-col">
    <main class="flex-1 flex flex-col overflow-hidden">
      <GestionReservas :perfil="perfil" />
    </main>
  </div>
</template>

<style scoped>
.loading-shell {
  min-height: 100vh;
  background: #080e0d;
  display: flex;
  align-items: center;
  justify-content: center;
}
.loading-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
}
.spin-icon {
  width: 40px;
  height: 40px;
  color: #00d68f;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.loading-label {
  font-size: 10px;
  font-weight: 700;
  color: #00d68f;
  text-transform: uppercase;
  letter-spacing: 0.25em;
  animation: pulse 1.5s ease-in-out infinite;
}
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
</style>
