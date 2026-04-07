<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: 'info'
  }
})

const emit = defineEmits(['update:modelValue'])

const menuItems = [
  {
    id: 'info',
    label: 'Información cuenta',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>`
  },
  {
    id: 'view',
    label: 'Vista perfil',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>`
  }
]

function selectItem(id) {
  emit('update:modelValue', id)
}
</script>

<template>
  <aside class="w-full lg:w-64 shrink-0 px-4 lg:px-0">
    <nav class="flex lg:flex-col gap-2 overflow-x-auto lg:overflow-visible pb-4 lg:pb-0 scrollbar-hide">
      <button
        v-for="item in menuItems"
        :key="item.id"
        @click="selectItem(item.id)"
        :class="[
          'flex items-center gap-3 px-4 py-3 rounded-2xl text-sm font-bold transition-all duration-300 whitespace-nowrap lg:whitespace-normal w-full group',
          modelValue === item.id
            ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-600/20 translate-x-1 lg:translate-x-2'
            : 'bg-white text-slate-600 hover:bg-slate-50 border border-slate-200/60'
        ]"
      >
        <div 
          class="shrink-0 transition-transform duration-300 group-hover:scale-110"
          v-html="item.icon"
        ></div>
        <span>{{ item.label }}</span>
        
        <!-- Indicador activo solo en Desktop -->
        <div 
          v-if="modelValue === item.id"
          class="hidden lg:block ml-auto w-1.5 h-1.5 rounded-full bg-emerald-200 animate-pulse"
        ></div>
      </button>
    </nav>

    <!-- Caja de ayuda o info extra -->
    <div class="hidden lg:block mt-8 p-6 bg-gradient-to-br from-emerald-50 to-teal-50 rounded-3xl border border-emerald-100 shadow-sm">
      <div class="w-10 h-10 bg-white rounded-xl shadow-sm flex items-center justify-center mb-4 text-emerald-600">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
      </div>
      <h4 class="text-xs font-extrabold text-emerald-900 uppercase tracking-widest mb-2">Seguridad</h4>
      <p class="text-[11px] text-emerald-700 font-medium leading-relaxed">
        Tus datos están protegidos bajo cifrado de extremo a extremo conforme a la ley de protección de datos personales.
      </p>
    </div>
  </aside>
</template>

<style scoped>
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
