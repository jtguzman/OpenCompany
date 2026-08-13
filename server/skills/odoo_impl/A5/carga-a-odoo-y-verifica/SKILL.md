---
name: carga-a-odoo-y-verifica
description: >-
  Runbook completo del Agente A5: aplica la configuración por RPC, carga los archivos validados con
  load() en orden de dependencias, verifica con read-back, y ejecuta los casos de QA de cada flujo.
  ÚNICO punto de escritura del sistema. Ejecuta los pasos en orden.
allowed-tools: odoo_jsonrpc file_read file_modify fs_search javascript_code
metadata:
  agente: A5
  tipo: MIX
  prioridad: P0
  depende_de: valida-archivos-completados
  siguiente_agente: COORD
  icon: "🚀"
  author: addval
  version: "1.0"
  category: odoo_impl
---

# Cargar a Odoo y verificar (runbook A5)

**Único punto de escritura del sistema.** Ningún otro agente escribe en Odoo. Lo que hagas acá es lo
único que no se deshace con un archivo corregido: deshacer una carga significa restaurar la base de
datos.

Lee `odoo-rpc-en-opencompany` (transporte, `load()`, taxonomía, reglas de entorno),
`orden-de-carga-odoo`, `convencion-ids-externos` y `contrato-implementacion-odoo`. De
`flujos-de-referencia`, abre solo los flujos del proyecto: sus "casos canónicos de QA" son la base del
paso 5. Skill adicional solo si hay rechazos que no son de dato: `administrar-casos-de-borde-odoo`.

Escribes en `08-carga/` y `09-qa/`, en ninguna otra carpeta.

## Precondiciones (verifícalas; no las asumas)

1. `07-validacion/` existe y trae la lista `cargables`. **Solo cargas los archivos de esa lista.** Un
   archivo `CON_ERRORES` o `DETENIDO` no se carga ni parcialmente.
2. **Entorno confirmado.** `file_read` del `blueprint.yaml` → `entorno_objetivo`. Si es `production` y
   la misión no trae confirmación explícita de **base de datos y rama**, no escribas: pendiente
   `entorno_produccion` y devuelve el control. "Adelante" no es una confirmación de entorno.
3. Cero pendientes con `respuesta: null` que afecten a los modelos a cargar.

## Paso 1 — Aplicar la configuración (`fuente: configuracion`)

Del `blueprint.yaml`, los objetos `fuente: configuracion` los escribes tú directo, en el orden `nn`.
Pocos registros, valores decididos en el diseño.

**Antes de crear, busca.** Los objetos de configuración son justo los que la localización suele haber
creado ya — el plan de cuentas de `l10n_cl` es el caso clásico, y duplicarlo deja dos planes
convivientes que nadie limpia después:

```
model="account.account", method="search_read",
domain=[["code","in",["1101","1102"]]], fields=["code","name"], limit=200
```

Existe → `write` con lo que el diseño cambia, y registra como actualizado. No existe → créalo **con su
xmlid**, vía `load()` (no `create`), para que quede referenciable por los archivos posteriores. Un
registro de configuración creado con `create` no tiene xmlid, y cualquier `<campo>/id` que lo apunte
va a fallar con `E300` en el archivo siguiente.

Registra cada objeto en `08-carga/bitacora-<modelo>.jsonl` igual que una carga.

## Paso 2 — Cargar los archivos, en orden

Orden alfabético de nombre de archivo — el prefijo `NN` **es** el orden de dependencias, así que no
hace falta otra lógica. Por archivo:

1. `file_read` del CSV y de su `.meta.json`.
2. Convierte a `fields` (la cabecera) + `data` (listas de strings, celda vacía = `""`) con
   `javascript_code`. **`"id"` tiene que estar en `fields`**; si no está, no llames — es `E100` y el
   archivo no debió llegar a esta lista.
3. Trocea en lotes de **200 a 500 filas**. Más grande, un error obliga a repetir todo el archivo; más
   chico, multiplica las llamadas y cada tool-result se queda en el historial encareciendo cada
   iteración siguiente.
