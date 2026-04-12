<script setup>
import { ref, onMounted } from 'vue';
import axios from '@/api/axios.js';

const experiencias = ref([]);
const isLoading = ref(true);

// State for Rating Modal
const showRatingModal = ref(false);
const selectedExp = ref(null);
const rating = ref(0);
const comment = ref('');
const isSubmitting = ref(false);
const downloadingZip = ref(null);

const fetchData = async () => {
    isLoading.value = true;
    try {
        const { data } = await axios.get('api/turista/experiencias/');
        experiencias.value = data;
    } catch (error) {
        console.error('Error fetching experiences:', error);
    } finally {
        isLoading.value = false;
    }
};

const openRating = (exp) => {
    selectedExp.value = exp;
    rating.value = exp.calificacion?.puntuacion || 0;
    comment.value = exp.calificacion?.comentario || '';
    showRatingModal.value = true;
};

const submitRating = async () => {
    if (rating.value === 0) return;
    isSubmitting.value = true;
    try {
        await axios.post(`api/experiencias/${selectedExp.value.id}/feedback/`, {
            puntuacion: rating.value,
            comentario: comment.value
        });
        await fetchData();
        showRatingModal.value = false;
    } catch (error) {
        console.error('Error submitting rating:', error);
    } finally {
        isSubmitting.value = false;
    }
};

const downloadImage = (url, name) => {
    const link = document.createElement('a');
    link.href = url;
    link.download = name || 'evidencia.jpg';
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
};

const downloadPack = async (expId, tourName) => {
    downloadingZip.value = expId;
    try {
        const response = await axios.get(`api/experiencias/${expId}/zip/`, {
            responseType: 'blob'
        });
        
        // Crear un link temporal para la descarga
        const url = window.URL.createObjectURL(response.data);
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `fotos-${tourName.replace(/\s+/g, '-')}.zip`);
        document.body.appendChild(link);
        link.click();
        
        // Limpiar
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Error downloading zip pack:', error);
        alert('Hubo un error al generar el archivo ZIP. Inténtalo de nuevo.');
    } finally {
        downloadingZip.value = null;
    }
};

onMounted(fetchData);
</script>

