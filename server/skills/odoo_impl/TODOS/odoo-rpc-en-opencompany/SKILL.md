---
name: odoo-rpc-en-opencompany
description: >-
  Cómo se habla con Odoo 19 desde OpenCompany con la tool odoo_jsonrpc, incluida la carga idempotente
  con load() y la taxonomía de errores E100-E500. Lee esto antes de la primera llamada a Odoo;
  contiene la desviación deliberada respecto de la API JSON-2 y las reglas de seguridad de entorno.
allowed-tools: odoo_jsonrpc
metadata:
  agente: TODOS
  tipo: DET
  prioridad: P0
  uso: referencia_compartida
  icon: "🔌"
  author: addval
  version: "1.0"
  category: odoo_impl
---

# Odoo desde OpenCompany

## La tool, y por qué no hay URL

Toda llamada a Odoo pasa por la tool **`odoo_jsonrpc`**. El host, la base de datos, el usuario y la
API key viven **en el panel del nodo**, no en tus argumentos: el esquema que ves no tiene campo de
URL ni de credenciales. Esto no es una comodidad, es un blindaje — el nodo existe precisamente
porque un modelo conduciendo un `httpRequest` genérico *inventa* el hostname de la instancia a partir
del nombre del cliente y luego reintenta para siempre contra un host que no autentica.

Consecuencia operativa: **si una llamada falla por login, el problema NO es el host.** El mensaje lo
dice explícitamente ("do NOT retry with a different host"). Es base de datos, usuario o API key mal
configurados en el nodo: escribe un pendiente `entorno_produccion` u `otro` y devuelve el control.
Nunca "pruebes otro host".

Argumentos que sí eliges tú:

```
model        "res.partner", "product.template", "ir.model.data", …
method       search_read | read | search | search_count | create | write | unlink | fields_get | call
method_name  obligatorio cuando method="call"
domain       para search / search_read / search_count
fields       para read / search_read  — pide SIEMPRE el mínimo
ids          obligatorio para read / write / unlink
values       obligatorio para create / write
limit        ≤ 1000    offset, order
args, kwargs posicionales / nombrados cuando method="call"
```

Devuelve `{ok: true, result: …}` o `{ok: false, error: {...}}`. El esquema es cerrado
(`extra="forbid"`): un argumento inventado se rechaza antes de salir a la red.

## Desviación deliberada: transporte legacy, no JSON-2

Odoo 19 introdujo la API JSON-2 (`POST /json/2/<modelo>/<metodo>`, `Authorization: Bearer`,
`X-Odoo-Database`, códigos HTTP reales) y anunció la eliminación de `/xmlrpc`, `/xmlrpc/2` y
`/jsonrpc` **para Odoo 20**.

Nuestra tool habla el transporte antiguo: `https://<host>/jsonrpc`, handshake `common.login` →
`object.execute_kw`. Esto es una decisión consciente, no un descuido:

- Odoo 19 **sigue soportando** `/jsonrpc`; la deprecación afecta a la versión siguiente.
- El modelo de objetos es el mismo. `search_read`, `create`, `write`, `fields_get` y `load` son
  métodos del ORM, idénticos en ambos transportes. Lo que cambia es el sobre, no la carta.
- Todo lo que las referencias de este proyecto dicen sobre modelos, campos, cabeceras nativas y
  `load()` aplica sin cambios.

**Lo que sí cambia para ti:**

- Los errores no llegan como códigos HTTP semánticos, sino dentro del `error` del JSON-RPC. Un
  registro inexistente y una regla de negocio violada llegan con la misma forma; clasifícalos por el
  **texto** del mensaje según la taxonomía de abajo.
- No hay endpoint por modelo: siempre `model` + `method`.
- Cualquier método del ORM que no esté en la lista corta se alcanza con `method="call"` +
  `method_name`.

Cuando Odoo 20 retire `/jsonrpc`, el cambio es en el nodo `odooJsonRpc` (un `_rpc` nuevo), no en
estas skills.

## Carga idempotente: `load()`

`load(fields, data)` es el método del importador nativo — el mismo que usa la interfaz al importar un
CSV. Es la forma de cargar, no `create` en bucle: respeta las cabeceras `<campo>/id`, resuelve xmlids
y **actualiza** en vez de duplicar cuando el `id` ya existe.

```
odoo_jsonrpc(
  model="res.partner",
  method="call",
  method_name="load",
  args=[
    ["id", "name", "vat", "property_account_position_id/id"],
    [
      ["adv_acme.partner_761234567", "ACME SpA", "76.123.456-7", "adv_acme.fiscal_pos_general"],
      ["adv_acme.partner_770001112", "Beta Ltda", "77.000.111-2", ""]
    ]
  ]
)
```

Reglas duras:

- **`"id"` debe estar entre las cabeceras.** Sin esa columna la carga duplica en cada corrida. Si no
  está, no llames: es `E100`.
- `data` son **listas de strings**, en el mismo orden que `fields`. Celda vacía = `""`, no `null`.
- Respuesta: `{"ids": [...], "messages": [...]}`. **`messages` no vacío significa que algo falló**,
  aunque `ok` sea `true` y `ids` traiga elementos. Cada mensaje trae `type`, `message`, y a menudo
  `record` (índice de fila 0-based) y `field`. Lee siempre `messages` antes de declarar éxito.
- Un `load` con `messages` de tipo `error` **no escribió nada** de ese lote: es transaccional.
- Lotes de 200-500 filas. Más grande, un error obliga a repetir todo; más chico, multiplica las
  llamadas (y cada tool-result se queda en el historial encareciendo las iteraciones siguientes).

## Comprobaciones de lectura que se usan siempre

