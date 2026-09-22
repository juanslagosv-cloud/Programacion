import calendar
from dataclasses import asdict, dataclass
from datetime import date, timedelta

from app.models import Empleado, Novedad, PeriodicidadPago, Proyecto, TipoNovedad

# En nómina el mes siempre se cuenta como 30 días, sin importar los días
# calendario reales: una quincena son 15 días y un mes completo 30.
DIAS_MES = 30
DIAS_QUINCENA = 15

# ---------------------------------------------------------------------------
# Reglas de nómina — valores y tasas legales vigentes en Colombia para 2026.
# Para actualizarlas cada año basta con editar estas constantes.
# ---------------------------------------------------------------------------

SALARIO_MINIMO = 1_750_905
TOPE_AUXILIO_TRANSPORTE = 2 * SALARIO_MINIMO  # $3.501.810
AUXILIO_TRANSPORTE = 249_095
AUXILIO_MOVILIDAD = 100_000

PALABRAS_CLAVE_CAMPO = ("campo", "monitoreo", "restauracion", "restauración", "forestal")

# --- Deducciones al trabajador (se restan de lo que recibe) ---
TASA_SALUD_EMPLEADO = 0.04
TASA_PENSION_EMPLEADO = 0.04

# --- Prestaciones sociales: provisión mensual de lo que se causa al año ---
TASA_PRIMA = 1 / 12  # un salario al año (mitad en junio, mitad en diciembre)
TASA_CESANTIAS = 1 / 12  # un salario al año
TASA_INTERESES_CESANTIAS = 0.12 / 12  # 12% anual sobre las cesantías
TASA_VACACIONES = 15 / 360  # 15 días hábiles de descanso pago al año

# --- Aportes del empleador ---
TASA_PENSION_EMPLEADOR = 0.12

# La ARL la paga 100% el empleador y su tasa depende de la clase de riesgo del
# cargo. Se asume riesgo V para roles de campo y riesgo I para oficina.
TASA_ARL_RIESGO_I = 0.00522
TASA_ARL_RIESGO_V = 0.06960

# Exonerados por la Ley 1607 de 2012 para trabajadores que devengan menos de
# 10 SMLMV. Si Ecodes no aplica la exoneración, basta con poner aquí las tasas
# reales (salud 8.5%, caja 4%, SENA 2%, ICBF 3%) y el cálculo las incluye.
TASA_SALUD_EMPLEADOR = 0.0
TASA_CAJA_COMPENSACION = 0.0
TASA_SENA = 0.0
TASA_ICBF = 0.0


def aplica_auxilio_transporte(salario_base: float) -> bool:
    """El auxilio de transporte es de ley y solo aplica a quienes devengan
    hasta 2 salarios mínimos mensuales legales vigentes."""
    return salario_base <= TOPE_AUXILIO_TRANSPORTE


def es_rol_campo(empleado: Empleado) -> bool:
    """Identifica los cargos de campo, que cotizan una clase de riesgo de ARL
    más alta que los de oficina."""
    return any(p in empleado.nombre_cargo.lower() for p in PALABRAS_CLAVE_CAMPO)


def calcular_auxilio_transporte(salario_base: float, auxilio_transporte: float) -> float:
    """El auxilio de transporte es de ley, así que se completa solo cuando no
    viene definido. El de movilidad no se calcula: lo decide la empresa y se
    registra tal como lo digite Talento Humano."""
    if auxilio_transporte == 0 and aplica_auxilio_transporte(salario_base):
        return AUXILIO_TRANSPORTE
    return auxilio_transporte


def tasa_arl(empleado: Empleado) -> float:
    """Los roles de campo cotizan riesgo V; los de oficina, riesgo I."""
    return TASA_ARL_RIESGO_V if es_rol_campo(empleado) else TASA_ARL_RIESGO_I


def ultimo_dia_del_mes(periodo: str) -> date:
    """`periodo` viene como 'YYYY-MM'."""
    anio, mes = (int(x) for x in periodo.split("-"))
    return date(anio, mes, calendar.monthrange(anio, mes)[1])


def fecha_de_pago(periodo: str, quincena: int | None) -> date:
    """Los pagos mensuales y la segunda quincena caen el último día del mes;
    la primera quincena, el 15."""
    anio, mes = (int(x) for x in periodo.split("-"))
    if quincena == 1:
        return date(anio, mes, 15)
    return ultimo_dia_del_mes(periodo)


