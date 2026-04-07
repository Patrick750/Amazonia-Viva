<script setup>

    import { ref } from 'vue';

    const props = defineProps(['datos'])
    const emit = defineEmits(['editar', 'eliminar', 'verDetalles'])

    const deleteTour = (id) => {
        emit('eliminar', id);
    };

</script>

<template>
    <section class="bg-white/65 backdrop-blur-xl border border-white/80 rounded-2xl p-6 shadow-sm">
    
        <div class="mb-6">
            <h2 class="text-lg font-semibold text-slate-800">Mis Tours</h2>
            <p class="text-sm text-slate-500">{{ datos.length }} tours en total</p>
        </div>

        <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse min-w-[800px]">
            <thead>
                <tr class="text-sm font-semibold text-slate-500 border-b border-white/80">
                <th class="pb-3 pl-2 w-1/3">Tour</th>
                <th class="pb-3">Ubicación</th>
                <th class="pb-3">Duración</th>
                <th class="pb-3">Precio</th>
                <th class="pb-3">Capacidad</th>
                <th class="pb-3">Calificación</th>
                <th class="pb-3 text-center">Ventas</th>
                <th class="pb-3 text-center">Acciones</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="tour in datos" :key="tour.id" class="border-b border-white/40 hover:bg-white/40 transition-colors group">
                <td class="py-4 pl-2">
                    <div class="flex items-center gap-3">
                    <div class="relative flex-shrink-0">
                      <!-- Indicador de estado -->
                      <span 
                        class="absolute -top-1 -right-1 w-3.5 h-3.5 rounded-full border-2 border-white z-10 shadow-sm transition-colors"
                        :class="tour.activo ? 'bg-emerald-500' : 'bg-red-500'"
                        :title="tour.activo !== false ? 'Tour Activo' : 'Tour Inactivo'"
                      ></span>
                      <div class="w-12 h-12 rounded-lg overflow-hidden border border-white shadow-sm bg-emerald-100">
                        <img 
                          v-if="tour.imagen_paquete && tour.imagen_paquete.length > 0"
                          :src="tour.imagen_paquete.find(i => i.es_portada)?.url || tour.imagen_paquete[0].url" 
                          :alt="tour.nombre"
                          class="w-full h-full object-cover"
                        />
                        <div v-else class="w-full h-full flex items-center justify-center">
                          <svg class="w-6 h-6 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                        </div>
                      </div>
                    </div>
                    <div>
                        <h3 class="font-semibold text-slate-800 text-sm cursor-pointer hover:text-emerald-600 hover:underline transition-all" @click="emit('verDetalles', tour)">{{ tour.nombre }}</h3>
                        <span class="text-xs text-slate-500">{{ tour.category }}</span>
                    </div>
                    </div>
                </td>
                <td class="py-4 text-sm text-slate-600">
                    <div class="flex items-center gap-1">
                    <svg class="w-4 h-4 text-emerald-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
                    {{ tour.ubicacion }}
                    </div>
                </td>
                <td class="py-4 text-sm text-slate-600">
                    <div class="flex items-center gap-1">
                    <svg class="w-4 h-4 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                    {{ tour.duracion }}h
                    </div>
                </td>
                <td class="py-4 text-sm font-medium text-slate-800">${{ parseInt(tour.precio).toLocaleString('es-CO')}}</td>
                <td class="py-4 text-sm text-slate-600">
                    <div class="flex items-center gap-1">
                    <svg class="w-4 h-4 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
                    {{ tour.capacidad }}
                    </div>
                </td>
                <td class="py-4 text-sm text-center font-bold text-emerald-700 bg-emerald-50/30 rounded-lg">
                    {{ tour.ventas_totales || 0 }}
                </td>
                <td class="py-4 text-sm text-slate-800">
                    <div class="flex items-center gap-1">
                    0
                    <svg class="w-4 h-4 text-amber-400 fill-amber-400" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
                    <span class="text-slate-500">(0)</span>
                    </div>
                </td>
                <td class="py-4">
                    <div class="flex items-center justify-center gap-2">
                    <button @click="emit('editar', tour)" class="p-1.5 text-slate-400 hover:text-emerald-600 hover:bg-emerald-50 rounded-lg transition-colors border border-transparent hover:border-emerald-200" title="Editar">
                        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                    </button>
                    <button @click="deleteTour(tour.id)" class="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors border border-transparent hover:border-red-200" title="Eliminar">
                        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                    </button>
                    </div>
                </td>
                </tr>
            </tbody>
            </table>
        </div>
    </section>
</template>