```
# ¿Existe este xmlid?  (evita E300 antes de cargar)
model="ir.model.data", method="search_read",
domain=[["module","=","adv_acme"],["name","=","partner_761234567"]],
fields=["module","name","model","res_id"]

# ¿Qué campos tiene realmente este modelo?  (la autoridad, no la memoria)
model="res.partner", method="fields_get", args=[[]],
kwargs={"attributes": ["type","required","selection","relation","string"]}

# ¿Qué módulos están instalados?
model="ir.module.module", method="search_read",
domain=[["state","=","installed"]], fields=["name","shortdesc","state"]

# Versión de la instancia
model="ir.module.module", method="search_read",
domain=[["name","=","base"]], fields=["latest_version"]
```

`fields_get` sobre los modelos del blueprint es la **única** autoridad sobre qué campos existen.
Ninguna lista de campos escrita en una referencia, incluida esta, es autoridad: todo lo marcado
`[VERIFICAR]` se confirma contra la instancia y el resultado se guarda en
`02-instancia/introspeccion.json`.

## Economía de llamadas

Cada resultado de tool queda en el historial del agente y se re-lee en cada iteración siguiente, así
que el costo crece de forma casi cuadrática con las iteraciones. Por eso:

- **`fields` mínimo, siempre.** Un `search_read` sin `fields` trae decenas de columnas por fila y las
  arrastra por el resto del turno.
- **En bloque, no por fila.** Un `search_read` con `domain=[["name","in",[...]]]` en vez de N
  llamadas; un `load` de 300 filas en vez de 300 `create`.
- **Cachea a archivo.** Introspección y maestros van a `02-instancia/*.json` con `fileModify`; los
  pasos siguientes leen el archivo con `fileRead`, no repiten la consulta.
- `limit` explícito en toda exploración. Sin `limit`, una tabla grande inunda el contexto.

## Taxonomía de errores

Clasificación común para el validador (A4) y el cargador (A5). El código determina **quién** corrige.

| Código | Qué es | Corrige | Efecto |
|---|---|---|---|
| `E100` | Estructura del archivo: falta columna `id`, cabecera desconocida, CSV ilegible, sidecar ausente | Agente | **Detiene el archivo completo** |
| `E200` | Campo obligatorio vacío | Consultor | Fila rechazada |
| `E210` | Formato inválido: fecha, número, booleano, RUT con DV incorrecto | Consultor | Fila rechazada |
| `E220` | Valor fuera del catálogo (`selection`, `catalogos` del sidecar) | Consultor | Fila rechazada |
| `E300` | Referencia no resuelta: el xmlid de un `<campo>/id` no existe | Consultor o agente según el caso | Fila rechazada |
| `E310` | xmlid duplicado dentro del archivo | Consultor | Ambas filas rechazadas |
| `E320` | Dependencia fuera de orden: referencia a un xmlid de un archivo `NN` mayor | Agente | **Detiene el archivo completo** |
| `E400` | Regla de negocio de Odoo (constraint, validación del modelo) | Consultor con criterio funcional | Fila rechazada |
| `E500` | Error de instancia: caída, timeout, permisos, login | Agente / infraestructura | **Detiene la carga completa** |

**Una `E100` o una `E320` detienen el archivo entero; cualquier `E5xx` detiene la carga completa.** No
son fallas de fila: significan que el archivo o la instancia no están en condiciones, y seguir
produce un estado a medias imposible de auditar. Todo lo demás se reporta por fila y el archivo
continúa, para que el consultor reciba **todos** los problemas en una pasada y no de uno en uno.

Formato de un error reportado (una fila de `07-validacion/errores-<modelo>.csv`):

```csv
codigo,archivo,fila,columna,valor,mensaje,corrige
E210,20_res.partner.csv,14,vat,76.123.456-8,"DV incorrecto: para 76.123.456 el DV es 7",consultor
E300,31_product.template.csv,7,categ_id/id,adv_acme.categ_insumo,"xmlid no existe; ¿adv_acme.categ_insumos?",consultor
```

Un mensaje de error sin `archivo`+`fila`+`columna` es inútil para quien corrige. Y cuando el valor
erróneo se parece a uno válido, **sugiere el candidato**: es la diferencia entre una corrección de un
minuto y una de media hora.

## Seguridad y entornos

- La API key vive en el parámetro `api_key` del nodo (marcado secreto) o en la variable de entorno
  `ODOO_API_KEY`. **Nunca** en el repositorio, en `blueprint.yaml`, en un artefacto del proyecto, ni
  en un `console`/informe. Si la ves en un archivo, es un hallazgo de seguridad: repórtalo como
  alerta.
- Usuario **dedicado de integración**, nunca la cuenta personal de un consultor: la trazabilidad de
  la carga y la rotación de la clave dependen de eso.
- El acceso a la API externa solo está disponible en planes Custom de Odoo. Si `common.login`
  responde negativo con credenciales correctas, esa es la causa probable.
- **QA y ensayos de carga van contra `staging`, jamás contra producción.** Ramas de Odoo.sh:
  `production`, `staging`, `development`. Staging está neutralizado (correo saliente, crons y pagos
  deshabilitados), que es exactamente lo que hace seguro repetir la carga.
- **Antes de la primera escritura en producción**, confirma explícitamente base de datos y rama, y
  déjalo registrado. Sin esa confirmación, escribir en producción es un pendiente
  `entorno_produccion`, no una decisión del agente.
- El ensayo completo en staging incluye **reconstruir staging desde cero y repetir la carga entera**.
  Es el paso que todos se saltan y el único que detecta las dependencias ocultas entre archivos: una
  carga que funciona sobre una base ya ensuciada por intentos previos no prueba nada.
