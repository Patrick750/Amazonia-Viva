# 🌿 Amazonia Viva

Plataforma web para la gestión y oferta de turismo amazónico. Conecta agencias, proveedores y turistas mediante una interfaz multi-rol con autenticación, paquetes turísticos y gestión de ventas.

## 🛠️ Stack Tecnológico

- **Backend:** Django (Python 3.12) + Django REST Framework
- **Frontend:** Vue 3 + Vite + Vue Router
- **Base de datos:** PostgreSQL
- **Autenticación:** JWT / Sesiones Django
- **Servicios en la nube:** Cloudinary (Imágenes)
- **Control de versiones:** Git

---

## 📦 Historial de Versiones

> Formato: `MAYOR.MENOR.PARCHE` (`high.low.patch`)
>
> - **MAYOR** — cambio funcional significativo o rediseño arquitectónico
> - **MENOR** — nueva funcionalidad añadida
> - **PARCHE** — correcciones, ajustes menores o refactorizaciones

### 2.6.0 — Módulo de Catálogo Público y Filtrado Inteligente (SCRUM-40)
> Archivos: `catalogo.vue`, `tarjeta-tour.vue`, `tarjeta-producto.vue`, `formulario.vue`, `useCatalogo.js`, `views.py`, `serializers.py`, `urls.py`

- **[Feature] Vista de Catálogo**: Nueva vista `/panel/catalogo` accesible desde el header para todos los roles (turista, agencia, proveedor).
- **[Feature] Filtrado Global**: Panel de filtrado dinámico por **Grupo** y **Subcategoría** en la pestaña de Tours, con soporte para filtrado por grupo completo o categoría específica.
- **[Feature] Persistencia de Filtros**: Los filtros seleccionados se mantienen activos incluso al cambiar el criterio de ordenamiento (precio, calificación).
- **[Feature] Tabs Tours / Productos**: Navegación por pestañas que separa los paquetes turísticos de los productos del catálogo.
- **[Feature] Categorías Dinámicas**: Gestión de categorías en el formulario de productos vinculada al Seeder, permitiendo actualizaciones de catálogo en tiempo real.
- **[Feature] Buscador Reactivo**: Campo de búsqueda tipo píldora por nombre y agencia/proveedor con retroalimentación instantánea.
- **[UI/UX] Sticky Header**: Unificación de la lógica de cabecera fija (sticky) responsiva para una navegación fluida en todas las resoluciones.
- **[Optimization] Backend**: Implementación de `select_related` y `prefetch_related` para optimizar las consultas del catálogo, reduciendo significativamente el tiempo de respuesta.
- **[Feature] Tarjetas de Tour**: Componente `tarjeta-tour.vue` con galería, badges de riesgo, ubicación, duración y botón de detalles integrado.
- **[UI/UX] Navegación Inmersiva**: Implementación de lógica *Hide-on-Scroll* que oculta automáticamente los controles del catálogo al bajar y los revela al subir, maximizando el área de visualización.
- **[Refactor] Iconografía**: Migración total de emojis a íconos SVG vectoriales en tabs, chips de categoría y estados.

---

### 2.5.1 — Filtro de Estados en Catálogo de Productos
> Tarea: `SCRUM-52` | Archivo: `tabla-productos.vue`

- **[Feature] Filtro Reactivo de Estado**: Implementación de un selector desplegable para filtrar proactivamente productos por su disponibilidad (Todos, Activos, Inactivos) en la vista principal del catálogo.

---

### 2.5.0 — Dashboard Analítico y Control Integral de Productos
> Archivos: `productos.vue`, `formulario.vue`, `eliminar-producto.vue`, `seed_categorias_productos.py`

- **[Feature] Búsqueda Reactiva**: Implementación de un motor de búsqueda instantánea por Nombre de Producto o SKU sobre la grilla principal.
- **[Feature] Alertas de Stock**: Nuevo Widget lateral derecho para monitorizar e identificar automáticamente productos con niveles críticos de inventario (≤ 5).
- **[Feature] Eliminación Dinámica**: Creación del componente `eliminar-producto.vue` con un modal animado de "Candado de Seguridad Turística", erradicando las alertas nativas del navegador, finalizando con una petición `DELETE` segura al API.
- **[Feature] Rediseño de Categorías**: Reescritura completa del Seeder en Django y el mapeo en VueJS para orientar el catálogo estrictamente a perfiles de "Seguridad y Supervivencia" (p.ej. _Indumentaria Outdoor_, _Tecnología y Navegación_).
- **[Feature] Validaciones Estrictas**: Integración proactiva y segura del entorno de notificaciones Toaster en Vue para atrapar campos vacíos, características sin variables o pre-aprobación del precio superior a $0 localmente.

