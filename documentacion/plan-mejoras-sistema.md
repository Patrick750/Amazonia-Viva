# Planificación de mejoras de Amazonia Viva

Fecha de inicio: 16 de octubre de 2026.

Documento de trabajo que se actualizará con las necesidades indicadas por el usuario. Los requisitos confirmados se separan de las propuestas y preguntas pendientes. El orden global de desarrollo se definirá al completar el inventario de mejoras; las etapas siguientes son provisionales. Este documento no acredita implementación ni viabilidad técnica comprobada.

## Inventario de mejoras

| ID      | Mejora                                                                                                         | Estado                                     | Prioridad global                             |
| ------- | -------------------------------------------------------------------------------------------------------------- | ------------------------------------------ | -------------------------------------------- |
| MEJ-001 | PWA con registro GPS sin conexión, trazado asociado al paquete y acceso al recorrido para turistas con compra | Necesidad registrada; alcance por precisar | Pendiente de comparar con las demás mejoras |
| MEJ-002 | Mejora UX del catálogo de paquetes y productos, onboarding por rol y recomendaciones personalizadas | Necesidad registrada; alcance por precisar | Pendiente de comparar con las demás mejoras |
| MEJ-003 | Actualizar el registro de paquetes turísticos conforme al documento de referencia y mejorar su interfaz visual y de uso | Implementada en `codex/mej-003-estandar-paquetes`; pendiente de revisión e integración | En ejecución |
| MEJ-004 | Rediseño UX de inicio de sesión y creación de cuenta utilizando la skill diseno-ux-web | Necesidad registrada; diseño por concretar | Pendiente de comparar con las demás mejoras |

## MEJ-001. Recorridos GPS vinculados a paquetes turísticos

### Objetivo

Permitir que una agencia registre el recorrido real de un paquete turístico mediante GPS, incluso sin conexión a internet; mostrar el trazado en el mapa del paquete y habilitar una opción de recorrido al turista que lo haya comprado cuando llegue la fecha de realización.

### Requisitos expresados por el usuario

| ID     | Actor o contexto                  | Requisito                                                                                             |
| ------ | --------------------------------- | ----------------------------------------------------------------------------------------------------- |
| RF-001 | Plataforma                        | Contar con una PWA para la funcionalidad de recorridos.                                               |
| RF-002 | Usuario con rol de agencia        | Registrar mediante GPS el trayecto realizado, incluso sin conexión a internet.                       |
| RF-003 | Usuario con rol de agencia        | Ver un mapa que muestre una línea con el trayecto por el que ha pasado.                              |
| RF-004 | Paquete turístico                | Vincular el trazado registrado a un paquete turístico.                                               |
| RF-005 | Personas que consultan el paquete | Ver en el mapa del paquete el trazado de ese recorrido.                                               |
| RF-006 | Turista que compró el paquete    | Tener habilitada la opción de recorrido cuando llegue la fecha de realización del paquete comprado. |

### Flujo funcional inicial

1. La agencia registra mediante GPS un trayecto sin depender de una conexión a internet y ve su trazado en un mapa.
2. El recorrido queda vinculado al paquete turístico correspondiente. El momento de selección del paquete está pendiente de definir.
3. Quien consulta el paquete puede ver el trazado en su mapa. La sincronización y el momento de publicación están pendientes de definir.
4. El turista compra el paquete para una fecha de realización.
5. Al llegar esa fecha, se habilita la opción de recorrido para ese turista y esa compra. El comportamiento de esta opción está pendiente de definir.

### Orden interno propuesto para desarrollar esta mejora

Estas etapas son una propuesta de planificación, no decisiones ya aprobadas.

1. **Definir las reglas del recorrido y de acceso.** Precisar qué hará el turista, cómo se determina la fecha y cómo se relacionan paquete, recorrido y compra.
2. **Definir y validar la base PWA y el funcionamiento sin conexión.** Comprobar en los dispositivos previstos la captura GPS, la persistencia local, el comportamiento al bloquear la pantalla y el alcance del mapa sin internet.
3. **Implementar el registro de la agencia y la sincronización.** Guardar el trazado, asociarlo al paquete y transferirlo al sistema al recuperar conexión; definir recuperación ante interrupciones y reintentos sin duplicados.
4. **Mostrar el recorrido en el paquete.** Presentar el trazado disponible a las personas que consultan el paquete.
5. **Habilitar el recorrido del turista.** Aplicar las reglas acordadas de compra y fecha e implementar las acciones que se definan para esa opción.

El registro de la agencia alimenta el trazado que verá el público. La habilitación del turista requiere que estén definidas la compra válida, la fecha de realización y la funcionalidad concreta del recorrido.

