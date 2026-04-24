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
    <div v-if="abrir" class="fixed inset-0 z-[100] flex items-center justify-center p-4 pt-24 animate-fade-in" @click.self="emit('cerrar')">
      
      <!-- Backdrop -->
      <div class="absolute inset-0 bg-[#06120b]/95 backdrop-blur-md"></div>

      <div class="relative bg-[#0d2114] rounded-[2.5rem] shadow-[0_0_80px_rgba(0,0,0,0.8)] w-full max-w-md px-10 pb-10 pt-20 text-center transform transition-all animate-scale-up border border-white/10 overflow-visible">
        
        <!-- Illustration Container -->
        <div class="absolute -top-32 left-1/2 -translate-x-1/2 w-56 h-56 pointer-events-none drop-shadow-[0_20px_40px_rgba(0,0,0,0.5)]">
          <svg viewBox="-20 -20 240 240" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-full h-full overflow-visible">
            
            <path d="M30 60 L10 40 M170 60 L190 40" stroke="#10b981" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" class="animate-pulse" />
            
            <path d="M150 70 C160 50, 175 70, 165 85 C155 100, 140 85, 150 70 Z" fill="#10b981" stroke="#06120b" stroke-width="5" stroke-linejoin="round" />

            <g class="animate-bounce" style="animation-duration: 3s;">
              <path d="M60 45 C60 15, 120 15, 120 45" fill="#06120b" stroke="#10b981" stroke-width="7" stroke-linejoin="round" />
              <ellipse cx="90" cy="45" rx="45" ry="12" fill="#0d2114" stroke="#10b981" stroke-width="7" />
              <path d="M62 40 Q90 50 118 40" stroke="#f43f5e" stroke-width="6" stroke-linecap="round" />
            </g>

            <path d="M50 120 Q10 80 15 110 Q25 140 45 145" fill="#10b981" stroke="#06120b" stroke-width="7" stroke-linejoin="round" />
            <path d="M130 120 Q170 80 165 110 Q155 140 135 145" fill="#10b981" stroke="#06120b" stroke-width="7" stroke-linejoin="round" />

            <path d="M90 180 C40 180, 40 90, 90 90 C140 90, 140 180, 90 180 Z" fill="#06120b" stroke="#10b981" stroke-width="7" stroke-linejoin="round" />
            
            <path d="M90 180 C60 180, 60 130, 90 130 C120 130, 120 180, 90 180 Z" fill="#0d2114" stroke="#10b981" stroke-width="5" stroke-linejoin="round" />

            <circle cx="70" cy="100" r="25" fill="#06120b" stroke="#10b981" stroke-width="7" />
            <circle cx="110" cy="100" r="25" fill="#06120b" stroke="#10b981" stroke-width="7" />
            
            <circle cx="75" cy="100" r="4" fill="#10b981" />
            <circle cx="105" cy="100" r="4" fill="#10b981" />

            <path d="M80 130 Q90 160 100 130 Q90 120 80 130 Z" fill="#f43f5e" stroke="#06120b" stroke-width="6" stroke-linejoin="round" />
          </svg>
        </div>
        
        <div class="mb-8">
          <div class="text-[10px] font-black text-rose-500 uppercase tracking-[0.4em] mb-4">Acción Irreversible</div>
          <h3 class="text-4xl font-black text-white tracking-tighter mb-4">¿Estás seguro?</h3>
          <p class="text-white/40 mb-6 leading-relaxed font-medium px-4">
            Vas a eliminar el tour <br>
            <span class="block mt-2 px-4 py-2 bg-rose-500/10 border border-rose-500/20 rounded-2xl text-rose-400 font-black text-lg">
              "{{ paquete?.nombre }}"
            </span>
          </p>
          <div class="text-[9px] font-black text-white/20 uppercase tracking-widest italic flex items-center justify-center gap-2">
            <span class="w-1.5 h-1.5 rounded-full bg-rose-500/40"></span>
            El inventario se ajustará automáticamente
            <span class="w-1.5 h-1.5 rounded-full bg-rose-500/40"></span>
          </div>
        </div>

        <div class="flex flex-col sm:flex-row items-center gap-4 w-full relative z-10 pt-2">
          <button @click="emit('cerrar')" type="button" :disabled="isLoading"
            class="w-full sm:flex-1 px-8 py-5 rounded-2xl font-black text-white/60 bg-white/5 border border-white/10 hover:bg-white/10 hover:text-white transition-all disabled:opacity-50 uppercase text-[10px] tracking-widest">
            Mejor no
          </button>

          <button @click="confirmarEliminar" type="button" :disabled="isLoading"
            class="w-full sm:flex-1 px-8 py-5 rounded-2xl font-black text-white bg-rose-600 hover:bg-rose-500 shadow-[0_10px_20px_rgba(225,29,72,0.3)] transition-all disabled:opacity-70 disabled:cursor-not-allowed flex items-center justify-center gap-3 uppercase text-[10px] tracking-widest group">
            
            <svg v-if="isLoading" class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            
            <span v-else class="group-hover:scale-110 transition-transform">¡Eliminar!</span>
            <svg v-if="!isLoading" class="w-4 h-4 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" /></svg>
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.animate-fade-in { animation: fadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
.animate-scale-up { animation: scaleUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards; }

@keyframes fadeIn { from { opacity: 0; backdrop-filter: blur(0px); } to { opacity: 1; backdrop-filter: blur(8px); } }
@keyframes scaleUp { from { opacity: 0; transform: scale(0.9) translateY(40px); } to { opacity: 1; transform: scale(1) translateY(0); } }
</style>
