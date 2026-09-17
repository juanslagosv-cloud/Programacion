from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import get_current_user
from app.models import Empleado, EstadoEmpleado, Novedad
from app.routers.nomina import resumen_nomina
from app.routers.novedades import _to_out as novedad_to_out
from app.schemas import (
    AlertaNomina,
    AlertaSobreasignacion,
    AlertasResumen,
    AlertaVacaciones,
)
from app.utils import meses_entre, porcentaje_total_empleado

router = APIRouter(prefix="/alertas", tags=["Alertas"])

UMBRAL_DIAS_PENDIENTES = 15
UMBRAL_MESES_SIN_TOMAR = 11
UMBRAL_SOBREASIGNACION_ALERTA = 90
UMBRAL_SOBREASIGNACION_CRITICO = 100


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


@router.get("/vacaciones", response_model=list[AlertaVacaciones])
def alertas_vacaciones(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return _alertas_vacaciones(db)


@router.get("/sobreasignacion", response_model=list[AlertaSobreasignacion])
def alertas_sobreasignacion(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return _alertas_sobreasignacion(db)


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
    )
