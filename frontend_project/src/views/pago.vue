<script setup>
import { ref, computed, watch } from 'vue';
import axios from '@/api/axios';
import { useRouter } from 'vue-router';
import { useCarrito } from '@/composables/useCarrito';

const router = useRouter();
const { 
  totalFinal, 
  subtotalProductos, 
  subtotalTours, 
  tarifaEcologica,
  toursSeleccionados, // Tours del carrito
  productosSeleccionados, // Productos físicos en el carrito (asumido para el composable)
  itemsCarrito,
  vaciarCarrito
} = useCarrito();

const mostrarModalExito = ref(false);

// Determinar si hay productos físicos en el carrito para mostrar el formulario de envío
const requiereEnvio = computed(() => {
    // Checkear si la variable productosSeleccionados existe y tiene elementos
    return productosSeleccionados && productosSeleccionados.value && productosSeleccionados.value.length > 0;
});

// Helper para formato de moneda (simplificado para mostrar)
const formatPrecio = (valor) => 
  new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 }).format(valor || 0);

// --- ESTADOS DE FORMULARIO (Con persistencia) ---
const formTocado = ref(false);

const savedEnvio = sessionStorage.getItem('checkout_envio');
const envio = ref(savedEnvio ? JSON.parse(savedEnvio) : {
    nombre: '',
    telefono: '',
    direccion: '',
    apto: '',
    ciudad: ''
});

const metodosPago = [
    { 
      id: 'billeteras', 
      titulo: 'Nequi / DaviPlata', 
      svg: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" /></svg>' 
    },
    { 
      id: 'pse', 
      titulo: 'PSE (Transferencia Bancaria)', 
      svg: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" /></svg>' 
    },
    { 
      id: 'tarjeta', 
      titulo: 'Tarjeta de Crédito / Débito', 
      svg: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" /></svg>' 
    }
];

const savedMetodo = sessionStorage.getItem('checkout_metodo');
const metodoSeleccionado = ref(savedMetodo || '');

const savedFormsPago = sessionStorage.getItem('checkout_forms_pago');
const formsPago = ref(savedFormsPago ? JSON.parse(savedFormsPago) : {
    billeteras: { celular: '' },
    pse: { banco: '' },
    tarjeta: { numero: '', expiracion: '', cvv: '', titular: '' }
});

// Observadores para guardar automáticamente en el sessionStorage cada cambio
watch(envio, (newVal) => {
    sessionStorage.setItem('checkout_envio', JSON.stringify(newVal));
}, { deep: true });

watch(metodoSeleccionado, (newVal) => {
    sessionStorage.setItem('checkout_metodo', newVal);
});

watch(formsPago, (newVal) => {
    sessionStorage.setItem('checkout_forms_pago', JSON.stringify(newVal));
}, { deep: true });

// --- LÓGICA DE VALIDACIÓN ---
const esEnvioValido = computed(() => {
    // Si no requiere envío, siempre es válido (se salta la validación de dirección)
    if (!requiereEnvio.value) return true;
    
    return envio.value.nombre.trim().length >= 3 &&
           envio.value.telefono.trim().length >= 7 &&
           envio.value.direccion.trim().length >= 5 &&
           envio.value.ciudad !== '';
});

const esPagoValido = computed(() => {
    if (metodoSeleccionado.value === 'billeteras') {
        return formsPago.value.billeteras.celular.trim().length >= 10;
    }
    if (metodoSeleccionado.value === 'pse') {
        return formsPago.value.pse.banco !== '';
    }
    if (metodoSeleccionado.value === 'tarjeta') {
        const { numero, expiracion, cvv, titular } = formsPago.value.tarjeta;
        return numero.trim().length >= 15 &&
               expiracion.trim().length >= 4 &&
               cvv.trim().length >= 3 &&
               titular.trim().length >= 3;
    }
    return false;
});

const todoValido = computed(() => esEnvioValido.value && esPagoValido.value);

