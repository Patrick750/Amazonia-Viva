<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import axios from '@/api/axios'

const props = defineProps({
  perfil: { type: Object, default: () => ({}) }
})

const route = useRoute()

// ── STATE ─────────────────────────────────────────────────────────────────
const rawData      = ref({ reservasAgrupadas: [], rechazadosAgrupados: [], cancelaciones: [] })
const loading      = ref(true)
const globalSearch = ref('')
const searchQuery  = ref('')
const currentTab   = ref('pendientes')
const currentPage  = ref(1)
const perPage      = ref(10)
const sortKey      = ref('fecha_pedido')
const sortAsc      = ref(false)
const activeMenu   = ref(null)

// ── CONSTANTS ─────────────────────────────────────────────────────────────
const TAB_STATE_MAP = {
  pendientes: ['Pendiente de Empaque', 'Confirmado'],
  encamino:   ['Enviado', 'En Tránsito'],
  entregados: ['Entregado'],
  anulados:   ['Devuelto', 'Cancelado', 'Reembolsado']
}

const TABS = [
  { id: 'pendientes', label: 'Pedidos Activos' },
  { id: 'encamino',   label: 'En Camino' },
  { id: 'entregados', label: 'Entregados' },
  { id: 'anulados',   label: 'Anulados' }
]

const BADGE_MAP = {
  'Pendiente de Empaque': { text: 'Pendiente',   cls: 'badge-warn',    dot: '#fbbf24' },
  'Confirmado':           { text: 'Confirmado',   cls: 'badge-warn',    dot: '#fbbf24' },
  'Enviado':              { text: 'Enviado',       cls: 'badge-info',    dot: '#60a5fa' },
  'En Tránsito':          { text: 'En Tránsito',  cls: 'badge-info',    dot: '#60a5fa' },
  'Entregado':            { text: 'Entregado',     cls: 'badge-success', dot: '#4ade80' },
  'Devuelto':             { text: 'Devuelto',      cls: 'badge-error',   dot: '#f87171' },
  'Cancelado':            { text: 'Cancelado',     cls: 'badge-error',   dot: '#f87171' },
  'Reembolsado':          { text: 'Reembolsado',   cls: 'badge-neutral', dot: '#9ba8a0' }
}

const NEXT_STATE_MAP = {
  'Pendiente de Empaque': 'Enviado',
  'Confirmado':           'Enviado',
  'Enviado':              'En Tránsito',
  'En Tránsito':          'Entregado',
  'Entregado':            'Devuelto'
}

const NAV_ITEMS = [
  { label: 'Dashboard',     to: '/panel/dashboard',        icon: 'grid'  },
  { label: 'Ver Ventas',    to: '/panel/gestion-reservas', icon: 'chart' },
  { label: 'Mis Productos', to: '/panel/productos',        icon: 'box'   },
  { label: 'Mi Perfil',     to: '/panel/perfil-empresa',   icon: 'user'  }
]

const ICONS = {
  grid:  `<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/></svg>`,
  chart: `<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>`,
  box:   `<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>`,
  user:  `<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>`
}

// ── FETCH ──────────────────────────────────────────────────────────────────
const fetchData = async () => {
  loading.value = true
  try {
    const { data } = await axios.get('/api/gestion-proveedor/logistica/')
    rawData.value = data
  } catch (e) {
    console.error('VentasProveedor fetch error:', e)
  } finally {
    loading.value = false
  }
}

onMounted(fetchData)

// ── COMPUTED ───────────────────────────────────────────────────────────────
const allOrders = computed(() => {
  const src = [
    ...(rawData.value?.reservasAgrupadas   || []),
    ...(rawData.value?.rechazadosAgrupados || [])
  ]
  const out = []
  for (const g of src) {
    for (const dg of g.reservasPorFecha || []) {
      for (const t of dg.turistas || []) {
        out.push({ ...t, paquete: g.paquete, fecha_pedido: dg.fecha })
      }
    }
  }
  return out
})

const tabCounts = computed(() => {
  const c = {}
  for (const tab of TABS) {
    c[tab.id] = allOrders.value.filter(o =>
      (TAB_STATE_MAP[tab.id] || []).includes(o.estado)
    ).length
  }
  return c
})

const filtered = computed(() => {
  const states = TAB_STATE_MAP[currentTab.value] || []
  let rows = allOrders.value.filter(o => states.includes(o.estado))
  const q = (searchQuery.value || globalSearch.value).toLowerCase().trim()
  if (q) {
    rows = rows.filter(o =>
      o.nombre?.toLowerCase().includes(q) ||
      o.producto_nombre?.toLowerCase().includes(q) ||
      String(o.id_transaccion || '').includes(q)
    )
  }
  return [...rows].sort((a, b) => {
    const vA = a[sortKey.value]
    const vB = b[sortKey.value]
    if (vA == null) return 1
    if (vB == null) return -1
    const cmp = String(vA).localeCompare(String(vB), 'es', { numeric: true })
    return sortAsc.value ? cmp : -cmp
  })
})

