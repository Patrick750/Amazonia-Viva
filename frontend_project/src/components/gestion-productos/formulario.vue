<script setup>
import { ref, watch, defineProps, defineEmits, computed, onMounted } from 'vue';
import axios from '@/api/axios';
import { useNotificacion } from '@/composables/useNotificacion';

const { mostrarNotificacion } = useNotificacion();

const API_URL = 'api/productos/';

const props = defineProps({
  abrir: {
      type: Boolean,
      default: false
  },
  producto: {
      type: Object,
      default: null
  },
  tipoCatalogo: {
    type: String,
    required: true
  }
});

const emit = defineEmits(['cerrar', 'guardadoExitoso']);

const isLoading = ref(false);
const isDragging = ref(false);
const fileInput = ref(null);

const inicialForm = {
  nombre: '',
  sku: '',
  stock: 0,
  precio: 0.00,
  disponible: true,
  categorias: '',
  caracteristicas: [ { clave: '', valor: '' } ],
  imagenes: []
};

const categoriasLista = ref([]);

const cargarCategorias = async () => {
    try {
        const res = await axios.get('api/categorias-productos/');
        categoriasLista.value = res.data;
    } catch (error) {
        console.error('Error cargando categorías:', error);
        mostrarNotificacion('Error al cargar las categorías del servidor.', 'error');
    }
};

onMounted(() => {
    cargarCategorias();
});

const atributosGenerales = [
    'Color', 'Talla', 'Material', 'Peso', 'Dimensiones', 'Capacidad', 'Marca'
];

const atributosPredefinidos = computed(() => {
    const cat = categoriasLista.value.find(c => c.id === form.value.categorias);
    if (cat && cat.caracteristicas && cat.caracteristicas.default_attributes) {
        return cat.caracteristicas.default_attributes;
    }
    return atributosGenerales;
});

const form = ref(JSON.parse(JSON.stringify(inicialForm)));

watch(() => form.value.categorias, (nuevaCat, viejaCat) => {
    if (viejaCat !== undefined && viejaCat !== '' && nuevaCat !== viejaCat) {
        const catObj = categoriasLista.value.find(c => c.id === nuevaCat);
        if (catObj && catObj.caracteristicas && catObj.caracteristicas.default_attributes) {
            form.value.caracteristicas = catObj.caracteristicas.default_attributes.map(attr => ({ clave: attr, valor: '' }));
        } else {
            form.value.caracteristicas = [{ clave: '', valor: '' }];
        }
    }
});

watch(() => props.producto, (prodActual) => {
    if (prodActual) {
        form.value = JSON.parse(JSON.stringify(prodActual));
        if(!form.value.caracteristicas || form.value.caracteristicas.length === 0) {
            form.value.caracteristicas = [{ clave: '', valor: '' }];
        }
        form.value.imagenes = prodActual.imagen_producto ? [...prodActual.imagen_producto] : [];
    } else {
        form.value = JSON.parse(JSON.stringify(inicialForm));
    }
}, { immediate: true });

const validarFormulario = () => {
    if (!form.value.nombre || form.value.nombre.trim().length < 3) {
        mostrarNotificacion('El nombre debe tener al menos 3 caracteres.', 'error');
        return false;
    }
    if (!form.value.sku || form.value.sku.trim().length < 2) {
        mostrarNotificacion('El SKU/Código es obligatorio.', 'error');
        return false;
    }
    if (!form.value.precio || form.value.precio <= 0) {
        mostrarNotificacion('El precio debe ser superior a $0 COP.', 'error');
        return false;
    }
    if (form.value.stock === '' || form.value.stock === null || form.value.stock < 0) {
        mostrarNotificacion('El stock inicial no puede ser negativo.', 'error');
        return false;
    }
    if (!form.value.categorias) {
        mostrarNotificacion('Debes clasificar el producto en una Categoría.', 'error');
        return false;
    }
    
    // Validación estructural de atributos clave/valor
    if (form.value.caracteristicas && form.value.caracteristicas.length > 0) {
        const filaVacia = form.value.caracteristicas.find(c => !c.clave.trim() || !c.valor.trim());
        if (filaVacia) {
            mostrarNotificacion('Completa los Atributos Extra o elimina la fila vacía.', 'error');
            return false;
        }
    }

    // Validación multimedia obligatoria
    if (!form.value.imagenes || form.value.imagenes.length === 0) {
        mostrarNotificacion('Debes adjuntar al menos 1 fotografía del producto.', 'warning');
        return false;
    }

    return true;
};

