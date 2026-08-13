# Guía de redacción sección por sección

Cada sección tiene un trabajo distinto que hacer. Los ejemplos son de propuestas realmente enviadas.

## Índice

- [1. Entendimiento del Cliente](#1-entendimiento-del-cliente)
- [2. Addval Connect](#2-addval-connect)
- [3. Promesa de la Propuesta](#3-promesa-de-la-propuesta)
- [4. Valores de la Propuesta](#4-valores-de-la-propuesta)
- [5. Condiciones Comerciales](#5-condiciones-comerciales)
- [6. Información Técnica del Servicio](#6-información-técnica-del-servicio)
- [7. Experiencia y 8. Contacto](#7-experiencia-y-8-contacto)
- [CTA y botón de aceptación](#cta-y-botón-de-aceptación)
- [Adendo A — Metodología](#adendo-a--metodología)
- [Adendo B — Alcance Detallado](#adendo-b--alcance-detallado)
- [Adendo C — Equipo y Cronograma](#adendo-c--equipo-y-cronograma)
- [Adendo D — Dependencias y Prerrequisitos](#adendo-d--dependencias-y-prerrequisitos)
- [Adendo E — Supuestos y Exclusiones](#adendo-e--supuestos-y-exclusiones)

---

## 1. Entendimiento del Cliente

Su trabajo es demostrar que entendimos el problema antes de proponer nada. Dos párrafos, cuatro dolores, y un recuadro con lo que proponemos.

**Párrafo 1** — dónde estamos parados. Nombra el sistema, la versión, el área y el proceso concreto.

**Párrafo 2** — el reencuadre. Aquí está el diferenciador de la firma: el problema casi nunca es la herramienta, es el proceso. Nombra la sesión de levantamiento, la fecha y las personas si existieron; da credibilidad inmediata.

> Ejemplo: "La sesión de levantamiento del 15 de julio con Ximena Arias y Nicolás Ernst permitió trabajar en el modelamiento de esta implementación. Lo que muestra ese modelamiento es que el problema no es de contabilidad sino de **circuito**: el gasto existe, el respaldo existe y el activo existe, pero ninguno de los tres tiene un camino definido dentro del sistema. Cada mes, alguien los vuelve a llevar a mano."

**Dolores** (`ul.pain-points-list`, 3 a 5 ítems). Cada uno es `<strong>Título corto:</strong> consecuencia operacional concreta`. El título nombra el síntoma; la descripción explica el costo. Evita dolores genéricos tipo "falta de integración": di qué se rehace, quién lo rehace y cada cuánto.

> Ejemplos: "**Rendiciones transcritas a mano:** cada gasto pagado con la cuenta Bice se registra manualmente en el libro de Operaciones Varias, sin circuito contable estandarizado ni trazabilidad del respaldo."
> "**Validación atada a personas, no a roles:** quién aprueba una rendición no está definido como perfil, de modo que cualquier cambio de organigrama detiene el circuito."

**Lo que proponemos** (`div.value-prop-box`, dos párrafos). El primero, qué haremos en términos de solución. El segundo, qué cambia en el día a día del cliente. Sin precios, sin fases, sin plazos.

---

## 2. Addval Connect

Bloque fijo. Lo único que se escribe es la última línea, que ancla el proyecto a una de las seis líneas de servicio y, si aplica, a la historia previa con el cliente.

> "**Este proyecto corresponde a la línea de Implementación de ERP y Sistemas de Gestión**, como continuidad de la implementación de Odoo Enterprise 17 ya operativa en el holding."

---

## 3. Promesa de la Propuesta

Tres promesas numeradas. Es la sección que lee el decisor si no lee nada más.

Reglas duras:

- Solo beneficio para el Cliente. Nada de condiciones de pago, control de cambios, metodología ni nombres de hitos.
- Título en lenguaje de negocio, no de sistema. "El cierre mensual deja de depender del cálculo manual" ✓ / "Automatización del cálculo de depreciación" ✗
- Un patrón que funciona bien: **(1)** el orden nuevo que queda instalado, **(2)** el trabajo manual que desaparece, **(3)** el compromiso de fecha y qué queda habilitado hacia adelante.

> Ejemplo 03: "**En producción el 31 de agosto.** Cinco semanas desde el kick-off del 20 de julio, con acompañamiento en la salida a producción y 30 días de garantía posteriores. El circuito queda además preparado para replicarse en Asesoría y el resto de las empresas del grupo sin rehacer la configuración."

Nota que la promesa 03 sí menciona fecha y garantía: eso es beneficio, no condición comercial. La diferencia está en si el cliente lo lee como algo que recibe o como algo que debe cumplir.

---

## 4. Valores de la Propuesta

Tabla de dos columnas: componente y monto. Normalmente **una sola fila** más el total: el proyecto completo. El detalle de qué incluye va en la línea gris bajo el nombre del componente, no en filas separadas — desglosar el precio invita a negociar por partes.

Si hay servicio recurrente (hosting, soporte, licencia de mantención), va en **tabla separada** bajo el subtítulo "Servicio recurrente", con su unidad explícita (`UF 0,15 / sociedad / mes`) y su vigencia (`desde el cierre de la garantía`). No suma al total del proyecto.

Cierra siempre con: "Todos los valores están expresados en UF y no incluyen IVA."

---

## 5. Condiciones Comerciales

**Calendario de pagos.** Tabla hito / % / monto / fecha estimada, con fila de total. Estructura típica: 50–50 en proyectos cortos; 20 / 54 / 26 contra hitos entregados en proyectos de desarrollo. Cada hito de facturación se amarra a un acta o aceptación formal, no al calendario. Si hay recurrente, va como fila adicional **bajo** la fila de total, con `—` en el porcentaje.

**Términos.** Lista de viñetas, cada una con etiqueta en negrita. El set base:

- **Modalidad** — precio fijo sobre alcance fijo, facturado en N hitos. No se factura por hora ni por consumo.
- **Moneda** — valores en UF, más IVA. Se factura al valor de la UF del día de emisión.
- **Garantía** — 30 días corridos desde la aceptación formal, sobre [objeto acotado de la garantía].
- **Control de cambios** — todo requerimiento fuera de [documento base] se gestiona mediante addendum a la OT o nueva Orden de Trabajo, con evaluación de impacto en plazo y costo.
- **Condición de inicio** — firma de la Orden de Trabajo y pago del anticipo.
- **Condición de inicio de la construcción/configuración** — aprobación formal de [entregable del hito 1] dentro de los 5 días hábiles siguientes a su entrega.
- **Dependencia de insumos del cliente** — los plazos suponen la entrega oportuna de [insumos]. Un atraso desplaza las fechas de los hitos siguientes.
- **Licenciamiento** — las licencias son provistas y mantenidas por el Cliente y no forman parte de esta propuesta.
- **Vigencia de esta propuesta** — 30 días corridos desde su emisión.

El término de garantía debe acotar **sobre qué** aplica: "sobre la configuración definida en el modelamiento aprobado", "sobre los endpoints y entidades definidos en la Especificación Técnica". Una garantía sin objeto es una garantía abierta.

---

## 6. Información Técnica del Servicio

Un párrafo de resumen, la ficha, y la grilla incluido / no incluido.

**Ficha** — tabla componente / definición. Filas habituales: Tipo de solución, Alcance funcional, Metodología, Plazo, Entregables, más dos o tres filas específicas del proyecto (Circuito contable, Depreciación, Carga de datos, Seguridad y control, Arquitectura, Integraciones...).

**Grilla ✓ / ✗** — cinco o seis ítems por lado, redactados en paralelo. El lado "No incluido" es el que protege el margen: pon ahí lo que el cliente probablemente asuma incluido. Si algo se excluye por una razón técnica, dila entre paréntesis — "Corrección monetaria de activos fijos (sin módulo nativo en Odoo)" convence mucho más que la exclusión pelada.

Cierra remitiendo al Adendo Técnico, para que no se repita nada aquí.

---

## 7. Experiencia y 8. Contacto

Sección 7 es bloque fijo (tabla de casos + roster + Russell Bedford). Solo se escribe el párrafo introductorio, que se orienta a la industria del cliente:

> "Implementaciones de ERP y procesos contables en industrias diversas: manufactura, minería, agroindustria, retail, banca y servicios financieros."

Sección 8 explica qué ocurre al aceptar: se emite la OT, se factura el anticipo, se presenta el cronograma detallado, se confirman responsables de insumos.

---

## CTA y botón de aceptación

**Titular del CTA**: acción concreta en lenguaje del cliente, no eslogan. "Listos para estandarizar Gastos y Activos Fijos" ✓ / "Transformemos juntos su empresa" ✗

**Botón**: `mailto:tecnologia@addval.cl` con asunto y cuerpo URL-encoded. Plantilla del cuerpo:

```
Estimado equipo Addval Connect,

Por medio de la presente, confirmo la aceptación de la propuesta comercial N° {NUMERO} para el proyecto "{TITULO}".

DATOS DEL PROYECTO:
Nombre: {TITULO}
Número de Propuesta: {NUMERO}
Cliente: {CLIENTE}
Representante:

Quedo atento a los próximos pasos para iniciar la implementación.

Saludos cordiales.
```

Codifica espacios como `%20`, saltos de línea como `%0D%0A`, comillas como `%22`, acentos en UTF-8 porcentual.

---

## Adendo A — Metodología

De tres a cinco hitos, cada uno en un `div.phase phase-N`. Estructura de cada hito:

- **Título**: `Hito N — Nombre · semanas X a Y`
- **Descripción**: qué se hace, en concreto. Nombra cuentas, módulos, entidades.
- **Dinámica** (opcional, cuando aporta): cómo se trabaja y por qué así. Es el lugar para justificar decisiones metodológicas. Ej.: "dado que las planillas arrastran 6 a 7 años de historia, el paso por staging existe precisamente para que las inconsistencias aparezcan antes de contabilizar, no después."
- **Cierre**: el criterio verificable que da por terminado el hito. Debe ser algo que ambas partes puedan constatar, no una opinión.

El hito 1 casi siempre es de definición/especificación y su cierre es un documento aprobado que pasa a ser la base contractual del resto. El último hito es puesta en producción y su cierre es el acta de aceptación que gatilla la garantía.

Cierra con la subsección **Control de cambios**, mencionando el cambio más probable de este proyecto en particular.

---

## Adendo B — Alcance Detallado

Tabla de tres columnas: Ámbito / Incluido / No incluido. Un ámbito por dimensión del trabajo. Ámbitos recurrentes: modelamiento, configuración por módulo, datos y carga, seguridad y perfiles, integraciones, documentación y traspaso, post-entrega, licencias e infraestructura.

Cuando un ámbito está completamente fuera, la celda "Incluido" lleva `—` y la de "No incluido" explica el tratamiento alternativo. Esto es más útil que omitir el ámbito: deja constancia de que se conversó.

---

## Adendo C — Equipo y Cronograma

**Equipo**: perfil en negrita, nombre en gris debajo, responsabilidad concreta y distinta para cada uno. Tres o cuatro perfiles. Nombres y cargos reales: ver `datos_firma.md`.

**Cronograma**: tabla Hito / Requerimientos incluidos / Criterio de aceptación. Los requerimientos van en `<ul class="req-list">` dentro de la celda, tres a cinco por hito. El hito 1 es el de aceptación de la propuesta (firma de OT, designación de contraparte, confirmación de accesos), lo que hace visible que el reloj parte con el cliente.

Antes de la tabla, dos líneas: fecha de puesta en producción y cierre de garantía; y una nota indicando cuáles hitos son facturables.

---

## Adendo D — Dependencias y Prerrequisitos

Tres bloques:

1. **Insumos que debe entregar el Cliente** — tabla insumo / propósito / requerido antes de. La columna "propósito" evita que el cliente lo lea como burocracia.
2. **Dependencias Críticas del Cliente** — viñetas. Contraparte con autoridad, disponibilidad para mesas de trabajo, plazos de aprobación (5 días hábiles), plazos de respuesta a consultas (2 días hábiles).
3. **Prerrequisitos Operativos** — viñetas. Instancia operativa, accesos, ambiente de pruebas, licenciamiento vigente, firma de OT y anticipo.

---

## Adendo E — Supuestos y Exclusiones

**Supuestos** — cada uno con su consecuencia si no se cumple. Un supuesto sin consecuencia no protege nada.

> "La contabilización de la rendición contra Fondo Fijo es alcanzable mediante parametrización nativa de la versión 17. Si el resultado del análisis de Arquitectura indica que requiere desarrollo, se aborda mediante addendum con evaluación de plazo y costo."

**Exclusiones** — lista limpia, sin justificaciones largas (esas ya están en la sección 6 y en el ámbito B). Cierra con las tres estándar: desarrollo no descrito en el documento base, licencias/hosting/administración de ambientes, soporte posterior a la garantía.
