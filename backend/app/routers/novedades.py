from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import get_current_user, require_write
from app.models import Empleado, EstadoEmpleado, Novedad, Proyecto, TipoNovedad
from app.schemas import NovedadCreate, NovedadOut

router = APIRouter(prefix="/novedades", tags=["Novedades"])


def _to_out(novedad: Novedad) -> NovedadOut:
    data = NovedadOut.model_validate(novedad)
    data.empleado_nombre = novedad.empleado.nombre_completo
    data.proyecto_nombre = novedad.proyecto.nombre if novedad.proyecto else None
    return data


@router.get("", response_model=list[NovedadOut])
def listar_novedades(
    empleado_id: int | None = None,
    tipo: TipoNovedad | None = None,
    procesada: bool | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = db.query(Novedad).options(joinedload(Novedad.empleado), joinedload(Novedad.proyecto))
    if empleado_id:
        query = query.filter(Novedad.empleado_id == empleado_id)
    if tipo:
        query = query.filter(Novedad.tipo == tipo)
    if procesada is not None:
        query = query.filter(Novedad.procesada == procesada)
    novedades = query.order_by(Novedad.fecha.desc()).all()
    return [_to_out(n) for n in novedades]


@router.post("", response_model=NovedadOut, status_code=status.HTTP_201_CREATED)
def crear_novedad(
    payload: NovedadCreate, db: Session = Depends(get_db), current_user=Depends(require_write)
):
    empleado = db.query(Empleado).filter(Empleado.id == payload.empleado_id).first()
    if empleado is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empleado no encontrado")
    if payload.proyecto_id:
        proyecto = db.query(Proyecto).filter(Proyecto.id == payload.proyecto_id).first()
        if proyecto is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proyecto no encontrado")

    novedad = Novedad(**payload.model_dump())
    db.add(novedad)

    if payload.tipo == TipoNovedad.salida:
        empleado.estado = EstadoEmpleado.inactivo

    db.commit()
    db.refresh(novedad)
    return _to_out(novedad)


@router.put("/{novedad_id}/procesar", response_model=NovedadOut)
def marcar_procesada(
    novedad_id: int, db: Session = Depends(get_db), current_user=Depends(require_write)
):
    novedad = db.query(Novedad).filter(Novedad.id == novedad_id).first()
    if novedad is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novedad no encontrada")
    novedad.procesada = True
    db.commit()
    db.refresh(novedad)
    return _to_out(novedad)


@router.delete("/{novedad_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_novedad(
    novedad_id: int, db: Session = Depends(get_db), current_user=Depends(require_write)
):
    novedad = db.query(Novedad).filter(Novedad.id == novedad_id).first()
    if novedad is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novedad no encontrada")
    db.delete(novedad)
    db.commit()
