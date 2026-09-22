"""Generación del certificado laboral en PDF.

El certificado se arma con los datos que ya están en el sistema (nombre,
documento, cargo, fecha de ingreso y, si se pide, el salario de la última
nómina registrada). Los datos de la empresa y de quien firma vienen de la
configuración, porque el sistema no puede inventárselos.
"""

from datetime import date
from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.config import settings
from app.models import Empleado, EstadoEmpleado, Genero, Nomina, TipoNovedad

LOGO = Path(__file__).parent / "assets" / "logo.jpg"

MESES = (
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
)

VERDE = colors.HexColor("#1c4a1c")
GRIS = colors.HexColor("#4c5b50")

UNIDADES = ("", "un", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve",
            "diez", "once", "doce", "trece", "catorce", "quince", "dieciséis", "diecisiete",
            "dieciocho", "diecinueve", "veinte")
DECENAS = ("", "", "veinti", "treinta", "cuarenta", "cincuenta", "sesenta", "setenta",
           "ochenta", "noventa")
CENTENAS = ("", "ciento", "doscientos", "trescientos", "cuatrocientos", "quinientos",
            "seiscientos", "setecientos", "ochocientos", "novecientos")


def _hasta_999(n: int) -> str:
    if n == 0:
        return ""
    if n == 100:
        return "cien"
    centena, resto = divmod(n, 100)
    partes = []
    if centena:
        partes.append(CENTENAS[centena])
    if resto:
        if resto <= 20:
            partes.append(UNIDADES[resto])
        else:
            decena, unidad = divmod(resto, 10)
            if decena == 2:
                partes.append("veinti" + UNIDADES[unidad] if unidad else "veinte")
            elif unidad:
                partes.append(f"{DECENAS[decena]} y {UNIDADES[unidad]}")
            else:
                partes.append(DECENAS[decena])
    return " ".join(partes)


def numero_a_letras(valor: float) -> str:
    """Convierte un valor en pesos a letras, como se acostumbra en los certificados."""
    n = int(round(valor))
    if n == 0:
        return "cero pesos"

    millones, resto = divmod(n, 1_000_000)
    miles, unidades = divmod(resto, 1_000)

    partes = []
    if millones:
        partes.append("un millón" if millones == 1 else f"{_hasta_999(millones)} millones")
    if miles:
        partes.append("mil" if miles == 1 else f"{_hasta_999(miles)} mil")
    if unidades:
        partes.append(_hasta_999(unidades))

    texto = " ".join(partes).replace("veintiun", "veintiún")
    # "quince millones DE pesos", pero "quince millones quinientos mil pesos":
    # el "de" solo va cuando la cifra termina exacta en millones.
    if millones and not miles and not unidades:
        return f"{texto} de pesos"
    if n == 1:
        return "un peso"
    return f"{texto} pesos"


def _fecha_en_letras(f: date) -> str:
    return f"{f.day} de {MESES[f.month - 1]} de {f.year}"


def _tratamiento(empleado: Empleado) -> tuple[str, str]:
    """Devuelve (señor/señora, identificado/identificada) según el género."""
    if empleado.genero == Genero.femenino:
        return "la señora", "identificada"
    if empleado.genero == Genero.masculino:
        return "el señor", "identificado"
    return "la persona", "identificada"


def _fecha_retiro(empleado: Empleado) -> date | None:
    """Fecha de la novedad de salida, si el empleado ya no está activo."""
    if empleado.estado == EstadoEmpleado.activo:
        return None
    salidas = [n.fecha for n in empleado.novedades if n.tipo == TipoNovedad.salida]
    return max(salidas) if salidas else None


def _salario_vigente(empleado: Empleado) -> float | None:
    """Salario base del contrato según el último período de nómina registrado."""
    if not empleado.nominas:
        return None
    ultimo = max(n.periodo for n in empleado.nominas)
    registros: list[Nomina] = [n for n in empleado.nominas if n.periodo == ultimo]
    return float(registros[0].salario_base) if registros else None


def _encabezado(estilos) -> list:
    """Membrete: logo a la izquierda y datos de la empresa a la derecha."""
    datos = [f"<b>{settings.empresa_nombre}</b>", f"NIT {settings.empresa_nit}"]
    for extra in (settings.empresa_direccion, settings.empresa_telefono, settings.empresa_correo):
        if extra:
            datos.append(extra)
    bloque = Paragraph("<br/>".join(datos), estilos["membrete"])

    if LOGO.exists():
        fila = [[Image(str(LOGO), width=2.6 * cm, height=2.6 * cm, kind="proportional"), bloque]]
        tabla = Table(fila, colWidths=[3.2 * cm, 12.3 * cm])
    else:
        tabla = Table([[bloque]], colWidths=[15.5 * cm])

    tabla.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("LINEBELOW", (0, 0), (-1, -1), 1.2, VERDE),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    return [tabla, Spacer(1, 0.9 * cm)]