---

### 2.4.1 — Carrusel de Productos y Estabilización de Edición
> Archivos: `detalles-producto.vue`, `views_productos.py`, `serializers_productos.py`

- Implementación del Carrusel Infinito (Animación continua y track de clonación) homólogo al módulo de Tours dentro del visor de detalles de productos.
- **[Bugfix]** Resolución de alertas de subida omitiendo la cabecera forzada `multipart/form-data` de Axios para permitir inyección orgánica de boundaries en el navegador.
- **[Bugfix]** Parsing recursivo nativo en DRF de variables `FormData` (JSON strings y variables booleanas) estabilizando la técnica de edición de registros (`PUT`).
- **[Bugfix]** Bypass deliberado de la validación interna `Pillow` en serializers, permitiendo que formatos web asíncronos (`webp`, `avif`, `heic`) se suban nativamente y sin alertas a la API de Cloudinary.

---

### 2.4.0 — Módulo CRUD de Productos Integrado (API & Cloudinary)
> Archivos: `models.py`, `serializers_productos.py`, `views_productos.py`, `productos.vue`, `formulario.vue`, `detalles-producto.vue`

- Refactorización de la Vista de Productos con un diseño de UI avanzado (Modales dinámicos, Tablas, Estado Reactivo).
- Creación de Backend API bajo arquitectura SOLID para la gestión de inventario de `Productos`.
- Integración real con **Cloudinary** mediante el uso del modelo auxiliar `ProductoImagen` y envíos muti-part (`FormData`).
- Eliminación de la "Data Mock" e inyección de **Categorías Dinámicas** (Seed de DB con comando nativo).
- Reestructuración del Visor de Detalles (`detalles-producto.vue`) mostrando en tiempo real los metadatos `tipo_catalogo`, galerías miniatura y atributos JSON.

---

### 2.3.2 — Restricción de Gestión de Paquetes sólo para Agencias
> Tarea: `SCRUM-50` | Archivos: `dashboard.vue`, `router/index.js`

- Ocultamiento condicional (`v-if`) del botón "Gestionar Catálogo" en el dashboard para roles distintos a agencia.
- Protección de ruta en el guardián global `beforeEach` para `/panel/gestion-paquetes`, redirigiendo al panel principal a usuarios sin autorización.

---

### 2.3.1 — Corrección de modelos y configuración IDE
> Archivos: `autenticacion/models.py`, `.vscode/settings.json`

- Corrección de ortografía en el campo `caracteristicas` del modelo `Productos`
- Ajuste de límites válidos para `precio` (`DecimalField` con max_digits=12, decimal_places=2)
- Integración de entorno virtual (`venv`) para el IDE a través de `.vscode/settings.json`

---

### 2.3.0 — Carrusel infinito de imágenes en detalle de tour
> Rama: `SCRUM-33-Menu-principal-para-agencias` | Archivo: `detalles-tour.vue`

- Implementación de **carrusel infinito** (clone-and-jump) en el modal de detalle de paquete turístico
- El track incluye clones del primer y último slide para lograr un loop continuo sin corte visual
- Navegación con **flechas ‹ ›**, **dots indicadores** y **miniaturas** sincronizadas con el slide actual
- **Auto-avance** cada 4 segundos, reiniciable al navegar manualmente
- Carrusel activo solo cuando hay más de 1 imagen; imagen estática para 1 imagen; placeholder SVG si no hay imágenes
- Corrección visual: muestra la unidad `h` junto a la duración del paquete


> Rama: `SCRUM-33-Menu-principal-para-agencias` | Commits: `0e29361`, `c1c7903`, `876b62f`, `bb991d9` (HEAD)

- Corrección de errores en la base de datos y modelos relacionados
- Desarrollo iterativo del menú principal de navegación para agencias
- Avances en la integración de vistas de agencia

---

### 2.1.0 — Tablas de categorías y actividades
> Commit: `1493e8c`

- Añadidas tablas de **categorías** y **actividades** al modelado de datos
- Ampliación del esquema relacional para soportar clasificación de paquetes turísticos
- Avances de integración en el frontend (`paneles.vue`, `navigation.js`)

---

### 2.0.0 — Paquetes turísticos e interfaz de gestión de tours con geolocalización
> Commits: `83619f4`, `5e02b3f`, `806c737`, `6f1c423`, `787094e`, `3e9bd43`, `8f6afba`

**Nuevo módulo mayor — Gestión de Paquetes Turísticos:**