const totalRows  = computed(() => filtered.value.length)
const totalPages = computed(() => Math.max(1, Math.ceil(totalRows.value / perPage.value)))
const startRow   = computed(() => totalRows.value === 0 ? 0 : (currentPage.value - 1) * perPage.value + 1)
const endRow     = computed(() => Math.min(currentPage.value * perPage.value, totalRows.value))
const pageRows   = computed(() => {
  const s = (currentPage.value - 1) * perPage.value
  return filtered.value.slice(s, s + perPage.value)
})

// ── USER INFO ─────────────────────────────────────────────────────────────
const userName    = computed(() => props.perfil?.nombre || props.perfil?.nombre_empresa || localStorage.getItem('usuario') || 'Proveedor')
const userInitial = computed(() => userName.value.charAt(0).toUpperCase())
const isNavActive = (to) => route.path.startsWith(to)
const navIcon     = (name) => ICONS[name] || ICONS.grid

// ── ACTIONS ───────────────────────────────────────────────────────────────
const setTab = (id) => {
  currentTab.value  = id
  currentPage.value = 1
  searchQuery.value = ''
  activeMenu.value  = null
}

const toggleSort = (key) => {
  if (sortKey.value === key) sortAsc.value = !sortAsc.value
  else { sortKey.value = key; sortAsc.value = true }
}

const toggleMenu = (id) => { activeMenu.value = activeMenu.value === id ? null : id }
const closeMenu  = () => { activeMenu.value = null }

const actualizarEstado = async (order, nuevoEstado) => {
  closeMenu()
  try {
    await axios.post('/api/gestion-proveedor/logistica/actualizar-estado/', {
      id_detalle: order.id_detalle,
      estado: nuevoEstado
    })
    await fetchData()
  } catch (e) {
    console.error(e)
    alert('Error al actualizar el estado del pedido.')
  }
}

// ── HELPERS ───────────────────────────────────────────────────────────────
const getBadge = (estado) => BADGE_MAP[estado] || { text: estado, cls: 'badge-neutral', dot: '#9ba8a0' }
const getNext  = (estado) => NEXT_STATE_MAP[estado] || null
const fDate    = (s) => s ? new Date(s).toLocaleDateString('es-CO', { year: 'numeric', month: 'short', day: 'numeric', timeZone: 'UTC' }) : '—'

// Click outside to close menu
const handleOutsideClick = (e) => { if (!e.target.closest('.row-menu-wrapper')) closeMenu() }
onMounted(() => document.addEventListener('click', handleOutsideClick))
onBeforeUnmount(() => document.removeEventListener('click', handleOutsideClick))
</script>