<template>
  <div class="min-h-screen bg-[#0a1410] text-white font-sans selection:bg-emerald-500/30">
    <div class="max-w-4xl mx-auto px-6 py-12">
      
      <!-- Volver -->
      <router-link to="/mi-perfil" class="inline-flex items-center gap-2 text-emerald-400 font-black uppercase text-[10px] tracking-widest mb-8 hover:text-white transition-colors group/back">
        <svg class="w-4 h-4 transition-transform group-hover/back:-translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
        Mi Perfil
      </router-link>

      <!-- Encabezado -->
      <header class="mb-12">
        <h1 class="text-5xl font-black tracking-tighter mb-2">Mis Experiencias</h1>
        <p class="text-gray-400 text-lg">Revive tus aventuras y comparte tus opiniones</p>
      </header>

      <!-- Skeleton Loading -->
      <div v-if="isLoading" class="space-y-6">
        <div v-for="i in 2" :key="i" class="bg-[#12221b] h-64 rounded-2xl animate-pulse border border-[#1e362a]"></div>
      </div>

      <!-- Lista de Experiencias -->
      <div v-else class="space-y-8">
        <div v-if="experiencias.length === 0" class="py-20 text-center bg-[#12221b] rounded-3xl border border-dashed border-[#1e362a]">
          <svg class="w-16 h-16 text-gray-700 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M11 15l-3-3m0 0l3-3m-3 3h8M3 12a9 9 0 1118 0 9 9 0 01-18 0z"/></svg>
          <p class="text-xl font-bold text-gray-500">Aún no tienes experiencias registradas</p>
          <router-link to="/catalogo/tours" class="mt-4 inline-block text-emerald-400 font-black uppercase text-xs tracking-widest hover:underline">¡Empieza tu aventura ahora!</router-link>
        </div>

        <div v-for="exp in experiencias" :key="exp.id" class="bg-[#12221b] border border-[#1e362a] rounded-3xl shadow-2xl overflow-hidden transition-all hover:border-emerald-500/30 group">
          
          <!-- SECCIÓN SUPERIOR: Información y Estado -->
          <div class="p-8 pb-6 flex flex-col md:flex-row justify-between items-start gap-6">
            <div class="space-y-3">
              <h2 class="text-3xl font-black text-white leading-tight">{{ exp.tour_nombre }}</h2>
              
              <div class="flex flex-wrap gap-x-6 gap-y-2">
                <div class="flex items-center gap-2 text-gray-400 text-sm font-medium">
                  <svg class="w-4 h-4 text-emerald-500/60" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m4 0h1m-5 10h1m4 0h1m-5-4h1m4 0h1"/></svg>
                  {{ exp.agencia.nombre }}
                </div>
                <div class="flex items-center gap-2 text-gray-400 text-sm font-medium">
                  <svg class="w-4 h-4 text-emerald-500/60" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                  {{ exp.fecha }}
                </div>
                <div class="flex items-center gap-2 text-gray-400 text-sm font-medium">
                  <svg class="w-4 h-4 text-emerald-500/60" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/></svg>
                  {{ exp.personas }} viajeros
                </div>
              </div>
            </div>

            <div class="shrink-0">
              <span class="px-5 py-2 bg-emerald-500/10 text-emerald-400 text-[10px] font-black uppercase tracking-widest rounded-full border border-emerald-500/20 shadow-[0_0_15px_rgba(16,185,129,0.1)]">
                {{ exp.estado }}
              </span>
            </div>
          </div>

          <!-- SECCIÓN MEDIA: Evidencias -->
          <div class="px-8 py-6 bg-black/10 border-y border-white/5">
            <h4 class="text-[10px] font-black uppercase tracking-widest text-gray-500 mb-4 flex items-center gap-2">
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
              Evidencias Fotográficas
            </h4>
            
            <div v-if="exp.evidencias.length > 0" class="flex flex-nowrap gap-4 overflow-x-auto pb-4 scrollbar-hide">
              <div v-for="ev in exp.evidencias" :key="ev.id" class="shrink-0 w-32 h-32 rounded-2xl overflow-hidden border border-white/10 relative group/pic">
                <img :src="ev.url" class="w-full h-full object-cover transition-transform group-hover/pic:scale-110">
                <button @click="downloadImage(ev.url, `foto-${exp.tour_nombre}-${ev.id}`)" class="absolute inset-0 bg-black/60 opacity-0 group-hover/pic:opacity-100 transition-opacity flex items-center justify-center">
                  <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
                </button>
              </div>
            </div>
            <div v-else class="py-8 text-center bg-[#1a2e24] rounded-2xl border border-dashed border-white/5 mx-2">
              <p class="text-[10px] text-gray-500 font-bold uppercase tracking-widest italic">La agencia aún no ha subido fotos de esta experiencia</p>
            </div>
          </div>

          <!-- SECCIÓN INFERIOR: Acciones -->
          <div class="p-8 pt-6 flex flex-wrap gap-4">
            <button @click="openRating(exp)" class="flex items-center gap-2 px-6 py-3 bg-white/5 border border-white/10 hover:border-emerald-500/40 hover:bg-white/10 rounded-2xl text-[11px] font-black uppercase tracking-widest transition-all">
              <svg class="w-5 h-5" :class="exp.calificacion ? 'text-yellow-500 fill-current' : 'text-gray-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.54 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.784.57-1.838-.196-1.539-1.117l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"/></svg>
              {{ exp.calificacion ? 'Editar Calificación' : 'Calificar Experiencia' }}
            </button>

            <button 
              v-if="exp.evidencias.length > 0" 
              @click="downloadPack(exp.id, exp.tour_nombre)" 
              :disabled="downloadingZip === exp.id"
              class="flex items-center gap-2 px-6 py-3 bg-emerald-500/5 text-emerald-400 border border-emerald-500/20 hover:bg-emerald-500/10 rounded-2xl text-[11px] font-black uppercase tracking-widest transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg v-if="downloadingZip === exp.id" class="animate-spin h-5 w-5 text-emerald-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
              {{ downloadingZip === exp.id ? 'Preparando ZIP...' : 'Descargar Pack Fotos' }}
            </button>
          </div>

        </div>
      </div>

    </div>

    <!-- MODAL DE CALIFICACIÓN -->
    <div v-if="showRatingModal" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-[#0a1410]/95 backdrop-blur-sm" @click="showRatingModal = false"></div>
      
      <div class="relative bg-[#12221b] border border-white/10 rounded-3xl shadow-2xl w-full max-w-lg p-8 animate-fade-in-up">
        <h3 class="text-2xl font-black mb-1">¿Qué te pareció el tour?</h3>
        <p class="text-emerald-400 font-bold text-xs uppercase tracking-widest mb-8">{{ selectedExp?.tour_nombre }}</p>

        <div class="space-y-8">
          <!-- Estrellas -->
          <div class="flex justify-center gap-3">
            <button v-for="i in 5" :key="i" @click="rating = i" class="transition-transform hover:scale-125">
              <svg class="w-10 h-10" :class="i <= rating ? 'text-yellow-500 fill-current' : 'text-white/10'" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.54 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.784.57-1.838-.196-1.539-1.117l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"/></svg>
            </button>
          </div>

          <!-- Comentario -->
          <div class="space-y-2">
            <label class="text-[10px] font-black uppercase tracking-[0.2em] text-gray-500">Cuéntanos más (opcional)</label>
            <textarea 
              v-model="comment" 
              placeholder="Tu opinión nos ayuda a mejorar..."
              class="w-full bg-black/40 border border-white/10 rounded-2xl p-4 text-sm focus:outline-none focus:border-emerald-500/50 transition-all h-32 resize-none"
            ></textarea>
          </div>

          <!-- Acciones -->
          <div class="flex flex-col gap-3">
            <button @click="submitRating" :disabled="isSubmitting || rating === 0" class="w-full bg-emerald-500 text-black py-4 rounded-2xl font-black uppercase text-xs tracking-widest hover:bg-emerald-400 transition-all shadow-[0_10px_20px_rgba(0,209,139,0.2)] disabled:opacity-50 disabled:cursor-not-allowed">
              {{ isSubmitting ? 'Guardando...' : 'Publicar Calificación' }}
            </button>
            <button @click="showRatingModal = false" class="w-full text-gray-500 font-bold uppercase text-[10px] tracking-widest hover:text-white transition-colors">
              Ahora no
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
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