### Decisiones pendientes

- **Función del turista:** ¿la opción de recorrido permite solamente consultar el mapa, seguir la ruta usando su ubicación o también registrar su propio trayecto?
- **PWA:** ¿se adaptará la plataforma actual o se creará una aplicación separada?
- **Uso sin conexión:** ¿debe verse el mapa completo sin internet, además de poder guardar los puntos GPS? ¿También aplica al turista?
- **Captura GPS:** ¿debe continuar con la pantalla bloqueada o con la aplicación en segundo plano? Requiere validación técnica en los dispositivos objetivo.
- **Relación con el paquete:** ¿cada paquete tendrá un solo recorrido o varios? ¿Cómo se actualiza un recorrido ya publicado?
- **Publicación:** ¿el trazado se publica automáticamente al sincronizar o la agencia debe revisarlo antes?
- **Fecha y acceso:** ¿cuándo comienza y termina la habilitación, qué zona horaria aplica y qué ocurre con cancelaciones o cambios de fecha?
- **Control del registro:** ¿se necesitan acciones de iniciar, pausar, reanudar y finalizar?
- **Visibilidad de ubicación:** definir qué datos del recorrido se publican y quién puede consultar las ubicaciones individuales.

### Validación funcional propuesta

Los casos se concretarán una vez resueltas las decisiones anteriores:

- Una agencia registra un trayecto sin internet y los puntos guardados se conservan ante las interrupciones que se acuerde soportar.
- El mapa presenta el trazado capturado y este queda asociado al paquete correcto.
- Al recuperar conexión, el recorrido se sincroniza sin duplicarse por reintentos.
- La consulta del paquete muestra su recorrido publicado.
- La opción del turista se habilita conforme a las reglas acordadas de compra y fecha, con validación de acceso en el servidor.

## MEJ-002. Experiencia del catálogo y recomendaciones personalizadas

### Objetivo

Mejorar el diseño y la experiencia de uso del catálogo de paquetes y productos, e incorporar un onboarding para los usuarios que acaban de crear una cuenta, adaptado a su rol. La información obtenida debe permitir conocer el perfil de cada usuario y recomendarle productos o paquetes acordes con sus intereses y necesidades.

### Requisitos expresados por el usuario

| ID | Actor o contexto | Requisito |
| --- | --- | --- |
| RF-007 | Catálogo de paquetes | Mejorar el diseño UX y la experiencia de consulta. |
| RF-008 | Catálogo de productos | Mejorar el diseño UX y la experiencia de consulta. |
| RF-009 | Sugerencias de ítems | Mejorar la experiencia de presentación y consulta de las recomendaciones. |
| RF-010 | Todos los usuarios que acaban de crear una cuenta | Presentar un onboarding adaptado al rol del usuario. |
| RF-011 | Perfil del usuario | Recopilar durante el onboarding información que permita caracterizar al usuario para personalizar las sugerencias. Los campos concretos están pendientes de definir. |
| RF-012 | Recomendaciones | Sugerir productos o paquetes acordes con el perfil de cada usuario. |

La referencia a identificar al usuario se interpreta aquí como conocer sus preferencias para personalizar la experiencia. No se ha solicitado una verificación de identidad documental.

### Flujo funcional inicial

1. El usuario crea una cuenta y el sistema reconoce el rol con el que se registró.
2. Se presenta el onboarding correspondiente a ese rol.
3. El usuario proporciona la información de perfil que se defina para ese flujo.
4. El sistema conserva esa información asociada a su cuenta.
5. El usuario consulta el catálogo y recibe sugerencias de productos o paquetes relacionadas con su perfil.

### Orden interno propuesto para desarrollar esta mejora

Estas etapas son una propuesta de planificación, no decisiones ya aprobadas.

1. **Definir perfiles y criterios de recomendación.** Precisar los roles incluidos, qué necesita cada uno y qué información de los ítems permite relacionarlos con esas necesidades.
2. **Diseñar la experiencia del catálogo y del onboarding.** Concretar navegación, presentación de los ítems y de las sugerencias, y preguntas de cada rol; revisar los flujos antes de implementarlos.
3. **Implementar el onboarding y guardar las preferencias.** Definir su estado de avance, reanudación y actualización del perfil.
4. **Implementar las recomendaciones y su presentación.** Relacionar las preferencias con la información disponible de productos y paquetes, y definir qué mostrar cuando falten datos o coincidencias.
5. **Validar la experiencia completa por rol.** Comprobar registro, onboarding, consulta del catálogo y pertinencia de las sugerencias con escenarios representativos.