<template>
  <div class="vp-shell">

    <!-- ═══════════════════════════════════════════════════════
         SIDEBAR
    ════════════════════════════════════════════════════════ -->
    <aside class="vp-sidebar">
      <!-- Logo -->
      <div class="vp-logo">
        <div class="vp-logo-icon">
          <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
          </svg>
        </div>
        <div>
          <p class="vp-logo-brand">Amazonia Viva</p>
          <p class="vp-logo-role">Panel Proveedor</p>
        </div>
      </div>

      <!-- Nav -->
      <nav class="vp-nav" aria-label="Navegación principal">
        <p class="vp-nav-heading">Menú Principal</p>
        <router-link
          v-for="item in NAV_ITEMS"
          :key="item.to"
          :to="item.to"
          class="vp-nav-item"
          :class="{ 'is-active': isNavActive(item.to) }"
        >
          <span class="vp-nav-icon" v-html="navIcon(item.icon)"></span>
          <span class="vp-nav-label">{{ item.label }}</span>
          <span v-if="item.to === '/panel/gestion-reservas' && tabCounts.pendientes > 0" class="vp-nav-badge">{{ tabCounts.pendientes }}</span>
        </router-link>
      </nav>

      <!-- Footer -->
      <div class="vp-sidebar-footer">
        <div class="vp-user-card">
          <div class="vp-user-avatar">{{ userInitial }}</div>
          <div class="vp-user-meta">
            <p class="vp-user-name">{{ userName }}</p>
            <p class="vp-user-role">Proveedor Activo</p>
          </div>
        </div>
      </div>
    </aside>

    <!-- ═══════════════════════════════════════════════════════
         RIGHT PANEL
    ════════════════════════════════════════════════════════ -->
    <div class="vp-right">

      <!-- TOP BAR -->
      <header class="vp-topbar">
        <nav class="vp-breadcrumbs" aria-label="Ubicación">
          <router-link to="/panel/dashboard" class="vp-bc-link">Panel</router-link>
          <span class="vp-bc-sep">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 18l6-6-6-6"/></svg>
          </span>
          <span class="vp-bc-current">Ver Ventas</span>
        </nav>

        <div class="vp-topbar-search">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
          </svg>
          <input
            v-model="globalSearch"
            type="text"
            placeholder="Búsqueda global..."
            class="vp-topbar-input"
            id="global-search-input"
          />
        </div>

        <div class="vp-topbar-actions">
          <button class="vp-icon-btn" @click="fetchData" title="Actualizar datos">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
              <path d="M1 4v6h6M23 20v-6h-6"/>
              <path d="M20.49 9A9 9 0 005.64 5.64L1 10m22 4-4.64 4.36A9 9 0 013.51 15"/>
            </svg>
          </button>
          <div class="vp-avatar-btn" :title="userName">{{ userInitial }}</div>
        </div>
      </header>

      <!-- MAIN CANVAS -->
      <main class="vp-canvas">

        <!-- Loading State -->
        <div v-if="loading" class="vp-loading-state">
          <div class="vp-spinner"></div>
          <p>Sincronizando registros de ventas...</p>
        </div>

        <template v-else>
          <!-- SURFACE CARD -->
          <div class="vp-surface">

            <!-- ── VIEW HEADER ──────────────────────────────────────────── -->
            <div class="vp-view-header">
              <div class="vp-view-header-left">
                <h2 class="vp-view-title" id="ventas-title">Gestión de Ventas</h2>
                <p class="vp-view-subtitle">Monitorea y gestiona el ciclo completo de tus pedidos en tiempo real</p>
              </div>
              <button class="vp-btn-primary" id="export-btn">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round">
                  <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
                  <polyline points="7 10 12 15 17 10"/>
                  <line x1="12" y1="15" x2="12" y2="3"/>
                </svg>
                Exportar Reporte
              </button>
            </div>

            <!-- ── FILTER BAR ────────────────────────────────────────────── -->
            <div class="vp-filter-bar">
              <!-- Tabs -->
              <div class="vp-tabs" role="tablist" aria-label="Estados de pedido">
                <button
                  v-for="tab in TABS"
                  :key="tab.id"
                  :id="`tab-${tab.id}`"
                  role="tab"
                  :aria-selected="currentTab === tab.id"
                  class="vp-tab"
                  :class="{ 'is-active': currentTab === tab.id }"
                  @click="setTab(tab.id)"
                >
                  {{ tab.label }}
                  <span class="vp-tab-count">{{ tabCounts[tab.id] }}</span>
                </button>
              </div>

              <!-- Local search -->
              <div class="vp-search-box">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
                </svg>
                <input
                  v-model="searchQuery"
                  type="text"
                  placeholder="Buscar pedido, cliente, producto..."
                  class="vp-search-input"
                  id="table-search-input"
                />
                <button v-if="searchQuery" class="vp-clear-search" @click="searchQuery = ''" title="Limpiar">
                  <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M18 6L6 18M6 6l12 12"/></svg>
                </button>
              </div>
            </div>

            <!-- ── DATA TABLE ────────────────────────────────────────────── -->
            <div class="vp-table-wrap" role="region" aria-labelledby="ventas-title">
              <table class="vp-table">
                <thead>
                  <tr>
                    <th class="vp-th" style="width:260px;">Producto</th>
                    <th class="vp-th vp-th--sort" @click="toggleSort('nombre')">
                      <span>Cliente</span>
                      <span class="vp-sort-icon" :class="{ '--active': sortKey === 'nombre', '--asc': sortAsc && sortKey === 'nombre' }">
                        <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M7 15l5 5 5-5M7 9l5-5 5 5"/></svg>
                      </span>
                    </th>
                    <th class="vp-th">Referencia</th>
                    <th class="vp-th vp-th--sort" @click="toggleSort('fecha_pedido')">
                      <span>Fecha</span>
                      <span class="vp-sort-icon" :class="{ '--active': sortKey === 'fecha_pedido', '--asc': sortAsc && sortKey === 'fecha_pedido' }">
                        <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M7 15l5 5 5-5M7 9l5-5 5 5"/></svg>
                      </span>
                    </th>
                    <th class="vp-th vp-th--sort" @click="toggleSort('cupos')">
                      <span>Cant.</span>
                      <span class="vp-sort-icon" :class="{ '--active': sortKey === 'cupos', '--asc': sortAsc && sortKey === 'cupos' }">
                        <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M7 15l5 5 5-5M7 9l5-5 5 5"/></svg>
                      </span>
                    </th>
                    <th class="vp-th">Estado</th>
                    <th class="vp-th" style="text-align:center; width:72px;">Acciones</th>
                  </tr>
                </thead>
                <tbody>

                  <!-- Empty State -->
                  <tr v-if="pageRows.length === 0" class="vp-empty-row">
                    <td colspan="7">
                      <div class="vp-empty-state">
                        <div class="vp-empty-icon-wrap">
                          <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
                            <rect x="2" y="4" width="20" height="16" rx="2"/>
                            <path d="M8 2v4M16 2v4M2 10h20M9 16l2 2 4-4"/>
                          </svg>
                        </div>
                        <p class="vp-empty-title">Sin registros</p>
                        <p class="vp-empty-text">
                          No hay pedidos{{ searchQuery ? ` con "${searchQuery}"` : '' }} en este estado.
                        </p>
                      </div>
                    </td>
                  </tr>

                  <!-- Data Rows -->
                  <tr
                    v-for="order in pageRows"
                    :key="order.id_detalle"
                    class="vp-row"
                  >
                    <!-- Col 1: Producto -->
                    <td class="vp-td">
                      <div class="vp-cell-product">
                        <div class="vp-thumb">
                          <img
                            v-if="order.paquete?.portada"
                            :src="order.paquete.portada"
                            :alt="order.producto_nombre"
                          />
                          <span v-else class="vp-thumb-fallback">
                            {{ (order.producto_nombre || 'P').charAt(0) }}
                          </span>
                        </div>
                        <div class="vp-product-text">
                          <span class="vp-product-name">{{ order.producto_nombre || 'Sin nombre' }}</span>
                          <span class="vp-product-pkg">{{ order.paquete?.nombre || '—' }}</span>
                        </div>
                      </div>
                    </td>

                    <!-- Col 2: Cliente -->
                    <td class="vp-td">
                      <span class="vp-cell-primary">{{ order.nombre || '—' }}</span>
                      <span class="vp-cell-secondary">{{ order.identificacion || '—' }}</span>
                    </td>

                    <!-- Col 3: Referencia -->
                    <td class="vp-td">
                      <span class="vp-cell-mono">TRX-{{ order.id_transaccion }}</span>
                    </td>

                    <!-- Col 4: Fecha -->
                    <td class="vp-td">
                      <span class="vp-cell-secondary">{{ fDate(order.fecha_pedido) }}</span>
                    </td>

                    <!-- Col 5: Cantidad -->
                    <td class="vp-td">
                      <span class="vp-cell-qty">×{{ order.cupos ?? 1 }}</span>
                    </td>

                    <!-- Col 6: Estado Badge -->
                    <td class="vp-td">
                      <span class="vp-badge" :class="getBadge(order.estado).cls">
                        <span class="vp-badge-dot" :style="{ background: getBadge(order.estado).dot }"></span>
                        {{ getBadge(order.estado).text }}
                      </span>
                    </td>

                    <!-- Col 7: Acciones -->
                    <td class="vp-td" style="text-align:center;">
                      <div class="row-menu-wrapper">
                        <button
                          class="vp-more-btn"
                          :id="`row-menu-btn-${order.id_detalle}`"
                          @click.stop="toggleMenu(order.id_detalle)"
                          :aria-expanded="activeMenu === order.id_detalle"
                          title="Acciones"
                        >
                          <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor">
                            <circle cx="12" cy="5" r="1.6"/><circle cx="12" cy="12" r="1.6"/><circle cx="12" cy="19" r="1.6"/>
                          </svg>
                        </button>

                        <!-- Dropdown -->
                        <transition name="menu-fade">
                          <div
                            v-if="activeMenu === order.id_detalle"
                            class="vp-dropdown"
                            role="menu"
                            @click.stop
                          >
                            <template v-if="getNext(order.estado)">
                              <button
                                class="vp-dd-item vp-dd-item--accent"
                                @click="actualizarEstado(order, getNext(order.estado))"
                                role="menuitem"
                              >
                                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
                                Avanzar a "{{ getNext(order.estado) }}"
                              </button>
                              <div class="vp-dd-divider"></div>
                            </template>
                            <button class="vp-dd-item" @click="closeMenu" role="menuitem">
                              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/></svg>
                              Ver detalles del pedido
                            </button>
                          </div>
                        </transition>
                      </div>
                    </td>
                  </tr>

                </tbody>
              </table>
            </div>

            <!-- ── PAGINATION ──────────────────────────────────────────── -->
            <div class="vp-pagination">
              <p class="vp-page-info">
                Mostrando <strong>{{ startRow }}–{{ endRow }}</strong> de <strong>{{ totalRows }}</strong> registros
              </p>
              <div class="vp-page-controls">
                <label class="vp-page-label" for="rows-per-page">Filas por página:</label>
                <select v-model="perPage" class="vp-per-page" id="rows-per-page" @change="currentPage = 1">
                  <option :value="5">5</option>
                  <option :value="10">10</option>
                  <option :value="25">25</option>
                  <option :value="50">50</option>
                </select>
                <div class="vp-page-nav">
                  <button class="vp-page-btn" :disabled="currentPage <= 1" @click="currentPage = 1" title="Primera página">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M11 17l-5-5 5-5M18 17l-5-5 5-5"/></svg>
                  </button>
                  <button class="vp-page-btn" :disabled="currentPage <= 1" @click="currentPage--" title="Anterior">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M15 18l-6-6 6-6"/></svg>
                  </button>
                  <span class="vp-page-display">{{ currentPage }} / {{ totalPages }}</span>
                  <button class="vp-page-btn" :disabled="currentPage >= totalPages" @click="currentPage++" title="Siguiente">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M9 18l6-6-6-6"/></svg>
                  </button>
                  <button class="vp-page-btn" :disabled="currentPage >= totalPages" @click="currentPage = totalPages" title="Última página">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M13 17l5-5-5-5M6 17l5-5-5-5"/></svg>
                  </button>
                </div>
              </div>
            </div>

          </div><!-- /vp-surface -->
        </template>
      </main>
    </div><!-- /vp-right -->
  </div><!-- /vp-shell -->
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ═══════════════════════════════════════════════════════════
   DESIGN TOKENS — Dark Provider Theme
