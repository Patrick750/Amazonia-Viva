<script setup>
import { ref, computed, onMounted } from 'vue'

const props = defineProps({
  perfil: {
    type: Object,
    required: true
  },
  rolLabel: {
    type: String,
    default: 'Usuario'
  }
})

const portadaPreview = ref(null)
const cargandoPortada = ref(false)

const triggerPortadaInput = () => {
  const el = document.getElementById('input-portada')
  if(el) el.click()
}

const onPortadaSeleccionada = async (e) => {
  const file = e.target.files[0]
  if (!file) return

  // Previsualización local inmediata
  portadaPreview.value = URL.createObjectURL(file)
  cargandoPortada.value = true

  try {
    const formData = new FormData()
    formData.append('portada', file)

    const res = await clienteAxios.post('/api/perfil/foto/?tipo=portada', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    if (res.data.foto_url) {
      // Éxito: La imagen se guardó en Cloudinary
      console.log('Portada guardada:', res.data.foto_url)
    }
  } catch (err) {
    console.error('Error subiendo portada:', err)
    alert('No se pudo guardar la portada en el servidor.')
  } finally {
    cargandoPortada.value = false
  }
}

const categorias = ref(['Todos'])
const categoriaActiva = ref('Todos')

const filtroBusqueda = ref('')

const items = ref([])
const cargando = ref(true)

const formatearMoneda = (valor) => {
  if (!valor) return '$0'
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0
  }).format(valor)
}

import clienteAxios from '@/api/axios.js'

onMounted(async () => {
  try {
    const rol = (props.rolLabel || '').toLowerCase()
    let dataFetch = []
    
    // Fetch only the authenticated user's products/packages 
    // depending on their role context
    if (rol === 'agencia') {
      const res = await clienteAxios.get(`api/pack/?agencia_id=${props.perfil.id}`)
      dataFetch = res.data.map(p => {
        // Encontrar la imagen de portada o la primera disponible
        const imgObj = (p.imagen_paquete || []).find(img => img.es_portada) || (p.imagen_paquete || [])[0]
        return {
          id: p.id,
          tipo: 'tour',
          titulo: p.nombre,
          precio: formatearMoneda(p.precio),
          rating: p.rating || 0,
          ventas: p.ventas_totales || 0,
          img: imgObj ? imgObj.url : null,
          categoria: p.categoria_paquete_nombre || p.categoria_nombre || 'Tours Selváticos'
        }
      })
    } else if (rol === 'proveedor') {
      const res = await clienteAxios.get(`api/productos/?proveedor_id=${props.perfil.id}`)
      dataFetch = res.data.map(p => {
        // Encontrar la imagen de portada o la primera disponible
        const imgObj = (p.imagen_producto || []).find(img => img.es_portada) || (p.imagen_producto || [])[0]
        return {
          id: p.id,
          tipo: 'producto',
          titulo: p.nombre,
          precio: formatearMoneda(p.precio),
          rating: p.rating || 0,
          ventas: p.ventas_totales || 0,
          img: imgObj ? imgObj.url : null,
          categoria: p.nombre_categoria || 'Equipamiento'
        }
      })
    }
    
    items.value = dataFetch
    
    // Extraer categorias únicas reales del catálogo del usuario
    const catSpecs = new Set(dataFetch.map(i => i.categoria))
    categorias.value = ['Todos', ...Array.from(catSpecs)]
    
  } catch (err) {
    console.error('Error cargando catálogo público:', err)
  } finally {
    cargando.value = false
  }
})

const itemsFiltrados = computed(() => {
  let list = items.value

  if (categoriaActiva.value !== 'Todos') {
    list = list.filter(item => item.categoria === categoriaActiva.value)
  }

  if (filtroBusqueda.value) {
    const term = filtroBusqueda.value.toLowerCase()
    list = list.filter(item => item.titulo.toLowerCase().includes(term))
  }
  return list
})

const getIniciales = computed(() => {
  const n = (props.perfil.first_name || props.perfil.nombreEmpresa || '').charAt(0)
  const a = (props.perfil.last_name || '').charAt(0)
  return (n + a).toUpperCase() || '?'
})

