<script setup>
import { ref } from 'vue';
import { eliminarPaquete } from '@/composables/gestion-tours/paquetes';
import { useNotificacion } from '@/composables/useNotificacion';

const props = defineProps({
  abrir: Boolean,
  paquete: Object
});

const emit = defineEmits(['cerrar', 'eliminadoExitoso']);

const isLoading = ref(false);

const { mostrarNotificacion } = useNotificacion();

const confirmarEliminar = async () => {
  if (!props.paquete) return;
  isLoading.value = true;
  try {
    await eliminarPaquete(props.paquete.id);
    mostrarNotificacion('¡Tour eliminado correctamente!', 'exito');
    setTimeout(() => {
        emit('eliminadoExitoso', props.paquete.id);
    }, 1000);
  } catch (error) {
      console.error(error);
      mostrarNotificacion('Hubo un error al eliminar el tour', 'error');
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
            
            <path d="M30 60 L10 40 M170 60 L190 40" stroke="#1E293B" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" class="animate-pulse" />
            
            <path d="M150 70 C160 50, 175 70, 165 85 C155 100, 140 85, 150 70 Z" fill="#38BDF8" stroke="#1E293B" stroke-width="5" stroke-linejoin="round" />

            <g class="animate-bounce" style="animation-duration: 2s;">
              <path d="M60 45 C60 15, 120 15, 120 45" fill="#D4A373" stroke="#1E293B" stroke-width="7" stroke-linejoin="round" />
              <ellipse cx="90" cy="45" rx="45" ry="12" fill="#FAEDCD" stroke="#1E293B" stroke-width="7" />
              <path d="M62 40 Q90 50 118 40" stroke="#E63946" stroke-width="6" stroke-linecap="round" />
            </g>

            <path d="M50 120 Q10 80 15 110 Q25 140 45 145" fill="#F4A261" stroke="#1E293B" stroke-width="7" stroke-linejoin="round" />
            <path d="M130 120 Q170 80 165 110 Q155 140 135 145" fill="#F4A261" stroke="#1E293B" stroke-width="7" stroke-linejoin="round" />

            <path d="M90 180 C40 180, 40 90, 90 90 C140 90, 140 180, 90 180 Z" fill="#E9C46A" stroke="#1E293B" stroke-width="7" stroke-linejoin="round" />
            
            <path d="M90 180 C60 180, 60 130, 90 130 C120 130, 120 180, 90 180 Z" fill="#FFF3B0" stroke="#1E293B" stroke-width="5" stroke-linejoin="round" />

            <circle cx="70" cy="100" r="25" fill="#FFFFFF" stroke="#1E293B" stroke-width="7" />
            <circle cx="110" cy="100" r="25" fill="#FFFFFF" stroke="#1E293B" stroke-width="7" />
            
            <circle cx="75" cy="100" r="4" fill="#1E293B" />
            <circle cx="105" cy="100" r="4" fill="#1E293B" />

            <path d="M80 130 Q90 160 100 130 Q90 120 80 130 Z" fill="#E63946" stroke="#1E293B" stroke-width="6" stroke-linejoin="round" />
          </svg>
        </div>
        
        <h3 class="text-3xl font-black text-slate-800 tracking-tight mb-3 mt-4">¡Pausa ahí!</h3>
        <p class="text-slate-600 mb-8 leading-relaxed font-medium">
          Estás a punto de eliminar el tour <br>
          <strong class="text-slate-900 font-black text-lg underline decoration-rose-500 decoration-4 underline-offset-4">"{{ paquete?.nombre }}"</strong>.<br>
          ¡Nuestro guía emplumado se quedará sin trabajo!
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
.animate-slide-in { animation: slideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards; }

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes scaleUp { from { opacity: 0; transform: scale(0.95) translateY(10px); } to { opacity: 1; transform: scale(1) translateY(0); } }
@keyframes slideIn { from { opacity: 0; transform: translateX(20px); } to { opacity: 1; transform: translateX(0); } }
</style>