// --- CLASES DINÁMICAS (Validación Visual) ---
const getClassInput = (esValido) => {
    if (!formTocado.value) {
        return 'border-white/15 bg-white/8 text-white focus:border-emerald-500/60 focus:bg-white/10';
    }
    if (!esValido) {
        return 'border-red-400 bg-red-900/20 text-white focus:border-red-500';
    }
    return 'border-white/15 bg-white/8 text-white focus:border-emerald-500/60 focus:bg-white/10';
};

// --- ACCIÓN PRINCIPAL ---
const cargandoPago = ref(false);

const confirmarYPagar = async () => {
    formTocado.value = true;
    if (todoValido.value) {
        cargandoPago.value = true;
        try {
            const payload = {
                total: totalFinal.value,
                novedades_turistas: JSON.parse(sessionStorage.getItem('checkout_viajeros') || '[]'),
                items: itemsCarrito.value.map(i => ({
                    id: i.id,
                    tipo: i.tipo,
                    cantidad: i.cantidad,
                    precio: i.precio
                }))
            };

            await axios.post('api/venta/procesar/', payload);
            
            // Limpieza local de frontend
            vaciarCarrito();
            sessionStorage.removeItem('checkout_viajeros');
            sessionStorage.removeItem('checkout_envio');
            sessionStorage.removeItem('checkout_metodo');
            sessionStorage.removeItem('checkout_forms_pago');
            
            // Mostrar modal de éxito
            mostrarModalExito.value = true;

        } catch (error) {
            console.error("Error al procesar el pago:", error);
            alert("Hubo un error procesando el pago. Inténtalo de nuevo.");
        } finally {
            cargandoPago.value = false;
        }
    }
};

const volverInicio = () => {
    mostrarModalExito.value = false;
    router.push('/');
};

</script>

