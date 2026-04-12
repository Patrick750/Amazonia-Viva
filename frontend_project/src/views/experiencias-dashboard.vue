<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from '@/api/axios';

const metrics = ref({ total: 0, completadas: 0, pendientes: 0 });
const registro = ref([]);
const isLoading = ref(true);
const isUploading = ref(false);
const selectedDetalle = ref(null);
const fileInput = ref(null);
const uploadProgress = ref(0);

const mostrarModalTuristas = ref(false);
const selectedTour = ref(null);
const searchQuery = ref('');
const dateFilter = ref('');

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

const filteredRegistro = computed(() => {
    return registro.value.filter(g => {
        const query = searchQuery.value.toLowerCase();
        const matchesPackage = g.tour.toLowerCase().includes(query);
        const matchesTourist = g.turistas.some(t => t.nombre.toLowerCase().includes(query));
        
        const matchesSearch = matchesPackage || matchesTourist;
        const matchesDate = !dateFilter.value || g.fecha === dateFilter.value;
        return matchesSearch && matchesDate;
    });
});

const verTuristas = (tour) => {
    selectedTour.value = tour;
    mostrarModalTuristas.value = true;
};

const openUpload = (tour) => {
    // Usamos el ID del líder del grupo para asociar las fotos
    selectedDetalle.value = { id: tour.leader_id };
    fileInput.value.click();
};

