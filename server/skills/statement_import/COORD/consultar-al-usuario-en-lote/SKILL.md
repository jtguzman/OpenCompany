---
name: consultar-al-usuario-en-lote
description: >-
  Agrupa todos los pendientes de una sesión en una sola consulta al equipo Tax,
  con contexto suficiente (página, línea, monto, fecha) para responder sin
  reabrir el documento. Úsala en estado REQUIERE_USUARIO. NUNCA una pregunta por
  pendiente ni más de una interrupción por sesión mientras el lote siga abierto.
allowed-tools: file_read write_todos
metadata:
  agente: COORDINADOR
  tipo: LLM
  prioridad: P0
  depende_de: orquestar-sesion-cartola
  author: addval
  version: "2.0"
  category: statement_import
---

# Consultar al usuario en lote

Una cartola puede tener docenas de movimientos y varios tipos de duda a la vez.
Preguntar de a una agota al equipo Tax y degrada sus respuestas. Este es el
único punto donde se interrumpe al usuario, y concentra la disciplina de hacerlo
bien.

El "usuario" es el equipo Tax al otro lado del **chatTrigger** del workflow. El
COORDINADOR surface el lote y recibe la respuesta; los workers A2/A3/A4 nunca
hablan con el usuario, solo devuelven pendientes en el resultado de su TeamTask.

## Entrada

- `pendientes[]` agregados de los TeamTask de los workers (típicamente A3,
  también A2 o A4). El COORDINADOR los junta en un lote. Si un pendiente
  referencia un artefacto del workspace, su ruta relativa viene en el pendiente
  y se lee con **fileRead** para completar el contexto.
- `estado_previo` (en `context`/workspace), para saber a qué worker re-asignar
  cuando el usuario responda.

## Procedimiento

1. Verifica que cada pendiente traiga lo mínimo: motivo, pregunta, referencia
   (página/línea si aplica) y opciones cerradas cuando existan. Si llega
   incompleto, complétalo con **fileRead** (custodio, fecha, cliente) antes de
   mostrarlo.
2. Agrupa por `motivo`, no por orden de aparición. Dentro de cada grupo, ordena
   por página/línea.
3. Prioriza los pendientes bloqueantes de sesión (ej. `cliente_ambiguo`), luego
   los de líneas específicas. Refleja el lote con **writeTodos**.
4. Con opciones cerradas del diccionario del custodio, ofrécelas en su orden;
   nunca sugieras ni reformules.
5. Redacta un único mensaje con todos los pendientes y envíalo por chat (la
   conversación del chatTrigger). No lo dividas salvo límite técnico de longitud.
6. Espera la respuesta por el mismo chat. No reintentes preguntar de otra forma:
   la sesión permanece en `REQUIERE_USUARIO` (TeamTask abierto) hasta que
   contesten. Al llegar la respuesta, `orquestar-sesion-cartola` re-asigna al
   worker de `estado_previo` con las respuestas en `context`.

## Salida

```
Sesión <sesion_id> — Custodio Ameris — Cliente <cliente_nombre>
Tengo 3 dudas para poder continuar con esta cartola:

1) Código de movimiento no documentado (página 4, línea "REUS CFIAMG3R-E", $XXX, 12/07/2024)
   ¿A qué concepto corresponde el código 'REUS': dividendo, interés, devolución de capital u otro?

2) Instrumento sin match en Odoo (página 3)
   El nemotécnico 'CFIAMG3R-E' no aparece en las tablas de posiciones. ¿A qué instrumento corresponde?

3) Disminución de capital (página 5, línea …)
   [texto fijo del motivo disminucion_capital]
```

## Casos de borde

- **Sesión con un único pendiente**: igual pasa por esta skill y el mismo canal,
  para mantener formato y tono.
- **El usuario responde algo fuera del lote actual** (ej. corrige una sesión
  anterior): no lo aceptes como respuesta a un pendiente de esta sesión. Aclara
  por chat a qué `sesion_id` y pendiente corresponde antes de aplicarlo.
- **El usuario pide más contexto** (ej. ver la imagen de la página): esta skill
  puede proveerlo — el COORDINADOR lee la página con **fileRead** (`.jpeg` o
  texto) y la comparte — sin contar como segunda interrupción.