<template>
  <div class="min-h-screen bg-[#0a1a0f] text-white font-sans pb-16">
    
    <!-- ── Hero / Header ─────────────────────────────────────────────── -->
    <section class="relative pt-28 pb-10 overflow-hidden">
      <div class="absolute inset-0 bg-gradient-to-b from-[#0f2318] via-[#0a1a0f] to-[#0a1a0f]"></div>
      <div class="absolute top-20 left-1/4 w-80 h-80 rounded-full bg-emerald-500/5 blur-3xl pointer-events-none"></div>
      <div class="absolute bottom-0 right-1/4 w-56 h-56 rounded-full bg-teal-400/5 blur-3xl pointer-events-none"></div>

      <div class="relative z-10 max-w-4xl mx-auto px-6">

        <!-- Botón volver -->
        <button
          @click="router.back()"
          class="group flex items-center gap-2 text-white/40 hover:text-emerald-300 text-sm font-semibold transition-all mb-8 w-fit"
        >
          <svg class="w-4 h-4 group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18"/>
          </svg>
          Volver atrás
        </button>

        <!-- Contenido centrado -->
        <div class="text-center">

          <!-- Breadcrumb pasos -->
          <div class="flex items-center justify-center gap-2 mb-8">
            <div class="flex items-center gap-2">
              <div class="w-7 h-7 rounded-full bg-emerald-500/30 flex items-center justify-center">
                <svg class="w-3.5 h-3.5 text-emerald-300" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>
              </div>
              <span class="text-white/40 text-xs font-medium">Carrito</span>
            </div>
            <div class="w-10 h-px bg-white/15"></div>
            <div class="flex items-center gap-2">
              <div class="w-7 h-7 rounded-full bg-emerald-500/30 flex items-center justify-center">
                <svg class="w-3.5 h-3.5 text-emerald-300" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>
              </div>
              <span class="text-white/40 text-xs font-medium">Viajeros</span>
            </div>
            <div class="w-10 h-px bg-white/15"></div>
            <div class="flex items-center gap-2">
              <div class="w-7 h-7 rounded-full bg-emerald-500 flex items-center justify-center shadow-lg shadow-emerald-500/30">
                <span class="text-white text-xs font-black">3</span>
              </div>
              <span class="text-emerald-300 text-xs font-bold">Pago</span>
            </div>
          </div>

          <!-- Título -->
          <div class="inline-flex items-center gap-2 bg-emerald-500/15 backdrop-blur border border-emerald-400/25 text-emerald-300 text-xs font-bold uppercase tracking-widest px-5 py-2 rounded-full mb-6">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
            </svg>
            Pasarela Segura
          </div>
          <h1 class="text-4xl sm:text-5xl font-black text-white mb-4 leading-tight">
            Finaliza tu
            <span class="text-transparent bg-clip-text bg-gradient-to-r from-emerald-300 via-teal-200 to-lime-300"> Compra</span>
          </h1>
          <p class="text-white/50 text-base max-w-xl mx-auto mb-6 leading-relaxed">
            Estás a un solo paso de asegurar las reservas. Por favor completa los métodos de pago electrónico.
          </p>

          <!-- Trust badge -->
          <div class="inline-flex items-center gap-2.5 bg-white/5 border border-white/10 text-white/50 text-xs px-5 py-2.5 rounded-2xl mx-auto">
            <svg class="w-4 h-4 text-emerald-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/>
            </svg>
            <span>Conexión cifrada SSL 256 bits.</span>
          </div>

        </div><!-- /text-center -->
      </div><!-- /container -->
    </section>

    <!-- Layout Dividido (Desktop: 60/40, Mobile: Stack) -->
    <main class="max-w-6xl mx-auto px-5 lg:px-8 pt-8 lg:pt-12 relative z-10">
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-start">
        
        <!-- 2. Panel Izquierdo: Formularios (60% -> col-span-7) -->
        <div class="lg:col-span-7 space-y-8">
          
          <!-- SECCIÓN 1: Dirección de Entrega (CONDICIONAL) -->
          <section v-if="requiereEnvio" class="bg-white/5 rounded-2xl shadow-sm border border-white/10 p-6 sm:p-8 backdrop-blur-sm">
            <h2 class="text-lg font-bold text-white mb-6 flex items-center gap-3">
               <span class="w-7 h-7 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-black text-xs border border-emerald-500/40">1</span>
               Dirección de Entrega
            </h2>
            
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
              
              <!-- Nombre -->
              <div class="sm:col-span-2">
                <label class="block text-[11px] font-bold text-white/50 uppercase tracking-wider mb-2">Nombre Completo *</label>
                <input type="text" v-model="envio.nombre" 
                       :class="['w-full rounded-xl px-4 py-3 text-sm outline-none transition-all border ring-4 ring-transparent placeholder-white/30', getClassInput(envio.nombre.trim().length >= 3)]" 
                       placeholder="Ej: Juan Pérez">
                <p v-if="formTocado && envio.nombre.trim().length < 3" class="text-red-400 text-xs mt-1 font-medium">Requerido</p>
              </div>

              <!-- Teléfono -->
              <div>
                <label class="block text-[11px] font-bold text-white/50 uppercase tracking-wider mb-2">Teléfono Celular *</label>
                <input type="tel" v-model="envio.telefono" 
                       :class="['w-full rounded-xl px-4 py-3 text-sm outline-none transition-all border ring-4 ring-transparent placeholder-white/30', getClassInput(envio.telefono.trim().length >= 7)]" 
                       placeholder="Ej: 300 123 4567">
                <p v-if="formTocado && envio.telefono.trim().length < 7" class="text-red-400 text-xs mt-1 font-medium">Requerido</p>
              </div>

              <!-- Ciudad -->
              <div>
                <label class="block text-[11px] font-bold text-white/50 uppercase tracking-wider mb-2">Ciudad *</label>
                <div class="relative">
                    <select v-model="envio.ciudad" 
                            :class="['w-full rounded-xl px-4 py-3 text-sm outline-none transition-all border ring-4 ring-transparent appearance-none cursor-pointer', getClassInput(envio.ciudad !== '')]">
                        <option value="" disabled class="bg-[#0f2318] text-white">Selecciona tu ciudad</option>
                        <option value="Bogotá" class="bg-[#0f2318]">Bogotá D.C.</option>
                        <option value="Medellín" class="bg-[#0f2318]">Medellín</option>
                        <option value="Cali" class="bg-[#0f2318]">Cali</option>
                        <option value="Barranquilla" class="bg-[#0f2318]">Barranquilla</option>
                        <option value="Cartagena" class="bg-[#0f2318]">Cartagena</option>
                        <option value="Leticia" class="bg-[#0f2318]">Leticia</option>
                        <option value="Otra" class="bg-[#0f2318]">Otra ciudad/municipio</option>
                    </select>
                    <div class="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-white/40">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
                    </div>
                </div>
                <p v-if="formTocado && envio.ciudad === ''" class="text-red-400 text-xs mt-1 font-medium">Seleccione una ciudad</p>
              </div>

              <!-- Dirección -->
              <div class="sm:col-span-2">
                <label class="block text-[11px] font-bold text-white/50 uppercase tracking-wider mb-2">Dirección *</label>
                <input type="text" v-model="envio.direccion" 
                       :class="['w-full rounded-xl px-4 py-3 text-sm outline-none transition-all border ring-4 ring-transparent placeholder-white/30', getClassInput(envio.direccion.trim().length >= 5)]" 
                       placeholder="Ej: Carrera 10 # 20 - 30">
                <p v-if="formTocado && envio.direccion.trim().length < 5" class="text-red-400 text-xs mt-1 font-medium">Ingresa una dirección válida</p>
              </div>

              <!-- Apto (Opcional) -->
              <div class="sm:col-span-2">
                <label class="block text-[11px] font-bold text-white/50 uppercase tracking-wider mb-2">Apto / Torre / Barrio <span class="text-white/30 normal-case font-medium">(Opcional)</span></label>
                <input type="text" v-model="envio.apto" 
                       class="w-full rounded-xl px-4 py-3 text-sm outline-none transition-all border border-white/15 bg-white/8 text-white focus:border-emerald-500/60 focus:bg-white/10 placeholder-white/30" 
                       placeholder="Datos adicionales">
              </div>

            </div>
          </section>

          <!-- SECCIÓN 2: Método de Pago -->
          <section class="bg-white/5 rounded-2xl shadow-sm border border-white/10 p-6 sm:p-8 backdrop-blur-sm">
            <h2 class="text-lg font-bold text-white mb-2 flex items-center gap-3">
               <span class="w-7 h-7 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-black text-xs border border-emerald-500/40">{{ requiereEnvio ? '2' : '1' }}</span>
               Método de Pago
            </h2>
            <p class="text-sm text-white/50 mb-6 pl-10">Selecciona tu medio electrónico preferido.</p>
            
            <div class="space-y-4">
               
               <!-- Iterador de Opciones de Pago (Radio Buttons estilizados) -->
               <div v-for="metodo in metodosPago" :key="metodo.id" 
                    :class="['border rounded-xl transition-all overflow-hidden', metodoSeleccionado === metodo.id ? 'border-emerald-500/60 ring-1 ring-emerald-500/60 bg-emerald-500/10' : 'border-white/10 bg-white/5 hover:border-white/20']">
                 
                 <label class="flex items-center gap-4 p-4 cursor-pointer select-none">
                    <input type="radio" name="pago" :value="metodo.id" v-model="metodoSeleccionado" class="w-4 h-4 text-emerald-500 border-white/20 focus:ring-emerald-500 bg-white/10 cursor-pointer">
                    <span class="text-emerald-400" v-html="metodo.svg"></span>
                    <span class="font-bold text-sm text-white">{{ metodo.titulo }}</span>
                 </label>

                 <!-- CONTENIDO DINÁMICO DESPLEGABLE -->
                 <div v-if="metodoSeleccionado === metodo.id" class="px-4 pb-5 border-t border-white/10 pt-4 bg-white/5">
                    
                    <!-- Formulario Billeteras -->
                    <div v-if="metodo.id === 'billeteras'" class="pl-8">
                        <label class="block text-[11px] font-bold text-white/50 uppercase tracking-wider mb-2">Número de Celular *</label>
                        <input type="tel" v-model="formsPago.billeteras.celular" 
                               :class="['w-full max-w-sm rounded-xl px-4 py-3 text-sm outline-none transition-all border ring-4 ring-transparent placeholder-white/30', getClassInput(formsPago.billeteras.celular.trim().length >= 10)]" 
                               placeholder="Ej: 300 123 4567">
                        <p class="text-white/30 text-xs mt-2 font-medium">Recibirás una notificación push en Nequi/DaviPlata.</p>
                    </div>

                    <!-- Formulario PSE -->
                    <div v-if="metodo.id === 'pse'" class="pl-8">
                        <label class="block text-[11px] font-bold text-white/50 uppercase tracking-wider mb-2">Banco *</label>
                        <div class="relative max-w-sm">
                            <select v-model="formsPago.pse.banco" 
                                    :class="['w-full rounded-xl px-4 py-3 text-sm outline-none transition-all border ring-4 ring-transparent appearance-none cursor-pointer', getClassInput(formsPago.pse.banco !== '')]">
                                <option value="" disabled class="bg-[#0f2318] text-white">Selecciona tu banco</option>
                                <option value="Bancolombia" class="bg-[#0f2318]">Bancolombia</option>
                                <option value="Banco de Bogota" class="bg-[#0f2318]">Banco de Bogotá</option>
                                <option value="Davivienda" class="bg-[#0f2318]">Davivienda</option>
                                <option value="BBVA" class="bg-[#0f2318]">BBVA Colombia</option>
                                <option value="AV Villas" class="bg-[#0f2318]">Banco AV Villas</option>
                                <option value="Scotiabank" class="bg-[#0f2318]">Scotiabank Colpatria</option>
                            </select>
                            <div class="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-white/40">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7"/></svg>
                            </div>
                        </div>
                        <p class="text-white/30 text-[11px] mt-2 font-medium">Serás redirigido a la pasarela segura de PSE al confirmar.</p>
                    </div>

                    <!-- Formulario Tarjeta -->
                    <div v-if="metodo.id === 'tarjeta'" class="pl-8 grid grid-cols-2 gap-4">
                        <div class="col-span-2">
                            <label class="block text-[11px] font-bold text-white/50 uppercase tracking-wider mb-2">Número de Tarjeta *</label>
                            <input type="text" v-model="formsPago.tarjeta.numero" 
                                   :class="['w-full rounded-xl px-4 py-3 text-sm font-mono tracking-widest outline-none transition-all border ring-4 ring-transparent placeholder-white/30', getClassInput(formsPago.tarjeta.numero.trim().length >= 15)]" 
                                   placeholder="0000 0000 0000 0000" maxlength="19">
                        </div>
                        <div>
                            <label class="block text-[11px] font-bold text-white/50 uppercase tracking-wider mb-2">Expiración *</label>
                            <input type="text" v-model="formsPago.tarjeta.expiracion" 
                                   :class="['w-full rounded-xl px-4 py-3 text-sm outline-none transition-all border ring-4 ring-transparent placeholder-white/30', getClassInput(formsPago.tarjeta.expiracion.trim().length >= 4)]" 
                                   placeholder="MM/AA" maxlength="5">
                        </div>
                        <div>
                            <label class="block text-[11px] font-bold text-white/50 uppercase tracking-wider mb-2">CVV *</label>
                            <input type="text" v-model="formsPago.tarjeta.cvv" 
                                   :class="['w-full rounded-xl px-4 py-3 text-sm outline-none transition-all border ring-4 ring-transparent placeholder-white/30', getClassInput(formsPago.tarjeta.cvv.trim().length >= 3)]" 
                                   placeholder="123" maxlength="4">
                        </div>
                        <div class="col-span-2">
                            <label class="block text-[11px] font-bold text-white/50 uppercase tracking-wider mb-2">Titular de la Tarjeta *</label>
                            <input type="text" v-model="formsPago.tarjeta.titular" 
                                   :class="['w-full rounded-xl px-4 py-3 text-sm outline-none transition-all border ring-4 ring-transparent placeholder-white/30', getClassInput(formsPago.tarjeta.titular.trim().length >= 3)]" 
                                   placeholder="Nombre como aparece en la tarjeta">
                        </div>
                    </div>
                 </div>
               </div>
               
               <p v-if="formTocado && !esPagoValido" class="text-red-400 text-sm mt-3 font-semibold pl-2">Selecciona y completa un método de pago.</p>
               
            </div>
          </section>

        </div>

        <!-- 3. Panel Derecho: Resumen (40% -> col-span-5) -->
        <div class="lg:col-span-5 md:sticky md:top-28">
           <section class="bg-white/5 rounded-2xl shadow-sm border border-white/10 overflow-hidden flex flex-col backdrop-blur-sm">
              
              <!-- Title -->
              <div class="p-6 bg-white/5 border-b border-white/10">
                 <h2 class="text-lg font-bold text-white">Resumen de Compra</h2>
              </div>
              
              <!-- Lista Corta de Productos (Scroll sutil si son muchos) -->
              <div class="p-6 max-h-[35vh] overflow-y-auto space-y-4">
                 
                 <!-- Lista de tours -->
                 <div v-for="tour in toursSeleccionados" :key="'t-'+tour.id" class="flex gap-4">
                    <div class="w-16 h-16 rounded-lg bg-[#0f2318] flex-shrink-0 overflow-hidden border border-white/10">
                        <img v-if="tour.imagen" :src="tour.imagen" class="w-full h-full object-cover">
                    </div>
                    <div class="flex-1 min-w-0 flex flex-col justify-center">
                        <p class="text-sm font-bold text-white line-clamp-2 leading-tight">{{ tour.nombre }}</p>
                        <p class="text-xs text-white/50 mt-1">Tour · Cant: {{ tour.cantidad }}</p>
                    </div>
                    <div class="flex-shrink-0 font-bold text-sm text-white flex items-center">
                        {{ formatPrecio(tour.precio * tour.cantidad) }}
                    </div>
                 </div>

                 <!-- Lista de productos -->
                 <div v-for="prod in productosSeleccionados" :key="'p-'+prod.id" class="flex gap-4">
                    <div class="w-16 h-16 rounded-lg bg-[#0f2318] flex-shrink-0 overflow-hidden border border-white/10">
                        <img v-if="prod.imagen" :src="prod.imagen" class="w-full h-full object-cover">
                    </div>
                    <div class="flex-1 min-w-0 flex flex-col justify-center">
                        <p class="text-sm font-bold text-white line-clamp-2 leading-tight">{{ prod.nombre }}</p>
                        <p class="text-xs text-white/50 mt-1">Producto · Cant: {{ prod.cantidad }}</p>
                    </div>
                    <div class="flex-shrink-0 font-bold text-sm text-white flex items-center">
                        {{ formatPrecio(prod.precio * prod.cantidad) }}
                    </div>
                 </div>

                 <!-- Si el carrito está vacío (ej. test), mostrar mockup genérico para evitar layout roto -->
                 <div v-if="(!toursSeleccionados || toursSeleccionados.length === 0) && (!productosSeleccionados || productosSeleccionados.length === 0)" class="flex gap-4">
                    <div class="w-16 h-16 rounded-lg bg-[#0f2318] flex-shrink-0 border border-white/10"></div>
                    <div class="flex-1">
                        <p class="text-sm font-bold text-white">Cargando carrito...</p>
                        <p class="text-xs text-white/40 mt-1">O no hay items</p>
                    </div>
                 </div>
              </div>

              <!-- Desglose (Subtotales y Total) -->
              <div class="p-6 border-t border-white/10 bg-white/5 space-y-3">
                 <div class="flex justify-between text-sm text-white/70">
                     <span>Subtotal</span>
                     <span class="font-semibold text-white">{{ formatPrecio(subtotalTours + subtotalProductos) }}</span>
                 </div>
                 <div v-if="requiereEnvio" class="flex justify-between text-sm text-white/70">
                     <span>Costo de Envío</span>
                     <span class="font-semibold text-emerald-400">Por cotizar</span>
                 </div>
                 <div v-if="toursSeleccionados && toursSeleccionados.length > 0" class="flex justify-between text-sm text-white/70">
                     <span>Aporte Ecológico</span>
                     <span class="font-semibold text-emerald-400">{{ formatPrecio(tarifaEcologica) }}</span>
                 </div>
                 
                 <!-- Divider -->
                 <div class="h-px w-full bg-white/10 my-4"></div>

                 <!-- TOTAL (Destacado) -->
                 <div class="flex justify-between items-end">
                     <span class="text-sm font-bold text-white/50 uppercase tracking-widest">Total a Pagar</span>
                     <span class="text-3xl font-black text-white leading-none">{{ formatPrecio(totalFinal) }}</span>
                 </div>
                 <p class="text-[10px] text-white/40 text-right mt-1 w-full">Incluye impuestos locales (IVA)</p>
              </div>

              <!-- CTA PRINCIPAL -->
              <div class="p-6 pt-0 bg-white/5">
                  <!-- Mostrar alerta visual si se intenta dar clic estando form inválido y tocado -->
                  <div v-if="formTocado && !todoValido" class="mb-4 bg-red-900/20 border border-red-500/30 text-red-300 text-[11px] font-bold p-3 rounded-xl flex items-start gap-2">
                      <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                      Por favor, completa correctamente todos los campos obligatorios antes de continuar.
                  </div>

                  <!-- Botón Deshabilitado visualmente y lógicamente -->
                  <button @click="confirmarYPagar"
                          :disabled="cargandoPago" 
                          :class="['w-full py-4 rounded-xl font-black text-[15px] transition-all flex justify-center items-center gap-2', 
                                   todoValido && !cargandoPago
                                     ? 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white shadow-lg shadow-emerald-500/20 active:scale-[0.98]' 
                                     : 'bg-white/10 text-white/30 cursor-not-allowed border border-white/10']">
                      
                      <template v-if="cargandoPago">
                          <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          Procesando de forma segura...
                      </template>
                      <template v-else>
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg> 
                          Confirmar y Pagar
                      </template>
                  </button>

                  <p class="text-center text-[10px] font-medium text-white/30 mt-4 leading-relaxed">
                      Tus transacciones están encriptadas con seguridad SSL de 256 bits. No guardamos información de tus tarjetas sensibles.
                  </p>
              </div>

           </section>
        </div>

      </div>
    </main>

    <!-- MODAL DE ÉXITO -->
    <div v-if="mostrarModalExito" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
        <!-- Overlay blur -->
        <div class="absolute inset-0 bg-[#0a1a0f]/80 backdrop-blur-sm transition-opacity"></div>
        
        <!-- Contenido Modal -->
        <div class="relative bg-[#0f2318] border border-white/10 rounded-3xl shadow-2xl w-full max-w-sm p-8 text-center animate-fade-in-up">
            <!-- Icono verde gigante radiante -->
            <div class="mx-auto w-24 h-24 bg-emerald-500/20 rounded-full flex items-center justify-center mb-6 relative">
                <div class="absolute inset-0 rounded-full border border-emerald-500/30 animate-ping"></div>
                <svg class="w-12 h-12 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                </svg>
            </div>
            
            <h3 class="text-2xl font-black text-white mb-2">¡Compra Exitosa!</h3>
            <p class="text-white/60 text-sm mb-8 leading-relaxed">
                Tu transacción se procesó de manera segura y tus reservas han quedado guardadas. Te hemos enviado un recibo y los detalles al correo.
            </p>
            
            <button @click="volverInicio"
                    class="w-full bg-white/5 hover:bg-emerald-500/20 border border-white/10 hover:border-emerald-500/40 text-white py-4 rounded-xl font-bold transition-colors">
                Volver al Incio
            </button>
        </div>
    </div>

  </div>
</template>

<style scoped>
/* Eliminar flechas de inputs numéricos si los hubiera, 
   o ajustes menores custom */
input[type='number']::-webkit-inner-spin-button, 
input[type='number']::-webkit-outer-spin-button { 
    -webkit-appearance: none; 
    margin: 0; 
}
.line-clamp-2 {
    display: -webkit-box;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
</style>
