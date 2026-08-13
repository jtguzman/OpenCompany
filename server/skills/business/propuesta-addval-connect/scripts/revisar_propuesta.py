#!/usr/bin/env python3
"""Revisión automática de una propuesta comercial de Addval Connect.

Uso:
    python3 revisar_propuesta.py Propuesta_ODOO-ACME-001_Acme.html

Chequea lo que se puede chequear a máquina: placeholders sin reemplazar,
vocabulario prohibido, estructura de secciones, consistencia de montos y
fugas de contenido comercial hacia la sección de Promesa. El juicio editorial
—si la propuesta se entiende, si los dolores son concretos— sigue siendo humano.

Salida: reporte por consola. Código 1 si hay errores, 0 si solo hay avisos.
"""

import re
import sys
import unicodedata
from pathlib import Path

SECCIONES_CUERPO = [
    "1. Entendimiento del Cliente",
    "2. Addval Connect",
    "3. Promesa de la Propuesta",
    "4. Valores de la Propuesta",
    "5. Condiciones Comerciales",
    "6. Información Técnica del Servicio",
    "7. Experiencia",
    "8. Contacto",
]

SECCIONES_LEGADO = [
    "Antecedentes y Diagnóstico",
    "Resumen Ejecutivo",
    "Objetivos y Alcance",
    "Inversión y Estructura de Tarifas",
    "Términos y Prerrequisitos",
]

SECCIONES_ADENDO = [
    "A. Metodología",
    "B. Alcance Detallado",
    "C. Equipo y Cronograma",
    "D. Dependencias y Prerrequisitos",
    "E. Supuestos y Exclusiones",
]

# Vocabulario ágil, prohibido en propuestas de modelo secuencial.
VOCABULARIO_AGIL = ["sprint", "backlog", "retrospectiva", "iteracion", "refinamiento", "daily", "scrum"]

# Prohibido en cualquier modelo.
VOCABULARIO_PROHIBIDO = ["cascada", "waterfall"]

# Términos comerciales que no deben aparecer en la sección de Promesa.
FUGAS_EN_PROMESA = ["factura", "anticipo", "iva", "pago del", "addendum", "orden de trabajo", "hito 1", "hito 2"]


def normalizar(texto):
    """Minúsculas sin acentos, para buscar palabras clave de forma robusta."""
    t = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def a_numero(monto):
    """'1.234,50' -> 1234.5 ; '120' -> 120.0"""
    try:
        return float(monto.replace(".", "").replace(",", "."))
    except ValueError:
        return None


def sin_etiquetas(html):
    html = re.sub(r"<style.*?</style>", " ", html, flags=re.S)
    html = re.sub(r"<script.*?</script>", " ", html, flags=re.S)
    html = re.sub(r"<!--.*?-->", " ", html, flags=re.S)
    return re.sub(r"<[^>]+>", " ", html)


def extraer_seccion(html, titulo):
    """Devuelve el HTML de la sección cuyo section-title empieza con `titulo`."""
    patron = re.compile(
        r'<h2 class="section-title">\s*' + re.escape(titulo) + r".*?(?=<h2 class=\"section-title\">|</body>)",
        re.S,
    )
    m = patron.search(html)
    return m.group(0) if m else ""


