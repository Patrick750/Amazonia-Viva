<script setup>
import { computed, onMounted, ref } from 'vue'
import clienteAxios from '@/api/axios'

// Lo que la agencia (paquetes) o el proveedor (productos) tiene publicado, incluido lo que está inactivo o agotado,
// que el catálogo público no muestra. Administrar, crear o editar se hace en el panel correspondiente.
const props = defineProps({
  rol: { type: String, required: true }, // 'agencia' | 'proveedor'
})

const esAgencia = computed(() => props.rol.toLowerCase() === 'agencia')
const cargando = ref(true)
const error = ref('')
const items = ref([])

const moneda = (valor) => new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(Number(valor) || 0)

const filas = computed(() => items.value.map((item) => (esAgencia.value
  ? {
    id: item.id,
    nombre: item.nombre,
    precio: item.precio,
    activo: !!item.activo,
    estado: item.activo ? 'Activo' : 'Inactivo',
    detalle: [item.ubicacion, `${item.reservas_totales ?? 0} reservas`].filter(Boolean).join(' · '),
  }
  : {
    id: item.id,
    nombre: item.nombre,
    precio: item.precio,
    activo: !!item.disponible && item.stock > 0,
    estado: !item.disponible ? 'No disponible' : (item.stock > 0 ? 'Disponible' : 'Agotado'),
    detalle: `${item.stock ?? 0} en stock`,
  })))

const resumen = computed(() => {
  const activos = filas.value.filter(fila => fila.activo).length
  return `${filas.value.length} ${esAgencia.value ? 'paquetes' : 'productos'} · ${activos} ${esAgencia.value ? 'activos' : 'disponibles'}`
})

onMounted(async () => {
  try {
    const { data } = await clienteAxios.get(esAgencia.value ? 'api/pack/' : 'api/productos/')
    items.value = Array.isArray(data) ? data : (data.results || [])
  } catch {
    error.value = `No pudimos cargar tus ${esAgencia.value ? 'paquetes' : 'productos'}. Revisa tu conexión e inténtalo de nuevo.`
  } finally {
    cargando.value = false
  }
})
</script>

<template>
  <section class="overflow-hidden rounded-3xl border border-slate-200 bg-white shadow-sm" aria-labelledby="titulo-catalogo">
    <div class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 px-6 pb-4 pt-6 sm:px-8">
      <div>
        <h2 id="titulo-catalogo" class="text-lg font-extrabold text-slate-800">{{ esAgencia ? 'Mis paquetes' : 'Mis productos' }}</h2>
        <p v-if="!cargando && !error" class="mt-0.5 text-sm text-slate-500">{{ resumen }}</p>
      </div>
      <router-link :to="esAgencia ? '/panel/gestion-paquetes' : '/panel/productos'" class="inline-flex min-h-11 items-center rounded-2xl bg-slate-900 px-5 text-sm font-bold text-white outline-none hover:bg-slate-800 focus-visible:ring-2 focus-visible:ring-emerald-500">
        {{ esAgencia ? 'Administrar paquetes' : 'Administrar productos' }}
      </router-link>
    </div>

    <p v-if="cargando" class="p-8 text-sm text-slate-500" role="status">Cargando…</p>
    <p v-else-if="error" class="m-6 rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700" role="alert">{{ error }}</p>
    <div v-else-if="!filas.length" class="px-6 py-14 text-center">
      <p class="text-sm font-bold text-slate-600">Aún no tienes {{ esAgencia ? 'paquetes' : 'productos' }}.</p>
      <p class="mt-1 text-xs text-slate-400">Créalos desde el panel de administración.</p>
    </div>
    <ul v-else class="divide-y divide-slate-100">
      <li v-for="fila in filas" :key="fila.id" class="flex items-center justify-between gap-4 px-6 py-4 sm:px-8">
        <div class="min-w-0">
          <p class="truncate text-sm font-bold text-slate-800">{{ fila.nombre }}</p>
          <p class="mt-0.5 truncate text-xs text-slate-400">{{ fila.detalle }}</p>
        </div>
        <div class="flex shrink-0 flex-col items-end gap-1">
          <span class="text-sm font-black text-slate-800">{{ moneda(fila.precio) }}</span>
          <span class="rounded-full px-2.5 py-0.5 text-[11px] font-bold" :class="fila.activo ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-500'">{{ fila.estado }}</span>
        </div>
      </li>
    </ul>
  </section>
</template>