4. Por lote:

```
odoo_jsonrpc(model="res.partner", method="call", method_name="load",
             args=[["id","name","vat","property_payment_term_id/id"],
                   [["adv_acme.partner_761234567","ACME SpA","76.123.456-7","adv_acme.payment_term_30d"],
                    ["adv_acme.partner_770001112","Beta Ltda","77.000.111-2",""]]])
```

**`load()` es idempotente por diseño**: el `id` existente se actualiza en vez de duplicar. Esa es toda
la razón por la que la columna `id` es obligatoria y por la que este paso se puede repetir.

**La lectura de la respuesta es el paso que se hace mal.** `load` devuelve
`{"ids": [...], "messages": [...]}`, y `ok: true` con `ids` poblado **no significa éxito**:

- `messages` vacío → el lote entró completo.
- `messages` con `type: "error"` → **el lote no escribió nada** (es transaccional). Cada mensaje trae
  `record` (índice de fila 0-based **dentro del lote**) y a menudo `field`. Traduce el índice a número
  de fila del CSV antes de reportarlo, o el consultor busca en la fila equivocada.
- `messages` con `type: "warning"` → entró, pero anótalo en la bitácora.

Un lote con error: **no lo reintentes igual.** Clasifica el mensaje con la taxonomía. `E400` (regla de
negocio) o algo que no es de dato → `administrar-casos-de-borde-odoo`. `E5xx` → detén la carga
completa y devuelve el control.

Bitácora, una línea JSON por lote en `08-carga/bitacora-<modelo>.jsonl`:

```json
{"archivo":"20_res.partner.csv","lote":1,"filas":300,"desde":2,"hasta":301,"ids":[1042,1043],"creados":298,"actualizados":2,"messages":[]}
```

Con `desde`/`hasta` en números de fila del CSV, la bitácora es auditable contra el archivo original.

## Paso 3 — Verificar con read-back (obligatorio)

Un `load` sin errores no prueba que los registros quedaron como querías: prueba que Odoo aceptó la
escritura. Por archivo cargado, una consulta en bloque:

```
model="ir.model.data", method="search_read",
domain=[["module","=","adv_acme"],["model","=","res.partner"]],
fields=["name","res_id"], limit=1000
```

Compara el conteo y el conjunto de `name` contra los `id` del CSV. Diferencia → repórtala; no la
expliques como "probablemente el filtro". Con más de 1000 registros, pagina con `offset`.

Para los modelos con campos calculados que importan (impuestos en un producto, cuentas en un diario),
un `read` de muestra de 3-5 registros con `fields` mínimos. No de todos: el objetivo es detectar un
mapeo sistemáticamente mal, y eso se ve en tres filas.

## Paso 4 — Escribir el resumen de carga

`08-carga/resumen-carga.md`: por modelo, filas del archivo, creados, actualizados, rango de xmlids, y
errores con su código. Referencia por **xmlid**, no por id numérico: el id numérico de staging no
significa nada en producción, y este resumen es lo que se lee al replicar la carga.

**`actualizados > 0` en una primera carga no es normal.** Significa que esos xmlids ya existían: o es
una recarga, o el prefijo colisiona con otro proyecto. Dilo explícitamente en el resumen; no lo
reportes como éxito silencioso.

## Paso 5 — Ejecutar el QA

Genera `09-qa/casos.yaml` desde los casos canónicos de la referencia de cada flujo, cruzados con los
`criterios_aceptacion` de `00-entrada/historias.csv`. Un caso por criterio verificable.

```yaml
- id: QA-007
  hu: [HU-014]
  flujo: ventas
  descripcion: Cotización a cliente mayorista aplica lista de precios
  pasos:
    - modelo: sale.order
      metodo: create
      valores: {partner_id_xmlid: adv_acme.partner_761234567, order_line: [...]}
    - modelo: sale.order
      metodo: action_confirm
  aserciones:
    - "pricelist_id == adv_acme.pricelist_mayorista"
    - "amount_total == 119000"
    - "len(picking_ids) == 1"
```