const handleFileUpload = async (event) => {
    const files = event.target.files;
    if (!files || files.length === 0 || !selectedDetalle.value) return;

    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append('imagenes', files[i]);
    }

    isUploading.value = true;
    uploadProgress.value = 0;
    try {
        await axios.post(`api/experiencias/${selectedDetalle.value.id}/evidencia/`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
            onUploadProgress: (progressEvent) => {
                const total = progressEvent.total;
                if (total) {
                    uploadProgress.value = Math.round((progressEvent.loaded * 100) / total);
                }
            }
        });
        await fetchData();
        // Si el modal está abierto, actualizar el selectedTour para reflejar las nuevas fotos
        if (mostrarModalTuristas.value && selectedTour.value) {
            const updated = registro.value.find(g => g.id === selectedTour.value.id);
            if (updated) selectedTour.value = updated;
        }
    } catch (error) {
        console.error('Error uploading evidence:', error);
    } finally {
        isUploading.value = false;
        uploadProgress.value = 0;
        selectedDetalle.value = null;
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
        <p class="text-gray-400 text-lg">Gestiona las evidencias y feedback de tus servicios prestados</p>
      </header>

      <!-- Tarjetas de Resumen -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <div class="bg-[#12221b] border border-[#1e362a] p-8 rounded-2xl shadow-2xl transition-all hover:border-emerald-500/30 group">
          <p class="text-gray-400 font-bold uppercase text-xs tracking-widest mb-2 group-hover:text-emerald-400 transition-colors">Tours Realizados</p>
          <p class="text-4xl font-black">{{ metrics.total }}</p>
        </div>
        <div class="bg-[#12221b] border border-[#1e362a] p-8 rounded-2xl shadow-2xl transition-all hover:border-emerald-500/30 group">
          <p class="text-gray-400 font-bold uppercase text-xs tracking-widest mb-2 group-hover:text-emerald-400 transition-colors">Completados</p>
          <p class="text-4xl font-black text-emerald-400">{{ metrics.completadas }}</p>
        </div>
        <div class="bg-[#12221b] border border-[#1e362a] p-8 rounded-2xl shadow-2xl transition-all hover:border-emerald-500/30 group">
          <p class="text-gray-400 font-bold uppercase text-xs tracking-widest mb-2 group-hover:text-rose-400 transition-colors">Pendientes</p>
          <p class="text-4xl font-black">{{ metrics.pendientes }}</p>
        </div>
      </div>

      <!-- Sección Principal: Tabla e Interfaz Responsiva -->
      <div class="bg-[#12221b] border border-[#1e362a] rounded-3xl overflow-hidden shadow-2xl">
        
        <!-- Barra de Herramientas: Título + Filtros -->
        <div class="p-8 border-b border-[#1e362a] space-y-6">
          <div class="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6">
            <div>
              <h2 class="text-2xl font-bold mb-1">Registro de Tours</h2>
              <p class="text-sm text-gray-400">Listado de salidas programadas y gestión masiva</p>
            </div>
            
            <div v-if="isUploading" class="flex flex-col items-end gap-1 w-full lg:w-auto">
              <div class="flex items-center gap-3 bg-emerald-500/10 text-emerald-400 px-4 py-2 rounded-full border border-emerald-500/20 w-full lg:w-auto justify-center lg:justify-start">
                <svg class="animate-spin h-3 w-3" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/></svg>
                <span class="text-[10px] font-black uppercase tracking-widest">Subiendo {{ uploadProgress }}%</span>
              </div>
              <div class="w-full lg:w-48 h-1 bg-white/5 rounded-full overflow-hidden border border-white/5">
                <div class="h-full bg-emerald-500 transition-all duration-300 shadow-[0_0_10px_rgba(16,185,129,0.5)]" :style="{ width: uploadProgress + '%' }"></div>
              </div>
            </div>
          </div>

          <!-- Filtros -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <!-- Buscador -->
            <div class="relative group">
              <input 
                v-model="searchQuery"
                type="text" 
                placeholder="Buscar por paquete o turista..." 
                class="w-full bg-black/40 border border-[#1e362a] rounded-xl px-5 py-3 text-sm focus:outline-none focus:border-emerald-500/50 transition-all placeholder:text-gray-600 pl-12"
              >
              <svg class="w-5 h-5 absolute left-4 top-1/2 -translate-y-1/2 text-gray-600 group-focus-within:text-emerald-500 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
            </div>
            
            <!-- Filtro de Fecha -->
            <div class="relative group">
              <input 
                v-model="dateFilter"
                type="date" 
                class="w-full bg-black/40 border border-[#1e362a] rounded-xl px-5 py-3 text-sm focus:outline-none focus:border-emerald-500/50 transition-all text-gray-300 appearance-none pl-12"
              >
              <svg class="w-5 h-5 absolute left-4 top-1/2 -translate-y-1/2 text-gray-600 group-focus-within:text-emerald-500 transition-colors pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
            </div>

            <!-- Botón Limpiar -->
            <button v-if="searchQuery || dateFilter" @click="searchQuery = ''; dateFilter = ''" class="flex items-center justify-center gap-2 text-[10px] font-black uppercase tracking-widest text-rose-500 hover:text-rose-400 transition-colors p-3 lg:justify-start">
              Limpiar Filtros
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
            </button>
          </div>
        </div>

        <!-- LISTADO PARA MÓVIL (Cards) -->
        <div class="block md:hidden p-6 space-y-4">
          <div v-if="filteredRegistro.length === 0" class="py-20 text-center">
            <p class="text-gray-500 font-bold italic">No se encontraron tours con los filtros aplicados</p>
          </div>
          <div v-for="g in filteredRegistro" :key="g.id" class="bg-black/20 border border-white/5 p-6 rounded-2xl relative group">
            <div class="flex justify-between items-start mb-4">
              <h3 class="font-bold text-lg leading-tight">{{ g.tour }}</h3>
              <span v-if="g.estado === 'Realizado'" class="px-2 py-0.5 bg-emerald-500/10 text-emerald-400 text-[8px] font-black uppercase tracking-widest rounded-full border border-emerald-500/20">
                Realizado
              </span>
              <span v-else class="px-2 py-0.5 bg-blue-500/10 text-blue-400 text-[8px] font-black uppercase tracking-widest rounded-full border border-blue-500/20">
                Confirmado
              </span>
            </div>
            
            <div class="grid grid-cols-2 gap-4 mb-6">
              <div class="space-y-1">
                <p class="text-[8px] font-black uppercase tracking-widest text-gray-500">Fecha</p>
                <div class="flex items-center gap-1.5 text-xs text-gray-300">
                  <svg class="w-3.5 h-3.5 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                  {{ g.fecha }}
                </div>
              </div>
              <div class="space-y-1">
                <p class="text-[8px] font-black uppercase tracking-widest text-gray-500">Pasajeros</p>
                <div class="flex items-center gap-1.5 text-xs text-gray-300 font-bold">
                   {{ g.personas }} Pax
                </div>
              </div>
            </div>

            <div class="flex items-center justify-between pt-4 border-t border-white/5">
              <div class="flex items-center gap-2">
                <span v-if="g.evidencias_count > 0" class="text-[10px] font-black text-emerald-400 flex items-center gap-1">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                  {{ g.evidencias_count }}
                </span>
                <span v-else class="text-[10px] font-black text-gray-600">0 fotos</span>
              </div>
              <div class="flex gap-2">
                <button @click="verTuristas(g)" class="p-3 bg-white/5 rounded-xl border border-white/10 text-emerald-400">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
                </button>
                <button v-if="g.estado === 'Realizado'" @click="openUpload(g)" class="px-4 py-2 bg-emerald-500 text-black rounded-xl text-[10px] font-black uppercase tracking-widest">
                  Subir
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- TABLA PARA ESCRITORIO -->
        <div class="hidden md:block overflow-x-auto">
          <table class="w-full">
            <thead class="bg-black/20">
              <tr>
                <th class="px-8 py-4 text-left text-[10px] font-black uppercase tracking-[0.2em] text-gray-500">Paquete Turístico</th>
                <th class="px-8 py-4 text-left text-[10px] font-black uppercase tracking-[0.2em] text-gray-500">Fecha Salida</th>
                <th class="px-8 py-4 text-center text-[10px] font-black uppercase tracking-[0.2em] text-gray-500">Pax Total</th>
                <th class="px-8 py-4 text-left text-[10px] font-black uppercase tracking-[0.2em] text-gray-500">Estado</th>
                <th class="px-8 py-4 text-left text-[10px] font-black uppercase tracking-[0.2em] text-gray-500">Evidencias</th>
                <th class="px-8 py-4 text-right text-[10px] font-black uppercase tracking-[0.2em] text-gray-500">Acciones</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[#1e362a]">
              <tr v-for="g in filteredRegistro" :key="g.id" class="hover:bg-white/5 transition-colors group">
                <td class="px-8 py-6 font-bold truncate max-w-[250px]">{{ g.tour }}</td>
                <td class="px-8 py-6 text-sm text-gray-300">
                  <div class="flex items-center gap-2">
                    <svg class="w-4 h-4 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                    {{ g.fecha }}
                  </div>
                </td>
                <td class="px-8 py-6 text-center text-sm font-bold text-gray-300">
                  {{ g.personas }} personas
                </td>
                <td class="px-8 py-6">
                  <span v-if="g.estado === 'Realizado'" class="px-3 py-1 bg-emerald-500/10 text-emerald-400 text-[10px] font-black uppercase tracking-widest rounded-full border border-emerald-500/20">
                    Realizado
                  </span>
                  <span v-else class="px-3 py-1 bg-blue-500/10 text-blue-400 text-[10px] font-black uppercase tracking-widest rounded-full border border-blue-500/20">
                    Confirmado
                  </span>
                </td>
                <td class="px-8 py-6">
                  <div v-if="g.evidencias_count > 0" class="flex items-center gap-2 text-emerald-400">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                    <span class="text-xs font-black">{{ g.evidencias_count }} fotos</span>
                  </div>
                  <span v-else class="text-xs text-gray-600 font-bold uppercase tracking-widest">Sin fotos</span>
                </td>
                <td class="px-8 py-6 text-right">
                  <div class="flex justify-end gap-3 translate-x-2 group-hover:translate-x-0 transition-transform opacity-0 group-hover:opacity-100 duration-300">
                    <button @click="verTuristas(g)" class="flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 hover:border-emerald-500/40 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
                      Ver Detalles
                    </button>
                    <button v-if="g.estado === 'Realizado'" @click="openUpload(g)" class="flex items-center gap-2 px-4 py-2 bg-emerald-500 text-black hover:bg-emerald-400 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all shadow-[0_4px_15px_rgba(0,209,139,0.3)]">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/></svg>
                      Subir fotos
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="filteredRegistro.length === 0">
                <td colspan="6" class="py-20 text-center text-gray-600 font-bold italic">
                  No se encontraron resultados que coincidan con los filtros.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- MODAL DE LISTADO DE TURISTAS Y EVIDENCIAS -->
    <div v-if="mostrarModalTuristas" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-[#0a1410]/95 backdrop-blur-sm" @click="mostrarModalTuristas = false"></div>
      
      <div class="relative bg-[#12221b] border border-white/10 rounded-3xl shadow-2xl w-full max-w-5xl max-h-[90vh] overflow-hidden flex flex-col animate-fade-in-up">
        
        <!-- Header -->
        <div class="p-8 border-b border-white/10 flex items-center justify-between">
            <div>
                <h3 class="text-2xl font-black text-white mb-1">Detalles de la Experiencia</h3>
                <p class="text-sm text-emerald-400 font-bold uppercase tracking-widest">{{ selectedTour?.tour }} — {{ selectedTour?.fecha }}</p>
            </div>
            <div class="flex items-center gap-4">
                <button v-if="selectedTour?.estado === 'Realizado'" @click="openUpload(selectedTour)" class="flex items-center gap-2 px-4 py-2 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 hover:bg-emerald-500/20 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4"/></svg>
                    Añadir Foto
                </button>
                <button @click="mostrarModalTuristas = false" class="p-2 hover:bg-white/5 rounded-full transition-colors">
                    <svg class="w-6 h-6 text-gray-500 hover:text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                </button>
            </div>
        </div>

        <div class="flex-1 overflow-y-auto grid grid-cols-1 lg:grid-cols-2 divide-y lg:divide-y-0 lg:divide-x divide-white/10">
            
            <!-- Izquierda: Listado de Pasajeros -->
            <div class="p-8">
                <h4 class="text-[10px] font-black uppercase tracking-[0.2em] text-gray-500 mb-6 flex items-center gap-2">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/></svg>
                    Pasajeros Registrados ({{ selectedTour?.turistas.length }})
                </h4>
                <div class="space-y-4">
                    <div v-for="t in selectedTour?.turistas" :key="t.id" class="bg-black/20 p-4 rounded-2xl border border-white/5 flex items-center justify-between group hover:border-emerald-500/30 transition-all">
                        <div>
                            <p class="font-bold text-gray-200 group-hover:text-white transition-colors">{{ t.nombre }}</p>
                            <p class="text-[10px] text-gray-500 font-bold uppercase tracking-widest">{{ t.identificacion }}</p>
                        </div>
                        <div class="text-right">
                            <span class="block px-2 py-0.5 rounded-full text-[8px] font-black uppercase tracking-widest mb-1"
                                  :class="t.estado === 'Realizado' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-blue-500/10 text-blue-400'">
                                {{ t.estado }}
                            </span>
                            <div v-if="t.rating" class="flex items-center justify-end gap-1 text-yellow-500">
                                <span class="font-black text-xs">{{ t.rating }}</span>
                                <svg class="w-3 h-3 fill-current" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Derecha: Galería de Imágenes -->
            <div class="p-8 bg-black/10">
                <h4 class="text-[10px] font-black uppercase tracking-[0.2em] text-gray-500 mb-6 flex items-center gap-2">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                    Galería de Evidencias ({{ selectedTour?.imagenes.length }})
                </h4>
                
                <div v-if="selectedTour?.imagenes.length > 0" class="grid grid-cols-2 sm:grid-cols-3 gap-3">
                    <div v-for="img in selectedTour.imagenes" :key="img.id" class="aspect-square rounded-xl overflow-hidden bg-black/40 border border-white/5 group/img relative">
                        <img :src="img.url" class="w-full h-full object-cover transition-transform duration-500 group-hover/img:scale-110" loading="lazy">
                        <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover/img:opacity-100 transition-opacity flex items-end p-2">
                            <span class="text-[8px] font-bold text-gray-300">{{ img.fecha }}</span>
                        </div>
                    </div>
                </div>

                <div v-else class="flex flex-col items-center justify-center py-20 bg-black/20 rounded-3xl border border-dashed border-white/10">
                    <svg class="w-12 h-12 text-gray-700 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                    <p class="text-sm text-gray-600 font-bold uppercase tracking-widest">No hay fotos subidas</p>
                    <button v-if="selectedTour?.estado === 'Realizado'" @click="openUpload(selectedTour)" class="mt-4 text-[10px] text-emerald-400 font-black uppercase tracking-widest hover:text-white transition-colors">
                        Subir la primera foto
                    </button>
                </div>
            </div>

        </div>

        <!-- Footer -->
        <div class="p-6 border-t border-white/10 bg-black/40 text-center">
            <p class="text-[9px] text-gray-600 font-black uppercase tracking-[0.3em]">
                Amazonia Viva — Módulo de Gestión de Experiencias
            </p>
        </div>
      </div>
    </div>

    <!-- Buscador Oculto de Archivos -->
    <input 
      type="file" 
      ref="fileInput" 
      class="hidden" 
      accept="image/*"
      multiple
      @change="handleFileUpload"
    />
  </div>
</template>

<style scoped>
.tracking-widest {
  letter-spacing: 0.25em;
}

@keyframes fade-in-up {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
.animate-fade-in-up {
    animation: fade-in-up 0.4s ease-out forwards;
}
</style>
