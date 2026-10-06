# Plan de trabajo — Seguridad de Amazonia Viva

**Objetivo:** corregir los problemas de autorización, compras, credenciales y liquidaciones antes de habilitar operaciones reales.

**Duración estimada:** 8–12 días de trabajo para una persona, sujeta al alcance de la integración de pagos.

## 1. Contención inmediata

**Prioridad: crítica · Estimación: ½–1 día**

- Restringir temporalmente los endpoints de edición y eliminación de paquetes.
- Suspender compras y retiros reales mientras se corrigen sus validaciones.
- Rotar las credenciales expuestas de Cloudinary y la clave secreta de Django.
- Eliminar secretos del código y exigir variables de entorno, sin valores secretos predeterminados.
- Revisar el historial del repositorio y retirar las credenciales expuestas.
- Invalidar sesiones afectadas por la rotación de claves.
- Separar la carga de datos de demostración del despliegue operativo.

**Criterio de aceptación:** ninguna credencial activa permanece en el repositorio; los endpoints sensibles están restringidos y los despliegues no crean ni restablecen cuentas de prueba.

## 2. Autorización y protección de cuentas

**Prioridad: crítica · Estimación: 1–2 días**

- Exigir autenticación por defecto en la API y declarar explícitamente los endpoints públicos.
- Crear permisos reutilizables para turistas, agencias y proveedores.
- Verificar que cada modificación o eliminación corresponde al propietario del recurso.
- Revisar la misma regla en productos, reservas, evidencias, reportes y liquidaciones.
- Aplicar validación de contraseñas en los registros y límites de intentos en acceso y confirmación de contraseña.
- Revisar vencimiento, renovación y cierre de sesión de los tokens.

**Pruebas obligatorias:**

- Un visitante no puede modificar ni eliminar paquetes.
- Una agencia no puede gestionar recursos de otra.
- Un usuario con un rol distinto recibe una respuesta de acceso denegado.
- Los catálogos públicos siguen disponibles.

**Criterio de aceptación:** los permisos se comprueban en el servidor y están cubiertos por pruebas automatizadas.

## 3. Integridad de compras y reservas

**Prioridad: crítica · Estimación: 2–3 días**

- Obtener los precios de la base de datos y calcular el total en el servidor.
- Rechazar cantidades negativas, cero, decimales y valores fuera de límites.
- Validar disponibilidad, productos activos, fechas y cupos.
- Rechazar identificadores inexistentes y tipos de artículo desconocidos.
- Definir qué ocurre con artículos duplicados y compras parciales del carrito.
- Mantener la transacción y los bloqueos de inventario.
- Incorporar una clave de operación para evitar compras duplicadas por reintentos.
- Usar valores decimales en todos los cálculos monetarios.
- Retirar detalles internos de las respuestas de error.

**Pruebas obligatorias:**

- Alterar el precio o total enviado no cambia el importe calculado.
- Una cantidad negativa no aumenta el inventario.
- Dos compras simultáneas no exceden stock ni cupos.
- Repetir una solicitud no genera una segunda venta.
- Un fallo revierte todos los cambios de la compra.

**Criterio de aceptación:** el servidor determina el importe y ninguna compra deja inventario, reservas o ventas inconsistentes.

## 4. Confirmación de pagos y control de retiros

**Prioridad: alta · Estimación: 2–3 días, más integración externa**

### Pagos

- Separar los estados de pedido y pago.
- Crear ventas pendientes hasta recibir una confirmación verificable.
- Para operación real, integrar una pasarela y verificar sus notificaciones desde el servidor.
- Validar referencia, importe, moneda y estado del pago.
- Procesar notificaciones repetidas sin duplicar efectos.
- Definir la liberación de inventario y cupos para pagos fallidos o vencidos.
- Si se conserva una demostración, identificar claramente los pagos simulados.

### Retiros

- Descontar del saldo disponible los retiros pendientes y pagados.
- Liberar el importe reservado cuando una solicitud se rechace o cancele.
- Validar rol, método, monto y datos requeridos.
- Proteger el cálculo y la solicitud mediante transacción y bloqueo.
- Generar referencias únicas y registrar cambios de estado.
- Contemplar reembolsos en el saldo liquidable.

**Pruebas obligatorias:**

- Una compra sin confirmación no figura como pagada.
- Una notificación inválida no modifica la venta.
- Dos solicitudes simultáneas no comprometen más saldo del disponible.
- Un retiro pagado permanece descontado.

**Criterio de aceptación:** cada pago tiene evidencia verificable y cada retiro corresponde a saldo disponible respaldado.

## 5. Endurecimiento y publicación

**Prioridad: alta · Estimación: 2–3 días**

- Restringir CORS a los dominios autorizados.
- Revisar HTTPS, cookies seguras y configuración del proxy.
- Impedir que archivos de entorno entren en las imágenes de despliegue.
- Ejecutar las pruebas y verificaciones antes de cada despliegue.
- Completar la documentación de los endpoints críticos.
- Revisar registros para evitar contraseñas, tokens y datos bancarios.
- Probar en un entorno separado con datos ficticios.
- Preparar respaldo, migraciones y procedimiento de reversión.
- Revisar ventas y retiros históricos potencialmente afectados antes de habilitar operaciones reales.

**Criterio de aceptación:** las pruebas críticas pasan, los avisos de seguridad están resueltos o justificados y existe un procedimiento probado de recuperación.

## Mejoras posteriores

Una vez corregidos los problemas críticos:

- Dividir las vistas extensas por módulos de negocio.
- Fortalecer relaciones y restricciones de la base de datos preservando el historial de ventas.
- Optimizar imágenes y cargar las páginas bajo demanda.
- Actualizar las instrucciones de instalación y despliegue.

**Orden de ejecución:** contención → permisos → compras → pagos y retiros → validación y publicación.
