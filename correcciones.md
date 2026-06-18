# 🛠️ Instructivo de Correcciones — Proyecto Amazonia Viva

> **Destinatario:** Agente de desarrollo  
> **Proyecto:** Amazonia Viva (Django + DRF + Vue 3)  
> **Repositorio:** https://github.com/Patrick750/Amazonia-Viva  
> **Prioridad:** Las correcciones están ordenadas de mayor a menor criticidad.

---

## Contexto del Proyecto

Amazonia Viva es una plataforma web de turismo amazónico con backend en **Django + Django Rest Framework** y frontend en **Vue 3**. Implementa autenticación JWT, gestión de paquetes turísticos, carritos de compra, pagos, importación masiva de datos y reportes. Los roles principales son: Agencia, Proveedor y Turista.

---

## 🔴 Correcciones Críticas (Seguridad)

### 1. Mover secretos a variables de entorno

**Archivos afectados:** `amazoniaviva/settings.py` (líneas ~37–42, ~75–80)

**Problema:** La `SECRET_KEY` de Django, las credenciales de Cloudinary (`cloud_name`, `api_key`, `api_secret`) y los parámetros de correo electrónico están escritos directamente en el código fuente. Esto expone información sensible en el repositorio.

**Acción requerida:**

1. Instalar `python-decouple`:
   ```bash
   pip install python-decouple
   ```

2. Crear un archivo `.env` en la raíz del proyecto (y agregarlo a `.gitignore`):
   ```env
   SECRET_KEY=tu_clave_secreta_aqui
   CLOUDINARY_CLOUD_NAME=...
   CLOUDINARY_API_KEY=...
   CLOUDINARY_API_SECRET=...
   EMAIL_HOST_USER=...
   EMAIL_HOST_PASSWORD=...
   DATABASE_URL=postgres://...
   ```

3. En `settings.py`, reemplazar los valores hardcodeados:
   ```python
   from decouple import config

   SECRET_KEY = config('SECRET_KEY')
   CLOUDINARY_STORAGE = {
       'CLOUD_NAME': config('CLOUDINARY_CLOUD_NAME'),
       'API_KEY': config('CLOUDINARY_API_KEY'),
       'API_SECRET': config('CLOUDINARY_API_SECRET'),
   }
   EMAIL_HOST_USER = config('EMAIL_HOST_USER')
   EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
   ```

---

### 2. Restringir `ALLOWED_HOSTS`

**Archivo afectado:** `amazoniaviva/settings.py` (líneas ~43–57)

**Problema:** Existe un fallback a `['*']` cuando no se define un host externo, lo que permite cualquier dominio en producción y expone el sistema a ataques de tipo HTTP Host Header.

**Acción requerida:**

```python
# settings.py
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=lambda v: [s.strip() for s in v.split(',')])
```

```env
# .env (producción)
ALLOWED_HOSTS=amazoniaviva.com,www.amazoniaviva.com
```

```env
# .env (desarrollo)
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

### 3. Proteger la vista `VerificarEmail` contra enumeración de usuarios

**Archivo afectado:** `autenticacion/views.py` (líneas ~32–63)

**Problema:** El endpoint que verifica si un correo o nombre de usuario existe permite a un atacante enumerar usuarios válidos del sistema mediante fuerza bruta.

**Acciones requeridas:**

- Implementar **rate limiting** con `django-ratelimit`:
  ```bash
  pip install django-ratelimit
  ```
  ```python
  from ratelimit.decorators import ratelimit

  @ratelimit(key='ip', rate='5/m', method='POST', block=True)
  def verificar_email(request):
      ...
  ```

- Opcionalmente, integrar **reCAPTCHA v3** de Google en el frontend para este endpoint.

- Considerar retornar siempre el mismo mensaje genérico (`"Si el correo existe, recibirás un correo de confirmación"`) para no revelar información.

---

## 🟠 Correcciones Importantes (Calidad y Mantenibilidad)

### 4. Reemplazar `print()` con logging estructurado

**Archivos afectados:** múltiples vistas en `autenticacion/views.py`

**Problema:** Existen llamadas a `print()` en vistas que generan ruido en producción y no permiten controlar niveles de log ni redirigir a archivos o servicios externos.

**Acción requerida:**

1. Configurar logging en `settings.py`:
   ```python
   LOGGING = {
       'version': 1,
       'disable_existing_loggers': False,
       'handlers': {
           'console': {'class': 'logging.StreamHandler'},
           'file': {
               'class': 'logging.FileHandler',
               'filename': 'logs/amazoniaviva.log',
           },
       },
       'root': {
           'handlers': ['console', 'file'],
           'level': 'WARNING',
       },
       'loggers': {
           'autenticacion': {
               'handlers': ['console', 'file'],
               'level': 'DEBUG',
               'propagate': False,
           },
       },
   }
   ```

2. En cada vista, reemplazar `print(...)` por:
   ```python
   import logging
   logger = logging.getLogger('autenticacion')

   # En lugar de print("Error en pago:", e)
   logger.error("Error en procesamiento de pago: %s", str(e), exc_info=True)
   ```

---

### 5. Optimizar consultas a la base de datos

**Archivos afectados:** `autenticacion/views.py`, `autenticacion/serializers.py`

**Problema:** Existen consultas con múltiples operaciones encadenadas que pueden generar el problema N+1 (una consulta por cada objeto relacionado), degradando el rendimiento.

**Acción requerida:**

Revisar todas las vistas que retornen listas de objetos con relaciones y agregar `select_related` o `prefetch_related`:

```python
# Ejemplo para listado de paquetes con agencia y categoría
paquetes = PaqueteTuristico.objects.select_related(
    'agencia', 'categoria'
).prefetch_related(
    'actividades', 'imagenes'
).filter(activo=True)
```

Herramienta recomendada para detectar consultas N+1 en desarrollo:
```bash
pip install django-debug-toolbar
```

---

### 6. Reforzar validación en importación masiva

**Archivo afectado:** vista `CargaMasivaPaquetesAPIView` en `autenticacion/views.py`

**Problema:** La importación de archivos CSV/Excel valida categorías pero no verifica completamente los tipos numéricos ni los rangos de valores (ej. precios negativos, cupos = 0, fechas pasadas para paquetes nuevos).

**Acción requerida:**

Agregar validaciones antes del `bulk_create`/`bulk_update`:

```python
def validar_fila(fila):
    errores = []
    if fila.get('precio') is not None:
        try:
            precio = float(fila['precio'])
            if precio < 0:
                errores.append("El precio no puede ser negativo.")
        except ValueError:
            errores.append("El precio debe ser un número.")
    if fila.get('cupos') is not None:
        try:
            cupos = int(fila['cupos'])
            if cupos < 1:
                errores.append("Los cupos deben ser al menos 1.")
        except ValueError:
            errores.append("Los cupos deben ser un entero.")
    return errores
