# Informe de ejecución — CartolaTax Statement Import

**Run analizado:** 2026-08-06, ~22:12 → 22:29 (hora local del log)
**Cartola:** BTG Pactual (`cartola.pdf`)
**Resultado:** cartola cargada a Odoo, casos de borde manejados correctamente
**Modelo:** `claude-sonnet-4-6` (todos los agentes)
**Estructura de skills:** post-optimización (15 skills, runbook único por agente)

> Orientado al esfuerzo, iteraciones y costos por etapa, para pensar
> optimizaciones posteriores. **No incluye acciones de optimización** — es
> línea base de medición.

---

## 1. Esfuerzo por etapa

| Etapa | Agente (nodo) | LLM steps¹ | Duración² | Llamadas Odoo | Otras tools |
|---|---|---|---|---|---|
| **A1** Procesa archivo | coding_agent | 14 | 1m21s | — | shell, fileRead×2, fsSearch |
| **A2** Interpreta | aiAgent | 14 | 1m47s | — | fileRead×5, fsSearch×6, fileModify |
| **A3** Consolida | task_agent | 21 | 4m37s | 13 ok / **1 fail** | javascriptExecutor×2, fileModify |
| **A4** Importa | tool_agent | 22 | 5m14s | 7 ok / **2 fail** | javascriptExecutor×3, fileModify×3 |
| **COORD** | ai_employee | ~13 (repartido) | (orquesta) | — | taskManager×14, writeTodos×12, console×5 |
| **TOTAL** | | **~71** | ~13m netos | 20 ok / 3 fail | |

¹ *LLM step* = una llamada al modelo = un round-trip. Es la unidad de costo
real: en la iteración N el modelo re-lee todo el historial de las N-1
anteriores, por lo que el costo crece de forma casi cuadrática con las
iteraciones dentro de un mismo agente.

² Duración tomada de `team_tasks.created_at → completed_at` en la DB (fuente
confiable). El wall-clock total A1→A4 fue ~16m39s, pero incluye esperas de
input del usuario (respuesta a pendientes por chat).

---

## 2. Costo (estimación — NO medido)

**No hay datos de tokens.** El `AgentWorkflow` de Temporal agrega uso dentro del
loop pero **no lo persiste** vía `CompactionService`: `token_usage_metrics` = 0
filas. Solo se registró `api_usage_metrics` (28 filas, servicios no-LLM). Es una
limitación conocida del proyecto (ver CLAUDE.md → Memory Compaction: "executions
without connected memory still aggregate usage inside the loop but do not create
session compaction records").

**Proxy de costo** = `LLM steps × tamaño de contexto`. Como el historial crece
cada iteración, A3 (21 steps, historial hasta ~37 msgs) y A4 (22 steps, hasta
~42 msgs) **dominan el gasto**. Estimación grosera: **A3 + A4 ≈ 60-70%** del
costo total del run. A1 y A2 son baratos (14 steps c/u, historiales cortos).

---

## 3. Comparación vs run pre-optimización (A4, comparable)

Mismo A4, medido en el run anterior (~21:29-21:34, antes de fusionar skills +
inyectar el contrato Odoo exacto):

| Métrica A4 | Antes | Ahora | Δ |
|---|---|---|---|
| LLM steps | 33 | 22 | **−33%** |
| Llamadas Odoo | 18 | 9 | **−50%** |
| Máx. iteraciones en un tramo | 24 | 17 | **−29%** |

La fusión de skills (una carga de instrucciones en vez de N) + el contrato Odoo
inline (modelos reales, `financial_instrument_id`+nombre del `default_code`,
redondeo 4dp, `line_ids` nunca vacío) eliminaron el descubrimiento por prueba y
error del esquema de Odoo.

---

## 4. Dónde está el gasto restante (candidatos a optimización futura)

1. **A4 es el más caro** (22 steps, 5m14s). Los 2 fallos fueron **datos de
   negocio reales, no bugs**:
   - `moneda USD no coincide con instrumento (CLP)` (error #8 de Odoo).
   - `administrador del instrumento (MBI AGF) ≠ custodio (BTG PACTUAL)` (#12.2).
   El agente gastó ~5 steps recuperándose. **Idea:** que A3 pre-valide moneda y
   administrador contra el producto en el paso de emparejar, para que A4 nunca
   los envíe mal.

2. **A3: 1 fallo `partner_id`** — buscó duplicados con un campo inexistente en
   `kardex.import.log` (el header usa `custodian_id`). **Ya corregido en el
   skill `consolida-informacion`** con los campos exactos del search; el próximo
   run debería bajar A3 de 21 a ~15 steps. (Corrección hecha, no medida aún.)

3. **Historiales largos** (A3/A4 llegan a 37-42 mensajes): cada tool-result de
   Odoo queda en contexto y se re-lee cada iteración. **Idea:** cachear
   resultados a archivo y pasar solo rutas (ya diseñado en `obtener-maestros`);
   pedir `fields` mínimos en cada `search_read`.

4. **Sin visibilidad de tokens** — optimización de *instrumentación* prioritaria:
   conectar `simpleMemory` a los agentes o persistir el agregado del
   `AgentWorkflow` vía `CompactionService`, para medir costo real por etapa en
   vez de estimarlo.

---

## 5. Puntos fuertes observados

- Pipeline A1→A2→A3→A4 **auto-encadenado** vía `task_manager`, sin intervención
  manual entre etapas.
- **Casos de borde bien gestionados**: A3 levantó 3 pendientes legítimos (código
  ambiguo, posición, tipo de cambio), el usuario respondió por chat, y A4 aplicó
  las respuestas.
- **Cero fallos de esquema o de conexión** — los 3 fallos de Odoo fueron todos de
  negocio, con mensaje claro y accionable.

---

## Anexo — cómo se obtuvieron las métricas

- **LLM steps por etapa:** conteo de líneas `Agent LLM step` en el log del dev
  server, acotado por la ventana de tiempo de cada `team_task`.
- **Duración por etapa:** `team_tasks.created_at → completed_at` (DB
  `workflow.db`, `workflow_id='8'`).
- **Llamadas Odoo:** `Node 8:odooJsonRpc:1 succeeded|failed` (A3, lectura) y
  `:2` (A4, escritura).
- **Comparación:** mismo A4 en la ventana del run anterior del mismo log.
- **Tokens:** no disponibles (`token_usage_metrics` vacía).
