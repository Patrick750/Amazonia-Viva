<script setup>
import { ref } from 'vue';
import axios from '@/api/axios';
import { useNotificacion } from '@/composables/useNotificacion';

const API_URL = 'api/productos/';

const props = defineProps({
  abrir: Boolean,
  producto: Object
});

const emit = defineEmits(['cerrar', 'eliminadoExitoso']);
const isLoading = ref(false);
const { mostrarNotificacion } = useNotificacion();

const confirmarEliminar = async () => {
  if (!props.producto) return;
  isLoading.value = true;
  try {
    await axios.delete(`${API_URL}${props.producto.id}/`);
    mostrarNotificacion('¡Producto eliminado correctamente del inventario!', 'exito');
    setTimeout(() => {
        emit('eliminadoExitoso', props.producto.id);
    }, 1000);
  } catch (error) {
      console.error(error);
      mostrarNotificacion('Hubo un error al eliminar el producto', 'error');
  } finally {
      isLoading.value = false;
  }
};
</script>

<template>
  <Teleport to="body">
    <div v-if="abrir" class="fixed inset-0 z-[70] flex items-center justify-center p-4 sm:pt-24 animate-fade-in" @click.self="emit('cerrar')">
      
      <div class="absolute inset-0 bg-black/85 backdrop-blur-md"></div>

      <div class="relative bg-[#0d2114] border border-white/10 rounded-[2.5rem] shadow-[0_40px_100px_-20px_rgba(0,0,0,0.8)] w-full max-w-md px-8 pb-10 pt-16 sm:pt-20 text-center transform transition-all animate-scale-up overflow-visible">
        
        <div class="absolute -top-24 sm:-top-32 left-1/2 -translate-x-1/2 w-48 h-48 sm:w-60 sm:h-60 pointer-events-none group-hover:scale-110 transition-transform duration-500">
          
          <svg viewBox="-20 -20 240 240" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-full h-full drop-shadow-[0_0_30px_rgba(244,63,94,0.3)] overflow-visible">
            
            <!-- Sparkles -->
            <path d="M30 60 L10 40 M170 60 L190 40" stroke="#f43f5e" stroke-width="8" stroke-linecap="round" stroke-linejoin="round" class="animate-pulse" />
            
            <!-- Bouncing Security Lock -->
            <g class="animate-bounce" style="animation-duration: 2.5s;">
              <!-- Shackle (Arco) -->
              <path d="M70 100 V60 C70 30, 130 30, 130 60 V100" fill="none" stroke="#334155" stroke-width="20" stroke-linecap="round" stroke-linejoin="round" />
              <!-- Highlight on Shackle -->
              <path d="M70 100 V60 C70 45, 100 40, 100 40" fill="none" stroke="#94a3b8" stroke-width="6" stroke-linecap="round" opacity="0.4" />
              
              <!-- Lock Body -->
              <rect x="50" y="100" width="100" height="85" rx="20" fill="#f43f5e" stroke="#1e293b" stroke-width="12" stroke-linejoin="round" />
              <rect x="58" y="108" width="84" height="30" rx="12" fill="#fda4af" opacity="0.3" stroke="none" />
              <path d="M50 148 H150" stroke="#1e293b" stroke-width="10" />

              <!-- Keyhole -->
              <circle cx="100" cy="160" r="12" fill="#1e293b" />
              <path d="M94 165 L90 182 A8 8 0 0 0 110 182 L106 165 Z" fill="#1e293b" stroke="#1e293b" stroke-width="2" stroke-linejoin="round" />
              <circle cx="100" cy="160" r="4" fill="#fb7185" opacity="0.8" />
            </g>

            <!-- Decorative Elements -->
            <path d="M165 140 L172 158 L190 165 L172 172 L165 190 L158 172 L140 165 L158 158 Z" fill="#fb7185" stroke="#1e293b" stroke-width="4" stroke-linejoin="round" />
            <circle cx="35" cy="170" r="12" fill="#f43f5e" stroke="#1e293b" stroke-width="6" opacity="0.5" />
          </svg>
        </div>
        
        <h3 class="text-4xl font-black text-white tracking-tighter mb-4 mt-6">¡Un momento!</h3>
        <p class="text-white/40 mb-10 leading-relaxed font-bold text-sm tracking-tight px-4">
          Estás a punto de retirar definitivamente el producto <br>
          <span class="inline-block mt-3 px-4 py-2 bg-rose-500/10 border border-rose-500/20 text-rose-400 font-black text-xl rounded-2xl italic shadow-2xl">
            "{{ producto?.nombre }}"
          </span><br>
          <span class="block mt-4 text-[10px] uppercase tracking-[0.2em] font-black opacity-50 italic">¿Confirmas esta eliminación total?</span>
        </p>

        <div class="flex flex-col sm:flex-row items-center gap-4 w-full relative z-10 font-black uppercase tracking-widest text-[11px]">
          <button @click="emit('cerrar')" type="button" :disabled="isLoading"
            class="w-full sm:flex-1 px-8 py-4 rounded-2xl text-white/40 bg-white/5 border border-white/5 transition-all hover:bg-white/10 hover:text-white disabled:opacity-30 cursor-pointer">
            Cancelar
          </button>

          <button @click="confirmarEliminar" type="button" :disabled="isLoading"
            class="w-full sm:flex-1 px-8 py-4 rounded-2xl text-black bg-rose-500 border border-rose-500 shadow-xl shadow-rose-900/40 hover:bg-rose-400 hover:-translate-y-1 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3 cursor-pointer">
            
            <svg v-if="isLoading" class="animate-spin h-5 w-5 text-black" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            
            <span v-else>Borrar Todo</span>
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.animate-fade-in { animation: fadeIn 0.2s ease-out forwards; }
.animate-scale-up { animation: scaleUp 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards; }

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes scaleUp { from { opacity: 0; transform: scale(0.95) translateY(10px); } to { opacity: 1; transform: scale(1) translateY(0); } }
</style>
