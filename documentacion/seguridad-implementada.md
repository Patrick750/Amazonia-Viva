# Implementación del plan de seguridad

Versión: 5.0.0. Fecha: 6 de octubre de 2026. Cambios preparados localmente; no desplegados.

## Estado del plan

| Etapa | Resultado | Pendiente para operación real |
| --- | --- | --- |
| Contención | Compras y retiros bloqueados por defecto; secretos retirados de settings; Docker excluye archivos de entorno y bases locales; despliegue sin demo. | Rotar claves en Cloudinary y entorno del servidor; depurar historial remoto y copias. |
| Permisos | Autenticación por defecto, permisos de rol, propiedad en paquetes/productos/evidencias/feedback/reportes/billetera; propietario inmutable; contraseñas validadas. | Revisar cuentas y sesiones existentes después de rotar claves. |
| Compras | Precios y tarifa calculados en servidor con Decimal; validación estricta; transacción; bloqueos; UUID y huella para reintentos; carrito parcial. | Ejecutar sobre datos operativos reconciliados. |
| Pagos | Wompi: checkout firmado, webhook autenticado, consulta privada, referencia/importe/COP verificados, eventos idempotentes y anulaciones verificadas. Sandbox excluido del saldo. | Configurar claves del comercio y webhook; validar sandbox de extremo a extremo; conciliación y reembolsos operativos. |
| Retiros | Reserva de pendientes/procesando/pagados; validación de método/monto/destinatario; bloqueo del titular; referencia UUID; cambios auditados. | Reconciliar retiros antiguos y ventas con evidencia externa antes de habilitar. Ejecución bancaria y conciliación quedan fuera de esta implementación. |
| Publicación | CORS restringido, HTTPS/cookies/HSTS, pruebas como requisito del despliegue, documentación y comandos operativos. | Aplicar y comprobar en el servidor el proxy, backup, rotación, migración, tareas de vencimiento y revisión histórica. |

El workflow de GitHub bloquea la construcción/publicación si fallan las verificaciones. build.sh (Render) exige TEST_DATABASE_URL distinta de DATABASE_URL y ejecuta las pruebas antes de migrar; no utiliza la base operativa como base de pruebas.

Las ventas existentes reciben `estado_pago=Pendiente`: el estado antiguo Completado no prueba un cobro. No se convierten automáticamente en fondos retirables. Las bajas de paquetes y productos son lógicas para conservar propietarios e historial. Los artículos cancelados, rechazados, devueltos o reembolsados no aportan saldo. Una pérdida de respaldo después de un retiro aparece como `saldo_por_recuperar`; requiere conciliación del operador.

## Configuración

Usar `.env.example` como referencia; generar una SECRET_KEY nueva y de alta entropía, de al menos 50 caracteres. El despliegue usa `DEBUG=false`. Sin SECRET_KEY válida, el servicio no inicia. Cloudinary recibe exclusivamente configuración de entorno; no hay credenciales incrustadas.

- `CHECKOUT_MODE=disabled`: POST de compra devuelve 503 sin modificar datos.
- `CHECKOUT_MODE=pending`: crea pedido pendiente y reserva stock/cupos durante 30 minutos. Con PAYMENT_PROVIDER=wompi entrega un enlace firmado al checkout; solo un webhook verificado confirma el cobro.
- `CHECKOUT_MODE=demo`: solo para base aislada; pedidos con pago Simulado, sin saldo liquidable. La interfaz indica la ausencia de cobro.
- `ALLOW_WITHDRAWALS=false`: bloquea solicitudes nuevas. Habilitar solamente después de verificar saldo y retiros históricos.
- `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS` y `CSRF_TRUSTED_ORIGINS`: dominios concretos separados por comas.
- `DATABASE_URL`: PostgreSQL. SQLite no sirve para verificar los bloqueos concurrentes.

El proxy debe eliminar cabeceras X-Forwarded-Proto del cliente y establecerlas él mismo, redirigir HTTP a HTTPS y limitar solicitudes por IP real. El límite de credenciales se comparte entre workers en PostgreSQL: 5 intentos/minuto por cuenta y REMOTE_ADDR. Si el proxy agrupa clientes bajo una sola dirección, configurar correctamente la dirección de origen y el límite del proxy. Tokens de acceso: 15 minutos; refresh: 7 días, rotación y lista de revocados. El frontend renueva y almacena el refresh rotado. El logout revoca la renovación; el access emitido vence en un máximo de 15 minutos.

Los comandos que crean datos de demostración exigen `DEBUG=true` y `CHECKOUT_MODE=demo`. No se ejecutan durante el despliegue.

## Endpoints críticos

`POST /api/venta/procesar/` requiere turista o agencia. Las agencias compran productos del catálogo agencias; solo turistas reservan paquetes. Ejemplo:

```json
{
  "clave_operacion": "29f3c7cb-d074-4b78-8a42-25b276562a2c",
  "items": [{"tipo": "producto", "id": 1, "cantidad": 2}],
  "novedades_turistas": []
}
```

