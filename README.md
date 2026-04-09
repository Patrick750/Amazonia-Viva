# 🌿 Amazonia Viva

Plataforma web para la gestión y oferta de turismo amazónico. Conecta agencias, proveedores y turistas mediante una interfaz multi-rol con autenticación, paquetes turísticos y gestión de ventas.

## Problema y objetivos
Amazonia viva nace de la idea de integrar uns plataforma donde los turistas puedan encontrar paquetes turísticos y productos relacionados con el turismo amazónico, y las agencias puedan ofrecer sus servicios y productos a los turistas. Existen muchas agencias turisticas poco conocidas en el sur del pais, por lo que se busca darles visibilidad y ofrecer sus servicios a los turistas.



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
 
### 3.9.0 — Persistencia de Cantidades y Consistencia de Cupos
> Archivos: `models.py`, `views.py`, `serializers.py`, `useCarrito.js`, `pago.vue`

- **[Feature] Persistencia de Cantidades**: El carrito ahora soporta el campo `cantidad` en la base de datos, asegurando que el número de personas seleccionadas no se pierda al recargar la página o navegar por la plataforma.
- **[Fix] Suma de Cupos por Fecha**: Se corrigió el cálculo de disponibilidad para realizar una suma real de cupos ocupados (`Sum('cantidad')`) en lugar de contar registros únicos, garantizando precisión cuando un turista reserva para múltiples acompañantes.
- **[UX] Sincronización Reactiva**: Implementación de sincronización automática vía `PATCH` cada vez que el usuario ajusta la cantidad en el carrito, manteniendo el estado global siempre actualizado en el servidor.
- **[Fix] Paridad en Pasarela de Pago**: Resolución del error de referencia circular en la selección de ítems, permitiendo que productos físicos y tours digitales se procesen en la misma transacción sin conflictos de importación.
> Archivos: `useCarrito.js`, `carrito.vue`, `detalle-paquete.vue`, `checkout-viajeros.vue`, `serializers.py`

- **[Feature] Traslado de Fecha al Carrito**: La elección de la fecha de reserva se movió de la vista de detalle al carrito, permitiendo una planificación más flexible antes del pago.
- **[Feature] Una Fecha por Unidad**: Se desactivó la agrupación de paquetes en el carrito. Ahora cada unidad añadida mantiene su propio selector de fecha independiente, ideal para grupos con itinerarios distintos.
- **[Security] Bloqueo Estricto de 7 Días**: Implementación de restricción automática que impide seleccionar fechas para el día actual y los 7 días siguientes, garantizando el tiempo mínimo de operación requerido.
- **[Architecture] Gestión por UUID**: Integración de identificadores únicos universales para cada ítem del carrito, asegurando que las actualizaciones de fecha y eliminaciones sean precisas incluso con ítems duplicados.
- **[UX] Confirmación en Checkout**: Inclusión de la fecha seleccionada en el resumen lateral del registro de viajeros, brindando visibilidad total durante todo el proceso de compra.
- **[Optimization] Backend Metadata**: El serializador de ítems de carrito ahora entrega metadatos sobre el tipo de paquete (fijo/flexible) para adaptar la interfaz dinámicamente.

### 3.7.0 — Métricas de Negocio y Filtros Avanzados (SCRUM-58, SCRUM-59)
> Archivos: `serializers.py`, `catalogo.vue`, `perfil-empresa.vue`, `detalle-paquete.vue`, `detalle-producto.vue`

- **[Feature] Analítica de Ventas en Tiempo Real (SCRUM-58)**: Integración de métricas de `ventas_totales` en todos los serializadores de catálogo y detalles. Ahora las agencias y proveedores pueden monitorizar el éxito de sus items directamente desde sus tablas de gestión.
- **[Feature] Resumen de Rendimiento de Negocio**: Adición de una tarjeta de estadísticas en el perfil de empresa que muestra el total acumulado de ventas, proporcionando una visión global inmediata del desempeño comercial.
- **[UX/UI] Filtro por Calificación (SCRUM-59)**: Implementación de un selector de estrellas reactivo ("4+ Estrellas", etc.) mediante chips visuales de color ámbar, permitiendo a los turistas filtrar por calidad percibida.
- **[UX] Ordenamiento por Popularidad**: Nueva opción de ordenamiento por "Más vendidos" que utiliza los datos agregados para destacar los productos y tours con mayor tracción en la plataforma.
- **[UI] Social Proof Inmersivo**: Los indicadores de ventas ("X vendidos") ahora son visibles en las tarjetas públicas del catálogo y en las vistas de detalle, reforzando la confianza del comprador.
- **[FIX] Visibilidad de Cambios**: Optimización de la lógica de renderizado para mostrar "0 vendidos" en items nuevos, asegurando que la funcionalidad sea visible desde el primer momento.

