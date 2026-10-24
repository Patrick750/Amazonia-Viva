# ECC en Amazonia Viva

Amazonia Viva usa [Everything Claude Code (ECC)](https://ecc.tools/) como conjunto de flujos para planificación, desarrollo, revisión, pruebas, seguridad y documentación asistidos por Codex.

## Integración

La integración tiene dos capas:

- El plugin nativo `ecc@ecc` se instala en el `CODEX_HOME` de cada persona. Codex no ofrece un alcance de plugin exclusivo por repositorio.
- El archivo `AGENTS.md` de la raíz contiene el contexto, los comandos de validación y las convenciones específicas de Amazonia Viva.

No se deben copiar al repositorio los agentes, skills ni hooks distribuidos por ECC. Eso duplicaría la instalación y dificultaría sus actualizaciones.

## Instalación reproducible

ECC requiere Codex 0.146.0 o posterior:

```bash
codex plugin marketplace add affaan-m/ECC
codex plugin add ecc@ecc
codex plugin list --marketplace ecc --json
```

El resultado debe mostrar `ecc@ecc` como instalado y habilitado. Después de instalarlo, reinicia Codex para cargar sus skills y servidores MCP.

Si la red no permite que Codex clone el marketplace de GitHub, puede usarse el paquete npm oficial como fuente local:

```bash
npm install --global ecc-universal@2.2.3
codex plugin marketplace add "$(npm root --global)/ecc-universal"
codex plugin add ecc@ecc --json
```

Los hooks son un permiso independiente. En una sesión nueva, abre `/hooks`, revisa la definición de ECC y decide si confías en ella. La instalación del plugin no autoriza sus comandos automáticamente.

## Actualización

```bash
codex plugin marketplace upgrade ecc --json
codex plugin add ecc@ecc --json
codex plugin list --marketplace ecc --json
```

`marketplace upgrade` requiere que `marketplace list` muestre `sourceType: git`. Para una fuente local instalada mediante npm, actualiza el paquete y vuelve a materializar la caché:

```bash
npm install --global ecc-universal@latest
codex plugin add ecc@ecc --json
codex plugin list --marketplace ecc --json
```

Si la definición de hooks cambia, Codex solicitará una nueva revisión porque la confianza se registra contra el contenido exacto de esa definición.

## Uso en este proyecto

Codex selecciona automáticamente la skill ECC más específica cuando su descripción coincide con la tarea. No es necesario escribir `$skill` ni pedir expresamente que se use ECC. La regla general está en `~/.codex/AGENTS.md` y las prioridades de Amazonia Viva están en el `AGENTS.md` del repositorio.

Las tareas también deben respetar los documentos de `documentacion/`. Los controles base son:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test autenticacion --noinput
python scripts/versionamiento.py check
cd frontend_project && npm ci && npm run build
```

Aplica solamente los controles relacionados con el cambio. Los flujos de ECC ayudan a ejecutar el trabajo, pero no sustituyen los requisitos funcionales ni las verificaciones del proyecto.

## Diagnóstico

```bash
codex plugin marketplace list --json
codex plugin list --marketplace ecc --json
```

La instalación nativa debe mostrar una única entrada `ecc@ecc`, una versión y un `installedPath`. Si ECC no aparece en una sesión abierta antes de instalarlo, reinicia Codex.