- Creación del módulo de **paquetes turísticos** (backend + frontend)
- Implementación de la interfaz de **gestión de tours** con integración de API para registro de ubicación exacta (geolocalización)
- Nuevas vistas y componentes Vue para administración de tours
- Múltiples iteraciones de avance e integración del módulo

---

### 1.7.0 — Modelado de gestión de ventas (SCRUM-49)
> Commits: `1316c18`, `d9f1737`, `8cf110d`, `f29a1c4`

- Modelado completo del módulo de **gestión de ventas** (SCRUM-49)
- Definición de modelos, migraciones y relaciones para el flujo de ventas
- Merge a rama principal (`main`)
- Cierre de tareas SCRUM-45 y SCRUM-46

---

### 1.6.0 — Dashboard multi-rol y actualización de logo
> Commits: `65d8202`, `91d7d55`, `33c21d1`, `c8fff3d`

- Interfaz de **dashboard** terminada con soporte multi-rol (agencia, proveedor, turista, visitante)
- Actualización del **logo** y branding del proyecto
- Paneles de control diferenciados por tipo de usuario

---

### 1.5.0 — Perfil de usuario, menú desplegable y cierre de sesión (SCRUM-45 / SCRUM-46)
> Commits: `b7ae1e8`, `3104273`, `197c53f`, `7c3538c`, `a16caa6`, `df7d139`, `1abd3e6`

- Implementación del **menú de perfil desplegable** con cierre de sesión (SCRUM-45, SCRUM-46)
- Integración del principio **SOLID** en el componente de encabezado (`header.vue`)
- Configuración de navegación por rol (`navigation.js`)
- Unificación de paneles en un componente `paneles.vue` reutilizable

---

### 1.4.0 — Encabezados por rol y mejora del login (SCRUM-38)
> Commits: `fba0938`, `2c1ca44`, `4872e56`

- Mejora del flujo de **login**: validaciones, UI y redirección por rol
- Creación de **encabezados diferenciados** por rol de usuario y visitante (SCRUM-38)
- Adición de componente `visitante.vue` para usuarios no autenticados
- Refactorización del router para rutas protegidas

---

### 1.3.0 — Inicio y validación de sesión (SCRUM-15)
> Commits: `c9815f1`, `0a6e82f`, `58547a1`

- Implementación completa del **inicio de sesión con validación** (SCRUM-15)
- Creación del módulo `axios.js` para comunicación con la API REST
- Corrección de serializers y vistas de autenticación en el backend
- Arreglos de registro y redirección post-login (SCRUM-14)

---

### 1.2.0 — Registro de usuarios por rol (SCRUM-14)
> Commits: `ca5a4e7`, `cd7ae61`, `07c801f`, `5be7531`

- **Registro completo** para roles agencia, proveedor y turista (SCRUM-14)
- Paneles de bienvenida diferenciados por rol (`panelagencia.vue`, `panelproveedor.vue`, `panelturista.vue`)
- Corrección de vistas y serializers del backend para registro multi-rol
- Arreglos menores de validación y flujo post-registro

---

### 1.1.0 — Registro de usuarios e integración del frontend Vue
> Commits: `06c77ab`, `b26ab9f`, `db21fa6`, `e87f5de`, `c49056b`

- Integración del **frontend Vue 3 + Vite** con el backend Django (REST API)
- Creación del proyecto Vue (`App.vue`, `router/index.js`, `signup.vue`, `login.vue`)
- Serializers y modelos de base de datos para el registro de usuarios
- Migración de plantillas Django a componentes Vue (eliminación de templates HTML clásicos)
- Configuración de CORS y ajustes en `settings.py`

---

### 1.0.0 — Inicialización del proyecto
> Commits: `a93bbfa`, `e99c488`

- Creación del proyecto **Django** con estructura base (`amazoniaviva/`, `autenticacion/`)
- Configuración inicial: `settings.py`, `urls.py`, `wsgi.py`, `asgi.py`
- Modelo inicial de usuario (`autenticacion/models.py`)
- Plantillas HTML de login y registro (versión inicial Django templates)
- Agregar `.gitignore` y `requirements.txt`

---

## 🚀 Instalación y Ejecución

### Backend (Django)
```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Aplicar migraciones
python manage.py makemigrations
python manage.py migrate

# Iniciar servidor
python manage.py seed_actividades
python manage.py seed_groups
python manage.py seed_categorias_paquetes
python manage.py runserver
```

### Frontend (Vue + Vite)
```bash
cd frontend_project

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo
npm run dev
```

---

## 📄 Licencia

Este proyecto fue desarrollado como parte de un proyecto académico/estudiantil.
