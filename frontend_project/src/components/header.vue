<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';
import { useUserStats } from '@/composables/useUserStats';
import { useCarrito } from '@/composables/useCarrito';
import { navegacion } from '@/config/navigation';
import axios from '@/api/axios';

const menuAbierto   = ref(false);
const mobileAbierto = ref(false);
const route         = useRoute();

const rolRaw = localStorage.getItem('rol') || '';
const rol    = rolRaw.toLowerCase();
const token = localStorage.getItem('token');

// ── Nombre reactivo (se actualiza en tiempo real desde la página de perfil) ──
const nombreRef = ref(
  rol === 'agencia'   ? (localStorage.getItem('nombre_agencia') || '') :
  rol === 'proveedor' ? (localStorage.getItem('nombre_empresa')  || '') :
  rol === 'turista'   ? (localStorage.getItem('nombre')          || '') : ''
);

// ── Foto de perfil reactiva ──
const fotoUrlHeader = ref(localStorage.getItem('foto_url') || null);

const nombre_usuario = computed(() => nombreRef.value || 'Invitado');

const iniciales = computed(() => {
  const n = nombre_usuario.value || '';
  return n.trim().slice(0, 2).toUpperCase() || 'AV';
});

const menu = computed(() => navegacion[rol] || navegacion.invitado);

const rolConfig = computed(() => {
  if (rol === 'turista')   return { label: 'Turista',   color: 'bg-emerald-500/25 text-emerald-300 border border-emerald-500/30' };
  if (rol === 'agencia')   return { label: 'Agencia',   color: 'bg-teal-500/25 text-teal-300 border border-teal-500/30' };
  if (rol === 'proveedor') return { label: 'Proveedor', color: 'bg-amber-500/25 text-amber-300 border border-amber-500/30' };
  return null;
});

const { favoritesCount, updateStats } = useUserStats();
const { cartCount, cargarDesdeBackend, resetearCarrito } = useCarrito();

// ── Handlers de eventos del módulo de Perfil ──
function onNombreActualizado(e) {
  nombreRef.value = e.detail.nombre;
}
function onFotoActualizada(e) {
  fotoUrlHeader.value = e.detail.foto_url;
}

onMounted(() => {
  if (token) {
    updateStats();
    cargarDesdeBackend();
  }
  window.addEventListener('perfil:nombre-actualizado', onNombreActualizado);
  window.addEventListener('perfil:foto-actualizada',   onFotoActualizada);
});

onUnmounted(() => {
  window.removeEventListener('perfil:nombre-actualizado', onNombreActualizado);
  window.removeEventListener('perfil:foto-actualizada',   onFotoActualizada);
});

const cerrarSesion = async () => {
  try {
    const refresh_token = localStorage.getItem('refresh_token');
    if (refresh_token) await axios.post('api/logout/', { refresh_token });
  } catch (e) {
    console.error(e);
  } finally {
    localStorage.clear();
    resetearCarrito();
    window.location.href = '/';
  }
};

const isActive = (path) => {
  if (path === '/') return route.path === '/';
  return route.path.startsWith(path);
};
</script>

