// src/config/navigation.js
export const navegacion = {
  turista: [
    { label: 'Inicio', path: '/' },
    { label: 'Catálogo', path: '/catalogo/tours' },
    { label: 'Mis Reservas', path: '/panel/reservas' },
    { label: 'Mis Experiencias', path: '/panel/mis-experiencias' },
    { label: 'Mis Productos', path: '/panel/mis-productos' }
  ],
  agencia: [
    { label: 'Inicio', path: '/' },
    { label: 'Catálogo', path: '/catalogo/tours' },
    { label: 'Mis compras', path: '/panel/compras' },
    { label: 'Dashboard', path: '/panel/dashboard' }
  ],
  proveedor: [
    { label: 'Inicio', path: '/' },
    { label: 'Catálogo', path: '/catalogo/tours' },
    { label: 'Gestión de Ventas', path: '/panel/gestion-ventas' },
    { label: 'Mis Productos', path: '/panel/productos' },
    { label: 'Dashboard', path: '/panel/dashboard' }
  ],
  invitado: [
    { label: 'Inicio', path: '/'},
    { label: 'Catálogo', path: '/catalogo/tours'}
  ]
}