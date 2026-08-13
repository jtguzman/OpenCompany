# Modelos alternativos de entrega

El modelo por defecto es **secuencial por hitos** y está resuelto en la referencia `references/plantilla_secuencial.html.txt`. Este archivo cubre los dos casos en que no aplica.

En ambos casos se conserva la misma estructura de ocho secciones, la misma marca y las mismas reglas editoriales. Lo que cambia es la sección de metodología, la tabla de inversión y el calendario de pagos.

---

## Modelo Sprint

**Cuándo usarlo.** Desarrollo acotado con alcance ya conocido — típicamente un ajuste, un reporte, un endpoint o una funcionalidad derivada de un desarrollo previo. No hay fase de diseño independiente porque la definición ya existe. Duración típica: uno o dos sprints de dos semanas.

**Qué cambia en el documento:**

- El título de la metodología pasa a `4. Metodología: Sprint de Desarrollo` y el bloque `div.phase phase-1` describe un único sprint con: levantamiento, desarrollo, pruebas y demo de cierre.
- Aquí **sí** se usa el vocabulario de sprint, porque el modelo es ese. Lo que sigue prohibido es mezclarlo con el modelo secuencial en un mismo documento.
- La demo de cierre se describe explícitamente como validación sobre el ambiente real del cliente, no sobre mockups ni prototipos. Es un diferenciador y conviene decirlo.
- El precio se determina **prorrateando la tarifa base de sprint** según las horas estimadas. Las horas pueden mencionarse dentro del bloque de metodología como "Horas estimadas", pero no aparecen en la tabla de precios.
- Calendario de pagos simple: firma de OT, inicio de sprint, y 100% contra entrega funcional y aceptación formal. Las dos primeras filas llevan `—` en el porcentaje.

**Redacción tipo del bloque de sprint:**

> **Sprint de Desarrollo (Precio Fijo · 2 semanas)**
> Dado que [la definición previa ya existe], este requerimiento es acotado y no requiere una fase de diseño independiente. El trabajo se ejecuta en un único sprint de 2 semanas con entrega funcional real al cierre.
>
> **Dinámica del sprint:** Levantamiento · Desarrollo · Pruebas · Demo de cierre
>
> **Duración:** 2 semanas · **Entregables:** [lista] · **Garantía:** 30 días post-entrega

**Nota de alcance.** Cierra el bloque con la frase de contención: cualquier cambio de alcance fuera de lo definido —otros reportes, módulos o funcionalidades— se gestiona mediante addendum formal o nueva Orden de Trabajo, con evaluación de impacto en plazo y costo.

---

## Modelo Recurrente Mensual

**Cuándo usarlo.** Equipo dedicado o bolsa mensual de horas, acompañamiento continuo, soporte evolutivo. No hay fecha de término ni entregable único.

**Qué cambia en el documento:**

- La metodología pasa a `4. Metodología: Trabajo Mensual (Equipo Dedicado)` y describe la cadencia: reuniones de coordinación, priorización mensual de requerimientos con la contraparte, reporte de avance y cierre mensual.
- La tabla de inversión expresa un **valor mensual** con la dedicación asociada (perfiles y horas comprometidas al mes). El total no es un monto de proyecto sino un monto por período.
- El calendario de pagos es mensual, facturado por mes vencido contra reporte de avance aceptado.
- Términos adicionales: plazo mínimo de contratación, aviso previo de término (30 o 60 días corridos), y qué ocurre con las horas no consumidas — por defecto **no se acumulan** al mes siguiente, salvo pacto expreso.
- La sección de garantía se reemplaza por SLA de respuesta y resolución si el servicio incluye soporte.

**Riesgo comercial a cubrir.** En este modelo el alcance es abierto por diseño, así que el control debe estar en la priorización: deja explícito que la bolsa mensual se prioriza en conjunto con la contraparte y que los requerimientos que excedan la capacidad del mes se reagendan, no se absorben.

---

## Trabajo fuera de alcance de un proyecto anterior

No es un modelo de entrega, pero sí un caso que aparece seguido y se trata distinto.

Cuando la necesidad es un pedido derivado de un proyecto ya cerrado o en curso, la propuesta debe:

1. Declararlo en la sección 1, con una frase directa: este requerimiento no forma parte del alcance de [proyecto/OT anterior] y se cotiza de forma independiente.
2. Incluir un `div.note-box` visible en la sección 6 o en el adendo A repitiendo la condición.
3. Reforzarlo en Control de cambios, referenciando la OT original.

No se absorbe, no se descuenta y no se presenta como "cortesía". El punto de la propuesta es justamente hacer visible que hay trabajo adicional con costo adicional.
