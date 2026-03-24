<script setup>
import { ref, watch, defineProps, defineEmits } from 'vue';
import axios from 'axios';
import { useNotificacion } from '@/composables/useNotificacion';

const { mostrarNotificacion } = useNotificacion();

const API_URL = 'http://localhost:8000/api/productos/';

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

const categoriasLista = [
    { id: 1, nombre: 'Equipos de Supervivencia' },
    { id: 2, nombre: 'Seguridad y Primeros Auxilios' },
    { id: 3, nombre: 'Indumentaria Outdoor' },
    { id: 4, nombre: 'Accesorios de Viaje' },
    { id: 5, nombre: 'Tecnología y Navegación' }
];

const atributosPredefinidos = [
    'Color',
    'Talla',
    'Material',
    'Peso',
    'Dimensiones',
    'Capacidad',
    'Marca'
];

const form = ref(JSON.parse(JSON.stringify(inicialForm)));

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

        emit('guardadoExitoso');
    } catch (error) {
        console.error('Error guardando el producto:', error);
        let errorMsg = 'Hubo un error al guardar el producto.';
        if (error.response && error.response.data && error.response.data.errores) {
             errorMsg += '\nRevisa los siguientes campos: ' + JSON.stringify(error.response.data.errores);
        }
        alert(errorMsg);
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

      <div class="absolute inset-0 bg-slate-950/60 backdrop-blur-sm"></div>

      <div class="relative bg-white rounded-3xl shadow-2xl w-full max-w-3xl max-h-[92vh] flex flex-col overflow-hidden animate-fade-in-up">
        
        <!-- HEADER -->
        <div class="bg-gradient-to-br from-emerald-600 via-teal-600 to-cyan-600 px-8 py-6 flex-shrink-0">
          <div class="flex items-start justify-between gap-4">
            <div>
              <div class="flex items-center gap-2 mb-2">
                <span class="inline-flex items-center gap-1.5 text-[11px] font-bold tracking-widest uppercase text-emerald-200">
                  <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>
                  {{ producto ? 'Editando Producto' : 'Nuevo Producto' }}
                </span>
                <span class="text-xs bg-emerald-800 text-emerald-100 px-2 py-0.5 rounded-full uppercase tracking-wider font-semibold opacity-80 border border-emerald-500/30">
                    Catálogo: {{ tipoCatalogo }}
                </span>
              </div>
              <h2 class="text-2xl font-bold text-white leading-tight">
                {{ producto ? producto.nombre : 'Configurar Producto' }}
              </h2>
              <p class="text-emerald-100 text-sm mt-1">
                {{ producto ? 'Actualiza los datos del inventario' : 'Ingresa los datos para registrar un nuevo producto' }}
              </p>
            </div>
            <button @click="limpiarFormularioYcerrar"
              class="flex-shrink-0 w-10 h-10 flex items-center justify-center rounded-full bg-white/20 hover:bg-white/30 text-white transition-all hover:rotate-90 duration-200">
              <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
        </div>

        <div v-if="isLoading"
          class="absolute inset-0 bg-white/85 backdrop-blur-sm z-20 flex flex-col items-center justify-center rounded-3xl">
          <div class="w-16 h-16 border-4 border-emerald-100 border-t-emerald-600 rounded-full animate-spin mb-4"></div>
          <p class="text-emerald-800 font-bold text-lg">{{ producto ? 'Actualizando...' : 'Guardando producto...' }}</p>
          <p class="text-slate-400 text-sm mt-1">Esto tomará solo un momento</p>
        </div>

        <!-- FORM BODY -->
        <div class="overflow-y-auto flex-1 form-scroll">
            <form id="productForm" @submit.prevent="guardarProducto" class="p-8 space-y-8">
                
                <section>
                    <div class="flex items-center gap-3 mb-6">
                        <div class="w-8 h-8 rounded-full bg-emerald-600 text-white text-sm font-bold flex items-center justify-center shadow-md shadow-emerald-200 flex-shrink-0">1</div>
                        <h3 class="text-sm font-bold text-slate-700 uppercase tracking-wider">Detalles Generales</h3>
                        <div class="flex-1 h-px bg-gradient-to-r from-slate-200 to-transparent"></div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div class="space-y-1.5 md:col-span-2">
                            <label class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Nombre del Producto <span class="text-emerald-500">*</span></label>
                            <input v-model="form.nombre" type="text" required placeholder="Artesanía tallada, Tour fotográfico..." class="w-full bg-slate-50 border-2 border-slate-200 rounded-2xl px-5 py-3 text-slate-800 font-medium focus:outline-none focus:bg-white transition-all placeholder:text-slate-300 focus:border-emerald-500">
                        </div>
                        
                        <div class="space-y-1.5">
                            <label class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">SKU / Código <span class="text-emerald-500">*</span></label>
                            <input v-model="form.sku" type="text" required placeholder="AMZ-PRD-001" class="w-full bg-slate-50 border-2 border-slate-200 rounded-2xl px-5 py-3 text-slate-800 font-medium focus:outline-none focus:bg-white transition-all placeholder:text-slate-300 focus:border-emerald-500">
                        </div>

                        <div class="space-y-1.5">
                            <label class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Precio (COP) <span class="text-emerald-500">*</span></label>
                            <div class="relative">
                                <span class="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 font-bold">$</span>
                                <input v-model.number="form.precio" type="number" step="100" required placeholder="45000" class="w-full bg-slate-50 border-2 border-slate-200 rounded-2xl pl-9 pr-4 py-3 text-slate-800 font-bold focus:outline-none focus:bg-white transition-all placeholder:text-slate-300 focus:border-emerald-500">
                            </div>
                        </div>

                        <div class="space-y-1.5">
                            <label class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Stock Inicial <span class="text-emerald-500">*</span></label>
                            <input v-model.number="form.stock" type="number" min="0" required class="w-full bg-slate-50 border-2 border-slate-200 rounded-2xl px-5 py-3 text-slate-800 font-medium focus:outline-none focus:bg-white transition-all placeholder:text-slate-300 focus:border-emerald-500">
                        </div>

                        <div class="space-y-1.5 relative">
                            <label class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Categoría <span class="text-emerald-500">*</span></label>
                            <select v-model="form.categorias" required class="w-full bg-slate-50 border-2 border-slate-200 rounded-2xl px-5 py-3 pr-10 text-slate-800 font-medium focus:outline-none focus:bg-white transition-all focus:border-emerald-500 appearance-none cursor-pointer">
                                <option value="" disabled>Selecciona una categoría...</option>
                                <option v-for="cat in categoriasLista" :key="cat.id" :value="cat.id">{{ cat.nombre }}</option>
                            </select>
                            <div class="pointer-events-none absolute bottom-3.5 right-4 flex items-center text-slate-400">
                              <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                            </div>
                        </div>
                    </div>
                </section>

                <section>
                    <div class="flex items-center gap-3 mb-6">
                        <div class="w-8 h-8 rounded-full bg-emerald-600 text-white text-sm font-bold flex items-center justify-center shadow-md shadow-emerald-200 flex-shrink-0">2</div>
                        <h3 class="text-sm font-bold text-slate-700 uppercase tracking-wider">Multimedia & Estado</h3>
                        <div class="flex-1 h-px bg-gradient-to-r from-slate-200 to-transparent"></div>
                    </div>

                    <div class="mb-6 flex items-center justify-between bg-slate-50 border-2 border-slate-200 rounded-2xl px-5 py-4">
                        <div>
                        <h4 class="text-sm font-bold text-slate-700">Visibilidad en Catálogo</h4>
                        <p class="text-xs text-slate-500 mt-0.5">Si se desactiva, dejará de aparecer para la venta.</p>
                        </div>
                        <label class="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" v-model="form.disponible" class="sr-only peer">
                        <div class="w-11 h-6 bg-slate-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-emerald-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-600"></div>
                        <span class="ml-3 text-sm font-bold flex-shrink-0 w-16" :class="form.disponible ? 'text-emerald-600' : 'text-slate-400'">
                            {{ form.disponible ? 'Visible' : 'Oculto' }}
                        </span>
                        </label>
                    </div>

                    <div class="space-y-1.5">
                        <label class="block text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Galería de Imágenes <span class="text-emerald-500">*</span></label>
                        
                        <!-- Miniaturas de imágenes listas para subir -->
                        <div v-if="Array.isArray(form.imagenes) && form.imagenes.length > 0" class="mb-4">
                            <div class="grid grid-cols-4 sm:grid-cols-5 gap-3">
                                <div v-for="(img, index) in form.imagenes" :key="'new-'+index"
                                    class="relative group rounded-2xl overflow-hidden aspect-square bg-slate-100 ring-2 ring-emerald-400 shadow-sm">
                                    <img :src="img.url || img" :alt="img.name || 'Portada'" class="w-full h-full object-cover">
                                    <div class="absolute inset-0 bg-slate-950/60 opacity-0 group-hover:opacity-100 transition-opacity duration-200 flex items-center justify-center">
                                    <button @click.prevent="removeImage(index)" type="button"
                                        class="w-11 h-11 rounded-full bg-red-500 hover:bg-red-600 text-white flex items-center justify-center shadow-lg transition-all transform hover:scale-110">
                                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                                        </svg>
                                    </button>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Drop Zone -->
                        <div @dragover.prevent="isDragging = true" @dragleave.prevent="isDragging = false" @drop.prevent="handleDrop"
                            @click="$refs.fileInput.click()"
                            :class="['rounded-2xl border-2 border-dashed p-8 transition-all duration-200 cursor-pointer mt-2',
                            isDragging ? 'border-emerald-500 bg-emerald-50 scale-[1.01] shadow-lg shadow-emerald-100' : 'border-slate-200 bg-slate-50 hover:border-emerald-300 hover:bg-emerald-50/40']">
                            <div class="flex flex-col items-center gap-3 pointer-events-none">
                            <div :class="['w-14 h-14 rounded-2xl flex items-center justify-center transition-all', isDragging ? 'bg-emerald-100 rotate-3' : 'bg-white border border-slate-200']">
                                <svg :class="['w-7 h-7 transition-colors', isDragging ? 'text-emerald-600' : 'text-emerald-400']" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
                                </svg>
                            </div>
                            <div class="text-center">
                                <p class="text-sm font-bold text-slate-600">
                                <span class="text-emerald-600">Haz clic para seleccionar</span> o arrastra aquí
                                </p>
                                <p class="text-xs text-slate-400 mt-1">Soporta PNG, JPG, WEBP. Sube hasta 5 fotos.</p>
                            </div>
                            </div>
                            <input ref="fileInput" type="file" multiple accept="image/*" class="hidden" @change="handleSelect">
                        </div>
                    </div>
                </section>

                <section>
                    <div class="flex items-center gap-3 mb-6">
                        <div class="w-8 h-8 rounded-full bg-emerald-600 text-white text-sm font-bold flex items-center justify-center shadow-md shadow-emerald-200 flex-shrink-0">3</div>
                        <h3 class="text-sm font-bold text-slate-700 uppercase tracking-wider">Atributos Extra</h3>
                        <div class="flex-1 h-px bg-gradient-to-r from-slate-200 to-transparent"></div>
                        <button type="button" @click="agregarCaracteristica" class="flex items-center gap-1.5 text-xs font-bold text-emerald-700 bg-emerald-100 hover:bg-emerald-200 px-3 py-1.5 rounded-full transition-colors">
                            <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                            Agr. Atributo
                        </button>
                    </div>

                    <div class="space-y-3 p-5 rounded-2xl bg-slate-50 border-2 border-slate-200">
                        <transition-group name="list">
                            <div v-for="(carac, index) in form.caracteristicas" :key="index" class="flex items-center gap-3 group animate-fade-in-up">
                                <div class="w-1/3 relative">
                                    <select v-model="carac.clave" class="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 pr-8 text-sm text-slate-800 focus:outline-none focus:border-emerald-500 shadow-sm transition-all focus:ring-2 focus:ring-emerald-500/20 appearance-none cursor-pointer">
                                        <option value="" disabled>Elegir atributo...</option>
                                        <option v-for="attr in atributosPredefinidos" :key="attr" :value="attr">{{ attr }}</option>
                                    </select>
                                    <div class="pointer-events-none absolute inset-y-0 right-3 flex items-center text-slate-400">
                                      <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                                    </div>
                                </div>
                                <input v-model="carac.valor" type="text" placeholder="Valor o listado (Ej. Rojo, Verde o 300g)" class="flex-1 bg-white border border-slate-200 rounded-xl px-4 py-3 text-sm text-slate-800 focus:outline-none focus:border-emerald-500 shadow-sm transition-all focus:ring-2 focus:ring-emerald-500/20">
                                <button type="button" @click="eliminarCaracteristica(index)" class="w-10 h-10 flex items-center justify-center rounded-full text-slate-300 hover:text-red-500 hover:bg-red-50 transition-all flex-shrink-0 opacity-0 group-hover:opacity-100">
                                    <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 6h18"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                                </button>
                            </div>
                        </transition-group>
                        <p v-if="form.caracteristicas.length === 0" class="text-sm text-slate-400 text-center py-3 italic border border-dashed border-slate-300 rounded-xl bg-white/50">
                            No hay características configuradas.
                        </p>
                    </div>
                </section>
            </form>
        </div>

        <!-- FOOTER -->
        <div class="border-t border-slate-100 px-8 py-5 flex items-center justify-between gap-4 bg-white/80 backdrop-blur-sm flex-shrink-0 rounded-b-3xl">
          <p class="text-xs text-slate-400">Campos con <span class="text-emerald-500 font-bold">*</span> son obligatorios</p>
          <div class="flex items-center gap-3">
            <button @click="limpiarFormularioYcerrar" type="button" :disabled="isLoading"
              class="px-6 py-2.5 rounded-2xl font-semibold text-slate-600 border-2 border-slate-200 hover:bg-slate-100 transition-colors disabled:opacity-50">
              Cancelar
            </button>
            <button form="productForm" type="submit" :disabled="isLoading"
              class="px-7 py-2.5 rounded-2xl font-bold text-white bg-gradient-to-r from-emerald-600 to-teal-500 hover:from-emerald-700 hover:to-teal-600 shadow-lg shadow-emerald-200/60 transition-all flex items-center gap-2 hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-70 disabled:hover:translate-y-0">
              <svg v-if="isLoading" class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <svg v-else-if="producto" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
              <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
              {{ isLoading ? (producto ? 'Actualizando...' : 'Creando...') : (producto ? 'Guardar Cambios' : 'Crear Producto') }}
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