### 3.6.0 — Perfiles Públicos, Navegación Contextual y Verificación Legal
> Archivos: `perfil-publico.vue`, `VistaPerfilPublico.vue`, `tarjeta-tour.vue`, `tarjeta-producto.vue`, `serializers.py`, `views.py`

- **[Feature] Perfiles Públicos Universales**: Implementación de una vista unificada (`/perfil/:id`) para visualizar la identidad de cualquier usuario (Agencia, Proveedor o Turista) con diseño premium adaptativo.
- **[Feature] Catálogo Integrado en Perfil**: Los perfiles comerciales (Agencia/Proveedor) ahora proyectan sus productos y tours activos directamente, utilizando las tarjetas estándar del catálogo para mantener la paridad visual.
- **[Feature] Insignias de Legalidad**: Sistema de validación visual automática: "Verificación legal" (verde) para empresas con NIT/RUT/RNT registrado y "Sin verificar" (rojo) para perfiles en proceso de formalización.
- **[UX] Navegación de "Valla a Valla"**: Integración de enlaces profundos en los nombres de agencias y proveedores dentro de las vistas de detalle (`detalle-paquete`, `detalle-producto`), permitiendo una exploración fluida de la oferta de cada autor.
- **[Architecture] Paridad de Datos API**: Extensión de los endpoints de catálogo (`/api/catalogo/`) para soportar filtrado por ID de empresa, asegurando que la información de riesgo, estrellas y portadas sea idéntica en todas las vistas.
- **[UI/UX] Optimización de Grid**: Expansión del contenedor de ítems a `max-w-7xl` y retiro de botones transaccionales ("Añadir") en favor de una experiencia de exploración ("Ver +") coherente con un perfil de presentación.
 
### 3.5.0 — Seguridad de Datos Legales y Unificación de Perfiles
> Archivos: `models.py`, `serializers.py`, `InformacionAvanzada.vue`, `perfil-empresa.vue`, `views.py`

- **[Security] Inmutabilidad de Documentos**: Implementación de bloqueo estricto para NIT, RUT y RNT después de su registro inicial, previniendo modificaciones no autorizadas en perfiles de Agencia y Proveedor.
- **[UX] Registro Atómico con Verificación**: El proceso de verificación ahora registra automáticamente el documento en la base de datos de la plataforma al ser validado por el sistema mock, eliminando pasos redundantes para el usuario.
- **[Feature] Paridad de Perfil Proveedor**: Extensión de los campos de "Información Básica" (Descripción, Horario de Atención y Redes Sociales) al rol de Proveedor, igualando su capacidad de personalización con las Agencias.
- **[Security] Acceso Protegido**: Implementación de un modal de seguridad con validación de contraseña para acceder a la pestaña de "Información Avanzada", protegiendo datos sensibles.
- **[Feature] Ciclo de Vida RNT**: Ampliación del periodo de vigencia de la verificación del RNT a 30 días (1 mes), con un sistema de cuenta regresiva y estados visuales (Vigente/Por Renovar).
- **[Architecture] Sincronización Reactiva**: Refactorización de la comunicación entre componentes de perfil utilizando `v-model` y eventos personalizados para garantizar la integridad de los datos en tiempo real.

### 3.4.3 — Configuración de Entorno de Producción Gunicorn / Render
> Archivos: `settings.py`, `requirements.txt`, `build.sh`

- **[Feature] Configuración de Seguridad y Host Dinámica**: Ajustes para Render de las configuraciones de `ALLOWED_HOSTS` y `DEBUG`, ahora condicionados estrictamente a la existencia de variables de entorno pasadas por el servidor. 
- **[Architecture] WhiteNoise Middleware**: Agregada la librería e inyección en la capa de seguridad de Django permitiendo el servicio eficiente de archivos estáticos sobre un sistema manejado con Gunicorn.  
- **[Tooling] Automatización de Build**: Se integró en la base del proyecto `build.sh`, encargado de la descarga limpia de dependencias, recolección de estáticos en almacenamiento virtual y la automatización de migraciones en cada *deploy*.

