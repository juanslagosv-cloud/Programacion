from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import get_current_user, require_write
from app.models import EstadoProyecto, Proyecto
from app.schemas import ProyectoCreate, ProyectoListOut, ProyectoOut, ProyectoUpdate
from app.utils import costo_nomina_mes_proyecto, porcentaje_rotacion_proyecto

router = APIRouter(prefix="/proyectos", tags=["Proyectos"])


def _proyecto_con_relaciones(db: Session, proyecto_id: int) -> Proyecto:
    proyecto = (
        db.query(Proyecto)
        .options(
            joinedload(Proyecto.participaciones),
            joinedload(Proyecto.novedades),
            joinedload(Proyecto.empresa),
        )
        .filter(Proyecto.id == proyecto_id)
        .first()
    )
    if proyecto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proyecto no encontrado")
    return proyecto


def _to_list_out(proyecto: Proyecto) -> ProyectoListOut:
    data = ProyectoListOut.model_validate(proyecto)
    data.tamano_equipo = len(proyecto.participaciones)
    data.costo_nomina_mes = costo_nomina_mes_proyecto(proyecto)
    data.porcentaje_rotacion = porcentaje_rotacion_proyecto(proyecto)
    data.empresa_nombre = proyecto.empresa.nombre if proyecto.empresa else None
    return data


def _to_out(proyecto: Proyecto) -> ProyectoOut:
    data = ProyectoOut.model_validate(proyecto)
    data.tamano_equipo = len(proyecto.participaciones)
    data.costo_nomina_mes = costo_nomina_mes_proyecto(proyecto)
    data.porcentaje_rotacion = porcentaje_rotacion_proyecto(proyecto)
    data.empresa_nombre = proyecto.empresa.nombre if proyecto.empresa else None
    for part_out, part in zip(data.participaciones, proyecto.participaciones):
        part_out.empleado_nombre = part.empleado.nombre_completo
        part_out.proyecto_nombre = proyecto.nombre
    return data


@router.get("", response_model=list[ProyectoListOut])
def listar_proyectos(
    estado: EstadoProyecto | None = None,
    empresa_id: int | None = None,
    q: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = db.query(Proyecto).options(
        joinedload(Proyecto.participaciones), joinedload(Proyecto.novedades), joinedload(Proyecto.empresa)
    )
    if estado:
        query = query.filter(Proyecto.estado == estado)
    if empresa_id:
        query = query.filter(Proyecto.empresa_id == empresa_id)
    if q:
        query = query.filter(Proyecto.nombre.ilike(f"%{q}%"))
    proyectos = query.order_by(Proyecto.nombre).all()
    return [_to_list_out(p) for p in proyectos]


@router.get("/{proyecto_id}", response_model=ProyectoOut)
def obtener_proyecto(
    proyecto_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    proyecto = _proyecto_con_relaciones(db, proyecto_id)
    return _to_out(proyecto)


@router.post("", response_model=ProyectoOut, status_code=status.HTTP_201_CREATED)
def crear_proyecto(
    payload: ProyectoCreate, db: Session = Depends(get_db), current_user=Depends(require_write)
):
    proyecto = Proyecto(**payload.model_dump())
    db.add(proyecto)
    db.commit()
    db.refresh(proyecto)
    return _to_out(proyecto)


@router.put("/{proyecto_id}", response_model=ProyectoOut)
def actualizar_proyecto(
    proyecto_id: int,
    payload: ProyectoUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_write),
):
    proyecto = _proyecto_con_relaciones(db, proyecto_id)
    for key, value in payload.model_dump().items():
        setattr(proyecto, key, value)
    db.commit()
    db.refresh(proyecto)
    return _to_out(proyecto)


@router.delete("/{proyecto_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_proyecto(
    proyecto_id: int, db: Session = Depends(get_db), current_user=Depends(require_write)
):
    proyecto = _proyecto_con_relaciones(db, proyecto_id)
    db.delete(proyecto)
    db.commit()
