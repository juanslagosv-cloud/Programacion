from datetime import date

from app.models import Empleado, Novedad, Proyecto, TipoNovedad


def meses_entre(inicio: date, fin: date) -> int:
    if fin < inicio:
        return 0
    return (fin.year - inicio.year) * 12 + (fin.month - inicio.month) - (1 if fin.day < inicio.day else 0)


def antiguedad_meses(empleado: Empleado) -> int:
    return meses_entre(empleado.fecha_ingreso, date.today())


def porcentaje_total_empleado(empleado: Empleado) -> float:
    return round(sum(float(p.porcentaje) for p in empleado.participaciones), 2)


def costo_prorrateado_empleado(empleado: Empleado) -> float:
    """Costo mensual aproximado del empleado, tomando su última nómina registrada."""
    if not empleado.nominas:
        return 0.0
    ultima = max(empleado.nominas, key=lambda n: n.periodo)
    return float(ultima.total)


def costo_nomina_mes_proyecto(proyecto: Proyecto) -> float:
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
