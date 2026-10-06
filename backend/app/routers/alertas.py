from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import get_current_user
from app.models import Empleado, EstadoAprobacion, EstadoEmpleado, Novedad, TipoSolicitud
from app.routers.nomina import resumen_nomina
from app.routers.novedades import _to_out as novedad_to_out
from app.schemas import (
    AlertaGenerica,
    AlertaNomina,
    AlertaSobreasignacion,
    AlertasResumen,
    AlertaVacaciones,
)
from app.utils import (
    UMBRAL_DIAS_CERTIFICACION_POR_VENCER,
    UMBRAL_DIAS_CONTRATO_POR_VENCER,
    UMBRAL_DIAS_EXAMEN_MEDICO_PROXIMO,
    UMBRAL_DIAS_PERIODO_PRUEBA,
    dias_para_fin_periodo_prueba,
    meses_entre,
    porcentaje_total_empleado,
    proximo_aniversario_laboral,
    tipos_documento_faltantes,
)

router = APIRouter(prefix="/alertas", tags=["Alertas"])

UMBRAL_DIAS_PENDIENTES = 15
UMBRAL_MESES_SIN_TOMAR = 11
UMBRAL_SOBREASIGNACION_ALERTA = 90
UMBRAL_SOBREASIGNACION_CRITICO = 100
UMBRAL_DIAS_ANIVERSARIO = 30


def _alertas_vacaciones(db: Session) -> list[AlertaVacaciones]:
    empleados = db.query(Empleado).filter(Empleado.estado == EstadoEmpleado.activo).all()
    alertas = []
    hoy = date.today()
    for e in empleados:
        meses_sin_tomar = meses_entre(e.vacaciones_ultima_toma, hoy) if e.vacaciones_ultima_toma else None
        dispara_dias = e.vacaciones_dias_pendientes >= UMBRAL_DIAS_PENDIENTES
        dispara_meses = meses_sin_tomar is not None and meses_sin_tomar >= UMBRAL_MESES_SIN_TOMAR
        if not (dispara_dias or dispara_meses):
            continue
        nivel = "critico" if e.vacaciones_dias_pendientes >= 20 or (meses_sin_tomar or 0) >= 12 else "alerta"
        alertas.append(
            AlertaVacaciones(
                empleado_id=e.id,
                empleado_nombre=e.nombre_completo,
                foto_url=e.foto_url,
                dias_pendientes=e.vacaciones_dias_pendientes,
                ultima_toma=e.vacaciones_ultima_toma,
                meses_sin_tomar=meses_sin_tomar,
                nivel=nivel,
            )
        )
    alertas.sort(key=lambda a: a.dias_pendientes, reverse=True)
    return alertas


def _alertas_sobreasignacion(db: Session) -> list[AlertaSobreasignacion]:
    empleados = (
        db.query(Empleado)
        .options(joinedload(Empleado.participaciones))
        .filter(Empleado.estado == EstadoEmpleado.activo)
        .all()
    )
    alertas = []
    for e in empleados:
        total = porcentaje_total_empleado(e)
        if total < UMBRAL_SOBREASIGNACION_ALERTA:
            continue
        nivel = "critico" if total >= UMBRAL_SOBREASIGNACION_CRITICO else "alerta"
        alertas.append(
            AlertaSobreasignacion(
                empleado_id=e.id,
                empleado_nombre=e.nombre_completo,
                foto_url=e.foto_url,
                porcentaje_total=total,
                nivel=nivel,
            )
        )
    alertas.sort(key=lambda a: a.porcentaje_total, reverse=True)
    return alertas


def _alertas_nomina(db: Session) -> list[AlertaNomina]:
    resumen = resumen_nomina(periodo=None, db=db, current_user=None)
    alertas = [
        AlertaNomina(
            tipo="Próximo pago",
            descripcion=f"El próximo pago de nómina es el {resumen.proximo_pago}",
            fecha=date.fromisoformat(resumen.proximo_pago) if resumen.proximo_pago else None,
            nivel="info",
        )
    ]
    if resumen.novedades_sin_procesar > 0:
        alertas.append(
            AlertaNomina(
                tipo="Novedades sin procesar",
                descripcion=(
                    f"Hay {resumen.novedades_sin_procesar} novedad(es) sin procesar que "
                    "pueden afectar la nómina del período"
                ),
                nivel="alerta",
            )
        )
    return alertas


