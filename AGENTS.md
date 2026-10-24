# Instrucciones de trabajo para Amazonia Viva

Estas reglas complementan los flujos de ECC. Si una regla general de ECC no coincide con este repositorio, prevalecen estas instrucciones y la documentación vigente del proyecto.

## Contexto técnico

- Backend: Django 6 y Django REST Framework en la raíz del repositorio.
- Aplicación principal: `autenticacion/`.
- Frontend: Vue 3 y Vite en `frontend_project/`.
- Persistencia: PostgreSQL en producción; las pruebas de Django administran su propia base de datos.
- Despliegue: GitHub Actions y Docker Compose mediante `.github/workflows/deploy.yml`.
- Documentación funcional y operativa: `documentacion/`.

## Forma de trabajo

1. Revisa primero la documentación y el código relacionados con el cambio.
2. Conserva los contratos actuales de la API salvo que el requerimiento exija modificarlos.
3. Para cambios de datos o esquema usa migraciones de Django. Los catálogos se cargan con comandos de administración idempotentes; no agregues datos de demostración al despliegue.
4. Mantén secretos y credenciales fuera del repositorio. Usa variables de entorno y actualiza `.env.example` cuando aparezca una variable obligatoria nueva.
5. Añade pruebas enfocadas cuando cambie el comportamiento. Para ediciones de documentación o configuración de bajo riesgo basta con la validación específica correspondiente.
6. Actualiza la documentación del módulo cuando cambien el comportamiento, la operación o el despliegue.

## Validación

Ejecuta los controles que correspondan al cambio:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test autenticacion --noinput
python scripts/versionamiento.py check
```

Para cambios del frontend:

```bash
cd frontend_project
npm ci
npm run build
```

Para cambios de seguridad o despliegue, ejecuta además:

```bash
DEBUG=false python manage.py check --deploy --tag security --fail-level WARNING
```

## Git y versiones

- No alteres cambios del usuario que no formen parte de la tarea.
- Los commits siguen el formato documentado en `documentacion/versionamiento.md`, por ejemplo: `feat(paquetes): low [0.1.0] agregar filtro`.
- `VERSION` es la fuente de verdad; usa `python scripts/versionamiento.py check` para comprobar consistencia.
- Antes de cambiar el flujo de despliegue, verifica que la rama, el SHA y los comandos remotos mantengan la misma revisión durante todo el proceso.

## Flujos ECC recomendados

- Planificación compleja: skill de planificación o arquitectura.
- Django, API y migraciones: skills de Django, revisión Python y migraciones de base de datos.
- Vue y UX: skills de Vue, accesibilidad y diseño web.
- Antes de cerrar cambios relevantes: revisión de código, seguridad cuando aplique y pruebas del proyecto.

La instalación de ECC pertenece al entorno de Codex. No copies su catálogo de skills, agentes o hooks dentro de este repositorio.
