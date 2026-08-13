---
name: orden-de-carga-odoo
description: >-
  Orden canónico de carga de objetos en Odoo 19 (bloques 0 a 7) con el prefijo NN de cada archivo.
  El orden alfabético del nombre de archivo ES el orden de dependencias. Lee esto antes de numerar
  una plantilla, planificar el backlog o ejecutar una carga.
metadata:
  agente: TODOS
  tipo: DET
  prioridad: P0
  uso: referencia_compartida
  icon: "🔢"
  author: addval
  version: "1.0"
  category: odoo_impl
---

# Orden de carga

Odoo valida las relaciones al escribir. Cargar un producto antes de su categoría, o una factura
antes de su diario, falla — y falla a la mitad, dejando el lote partido. El orden de abajo es el
grafo de dependencias real, aplanado.

**El número `NN` del nombre de archivo ES el orden.** El cargador procesa por orden alfabético de
archivo, así que `20_res.partner.csv` entra antes que `31_product.template.csv` sin lógica extra. Los
números dejan huecos a propósito: insertar un objeto nuevo no obliga a renumerar todo el proyecto.

## Bloque 0 — Compañía y base

| NN | Modelo | Nota |
|---|---|---|
| 01 | `res.company` | Normalmente ya existe: se **configura**, no se carga. Moneda y país antes que todo lo demás. |
| 02 | `res.currency` | Activar las que se usen. La moneda de la compañía no se cambia después de haber movimientos. |
| 03 | `res.users`, `res.groups` | Usuarios y permisos. Un usuario dedicado de integración para la carga. |

## Bloque 1 — Contabilidad (antes que cualquier maestro)

| NN | Modelo | Nota |
|---|---|---|
| 05 | `account.account` | Plan de cuentas. En Chile lo instala `l10n_cl`: **revisa antes de crear**, no dupliques el plan. |
| 07 | `account.tax` | Impuestos. Requiere las cuentas del 05. |
| 09 | `l10n_latam.document.type` | Tipos de documento (33, 34, 39, 61 …). Los trae `l10n_cl`. |
| 11 | `account.journal` | Diarios. Requiere cuentas + tipos de documento. |
| 13 | `account.fiscal.position` | Posiciones fiscales. Requiere impuestos. |
| 15 | `account.payment.term` | Condiciones de pago. Independiente, pero se referencia desde partners. |

Contabilidad va **antes** que partners y productos porque ambos referencian impuestos, posiciones
fiscales y condiciones de pago. Es el error de secuencia más común y el más caro de deshacer.

## Bloque 2 — Partners

| NN | Modelo | Nota |
|---|---|---|
| 20 | `res.partner` (empresas) | `is_company = True`. Primero las matrices. |
| 21 | `res.partner` (contactos hijos) | `parent_id/id` → una empresa del 20. Archivo separado, no filas mezcladas. |
| 23 | `res.partner.bank` | Cuentas bancarias. Requiere el partner. |

En Chile `l10n_cl` debe estar instalado y configurado **antes** del 20: `res.partner` gana `vat`
(RUT+DV), tipo de contribuyente, giro, actividad económica y comuna. Cargar partners primero obliga
a reprocesarlos.

## Bloque 3 — Productos

| NN | Modelo | Nota |
|---|---|---|
| 25 | `uom.category`, `uom.uom` | Solo si se necesitan unidades propias. Las estándar ya existen. |
| 27 | `product.category` | Jerarquía: padres antes que hijos, en el mismo archivo, ordenados. |
| 29 | `product.attribute`, `product.attribute.value` | Solo si hay variantes. |
| 31 | `product.template` | Requiere categoría, UoM, impuestos. El grueso del volumen. |
| 33 | `product.product` | **Solo variantes con datos propios** (código, código de barras, precio extra). Odoo genera las variantes desde los atributos: cargarlas a mano duplica. |
| 35 | `product.supplierinfo` | Requiere producto + partner proveedor. |

## Bloque 4 — Logística

| NN | Modelo | Nota |
|---|---|---|
| 40 | `stock.warehouse` | Crea sus ubicaciones y tipos de operación automáticamente. |
| 42 | `stock.location` | Solo ubicaciones adicionales a las que creó la bodega. |
| 44 | `stock.picking.type` | Solo tipos adicionales. |
| 46 | `stock.route`, `stock.rule` | Rutas multi-paso. Requiere ubicaciones y tipos de operación. |
| 48 | `stock.putaway.rule` | Estrategias de almacenamiento. |

## Bloque 5 — Comercial

| NN | Modelo | Nota |
|---|---|---|
| 50 | `product.pricelist` | |
| 51 | `product.pricelist.item` | Requiere lista + producto/categoría. |
| 53 | `crm.team` | Equipos de venta. Requiere usuarios. |

## Bloque 6 — Fabricación

| NN | Modelo | Nota |
|---|---|---|
| 60 | `mrp.workcenter` | |
| 62 | `mrp.routing.workcenter` | Operaciones. Requiere centro de trabajo. |
| 64 | `mrp.bom` | Requiere productos. |
| 65 | `mrp.bom.line` | Requiere la BoM + los componentes. |

**Listas multinivel: de abajo hacia arriba.** La BoM de un subconjunto se carga antes que la BoM del
producto que lo consume. Si dos BoM se referencian mutuamente hay un ciclo de diseño: escríbelo como
pendiente, no lo fuerces.

## Bloque 7 — Saldos iniciales (siempre al final)

| NN | Modelo | Nota |
|---|---|---|
| 80 | `stock.quant` | Inventario inicial. Requiere productos + ubicaciones. |
| 82 | `account.move` (apertura) | Asiento de apertura. Requiere cuentas + diarios. |
| 84 | `account.move` (facturas abiertas) | Cuentas por cobrar/pagar vivas. Requiere partners + productos + diarios. |

Los saldos van al final por definición: son el estado del negocio sobre una estructura que ya debe
existir completa. Cargar un `stock.quant` sobre un producto que después se corrige deja una
diferencia de inventario que hay que ajustar a mano.

## Verificación de orden antes de cargar

1. Cada archivo tiene prefijo `NN` y el `NN` corresponde a la tabla de arriba.
2. Para cada `<campo>/id` de cada archivo, el xmlid destino está definido en un archivo con `NN`
   **menor o igual**, o ya existe en la instancia. Si está en un `NN` mayor → `E320`, y una `E320`
   **detiene el archivo completo** (ver `politica-de-escalamiento-odoo`).
3. Dentro de un archivo con jerarquía propia (`product.category`, `stock.location`,
   `res.partner` padre/hijo en el mismo archivo), los padres van en filas anteriores a los hijos.
4. Objetos con `fuente: derivado` en el `blueprint.yaml` **no** tienen archivo. Si aparece uno, es un
   error de diseño aguas arriba: pendiente, no carga.