def periodos_de_pago(empleado: Empleado) -> list[int | None]:
    """Qué pagos le corresponden a una persona dentro de un mes."""
    if empleado.periodicidad_pago == PeriodicidadPago.quincenal:
        return [1, 2]
    return [None]


def dias_del_periodo(quincena: int | None) -> int:
    return DIAS_QUINCENA if quincena is not None else DIAS_MES


def proximo_pago(n_mensuales: int, n_quincenales: int, hoy: date | None = None) -> tuple[date, str]:
    """Devuelve la próxima fecha de pago y a quiénes cubre. El 15 solo se paga
    a quienes cobran quincenalmente; el último día del mes, a todos."""
    hoy = hoy or date.today()
    periodo_actual = hoy.strftime("%Y-%m")
    quince = date(hoy.year, hoy.month, 15)
    fin_de_mes = ultimo_dia_del_mes(periodo_actual)

    if hoy <= quince and n_quincenales:
        return quince, f"Primera quincena · {n_quincenales} persona(s)"

    if hoy <= fin_de_mes:
        personas = n_mensuales + n_quincenales
        detalle = "mensuales" if not n_quincenales else "mensuales + segunda quincena"
        return fin_de_mes, f"Pago de fin de mes ({detalle}) · {personas} persona(s)"

    # ya pasó el fin de mes: el siguiente pago es del mes entrante
    siguiente_mes = (fin_de_mes.replace(day=1) + timedelta(days=32)).strftime("%Y-%m")
    if n_quincenales:
        anio, mes = (int(x) for x in siguiente_mes.split("-"))
        return date(anio, mes, 15), f"Primera quincena · {n_quincenales} persona(s)"
    return ultimo_dia_del_mes(siguiente_mes), f"Pago de fin de mes · {n_mensuales} persona(s)"


@dataclass
class LiquidacionNomina:
    """Liquidación de un pago: lo que recibe el trabajador y lo que realmente
    le cuesta a la empresa. Todos los valores corresponden al período
    liquidado, así que sumar las quincenas de un mes da el total mensual."""

    salario_base: float  # salario mensual del contrato (referencia, no se suma)
    dias_liquidados: int
    salario_devengado: float  # lo causado en este período
    auxilio_transporte: float
    auxilio_movilidad: float
    # Deducciones al trabajador
    salud_empleado: float
    pension_empleado: float
    otros_descuentos: float
    total_descuentos: float
    neto_pagado: float
    # Prestaciones sociales y aportes que asume el empleador
    prima: float
    cesantias: float
    intereses_cesantias: float
    provision_vacaciones: float
    pension_empleador: float
    arl: float
    otros_aportes: float
    total_prestaciones: float
    costo_empleador: float

    def as_dict(self) -> dict:
        return asdict(self)


def _liquidar_mes(
    empleado: Empleado,
    salario_base: float,
    auxilio_transporte: float,
    auxilio_movilidad: float,
    otros_descuentos: float,
) -> dict:
    """Liquida el mes completo. Todos los conceptos salen de aquí; las
    quincenas se derivan partiendo estos valores."""
    transporte = calcular_auxilio_transporte(salario_base, auxilio_transporte)

    base_prestacional = salario_base + transporte
    base_seguridad_social = salario_base

    prima = round(base_prestacional * TASA_PRIMA)
    cesantias = round(base_prestacional * TASA_CESANTIAS)
    intereses_cesantias = round(base_prestacional * TASA_INTERESES_CESANTIAS)

    return {
        "salario_devengado": round(salario_base),
        "auxilio_transporte": transporte,
        "auxilio_movilidad": auxilio_movilidad,
        "salud_empleado": round(base_seguridad_social * TASA_SALUD_EMPLEADO),
        "pension_empleado": round(base_seguridad_social * TASA_PENSION_EMPLEADO),
        "otros_descuentos": otros_descuentos,
        "prima": prima,
        "cesantias": cesantias,
        "intereses_cesantias": intereses_cesantias,
        "provision_vacaciones": round(salario_base * TASA_VACACIONES),
        "pension_empleador": round(base_seguridad_social * TASA_PENSION_EMPLEADOR),
        "arl": round(base_seguridad_social * tasa_arl(empleado)),
        "otros_aportes": round(
            base_seguridad_social
            * (TASA_SALUD_EMPLEADOR + TASA_CAJA_COMPENSACION + TASA_SENA + TASA_ICBF)
        ),
    }