def _alertas_aniversarios(db: Session) -> list[AlertaGenerica]:
    """Aniversario laboral (1 año, 2 años, etc. con la empresa desde
    `fecha_ingreso`), dentro de los próximos UMBRAL_DIAS_ANIVERSARIO días."""
    empleados = db.query(Empleado).filter(Empleado.estado == EstadoEmpleado.activo).all()
    alertas = []
    for e in empleados:
        proxima, anios = proximo_aniversario_laboral(e)
        if anios < 1:
            continue  # todavía no cumple ni el primer año
        dias = (proxima - date.today()).days
        if 0 <= dias <= UMBRAL_DIAS_ANIVERSARIO:
            etiqueta = "año" if anios == 1 else "años"
            alertas.append(
                AlertaGenerica(
                    tipo="Aniversario laboral",
                    empleado_id=e.id,
                    empleado_nombre=e.nombre_completo,
                    foto_url=e.foto_url,
                    descripcion=f"Cumple {anios} {etiqueta} con la empresa el {proxima.isoformat()}",
                    fecha=proxima,
                    nivel="info",
                )
            )
    alertas.sort(key=lambda a: a.fecha)
    return alertas


def _alertas_expediente(db: Session) -> list[AlertaGenerica]:
    """Las alertas del expediente del empleado: contrato por vencer, período
    de prueba por finalizar, certificación por vencer, documento faltante,
    evaluación pendiente, capacitación pendiente, examen médico próximo e
    incapacidad activa. Se agrupan en una sola lista con un campo `tipo`
    porque todas comparten la misma forma (empleado, descripción, fecha,
    nivel) y no justifican un endpoint separado cada una."""
    hoy = date.today()
    empleados = (
        db.query(Empleado)
        .options(
            joinedload(Empleado.contratos),
            joinedload(Empleado.certificaciones),
            joinedload(Empleado.documentos),
            joinedload(Empleado.evaluaciones),
            joinedload(Empleado.capacitaciones),
            joinedload(Empleado.examenes_medicos),
            joinedload(Empleado.solicitudes),
        )
        .filter(Empleado.estado == EstadoEmpleado.activo)
        .all()
    )
    alertas: list[AlertaGenerica] = []

    for e in empleados:
        # Contrato próximo a vencer
        for c in e.contratos:
            if c.fecha_fin is None:
                continue
            dias = (c.fecha_fin - hoy).days
            if 0 <= dias <= UMBRAL_DIAS_CONTRATO_POR_VENCER:
                alertas.append(
                    AlertaGenerica(
                        tipo="Contrato próximo a vencer",
                        empleado_id=e.id,
                        empleado_nombre=e.nombre_completo,
                        foto_url=e.foto_url,
                        descripcion=f"El contrato vence el {c.fecha_fin.isoformat()} ({dias} día(s))",
                        fecha=c.fecha_fin,
                        nivel="critico" if dias <= 7 else "alerta",
                    )
                )

            # Período de prueba próximo a finalizar
            dias_prueba = dias_para_fin_periodo_prueba(c)
            if dias_prueba is not None and 0 <= dias_prueba <= UMBRAL_DIAS_PERIODO_PRUEBA:
                alertas.append(
                    AlertaGenerica(
                        tipo="Período de prueba próximo a finalizar",
                        empleado_id=e.id,
                        empleado_nombre=e.nombre_completo,
                        foto_url=e.foto_url,
                        descripcion=f"El período de prueba termina en {dias_prueba} día(s)",
                        nivel="critico" if dias_prueba <= 3 else "alerta",
                    )
                )

        # Certificación próxima a vencer
        for cert in e.certificaciones:
            if cert.fecha_vencimiento is None:
                continue
            dias = (cert.fecha_vencimiento - hoy).days
            if 0 <= dias <= UMBRAL_DIAS_CERTIFICACION_POR_VENCER:
                alertas.append(
                    AlertaGenerica(
                        tipo="Certificación próxima a vencer",
                        empleado_id=e.id,
                        empleado_nombre=e.nombre_completo,
                        foto_url=e.foto_url,
                        descripcion=f"«{cert.nombre}» vence el {cert.fecha_vencimiento.isoformat()}",
                        fecha=cert.fecha_vencimiento,
                        nivel="critico" if dias <= 7 else "alerta",
                    )
                )

        # Documento faltante
        faltantes = tipos_documento_faltantes(e)
        if faltantes:
            alertas.append(
                AlertaGenerica(
                    tipo="Documento faltante",
                    empleado_id=e.id,
                    empleado_nombre=e.nombre_completo,
                    foto_url=e.foto_url,
                    descripcion="Falta(n): " + ", ".join(t.value for t in faltantes),
                    nivel="alerta",
                )
            )

        # Evaluación pendiente
        for ev in e.evaluaciones:
            if ev.fecha_realizada is None:
                alertas.append(
                    AlertaGenerica(
                        tipo="Evaluación pendiente",
                        empleado_id=e.id,
                        empleado_nombre=e.nombre_completo,
                        foto_url=e.foto_url,
                        descripcion=f"Evaluación de {ev.periodo} programada para el {ev.fecha_programada.isoformat()}",
                        fecha=ev.fecha_programada,
                        nivel="critico" if ev.fecha_programada < hoy else "info",
                    )
                )

        # Capacitación pendiente
        for cap in e.capacitaciones:
            if cap.fecha_realizada is None:
                alertas.append(
                    AlertaGenerica(
                        tipo="Capacitación pendiente",
                        empleado_id=e.id,
                        empleado_nombre=e.nombre_completo,
                        foto_url=e.foto_url,
                        descripcion=f"«{cap.nombre}» programada para el {cap.fecha_programada.isoformat()}",
                        fecha=cap.fecha_programada,
                        nivel="critico" if cap.fecha_programada < hoy else "info",
                    )
                )

        # Examen médico próximo
        for ex in e.examenes_medicos:
            if ex.fecha_proximo is None:
                continue
            dias = (ex.fecha_proximo - hoy).days
            if 0 <= dias <= UMBRAL_DIAS_EXAMEN_MEDICO_PROXIMO:
                alertas.append(
                    AlertaGenerica(
                        tipo="Examen médico próximo",
                        empleado_id=e.id,
                        empleado_nombre=e.nombre_completo,
                        foto_url=e.foto_url,
                        descripcion=f"Examen {ex.tipo.value.lower()} programado para el {ex.fecha_proximo.isoformat()}",
                        fecha=ex.fecha_proximo,
                        nivel="critico" if dias <= 7 else "alerta",
                    )
                )

        # Incapacidad activa (solicitud de tipo incapacidad ya aprobada,
        # vigente hoy)
        for s in e.solicitudes:
            if (
                s.tipo == TipoSolicitud.incapacidad
                and s.estado_th == EstadoAprobacion.aprobado
                and s.fecha_inicio <= hoy
                and (s.fecha_fin is None or s.fecha_fin >= hoy)
            ):
                hasta = f" hasta el {s.fecha_fin.isoformat()}" if s.fecha_fin else ""
                alertas.append(
                    AlertaGenerica(
                        tipo="Incapacidad activa",
                        empleado_id=e.id,
                        empleado_nombre=e.nombre_completo,
                        foto_url=e.foto_url,
                        descripcion=f"Incapacidad activa desde el {s.fecha_inicio.isoformat()}{hasta}",
                        fecha=s.fecha_inicio,
                        nivel="info",
                    )
                )

    alertas.sort(key=lambda a: (a.fecha is None, a.fecha or hoy))
    return alertas


