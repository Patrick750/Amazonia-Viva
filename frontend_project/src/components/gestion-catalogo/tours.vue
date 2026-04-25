<script setup>

    import { ref, computed } from 'vue';

    const props = defineProps(['datos'])
    const emit = defineEmits(['editar', 'eliminar', 'verDetalles'])

    // --- PAGINACIÓN ---
    const currentPage = ref(1);
    const itemsPerPage = 12;

    const totalPages = computed(() => Math.ceil(props.datos.length / itemsPerPage));

    const paginatedData = computed(() => {
        const start = (currentPage.value - 1) * itemsPerPage;
        const end = start + itemsPerPage;
        return props.datos.slice(start, end);
    });

    const irPagina = (p) => {
        if (p < 1 || p > totalPages.value) return;
        currentPage.value = p;
        // Scroll suave al inicio de la tabla/sección
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const deleteTour = (id) => {
        emit('eliminar', id);
    };

</script>

<template>
    <section class="bg-white/5 backdrop-blur-xl border border-white/10 rounded-[2.5rem] p-8 shadow-2xl relative overflow-hidden">
        <!-- Decorative background glow -->
        <div class="absolute -top-24 -right-24 w-64 h-64 bg-emerald-500/10 blur-[100px] rounded-full pointer-events-none"></div>

        <div class="mb-10 flex items-center justify-between">
            <div>
                <h2 class="text-[11px] font-black text-white/20 uppercase tracking-[0.2em] mb-1">Inventario de Experiencias</h2>
                <div class="flex items-center gap-3">
                    <h3 class="text-2xl font-black text-white">Mis Tours</h3>
                    <span class="px-2.5 py-0.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] font-black uppercase tracking-widest">
                        {{ datos.length }} Total
                    </span>
                </div>
            </div>
        </div>

        <!-- VISTA MÓVIL (Tarjetas) -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-6 md:hidden">
            <div v-for="tour in paginatedData" :key="tour.id" class="bg-white/5 rounded-3xl border border-white/5 p-5 relative flex flex-col gap-4 transition-all hover:bg-white/10 hover:border-white/10 group">
                
                <!-- Indicador de estado móvil -->
                <span class="absolute top-4 right-4 text-[9px] font-black px-3 py-1 rounded-full uppercase tracking-widest shadow-xl"
                  :class="tour.activo ? 'bg-emerald-500 text-black' : 'bg-rose-500 text-white'">
                  {{ tour.activo ? 'Activo' : 'Inactivo' }}
                </span>
                
                <div class="flex items-center gap-4">
                    <div class="w-20 h-20 rounded-2xl overflow-hidden border border-white/10 shadow-2xl bg-white/5 flex-shrink-0 cursor-pointer group-hover:scale-105 transition-transform" @click="emit('verDetalles', tour)">
                        <img v-if="tour.imagen_paquete && tour.imagen_paquete.length > 0" :src="tour.imagen_paquete.find(i => i.es_portada)?.url || tour.imagen_paquete[0].url" :alt="tour.nombre" class="w-full h-full object-cover" />
                        <div v-else class="w-full h-full flex items-center justify-center">
                            <svg class="w-8 h-8 text-white/10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                        </div>
                    </div>
                    <div class="flex-1 min-w-0">
                        <h3 class="font-black text-white text-base leading-tight hover:text-emerald-400 transition-colors line-clamp-2 cursor-pointer mb-2" @click="emit('verDetalles', tour)">{{ tour.nombre }}</h3>
                        <div class="flex items-center gap-1.5 text-[10px] text-white/30 font-bold uppercase tracking-widest italic">
                            <svg class="w-3.5 h-3.5 text-emerald-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
                            <span class="truncate">{{ tour.ubicacion }}</span>
                        </div>
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-3 text-[10px] font-black uppercase tracking-widest text-white/40 mt-1 bg-black/20 p-4 rounded-2xl border border-white/5">
                    <div class="flex items-center gap-2">
                        <svg class="w-4 h-4 text-emerald-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                        {{ tour.duracion }}h
                    </div>
                    <div class="flex items-center gap-2">
                        <svg class="w-4 h-4 text-emerald-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle></svg>
                        Max: {{ tour.capacidad }}
                    </div>
                    <div class="flex items-center gap-1.5 font-black text-white text-sm col-span-2 mt-1 pt-3 border-t border-white/5">
                        <span class="text-emerald-500 text-[10px]">$</span>{{ parseInt(tour.precio).toLocaleString('es-CO')}}
                        <span class="text-[9px] text-white/20 font-black tracking-tighter">COP</span>
                    </div>
                </div>
                
                <div class="flex gap-3 mt-2">
                    <button @click="emit('editar', tour)" class="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-white/5 border border-white/5 text-white/60 rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-white/10 hover:text-white transition-all active:scale-95">
                        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                        Editar
                    </button>
                    <button @click="deleteTour(tour.id)" class="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-xl text-[10px] font-black uppercase tracking-widest hover:bg-rose-500 hover:text-white transition-all active:scale-95">
                        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                        Borrar
                    </button>
                </div>
            </div>
            
            <div v-if="datos.length === 0" class="flex flex-col items-center justify-center py-16 px-6 text-center bg-white/5 rounded-[2.5rem] border-2 border-dashed border-white/5">
                <div class="w-16 h-16 rounded-3xl bg-white/5 flex items-center justify-center mb-4">
                    <svg class="w-8 h-8 text-white/10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 4v16m8-8H4"/></svg>
                </div>
                <p class="text-white/40 font-black text-xs uppercase tracking-widest">Sin paquetes registrados</p>
                <p class="text-[10px] text-white/20 mt-2 font-bold italic">Crea tu primer tour para comenzar a vender</p>
            </div>
        </div>

        <!-- VISTA ESCRITORIO (Tabla) -->
        <div class="hidden md:block overflow-x-auto bg-white/5 rounded-[2rem] border border-white/5 mt-6 shadow-3xl">
            <table class="w-full text-left border-collapse min-w-[900px]">
                <thead>
                    <tr class="text-[10px] font-black text-white/20 uppercase tracking-[0.2em] border-b border-white/5 bg-white/5">
                        <th class="px-4 py-4 w-1/3">Experiencia</th>
                        <th class="px-4 py-4">Ubicación</th>
                        <th class="px-4 py-4">Duración</th>
                        <th class="px-4 py-4">Valor</th>
                        <th class="px-4 py-4">Cupos</th>
                        <th class="px-4 py-4 text-center">Gestión</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-white/5 text-white">
                    <tr v-for="tour in paginatedData" :key="tour.id" class="hover:bg-white/5 transition-all group">
                        <!-- Columna: Tour -->
                        <td class="px-4 py-4">
                            <div class="flex items-center gap-5">
                                <div class="relative flex-shrink-0 group-hover:scale-110 transition-transform duration-500">
                                    <div class="w-16 h-16 rounded-2xl overflow-hidden shadow-2xl bg-white/10 border border-white/10">
                                        <img 
                                            v-if="tour.imagen_paquete && tour.imagen_paquete.length > 0"
                                            :src="tour.imagen_paquete.find(i => i.es_portada)?.url || tour.imagen_paquete[0].url" 
                                            :alt="tour.nombre"
                                            class="w-full h-full object-cover group-hover:scale-110 transition-all duration-700"
                                        />
                                        <div v-else class="w-full h-full flex items-center justify-center">
                                            <svg class="w-7 h-7 text-white/5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                                        </div>
                                    </div>
                                    <span 
                                        class="absolute -top-1 -right-1 w-4 h-4 rounded-full border-2 border-[#0a1a0f] z-10 shadow-2xl animate-pulse"
                                        :class="tour.activo ? 'bg-emerald-500' : 'bg-rose-500'"
                                    ></span>
                                </div>
                                <div class="min-w-0">
                                    <h3 class="font-black text-white text-sm hover:text-emerald-400 transition-colors cursor-pointer line-clamp-1 mb-1" @click="emit('verDetalles', tour)">
                                        {{ tour.nombre }}
                                    </h3>
                                    <div class="flex items-center gap-2">
                                        <span class="text-[9px] font-black text-emerald-500 bg-emerald-500/10 px-2 py-0.5 rounded uppercase tracking-widest">
                                            {{ tour.category || 'Experiencia' }}
                                        </span>
                                        <span class="text-[9px] font-black text-white/20 uppercase tracking-widest italic">
                                            {{ tour.reservas_totales || 0 }} Reservas
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </td>
                        
                        <!-- Columna: Ubicación -->
                        <td class="px-4 py-4">
                            <div class="flex items-center gap-2 text-white/40 text-xs font-bold font-mono">
                                <svg class="w-4 h-4 text-emerald-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
                                <span class="truncate max-w-[150px] italic" :title="tour.ubicacion">{{ tour.ubicacion }}</span>
                            </div>
                        </td>

                        <!-- Columna: Duración -->
                        <td class="px-4 py-4">
                            <div class="flex items-center gap-2.5 text-white/60 font-black text-xs">
                                <div class="w-8 h-8 rounded-xl bg-white/5 flex items-center justify-center border border-white/5">
                                    <svg class="w-4 h-4 text-emerald-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                                </div>
                                {{ tour.duracion }}h
                            </div>
                        </td>

                        <!-- Columna: Precio -->
                        <td class="px-4 py-4">
                            <div class="flex flex-col">
                                <div class="text-sm font-black text-white tabular-nums">
                                    <span class="text-emerald-500 text-[10px]">$</span>{{ parseInt(tour.precio).toLocaleString('es-CO') }}
                                </div>
                                <span class="text-[8px] font-black text-white/20 uppercase tracking-widest">Valor Unitario</span>
                            </div>
                        </td>

                        <!-- Columna: Cupos -->
                        <td class="px-4 py-4">
                            <div class="flex items-center gap-3">
                                <div class="w-10 h-10 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 shrink-0">
                                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/></svg>
                                </div>
                                <div class="flex flex-col">
                                    <span class="text-xs font-black text-white" :class="tour.cupos_disponibles <= 5 ? 'text-rose-400' : 'text-emerald-400'">
                                        {{ tour.cupos_disponibles ?? tour.capacidad }} / {{ tour.capacidad }}
                                    </span>
                                    <span class="text-[8px] font-black text-white/20 uppercase tracking-widest">Cupos Libres</span>
                                </div>
                            </div>
                        </td>

                        <!-- Columna: Acciones -->
                        <td class="px-4 py-4 text-center">
                            <div class="flex items-center justify-center gap-3">
                                <button @click="emit('editar', tour)" class="w-10 h-10 rounded-2xl bg-white/5 border border-white/10 text-white/40 hover:text-emerald-400 hover:bg-emerald-500/10 hover:border-emerald-500/30 transition-all flex items-center justify-center group/btn" title="Editar">
                                    <svg class="w-4 h-4 group-hover/btn:scale-110 transition-transform" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                                </button>
                                <button @click="deleteTour(tour.id)" class="w-10 h-10 rounded-2xl bg-white/5 border border-white/10 text-white/40 hover:text-rose-400 hover:bg-rose-500/10 hover:border-rose-500/30 transition-all flex items-center justify-center group/btn" title="Eliminar">
                                    <svg class="w-4 h-4 group-hover/btn:scale-110 transition-transform" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                                </button>
                            </div>
                        </td>
                    </tr>

                    <!-- Estado vacío -->
                    <tr v-if="datos.length === 0">
                        <td colspan="6" class="py-24 text-center">
                            <div class="w-20 h-20 mx-auto rounded-3xl bg-white/5 border border-white/5 flex items-center justify-center mb-6">
                                <svg class="w-10 h-10 text-white/5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5"><path stroke-linecap="round" stroke-linejoin="round" d="M20 12H4M20 12a8 8 0 11-16 0 8 8 0 0116 0z"/><path stroke-linecap="round" stroke-linejoin="round" d="M12 20V4"/></svg>
                            </div>
                            <p class="font-black text-white/20 uppercase tracking-[0.3em] text-[11px]">Inventario Vacío</p>
                            <p class="text-[10px] mt-2 text-white/10 font-bold italic">Haz clic en "+ Nuevo Tour" para registrar tu primera experiencia.</p>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- PAGINACIÓN -->
        <div v-if="totalPages > 1" class="mt-10 flex flex-col sm:flex-row items-center justify-between gap-6 bg-white/5 p-6 rounded-[2rem] border border-white/5">
            <p class="text-[10px] font-black uppercase tracking-[0.2em] text-white/30">
                Página <span class="text-emerald-400">{{ currentPage }}</span> de {{ totalPages }} 
                <span class="mx-2 text-white/10">|</span> 
                {{ datos.length }} Total
            </p>
            
            <div class="flex items-center gap-2">
                <button 
                    @click="irPagina(currentPage - 1)" 
                    :disabled="currentPage === 1"
                    class="w-10 h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-white/40 hover:text-emerald-400 hover:bg-emerald-500/10 hover:border-emerald-500/30 transition-all disabled:opacity-20 disabled:cursor-not-allowed group"
                >
                    <svg class="w-5 h-5 group-hover:-translate-x-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7"/></svg>
                </button>

                <div class="flex items-center gap-1.5">
                    <button 
                        v-for="p in totalPages" :key="p"
                        @click="irPagina(p)"
                        :class="[
                            'w-10 h-10 rounded-xl text-[11px] font-black transition-all border',
                            currentPage === p 
                                ? 'bg-emerald-500 border-emerald-400 text-black shadow-[0_0_20px_rgba(16,185,129,0.3)]' 
                                : 'bg-white/5 border-white/10 text-white/40 hover:text-white hover:bg-white/10'
                        ]"
                    >
                        {{ p }}
                    </button>
                </div>

                <button 
                    @click="irPagina(currentPage + 1)" 
                    :disabled="currentPage === totalPages"
                    class="w-10 h-10 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-white/40 hover:text-emerald-400 hover:bg-emerald-500/10 hover:border-emerald-500/30 transition-all disabled:opacity-20 disabled:cursor-not-allowed group"
                >
                    <svg class="w-5 h-5 group-hover:translate-x-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7"/></svg>
                </button>
            </div>
        </div>
    </section>
</template>