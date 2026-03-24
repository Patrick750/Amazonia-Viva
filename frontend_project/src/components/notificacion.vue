<script setup>
import { useNotificacion } from '@/composables/useNotificacion';

const { notificacion, cerrarNotificacion } = useNotificacion();
</script>

<template>
  <Teleport to="body">
    <!-- Toast Notificación Centralizada -->
    <div v-if="notificacion.mostrar"
      :class="['fixed top-6 right-6 z-[200] flex items-center gap-4 px-5 py-4 rounded-2xl shadow-2xl border max-w-sm animate-slide-in',
      notificacion.tipo === 'exito'
        ? 'bg-white border-emerald-200 shadow-emerald-100'
        : 'bg-white border-red-200 shadow-red-100']">
      <div :class="['w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0',
        notificacion.tipo === 'exito' ? 'bg-emerald-100' : 'bg-red-100']">
        <svg v-if="notificacion.tipo === 'exito'" class="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg>
        <svg v-else class="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
      </div>
      <p :class="['text-sm font-semibold flex-1 text-slate-800']">
        {{ notificacion.mensaje }}
      </p>
      <button @click="cerrarNotificacion"
        class="text-slate-300 hover:text-slate-600 transition-colors">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
      </button>
    </div>
  </Teleport>
</template>

<style scoped>
.animate-slide-in {
  animation: slideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
@keyframes slideIn {
  from { opacity: 0; transform: translateX(20px); }
  to   { opacity: 1; transform: translateX(0); }
}
</style>