La personalización depende de contar con información utilizable tanto del usuario como de los productos y paquetes. El rediseño general del catálogo puede avanzar junto al diseño del onboarding una vez acordados los flujos. La propuesta técnica inicial se detalla a continuación; su implementación y los criterios concretos están pendientes de validación.

### Propuesta técnica recomendada: estructuras de datos y algoritmo

**Opción inicial recomendada:** diccionarios, conjuntos y vectores de preferencias, combinados con una lista de reglas explícitas de compatibilidad. Se propone un recomendador basado en contenido que primero evalúe los requisitos aplicables y después ordene las opciones por afinidad. Esta elección permite empezar con las respuestas del onboarding sin depender de un historial amplio de compras de otros usuarios.

El usuario plantea cruzar características del turista, como altura, peso y condiciones declaradas como asma, con las características y niveles de riesgo de los paquetes o actividades. Estos datos se distinguirán de las preferencias comerciales. Los campos definitivos, las reglas y sus responsables deben definirse antes de implementar la evaluación.

#### Estructuras de datos

| Estructura | Aplicación propuesta | Consideración |
| --- | --- | --- |
| Diccionarios / tablas hash | Acceder por clave a atributos de perfiles, productos, actividades y reglas. | Usar campos y unidades definidos; distinguir dato desconocido de valor negativo. |
| Conjuntos (`set`) | Representar intereses y etiquetas; calcular intersecciones entre usuario e ítem. | Utilizar identificadores de un catálogo común, evitando variantes de texto libre. |
| Vectores numéricos | Representar afinidad en dimensiones compartidas, como categorías de interés. | Mantener el mismo orden de dimensiones y normalizar las puntuaciones comparadas. |
| Lista de reglas estructuradas | Evaluar requisitos de equipo, accesibilidad y situaciones que requieren revisión. | Registrar condición, resultado, explicación, fuente, versión y responsable de revisión. No ejecutar código arbitrario almacenado como regla. |
| Lista de resultados | Conservar ítem, puntuación, estado de compatibilidad y motivos; ordenar los candidatos. | Suficiente para el catálogo inicial; utilizar un desempate estable. |
| Heap mínimo de tamaño K, opcional | Conservar los K mejores resultados cuando el volumen justifique evitar ordenar todos los candidatos. | Selección O(N log K), más la ordenación final de los K elegidos; no es necesario introducirlo desde el inicio. |

Las estructuras anteriores se utilizarían en memoria durante el cálculo. Los perfiles, atributos, relaciones y reglas se persistirían en tablas relacionales; no se propone reemplazar la base de datos por árboles o diccionarios en memoria.

No se recomienda un árbol binario de búsqueda como estructura principal porque el problema combina múltiples atributos y reglas, no una única clave de ordenación. Un árbol de decisión puede representar algunos flujos, pero para la primera versión se propone una lista de reglas independientes que permita evaluar y conservar varios motivos simultáneamente. Los grafos y el filtrado colaborativo quedan como alternativas futuras, sujetas a necesidades e historial reales.

#### Flujo del algoritmo

1. **Seleccionar el contexto del rol.** Cargar las preguntas, atributos y candidatos correspondientes. Los tres roles pueden compartir el motor con configuraciones diferentes; falta concretar qué se recomienda a cada uno.
2. **Obtener candidatos.** Consultar productos o paquetes disponibles y pertinentes al contexto.
3. **Evaluar requisitos.** Comparar el perfil con los requisitos documentados de cada actividad o producto y conservar todos los motivos encontrados.
4. **Calcular afinidad.** Puntuar las opciones elegibles mediante coincidencias de intereses y criterios acordados, como presupuesto o destino.
5. **Ordenar y seleccionar.** Devolver los K resultados mejor puntuados con un criterio estable de desempate.
6. **Explicar el resultado.** Mostrar motivos comprensibles de recomendación y, cuando corresponda, información pendiente o necesidad de revisión, sin revelar datos personales a otros usuarios.

Se propone empezar con una suma ponderada de coincidencias normalizadas: `afinidad = suma(peso_del_criterio × coincidencia_del_criterio)`. Los criterios, pesos y tratamiento de datos faltantes deben acordarse y versionarse; no se fijan porcentajes en esta etapa. Los datos físicos y de salud no se incorporan como una penalización comercial dentro de esa suma. Una incompatibilidad documentada no puede compensarse con una afinidad alta.

#### Evaluación de compatibilidad y riesgo