---
### 3.4.2 — Centralización de Cliente HTTP y Rutas Dinámicas
> Archivos: `login.vue`, `signup.vue`, `paneles.vue`, `axios.js`

- **[Refactor] Variables de Entorno**: Configuración dinámica de URL de API para transición local/producción.
- **[Architecture] Centralización Axios**: Se reemplazaron las instancias de `axios` puro por la global `clienteAxios`.
- **[Security] Rutas Relativas**: Eliminación de URLs hardcodeadas (`http://127.0.0.1:8000`) en toda la aplicación.

---
### 3.4.1 — Aislamiento de Carrito y Sincronización Backend (Bugfix)
> Archivos: `views.py`, `serializers.py`, `useCarrito.js`, `header.vue`, `useCatalogo.js`

- **[Fix] Aislamiento por Cuenta**: Se eliminó la filtración de ítems entre usuarios al cambiar de cuenta. Ahora el `localStorage` utiliza claves dinámicas vinculadas al email del usuario.
- **[Feature] Sincronización de Persistencia**: Implementación de sincronización bidireccional con el backend. Los ítems se guardan en la base de datos y se recuperan automáticamente al iniciar sesión, permitiendo que el carrito sobreviva a la limpieza del navegador.
- **[Feature] Gestión de Ítems via API**: Nuevos endpoints `GET` (recuperar) y `DELETE` (eliminar) en el backend para permitir una gestión completa del carrito desde el servidor.
- **[UX/UI] Limpieza Automática**: Refactorización del flujo de logout para garantizar que el estado reactivo del carrito se resetee completamente antes de la siguiente sesión.

---
### 3.4.0 — Registro de Expedicionarios y Flujo de Checkout (SCRUM-43)

> Archivos: `checkout-viajeros.vue`, `router/index.js`, `carrito.vue`

- **[Feature] Registro de Viajeros**: Nueva interfaz de captura de datos para múltiples expedicionarios utilizando el principio de "Divulgación Progresiva" mediante acordeones interactivos.
- **[UX/UI] Acordeones de Seguimiento**: Los formularios se expanden y colapsan automáticamente al ser completados, mostrando indicadores visuales de éxito (checks verdes) y progreso real.
- **[Feature] Auto-rellenado Titular**: Opción para utilizar los datos del perfil del usuario logueado en el primer viajero con un solo clic.
- **[Architecture] Smart Routing**: El botón de pago en el carrito ahora redirige inteligentemente: si hay tours seleccionados, solicita datos de viajeros; si solo hay productos, avanza directo al pago.
- **[UI/UX] Navegación Intuitiva**: Incorporación de breadcrumbs de pasos (Carrito → Viajeros → Pago) y botones de retorno prominentes para reducir la fricción en el proceso de compra.

---

### 3.3.0 — Módulo de Carrito de Compras Persistente (SCRUM-43)
> Archivos: `carrito.vue`, `useCarrito.js`, `useCatalogo.js`, `header.vue`

- **[Feature] Gestión de Carrito Local**: Implementación de un sistema de carrito basado en `localStorage` que permite persistencia total entre sesiones de usuario (Turista/Agencia).
- **[Feature] Selección de Ítems**: Capacidad de seleccionar y deseleccionar ítems específicos para proceder al pago, con recálculo dinámico de subtotales por categoría (Tours/Productos).
- **[Feature] Desglose de Costos Inmersivo**: Panel de resumen de compra con desglose de subtotales, aporte ecológico (1% en tours) y indicadores de confianza (Trust Badges).
- **[UI/UX] Checkout Review Premium**: Nueva vista `/carrito` con diseño de alta conversión, estados vacíos motivacionales y separación visual clara entre expediciones y equipo técnico.
- **[Control] Gestión de Cupos y Unidades**: Selectores de cantidad reactivos para personas por tour y unidades por producto con límites de validación integrados.
- **[Fix] Persistencia en Logout**: Refactorización del cierre de sesión para limpiar credenciales de acceso manteniendo intacta la mochila del viajero (`carrito_amazonia`).