═══════════════════════════════════════════════════════════ */
.vp-shell {
  --bg:          #07100d;
  --surface:     #0d1512;
  --surface-2:   #131c18;
  --surface-3:   #192320;
  --sidebar-bg:  #0a120f;
  --border:      #1d2e25;
  --border-2:    #253c2e;
  --accent:      #00d68f;
  --accent-dim:  rgba(0, 214, 143, 0.07);
  --accent-glow: rgba(0, 214, 143, 0.2);
  --text-1:      #dff0e8;
  --text-2:      #7a9b87;
  --text-3:      #3e5a4a;
  --font:        'Inter', system-ui, -apple-system, sans-serif;
  /* Semantic tokens */
  --c-success: #4ade80; --bg-success: rgba(74,222,128,0.08);
  --c-warn:    #fbbf24; --bg-warn:    rgba(251,191,36,0.08);
  --c-info:    #60a5fa; --bg-info:    rgba(96,165,250,0.08);
  --c-error:   #f87171; --bg-error:   rgba(248,113,113,0.08);
  --c-neutral: #9ba8a0; --bg-neutral: rgba(155,168,160,0.08);

  display: flex;
  height: 100vh;
  overflow: hidden;
  background: var(--bg);
  font-family: var(--font);
  color: var(--text-1);
  font-size: 14px;
}

