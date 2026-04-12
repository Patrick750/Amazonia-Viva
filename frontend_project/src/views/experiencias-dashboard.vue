<script setup>
import { ref, onMounted } from 'vue';
import axios from '@/api/axios';

const metrics = ref({ total: 0, completadas: 0, pendientes: 0 });
const registro = ref([]);
const isLoading = ref(true);
const isUploading = ref(false);
const selectedDetalle = ref(null);
const fileInput = ref(null);

const fetchData = async () => {
    isLoading.value = true;
    try {
        const { data } = await axios.get('api/experiencias/dashboard/');
        metrics.value = data.metrics;
        registro.value = data.registro;
    } catch (error) {
        console.error('Error fetching dashboard data:', error);
    } finally {
        isLoading.value = false;
    }
};

const openUpload = (detalle) => {
    selectedDetalle.value = detalle;
    fileInput.value.click();
};

const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file || !selectedDetalle.value) return;

    const formData = new FormData();
    formData.append('imagen', file);

    isUploading.value = true;
    try {
        await axios.post(`api/experiencias/${selectedDetalle.value.id}/evidencia/`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
        // Refrescar datos para ver el contador de evidencias actualizado
        await fetchData();
    } catch (error) {
        console.error('Error uploading evidence:', error);
    } finally {
        isUploading.value = false;
        selectedDetalle.value = null;
    }
};

const markAsRealizada = async (detalle) => {
    try {
        await axios.post(`api/experiencias/${detalle.id}/realizada/`);
        await fetchData();
    } catch (error) {
        console.error('Error marking as realizada:', error);
    }
};

onMounted(() => {
    fetchData();
});
</script>