@router.get("/vacaciones", response_model=list[AlertaVacaciones])
def alertas_vacaciones(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return _alertas_vacaciones(db)


@router.get("/sobreasignacion", response_model=list[AlertaSobreasignacion])
def alertas_sobreasignacion(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return _alertas_sobreasignacion(db)


@router.get("/expediente", response_model=list[AlertaGenerica])
def alertas_expediente(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return _alertas_expediente(db)


@router.get("/aniversarios", response_model=list[AlertaGenerica])
def alertas_aniversarios(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return _alertas_aniversarios(db)


@router.get("", response_model=AlertasResumen)
def alertas_resumen(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    novedades_sin_procesar = (
        db.query(Novedad)
        .options(joinedload(Novedad.empleado), joinedload(Novedad.proyecto))
        .filter(Novedad.procesada.is_(False))
        .order_by(Novedad.fecha.desc())
        .all()
    )
    return AlertasResumen(
        vacaciones=_alertas_vacaciones(db),
        sobreasignacion=_alertas_sobreasignacion(db),
        nomina=_alertas_nomina(db),
        novedades_sin_procesar=[novedad_to_out(n) for n in novedades_sin_procesar],
        expediente=_alertas_expediente(db),
        aniversarios=_alertas_aniversarios(db),
    )
