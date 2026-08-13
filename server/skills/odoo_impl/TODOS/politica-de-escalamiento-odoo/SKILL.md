---
name: politica-de-escalamiento-odoo
description: >-
  Cuándo un agente se detiene y escala en vez de decidir: qué es un pendiente, cómo se escribe, qué
  detiene un archivo y qué detiene la carga completa. Lee esto cuando encuentres algo que no está en
  tu runbook.
metadata:
  agente: TODOS
  tipo: DET
  prioridad: P0
  uso: referencia_compartida
  icon: "🚦"
  author: addval
  version: "1.0"
  category: odoo_impl
---

# Política de escalamiento

Una implementación de Odoo falla de forma silenciosa: un dato mal clasificado se convierte en una
configuración que se convierte en un registro cargado que se convierte en un movimiento contable. El
costo de escalar una duda es minutos; el de adivinar, una restauración de base de datos.

## Regla base

**Si la respuesta no está en tu runbook, en el `blueprint.yaml`, en la introspección o en la
referencia del flujo, no la inventes: escríbela como pendiente y devuelve el control al
Coordinador.** No preguntes por chat tú mismo, no delegues a otro worker, no elijas "la opción más
razonable" en un campo que afecta contabilidad, impuestos, folios o saldos.

Un pendiente no es un fracaso. Un pendiente es el entregable correcto cuando la información no
existe.

## Qué escalar siempre

| Situación | Motivo |
|---|---|
| Un módulo que el blueprint asume no está instalado | `modulo_faltante` |
| Un campo del blueprint o de una referencia no existe en `fields_get` | `campo_inexistente` |
| Una HU no cae limpio en `estandar` / `parametrizable` / `desarrollo` / `integracion` | `clasificacion_dudosa` |
| Un `<campo>/id` apunta a un xmlid que no existe en ningún archivo ni en la instancia | `referencia_no_resuelta` |
| Odoo rechaza por constraint y la corrección requiere criterio funcional | `regla_negocio` |
| Vas a escribir en producción sin confirmación explícita de base + rama | `entorno_produccion` |
| Cualquier otra cosa que te obligue a suponer | `otro` |

## Qué NO es un pendiente

- **Un error de formato con corrección obvia y verificable.** Un RUT con DV mal calculado es `E210`
  con el DV correcto sugerido, no una pregunta. Lo mismo una fecha `10/08/2026` que claramente es
  `2026-08-10`. Reporta el error con la sugerencia; que decida el consultor al corregir el archivo.
- **Un dato que está en un artefacto que aún no leíste.** Lee primero: la introspección, el sidecar
  `.meta.json`, el `blueprint.yaml`, la referencia del flujo. Un pendiente cuya respuesta estaba en un
  archivo del proyecto quema un ciclo humano completo.
- **Una decisión que tu rol sí puede tomar.** A2 decide `fuente: plantilla` vs `configuracion`: es su
  trabajo. A3 decide el orden de las columnas. A5 decide el tamaño del lote de `load`.

## Cómo se escribe un pendiente

En el resultado que devuelves al Coordinador, dentro de `pendientes[]`, con la forma exacta del
contrato (`contrato-implementacion-odoo`):

```json
{
  "id": "P-003",
  "origen": "A3",
  "motivo": "campo_inexistente",
  "pregunta": "El blueprint pide 'l10n_cl_activity_description' en res.partner, pero fields_get no lo reporta. ¿Se usa 'l10n_cl_activity_description' de otro módulo, se omite la columna, o falta instalar l10n_cl_edi?",
  "opciones": ["Omitir la columna", "Instalar l10n_cl_edi y reintroducir", "Usar el campo alternativo <nombre>"],
  "referencia": { "archivo": "05-plantillas/20_res.partner.csv", "fila": 1, "columna": "l10n_cl_activity_description" },
  "respuesta": null,
  "respondido_por": null,
  "respondido_en": null
}
```

Un pendiente útil tiene tres cosas: la **pregunta cerrada** (respondible en una línea), las
**opciones** viables (quien responde no debería tener que investigar), y la **referencia** exacta
(archivo, fila, columna). Sin las tres, el ciclo de respuesta se duplica.

Los tres campos `respuesta` / `respondido_por` / `respondido_en` los llena el Coordinador tras
consultar al usuario. Un worker nunca los escribe.

## Qué detiene qué

Tres niveles, y confundirlos es el error caro:

1. **Fila rechazada** (`E200`, `E210`, `E220`, `E300`, `E310`, `E400`): el archivo continúa. Se
   reportan **todas** las filas malas en una pasada, para que el consultor corrija una vez.
2. **Archivo detenido** (`E100`, `E320`): el archivo no se procesa. No es una falla de dato: el
   archivo o su lugar en el orden están mal, y seguir produce un estado a medias que nadie puede
   auditar. Los demás archivos del lote continúan.
3. **Carga detenida** (`E5xx`): se aborta todo. Instancia caída, timeout, permisos, login. No
   reintentes en bucle; escribe el pendiente y devuelve el control.

Corolario que se olvida: **detenerse no es lo mismo que no reportar.** Un archivo detenido por `E320`
igual produce su `informe-<modelo>.md` diciendo qué dependencia falta y en qué archivo debería estar.

## Precondiciones que el Coordinador verifica antes de delegar

Estas no se saltan; están acá para que un worker pueda rechazar una misión mal formada:

- **A2 no diseña** sin `02-instancia/introspeccion.json` fechada contra la instancia actual.
- **A3 no genera plantillas** con pendientes abiertos que afecten a los modelos de esas plantillas.
- **A4 no valida** archivos que el consultor no ha devuelto a `06-completadas/`.
- **A5 no carga** un archivo con errores abiertos en `07-validacion/`, ni escribe en producción sin
  confirmación explícita.

Si recibes una misión que viola tu precondición: no la ejecutes a medias. Devuelve un pendiente
`otro` explicando qué falta.

## Nunca

- No reintentes un rechazo de negocio sin entender el mensaje. Un reintento ciego con el mismo payload
  gasta iteraciones y no cambia el resultado.
- No inventes datos maestros para que una referencia resuelva. Crear un `res.partner` o una
  `product.category` que no estaba en el blueprint, para que un `<campo>/id` no falle, deja basura que
  nadie sabe que existe.
- No reportes carga parcial como completa. Si hay filas en error, el resultado es parcial, con la
  lista de qué faltó.
- No escribas en la carpeta de otro agente para "arreglar" algo aguas arriba. Observación en
  `01-analisis/preguntas-abiertas.md` y control al Coordinador.
