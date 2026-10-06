# Versionamiento automático

Adaptación de [Patrick750/versionamiento](https://github.com/Patrick750/versionamiento), revisado en el commit `803bf9e4988540b48b56be1ebaf97f7ef19b0a80`. Solo se integró su sistema de versiones; los scripts de ejemplo de ese repositorio no forman parte de Amazonia Viva.

## Convención

```text
tipo(modulo): palabra_clave [incremento] descripción
```

| Palabra | Declaración | Efecto desde 5.2.3 |
| --- | --- | --- |
| high | high [1.0.0] | 6.0.0 |
| low | low [0.1.0] | 5.3.0 |
| parch o patch | parch [0.0.1] | 5.2.4 |

Ejemplos: `feat(auth): high [1.0.0] cambiar contrato de acceso`, `feat(api): low [0.1.0] añadir búsquedas`, `fix(ui): parch [0.0.1] corregir menú`.

Las palabras se aceptan sin distinguir mayúsculas. El número entre corchetes indica el incremento, no la versión final. Se aplica la coherencia estricta del linter actual del repositorio de referencia: high exige [1.0.0], low [0.1.0], y parch/patch [0.0.1]. Commits ordinarios, como `docs: actualizar guía`, no incrementan versiones. Declaraciones incompletas o incoherentes fallan en el PR y antes de generar versiones.

`VERSION` es la fuente de verdad y comienza en **5.0.0**, conservando la versión ya implementada. Si falta, el cálculo parte de 0.0.0. Se sincronizan package.json, el paquete raíz del lockfile, la versión del README y una entrada de changelog por cada origen. El historial detallado anterior se conserva.

## Flujo

1. Trabajar en una rama secundaria y declarar los incrementos en los commits que correspondan.
2. Abrir PR a main/master. `Lint PR Commits` comprueba formato/coherencia; no recibe permisos de escritura ni credenciales Git persistidas.
3. Fusionar con **Create a merge commit** o **Rebase and merge**. No usar squash: elimina los commits individuales que deben versionarse.
4. En la primera ejecución, se registra el tag anotado **v5.0.0** sobre el checkout inicial, antes de aplicar incrementos. Así el historial empieza en la versión existente; un commit `parch [0.0.1]` genera después **v5.0.1**. Si el tag ya existe, se conserva. Si falta pero VERSION ya avanzó, el proceso falla para evitar etiquetar una versión incorrecta.
5. `Version Bump on Merge` obtiene before..after, ordena los commits de ancestros a descendientes y calcula cada incremento. Crea un commit `chore(version-bump)` y un tag anotado por origen.
6. La rama y únicamente los tags creados se publican en un push atómico. Los tags existentes nunca se sobrescriben; una colisión detiene el lote antes de generar commits.
7. Se guarda el SHA final como artifact. El despliegue espera la finalización satisfactoria del versionado, descarga ese artifact y verifica/compila exactamente ese SHA antes de publicar las imágenes y actualizar el VPS.

No se dispara el bot en ramas secundarias. Los commits generados por el bot se omiten; además, GITHUB_TOKEN no inicia otro workflow push. Las referencias de origen almacenadas como trailers permiten repetir una ejecución sin duplicar versiones. Un force-push cuyo before no sea ancestro de after falla para revisión, en lugar de omitir historia silenciosamente.

Las ejecuciones están serializadas por rama con queue: max. GitHub mantiene hasta 100 ejecuciones pendientes; el orden entre ejecuciones depende de la cola, mientras que los commits de cada lote se ordenan topológicamente. Para mantener orden global, evitar fusiones simultáneas y esperar al bot antes de integrar el siguiente PR. Un push concurrente durante la publicación puede rechazar el push atómico: revisar y reejecutar el workflow. Nunca usar force-push para publicar los commits del bot.

## Configuración en GitHub

Después de integrar los archivos en main:

- Permitir escritura de contents al GITHUB_TOKEN del workflow de versionado. Las reglas de rama deben permitir al bot crear los commits de versión; si lo bloquean, el push fallará y no se desplegará.
- Desactivar squash merge en Settings → General → Pull Requests. Mantener merge commits y/o rebase.
- Marcar `Validate PR Commit Format & Coherence` como check requerido de los PR.
- Conservar los secretos actuales de Docker Hub y VPS usados por el despliegue. No requiere un PAT adicional.
- Para automatismos externos como Render, asegurarse de que desplieguen el SHA versionado: el encadenamiento workflow_run descrito corresponde al despliegue Docker/VPS.

Estas preferencias remotas no se modificaron durante la implementación. No se hizo push, merge, despliegue ni publicación de tags reales. El commit previo de seguridad `250952e` conserva su mensaje original y no generará otro incremento; no se reescribe el historial para reversionar 5.0.0.

## Verificación local

```bash
python scripts/versionamiento.py check
python -m unittest discover -s tests -p 'test_versionamiento.py'
python scripts/versionamiento.py lint --before SHA_BASE --after SHA_HEAD
```

`bump` crea commits y tags: usarlo solo en un clon limpio y aislado para pruebas. `--push` publica a origin y está reservado al workflow. Las pruebas automatizadas usan repositorios temporales y un remoto bare local; cubren formato, alias, coherencia, orden, sincronización, tags anotados, reintentos, versión inválida/ausente, colisiones y publicación atómica sin tags ajenos. No ejecutan mensajes de commit como código shell.

Referencias: [eventos generados con GITHUB_TOKEN](https://docs.github.com/en/enterprise-cloud@latest/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow), [concurrencia y queue](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#concurrency).