def liquidar_nomina(
    empleado: Empleado,
    salario_base: float,
    auxilio_transporte: float = 0,
    auxilio_movilidad: float = 0,
    otros_descuentos: float = 0,
    quincena: int | None = None,
) -> LiquidacionNomina:
    """Liquida un pago de nómina siguiendo la normativa laboral colombiana.

    `salario_base` y los auxilios se reciben siempre como valores mensuales.
    Si el pago es quincenal, cada concepto se parte en dos y la diferencia por
    redondeo se ajusta en la segunda quincena, de modo que las dos quincenas
    sumen exactamente el mes.

    Bases de cálculo:
    - El auxilio de transporte SÍ es base para prima, cesantías e intereses,
      pero NO hace parte del IBC de seguridad social ni de las vacaciones.
    - El auxilio de movilidad no es salarial ni prestacional: no entra en
      ninguna base, solo suma al costo de la empresa. Al ser una decisión de
      la empresa, se toma exactamente el valor que se registre.
    - La elegibilidad del auxilio de transporte y la clase de riesgo de la ARL
      se evalúan sobre el salario mensual, no sobre el valor de la quincena.
    """
    mes = _liquidar_mes(
        empleado, salario_base, auxilio_transporte, auxilio_movilidad, otros_descuentos
    )

    if quincena is None:
        c = mes
    elif quincena == 1:
        c = {k: round(v / 2) for k, v in mes.items()}
    else:
        # la segunda quincena absorbe el ajuste al peso
        c = {k: v - round(v / 2) for k, v in mes.items()}

    total_descuentos = c["salud_empleado"] + c["pension_empleado"] + c["otros_descuentos"]
    devengado = c["salario_devengado"] + c["auxilio_transporte"] + c["auxilio_movilidad"]
    total_prestaciones = (
        c["prima"]
        + c["cesantias"]
        + c["intereses_cesantias"]
        + c["provision_vacaciones"]
        + c["pension_empleador"]
        + c["arl"]
        + c["otros_aportes"]
    )

    return LiquidacionNomina(
        salario_base=salario_base,
        dias_liquidados=dias_del_periodo(quincena),
        neto_pagado=devengado - total_descuentos,
        total_descuentos=total_descuentos,
        total_prestaciones=total_prestaciones,
        costo_empleador=devengado + total_prestaciones,
        **c,
    )


def meses_entre(inicio: date, fin: date) -> int:
    if fin < inicio:
        return 0
    return (fin.year - inicio.year) * 12 + (fin.month - inicio.month) - (1 if fin.day < inicio.day else 0)


def antiguedad_meses(empleado: Empleado) -> int:
    return meses_entre(empleado.fecha_ingreso, date.today())


def porcentaje_total_empleado(empleado: Empleado) -> float:
    return round(sum(float(p.porcentaje) for p in empleado.participaciones), 2)


def costo_prorrateado_empleado(empleado: Empleado) -> float:
    """Costo mensual real del empleado para la empresa. Suma todos los pagos
    del último período liquidado, porque a quien se le paga quincenalmente le
    corresponden dos registros por mes. Incluye salario, auxilios, prestaciones
    sociales y aportes del empleador — no solo lo que la persona recibe."""
    if not empleado.nominas:
        return 0.0
    ultimo_periodo = max(n.periodo for n in empleado.nominas)
    return float(
        sum(n.costo_empleador for n in empleado.nominas if n.periodo == ultimo_periodo)
    )


def costo_nomina_mes_proyecto(proyecto: Proyecto) -> float:
    """Costo laboral mensual del proyecto: el costo real de cada persona
    multiplicado por su % de dedicación al proyecto."""
    total = 0.0
    for part in proyecto.participaciones:
        costo_empleado = costo_prorrateado_empleado(part.empleado)
        total += costo_empleado * (float(part.porcentaje) / 100.0)
    return round(total, 2)


def porcentaje_rotacion_proyecto(proyecto: Proyecto) -> float:
    """% de personas que salieron del proyecto (novedades de tipo Salida o
    Cambio de proyecto) sobre el total histórico de personas asignadas."""
    ids_historicos = {p.empleado_id for p in proyecto.participaciones}
    novedades_salida = [
        n
        for n in proyecto.novedades
        if n.tipo in (TipoNovedad.salida, TipoNovedad.cambio_proyecto)
    ]
    ids_historicos |= {n.empleado_id for n in novedades_salida}
    if not ids_historicos:
        return 0.0
    salieron = {n.empleado_id for n in novedades_salida}
    return round(len(salieron) / len(ids_historicos) * 100, 2)


def novedades_del_mes(empleado: Empleado, periodo: str) -> int:
    return len([n for n in empleado.novedades if n.fecha.strftime("%Y-%m") == periodo])
