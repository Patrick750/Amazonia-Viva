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
    <div v-if="abrir" class="fixed inset-0 z-[70] flex items-center justify-center p-4 pt-24 animate-fade-in" @click.self="emit('cerrar')">
      
      <div class="absolute inset-0 bg-slate-900/60 backdrop-blur-sm"></div>

      <div class="relative bg-white rounded-[2.5rem] shadow-[0_20px_60px_-15px_rgba(0,0,0,0.4)] w-full max-w-md px-8 pb-8 pt-16 text-center transform transition-all animate-scale-up border-4 border-slate-800 overflow-visible">
        
        <div class="absolute -top-28 left-1/2 -translate-x-1/2 w-52 h-52 pointer-events-none group-hover:scale-105 transition-transform duration-300">
          
          <svg viewBox="-20 -20 240 240" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-full h-full drop-shadow-2xl overflow-visible">
            
            <!-- Sparkles -->
            <path d="M30 60 L10 40 M170 60 L190 40" stroke="#1E293B" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" class="animate-pulse" />
            
            <!-- Bouncing Security Lock -->
            <g class="animate-bounce" style="animation-duration: 2s;">
              <!-- Shackle (Arco) -->
              <path d="M70 100 V60 C70 30, 130 30, 130 60 V100" fill="none" stroke="#94A3B8" stroke-width="18" stroke-linecap="round" stroke-linejoin="round" />
              <!-- Highlight on Shackle -->
              <path d="M70 100 V60 C70 45, 100 40, 100 40" fill="none" stroke="#F8FAFC" stroke-width="6" stroke-linecap="round" opacity="0.8" />
              
              <!-- Lock Body -->
              <rect x="50" y="100" width="100" height="80" rx="16" fill="#FBBF24" stroke="#1E293B" stroke-width="10" stroke-linejoin="round" />
              <rect x="55" y="105" width="90" height="35" rx="12" fill="#FDE68A" stroke="none" />
              <path d="M50 145 H150" stroke="#1E293B" stroke-width="8" />

              <!-- Keyhole -->
              <circle cx="100" cy="155" r="10" fill="#1E293B" />
              <path d="M95 160 L92 175 A6 6 0 0 0 108 175 L105 160 Z" fill="#1E293B" stroke="#1E293B" stroke-width="2" stroke-linejoin="round" />
              <circle cx="100" cy="155" r="4" fill="#FDE68A" opacity="0.6" />
            </g>

            <!-- Decorative Stars -->
            <path d="M160 130 L165 145 L180 150 L165 155 L160 170 L155 155 L140 150 L155 145 Z" fill="#38BDF8" stroke="#1E293B" stroke-width="4" stroke-linejoin="round" />
            <circle cx="35" cy="160" r="10" fill="#F4A261" stroke="#1E293B" stroke-width="5" />
          </svg>
        </div>
        
        <h3 class="text-3xl font-black text-slate-800 tracking-tight mb-3 mt-4">¡Alto ahí!</h3>
        <p class="text-slate-600 mb-8 leading-relaxed font-medium">
          Estás a punto de retirar de circulación el producto <br>
          <strong class="text-slate-900 font-black text-lg underline decoration-rose-500 decoration-4 underline-offset-4">"{{ producto?.nombre }}"</strong>.<br>
          Esta acción removerá el inventario completamente.
        </p>

        <div class="flex items-center gap-4 w-full relative z-10">
          <button @click="emit('cerrar')" type="button" :disabled="isLoading"
            class="flex-1 px-5 py-3.5 rounded-2xl font-black text-slate-700 bg-white border-4 border-slate-800 shadow-[0_6px_0_0_#1e293b] hover:shadow-[0_2px_0_0_#1e293b] hover:translate-y-1 transition-all disabled:opacity-50 cursor-pointer">
            Mejor no
          </button>

          <button @click="confirmarEliminar" type="button" :disabled="isLoading"
            class="flex-1 px-5 py-3.5 rounded-2xl font-black text-white bg-rose-500 border-4 border-slate-800 shadow-[0_6px_0_0_#1e293b] hover:shadow-[0_2px_0_0_#1e293b] hover:translate-y-1 transition-all disabled:opacity-70 disabled:cursor-not-allowed flex items-center justify-center gap-2 cursor-pointer">
            
            <svg v-if="isLoading" class="animate-spin h-6 w-6 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            
            <span v-else>¡Borrar!</span>
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