Los IDs y cantidades deben ser enteros JSON; cantidad entre 1 y 1000, máximo 100 artículos. `tour` es alias de `paquete`; los paquetes flexibles requieren fecha ISO con siete días de antelación y los fijos su fecha programada. No se admiten artículos duplicados dentro del pedido. Precios y total del navegador se ignoran. Tarifa ecológica: 1% del subtotal de tours, redondeada a pesos con ROUND_HALF_UP, igual que la presentación existente. Todo el pedido se confirma o revierte en una transacción.

Respuestas: 201 nueva operación; 200 reintento con mismo UUID y contenido; 400 datos inválidos o UUID utilizado con otro contenido; 401 sin autenticación; 403 rol incorrecto; 503 suspendido. La respuesta incluye venta_id, total calculado, moneda COP y estado_pago Pendiente/Simulado. Solo se eliminan del carrito los artículos adquiridos.

`POST /api/liquidacion/solicitar-retiro/` requiere agencia/proveedor y ALLOW_WITHDRAWALS=true:

```json
{
  "monto": "50000.00",
  "metodo": "nequi",
  "datos_bancarios": {"cuenta": "3001234567", "titular": "Nombre", "numero": "Documento"}
}
```

Métodos: nequi, daviplata, transferencia_bancaria. Transferencia requiere banco y tipo_cuenta ahorros/corriente; billeteras requieren celular numérico de diez dígitos. Se valida monto positivo con máximo dos decimales y saldo disponible. La comisión es 8% y solo se liquidan ventas Pagado con detalles entregados/realizados/completados. Pendiente, Procesando y Pagado permanecen descontados; Rechazado/Cancelado liberan la reserva. PSE no se ofrece como método de retiro.

Cambios de retiro, con operador staff:

```bash
python manage.py cambiar_estado_retiro ID Procesando --actor ID_OPERADOR
python manage.py cambiar_estado_retiro ID Pagado --actor ID_OPERADOR
```

Pendiente permite Procesando, Rechazado o Cancelado; Procesando permite Pagado o Rechazado. Pagado es terminal. El comando registra actor, fecha y estado anterior/nuevo. No realiza una transferencia bancaria.

`POST /api/token/refresh/` recibe `{ "refresh": "token" }`; devuelve access y refresh nuevos. `POST /api/logout/` recibe refresh_token del usuario autenticado. Nunca registrar cuerpos de estos endpoints.

## Wompi

Configurar PAYMENT_PROVIDER=wompi, CHECKOUT_MODE=pending y variables WOMPI_ENVIRONMENT (test/prod), WOMPI_PUBLIC_KEY, WOMPI_PRIVATE_KEY, WOMPI_INTEGRITY_SECRET, WOMPI_EVENTS_SECRET y WOMPI_REDIRECT_URL. Las claves privadas y secretos solo se usan en el servidor; la URL de retorno debe usar HTTPS en producción. Las claves pública/privada deben pertenecer al mismo ambiente.

Registrar en el dashboard del ambiente correspondiente la URL HTTPS `/api/pagos/wompi/webhook/`. Usar una instalación/base independiente para sandbox. El webhook no exige JWT: autentica el evento con el secreto de Wompi. Responde 200 cuando se procesa; firma/datos inválidos reciben 400 y indisponibilidad del proveedor/configuración recibe 503, permitiendo sus reintentos.

El servidor verifica el checksum con las propiedades declaradas por el evento y consulta `/v1/transactions/{id}` con llave privada. La referencia, moneda, importe y estado utilizados provienen de esa consulta, no de campos sin firma. Las URLs de API están fijadas a dominios Wompi y no se siguen redirecciones. No se almacenan tarjetas, CVV ni el cuerpo completo del evento: solo evidencia mínima (transacción, checksum, estado, importe, moneda, ambiente, resultado y fecha).

APPROVED de producción convierte el pedido en Pagado y sus artículos en pendientes de empaque/confirmados. En sandbox queda Simulado. DECLINED/ERROR/VOIDED de un pendiente libera inventario/cupos. VOIDED después de aprobación elimina el respaldo liquidable y registra Reembolsado; no repone productos físicos entregados. Una aprobación tardía o de un pedido ya liberado queda Revision, no vuelve a consumir inventario ni aporta saldo: el operador debe conciliar y devolver el dinero por el mecanismo aplicable del comercio.

`GET /api/venta/{id}/estado/` solo devuelve pedidos del comprador. El retorno de Wompi abre la consulta de ese estado; parámetros del navegador no confirman cobros. `POST /api/venta/{id}/cancelar/` cancela todo el pedido pendiente y libera reservas de forma idempotente. Una compra pendiente no admite cancelación parcial de artículos porque alteraría el importe del checkout firmado. La interfaz permite continuar en Wompi, consultar estado y cancelar un pedido pendiente.

No se hizo una transacción externa ni se verificaron credenciales reales: faltan las claves del comercio en el entorno. Antes de habilitar producción, completar una compra sandbox y observar el webhook real, el estado del pedido, la expiración y una anulación. Los reembolsos que no llegan como VOIDED y las dispersiones bancarias requieren gestión/conciliación del operador; no se disparan transferencias automáticamente.