Ejecución:

- **Solo en staging.** El QA crea documentos reales — órdenes, entregas, facturas, movimientos
  contables. Si `entorno_objetivo` es `production`, **no ejecutes el QA**: repórtalo como no ejecutado
  y por qué. Staging está neutralizado (correo saliente, crons y pagos deshabilitados) y eso es
  exactamente lo que lo hace seguro.
- Resuelve los xmlids a ids con `ir.model.data` antes de cada `create`.
- Métodos de acción (`action_confirm`, `action_post`, `button_validate`) con `method="call"` +
  `method_name` + `args=[[<id>]]`. **Muchos devuelven `False` incluso cuando hubo errores por
  registro**, así que después de cada acción **relee** el estado (`state`, y el campo que la aserción
  mira). Una acción que "no falló" no significa que hizo lo que esperabas.
- Un caso rojo no detiene el QA: sigue con los demás. Un caso rojo es configuración incompleta, y hay
  que saber cuántas y cuáles.

`09-qa/resultados-<flujo>.md` por flujo: caso, verde/rojo, aserción que falló, valor obtenido vs.
esperado. `09-qa/evidencia/` con los ids de los documentos creados, para que alguien pueda abrirlos.

Un caso rojo se reporta como **caso**, con su `id` y qué aserción falló — nunca como "hubo un problema
en ventas".

## Paso 6 — El ensayo completo (dilo, aunque no lo hayas hecho)

Una carga incremental sobre una base ya ensuciada por intentos previos **no prueba que el orden de
carga sea correcto**. El ensayo válido es reconstruir staging desde cero y repetir la carga entera; es
el paso que todos se saltan y el único que detecta las dependencias ocultas entre archivos.

No puedes reconstruir staging tú (es una operación de Odoo.sh, no de RPC). Lo que sí tienes que hacer
es **reportar si se hizo o no**. Sin ese dato, el informe de cierre se lee como "listo para
producción" y no lo es.

## Salida (un resultado al COORD)

```json
{
  "resultado_carga": {
    "archivos_ok": 6,
    "archivos_error": 1,
    "registros_creados": 1689,
    "registros_actualizados": 4,
    "por_modelo": [
      {"modelo": "res.partner", "creados": 306, "actualizados": 4,
       "rango_xmlid": "adv_acme.partner_*", "errores": {}}
    ],
    "errores": [
      {"codigo": "E400", "archivo": "31_product.template.csv", "fila": 412,
       "columna": "uom_po_id", "mensaje": "UoM de compra en otra categoría que la UoM"}
    ],
    "bitacoras": ["08-carga/bitacora-res.partner.jsonl"],
    "resumen": "08-carga/resumen-carga.md"
  },
  "resultado_qa": {
    "entorno": "staging",
    "casos_total": 16,
    "casos_ok": 14,
    "casos_fallidos": [
      {"id": "QA-007", "flujo": "ventas", "motivo": "pricelist_id quedó en la lista pública; falta property_product_pricelist en el partner"}
    ],
    "resultados": ["09-qa/resultados-ventas.md"]
  },
  "ensayo_desde_cero": false,
  "carga_completa": false,
  "pendientes": []
}
```

`carga_completa: false` si hay un solo archivo en error o un caso de QA rojo. Nunca reportes carga
parcial como completa.

## Nunca

- No cargues un archivo que no está en `cargables`.
- No escribas en producción sin confirmación explícita de base de datos y rama.
- No ejecutes el QA en producción.
- No uses `create` en bucle donde va `load()`: pierdes el xmlid y la idempotencia.
- No declares éxito por `ok: true` sin haber leído `messages`.
- No reintentes ciegamente un rechazo de negocio; pasa por `administrar-casos-de-borde-odoo`.
- No crees datos maestros que no estaban en el blueprint para que una referencia resuelva.
- No reportes carga parcial como completa, ni omitas el estado del ensayo desde cero.
