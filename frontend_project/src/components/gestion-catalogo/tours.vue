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

        <!-- VISTA MÓVIL (Tarjetas) -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 md:hidden">
            <div v-for="tour in datos" :key="tour.id" class="bg-white/80 rounded-xl shadow-sm border border-white/80 p-4 relative flex flex-col gap-3 transition-shadow hover:shadow-md">
                
                <!-- Indicador de estado móvil -->
                <span class="absolute top-3 right-3 text-[10px] font-bold px-2 py-0.5 rounded-full border border-white shadow-sm"
                  :class="tour.activo ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'">
                  {{ tour.activo ? 'Activo' : 'Inactivo' }}
                </span>
                
                <div class="flex items-center gap-3 pr-16">
                    <div class="w-14 h-14 rounded-lg overflow-hidden border border-white shadow-sm bg-emerald-100 flex-shrink-0 cursor-pointer" @click="emit('verDetalles', tour)">
                        <img v-if="tour.imagen_paquete && tour.imagen_paquete.length > 0" :src="tour.imagen_paquete.find(i => i.es_portada)?.url || tour.imagen_paquete[0].url" :alt="tour.nombre" class="w-full h-full object-cover" />
                        <div v-else class="w-full h-full flex items-center justify-center">
                            <svg class="w-6 h-6 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                        </div>
                    </div>
                    <div>
                        <h3 class="font-bold text-slate-800 text-sm leading-tight hover:text-emerald-600 line-clamp-2 cursor-pointer transition-colors" @click="emit('verDetalles', tour)">{{ tour.nombre }}</h3>
                        <div class="flex items-center gap-1 text-xs text-slate-500 mt-0.5">
                            <svg class="w-3 h-3 text-emerald-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
                            <span class="truncate max-w-[120px]">{{ tour.ubicacion }}</span>
                        </div>
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-2 text-[11px] font-medium text-slate-600 mt-1 bg-slate-50 p-2.5 rounded-lg border border-slate-100">
                    <div class="flex items-center gap-1.5">
                        <svg class="w-3.5 h-3.5 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                        {{ tour.duracion }}h
                    </div>
                    <div class="flex items-center gap-1.5">
                        <svg class="w-3.5 h-3.5 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
                        Capacidad: {{ tour.capacidad }}
                    </div>
                    <div class="flex items-center gap-1.5 font-bold text-slate-800">
                        <span class="text-emerald-600">$</span>{{ parseInt(tour.precio).toLocaleString('es-CO')}}
                    </div>
                    <div class="flex items-center gap-1.5 font-bold text-emerald-700">
                        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
                        {{ tour.ventas_totales || 0 }} Ventas
                    </div>
                </div>
                
                <div class="flex gap-2 mt-2 pt-2">
                    <button @click="emit('editar', tour)" class="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-emerald-50 border border-emerald-100 text-emerald-600 rounded-lg text-xs font-bold hover:bg-emerald-100 transition-colors">
                        <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                        Editar
                    </button>
                    <button @click="deleteTour(tour.id)" class="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 bg-red-50 border border-red-100 text-red-600 rounded-lg text-xs font-bold hover:bg-red-100 transition-colors">
                        <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                        Eliminar
                    </button>
                </div>
            </div>
            
            <div v-if="datos.length === 0" class="text-center py-8 text-slate-500 text-sm col-span-1 sm:col-span-2 bg-white/50 rounded-xl border border-dashed border-slate-300">
                No tienes paquetes turísticos registrados.
            </div>
        </div>

        <!-- VISTA ESCRITORIO (Tabla) -->
        <div class="hidden md:block overflow-x-auto bg-white rounded-xl shadow-sm border border-slate-100 mt-4">
            <table class="w-full text-left border-collapse min-w-[900px]">
                <thead>
                    <tr class="text-[11px] font-bold text-slate-400 uppercase tracking-wider border-b border-slate-100 bg-slate-50/50">
                        <th class="px-5 py-4 w-1/3">Tour</th>
                        <th class="px-5 py-4">Ubicación</th>
                        <th class="px-5 py-4">Duración</th>
                        <th class="px-5 py-4">Precio</th>
                        <th class="px-5 py-4">Capacidad</th>
                        <th class="px-5 py-4 text-center">Ventas</th>
                        <th class="px-5 py-4 text-center">Calificación</th>
                        <th class="px-5 py-4 text-center">Acciones</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-slate-100">
                    <tr v-for="tour in datos" :key="tour.id" class="hover:bg-slate-50/80 transition-colors group">
                        <!-- Columna: Tour -->
                        <td class="px-5 py-4">
                            <div class="flex items-center gap-4">
                                <div class="relative flex-shrink-0">
                                    <span 
                                        class="absolute -top-1 -right-1 w-3.5 h-3.5 rounded-full border-2 border-white z-10 shadow-sm transition-colors"
                                        :class="tour.activo ? 'bg-emerald-500' : 'bg-red-500'"
                                        :title="tour.activo ? 'Tour Activo' : 'Tour Inactivo'"
                                    ></span>
                                    <div class="w-14 h-14 rounded-xl overflow-hidden shadow-sm bg-slate-100 border border-slate-200">
                                        <img 
                                            v-if="tour.imagen_paquete && tour.imagen_paquete.length > 0"
                                            :src="tour.imagen_paquete.find(i => i.es_portada)?.url || tour.imagen_paquete[0].url" 
                                            :alt="tour.nombre"
                                            class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                                        />
                                        <div v-else class="w-full h-full flex items-center justify-center">
                                            <svg class="w-6 h-6 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                                        </div>
                                    </div>
                                </div>
                                <div>
                                    <h3 class="font-bold text-slate-800 text-sm hover:text-emerald-600 transition-colors cursor-pointer line-clamp-1" @click="emit('verDetalles', tour)">
                                        {{ tour.nombre }}
                                    </h3>
                                    <span class="text-[11px] font-semibold text-slate-400 uppercase tracking-widest mt-0.5 block">
                                        {{ tour.category }}
                                    </span>
                                </div>
                            </div>
                        </td>
                        
                        <!-- Columna: Ubicación -->
                        <td class="px-5 py-4 text-sm font-medium text-slate-600">
                            <div class="flex items-center gap-1.5">
                                <svg class="w-4 h-4 text-emerald-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
                                <span class="truncate max-w-[150px]" :title="tour.ubicacion">{{ tour.ubicacion }}</span>
                            </div>
                        </td>

                        <!-- Columna: Duración -->
                        <td class="px-5 py-4 text-sm font-medium text-slate-600">
                            <div class="flex items-center gap-1.5">
                                <svg class="w-4 h-4 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                                {{ tour.duracion }}h
                            </div>
                        </td>

                        <!-- Columna: Precio -->
                        <td class="px-5 py-4">
                            <span class="text-sm font-bold text-slate-800">
                                <span class="text-emerald-600 font-semibold">$</span>{{ parseInt(tour.precio).toLocaleString('es-CO') }}
                            </span>
                        </td>

                        <!-- Columna: Capacidad -->
                        <td class="px-5 py-4 text-sm font-medium text-slate-600">
                            <div class="flex items-center gap-1.5">
                                <svg class="w-4 h-4 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
                                {{ tour.capacidad }} pers.
                            </div>
                        </td>

                        <!-- Columna: Ventas (Arreglado el orden) -->
                        <td class="px-5 py-4">
                            <div class="mx-auto w-fit flex items-center justify-center gap-1.5 px-3 py-1 bg-emerald-50 border border-emerald-100 rounded-full">
                                <span class="text-xs font-bold text-emerald-700">{{ tour.ventas_totales || 0 }}</span>
                            </div>
                        </td>

                        <!-- Columna: Calificación (Arreglado el orden) -->
                        <td class="px-5 py-4 text-sm">
                            <div class="flex items-center justify-center gap-1">
                                <span class="font-bold text-slate-700">0</span>
                                <svg class="w-4 h-4 text-amber-400 fill-amber-400" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
                                <span class="text-xs text-slate-400 font-medium">(0)</span>
                            </div>
                        </td>

                        <!-- Columna: Acciones -->
                        <td class="px-5 py-4">
                            <div class="flex items-center justify-center gap-2">
                                <button @click="emit('editar', tour)" class="p-2 text-slate-400 hover:text-emerald-600 hover:bg-emerald-50 rounded-xl transition-all border border-transparent hover:border-emerald-200 shadow-sm hover:shadow" title="Editar">
                                    <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                                </button>
                                <button @click="deleteTour(tour.id)" class="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-xl transition-all border border-transparent hover:border-red-200 shadow-sm hover:shadow" title="Eliminar">
                                    <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                                </button>
                            </div>
                        </td>
                    </tr>

                    <!-- Estado vacío -->
                    <tr v-if="datos.length === 0">
                        <td colspan="8" class="py-16 text-center">
                            <div class="flex flex-col items-center justify-center text-slate-400">
                                <svg class="w-12 h-12 mb-3 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 12H4M20 12a8 8 0 11-16 0 8 8 0 0116 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 20V4"/></svg>
                                <p class="text-sm font-medium">No tienes paquetes turísticos registrados.</p>
                                <p class="text-xs mt-1 text-slate-400">Haz clic en "Nuevo Tour" para comenzar.</p>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </section>
</template>