def generar_certificado_laboral(empleado: Empleado, incluir_salario: bool = False) -> BytesIO:
    """Arma el PDF del certificado y lo devuelve en memoria."""
    hoy = date.today()
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        leftMargin=3 * cm, rightMargin=3 * cm, topMargin=2.2 * cm, bottomMargin=2.2 * cm,
        title=f"Certificado laboral - {empleado.nombre_completo}",
        author=settings.empresa_nombre,
    )

    base = getSampleStyleSheet()
    estilos = {
        "membrete": ParagraphStyle("membrete", parent=base["Normal"], fontSize=9,
                                   leading=12.5, textColor=GRIS),
        "titulo": ParagraphStyle("titulo", parent=base["Normal"], fontSize=14,
                                 leading=18, alignment=TA_CENTER, textColor=VERDE,
                                 fontName="Helvetica-Bold", spaceAfter=2),
        "cuerpo": ParagraphStyle("cuerpo", parent=base["Normal"], fontSize=11,
                                 leading=18, alignment=TA_JUSTIFY),
        "centrado": ParagraphStyle("centrado", parent=base["Normal"], fontSize=11,
                                   leading=16, alignment=TA_CENTER),
        "pie": ParagraphStyle("pie", parent=base["Normal"], fontSize=8.5,
                              leading=11, alignment=TA_CENTER, textColor=GRIS),
    }

    tratamiento, identificado = _tratamiento(empleado)
    documento = empleado.numero_documento or "[DOCUMENTO NO REGISTRADO]"
    retiro = _fecha_retiro(empleado)

    elementos = _encabezado(estilos)
    elementos += [
        Paragraph("CERTIFICADO LABORAL", estilos["titulo"]),
        Spacer(1, 0.8 * cm),
        Paragraph(f"{settings.empresa_nombre} <b>CERTIFICA QUE:</b>", estilos["cuerpo"]),
        Spacer(1, 0.5 * cm),
    ]

    if retiro:
        vinculo = (
            f"laboró en esta empresa desde el <b>{_fecha_en_letras(empleado.fecha_ingreso)}</b> "
            f"hasta el <b>{_fecha_en_letras(retiro)}</b>, desempeñando el cargo de "
            f"<b>{empleado.nombre_cargo}</b>"
        )
    else:
        vinculo = (
            f"labora en esta empresa desde el <b>{_fecha_en_letras(empleado.fecha_ingreso)}</b>, "
            f"desempeñando el cargo de <b>{empleado.nombre_cargo}</b>"
        )

    cuerpo = (
        f"Que {tratamiento} <b>{empleado.nombre_completo.upper()}</b>, {identificado} con "
        f"{empleado.tipo_documento.value} No. <b>{documento}</b>, {vinculo}"
    )

    salario_impreso = False
    if incluir_salario:
        salario = _salario_vigente(empleado)
        if salario is None:
            # No se inventa un valor ni se afirma algo que no consta: se omite.
            # El endpoint avisa antes de llegar aquí, esto es la red de seguridad.
            pass
        else:
            salario_impreso = True
            # El separador de miles se cambia aquí y solo aquí: aplicar el
            # replace sobre la frase completa también convertía la coma que
            # separa la oración.
            monto = f"{salario:,.0f}".replace(",", ".")
            letras = numero_a_letras(salario)
            cuerpo += f", devengando un salario mensual de <b>${monto}</b> ({letras} M/CTE)"
    cuerpo += "."

    elementos += [
        Paragraph(cuerpo, estilos["cuerpo"]),
        Spacer(1, 0.9 * cm),
        Paragraph(
            f"Se expide en {settings.empresa_ciudad}, a los {hoy.day} días del mes de "
            f"{MESES[hoy.month - 1]} de {hoy.year}, a solicitud del interesado.",
            estilos["cuerpo"],
        ),
        Spacer(1, 2.6 * cm),
    ]

    firma = Table(
        [[""], [Paragraph(f"<b>{settings.firmante_nombre}</b>", estilos["centrado"])],
         [Paragraph(settings.firmante_cargo, estilos["centrado"])],
         [Paragraph(settings.empresa_nombre, estilos["centrado"])]],
        colWidths=[8 * cm],
    )
    firma.setStyle(TableStyle([
        ("LINEBELOW", (0, 0), (0, 0), 0.8, colors.black),
        ("TOPPADDING", (0, 1), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    elementos += [firma, Spacer(1, 1.4 * cm)]

    # El pie tiene que decir lo que el documento realmente contiene, no lo
    # que se pidió: si no había salario registrado, el certificado salió sin él.
    if salario_impreso:
        nota = "Este certificado incluye información salarial por solicitud del interesado."
    else:
        nota = ("Este certificado se expide sin información salarial, "
                "por solicitud del interesado.")
    elementos.append(Paragraph(nota, estilos["pie"]))

    doc.build(elementos)
    buffer.seek(0)
    return buffer