<template>
  <header class="sticky top-0 z-50 bg-[#0f2318] border-b border-white/8 shadow-lg shadow-black/30">
    <nav class="max-w-7xl mx-auto px-6 h-[70px] flex items-center justify-between gap-6">

      <!-- ── LOGO ── -->
      <router-link
        to="/"
        class="flex items-center gap-3 flex-shrink-0 group"
        @click="mobileAbierto = false"
      >
        <div class="relative">
          <div class="absolute inset-0 rounded-xl bg-emerald-400/30 blur-md scale-125 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
          <img
            src="../assets/public/amazon_logo.png"
            class="relative w-9 h-9 object-contain drop-shadow-sm"
            alt="Amazonia Viva"
          >
        </div>
        <div class="leading-tight">
          <div class="text-white font-black text-base tracking-tight leading-none">Amazonia</div>
          <div class="text-emerald-400 font-bold text-[11px] uppercase tracking-[0.2em] leading-none">Viva</div>
        </div>
      </router-link>

      <!-- ── NAV LINKS (Desktop) ── -->
      <div class="hidden md:flex items-center gap-1 flex-1 justify-center">
        <router-link
          v-for="item in menu"
          :key="item.label"
          :to="item.path"
          :class="[
            'relative px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-200',
            isActive(item.path)
              ? 'text-emerald-300 bg-emerald-500/20'
              : 'text-slate-300 hover:text-white hover:bg-white/10'
          ]"
        >
          {{ item.label }}
          <!-- Punto indicador activo -->
          <span
            v-if="isActive(item.path)"
            class="absolute -bottom-0.5 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full bg-emerald-400"
          ></span>
        </router-link>
      </div>

      <!-- ── ACCIONES DERECHA ── -->
      <div class="flex items-center gap-1.5 flex-shrink-0">

        <!-- === AUTENTICADO === -->
        <template v-if="token">

          <!-- Carrito -->
          <button
            v-if="rol === 'turista' || rol === 'agencia'"
            @click="$router.push('/carrito')"
            class="relative p-2.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-all"
            title="Carrito"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"/>
            </svg>
            <span
              v-if="cartCount > 0"
              class="absolute -top-0.5 -right-0.5 min-w-[17px] h-[17px] bg-emerald-500 text-white text-[9px] font-black rounded-full flex items-center justify-center border border-[#0f2318] shadow badge-pop"
            >{{ cartCount }}</span>
          </button>

          <!-- Favoritos -->
          <button
            v-if="rol === 'turista' || rol === 'agencia'"
            @click="$router.push('/mis-favoritos')"
            class="relative p-2.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 transition-all"
            title="Mis Favoritos"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/>
            </svg>
            <span
              v-if="favoritesCount > 0"
              class="absolute -top-0.5 -right-0.5 min-w-[17px] h-[17px] bg-rose-500 text-white text-[9px] font-black rounded-full flex items-center justify-center border border-[#0f2318] shadow badge-pop"
            >{{ favoritesCount }}</span>
          </button>

          <!-- Divisor -->
          <div class="h-6 w-px bg-white/10 mx-1"></div>

          <!-- Avatar + Dropdown -->
          <div class="relative">
            <button
              @click="menuAbierto = !menuAbierto"
              :class="[
                'flex items-center gap-2 pl-1.5 pr-3 py-1.5 rounded-xl transition-all duration-200',
                menuAbierto ? 'bg-white/12' : 'hover:bg-white/10'
              ]"
            >
              <!-- Avatar (botón) -->
              <div class="w-7 h-7 rounded-lg bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center text-white text-[11px] font-black shadow-md overflow-hidden">
                <img v-if="fotoUrlHeader" :src="fotoUrlHeader" class="w-full h-full object-cover" alt="Foto" />
                <span v-else>{{ iniciales }}</span>
              </div>
              <!-- Nombre (solo en pantallas lg+) -->
              <span class="hidden lg:block text-slate-200 text-sm font-semibold max-w-[100px] truncate">
                {{ nombre_usuario }}
              </span>
              <!-- Chevron -->
              <svg
                :class="['w-3.5 h-3.5 text-slate-400 transition-transform duration-200', menuAbierto ? 'rotate-180' : '']"
                fill="none" stroke="currentColor" viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7"/>
              </svg>
            </button>

            <!-- Clic fuera -->
            <div v-if="menuAbierto" class="fixed inset-0 z-40" @click="menuAbierto = false"></div>

            <!-- Panel dropdown -->
            <transition
              enter-active-class="transition ease-out duration-150"
              enter-from-class="opacity-0 translate-y-1 scale-95"
              enter-to-class="opacity-100 translate-y-0 scale-100"
              leave-active-class="transition ease-in duration-100"
              leave-from-class="opacity-100 translate-y-0 scale-100"
              leave-to-class="opacity-0 translate-y-1 scale-95"
            >
              <div
                v-if="menuAbierto"
                class="absolute right-0 mt-2 w-56 rounded-2xl overflow-hidden z-50 shadow-2xl shadow-black/50 border border-white/10 bg-[#122b1a]"
              >
                <!-- Perfil mini en el header del dropdown -->
                <div class="px-4 py-3.5 flex items-center gap-3 border-b border-white/8 bg-white/4">
                  <div class="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center text-white font-black text-sm shadow overflow-hidden">
                    <img v-if="fotoUrlHeader" :src="fotoUrlHeader" class="w-full h-full object-cover" alt="Foto" />
                    <span v-else>{{ iniciales }}</span>
                  </div>
                  <div class="min-w-0">
                    <p class="text-white text-sm font-bold truncate">{{ nombre_usuario }}</p>
                    <span v-if="rolConfig" :class="['inline-block text-[10px] font-bold px-2 py-0.5 rounded-full mt-0.5', rolConfig.color]">
                      {{ rolConfig.label }}
                    </span>
                  </div>
                </div>

                <!-- Items -->
                <div class="py-1.5">
                  <router-link
                    :to="rol === 'turista' ? '/mi-perfil' : '/perfil'"
                    @click="menuAbierto = false"
                    class="flex items-center gap-3 px-4 py-2.5 text-sm text-slate-300 hover:text-white hover:bg-white/8 transition-colors">
                    <svg class="w-4 h-4 text-slate-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
                    Mi Perfil
                  </router-link>

                  <router-link to="/configuraciones" @click="menuAbierto = false"
                    class="flex items-center gap-3 px-4 py-2.5 text-sm text-slate-300 hover:text-white hover:bg-white/8 transition-colors">
                    <svg class="w-4 h-4 text-slate-400 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><circle cx="12" cy="12" r="3"/></svg>
                    Configuraciones
                  </router-link>

                  <div class="h-px bg-white/8 mx-4 my-1"></div>

                  <button @click="cerrarSesion"
                    class="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-red-400 hover:text-red-300 hover:bg-red-500/10 transition-colors text-left">
                    <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/></svg>
                    Cerrar Sesión
                  </button>
                </div>
              </div>
            </transition>
          </div>
        </template>

        <!-- === SIN SESIÓN === -->
        <template v-else>
          <router-link
            to="/auth/login"
            class="hidden sm:block px-4 py-2 rounded-lg text-sm font-semibold text-slate-300 hover:text-white hover:bg-white/10 transition-all"
          >
            Iniciar Sesión
          </router-link>
          <router-link
            to="/auth/signup"
            class="px-5 py-2.5 rounded-xl text-sm font-bold text-white bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 transition-all shadow-md shadow-emerald-500/20 hover:scale-105"
          >
            Registrarse
          </router-link>
        </template>

        <!-- Hamburguesa mobile -->
        <button
          @click="mobileAbierto = !mobileAbierto"
          class="md:hidden p-2.5 ml-1 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-all"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
            <path v-if="!mobileAbierto" stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16"/>
            <path v-else stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>
    </nav>

    <!-- ── MENÚ MOBILE ── -->
    <transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="opacity-0 -translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition ease-in duration-150"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-2"
    >
      <div
        v-if="mobileAbierto"
        class="md:hidden border-t border-white/8 bg-[#0f2318] px-4 pb-4 pt-3 space-y-1"
      >
        <router-link
          v-for="item in menu" :key="item.label" :to="item.path"
          @click="mobileAbierto = false"
          :class="[
            'flex items-center px-4 py-3 rounded-xl text-sm font-semibold transition-all',
            isActive(item.path)
              ? 'text-emerald-300 bg-emerald-500/20'
              : 'text-slate-300 hover:text-white hover:bg-white/10'
          ]"
        >{{ item.label }}</router-link>

        <!-- Botones login/registro en mobile sin sesión -->
        <div v-if="!token" class="pt-3 space-y-2 border-t border-white/8 mt-2">
          <router-link to="/auth/login" @click="mobileAbierto = false"
            class="block w-full text-center py-2.5 rounded-xl text-sm font-semibold text-slate-300 border border-white/15 hover:bg-white/10 transition-all">
            Iniciar Sesión
          </router-link>
          <router-link to="/auth/signup" @click="mobileAbierto = false"
            class="block w-full text-center py-2.5 rounded-xl text-sm font-bold text-white bg-gradient-to-r from-emerald-600 to-teal-600 shadow-md">
            Registrarse
          </router-link>
        </div>
      </div>
    </transition>
  </header>
</template>

<style scoped>
.badge-pop {
  animation: badgePop 0.35s cubic-bezier(0.34, 1.56, 0.64, 1) forwards;
}
@keyframes badgePop {
  from { transform: scale(0); opacity: 0; }
  to   { transform: scale(1); opacity: 1; }
}
</style>
