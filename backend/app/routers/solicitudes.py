from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import get_current_user, require_write
from app.models import EstadoAprobacion, Empleado, Proyecto, Solicitud, TipoSolicitud
from app.schemas import SolicitudCreate, SolicitudDecision, SolicitudOut
from app.utils import aplicar_aprobacion_vacaciones, dias_solicitados, estado_general_solicitud

router = APIRouter(prefix="/solicitudes", tags=["Solicitudes"])


def _solicitud_con_relaciones(db: Session, solicitud_id: int) -> Solicitud:
    solicitud = (
        db.query(Solicitud)
        .options(
            joinedload(Solicitud.empleado).joinedload(Empleado.jefe_inmediato),
            joinedload(Solicitud.proyecto_propuesto),
        )
        .filter(Solicitud.id == solicitud_id)
        .first()
    )
    if solicitud is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")
    return solicitud


def _to_out(solicitud: Solicitud) -> SolicitudOut:
    data = SolicitudOut.model_validate(solicitud)
    data.empleado_nombre = solicitud.empleado.nombre_completo
    data.jefe_inmediato_nombre = (
        solicitud.empleado.jefe_inmediato.nombre_completo if solicitud.empleado.jefe_inmediato else None
    )
    data.proyecto_propuesto_nombre = (
        solicitud.proyecto_propuesto.nombre if solicitud.proyecto_propuesto else None
    )
    data.estado_general = estado_general_solicitud(solicitud)
    data.dias_solicitados = dias_solicitados(solicitud)
    return data


@router.get("", response_model=list[SolicitudOut])
def listar_solicitudes(
    empleado_id: int | None = None,
    tipo: TipoSolicitud | None = None,
    estado_jefe: EstadoAprobacion | None = None,
    estado_th: EstadoAprobacion | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = db.query(Solicitud).options(
        joinedload(Solicitud.empleado).joinedload(Empleado.jefe_inmediato),
        joinedload(Solicitud.proyecto_propuesto),
    )
    if empleado_id:
        query = query.filter(Solicitud.empleado_id == empleado_id)
    if tipo:
        query = query.filter(Solicitud.tipo == tipo)
    if estado_jefe:
        query = query.filter(Solicitud.estado_jefe == estado_jefe)
    if estado_th:
        query = query.filter(Solicitud.estado_th == estado_th)
    solicitudes = query.order_by(Solicitud.fecha_solicitud.desc(), Solicitud.id.desc()).all()
    return [_to_out(s) for s in solicitudes]


@router.post("", response_model=SolicitudOut, status_code=status.HTTP_201_CREATED)
def crear_solicitud(
    payload: SolicitudCreate, db: Session = Depends(get_db), current_user=Depends(require_write)
):
    empleado = db.query(Empleado).filter(Empleado.id == payload.empleado_id).first()
    if empleado is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empleado no encontrado")

    if payload.proyecto_propuesto_id:
        proyecto = db.query(Proyecto).filter(Proyecto.id == payload.proyecto_propuesto_id).first()
        if proyecto is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proyecto propuesto no encontrado")

    solicitud = Solicitud(**payload.model_dump(), fecha_solicitud=date.today())
    db.add(solicitud)
    db.commit()
    db.refresh(solicitud)
    return _to_out(_solicitud_con_relaciones(db, solicitud.id))


@router.post("/{solicitud_id}/decision-jefe", response_model=SolicitudOut)
def decision_jefe(
    solicitud_id: int,
    payload: SolicitudDecision,
    db: Session = Depends(get_db),
    current_user=Depends(require_write),
):
    solicitud = _solicitud_con_relaciones(db, solicitud_id)
    if solicitud.estado_jefe != EstadoAprobacion.pendiente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El jefe inmediato ya decidió sobre esta solicitud.",
        )
    solicitud.estado_jefe = EstadoAprobacion.aprobado if payload.aprobar else EstadoAprobacion.rechazado
    solicitud.jefe_comentario = payload.comentario
    solicitud.jefe_fecha_respuesta = date.today()
    db.commit()
    db.refresh(solicitud)
    return _to_out(solicitud)


@router.post("/{solicitud_id}/decision-th", response_model=SolicitudOut)
def decision_talento_humano(
    solicitud_id: int,
    payload: SolicitudDecision,
    db: Session = Depends(get_db),
    current_user=Depends(require_write),
):
    solicitud = _solicitud_con_relaciones(db, solicitud_id)
    if solicitud.estado_jefe != EstadoAprobacion.aprobado:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Todavía no la aprueba el jefe inmediato; Talento Humano no puede decidir aún.",
        )
    if solicitud.estado_th != EstadoAprobacion.pendiente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Talento Humano ya decidió sobre esta solicitud.",
        )
    solicitud.estado_th = EstadoAprobacion.aprobado if payload.aprobar else EstadoAprobacion.rechazado
    solicitud.th_comentario = payload.comentario
    solicitud.th_fecha_respuesta = date.today()

    if payload.aprobar and solicitud.tipo == TipoSolicitud.vacaciones:
        aplicar_aprobacion_vacaciones(solicitud)

    db.commit()
    db.refresh(solicitud)
    return _to_out(solicitud)


@router.delete("/{solicitud_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_solicitud(
    solicitud_id: int, db: Session = Depends(get_db), current_user=Depends(require_write)
):
    solicitud = db.query(Solicitud).filter(Solicitud.id == solicitud_id).first()
    if solicitud is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")
    db.delete(solicitud)
    db.commit()