const nombreCompleto = computed(() => {
  return props.perfil.nombre_agencia || 
         props.perfil.nombre_empresa || 
         props.perfil.nombreEmpresa || 
         `${props.perfil.first_name || ''} ${props.perfil.last_name || ''}`.trim() || 
         'Usuario'
})

const tagUsuario = computed(() => {
  return `@${nombreCompleto.value.toLowerCase().replace(/\s+/g, '')}`
})

</script>

<template>
  <div class="bg-white min-h-screen pb-20 font-sans selection:bg-emerald-200">
    <!-- BLOQUE 1: Header de Identidad Estilo Facebook Reimagined -->
    <header class="relative bg-white border-b border-slate-100">
      <!-- Portada (16:9) -->
      <div class="relative w-full aspect-[21/9] md:h-64 bg-slate-600 overflow-hidden">
        <!-- Imagen de Portada: Prioridad: 1. Preview local, 2. URL del backend, 3. Placeholder -->
        <img :src="portadaPreview || perfil.foto_portada_url || 'https://images.unsplash.com/photo-1516026672322-bc52d61a55d5?q=80&w=1200&auto=format&fit=crop'" 
             alt="Portada" 
             class="w-full h-full object-cover mix-blend-overlay opacity-80"
             :class="{ 'animate-pulse': cargandoPortada }">
             
        <!-- Loader Overlay -->
        <div v-if="cargandoPortada" class="absolute inset-0 bg-black/40 flex items-center justify-center z-20">
          <svg class="w-8 h-8 text-white animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>
             
        <div @click="triggerPortadaInput" class="absolute bottom-4 right-4 bg-black/60 hover:bg-black/80 backdrop-blur text-white text-[10px] uppercase font-bold px-3 py-1.5 rounded flex items-center gap-2 cursor-pointer transition-all border border-white/20 z-10">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
          Editar portada
        </div>
        
        <input id="input-portada" type="file" accept="image/*" class="hidden" @change="onPortadaSeleccionada">
        
        <div class="absolute top-4 right-4 animate-pulse bg-black/60 backdrop-blur text-white text-[9px] uppercase font-bold tracking-widest px-3 py-1.5 rounded-full flex items-center gap-2 border border-white/10 shadow-lg">
          <svg class="w-3 h-3 text-emerald-400" fill="currentColor" viewBox="0 0 20 20"><path d="M10 12a2 2 0 100-4 2 2 0 000 4z"/><path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd"/></svg>
          Modo Previsualización
        </div>
      </div>

      <!-- Área de Identidad (No overlapping icons) -->
      <div class="max-w-4xl mx-auto px-4 sm:px-8 relative">
        <!-- Avatar floting partially over cover -->
        <div class="relative -mt-12 sm:-mt-16 mb-4 inline-block">
          <div class="w-24 h-24 sm:w-32 sm:h-32 rounded-3xl border-4 border-white shadow-2xl bg-white flex items-center justify-center overflow-hidden">
            <img v-if="perfil.foto_url" :src="perfil.foto_url" class="w-full h-full object-cover">
            <span v-else class="text-3xl font-black text-slate-300">{{ getIniciales }}</span>
          </div>
        </div>

        <!-- Info Grid -->
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div>
            <h1 class="text-2xl sm:text-3xl font-black text-slate-800 tracking-tight flex items-center gap-2">
              {{ nombreCompleto }}
              <svg v-if="perfil.nit || perfil.rut" class="w-6 h-6 text-blue-500 fill-current" viewBox="0 0 24 24"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M9 12l2 2 4-4" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </h1>
            <p class="text-sm font-bold text-slate-400 mt-0.5">{{ tagUsuario }}</p>

            <!-- Redes Sociales -->
            <div v-if="perfil.informacion_contacto" class="flex gap-2.5 mt-3">
              <a v-if="perfil.informacion_contacto.facebook" 
                 :href="perfil.informacion_contacto.facebook" 
                 target="_blank"
                 class="w-7 h-7 bg-slate-50 hover:bg-blue-50 text-slate-400 hover:text-blue-600 rounded-lg flex items-center justify-center transition-all border border-slate-100"
                 title="Facebook">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
              </a>
              <a v-if="perfil.informacion_contacto.instagram" 
                 :href="perfil.informacion_contacto.instagram" 
                 target="_blank"
                 class="w-7 h-7 bg-slate-50 hover:bg-pink-50 text-slate-400 hover:text-pink-600 rounded-lg flex items-center justify-center transition-all border border-slate-100"
                 title="Instagram">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>
              </a>
              <a v-if="perfil.informacion_contacto.whatsapp" 
                 :href="'https://wa.me/' + perfil.informacion_contacto.whatsapp" 
                 target="_blank"
                 class="w-7 h-7 bg-slate-50 hover:bg-green-50 text-slate-400 hover:text-green-600 rounded-lg flex items-center justify-center transition-all border border-slate-100"
                 title="WhatsApp">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.067 2.877 1.215 3.076.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/></svg>
              </a>
            </div>
          </div>
          
          <div class="flex items-center gap-2">
            <button class="flex-1 md:flex-none px-8 py-2.5 bg-slate-900 text-white rounded-xl font-bold text-sm shadow-xl shadow-slate-900/20 active:scale-95 transition-all">
              Contactar
            </button>
          </div>
        </div>

        <p class="text-sm sm:text-base text-slate-600 leading-relaxed font-normal max-w-2xl mb-6">
          {{ perfil.descripcion || "Sin descripción disponible para este perfil comercial." }}
        </p>

        <!-- Metadata Bar Real -->
        <div class="flex flex-wrap items-center gap-x-6 gap-y-4 border-t border-slate-100 py-5">
          <div v-if="perfil.email" class="flex items-center gap-2.5 text-xs sm:text-sm text-slate-500 font-bold">
            <div class="w-8 h-8 rounded-full bg-slate-50 flex items-center justify-center text-slate-400">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>
            </div>
            {{ perfil.email }}
          </div>
          <div v-if="perfil.numero_telefonico" class="flex items-center gap-2.5 text-xs sm:text-sm text-slate-500 font-bold">
            <div class="w-8 h-8 rounded-full bg-slate-50 flex items-center justify-center text-slate-400">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/></svg>
            </div>
            {{ perfil.numero_telefonico }}
          </div>
          <div v-if="perfil.horario_atencion" class="flex items-center gap-2.5 text-xs sm:text-sm text-slate-500 font-bold">
            <div class="w-8 h-8 rounded-full bg-slate-50 flex items-center justify-center text-slate-400">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
            </div>
            {{ perfil.horario_atencion }}
          </div>
          <div v-if="perfil.nit || perfil.rut" class="flex items-center gap-2.5 text-xs sm:text-sm text-blue-600 font-bold">
            <div class="w-8 h-8 rounded-full bg-blue-50 flex items-center justify-center text-blue-500">
              <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>
            </div>
            Validado
          </div>
        </div>
      </div>
    </header>

    <!-- BLOQUE 2: Barra de Control y Búsqueda (Sticky) -->
    <div class="sticky top-0 z-30 bg-white/90 backdrop-blur-md border-b border-slate-100 pb-2 pt-2">
      <div class="px-4 flex items-center gap-3">
        <!-- Input Buscador Minimalista -->
        <div class="relative flex-1">
          <svg class="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
          <input 
            v-model="filtroBusqueda"
            type="text" 
            placeholder="Buscar en la tienda..."
            class="w-full bg-slate-100/80 border-transparent rounded-full py-2.5 pl-10 pr-4 text-sm font-medium text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 focus:bg-white transition-all shadow-inner"
          >
        </div>
        <!-- Botón Filtros Avanzados -->
        <button class="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center shrink-0 border border-slate-200">
          <svg class="w-4 h-4 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"/></svg>
        </button>
      </div>

      <!-- Fila de Chips (Overflow horizontal) -->
      <div class="mt-3 px-4 flex gap-2 overflow-x-auto scrollbar-none pb-1" style="-ms-overflow-style:none; scrollbar-width:none;">
        <button 
          v-for="cat in categorias" :key="cat"
          @click="categoriaActiva = cat"
          :class="[
            'px-4 py-1.5 rounded-full text-[11px] font-bold transition-all whitespace-nowrap border',
            categoriaActiva === cat
              ? 'bg-slate-900 border-slate-900 text-white shadow-md shadow-slate-900/10'
              : 'bg-white border-slate-200 text-slate-600 active:bg-slate-50'
          ]"
        >
          {{ cat }}
        </button>
      </div>
    </div>

    <!-- BLOQUE 3: Feed de Catálogo (Visual Grid) -->
    <main class="p-1 sm:p-4 max-w-4xl mx-auto">
      <div v-if="itemsFiltrados.length === 0" class="flex flex-col items-center justify-center py-20 text-center px-6">
        <div class="w-20 h-20 bg-slate-50 rounded-full flex items-center justify-center mb-4">
          <svg class="w-8 h-8 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/></svg>
        </div>
        <h3 class="text-sm font-bold text-slate-600">Catálogo vacío</h3>
        <p class="text-xs text-slate-400 mt-1 max-w-xs">No se encontraron productos o tours en este momento.</p>
      </div>

      <div v-else class="grid grid-cols-2 md:grid-cols-3 gap-1 sm:gap-4">
        <!-- ITEM CARD -->
        <article 
          v-for="item in itemsFiltrados" :key="item.id"
          class="relative bg-black rounded-lg sm:rounded-2xl overflow-hidden aspect-[3/4] group cursor-pointer"
        >
          <!-- Media (Imagen) -->
          <img v-if="item.img" :src="item.img" :alt="item.titulo" class="w-full h-full object-cover opacity-90 group-hover:scale-105 transition-transform duration-700">
          <div v-else class="w-full h-full bg-slate-800 flex items-center justify-center opacity-90 group-hover:scale-105 transition-transform duration-700">
            <svg class="w-8 h-8 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
          </div>
          
          <!-- Gradiente Overlay (Oscurecimiento inferior para el texto) -->
          <div class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-transparent pointer-events-none"></div>



          <!-- Badges Sup-Derecha (Icono Tipo) -->
          <div class="absolute top-2 right-2 sm:top-3 sm:right-3 w-6 h-6 rounded-full bg-black/40 backdrop-blur flex items-center justify-center">
            <svg v-if="item.tipo === 'tour'" class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064"/></svg>
            <svg v-else class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"/></svg>
          </div>

          <!-- Información Inferior (Absoluta) -->
          <div class="absolute bottom-0 left-0 w-full p-2.5 sm:p-4 pt-10 flex flex-col justify-end">
            <!-- Calificación y Ventas -->
            <div class="flex items-center gap-2 mb-1.5 flex-wrap">
              <div class="flex items-center gap-1 bg-white/20 backdrop-blur text-white text-[10px] sm:text-xs font-bold px-1.5 py-0.5 rounded shadow-sm w-max">
                <svg class="w-2.5 h-2.5 text-amber-400" fill="currentColor" viewBox="0 0 20 20"><path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/></svg>
                {{ Number(item.rating || 0).toFixed(1) }}
              </div>
              <div class="text-[9px] sm:text-[10px] font-bold text-slate-300 uppercase tracking-wider bg-black/40 px-1.5 py-0.5 rounded">
                {{ item.ventas || 0 }} vendidos
              </div>
            </div>
            
            <h3 class="text-white text-[11px] sm:text-sm font-bold leading-tight line-clamp-2 drop-shadow-sm mb-1.5 group-hover:text-amber-200 transition-colors">
              {{ item.titulo }}
            </h3>

            <div class="flex items-end justify-between mt-auto">
              <p class="text-amber-300 text-[13px] sm:text-base font-black drop-shadow tracking-tight">
                {{ item.precio }}
              </p>
            </div>
          </div>
        </article>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* Eliminar barra de scroll sutilmente en webkit */
.scrollbar-none::-webkit-scrollbar {
  display: none;
}
</style>
