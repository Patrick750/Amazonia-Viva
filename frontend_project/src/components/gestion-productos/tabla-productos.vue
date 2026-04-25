<script setup>
import { ref, computed } from 'vue';

const props = defineProps(['datos', 'tipoCatalogo']);
const emit = defineEmits(['editar', 'eliminar', 'verDetalles']);

const estadoFiltro = ref('todos');

const filteredDatos = computed(() => {
    if (!props.datos) return [];
    
    return props.datos.filter(prod => {
        if (estadoFiltro.value === 'activo') return prod.disponible === true;
        if (estadoFiltro.value === 'inactivo') return prod.disponible === false;
        return true;
    });
});

// --- PAGINACIÓN ---
const currentPage = ref(1);
const itemsPerPage = 12;

const totalPages = computed(() => Math.ceil(filteredDatos.value.length / itemsPerPage));

const paginatedData = computed(() => {
    const start = (currentPage.value - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    return filteredDatos.value.slice(start, end);
});

const irPagina = (p) => {
    if (p < 1 || p > totalPages.value) return;
    currentPage.value = p;
    // Scroll suave al inicio de la tabla/sección
    window.scrollTo({ top: 0, behavior: 'smooth' });
};

const deleteProducto = (id) => {
    emit('eliminar', id);
};
</script>

<template>
  <section class="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 shadow-sm h-full">
    <div class="mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
           <h2 class="text-lg font-black text-white">Catálogo de {{ tipoCatalogo === 'turistas' ? 'Turistas' : 'Agencias' }}</h2>
           <p class="text-xs text-white/40 font-medium">{{ filteredDatos.length }} productos registrados</p>
        </div>
        <div class="flex items-center gap-3 bg-white/5 px-4 py-2 rounded-xl border border-white/5">
            <label for="filtro-estado" class="text-[10px] font-black text-white/30 uppercase tracking-widest">Filtrar:</label>
            <select id="filtro-estado" v-model="estadoFiltro" class="text-xs font-bold bg-transparent border-none text-emerald-400 focus:ring-0 py-0 pl-0 pr-8 cursor-pointer appearance-none">
                <option value="todos" class="bg-[#0d2114] text-white">Todos</option>
                <option value="activo" class="bg-[#0d2114] text-white">Activos</option>
                <option value="inactivo" class="bg-[#0d2114] text-white">Inactivos</option>
            </select>
            <svg class="w-3.5 h-3.5 text-emerald-500/50 -ml-6 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M19 9l-7 7-7-7"/></svg>
        </div>
    </div>

    <!-- VISTA MÓVIL (Tarjetas) -->
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 md:hidden">
        <div v-for="prod in paginatedData" :key="prod.id" class="bg-white/5 rounded-2xl shadow-sm border border-white/10 p-5 relative flex flex-col gap-4 transition-all hover:bg-white/8 hover:border-white/20 active:scale-[0.98]">
            
            <!-- Indicador de estado móvil -->
            <span class="absolute top-4 right-4 text-[9px] font-black px-2 py-0.5 rounded-full border uppercase tracking-widest"
              :class="prod.disponible ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-red-500/10 text-red-400 border-red-500/20'">
              {{ prod.disponible ? 'Activo' : 'Inactivo' }}
            </span>
            
            <div class="flex items-center gap-4 pr-16">
                <div class="w-16 h-16 rounded-xl overflow-hidden border border-white/10 shadow-xl bg-emerald-500/10 flex-shrink-0 cursor-pointer group" @click="emit('verDetalles', prod)">
                    <img v-if="prod.imagen_producto && prod.imagen_producto.length > 0" :src="prod.imagen_producto[0].url" :alt="prod.nombre" class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110" />
                    <svg v-else class="w-full h-full p-4 text-emerald-500/30" fill="none" stroke="currentColor" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>
                </div>
                <div>
                    <h3 class="font-black text-white text-sm leading-tight hover:text-emerald-400 line-clamp-2 cursor-pointer transition-colors" @click="emit('verDetalles', prod)">{{ prod.nombre }}</h3>
                    <div class="flex flex-wrap items-center gap-2 mt-2">
                        <span class="font-black text-[9px] bg-white/5 text-white/40 border border-white/5 px-1.5 py-0.5 rounded uppercase tracking-widest">{{ prod.sku }}</span>
                        <span class="text-[10px] font-bold text-emerald-500/70">{{ prod.nombre_categoria }}</span>
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-3 gap-3 text-[10px] bg-black/20 p-3 rounded-xl border border-white/5">
                <div class="flex flex-col gap-1">
                    <span class="text-[8px] uppercase text-white/20 font-black tracking-widest">Precio</span>
                    <span class="font-black text-white tabular-nums">${{ parseFloat(prod.precio).toLocaleString('es-CO') }}</span>
                </div>
                <div class="flex flex-col gap-1">
                    <span class="text-[8px] uppercase text-white/20 font-black tracking-widest">Stock</span>
                    <span :class="prod.stock < 5 ? 'text-rose-400' : 'text-emerald-400'" class="font-black tabular-nums">{{ prod.stock }}</span>
                </div>
                <div class="flex flex-col gap-1 items-end">
                    <span class="text-[8px] uppercase text-white/20 font-black tracking-widest">Ventas</span>
                    <span class="font-black text-white tabular-nums">{{ prod.ventas_totales || 0 }}</span>
                </div>
            </div>
            
            <div class="flex gap-2 mt-2 pt-4 border-t border-white/5">
                <button @click="emit('editar', prod)" class="flex-1 flex items-center justify-center gap-2 px-3 py-2.5 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all hover:bg-emerald-500/20 hover:text-emerald-300">
                    <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                    Editar
                </button>
                <button @click="deleteProducto(prod.id)" class="flex-1 flex items-center justify-center gap-2 px-3 py-2.5 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all hover:bg-rose-500/20 hover:text-rose-300">
                    <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                    Eliminar
                </button>
            </div>
        </div>
        
        <div v-if="filteredDatos.length === 0" class="text-center py-12 text-white/20 text-xs col-span-1 sm:col-span-2 bg-white/3 rounded-2xl border border-dashed border-white/5 font-bold italic">
            No hay productos registrados en este catálogo.
        </div>
    </div>

    <!-- VISTA ESCRITORIO (Tabla) -->
    <div class="hidden md:block overflow-x-auto custom-scroll">
        <table class="w-full text-left border-collapse min-w-[700px]">
        <thead>
            <tr class="text-[10px] font-black text-white/30 uppercase tracking-[0.2em] border-b border-white/5">
                <th class="pb-4 pl-2 w-1/3 text-left">Producto</th>
                <th class="pb-4 text-left">SKU</th>
                <th class="pb-4 text-left">Precio</th>
                <th class="pb-4 text-left">Stock</th>
                <th class="pb-4 text-center">Ventas</th>
                <th class="pb-4 text-center">Acciones</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="prod in paginatedData" :key="prod.id" class="border-b border-white/5 hover:bg-white/5 transition-all duration-200 group">
            <td class="py-5 pl-2">
                <div class="flex items-center gap-4">
                    <div class="relative flex-shrink-0">
                        <span 
                            class="absolute -top-1 -right-1 w-3 h-3 rounded-full border-2 border-[#0d2114] z-10 shadow-2xl transition-all"
                            :class="prod.disponible ? 'bg-emerald-500 shadow-emerald-500/50' : 'bg-red-500 shadow-red-500/50'"
                            :title="prod.disponible ? 'Activo' : 'Inactivo'"
                        ></span>
                        <div class="w-11 h-11 rounded-xl overflow-hidden border border-white/10 shadow-lg bg-white/5 flex items-center justify-center group-hover:border-emerald-500/30 transition-colors">
                            <img v-if="prod.imagen_producto && prod.imagen_producto.length > 0" :src="prod.imagen_producto[0].url" class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110">
                            <svg v-else class="w-5 h-5 text-white/10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>
                        </div>
                    </div>
                    <div class="min-w-0 flex-1">
                        <h3 class="font-black text-white text-sm cursor-pointer hover:text-emerald-400 transition-colors truncate" @click="emit('verDetalles', prod)">
                            {{ prod.nombre }}
                        </h3>
                        <div class="flex items-center gap-2 mt-1">
                            <span class="text-[10px] font-black text-emerald-500/60 uppercase tracking-widest">{{ prod.nombre_categoria || 'N/A' }}</span>
                            <span v-if="prod.marca || prod.modelo" class="text-[9px] font-bold text-white/20 uppercase tracking-tighter">
                                {{ [prod.marca, prod.modelo].filter(Boolean).join(' · ') }}
                            </span>
                        </div>
                    </div>
                </div>
            </td>
            <td class="py-5">
                <span class="text-[10px] font-black font-mono text-white/30 bg-white/5 px-2 py-0.5 rounded border border-white/5 uppercase">{{ prod.sku }}</span>
            </td>
            <td class="py-5 text-sm font-black text-white tabular-nums">
                ${{ parseFloat(prod.precio).toLocaleString('es-CO') }}
            </td>
            <td class="py-5">
                <div class="flex items-center gap-2">
                    <div class="w-1.5 h-1.5 rounded-full" :class="prod.stock < 5 ? 'bg-rose-500 animate-pulse' : 'bg-emerald-500'"></div>
                    <span class="text-sm font-black tabular-nums" :class="prod.stock < 5 ? 'text-rose-400' : 'text-white/70'">{{ prod.stock }}</span>
                </div>
            </td>
            <td class="py-5 text-center">
                <span class="inline-block px-3 py-1 bg-white/5 text-white text-xs font-black rounded-lg border border-white/5 tabular-nums">
                    {{ prod.ventas_totales || 0 }}
                </span>
            </td>
            <td class="py-5">
                <div class="flex items-center justify-center gap-1.5 opacity-40 group-hover:opacity-100 transition-opacity">
                    <button @click="emit('editar', prod)" class="p-2 text-white/50 hover:text-emerald-400 hover:bg-emerald-500/10 rounded-xl transition-all border border-transparent hover:border-emerald-500/20" title="Editar Producto">
                        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                    </button>
                    <button @click="deleteProducto(prod.id)" class="p-2 text-white/50 hover:text-rose-400 hover:bg-rose-500/10 rounded-xl transition-all border border-transparent hover:border-rose-500/20" title="Eliminar Producto">
                        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                    </button>
                </div>
            </td>
            </tr>
        </tbody>
        <tbody v-if="filteredDatos.length === 0">
            <tr>
                <td colspan="6" class="py-20 text-center">
                    <div class="w-16 h-16 mx-auto rounded-2xl bg-white/5 border border-white/5 flex items-center justify-center mb-4">
                        <svg class="w-8 h-8 text-white/10" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>
                    </div>
                    <p class="font-black text-white/30 uppercase tracking-widest text-xs">Sin productos en este catálogo</p>
                    <p class="text-[10px] mt-2 text-white/20 font-bold italic">Haz clic en "+ Nuevo Producto" para comenzar</p>
                </td>
            </tr>
        </tbody>
        </table>
    </div>

    <!-- PAGINACIÓN -->
    <div v-if="totalPages > 1" class="mt-8 flex flex-col sm:flex-row items-center justify-between gap-6 bg-white/5 p-5 rounded-2xl border border-white/5">
        <p class="text-[10px] font-black uppercase tracking-[0.2em] text-white/30">
            Página <span class="text-emerald-400">{{ currentPage }}</span> de {{ totalPages }} 
            <span class="mx-2 text-white/10">|</span> 
            {{ filteredDatos.length }} Total
        </p>
        
        <div class="flex items-center gap-2">
            <button 
                @click="irPagina(currentPage - 1)" 
                :disabled="currentPage === 1"
                class="w-9 h-9 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-white/40 hover:text-emerald-400 hover:bg-emerald-500/10 hover:border-emerald-500/30 transition-all disabled:opacity-20 disabled:cursor-not-allowed group"
            >
                <svg class="w-4 h-4 group-hover:-translate-x-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7"/></svg>
            </button>

            <div class="flex items-center gap-1.5">
                <button 
                    v-for="p in totalPages" :key="p"
                    @click="irPagina(p)"
                    :class="[
                        'w-9 h-9 rounded-xl text-[10px] font-black transition-all border',
                        currentPage === p 
                            ? 'bg-emerald-500 border-emerald-400 text-black shadow-[0_0_15px_rgba(16,185,129,0.3)]' 
                            : 'bg-white/5 border-white/10 text-white/40 hover:text-white hover:bg-white/10'
                    ]"
                >
                    {{ p }}
                </button>
            </div>

            <button 
                @click="irPagina(currentPage + 1)" 
                :disabled="currentPage === totalPages"
                class="w-9 h-9 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center text-white/40 hover:text-emerald-400 hover:bg-emerald-500/10 hover:border-emerald-500/30 transition-all disabled:opacity-20 disabled:cursor-not-allowed group"
            >
                <svg class="w-4 h-4 group-hover:translate-x-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7"/></svg>
            </button>
        </div>
    </div>
  </section>
</template>
