---
name: propuesta-addval-connect
description: Genera propuestas comerciales de Addval Connect en el formato HTML de la casa a partir de una necesidad de negocio descrita en lenguaje libre, cubriendo implementaciones y configuraciones de Odoo, desarrollos a medida, integraciones, asesorías ERP, agentes de IA y soporte. Úsala SIEMPRE que aparezca una necesidad de cliente que haya que cotizar, presupuestar o proponer, aunque no se diga la palabra propuesta. Se activa con frases como "el cliente X necesita...", "cotiza esto", "arma un documento para...", "cuánto le cobramos a...", "prepara la OT", "hazme la propuesta de...", y también cuando se pida ajustar, reestructurar o versionar una propuesta existente. Incluye la elección entre modelo secuencial por hitos y modelo por sprints, la numeración de referencia, el calendario de pagos en UF y el Adendo Técnico.
metadata:
  author: addval
  version: "1.0"
  category: business
  icon: "🧾"
  color: "#bd93f9"
---

# Propuesta Comercial — Addval Connect

Convierte una necesidad de negocio descrita en lenguaje libre en una propuesta comercial completa, lista para enviar, con la identidad visual y las convenciones editoriales de Addval Connect.

El destinatario del documento es **un decisor de negocio**, no un equipo técnico. El adendo técnico existe justamente para que el cuerpo comercial no tenga que ser técnico.

## Flujo de trabajo

1. **Extraer lo que ya está dicho.** Lee la necesidad y saca de ahí: cliente, proceso o sistema involucrado, dolor, alcance implícito, plazos, montos si los hay, y quién es la contraparte. Casi siempre hay más información de la que parece.
2. **Elegir el modelo de entrega.** Por defecto, **secuencial por hitos**. Ver "Elección del modelo" abajo.
3. **Supuestos, no interrogatorio.** No hagas una batería de preguntas antes de escribir. Completa los huecos con supuestos razonables, marca cada uno con la clase `placeholder` en el HTML y lístalos al final de tu respuesta en el chat. Si falta el precio o la fecha de inicio y no hay base para inferirlos, esos sí se preguntan — pero después de entregar el borrador, no antes.
4. **Redactar sobre la plantilla.** La plantilla HTML completa está en la referencia `references/plantilla_secuencial.html.txt` (se te entrega junto con esta skill). Tómala como base y reemplaza cada `{{PLACEHOLDER}}`. Nunca toques el CSS del `<head>` ni el bloque de servicios, la tabla de experiencia o el roster de clientes: son bloques fijos de marca.
5. **Verificar.** Ejecuta `python3 scripts/revisar_propuesta.py <archivo.html>`. Corrige todo lo que reporte antes de entregar.
6. **Entregar.** Guarda el HTML en el directorio de salida y preséntalo. En el chat, resume en pocas líneas: número de propuesta, monto total, plazo, y la lista de supuestos que quedaron marcados.

## Elección del modelo de entrega

| Situación | Modelo | Sección de metodología |
|---|---|---|
| Implementación, configuración, migración, integración, proyecto con fecha de producción comprometida | **Secuencial por hitos** (por defecto) | `A. Metodología: Ejecución Secuencial por Hitos` |
| Desarrollo acotado, alcance ya especificado en un documento previo, entrega funcional única | **Sprint** | Ver `references/modelos_alternativos.md` |
| Equipo dedicado, bolsa mensual de horas, acompañamiento continuo sin fecha de término | **Recurrente mensual** | Ver `references/modelos_alternativos.md` |

En una propuesta secuencial **no aparece vocabulario ágil**: nada de sprint, backlog, retrospectiva, iteración, refinamiento. Y la palabra **"cascada" no se usa nunca**, en ningún modelo — describe el trabajo como "hitos secuenciales" o "ejecución secuencial", que es lo que es.

## Reglas editoriales

Estas reglas vienen de propuestas ya enviadas y corregidas. Rómpelas solo si el usuario lo pide explícitamente.