Implementación basada en documentación oficial consultada el 6 de octubre de 2026: [checkout e integridad](https://docs.wompi.co/docs/colombia/widget-checkout-web/), [eventos y checksum](https://docs.wompi.co/docs/colombia/eventos/), [consulta autenticada y estados](https://docs.wompi.co/docs/colombia/transacciones/).

## Pruebas y límites conocidos

Validación local en PostgreSQL 18 aislado: 62 pruebas pasaron, incluidas compras simultáneas, cupos, reintentos concurrentes y retiros simultáneos. Se verificaron permisos, precios adulterados, cantidades inválidas, reversión ante error, conservación del carrito parcial, pedidos pendientes/simulados, liberación de stock/cupos, retiros pagados descontados y acceso a evidencias ajenas.

`manage.py check`, `makemigrations --check --dry-run` y `check --deploy --tag security --fail-level WARNING` pasan. El frontend compila; Vite advierte bundles grandes (optimización posterior del plan). El entorno local emite un aviso de compatibilidad de requests con las bibliotecas instaladas; no impidió la ejecución.

La comprobación de despliegue completa incluye avisos preexistentes de drf-spectacular por vistas legacy sin serializers y operationId duplicados. Los endpoints nuevos de compra y retiro tienen contratos OpenAPI explícitos; el control obligatorio de publicación comprueba el tag security. Queda pendiente completar el esquema de las vistas legacy; no se silencian avisos globalmente.

Se probaron migración, copia/restauración PostgreSQL y reversión/reaplicación en bases temporales; también se verificó que 0015 asigna referencias distintas a dos ventas históricas ficticias. Esto valida el mecanismo, no el contenido ni la recuperación del servidor operativo. Los datos operativos y db.sqlite3 local se conservaron.

Referencias técnicas: [bloqueos y pruebas transaccionales de Django](https://docs.djangoproject.com/en/6.0/ref/models/querysets/#select-for-update), [permisos DRF](https://www.django-rest-framework.org/api-guide/permissions/).

## Despliegue y recuperación

1. Mantener compras y retiros deshabilitados. Respaldar PostgreSQL con pg_dump -Fc, archivos y configuración fuera del repositorio; comprobar restauración en otra base antes de modificar producción.
2. Rotar API key/secret en Cloudinary y SECRET_KEY en el servicio. Revocar las credenciales antiguas, reemplazar el entorno y reiniciar todos los workers. No usar claves antiguas como fallback.
3. Con la nueva versión y la nueva clave, aplicar `python manage.py migrate --noinput` y ejecutar `python manage.py invalidar_sesiones`. Cambiar SECRET_KEY invalida los JWT antiguos; el comando limpia sesiones y revoca los refresh registrados.
4. Ejecutar pruebas en una base aislada y `python manage.py check --deploy --tag security --fail-level WARNING` con el entorno real. Verificar HTTPS, dominio permitido, CORS, admin y catálogos. Publicar manteniendo los bloqueos monetarios.
5. Ejecutar `python manage.py auditar_operaciones` para revisar cantidades, stock, importes y operaciones sin evidencia. Reconciliar todas las ventas y retiros históricos con comprobantes externos. El comando no corrige ni marca ventas como pagadas.
6. Si se habilitan pedidos pendientes, programar `python manage.py expirar_pedidos` cada minuto en el servidor. La liberación es idempotente. Sin scheduler los pedidos vencidos siguen reservando capacidad; no habilitar pending sin esa tarea.
7. Habilitar cobros/retiros solamente tras completar integración y conciliación. Probar webhooks inválidos/repetidos, referencias, COP, importes, vencimiento, anulaciones y conciliación bancaria con Wompi.

Para revertir: detener escrituras, mantener bloqueos, restaurar backup verificado y desplegar la versión segura compatible. Las migraciones 0014/0015 pueden revertirse a 0013 en staging; se perderían estados de pago/idempotencia/auditoría nuevos, por lo que no hacerlo sobre operaciones nuevas sin restaurar su respaldo. No reactivar una versión vulnerable para atender compras reales.

## Historial y credenciales externas

La revisión del historial alcanzable encontró cambios de credenciales incrustadas en settings en fce7974 y e99c488. Los valores se retiraron del árbol de trabajo; siguen en el historial. Rotarlos es obligatorio aunque después se limpie Git.

La depuración del remoto requiere coordinación con sus colaboradores: hacer un mirror de respaldo, usar git-filter-repo con un archivo privado de reemplazos para todos los valores expuestos, revisar todas las ramas/tags, actualizar las referencias remotas coordinadamente y pedir nuevos clones. Revisar forks, caches, registros de CI y copias descargadas. No almacenar el archivo de reemplazos en Git. Esta operación y la rotación en Cloudinary/servidor no fueron ejecutadas: no se dispone de acceso autenticado a esos servicios y se preservó el historial compartido.