---
### 3.2.2 — Corrección de Visualización en Favoritos (SCRUM-44)
> Archivos: `serializers.py`, `favoritos.vue`

- **[Fix] Serialización de Atributos**: Mejora en la lógica de `get_descripcion` para procesar listas de características de productos, convirtiéndolas en texto legible (ej: "Marca: Nike") en lugar de mostrar código JSON.
- **[Fix] Sanitización de HTML**: Implementación de un selector de texto plano (stripping HTML) en las descripciones truncadas para evitar que etiquetas residuales se visualicen en las tarjetas de favoritos.
- **[UI/UX] Consistencia de Tarjetas**: Se eliminó el "ruido visual" de los ítems guardados, garantizando una interfaz limpia y profesional en la colección personal de aventuras del usuario.

---

### 3.2.1 — Filtro del Home Inteligente y Refactor de Datos Global
> Archivos: `useCatalogo.js`, `home.vue`

- **[Architecture] useCatalogo Singleton**: Refactorización del composable de catálogo a un patrón **Singleton Global**. Los datos de `tours` y `categoriasTours` ahora se comparten entre todas las vistas, eliminando problemas de reactividad y redundancia en peticiones API.
- **[Feature] Autocompletado de Destinos**: Implementación de un buscador predictivo en el Home. Sugiere ciudades reales extraídas de la base de datos mientras el usuario escribe, con soporte para selección táctil y mouse.
- **[Feature] Filtros Cruzados Home → Catálogo**: Sincronización total del buscador del Home con el Catálogo. Al explorar, se pasan los parámetros de búsqueda y categoría (grupos dinámicos) vía URL para resultados inmediatos.
- **[Performance] Caché de Memoria**: Las peticiones de tours y categorías ahora se realizan una sola vez por sesión, mejorando la velocidad de navegación entre el Home y el Catálogo.

---

### 3.2.0 — Rediseño Premium "Amazonia Viva" y Consistencia Visual
> Archivos: `home.vue`, `catalogo.vue`, `header.vue`

- **[UI/UX] Home "Inmensivo"**: Rediseño total de la página de inicio con estética premium. Incluye imágenes de alta resolución, decoraciones SVG animadas (hojas flotantes) y un sistema de "Hero" con búsqueda integrada para tours.
- **[UI/UX] Catálogo Forest**: Adaptación del catálogo de tours y productos a la nueva identidad visual oscura. Uso de **Glassmorphism** en paneles de filtrado y transiciones fluidas.
- **[UI/UX] Header Forest de Alta Visibilidad**: Nueva barra de navegación global con fondo sólido `#0f2318`, asegurando legibilidad total del texto y módulos en cualquier sección de la plataforma (blanca o oscura).
- **[Feature] Identidad por Rol**: Implementación de insignias (badges) de colores por rol de usuario (Turista, Agencia, Proveedor) y generación automática de iniciales de perfil.
- **[Architecture] Paleta de Colores Curada**: Migración de colores genéricos a una paleta cohesiva de verdes profundos, esmeralda y teal que refuerzan el branding del proyecto.

---

### 3.1.0 — Migración a Leaflet, Autocompletado Geográfico y Optimización de Mapas
> Archivos: `formulario.vue`, `detalle-paquete.vue`, `serializers.py`

- **[Architecture] Adiós Google Maps**: Migración completa de la API de Google Maps a **Leaflet (OpenStreetMap)**. Eliminación de dependencias de pago y scripts externos pesados.
- **[Feature] Geolocalización Nominatim**: Implementación de búsqueda por texto y **autocompletado en tiempo real** utilizando la API de Nominatim. Sugerencias inteligentes al escribir para una ubicación precisa.
- **[UI/UX] Mapa Dinámico y Expandible**: Nueva funcionalidad para ampliar el área del mapa (`50vh`) durante la creación de tours, facilitando la ubicación exacta en dispositivos móviles y escritorio.
- **[UX] Control de Interacción**: Implementación de `touch-action: none` en contenedores de mapas para evitar que el scroll de la página interfiera con el arrastre del mapa (panning).
- **[Fix] Precisión de Coordenadas**: Truncado automático a **6 decimales** en el frontend para cumplir con las restricciones de `max_digits=9` del backend de Django, eliminando errores `400 Bad Request`.
- **[Fix] Renderizado Asíncrono**: Uso de `nextTick` y `invalidateSize` para asegurar que el mapa se pinte correctamente dentro de modales y componentes dinámicos de Vue.

