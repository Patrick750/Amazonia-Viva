// src/config/navigation.js
export const navegacion = {
  turista: [
    { label: 'Inicio', path: '/panel' },
    { label: 'Catálogo', path: '/panel/catalogo' },
    { label: 'Mis Reservas', path: '/panel/reservas' },
    { label: 'Mis Experiencias', path: '/panel/experiencias' }
  ],
  agencia: [
    { label: 'Inicio', path: '/' },
    { label: 'Catálogo', path: '/panel/catalogo' },
    { label: 'Mis compras', path: '/panel/compras' },
    { label: 'Dashboard', path: '/panel/dashboard' }
  ],
  proveedor: [
    { label: 'Inicio', path: '/panel' },
    { label: 'Catálogo', path: '/panel/catalogo' },
    { label: 'Dashboard', path: '/panel/dashboard' }
  ],
  invitado: [
    { label: 'Inicio', path: '/panel'},
    { label: 'Catalogo', path: '/panel/catalogo'}
  ]
}