```

---

## 🟡 Mejoras Recomendadas (Documentación y Estructura)

### 7. Separar la bitácora de versiones en `CHANGELOG.md`

**Archivo afectado:** `README.md`

**Problema:** El README contiene una sección extensa de historial de versiones que dificulta la lectura y el mantenimiento.

**Acción requerida:**

1. Crear `CHANGELOG.md` en la raíz del proyecto.
2. Mover todo el historial de versiones al nuevo archivo.
3. En el `README.md`, dejar únicamente un enlace: `Ver [CHANGELOG.md](./CHANGELOG.md) para el historial completo.`

Formato sugerido para el changelog (estándar [Keep a Changelog](https://keepachangelog.com/es/1.0.0/)):
```markdown
## [1.3.0] - 2025-06-01
### Añadido
- Procesamiento de pagos con validación atómica

### Corregido
- Error en cálculo de cupos disponibles
```

---

### 8. Documentar la API con OpenAPI/Swagger

**Problema:** No existe documentación automática de los endpoints REST, lo que dificulta la integración del frontend y futuros desarrolladores.

**Acción requerida:**

```bash
pip install drf-spectacular
```

En `settings.py`:
```python
INSTALLED_APPS = [
    ...
    'drf_spectacular',
]

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}
```

En `urls.py`:
```python
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    ...
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
```

---

### 9. Revisar el frontend Vue 3

**Directorio afectado:** `frontend_project/`

Aunque el análisis se enfocó en el backend, se recomienda verificar los siguientes puntos en el frontend:

- Los tokens JWT se almacenan de forma segura (preferir `httpOnly cookies` sobre `localStorage` para evitar XSS).
- Los formularios validan entradas antes de enviarlas al API.
- Los mensajes de error del API se muestran de forma amigable al usuario sin exponer detalles técnicos.
- Se maneja correctamente la expiración del token (refresh token flow).

---

## Resumen de Tareas por Prioridad

| # | Tarea | Prioridad | Archivo principal |
|---|-------|-----------|-------------------|
| 1 | Mover secretos a `.env` | 🔴 Crítica | `settings.py` |
| 2 | Restringir `ALLOWED_HOSTS` | 🔴 Crítica | `settings.py` |
| 3 | Proteger `VerificarEmail` con rate limit | 🔴 Crítica | `views.py` |
| 4 | Reemplazar `print()` con logging | 🟠 Importante | `views.py` |
| 5 | Optimizar consultas N+1 | 🟠 Importante | `views.py`, `serializers.py` |
| 6 | Validar tipos en importación masiva | 🟠 Importante | `views.py` |
| 7 | Crear `CHANGELOG.md` | 🟡 Recomendada | `README.md` |
| 8 | Documentar API con Swagger | 🟡 Recomendada | `urls.py`, `settings.py` |
| 9 | Auditar seguridad del frontend Vue 3 | 🟡 Recomendada | `frontend_project/` |

---

*Instructivo generado a partir de la revisión de repositorio Git — Amazonia Viva.*