const guardarProducto = async () => {
    if (!validarFormulario()) return;
    
    isLoading.value = true;
    try {
        const formData = new FormData();
        formData.append('nombre', form.value.nombre);
        formData.append('sku', form.value.sku);
        formData.append('stock', form.value.stock);
        formData.append('precio', form.value.precio);
        formData.append('disponible', form.value.disponible);
        formData.append('categorias', form.value.categorias);
        formData.append('tipo_catalogo', props.tipoCatalogo);
        
        formData.append('caracteristicas', JSON.stringify(form.value.caracteristicas));

        const newImages = form.value.imagenes.filter(img => img.file);
        newImages.forEach(img => {
            formData.append('archivos_subidos', img.file);
        });

        if (props.producto && props.producto.id) {
            const oldImageIds = (props.producto.imagen_producto || []).map(i => i.id);
            const currentImageIds = form.value.imagenes.filter(i => !i.file).map(i => i.id);
            const deletedIds = oldImageIds.filter(id => !currentImageIds.includes(id));
            
            deletedIds.forEach(id => {
                formData.append('imagenes_eliminar', id);
            });

            await axios.put(`${API_URL}${props.producto.id}/`, formData);
        } else {
            await axios.post(API_URL, formData);
        }

        mostrarNotificacion(`Producto ${props.producto ? 'actualizado' : 'registrado'} con éxito`, 'exito');
        emit('guardadoExitoso');
    } catch (error) {
        console.error('Error guardando el producto:', error);
        let errorMsg = 'Hubo un error al guardar el producto.';
        if (error.response && error.response.data) {
             if (error.response.data.detail) errorMsg = error.response.data.detail;
             else if (error.response.data.errores) errorMsg += ' ' + JSON.stringify(error.response.data.errores);
        }
        mostrarNotificacion(errorMsg, 'error');
    } finally {
        isLoading.value = false;
    }
};

const limpiarFormularioYcerrar = () => {
    form.value = JSON.parse(JSON.stringify(inicialForm));
    emit('cerrar');
};

const agregarCaracteristica = () => {
    form.value.caracteristicas.push({ clave: '', valor: '' });
};

const eliminarCaracteristica = (index) => {
    form.value.caracteristicas.splice(index, 1);
};

// --- IMÁGENES D&D ---
const handleDrop = (e) => {
    isDragging.value = false;
    if (e.dataTransfer.files) procesarArchivos(e.dataTransfer.files);
};
const procesarArchivos = (archivos) => {
    if(!Array.isArray(form.value.imagenes)) form.value.imagenes = form.value.imagenes ? [form.value.imagenes] : [];
    Array.from(archivos).filter(f => f.type.startsWith('image/')).forEach(file => {
        form.value.imagenes.push({ file, url: URL.createObjectURL(file), name: file.name });
    });
};
const handleSelect = (event) => {
    if (event.target.files) procesarArchivos(event.target.files);
};
const removeImage = (index) => {
    if (form.value.imagenes[index].url && form.value.imagenes[index].url.startsWith('blob:')) {
        URL.revokeObjectURL(form.value.imagenes[index].url);
    }
    form.value.imagenes.splice(index, 1);
};
</script>