def revisar(ruta):
    html = Path(ruta).read_text(encoding="utf-8")
    texto = sin_etiquetas(html)
    plano = normalizar(texto)
    errores, avisos = [], []

    # --- Placeholders sin reemplazar -------------------------------------
    pendientes = sorted(set(re.findall(r"\{\{([A-Z0-9_]+)\}\}", html)))
    if pendientes:
        muestra = ", ".join(pendientes[:12])
        resto = f" (+{len(pendientes) - 12} mas)" if len(pendientes) > 12 else ""
        errores.append(f"{len(pendientes)} marcador(es) sin reemplazar: {muestra}{resto}")

    # Restos de la plantilla que suelen quedar olvidados
    for resto in ("<!-- OPCIONAL", "FIN OPCIONAL", "PLANTILLA — PROPUESTA COMERCIAL"):
        if resto in html:
            avisos.append(f"Quedó un comentario de plantilla en el HTML: {resto!r}")

    # --- Estructura -------------------------------------------------------
    faltan = [s for s in SECCIONES_CUERPO if s not in html]
    presentes_legado = sum(1 for s in SECCIONES_LEGADO if s in html)
    if len(faltan) == len(SECCIONES_CUERPO) and presentes_legado >= 3:
        avisos.append(
            "El documento usa la estructura antigua (Antecedentes / Resumen Ejecutivo / Objetivos y "
            "Alcance / Inversión). La estructura vigente es la de ocho secciones con Adendo Técnico."
        )
    elif faltan:
        errores.append("Faltan secciones del cuerpo comercial: " + "; ".join(faltan))

    tiene_adendo = "Adendo Técnico" in html
    if tiene_adendo:
        faltan_ad = [s for s in SECCIONES_ADENDO if s not in html]
        if faltan_ad:
            avisos.append("Faltan secciones del Adendo Técnico: " + "; ".join(faltan_ad))
    else:
        avisos.append("El documento no incluye Adendo Técnico. Solo es correcto en propuestas muy acotadas.")

    # --- Vocabulario ------------------------------------------------------
    for palabra in VOCABULARIO_PROHIBIDO:
        if palabra in plano:
            errores.append(f"Palabra prohibida en cualquier modelo: {palabra!r}")

    es_secuencial = "Ejecución Secuencial por Hitos" in html
    if es_secuencial:
        for palabra in VOCABULARIO_AGIL:
            if palabra in plano:
                errores.append(
                    f"Vocabulario ágil {palabra!r} en una propuesta de modelo secuencial. "
                    "Reemplázalo por lenguaje de hitos."
                )

    # --- Promesa limpia ---------------------------------------------------
    promesa = normalizar(sin_etiquetas(extraer_seccion(html, "3. Promesa de la Propuesta")))
    for fuga in FUGAS_EN_PROMESA:
        if fuga in promesa:
            errores.append(
                f"La sección de Promesa menciona {fuga!r}. Esa sección lleva solo beneficios para el Cliente."
            )

    # --- Montos -----------------------------------------------------------
    montos = re.findall(r"UF\s*([\d.]+,\d{2}|\d+(?:[.,]\d+)?)", texto)
    if not montos:
        errores.append("No se encontró ningún monto en UF. Todos los precios se expresan en UF.")
    if "IVA" not in texto:
        errores.append("No se menciona el IVA. Los valores siempre se declaran netos, más IVA.")
    if re.search(r"\$\s?\d", texto):
        avisos.append("Hay montos en pesos. La convención de la firma es UF.")

    # Consistencia del total: el total del calendario de pagos debería coincidir
    # con el total de la tabla de inversión.
    totales = re.findall(r"Inversión total[^<]*</strong></td>\s*<td[^>]*><strong>UF\s*([\d.,]+)", html)
    totales_pago = re.findall(r"Total proyecto</strong></td>.*?<strong>UF\s*([\d.,]+)</strong>", html, re.S)
    if totales and totales_pago:
        a, b = totales[0], totales_pago[0]
        if a_numero(a) != a_numero(b):
            errores.append(
                f"El total de la tabla de inversión (UF {a}) no coincide con el "
                f"total del calendario de pagos (UF {b})."
            )
        elif a != b:
            avisos.append(
                f"El total se escribe de dos formas distintas: 'UF {a}' y 'UF {b}'. "
                "Usa siempre dos decimales con coma (UF 120,00)."
            )

    # Porcentajes del calendario de pagos
    pcts = [int(p) for p in re.findall(r">\s*(\d{1,3})%\s*<", html)]
    pcts_parciales = [p for p in pcts if p != 100]
    if pcts_parciales and sum(pcts_parciales) != 100:
        avisos.append(
            f"Los porcentajes del calendario de pagos suman {sum(pcts_parciales)}%, no 100%. Verifica."
        )

    # --- Marca e identidad ------------------------------------------------
    if "Addval Connect" not in html:
        errores.append("No aparece el nombre Addval Connect en el documento.")
    if "tecnologia@addval.cl" not in html:
        avisos.append("Falta el correo de contacto tecnologia@addval.cl.")
    if "addval-logo" not in html:
        avisos.append("Falta el logo de portada.")
    if not re.search(r"Propuesta N°\s*[A-Z]{2,5}-[A-Z0-9]+-\d{3}", html):
        avisos.append(
            "El número de propuesta no sigue el formato {LÍNEA}-{CLIENTE}-{NNN} (ej. ODOO-ACME-001)."
        )

    # --- Garantía y vigencia ---------------------------------------------
    if "garant" not in plano:
        avisos.append("No se menciona la garantía. El estándar son 30 días corridos desde la aceptación.")
    if "vigencia" not in plano:
        avisos.append("No se declara la vigencia de la propuesta (estándar: 30 días corridos).")
    if "control de cambios" not in plano:
        avisos.append("No hay cláusula de control de cambios. Es la protección principal del alcance.")

    # --- Requerimientos en viñetas ---------------------------------------
    crono = extraer_seccion(html, "C. Equipo y Cronograma")
    if crono and 'class="req-list"' not in crono:
        avisos.append(
            "El cronograma no usa <ul class=\"req-list\"> en la celda de requerimientos. "
            "Los requerimientos de hito van en viñetas, no en prosa."
        )

    # --- Supuestos marcados ----------------------------------------------
    n_supuestos = len(re.findall(r'class="placeholder"', html))
    if n_supuestos:
        avisos.append(
            f"Hay {n_supuestos} supuesto(s) marcado(s) con la clase 'placeholder'. "
            "Confírmalos con el usuario y quítales la marca antes de enviar."
        )

    return errores, avisos


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2

    salida = 0
    for ruta in sys.argv[1:]:
        p = Path(ruta)
        if not p.exists():
            print(f"✗ No existe: {ruta}")
            salida = 1
            continue

        errores, avisos = revisar(p)
        print(f"\n=== {p.name} ===")
        for e in errores:
            print(f"  ✗ ERROR   {e}")
        for a in avisos:
            print(f"  ! AVISO   {a}")
        if not errores and not avisos:
            print("  ✓ Sin observaciones.")
        elif not errores:
            print(f"\n  Sin errores. {len(avisos)} aviso(s) para revisar a criterio.")
        else:
            print(f"\n  {len(errores)} error(es) que corregir antes de enviar.")
            salida = 1

    return salida


if __name__ == "__main__":
    sys.exit(main())