/* ═══ SIDEBAR ════════════════════════════════════════════ */
.vp-sidebar {
  width: 234px;
  min-width: 234px;
  height: 100vh;
  background: var(--sidebar-bg);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  flex-shrink: 0;
}

/* Logo */
.vp-logo {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 18px 18px 16px;
  border-bottom: 1px solid var(--border);
}
.vp-logo-icon {
  width: 34px;
  height: 34px;
  background: var(--accent-dim);
  border: 1px solid rgba(0, 214, 143, 0.14);
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.vp-logo-brand {
  font-size: 12.5px;
  font-weight: 700;
  color: var(--text-1);
  line-height: 1;
  margin-bottom: 3px;
}
.vp-logo-role {
  font-size: 9.5px;
  color: var(--text-3);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Nav */
.vp-nav {
  flex: 1;
  padding: 14px 10px;
  overflow-y: auto;
}
.vp-nav-heading {
  font-size: 9px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-3);
  padding: 0 8px;
  margin-bottom: 8px;
}
.vp-nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 10px;
  border-radius: 8px;
  margin-bottom: 2px;
  text-decoration: none;
  color: var(--text-2);
  font-size: 13px;
  font-weight: 500;
  transition: background 0.14s, color 0.14s;
  border-left: 2.5px solid transparent;
  position: relative;
}
.vp-nav-item:hover {
  background: rgba(255, 255, 255, 0.035);
  color: var(--text-1);
}
.vp-nav-item.is-active {
  background: var(--accent-dim);
  color: var(--accent);
  font-weight: 700;
  border-left-color: var(--accent);
}
.vp-nav-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  flex-shrink: 0;
  opacity: 0.75;
}
.vp-nav-item.is-active .vp-nav-icon { opacity: 1; }
.vp-nav-label { flex: 1; }
.vp-nav-badge {
  font-size: 10px;
  font-weight: 800;
  background: var(--accent);
  color: #050e0a;
  border-radius: 10px;
  padding: 1px 6px;
  min-width: 18px;
  text-align: center;
}