- Diferenciar resultados como **cumple los requisitos registrados**, **requiere revisión previa**, **no cumple un requisito documentado** e **información insuficiente**. El primer estado no constituye certificación médica de seguridad. Si concurren varios resultados, conservar los motivos y definir una precedencia explícita; un incumplimiento conocido no se oculta por otro dato faltante.
- Comparar altura y peso con requisitos concretos y documentados de equipo o actividad, cuando sean pertinentes. No inferir capacidad física por apariencia, peso o altura.
- No crear una regla general `asma → excluir`. Las condiciones declaradas solo activarán las evaluaciones o revisiones específicas que hayan sido validadas por responsables competentes. No se definen aquí umbrales ni contraindicaciones médicas.
- Registrar factores de cada actividad, además de su nivel general de riesgo: por ejemplo, esfuerzo, distancia, desnivel, altitud, exposición ambiental y acceso a asistencia. Los campos y escalas se deben acordar con quienes evalúan la actividad.
- Evaluar cada actividad del paquete e identificar cuáles son obligatorias u opcionales. No promediar riesgos de manera que se oculte un requisito incumplido de una actividad obligatoria. Definir cómo se ofrece una alternativa para actividades opcionales.
- No interpretar un campo sin responder como ausencia de una condición. Definir la presentación y elegibilidad de los resultados que requieren revisión o información adicional antes de implementar el motor.
- Separar la información de salud de las preferencias, recoger únicamente los datos necesarios y definir autorización de uso, acceso restringido, actualización y eliminación. Evitar incorporar estos datos a explicaciones públicas o registros generales.

#### Orden de implementación recomendado

1. Definir atributos, unidades, preguntas por rol y relación paquete–actividad; identificar responsables de validar los requisitos.
2. Preparar la persistencia de perfiles, preferencias, actividades y reglas, con separación de información restringida.
3. Implementar y comprobar el evaluador de reglas y sus resultados, incluido el tratamiento de datos faltantes y actividades obligatorias.
4. Implementar conjuntos de intereses, puntuación ponderada y ordenación de candidatos con explicaciones.
5. Integrar el motor con onboarding y catálogo; validar escenarios por rol y ausencia de coincidencias.
6. Medir pertinencia y rendimiento antes de incorporar un heap, grafos o aprendizaje basado en interacciones.

Las comprobaciones del motor deben cubrir límites documentados de equipo, datos desconocidos, reglas concurrentes, incompatibilidades que no puedan compensarse por afinidad y separación de acceso entre roles. La recomendación técnica es una propuesta de desarrollo; no implica que las reglas de salud o el modelo de datos ya estén aprobados.

