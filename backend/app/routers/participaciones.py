from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import get_current_user, require_write
from app.models import Empleado, Participacion, Proyecto
from app.schemas import ParticipacionCreate, ParticipacionOut, ParticipacionUpdate

router = APIRouter(prefix="/participaciones", tags=["Participaciones"])

TOLERANCIA = 0.01


def _validar_suma_porcentaje(db: Session, empleado_id: int, nuevo_porcentaje: float, excluir_id: int | None = None):
    query = db.query(Participacion).filter(Participacion.empleado_id == empleado_id)
    if excluir_id:
        query = query.filter(Participacion.id != excluir_id)
    suma_actual = sum(float(p.porcentaje) for p in query.all())
    if suma_actual + nuevo_porcentaje > 100 + TOLERANCIA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"La suma de participación del empleado superaría el 100% "
                f"(actual: {suma_actual:.2f}%, intentado: {nuevo_porcentaje:.2f}%)"
            ),
        )


def _to_out(part: Participacion) -> ParticipacionOut:
    data = ParticipacionOut.model_validate(part)
    data.empleado_nombre = part.empleado.nombre_completo
    data.proyecto_nombre = part.proyecto.nombre
    return data


@router.get("", response_model=list[ParticipacionOut])
def listar_participaciones(
    empleado_id: int | None = None,
    proyecto_id: int | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = db.query(Participacion).options(
        joinedload(Participacion.empleado), joinedload(Participacion.proyecto)
    )
    if empleado_id:
        query = query.filter(Participacion.empleado_id == empleado_id)
    if proyecto_id:
        query = query.filter(Participacion.proyecto_id == proyecto_id)
    return [_to_out(p) for p in query.all()]


@router.post("", response_model=ParticipacionOut, status_code=status.HTTP_201_CREATED)
def crear_participacion(
    payload: ParticipacionCreate, db: Session = Depends(get_db), current_user=Depends(require_write)
):
    empleado = db.query(Empleado).filter(Empleado.id == payload.empleado_id).first()
    if empleado is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empleado no encontrado")
    proyecto = db.query(Proyecto).filter(Proyecto.id == payload.proyecto_id).first()
    if proyecto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proyecto no encontrado")

    existente = (
        db.query(Participacion)
        .filter(
            Participacion.empleado_id == payload.empleado_id,
            Participacion.proyecto_id == payload.proyecto_id,
        )
        .first()
    )
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El empleado ya está asignado a este proyecto",
        )

    _validar_suma_porcentaje(db, payload.empleado_id, payload.porcentaje)

    participacion = Participacion(**payload.model_dump())
    db.add(participacion)
    db.commit()
    db.refresh(participacion)
    return _to_out(participacion)


@router.put("/{participacion_id}", response_model=ParticipacionOut)
def actualizar_participacion(
    participacion_id: int,
    payload: ParticipacionUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_write),
):
    participacion = db.query(Participacion).filter(Participacion.id == participacion_id).first()
    if participacion is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participación no encontrada")

    _validar_suma_porcentaje(
        db, participacion.empleado_id, payload.porcentaje, excluir_id=participacion.id
    )
    participacion.porcentaje = payload.porcentaje
    db.commit()
    db.refresh(participacion)
    return _to_out(participacion)


@router.delete("/{participacion_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_participacion(
    participacion_id: int, db: Session = Depends(get_db), current_user=Depends(require_write)
):
    participacion = db.query(Participacion).filter(Participacion.id == participacion_id).first()
    if participacion is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participación no encontrada")
    db.delete(participacion)
    db.commit()