/* Sidebar Footer */
.vp-sidebar-footer {
  padding: 14px 12px;
  border-top: 1px solid var(--border);
}
.vp-user-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 10px;
  background: var(--surface-2);
  border-radius: 9px;
  border: 1px solid var(--border);
}
.vp-user-avatar {
  width: 30px;
  height: 30px;
  border-radius: 7px;
  background: linear-gradient(135deg, var(--accent) 0%, #009966 100%);
  color: #050e0a;
  font-size: 13px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.vp-user-name {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-1);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 130px;
}
.vp-user-role {
  font-size: 10px;
  color: var(--text-3);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

/* ═══ RIGHT PANEL ════════════════════════════════════════ */
.vp-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}

/* TOP BAR */
.vp-topbar {
  height: 54px;
  display: flex;
  align-items: center;
  padding: 0 22px;
  gap: 18px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
.vp-breadcrumbs {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  flex-shrink: 0;
}
.vp-bc-link {
  color: var(--text-2);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.14s;
}
.vp-bc-link:hover { color: var(--text-1); }
.vp-bc-sep { color: var(--text-3); display: flex; align-items: center; }
.vp-bc-current { color: var(--text-1); font-weight: 600; }

.vp-topbar-search {
  flex: 1;
  max-width: 360px;
  margin: 0 auto;
  position: relative;
  display: flex;
  align-items: center;
}
.vp-topbar-search svg {
  position: absolute;
  left: 11px;
  color: var(--text-3);
  pointer-events: none;
}
.vp-topbar-input {
  width: 100%;
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 7px 12px 7px 34px;
  font-size: 12.5px;
  color: var(--text-1);
  outline: none;
  font-family: var(--font);
  transition: border-color 0.18s;
}
.vp-topbar-input::placeholder { color: var(--text-3); }
.vp-topbar-input:focus { border-color: var(--accent); }

.vp-topbar-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-left: auto;
}
.vp-icon-btn {
  width: 32px;
  height: 32px;
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 7px;
  color: var(--text-2);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.14s;
}
.vp-icon-btn:hover { background: var(--surface-3); color: var(--text-1); }
.vp-avatar-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--accent) 0%, #009966 100%);
  color: #050e0a;
  font-size: 12.5px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  flex-shrink: 0;
}

/* ═══ CANVAS ════════════════════════════════════════════ */
.vp-canvas {
  flex: 1;
  overflow-y: auto;
  padding: 22px;
  background: var(--bg);
}

/* Loading */
.vp-loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  height: 300px;
  color: var(--text-2);
  font-size: 13px;
  font-weight: 500;
}
.vp-spinner {
  width: 30px;
  height: 30px;
  border: 2px solid var(--border-2);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: vp-spin 0.75s linear infinite;
}
@keyframes vp-spin { to { transform: rotate(360deg); } }

/* ═══ SURFACE ════════════════════════════════════════════ */
.vp-surface {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  box-shadow: 0 4px 28px rgba(0, 0, 0, 0.28), 0 1px 0 rgba(255, 255, 255, 0.015) inset;
  overflow: hidden;
}

/* VIEW HEADER */
.vp-view-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 22px 26px;
  border-bottom: 1px solid var(--border);
  gap: 14px;
}
.vp-view-title {
  font-size: 19px;
  font-weight: 700;
  color: var(--text-1);
  letter-spacing: -0.025em;
  margin-bottom: 3px;
}
.vp-view-subtitle {
  font-size: 12px;
  color: var(--text-2);
  font-weight: 400;
}
.vp-btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  background: var(--accent);
  color: #05100d;
  border: none;
  border-radius: 8px;
  padding: 9px 16px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  font-family: var(--font);
  transition: transform 0.15s, box-shadow 0.15s;
  white-space: nowrap;
  flex-shrink: 0;
}
.vp-btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 18px var(--accent-glow);
}

/* FILTER BAR */
.vp-filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 22px;
  border-bottom: 1px solid var(--border);
  gap: 14px;
  flex-wrap: wrap;
  min-height: 50px;
}

/* Tabs */
.vp-tabs {
  display: flex;
  align-items: stretch;
  overflow-x: auto;
  scrollbar-width: none;
}
.vp-tabs::-webkit-scrollbar { display: none; }