- **Cada dato aparece exactamente una vez.** Si el plazo está en la ficha técnica, no se repite en la promesa. Si el criterio de aceptación está en el cronograma, no se repite en la metodología. La redundancia es el defecto más común y el que más ensucia el documento.
- **La sección de Promesa contiene solo beneficios para el Cliente.** Cero condiciones de pago, cero control de cambios, cero metodología, cero nombres de fases. Si una promesa se puede leer como "nosotros trabajaremos así", está mal escrita: debe leerse como "usted tendrá esto".
- **Ítems opcionales fuera de la tabla de precio fijo.** Un servicio recurrente, una fase condicional o un módulo "si el cliente confirma" van en tabla aparte, con su propio encabezado. Nunca sumados al total del alcance fijo.
- **Los requerimientos de cada hito van en viñetas dentro de la celda de la tabla** (`<ul class="req-list">`), nunca como párrafo corrido.
- **La base horaria no se muestra.** Aunque el precio se haya calculado con horas × tarifa, en el documento aparece el monto en UF y nada más. Excepción: el usuario pide explícitamente mostrarlas.
- **Trabajo fuera de alcance se cotiza aparte y se dice fuerte.** Si la necesidad es un pedido derivado de un proyecto anterior, el documento debe declararlo como fuera del alcance original y facturable de forma independiente, en un bloque visible (`note-box`) y en Control de cambios. No se absorbe.
- **UF siempre, IVA nunca incluido.** Formato `UF 144,00` (coma decimal). Cierra las tablas de precio con la nota "Todos los valores están expresados en UF y no incluyen IVA."
- **Español de Chile, tono directo.** Frases cortas, sin marketing hueco. Nombra los sistemas, cuentas, módulos y personas concretas del cliente: la propuesta debe demostrar que entendimos el problema, y eso se logra con especificidad, no con adjetivos.

## Numeración de referencia

Formato `{LÍNEA}-{CLIENTE}-{NNN}`, correlativo por cliente y línea:

- `ODOO-{CLIENTE}-NNN` — implementación o configuración Odoo
- `DEV-{CLIENTE}-NNN` — desarrollo a medida o integración
- `DGS-{CLIENTE}-NNN` — diagnóstico, asesoría o acompañamiento
- `OT-{CLIENTE}-{LÍNEA}-NNN` — Orden de Trabajo (documento distinto, emitido al aceptar)

Si no se conoce el correlativo, usa `001` y márcalo como supuesto.

## Estructura del documento

El cuerpo comercial son ocho secciones, seguidas del CTA, el botón de aceptación y el Adendo Técnico:

```
1. Entendimiento del Cliente      diagnóstico + dolores + "Lo que proponemos"
2. Addval Connect                 bloque fijo + línea de servicio del proyecto
3. Promesa de la Propuesta        tres promesas numeradas, solo beneficio
4. Valores de la Propuesta        tabla de inversión (+ recurrente aparte si aplica)
5. Condiciones Comerciales        calendario de pagos + términos
6. Información Técnica            ficha componente/definición + incluido / no incluido
7. Experiencia                    bloque fijo, solo se ajusta el párrafo inicial
8. Contacto para el Cierre        qué pasa al aceptar
   CTA + Aceptación               mailto con asunto y cuerpo pre-armados
   Adendo Técnico  A. Metodología · B. Alcance Detallado · C. Equipo y Cronograma
                   D. Dependencias y Prerrequisitos · E. Supuestos y Exclusiones
```

Qué escribir exactamente en cada sección, con ejemplos reales de propuestas enviadas: **`references/guia_secciones.md`**. Léelo antes de redactar; es la parte que más diferencia una propuesta que suena a Addval de una genérica.

## Datos fijos de la firma

Equipo, líneas de servicio, casos de experiencia, roster de clientes, datos de contacto, colores y tipografías: **`references/datos_firma.md`**. Úsalo como fuente única; no inventes nombres, cargos ni casos.

## Salida

Un archivo HTML autocontenido (el CSS va embebido; solo las fuentes y el logo son remotos). Se abre en el navegador y se imprime a PDF con `@page letter`. Nombra el archivo `Propuesta_{NUMERO}_{Cliente}.html`.

Si el usuario pide Word o PDF en vez de HTML, genera igual el HTML como fuente de verdad y conviértelo; el formato de la casa está definido en CSS y perderlo empeora el documento.