<template>
  <div class="min-h-screen bg-[#0a1410] text-white font-sans selection:bg-emerald-500/30">
    <div class="max-w-7xl mx-auto px-6 py-12">
      
      <!-- Volver -->
      <router-link to="/panel/dashboard" class="inline-flex items-center gap-2 text-emerald-400 font-black uppercase text-[10px] tracking-widest mb-8 hover:text-white transition-colors group/back">
        <svg class="w-4 h-4 transition-transform group-hover/back:-translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
        Panel Principal
      </router-link>

      <!-- Encabezado -->
      <header class="mb-12">
        <h1 class="text-5xl font-black tracking-tighter mb-2">Experiencias</h1>
        <p class="text-gray-400 text-lg">Gestiona las experiencias prestadas a tus clientes</p>
      </header>

      <!-- Tarjetas de Resumen -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <div class="bg-[#12221b] border border-[#1e362a] p-8 rounded-2xl shadow-2xl transition-all hover:border-emerald-500/30 group">
          <p class="text-gray-400 font-bold uppercase text-xs tracking-widest mb-2 group-hover:text-emerald-400 transition-colors">Total Experiencias</p>
          <p class="text-4xl font-black">{{ metrics.total }}</p>
        </div>
        <div class="bg-[#12221b] border border-[#1e362a] p-8 rounded-2xl shadow-2xl transition-all hover:border-emerald-500/30 group">
          <p class="text-gray-400 font-bold uppercase text-xs tracking-widest mb-2 group-hover:text-emerald-400 transition-colors">Completadas</p>
          <p class="text-4xl font-black text-emerald-400">{{ metrics.completadas }}</p>
        </div>
        <div class="bg-[#12221b] border border-[#1e362a] p-8 rounded-2xl shadow-2xl transition-all hover:border-emerald-500/30 group">
          <p class="text-gray-400 font-bold uppercase text-xs tracking-widest mb-2 group-hover:text-rose-400 transition-colors">Pendientes</p>
          <p class="text-4xl font-black">{{ metrics.pendientes }}</p>
        </div>
      </div>

      <!-- Sección Principal: Tabla -->
      <div class="bg-[#12221b] border border-[#1e362a] rounded-2xl overflow-hidden shadow-2xl">
        <div class="p-8 border-b border-[#1e362a] flex justify-between items-center">
          <div>
            <h2 class="text-2xl font-bold mb-1">Registro de Clientes</h2>
            <p class="text-sm text-gray-400">Listado de clientes atendidos y estado de sus servicios</p>
          </div>
          <div v-if="isUploading" class="flex items-center gap-3 bg-emerald-500/10 text-emerald-400 px-4 py-2 rounded-full border border-emerald-500/20 animate-pulse">
            <svg class="animate-spin h-4 w-4" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/></svg>
            <span class="text-xs font-black uppercase tracking-widest">Subiendo Evidencia...</span>
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-black/20">
              <tr>
                <th class="px-8 py-4 text-left text-[10px] font-black uppercase tracking-[0.2em] text-gray-500">Cliente</th>
                <th class="px-8 py-4 text-left text-[10px] font-black uppercase tracking-[0.2em] text-gray-500">Tour</th>
                <th class="px-8 py-4 text-left text-[10px] font-black uppercase tracking-[0.2em] text-gray-500">Fecha</th>
                <th class="px-8 py-4 text-left text-[10px] font-black uppercase tracking-[0.2em] text-gray-500">Pax</th>
                <th class="px-8 py-4 text-left text-[10px] font-black uppercase tracking-[0.2em] text-gray-500">Estado</th>
                <th class="px-8 py-4 text-left text-[10px] font-black uppercase tracking-[0.2em] text-gray-500">Evidencias</th>
                <th class="px-8 py-4 text-right text-[10px] font-black uppercase tracking-[0.2em] text-gray-500">Acciones</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[#1e362a]">
              <tr v-for="item in registro" :key="item.id" class="hover:bg-white/5 transition-colors group">
                <td class="px-8 py-6 font-bold truncate max-w-[200px]">{{ item.cliente }}</td>
                <td class="px-8 py-6 text-gray-300">{{ item.tour }}</td>
                <td class="px-8 py-6 text-sm flex items-center gap-2 text-gray-400">
                  <svg class="w-4 h-4 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                  {{ item.fecha }}
                </td>
                <td class="px-8 py-6 text-sm text-gray-400">
                  <div class="flex items-center gap-2">
                    <svg class="w-4 h-4 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
                    {{ item.personas }}
                  </div>
                </td>
                <td class="px-8 py-6">
                  <span v-if="item.estado === 'Realizado'" class="px-3 py-1 bg-emerald-500/10 text-emerald-400 text-[10px] font-black uppercase tracking-widest rounded-full border border-emerald-500/20">
                    Realizado
                  </span>
                  <span v-else class="px-3 py-1 bg-blue-500/10 text-blue-400 text-[10px] font-black uppercase tracking-widest rounded-full border border-blue-500/20">
                    Confirmado
                  </span>
                </td>
                <td class="px-8 py-6">
                  <div v-if="item.evidencias > 0" class="flex items-center gap-2 text-emerald-400">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                    <span class="text-xs font-black">{{ item.evidencias }} fotos</span>
                  </div>
                  <span v-else class="text-xs text-gray-600 font-bold uppercase tracking-widest">Sin fotos</span>
                </td>
                <td class="px-8 py-6 text-right">
                  <div class="flex justify-end gap-3 translate-x-2 group-hover:translate-x-0 transition-transform opacity-0 group-hover:opacity-100 duration-300">
                    <button @click="openUpload(item)" class="flex items-center gap-2 px-4 py-2 border border-[#1e362a] hover:bg-white/5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/></svg>
                      Subir fotos
                    </button>
                    <button v-if="item.estado !== 'Realizado'" @click="markAsRealizada(item)" class="flex items-center gap-2 px-4 py-2 bg-[#00d18b] text-black hover:bg-[#00f5d4] rounded-xl text-[10px] font-black uppercase tracking-widest transition-all shadow-[0_4px_15px_rgba(0,209,139,0.3)]">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg>
                      Finalizar
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>

    <!-- Buscador Oculto de Archivos -->
    <input 
      type="file" 
      ref="fileInput" 
      class="hidden" 
      accept="image/*"
      @change="handleFileUpload"
    />
  </div>
</template>

<style scoped>
.tracking-widest {
  letter-spacing: 0.25em;
}
</style>
