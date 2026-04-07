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

const deleteProducto = (id) => {
    emit('eliminar', id);
};
</script>

<template>
  <section class="bg-white/65 backdrop-blur-xl border border-white/80 rounded-2xl p-6 shadow-sm h-full">
    <div class="mb-6 flex items-center justify-between">
        <div>
           <h2 class="text-lg font-semibold text-slate-800">Catálogo de {{ tipoCatalogo === 'turistas' ? 'Turistas' : 'Agencias' }}</h2>
           <p class="text-sm text-slate-500">{{ filteredDatos.length }} productos registrados en este catálogo</p>
        </div>
        <div class="flex items-center gap-3">
            <label for="filtro-estado" class="text-sm font-medium text-slate-600">Estado:</label>
            <select id="filtro-estado" v-model="estadoFiltro" class="text-sm border-slate-200 rounded-lg text-slate-600 focus:ring-emerald-500 focus:border-emerald-500 py-2 pl-3 pr-8 w-36 cursor-pointer bg-white">
                <option value="todos">Todos</option>
                <option value="activo">Activos</option>
                <option value="inactivo">Inactivos</option>
            </select>
        </div>
    </div>

    <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[700px]">
        <thead>
            <tr class="text-sm font-semibold text-slate-500 border-b border-white/80">
            <th class="pb-3 pl-2 w-1/3">Producto</th>
            <th class="pb-3">SKU</th>
            <th class="pb-3">Precio</th>
            <th class="pb-3">Stock</th>
            <th class="pb-3 text-center">Ventas</th>
            <th class="pb-3 text-center">Acciones</th>
            </tr>
        </thead>
        <tbody>
            <tr v-if="filteredDatos.length === 0">
                <td colspan="5" class="py-12 text-center text-slate-500 bg-white/40 rounded-xl border border-dashed border-white/80 w-full">
                    <p class="font-medium text-slate-600">No hay productos registrados en este catálogo.</p>
                    <p class="text-xs mt-1 text-slate-400">Haz clic en "+ Nuevo Producto" para añadir uno nuevo.</p>
                </td>
            </tr>
            <tr v-for="prod in filteredDatos" :key="prod.id" class="border-b border-white/40 hover:bg-emerald-50/50 transition-colors group">
            <td class="py-4 pl-2">
                <div class="flex items-center gap-3">
                <div class="relative flex-shrink-0">
                    <span 
                    class="absolute -top-1 -right-1 w-3 h-3 rounded-full border-2 border-white z-10 shadow-sm transition-colors"
                    :class="prod.disponible ? 'bg-emerald-500' : 'bg-red-500'"
                    :title="prod.disponible ? 'Activo' : 'Inactivo'"
                    ></span>
                    <div class="w-12 h-12 rounded-lg overflow-hidden border border-white shadow-sm bg-emerald-100 flex items-center justify-center">
                    <img v-if="prod.imagen_producto && prod.imagen_producto.length > 0" :src="prod.imagen_producto[0].url" class="w-full h-full object-cover">
                    <svg v-else class="w-6 h-6 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>
                    </div>
                </div>
                <div>
                    <h3 class="font-semibold text-slate-800 text-sm cursor-pointer hover:text-emerald-600 transition-all" @click="emit('verDetalles', prod)">
                        {{ prod.nombre }}
                        <span v-if="prod.marca || prod.modelo" class="text-slate-400 font-medium whitespace-nowrap"> - {{ [prod.marca, prod.modelo].filter(Boolean).join(' ') }}</span>
                    </h3>
                    <span class="text-xs text-slate-500">Cat: {{ prod.nombre_categoria || 'N/A' }}</span>
                </div>
                </div>
            </td>
            <td class="py-4 text-sm text-slate-600 font-mono">
                {{ prod.sku }}
            </td>
            <td class="py-4 text-sm font-medium text-slate-800">${{ parseFloat(prod.precio).toLocaleString('es-CO') }}</td>
            <td class="py-4 text-sm text-slate-600">
                <div class="flex items-center gap-1.5 min-w-[60px]">
                <svg class="w-4 h-4 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path></svg>
                <span :class="prod.stock < 5 ? 'text-rose-500 font-bold' : ''">{{ prod.stock }}</span>
                </div>
            </td>
            <td class="py-4 text-sm text-center font-bold text-teal-700 bg-teal-50/30 rounded-lg">
                {{ prod.ventas_totales || 0 }}
            </td>
            <td class="py-4">
                <div class="flex items-center justify-center gap-2">
                <button @click="emit('editar', prod)" class="p-1.5 text-slate-400 hover:text-emerald-600 hover:bg-emerald-50 rounded-lg transition-colors border border-transparent hover:border-emerald-200" title="Editar Producto">
                    <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                </button>
                <button @click="deleteProducto(prod.id)" class="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors border border-transparent hover:border-red-200" title="Eliminar Producto">
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