.vp-tab {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 13px 15px 12px;
  font-size: 12.5px;
  font-weight: 500;
  color: var(--text-2);
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  font-family: var(--font);
  transition: all 0.14s;
  white-space: nowrap;
  position: relative;
  top: 1px;
}
.vp-tab:hover { color: var(--text-1); }
.vp-tab.is-active {
  color: var(--accent);
  font-weight: 600;
  border-bottom-color: var(--accent);
}
.vp-tab-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 20px;
  font-size: 10px;
  font-weight: 700;
  padding: 1px 7px;
  color: var(--text-2);
  min-width: 20px;
  transition: all 0.14s;
}
.vp-tab.is-active .vp-tab-count {
  background: var(--accent-dim);
  border-color: rgba(0, 214, 143, 0.18);
  color: var(--accent);
}

/* Search Box */
.vp-search-box {
  display: flex;
  align-items: center;
  gap: 7px;
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 6px 10px;
  width: 250px;
  flex-shrink: 0;
  transition: border-color 0.18s;
}
.vp-search-box:focus-within { border-color: rgba(0,214,143,0.4); }
.vp-search-box svg { color: var(--text-3); flex-shrink: 0; }
.vp-search-input {
  flex: 1;
  background: none;
  border: none;
  outline: none;
  font-size: 12px;
  color: var(--text-1);
  font-family: var(--font);
  min-width: 0;
}
.vp-search-input::placeholder { color: var(--text-3); }
.vp-clear-search {
  background: none;
  border: none;
  color: var(--text-3);
  cursor: pointer;
  display: flex;
  padding: 2px;
  transition: color 0.14s;
  flex-shrink: 0;
}
.vp-clear-search:hover { color: var(--c-error); }

/* ═══ TABLE ══════════════════════════════════════════════ */
.vp-table-wrap { overflow-x: auto; }
.vp-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 780px;
}

.vp-th {
  padding: 10px 18px;
  font-size: 10.5px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.065em;
  color: var(--text-2);
  text-align: left;
  background: var(--surface-2);
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
  user-select: none;
}
.vp-th--sort { cursor: pointer; }
.vp-th--sort:hover { color: var(--text-1); }
.vp-th--sort > span:first-child {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}
.vp-sort-icon {
  display: inline-flex;
  color: var(--text-3);
  transition: color 0.14s;
}
.vp-sort-icon.--active { color: var(--accent); }
.vp-sort-icon.--active.--asc svg { transform: scaleY(-1); }

.vp-row {
  border-bottom: 1px solid var(--border);
  transition: background 0.11s;
}
.vp-row:last-child { border-bottom: none; }
.vp-row:hover { background: rgba(0, 214, 143, 0.022); }

.vp-td {
  padding: 15px 18px;
  vertical-align: middle;
}

/* Product cell */
.vp-cell-product {
  display: flex;
  align-items: center;
  gap: 11px;
}
.vp-thumb {
  width: 38px;
  height: 38px;
  border-radius: 8px;
  overflow: hidden;
  background: var(--surface-3);
  border: 1px solid var(--border);
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
.vp-thumb img { width: 100%; height: 100%; object-fit: cover; }
.vp-thumb-fallback {
  font-size: 15px;
  font-weight: 800;
  color: var(--accent);
}
.vp-product-text { min-width: 0; }
.vp-product-name {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-1);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 170px;
}
.vp-product-pkg {
  display: block;
  font-size: 11px;
  color: var(--text-3);
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 170px;
}

/* Cell variants */
.vp-cell-primary {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-1);
}
.vp-cell-secondary {
  display: block;
  font-size: 11px;
  color: var(--text-2);
  margin-top: 2px;
}
.vp-cell-mono {
  font-size: 11.5px;
  font-family: 'Fira Code', 'Cascadia Code', ui-monospace, monospace;
  color: var(--accent);
  background: var(--accent-dim);
  padding: 3px 8px;
  border-radius: 5px;
  white-space: nowrap;
}
.vp-cell-qty {
  display: inline-flex;
  align-items: center;
  font-size: 12px;
  font-weight: 700;
  color: var(--text-2);
  background: var(--surface-2);
  border: 1px solid var(--border);
  padding: 3px 9px;
  border-radius: 5px;
}

/* ═══ BADGES ══════════════════════════════════════════════ */
.vp-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
  letter-spacing: 0.01em;
}
.vp-badge-dot {
  width: 5.5px;
  height: 5.5px;
  border-radius: 50%;
  flex-shrink: 0;
}
.badge-success { background: var(--bg-success); color: var(--c-success); }
.badge-warn    { background: var(--bg-warn);    color: var(--c-warn); }
.badge-info    { background: var(--bg-info);    color: var(--c-info); }
.badge-error   { background: var(--bg-error);   color: var(--c-error); }
.badge-neutral { background: var(--bg-neutral); color: var(--c-neutral); }

