from dataclasses import asdict, dataclass
from datetime import date

from app.models import Empleado, Novedad, Proyecto, TipoNovedad

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


@dataclass
class LiquidacionNomina:
    """Liquidación mensual completa: lo que recibe el trabajador y lo que
    realmente le cuesta a la empresa."""

    salario_base: float
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


def liquidar_nomina(
    empleado: Empleado,
    salario_base: float,
    auxilio_transporte: float = 0,
    auxilio_movilidad: float = 0,
    otros_descuentos: float = 0,
) -> LiquidacionNomina:
    """Liquida un mes de nómina siguiendo la normativa laboral colombiana.

    Bases de cálculo:
    - El auxilio de transporte SÍ es base para prima, cesantías e intereses,
      pero NO hace parte del IBC de seguridad social ni de las vacaciones.
    - El auxilio de movilidad no es salarial ni prestacional: no entra en
      ninguna base, solo suma al costo de la empresa. Al ser una decisión de
      la empresa, se toma exactamente el valor que se registre.
    """
    transporte = calcular_auxilio_transporte(salario_base, auxilio_transporte)
    movilidad = auxilio_movilidad

    base_prestacional = salario_base + transporte
    base_seguridad_social = salario_base

    salud_empleado = round(base_seguridad_social * TASA_SALUD_EMPLEADO)
    pension_empleado = round(base_seguridad_social * TASA_PENSION_EMPLEADO)
    total_descuentos = salud_empleado + pension_empleado + otros_descuentos

    prima = round(base_prestacional * TASA_PRIMA)
    cesantias = round(base_prestacional * TASA_CESANTIAS)
    intereses_cesantias = round(base_prestacional * TASA_INTERESES_CESANTIAS)
    provision_vacaciones = round(salario_base * TASA_VACACIONES)

    pension_empleador = round(base_seguridad_social * TASA_PENSION_EMPLEADOR)
    arl = round(base_seguridad_social * tasa_arl(empleado))
    otros_aportes = round(
        base_seguridad_social
        * (TASA_SALUD_EMPLEADOR + TASA_CAJA_COMPENSACION + TASA_SENA + TASA_ICBF)
    )

    total_prestaciones = (
        prima
        + cesantias
        + intereses_cesantias
        + provision_vacaciones
        + pension_empleador
        + arl
        + otros_aportes
    )

    return LiquidacionNomina(
        salario_base=salario_base,
        auxilio_transporte=transporte,
        auxilio_movilidad=movilidad,
        salud_empleado=salud_empleado,
        pension_empleado=pension_empleado,
        otros_descuentos=otros_descuentos,
        total_descuentos=total_descuentos,
        neto_pagado=salario_base + transporte + movilidad - total_descuentos,
        prima=prima,
        cesantias=cesantias,
        intereses_cesantias=intereses_cesantias,
        provision_vacaciones=provision_vacaciones,
        pension_empleador=pension_empleador,
        arl=arl,
        otros_aportes=otros_aportes,
        total_prestaciones=total_prestaciones,
        costo_empleador=salario_base + transporte + movilidad + total_prestaciones,
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
    """Costo mensual real del empleado para la empresa, tomando su última
    nómina registrada. Incluye salario, auxilios, prestaciones sociales y
    aportes del empleador — no solo lo que la persona recibe."""
    if not empleado.nominas:
        return 0.0
    ultima = max(empleado.nominas, key=lambda n: n.periodo)
    return float(ultima.costo_empleador)


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
