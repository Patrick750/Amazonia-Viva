<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import axios from '@/api/axios';

const route = useRoute();
const detalleId = route.params.id;

const data = ref({ tour_nombre: '', evidencias: [], calificacion: null });
const rating = ref(0);
const comentario = ref('');
const isSubmitting = ref(false);
const showSuccess = ref(false);
const activeSlide = ref(0);

const fetchData = async () => {
    try {
        const response = await axios.get(`api/experiencias/${detalleId}/feedback/`);
        data.value = response.data;
        if (data.value.calificacion) {
            rating.value = data.value.calificacion.puntuacion;
            comentario.value = data.value.calificacion.comentario;
        }
    } catch (error) {
        console.error('Error fetching feedback data:', error);
    }
};

const submitRating = async () => {
    if (rating.value === 0) return;
    isSubmitting.value = true;
    try {
        await axios.post(`api/experiencias/${detalleId}/feedback/`, {
            puntuacion: rating.value,
            comentario: comentario.value
        });
        showSuccess.value = true;
        setTimeout(() => showSuccess.value = false, 3000);
    } catch (error) {
        console.error('Error submitting rating:', error);
    } finally {
        isSubmitting.value = false;
    }
};

const downloadImage = async (url, index) => {
    try {
        const response = await fetch(url);
        const blob = await response.blob();
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `experiencia-amazonia-${index + 1}.jpg`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } catch (error) {
        console.error('Error downloading image:', error);
    }
};

const nextSlide = () => {
    activeSlide.value = (activeSlide.value + 1) % data.value.evidencias.length;
};

const prevSlide = () => {
    activeSlide.value = (activeSlide.value - 1 + data.value.evidencias.length) % data.value.evidencias.length;
};

onMounted(() => {
    fetchData();
});
</script>

<template>
  <div class="min-h-screen bg-[#0a1410] text-white py-12 px-6">
    <div class="max-w-4xl mx-auto">
      
      <!-- Volver -->
      <router-link to="/mis-reservas" class="inline-flex items-center gap-2 text-emerald-400 font-black uppercase text-[10px] tracking-widest mb-8 hover:text-white transition-colors">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
        Mis Reservas
      </router-link>

      <header class="mb-12">
        <h1 class="text-4xl font-black mb-2 tracking-tighter">{{ data.tour_nombre }}</h1>
        <p class="text-gray-400">Tu álbum de recuerdos y calificación de la experiencia</p>
      </header>

      <!-- Carrucel de Evidencias -->
      <section v-if="data.evidencias.length > 0" class="mb-16 relative group">
        <div class="aspect-video bg-black/40 rounded-[32px] overflow-hidden border border-[#1e362a] relative">
          
          <!-- Slides -->
          <div class="w-full h-full">
            <template v-for="(img, index) in data.evidencias" :key="img.id">
              <transition name="fade">
                <div v-if="activeSlide === index" class="absolute inset-0">
                  <img :src="img.url" class="w-full h-full object-cover" alt="Recuerdo de la experiencia">
                  <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent"></div>
                  
                  <!-- Info Botón Descarga -->
                  <div class="absolute bottom-8 right-8">
                    <button @click="downloadImage(img.url, index)" class="bg-[#00d18b] text-black px-6 py-3 rounded-full font-black text-xs uppercase tracking-widest flex items-center gap-2 hover:bg-[#00f5d4] transition-all shadow-2xl">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
                      Descargar Foto
                    </button>
                  </div>
                </div>
              </transition>
            </template>
          </div>

          <!-- Navegación -->
          <button @click="prevSlide" class="absolute left-6 top-1/2 -translate-y-1/2 w-12 h-12 rounded-full bg-black/50 border border-white/10 flex items-center justify-center hover:bg-emerald-500 hover:text-black transition-all opacity-0 group-hover:opacity-100">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7"/></svg>
          </button>
          <button @click="nextSlide" class="absolute right-6 top-1/2 -translate-y-1/2 w-12 h-12 rounded-full bg-black/50 border border-white/10 flex items-center justify-center hover:bg-emerald-500 hover:text-black transition-all opacity-0 group-hover:opacity-100">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7"/></svg>
          </button>

          <!-- Indicadores -->
          <div class="absolute bottom-8 left-1/2 -translate-x-1/2 flex gap-2">
            <div v-for="(img, index) in data.evidencias" :key="'dot-'+index" 
                 @click="activeSlide = index"
                 :class="activeSlide === index ? 'w-8 bg-emerald-500' : 'w-2 bg-white/20'"
                 class="h-1 rounded-full cursor-pointer transition-all"></div>
          </div>
        </div>
      </section>

      <div v-else class="mb-16 p-12 bg-[#12221b] border border-[#1e362a] rounded-[32px] text-center">
        <svg class="w-16 h-16 text-gray-700 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
        <p class="text-gray-500 font-black uppercase tracking-[0.3em]">La agencia aún no ha subido fotos de tu tour</p>
      </div>

      <!-- Calificación -->
      <section class="bg-[#12221b] border border-[#1e362a] rounded-[40px] p-10 md:p-16 shadow-2xl relative overflow-hidden">
        <div class="absolute top-0 right-0 w-64 h-64 bg-emerald-500/5 rounded-full blur-3xl pointer-events-none"></div>
        
        <div class="max-w-xl">
          <h2 class="text-3xl font-black mb-8 tracking-tighter uppercase">¿Cómo fue tu aventura?</h2>
          
          <!-- Estrellas -->
          <div class="flex gap-4 mb-10">
            <button v-for="star in 5" :key="star" 
                    @click="rating = star"
                    class="transition-all hover:scale-110">
              <svg :class="star <= rating ? 'text-emerald-400 fill-emerald-400' : 'text-gray-700'"
                   class="w-12 h-12" viewBox="0 0 20 20" fill="currentColor">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
              </svg>
            </button>
          </div>

          <!-- Comentario -->
          <div class="mb-8">
            <label class="block text-[10px] font-black uppercase tracking-widest text-gray-400 mb-3">Tu testimonio selvático</label>
            <textarea v-model="comentario" 
                      placeholder="Cuéntanos qué fue lo que más te impactó..."
                      class="w-full bg-black/40 border border-[#1e362a] rounded-2xl p-6 text-white h-32 focus:border-emerald-500/50 outline-none transition-all placeholder:text-gray-700"></textarea>
          </div>

          <button @click="submitRating" 
                  :disabled="rating === 0 || isSubmitting"
                  class="w-full md:w-auto bg-[#00d18b] text-black px-12 py-4 rounded-2xl font-black text-xs uppercase tracking-widest hover:bg-[#00f5d4] disabled:opacity-30 transition-all flex items-center justify-center gap-3">
            <span v-if="isSubmitting">Procesando...</span>
            <span v-else>Guardar Calificación</span>
            <svg v-if="!isSubmitting" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg>
          </button>

          <transition name="fade">
            <div v-if="showSuccess" class="mt-6 text-emerald-400 text-xs font-bold uppercase tracking-widest animate-pulse">
              ¡Gracias! Tu valoración ha sido registrada.
            </div>
          </transition>
        </div>
      </section>

    </div>
  </div>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
.tracking-widest {
  letter-spacing: 0.25em;
}
</style>
