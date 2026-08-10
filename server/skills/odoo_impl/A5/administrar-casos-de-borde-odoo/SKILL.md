---
name: administrar-casos-de-borde-odoo
description: >-
  Qué hacer con un rechazo de Odoo que no es un error de dato: clasificar el mensaje, decidir si se
  corrige, se escala o se detiene, y recuperar el estado tras un lote fallido. Úsala solo cuando la
  carga o el QA devuelven algo que el runbook de A5 no cubre.
allowed-tools: odoo_jsonrpc file_read file_modify javascript_code
metadata:
  agente: A5
  tipo: MIX
  prioridad: P1
  depende_de: carga-a-odoo-y-verifica
  siguiente_agente: COORD
  icon: "🩹"
  author: addval
  version: "1.0"
  category: odoo_impl
---

# Casos de borde de la carga

A5 ya validó estructura, formatos, catálogos y referencias antes de escribir. Un rechazo que llega
igual es una de tres cosas: una regla de negocio que solo Odoo conoce, un estado de la instancia que
cambió, o un defecto de diseño aguas arriba. Ninguna se arregla reintentando.

**Regla que gobierna esta skill:** un reintento ciego con el mismo payload gasta iteraciones y no
cambia el resultado. Antes de cualquier segundo intento, tiene que haber cambiado algo — el payload, el
estado de la instancia, o una decisión humana.

## Paso 1 — Clasificar el mensaje

Con el transporte legacy los errores llegan todos con la misma forma, dentro del `error` del JSON-RPC o
en `messages` de un `load`. Clasifica por el **texto**:

| El mensaje dice | Es | Acción |
|---|---|---|
| "No matching record found for external id …" | `E300` | Referencia no resuelta → paso 2 |
| "Invalid field '…' on model" / cabecera desconocida | `E100` | Defecto de plantilla → paso 5 |
| "already exists" / "duplicate key" en un unique | `E400` o recarga | → paso 3 |
| Texto de un `_constraint` o de un `ValidationError` del modelo | `E400` | Regla de negocio → paso 4 |
| "Access Denied" / "not allowed to" | `E500` | Permisos del usuario de integración → detén |
| Timeout, 502/503, conexión cerrada | `E500` | → paso 6 |
| "uid is false" / login | `E500` | Credenciales del nodo. **No pruebes otro host.** Detén |

Si no encaja en ninguna, es `E400` con criterio funcional desconocido: pendiente `regla_negocio` con el
mensaje literal. **Nunca resumas ni parafrasees un mensaje de error de Odoo al escalarlo**: el texto
exacto es lo que un consultor funcional reconoce.

## Paso 2 — Referencia no resuelta en la carga (`E300`)

Ya pasó por A4, así que si aparece acá el mundo cambió entre la validación y la carga, o A4 resolvió
contra la instancia y el registro se borró. Verifica el xmlid concreto:

```
model="ir.model.data", method="search_read",
domain=[["module","=","adv_acme"],["name","=","payment_term_30d"]],
fields=["name","model","res_id"]
```

- **No existe y debía crearlo un archivo anterior** que se cargó OK → el archivo anterior cargó menos
  filas de las que crees. Revisa su bitácora: el `messages` de algún lote traía errores que se leyeron
  como éxito.
- **No existe y es un xmlid nativo de Odoo** (`base.*`, `uom.*`, `l10n_cl.*`) → el módulo no está
  instalado o el nombre es distinto en esta versión. Pendiente `modulo_faltante` o
  `referencia_no_resuelta`.
- **Existe pero apunta a otro modelo** → el diseño referencia el objeto equivocado. Pendiente, no lo
  fuerces.

**No crees el registro faltante para que la referencia resuelva.** Un `res.partner` o una
`product.category` inventada para desatascar un lote deja basura que nadie sabe que existe y que va a
aparecer en un informe contable seis meses después.

## Paso 3 — "Ya existe"

Dos causas con tratamiento opuesto, y confundirlas es el error caro:

- **Es una recarga.** El xmlid ya existía de una corrida anterior. `load()` debería haber actualizado
  en vez de fallar; si falló, es un unique constraint sobre **otro** campo (un `default_code`
  duplicado, un RUT repetido). Ahí el conflicto es con un registro **distinto** que tiene el mismo
  valor natural: es `E400` y va al consultor, porque decidir cuál de los dos es el correcto es una
  decisión de negocio.