---

### 3.0.0 — Navegación Universal, Catálogo Híbrido y Persistencia de Filtros
> Archivos: `router/index.js`, `catalogo.vue`, `home.vue`, `navigation.js`, `detalle-paquete.vue`, `detalle-producto.vue`

- **[Architecture] Navegación Universal**: Eliminación de la redirección forzada a `/panel`. La raíz `/` es ahora el centro de la experiencia para todos los usuarios.
- **[Feature] Catálogo de Rutas Independientes**: Separación física de las vistas de **Tours** (`/catalogo/tours`) y **Productos** (`/catalogo/productos`), permitiendo una navegación más clara y SEO-friendly.
- **[Feature] Persistencia de Estado vía URL**: Implementación de sincronización de filtros (búsqueda, categorías, orden) con parámetros de consulta (`Query Parameters`). Esto permite que los filtros sobrevivan a la navegación "atrás" y puedan ser compartidos por enlace directo.
- **[Feature] Vista Híbrida para Invitados**: Los usuarios no autenticados ahora ven los productos divididos en secciones estratégicas (**Para Turistas** y **Para Agencias**) con iconografía profesional.
- **[UI/UX] Iconografía SVG Premium**: Migración de los últimos emojis decorativos a iconos vectoriales SVG en el buscador de la página de inicio y en los encabezados del catálogo de productos.
- **[Security] Blindaje de Rutas Privadas**: Refactorización del guardián de navegación (`router.beforeEach`) para restringir el acceso a rutas administrativas y paneles a usuarios no autenticados, redirigiéndolos de forma segura a la raíz.

---

### 3.0.1 — Mejoras de Agencia y Vista de Detalle Inmersiva
> Archivos: `header.vue`, `detalle-producto.vue`, `views.py`, `serializers.py`, `useCatalogo.js`

- **[Feature] Paridad de Agencia**: Extensión de las capacidades de compra y favoritos al rol de **Agencia**. Ahora las agencias disponen de iconos de carrito y favoritos en el navbar con navegación funcional y contadores reactivos.
- **[Feature] Vista de Detalle Inmersiva**: Rediseño completo de la ficha de producto con carrusel de imágenes de alta resolución, galería de miniaturas y gestión dinámica de especificaciones técnicas desde el modelo de datos.
- **[Feature] Serialización Profunda**: Implementación de `SerializerDetalleProducto` en el backend para exponer el conjunto completo de metadatos y galerías de imágenes, optimizando la carga de la vista de detalle.
- **[Security] Privacidad de Datos**: Implementación de visibilidad de datos por rol; el código **SKU** del producto es ahora información privada visible únicamente para el **Proveedor** propietario.
- **[Fix] Robustez de Especificaciones**: Mejora en el motor de renderizado del frontend para procesar estructuras de características tanto en formato de objeto como de lista, eliminando fallos de carga (infinite loading) por inconsistencia de datos.
- **[Fix] Mapeo de Galería**: Sincronización de las rutas de Cloudinary entre el backend y frontend, asegurando que todas las imágenes adicionales se visualicen correctamente en el carrusel.

---

### 2.8.0 — Catálogo Público, Detalle dinámico y Contadores Reactivos
> Archivos: `detalle-paquete.vue`, `header.vue`, `useUserStats.js`, `useCatalogo.js`, `models.py`, `views.py`, `urls.py`

- **[Feature] Catálogo Público**: Apertura del catálogo de tours y vista de detalles a usuarios no registrados (invitados) en rutas de libre acceso, con redirección automática al login ante acciones de compra.
- **[Feature] Detalle de Paquete Premium**: Nueva interfaz de detalles con galería interactiva, itinerario visual tipo timeline, lista de inclusiones y vinculación directa con Google Maps.
- **[Feature] Contadores Reactivos en Header**: Implementación de badges (burbujas) en el carrito y favoritos que se actualizan en tiempo real mediante un estado global reactivo (`useUserStats`).
- **[Security] Restricciones por Rol**: Los proveedores y agencias ahora tienen bloqueadas las acciones de "Agregar al Carrito/Favoritos" con retroalimentación visual (botones deshabilitados) y tooltips informativos.
- **[Fix] Precisión de Datos y Nulabilidad**: Resolución de errores de precisión en campos `Decimal` y ajuste de campos nulos en `Items` y `Favoritos` para permitir operaciones parciales (solo Paquete o solo Producto).
- **[Optimization] Deduplicación**: Refactorización de vistas para evitar registros duplicados en el carrito y favoritos, manteniendo los conteos del header precisos y únicos.