Referencias técnicas de apoyo: [filtrado basado en contenido](https://developers.google.com/machine-learning/recommendation/content-based/basics) y [generación, puntuación y ajuste de candidatos](https://developers.google.com/machine-learning/recommendation/overview/types), documentación oficial de Google consultada el 16 de octubre de 2026. Para el contexto de planificación de actividades y condiciones personales: [guía de salud y seguridad del National Park Service](https://home.nps.gov/subjects/healthandsafety/trip-planning-guide.htm); no sustituye la validación específica de las reglas de la plataforma.

### Decisiones pendientes

- **Roles y propósito:** confirmar todos los roles que tendrán onboarding y qué productos o paquetes corresponde recomendar a cada uno.
- **Datos del perfil:** definir preguntas y campos por rol. Intereses, destinos, presupuesto y tipo de experiencia son ejemplos para evaluar, no requisitos confirmados.
- **Finalización:** ¿el onboarding será obligatorio o se podrá omitir? ¿Cómo se retoma si queda incompleto?
- **Usuarios existentes:** ¿también se les ofrecerá completar sus preferencias o el alcance se limita a cuentas nuevas?
- **Edición:** definir si el usuario podrá modificar sus preferencias y desde dónde.
- **Catálogo:** precisar qué dificultades actuales se quieren resolver y el alcance en navegación, búsqueda, filtros, tarjetas y consulta del detalle.
- **Sugerencias:** definir dónde aparecen, cómo se ordenan y qué se muestra cuando no hay información suficiente o ítems coincidentes.
- **Origen de las recomendaciones:** ¿se usarán solo las respuestas del onboarding o también interacciones posteriores? Esto último no forma parte del alcance confirmado.

### Validación funcional propuesta

- Cada cuenta nueva recibe el onboarding correspondiente a su rol.
- Las respuestas quedan asociadas a la cuenta correcta y están disponibles para personalizar las sugerencias.
- Las recomendaciones corresponden a los criterios de perfil acordados y a los ítems disponibles.
- El catálogo permite consultar paquetes y productos con los flujos UX aprobados, incluida su presentación en dispositivos móviles.
- La experiencia contempla perfiles incompletos y ausencia de coincidencias conforme a las reglas que se definan.

## MEJ-003. Registro de paquetes con clasificación de actividades, requisitos técnicos y mejora de interfaz

### Objetivo y fuente

Actualizar el registro de paquetes turísticos para incorporar el estándar descrito en el documento aportado por el usuario: [Significado técnico de las actividades turísticas en Colombia](referencias/actividades-turisticas-colombia.md). Se conserva una copia del archivo recibido para mantener la trazabilidad del alcance.

También se debe mejorar la interfaz de registro y edición de paquetes para que sea más amigable y agradable a la vista. Este rediseño forma parte de MEJ-003 y complementa la actualización de los campos y reglas.

La solicitud comprende utilizar ese documento como referencia funcional. Para la implementación se contrastaron sus afirmaciones principales con el índice oficial de Normas Técnicas Sectoriales del MinCIT, la comunicación oficial sobre la Resolución 0612 de 2024 y el Directorio Oficial de Acreditados de ONAC. El documento aportado no constituye por sí solo una certificación de cumplimiento del sistema o del prestador.

### Estado de implementación — 16 de octubre de 2026

MEJ-003 quedó implementada en la rama `codex/mej-003-estandar-paquetes` con estos componentes:

- Registro de modalidades turísticas aplicables al paquete.
- Ficha técnica independiente por actividad, con nombre del sistema de clasificación, nivel cuando existe una escala cargada y descripción operativa.
- Campos para requisitos y restricciones del participante, condiciones de operación, medidas de seguridad e información de sostenibilidad.
- Soporte de certificación para turismo de aventura. Un paquete de aventura activo requiere estado vigente, organismo evaluador, código y fecha de vigencia no vencida; un paquete inactivo puede conservarse como borrador mientras se completa esta información.
- Separación explícita entre el nivel de riesgo interno 1–10 del catálogo y la dificultad técnica de cada actividad.
- Vista informativa pública en `/estandar-paquetes`, alimentada por el mismo endpoint que expone la versión, los principios y las fuentes del estándar.
- Presentación de la ficha técnica al turista en el detalle público del paquete.
- Rediseño del formulario en secciones más claras, ayudas contextuales, resumen de errores, campos condicionales y controles adaptables.

Fuentes oficiales verificadas para esta entrega:

- [Resolución 0612 de 2024 y exigencia de nivel sobresaliente para turismo de aventura](https://www.mincit.gov.co/prensa/noticias/turismo/servicios-turismo-aventura-certificacion-seguridad), MinCIT.
- [Índice oficial de NTS para agencias de viajes, incluidas NTS-AV 010 a 015](https://www.mincit.gov.co/minturismo/calidad-y-desarrollo-sostenible/calidad-turistica/normas-tecnicas-sectoriales/nts-agencias-de-viajes-1), MinCIT.
- [Directorio Oficial de Organismos de Evaluación de la Conformidad](https://onac.org.co/directorio-de-acreditados/sectores/turismo-y-ocio/), ONAC.

La publicación en Amazonía Viva registra información y referencias aportadas por la agencia; no emite, reemplaza ni garantiza una certificación oficial.

### Requisito expresado por el usuario

| ID | Actor o contexto | Requisito |
| --- | --- | --- |
| RF-013 | Registro de paquetes turísticos | Actualizar el registro para incorporar el estándar estipulado en el documento de referencia suministrado. |
| RF-014 | Interfaz de registro y edición de paquetes turísticos | Mejorar el diseño visual y la facilidad de uso para que la interfaz sea más amigable y agradable a la vista. |
| RF-015 | Vista informativa del estándar | Incluir una vista de información que explique en qué se basa el estándar aplicado al registro de paquetes turísticos. |

### Vista informativa del estándar

La vista deberá explicar la base del estándar utilizado. Se propone que sea accesible desde el formulario de registro y edición mediante una acción visible, como «Información del estándar».

Contenido propuesto, pendiente de concretar en el diseño:

- Explicación clara del propósito de la clasificación de modalidades, actividades y dificultad.
- Bases y referencias utilizadas para cada clasificación, diferenciando las normas verificadas de otras referencias técnicas.
- Relación entre las actividades del paquete y sus escalas o requisitos específicos, con ejemplos que faciliten completar el formulario.
- Nombre, identificación y enlace de consulta de las fuentes oficiales verificadas, cuando estén disponibles.
- Versión o fecha de revisión de las referencias aplicadas por el sistema.

La vista debe reflejar las reglas efectivamente implementadas y sus fuentes verificadas. El documento aportado se conserva como referencia inicial; sus afirmaciones no se presentarán como normativa verificada sin el contraste previsto en esta mejora.

Queda pendiente definir si esta información se presentará como página, panel o ventana, y si también estará disponible desde el detalle público del paquete.

### Propuesta de experiencia visual

Como orientación inicial, pendiente de concretar en un diseño revisable:

- Agrupar los campos en secciones claras, con una jerarquía visual que facilite entender y completar el formulario.
- Mantener textos legibles, espaciado consistente y acciones fáciles de identificar.
- Mostrar los campos específicos de las actividades seleccionadas y explicar los términos técnicos cuando sea necesario.
- Presentar los errores y las indicaciones junto al campo correspondiente para facilitar su corrección.
- Adaptar el formulario a dispositivos móviles y escritorio.

La distribución final, el uso de pasos y el estilo visual quedan pendientes de definir. Esta mejora corresponde al formulario de paquetes; el rediseño del catálogo se mantiene en MEJ-002.

### Desglose funcional propuesto a partir del documento

El siguiente desglose interpreta la referencia para planificar el sistema. Los campos, escalas y bloqueos definitivos quedan pendientes de acordar y validar.

| Componente propuesto | Referencia en el documento | Aplicación prevista |
| --- | --- | --- |
| Modalidad turística | Sección 3 | Clasificar el paquete en las modalidades aplicables, como naturaleza, cultural, aventura o rural. |
| Actividades del paquete | Sección 4 | Registrar las actividades que componen el paquete y sus características técnicas. |
| Dificultad específica de la actividad | Sección 4.1 | Usar datos y escalas adecuados a cada actividad; evitar tratar las escalas diferentes como una única escala equivalente. |
| Perfil y requisitos del participante | Sección 4.1 | Describir las condiciones de participación que correspondan, como experiencia, edad, preparación física o certificación, según se valide para cada actividad. |
| Riesgos y condiciones de operación | Secciones 4 y 4.1 | Definir qué información del manejo de riesgos se registra, qué se informa al turista y qué revisa la agencia. El documento no proporciona una escala general de riesgo aplicable a todos los paquetes. |
| Prestador y soporte de certificaciones | Secciones 1, 2 y 4 | Determinar qué datos corresponden a la agencia o al operador, cuáles se vinculan al paquete y qué evidencias se requieren según la actividad. |
| Sostenibilidad | Sección 5 | Identificar qué requisitos de la referencia se traducen en información del paquete y cuáles pertenecen a la gestión del prestador. |

### Clasificaciones que deben evaluarse por actividad

Según la sección 4.1 de la fuente aportada, se deben estudiar las siguientes diferencias para diseñar el formulario:

- **Rafting y canotaje:** clasificación del tramo de río mediante clases I a VI; verificar su aplicación y las restricciones antes de definir opciones publicables.
- **Cabalgata:** características del equino y experiencia del jinete. Distinguir los datos operativos de asignación del caballo de la descripción comercial del paquete.
- **Parapente:** competencia y habilitación del piloto; no equivale a un grado de dificultad del turista.
- **Rapel y torrentismo:** características del descenso, altura, caudal, necesidad de nado y exigencia técnica.
- **Espeleología:** recorrido horizontal o vertical y requisitos de progresión.
- **Escalada:** escala utilizada y grado de la vía, evitando mezclar valores de escalas diferentes.
- **Buceo:** características de la inmersión y certificación requerida al participante.

Para las demás actividades de la sección 4, el documento no detalla una escala específica. No se inventarán escalas normativas para completar esos casos. La dificultad, el riesgo, la habilitación del operador y los requisitos del participante se tratarán como conceptos distintos.

### Flujo funcional propuesto

1. La agencia registra o edita un paquete y selecciona sus modalidades y actividades.
2. El formulario solicita información específica para cada actividad, conforme a las reglas verificadas y acordadas.
3. La agencia registra las condiciones de participación y vincula los soportes que resulten aplicables.
4. El sistema valida la información requerida y aplica el flujo de revisión o publicación que se defina.
5. El detalle del paquete presenta al turista la información relevante de actividades, dificultad y condiciones de participación. La presentación pública concreta está pendiente de aprobación.

### Relación con las otras mejoras

- **MEJ-002:** la clasificación de actividades y las condiciones del paquete pueden alimentar filtros y recomendaciones. Debe acordarse qué preferencias del onboarding se relacionan con estos datos. Una recomendación personalizada no acredita que una persona sea apta para realizar una actividad.
- **MEJ-001:** se debe definir si la dificultad y las características se asocian al paquete completo, a cada actividad o también a tramos del recorrido GPS.

### Orden interno propuesto

1. Contrastar las referencias y escalas del documento con las fuentes oficiales y determinar su aplicación a las actividades ofrecidas.
2. Acordar una matriz de actividades, campos, escalas, soportes y reglas, distinguiendo paquete, actividad, prestador y participante.
3. Diseñar y revisar una interfaz de registro y edición más amigable y agradable a la vista, incorporando los nuevos campos; definir cómo actualizar los paquetes existentes.
4. Implementar almacenamiento, validaciones y el flujo de publicación acordado.
5. Incorporar la información pertinente al detalle público y conectarla con filtros y recomendaciones cuando corresponda.

La definición de estos datos es una dependencia propuesta para la parte de MEJ-002 que recomiende paquetes por actividad o dificultad. El orden global sigue abierto hasta completar el inventario de mejoras.

### Decisiones pendientes

- **Cobertura inicial:** ¿se contemplarán todas las modalidades y actividades del documento o un grupo inicial?
- **Composición:** definir cómo registrar paquetes con varias actividades y diferentes exigencias, sin perder el detalle de cada actividad.
- **Riesgo:** definir la información a recopilar y su método de evaluación; la referencia no establece una escala universal de riesgo.
- **Prestadores y evidencias:** determinar quién opera cada actividad y cómo se registran, revisan y actualizan sus soportes.
- **Publicación:** definir campos obligatorios, revisión, bloqueos y tratamiento de soportes vencidos, según las reglas verificadas.
- **Paquetes existentes:** definir actualización, datos faltantes y condiciones para mantenerlos publicados.
- **Participantes:** precisar qué se declara en el perfil, qué se confirma al comprar o antes del recorrido y quién verifica las condiciones de participación.
- **Sostenibilidad y otras categorías de prestadores:** precisar qué partes del documento afectan este registro y cuáles requieren mejoras separadas.

### Validación funcional propuesta

- Cada actividad solicita los campos y la escala que le correspondan según la matriz aprobada.
- Un paquete con varias actividades conserva la clasificación y condiciones de cada una.
- Las reglas no confunden dificultad, riesgo, certificación del operador y requisitos del participante.
- La agencia puede actualizar paquetes existentes conforme al procedimiento acordado.
- La interfaz de registro y edición cumple el diseño aprobado, con campos y acciones legibles, secciones claras y una presentación usable en móvil y escritorio.
- La vista informativa es accesible desde el registro y explica las bases del estándar aplicado, con referencias que correspondan a las reglas implementadas.
- El turista consulta la información aprobada y las recomendaciones utilizan los datos definidos sin asumir aptitud personal.

## MEJ-004. Rediseño UX del inicio de sesión y creación de cuenta

### Objetivo y alcance confirmado

Rediseñar la experiencia de inicio de sesión y creación de cuenta utilizando la skill [diseno-ux-web](/home/patrickortiz/.codex/skills/diseno-ux-web/SKILL.md). Se registra como parte de la planificación; todavía no se implementan cambios en las pantallas.

| ID | Actor o contexto | Requisito |
| --- | --- | --- |
| RF-016 | Usuarios que inician sesión | Rediseñar la experiencia UX del inicio de sesión. |
| RF-017 | Personas que crean una cuenta | Rediseñar la experiencia UX de creación de cuenta. |
| RF-018 | Diseño de ambas pantallas | Aplicar la skill diseno-ux-web en la planificación y ejecución del rediseño. |

### Contexto inicial del código

La lectura inicial ubica el inicio de sesión en `frontend_project/src/views/login.vue` y la creación de cuenta en `frontend_project/src/views/signup.vue`. Las rutas públicas son `/auth/login` y `/auth/signup`. El registro contempla turista, agencia y proveedor, y el inicio de sesión utiliza correo y contraseña. Esta localización no constituye una evaluación visual ni una prueba de funcionamiento.

### Brief UX propuesto

- **Usuarios y tarea:** personas que quieren acceder a su cuenta o registrarse como turista, agencia o proveedor. El propósito principal de estas pantallas es completar una tarea con claridad y pocas fricciones.
- **Inicio de sesión:** identificar fácilmente los campos, comprender la acción principal, reconocer el estado del envío y recibir una indicación útil ante un error; mantener visible la alternativa de crear cuenta.
- **Creación de cuenta:** comprender los roles disponibles, seleccionar el correspondiente y completar los datos requeridos mediante una agrupación clara. La división en pasos se decidirá según la complejidad real del formulario.
- **Jerarquía visual:** títulos que describan la tarea, etiquetas legibles, acción principal destacada y enlaces secundarios diferenciados. Mantener coherencia entre ambas pantallas y con la identidad de Amazonia Viva.
- **Estados e interacción:** contemplar campos incompletos, errores de validación, fallo de conexión, envío en curso y confirmación. Conservar los datos no sensibles al corregir errores; evitar envíos duplicados y comunicar cómo continuar.
- **Adaptación y accesibilidad:** revisar móvil y escritorio, navegación por teclado, foco visible, etiquetas asociadas y contraste. Facilitar el uso de autocompletado y gestores de contraseñas sin alterar las reglas de autenticación.
- **Restricciones:** conservar los contratos de API, validaciones y permisos vigentes salvo cambios funcionales que se acuerden expresamente. Las propuestas UX no añaden métodos de autenticación ni conceden roles.

### Relación con MEJ-002

La creación de cuenta debe enlazar con el onboarding correspondiente al rol según el flujo que se acuerde. Deben distinguirse los datos necesarios para crear la cuenta de las preferencias destinadas a personalizar recomendaciones. El destino después del registro y el momento de inicio del onboarding quedan pendientes de definir conjuntamente.

### Orden interno propuesto

1. Revisar las pantallas renderizadas, los campos y las validaciones de cada rol; identificar fricciones con evidencia.
2. Diseñar el flujo y una propuesta visual de ambas pantallas, incluida la transición al onboarding.
3. Implementar el rediseño con los componentes y estilos apropiados del proyecto.
4. Comprobar inicio de sesión, registro por rol, recuperación de errores y resultado visual en móvil y escritorio.

### Decisiones pendientes

- Definir la dirección visual concreta y los componentes compartidos entre ambas pantallas.
- Evaluar si el registro se beneficia de pasos y cómo se comporta al cambiar de rol.
- Definir el destino posterior al registro y la transición al onboarding de MEJ-002.
- Determinar si recuperación de contraseña o verificación de cuenta requieren una mejora separada; no se incorporan como funciones nuevas confirmadas en esta solicitud.

### Validación propuesta

- Las personas distinguen iniciar sesión de crear una cuenta y pueden navegar entre ambos flujos.
- Los tres roles existentes presentan los campos y las validaciones que correspondan.
- Los estados de envío, error y éxito son visibles y permiten continuar sin perder innecesariamente el trabajo.
- Los flujos principales se comprueban con teclado y en móvil y escritorio, además de revisar el resultado renderizado.
- El registro se integra con el onboarding conforme a las reglas que se definan para MEJ-002.

## Registro de decisiones

| Fecha      | Registro                                                                          | Estado                          |
| ---------- | --------------------------------------------------------------------------------- | ------------------------------- |
| 2026-10-16 | Se registra MEJ-004: rediseño UX de inicio de sesión y creación de cuenta usando diseno-ux-web. Se documenta un brief inicial y su relación con el onboarding. | Necesidad confirmada; diseño propuesto por concretar |
| 2026-10-16 | Se registra MEJ-001 a partir de la descripción del usuario.                      | Confirmado como necesidad       |
| 2026-10-16 | Se propone un orden interno y se identifican preguntas para concretar el alcance. | Propuesta pendiente de precisar |
| 2026-10-16 | Se mantiene abierto el orden global hasta conocer las demás mejoras.             | Pendiente                       |
| 2026-10-16 | Se registra MEJ-002: UX del catálogo, onboarding para cuentas nuevas por rol y recomendaciones personalizadas. | Confirmado como necesidad |
| 2026-10-16 | Se proponen etapas para MEJ-002; preguntas, reglas y tecnología quedan pendientes de definir. | Propuesta pendiente de precisar |
| 2026-10-16 | Se registra MEJ-003 y se conserva el documento aportado como referencia del registro de paquetes. | Confirmado como necesidad |
| 2026-10-16 | Se propone un desglose por actividad y una relación con las recomendaciones; la aplicación normativa y las reglas concretas quedan por verificar y definir. | Propuesta pendiente de precisar |
| 2026-10-16 | El usuario amplía MEJ-003 para incluir una interfaz de registro y edición de paquetes más amigable y agradable a la vista. | Confirmado como necesidad |
| 2026-10-16 | El usuario amplía MEJ-003 con una vista informativa que explique en qué se basa el estándar. | Confirmado como necesidad |
| 2026-10-16 | Se implementa MEJ-003 en una rama propia, con ficha técnica por actividad, validación de turismo de aventura, vista informativa pública y presentación en el detalle del paquete. | Implementado; pendiente de revisión e integración |
| 2026-10-16 | A solicitud del usuario, se documenta para MEJ-002 la opción técnica recomendada: diccionarios, conjuntos, vectores y reglas explícitas, con ordenación por afinidad y heap opcional. Se incorpora el cruce planteado de características personales con requisitos y riesgo de actividades. | Propuesta documentada; reglas y campos pendientes de validación |