<template>
  <Teleport to="body">
    <div v-if="abrir"
      class="fixed inset-0 z-[60] flex items-center justify-center p-4"
      @click.self="limpiarFormularioYcerrar">

      <div class="absolute inset-0 bg-black/80 backdrop-blur-md"></div>

      <div class="relative bg-[#0d2114] border border-white/10 rounded-[2.5rem] shadow-2xl w-full max-w-3xl max-h-[92vh] flex flex-col overflow-hidden animate-fade-in-up">
        
        <!-- HEADER -->
        <div class="bg-gradient-to-br from-emerald-600 to-emerald-900 px-7 sm:px-9 py-6 sm:py-8 flex-shrink-0 relative overflow-hidden">
          <div class="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/leaf.png')] opacity-10"></div>
          <div class="relative z-10 flex items-start justify-between gap-4">
            <div>
              <div class="flex items-center gap-2 mb-3">
                <span class="inline-flex items-center gap-1.5 text-[10px] font-black tracking-[0.2em] uppercase text-emerald-200/70">
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15"/></svg>
                  {{ producto ? 'Editando Producto' : 'Nuevo Producto' }}
                </span>
                <span class="text-[9px] bg-emerald-500 text-black px-2.5 py-0.5 rounded-full uppercase tracking-wider font-black shadow-lg shadow-emerald-900/50">
                    Catálogo: {{ tipoCatalogo }}
                </span>
              </div>
              <h2 class="text-3xl font-black text-white leading-tight">
                {{ producto ? producto.nombre : 'Configurar Producto' }}
              </h2>
              <p class="text-emerald-100/60 text-sm mt-1.5 font-medium italic">
                {{ producto ? 'Actualiza los datos del inventario' : 'Ingresa los datos para registrar un nuevo producto' }}
              </p>
            </div>
            <button @click="limpiarFormularioYcerrar"
              class="flex-shrink-0 w-11 h-11 flex items-center justify-center rounded-2xl bg-white/10 hover:bg-white/20 text-white transition-all hover:rotate-90 duration-300 border border-white/5">
              <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
        </div>

        <div v-if="isLoading"
          class="absolute inset-0 bg-[#0d2114]/90 backdrop-blur-md z-20 flex flex-col items-center justify-center rounded-[2.5rem]">
          <div class="w-16 h-16 border-4 border-emerald-500/10 border-t-emerald-500 rounded-full animate-spin mb-6"></div>
          <p class="text-white font-black text-xl tracking-tight">{{ producto ? 'Actualizando...' : 'Guardando producto...' }}</p>
          <p class="text-emerald-500/50 text-sm mt-2 font-medium">Esto tomará solo un momento</p>
        </div>

        <!-- FORM BODY -->
        <div class="overflow-y-auto flex-1 custom-scroll bg-[#0a1a0f]">
            <form id="productForm" @submit.prevent="guardarProducto" class="p-7 sm:p-9 space-y-8 sm:space-y-10">
                
                <section>
                    <div class="flex items-center gap-4 mb-8">
                        <div class="w-10 h-10 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm font-black flex items-center justify-center shadow-lg shadow-emerald-500/5 flex-shrink-0">1</div>
                        <h3 class="text-xs font-black text-white/40 uppercase tracking-[0.2em]">Detalles Generales</h3>
                        <div class="flex-1 h-px bg-gradient-to-r from-white/10 to-transparent"></div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-7">
                        <div class="space-y-2 md:col-span-2">
                            <label class="block text-[10px] font-black text-white/30 uppercase tracking-[0.15em] mb-2 px-1">Nombre del Producto <span class="text-emerald-500">*</span></label>
                            <input v-model="form.nombre" type="text" required placeholder="Artesanía tallada, Tour fotográfico..." class="w-full bg-white/5 border border-white/10 rounded-2xl px-6 py-4 text-white font-bold focus:outline-none focus:bg-white/10 transition-all placeholder:text-white/10 focus:border-emerald-500/50">
                        </div>
                        
                        <div class="space-y-2">
                            <label class="block text-[10px] font-black text-white/30 uppercase tracking-[0.15em] mb-2 px-1">SKU / Código <span class="text-emerald-500">*</span></label>
                            <input v-model="form.sku" type="text" required placeholder="AMZ-PRD-001" class="w-full bg-white/5 border border-white/10 rounded-2xl px-6 py-4 text-white font-bold font-mono focus:outline-none focus:bg-white/10 transition-all placeholder:text-white/10 focus:border-emerald-500/50 uppercase tracking-widest">
                        </div>

                        <div class="space-y-2">
                            <label class="block text-[10px] font-black text-white/30 uppercase tracking-[0.15em] mb-2 px-1">Precio (COP) <span class="text-emerald-500">*</span></label>
                            <div class="relative">
                                <span class="absolute left-6 top-1/2 -translate-y-1/2 text-white/20 font-black text-lg">$</span>
                                <input v-model.number="form.precio" type="number" step="100" required placeholder="45000" class="w-full bg-white/5 border border-white/10 rounded-2xl pl-12 pr-6 py-4 text-white font-black tabular-nums focus:outline-none focus:bg-white/10 transition-all placeholder:text-white/10 focus:border-emerald-500/50 text-xl">
                            </div>
                        </div>

                        <div class="space-y-2">
                            <label class="block text-[10px] font-black text-white/30 uppercase tracking-[0.15em] mb-2 px-1">Stock Inicial <span class="text-emerald-500">*</span></label>
                            <input v-model.number="form.stock" type="number" min="0" required class="w-full bg-white/5 border border-white/10 rounded-2xl px-6 py-4 text-white font-black tabular-nums focus:outline-none focus:bg-white/10 transition-all placeholder:text-white/10 focus:border-emerald-500/50 text-xl text-center">
                        </div>

                        <div class="space-y-2 relative">
                            <label class="block text-[10px] font-black text-white/30 uppercase tracking-[0.15em] mb-2 px-1">Categoría <span class="text-emerald-500">*</span></label>
                            <select v-model="form.categorias" required class="w-full bg-white/5 border border-white/10 rounded-2xl px-6 py-4 pr-12 text-white font-bold focus:outline-none focus:bg-white/10 transition-all focus:border-emerald-500/50 appearance-none cursor-pointer">
                                <option value="" disabled class="bg-[#0d2114]">Selecciona una categoría...</option>
                                <option v-for="cat in categoriasLista" :key="cat.id" :value="cat.id" class="bg-[#0d2114]">{{ cat.nombre }}</option>
                            </select>
                            <div class="pointer-events-none absolute bottom-4.5 right-5 flex items-center text-emerald-500/50">
                              <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"></path></svg>
                            </div>
                        </div>
                    </div>
                </section>

                <section>
                    <div class="flex items-center gap-4 mb-8">
                        <div class="w-10 h-10 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm font-black flex items-center justify-center shadow-lg shadow-emerald-500/5 flex-shrink-0">2</div>
                        <h3 class="text-xs font-black text-white/40 uppercase tracking-[0.2em]">Multimedia & Estado</h3>
                        <div class="flex-1 h-px bg-gradient-to-r from-white/10 to-transparent"></div>
                    </div>

                    <div class="mb-8 flex items-center justify-between bg-white/5 border border-white/10 rounded-[1.5rem] px-6 py-5">
                        <div>
                        <h4 class="text-sm font-black text-white tracking-tight">Visibilidad en Catálogo</h4>
                        <p class="text-xs text-white/30 mt-1 font-medium italic">Si se desactiva, dejará de aparecer para la venta.</p>
                        </div>
                        <label class="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" v-model="form.disponible" class="sr-only peer">
                        <div class="w-12 h-6 bg-white/10 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-6 peer-checked:after:border-emerald-500 after:content-[''] after:absolute after:top-[4px] after:left-[4px] after:bg-white/20 after:rounded-full after:h-[16px] after:w-[16px] after:transition-all peer-checked:bg-emerald-600/40 border border-white/5"></div>
                        <span class="ml-4 text-[10px] font-black uppercase tracking-[0.1em] w-16" :class="form.disponible ? 'text-emerald-400' : 'text-white/20'">
                            {{ form.disponible ? 'Visible' : 'Oculto' }}
                        </span>
                        </label>
                    </div>

                    <div class="space-y-4">
                        <label class="block text-[10px] font-black text-white/30 uppercase tracking-[0.15em] mb-2 px-1">Galería de Imágenes <span class="text-emerald-500">*</span></label>
                        
                        <!-- Miniaturas de imágenes listas para subir -->
                        <div v-if="Array.isArray(form.imagenes) && form.imagenes.length > 0" class="mb-4">
                            <div class="grid grid-cols-4 sm:grid-cols-5 gap-4">
                                <div v-for="(img, index) in form.imagenes" :key="'new-'+index"
                                    class="relative group rounded-[1.25rem] overflow-hidden aspect-square bg-white/5 border-2 border-emerald-500/30 shadow-xl">
                                    <template v-if="img.url || img">
                                        <img :src="img.url || img" :alt="img.name || 'Portada'" class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110">
                                        <div class="absolute inset-0 bg-black/70 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center backdrop-blur-sm">
                                            <button @click.prevent="removeImage(index)" type="button"
                                                class="w-12 h-12 rounded-2xl bg-rose-500/20 border border-rose-500/50 text-rose-400 flex items-center justify-center shadow-lg transition-all transform hover:scale-110 hover:bg-rose-500 hover:text-white">
                                                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5">
                                                    <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                                                </svg>
                                            </button>
                                        </div>
                                    </template>
                                </div>
                            </div>
                        </div>

                        <!-- Drop Zone -->
                        <div @dragover.prevent="isDragging = true" @dragleave.prevent="isDragging = false" @drop.prevent="handleDrop"
                            @click="$refs.fileInput.click()"
                            :class="['rounded-[2rem] border-2 border-dashed p-10 transition-all duration-300 cursor-pointer',
                            isDragging ? 'border-emerald-500 bg-emerald-500/10 scale-[1.01] shadow-2xl shadow-emerald-500/20' : 'border-white/10 bg-white/3 hover:border-emerald-500/40 hover:bg-white/5']">
                            <div class="flex flex-col items-center gap-4 pointer-events-none">
                            <div :class="['w-16 h-16 rounded-[1.5rem] flex items-center justify-center transition-all', isDragging ? 'bg-emerald-500 text-black rotate-6' : 'bg-white/5 border border-white/10 text-emerald-500']">
                                <svg :class="['w-8 h-8 transition-colors', isDragging ? 'text-black' : 'text-emerald-500']" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
                                </svg>
                            </div>
                            <div class="text-center">
                                <p class="text-sm font-black text-white/70">
                                <span class="text-emerald-400">Haz clic para seleccionar</span> o arrastra aquí
                                </p>
                                <p class="text-[11px] text-white/20 mt-2 font-bold uppercase tracking-widest">PNG, JPG, WEBP · Hasta 5 fotos</p>
                            </div>
                            </div>
                            <input ref="fileInput" type="file" multiple accept="image/*" class="hidden" @change="handleSelect">
                        </div>
                    </div>
                </section>

                <section>
                    <div class="flex items-center gap-4 mb-8">
                        <div class="w-10 h-10 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm font-black flex items-center justify-center shadow-lg shadow-emerald-500/5 flex-shrink-0">3</div>
                        <h3 class="text-xs font-black text-white/40 uppercase tracking-[0.2em]">Atributos Extra</h3>
                        <div class="flex-1 h-px bg-gradient-to-r from-white/10 to-transparent"></div>
                        <button type="button" @click="agregarCaracteristica" class="flex items-center gap-2 text-[10px] font-black text-emerald-400 bg-emerald-500/10 hover:bg-emerald-500/20 px-4 py-2.5 rounded-xl border border-emerald-500/20 transition-all uppercase tracking-widest">
                            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                            Añadir
                        </button>
                    </div>

                    <div class="space-y-4 p-6 rounded-[2rem] bg-black/20 border border-white/5">
                        <transition-group name="list">
                            <div v-for="(carac, index) in form.caracteristicas" :key="index" class="flex flex-col sm:flex-row sm:items-center gap-4 group animate-fade-in-up relative bg-white/5 sm:bg-transparent p-4 sm:p-0 rounded-2xl border border-white/5 sm:border-none">
                                <div class="w-full sm:w-1/3 relative">
                                    <select v-model="carac.clave" class="w-full bg-white/5 border border-white/10 rounded-xl px-5 py-3.5 pr-10 text-xs font-bold text-white focus:outline-none focus:border-emerald-500/50 shadow-sm transition-all appearance-none cursor-pointer">
                                        <option value="" disabled class="bg-[#0a1a0f]">Elegir atributo...</option>
                                        <option v-for="attr in atributosPredefinidos" :key="attr" :value="attr" class="bg-[#0a1a0f]">{{ attr }}</option>
                                    </select>
                                    <div class="pointer-events-none absolute inset-y-0 right-4 flex items-center text-emerald-500/50">
                                      <svg class="h-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"></path></svg>
                                    </div>
                                </div>
                                <div class="flex items-center gap-3 flex-1">
                                    <input v-model="carac.valor" type="text" placeholder="Valor (Ej. Rojo, 300g)" class="flex-1 bg-white/5 border border-white/10 rounded-xl px-5 py-3.5 text-xs font-black text-emerald-400 focus:outline-none focus:border-emerald-500/50 shadow-sm transition-all placeholder:text-white/10">
                                    <button type="button" @click="eliminarCaracteristica(index)" class="w-10 h-10 flex items-center justify-center rounded-xl text-white/20 hover:text-rose-400 hover:bg-rose-500/10 transition-all flex-shrink-0 sm:opacity-0 sm:group-hover:opacity-100">
                                        <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M3 6h18"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                                    </button>
                                </div>
                            </div>
                        </transition-group>
                        <p v-if="form.caracteristicas.length === 0" class="text-[10px] text-white/20 text-center py-6 font-black uppercase tracking-[0.2em] italic border border-dashed border-white/5 rounded-2xl">
                            Sin especificaciones adicionales
                        </p>
                    </div>
                </section>
            </form>
        </div>

        <!-- FOOTER -->
        <div class="border-t border-white/5 px-8 py-6 flex items-center justify-between gap-4 bg-[#0d2114] flex-shrink-0 rounded-b-[2.5rem]">
          <p class="text-[10px] text-white/20 font-bold uppercase tracking-widest">Campos con <span class="text-emerald-500 font-black">*</span> obligatorios</p>
          <div class="flex items-center gap-4">
            <button @click="limpiarFormularioYcerrar" type="button" :disabled="isLoading"
              class="px-6 py-3 rounded-2xl font-black text-[11px] uppercase tracking-widest text-white/40 border-2 border-white/5 hover:bg-white/5 hover:text-white transition-all disabled:opacity-30">
              Cancelar
            </button>
            <button form="productForm" type="submit" :disabled="isLoading"
              class="px-8 py-3 rounded-2xl font-black text-[11px] uppercase tracking-widest text-black bg-emerald-500 hover:bg-emerald-400 shadow-xl shadow-emerald-900/40 transition-all flex items-center gap-3 hover:-translate-y-1 active:translate-y-0 disabled:opacity-50">
              <svg v-if="isLoading" class="animate-spin h-4 w-4 text-black" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <svg v-else-if="producto" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>
              <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="3"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/></svg>
              {{ isLoading ? (producto ? 'Actualizando' : 'Creando') : (producto ? 'Guardar Cambios' : 'Registrar Producto') }}
            </button>
          </div>
        </div>

      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.animate-fade-in-up {
  animation: fadeInUp 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(16px) scale(0.98); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}
.form-scroll::-webkit-scrollbar { width: 5px; }
.form-scroll::-webkit-scrollbar-track { background: transparent; }
.form-scroll::-webkit-scrollbar-thumb { background-color: #cbd5e1; border-radius: 20px; }
.list-enter-active,
.list-leave-active { transition: all 0.3s ease; }
.list-enter-from,
.list-leave-to { opacity: 0; transform: translateX(-15px); }
</style>