---

### 2.7.4 — Activación Global de Notificaciones y Gestión Avanzada
> Archivos: `App.vue`, `serializers_productos.py`, `tabla-productos.vue`

- **[Fix] Notificaciones Globales**: Activación del componente `Notificacion.vue` en la raíz del proyecto (`App.vue`), habilitando el feedback visual para todas las acciones administrativas del sistema.
- **[Feature] Panel de Gestión con Marca/Modelo**: Actualización de la tabla de administración de productos para mostrar la identidad completa (**Nombre - Marca Modelo**), manteniendo paridad visual con el catálogo público.

---

### 2.7.3 — Feedback de Usuario y Refinamiento de Interfaz
> Archivos: `formulario.vue`, `tarjeta-producto.vue`

- **[UX] Sistema de Notificaciones**: Integración de alertas visuales reactivas para confirmar el éxito de registros y actualizaciones, o mostrar detalles en caso de errores de red.
- **[UI/UX] Pulido de Identidad**: Refinamiento estético en la concatenación de **Nombre - Marca Modelo** en el catálogo, mejorando la legibilidad y el espaciado.

---

### 2.7.2 — Corrección de Autenticación en Gestión de Productos
> Archivos: `formulario.vue`, `eliminar-producto.vue`

- **[Fix] Seguridad en Registro**: Sincronización del cliente de red en el formulario de creación/edición. Se corrigió el error `403 Forbidden` al asegurar que el token JWT se envíe correctamente en las peticiones `POST` y `PUT`.
- **[Fix] Eliminación Protegida**: Actualización del componente de borrado para utilizar el canal autenticado, permitiendo que solo los propietarios legales puedan remover ítems del inventario.

---

### 2.7.1 — Búsqueda Extendida y Visualización de Marca/Modelo
> Archivos: `serializers.py`, `catalogo.vue`, `tarjeta-producto.vue`

- **[Feature] Búsqueda Inteligente**: Expansión del motor de búsqueda del catálogo para admitir múltiples términos simultáneos. Ahora puedes combinar **Nombre, Marca y Modelo** (ej: "Cámara Canon PowerShot") para obtener resultados exactos.
- **[UI/UX] Visualización de Datos**: Actualización de las tarjetas de producto para mostrar el nombre concatenado (**Nombre - Marca Modelo**), facilitando la identificación rápida de ítems técnicos.

---

### 2.7.0 — Optimización de Gestión de Productos y Seguridad de Acceso
> Archivos: `views_productos.py`, `serializers_productos.py`, `productos.vue`, `formulario.vue`, `tabla-productos.vue`, `catalogo.vue`

- **[Feature] Restricción de Acceso**: Implementación de políticas de privacidad donde cada proveedor solo visualiza y gestiona sus propios productos.
- **[Security] Verificación de Propiedad**: Protección en el backend (`IsAuthenticated` + `Ownership check`) para prevenir modificaciones no autorizadas entre cuentas de proveedores.
- **[Feature] Atributos Dinámicos**: Migración de la lógica de atributos "Técnicos" y "Generales" a la base de datos, permitiendo que el formulario se adapte automáticamente según la categoría seleccionada sin dependencias en el código.
- **[UI/UX] Legibilidad de Categorías**: Actualización de la tabla de gestión para mostrar el **Nombre de la Categoría** en lugar del ID, mejorando la experiencia administrativa.
- **[Bugfix] Reseteo de Filtros**: Corrección del error de persistencia en las pestañas del catálogo, asegurando que los filtros se limpien correctamente al navegar entre Tours y Productos.
- **[Fix] Persistencia de Sesión**: Sincronización del cliente `Axios` en la vista de productos para garantizar el envío del token JWT en todas las operaciones administrativas.

---

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