/* ═══ ROW ACTIONS ════════════════════════════════════════ */
.row-menu-wrapper { position: relative; display: inline-block; }
.vp-more-btn {
  width: 30px;
  height: 30px;
  border-radius: 7px;
  background: none;
  border: 1px solid transparent;
  color: var(--text-3);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.14s;
}
.vp-more-btn:hover {
  background: var(--surface-2);
  border-color: var(--border);
  color: var(--text-1);
}

.vp-dropdown {
  position: absolute;
  right: 0;
  top: calc(100% + 6px);
  width: 218px;
  background: var(--surface-2);
  border: 1px solid var(--border-2);
  border-radius: 10px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.45), 0 2px 8px rgba(0,0,0,0.2);
  z-index: 100;
  overflow: hidden;
  padding: 4px;
}
.vp-dd-item {
  display: flex;
  align-items: center;
  gap: 9px;
  width: 100%;
  padding: 9px 11px;
  background: none;
  border: none;
  border-radius: 7px;
  cursor: pointer;
  font-size: 12.5px;
  font-weight: 500;
  color: var(--text-1);
  font-family: var(--font);
  text-align: left;
  transition: background 0.11s;
}
.vp-dd-item:hover { background: var(--surface-3); }
.vp-dd-item--accent { color: var(--accent); }
.vp-dd-item--accent:hover { background: var(--accent-dim); }
.vp-dd-divider { height: 1px; background: var(--border); margin: 3px 4px; }

.menu-fade-enter-active, .menu-fade-leave-active { transition: opacity 0.11s, transform 0.11s; }
.menu-fade-enter-from, .menu-fade-leave-to { opacity: 0; transform: translateY(-4px) scale(0.97); }

/* ═══ EMPTY STATE ════════════════════════════════════════ */
.vp-empty-row td { padding: 0; }
.vp-empty-state { padding: 56px 24px; text-align: center; }
.vp-empty-icon-wrap {
  width: 52px;
  height: 52px;
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 14px;
  color: var(--text-3);
}
.vp-empty-title {
  font-size: 14px;
  font-weight: 700;
  color: var(--text-1);
  margin-bottom: 5px;
}
.vp-empty-text { font-size: 12px; color: var(--text-2); }

/* ═══ PAGINATION ══════════════════════════════════════════ */
.vp-pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 13px 22px;
  border-top: 1px solid var(--border);
  gap: 14px;
  flex-wrap: wrap;
}
.vp-page-info { font-size: 12px; color: var(--text-2); }
.vp-page-info strong { color: var(--text-1); font-weight: 600; }
.vp-page-controls { display: flex; align-items: center; gap: 10px; }
.vp-page-label { font-size: 12px; color: var(--text-2); white-space: nowrap; }
.vp-per-page {
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 5px 26px 5px 9px;
  font-size: 12px;
  color: var(--text-1);
  outline: none;
  cursor: pointer;
  font-family: var(--font);
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='10' viewBox='0 0 24 24' fill='none' stroke='%237a9b87' stroke-width='2.5'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 7px center;
}
.vp-page-nav { display: flex; align-items: center; gap: 3px; }
.vp-page-btn {
  width: 30px;
  height: 30px;
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 7px;
  color: var(--text-2);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.14s;
}
.vp-page-btn:hover:not(:disabled) {
  background: var(--surface-3);
  color: var(--text-1);
  border-color: var(--border-2);
}
.vp-page-btn:disabled { opacity: 0.3; cursor: not-allowed; }
.vp-page-display {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-1);
  padding: 0 10px;
  min-width: 56px;
  text-align: center;
}

/* ═══ SCROLLBARS ══════════════════════════════════════════ */
.vp-canvas::-webkit-scrollbar { width: 5px; }
.vp-canvas::-webkit-scrollbar-track { background: transparent; }
.vp-canvas::-webkit-scrollbar-thumb { background: var(--border-2); border-radius: 10px; }
.vp-table-wrap::-webkit-scrollbar { height: 4px; }
.vp-table-wrap::-webkit-scrollbar-track { background: transparent; }
.vp-table-wrap::-webkit-scrollbar-thumb { background: var(--border); border-radius: 10px; }

/* ═══ RESPONSIVE ══════════════════════════════════════════ */
@media (max-width: 860px) {
  .vp-sidebar { display: none; }
  .vp-topbar-search { max-width: 230px; }
}
@media (max-width: 620px) {
  .vp-canvas { padding: 12px; }
  .vp-view-header { flex-direction: column; align-items: flex-start; }
  .vp-filter-bar { flex-direction: column; align-items: flex-start; padding: 12px 14px; }
  .vp-search-box { width: 100%; }
  .vp-pagination { flex-direction: column; align-items: flex-start; }
  .vp-topbar-search { display: none; }
}
</style>