- **Colisión de prefijo.** El xmlid existe pero apunta a un registro que este proyecto no creó. Eso
  significa que el `prefijo_xmlid` colisiona con otro proyecto o con un módulo. **Detén la carga
  completa** y escala: seguir sobrescribe registros ajenos.

Distinguirlas: `read` del registro existente y compara con la fila del CSV. Si es el mismo negocio, es
recarga. Si es otro, es colisión.

## Paso 4 — Regla de negocio (`E400`)

Odoo aplicó una validación que el modelo conoce y la plantilla no. Los casos que se repiten:

- **UoM incompatible**: `uom_po_id` en otra `uom.category` que `uom_id`. Corrección de dato, va al
  consultor con el nombre de la categoría correcta.
- **Cuenta contable del tipo equivocado** para el uso (por cobrar en un campo de ingreso). Criterio
  funcional: consultor.
- **Impuesto de venta en un campo de compra** o incoherente con la posición fiscal. Consultor.
- **Moneda del documento distinta de la del diario**. Diseño: pendiente hacia A2.
- **Localización chilena**: comuna como texto libre donde va una entidad; tipo de documento sin diario;
  folios CAF ausentes. El error de folios **no parece de configuración** — el mensaje habla de
  secuencia, no de CAF. Reconócelo y dilo con esas palabras.

Tu trabajo no es decidir el criterio funcional. Es traducir el mensaje de Odoo a algo accionable: qué
fila, qué columna, qué valor, qué esperaba Odoo, y las opciones viables. Después, pendiente
`regla_negocio` y control al Coordinador.

**El resto del archivo sigue.** Un `E400` es una falla de fila: separa las filas rechazadas del lote,
recarga el resto, y reporta las rechazadas. No descartes el archivo entero por dos filas.

## Paso 5 — Defecto de plantilla (`E100` en carga)

Una cabecera que Odoo no reconoce, llegando en la carga y no en la validación, significa que A3 generó
una columna para un campo que no existe, o que A4 no comparó cabeceras. Es un defecto **aguas arriba**:

- No edites la plantilla ni el archivo completado. No es tu carpeta.
- No quites la columna "para que pase". Si la columna estaba, alguien llenó datos ahí, y descartarla en
  silencio pierde información que el consultor cree entregada.
- `fields_get` del modelo para confirmar que el campo efectivamente no existe, y busca el nombre real
  si hay un candidato parecido.
- Pendiente `campo_inexistente` con el nombre que sí existe, si lo hay. El Coordinador re-delega a A3.

## Paso 6 — Error de instancia (`E500`)

- **Timeout o 502/503 en un lote**: el estado es **desconocido**, no fallido. `load()` es transaccional
  por lote, pero un timeout del cliente puede ocurrir con la transacción ya confirmada en el servidor.
  **Verifica antes de reintentar**: consulta `ir.model.data` por los xmlids de ese lote. Están → el
  lote entró, sigue con el siguiente. No están → reintenta ese lote. Reintentar sin verificar es como
  se duplican registros a pesar de la idempotencia, porque el segundo intento puede pegarle a un unique
  sobre otro campo y partir el archivo.
- **Un reintento, no tres.** Si el segundo intento también falla por instancia, detén la carga
  completa: la instancia no está en condiciones y seguir produce un estado a medias imposible de
  auditar.
- **Lotes más chicos** si el timeout es consistente (500 → 200 → 100). Si a 100 filas también hay
  timeout, el problema no es el tamaño.
- **Login o permisos**: no es recuperable desde acá y **no es el host**. Pendiente y control al
  Coordinador.

## Paso 7 — Reportar el estado real

Después de cualquier caso de borde, el estado tiene que quedar escrito, no en tu memoria de la
conversación:

1. Anota en `08-carga/bitacora-<modelo>.jsonl` el lote fallido con el mensaje literal de Odoo y qué
   filas quedaron fuera (en números de fila del CSV, no índices del lote).
2. Si un archivo quedó a medias, dilo con los rangos exactos: "filas 2-301 cargadas, 302-412 no". Un
   "carga parcial" sin rangos obliga a reconstruir a mano qué entró.
3. `carga_completa: false` siempre que haya una fila fuera.

## Nunca

- No reintentes un rechazo de negocio sin cambiar el payload.
- No crees datos maestros para desatascar una referencia.
- No edites `05-plantillas/` ni `06-completadas/`.
- No parafrasees el mensaje de error de Odoo al escalarlo.
- No reintentes un timeout sin verificar primero si el lote entró.
- No reportes como completa una carga con filas fuera.
- No cambies el host ante un fallo de login.
