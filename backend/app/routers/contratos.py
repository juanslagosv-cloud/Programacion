from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import get_current_user, require_write
from app.models import Contrato, Empleado, ModificacionContrato, TipoModificacionContrato
from app.schemas import (
    ContratoCreate,
    ContratoOut,
    ContratoUpdate,
    ModificacionContratoCreate,
    ModificacionContratoOut,
)
from app.utils import contrato_vencido, duracion_contrato

router = APIRouter(tags=["Contratos"])


def _contrato_con_relaciones(db: Session, contrato_id: int) -> Contrato:
    contrato = (
        db.query(Contrato)
        .options(joinedload(Contrato.modificaciones), joinedload(Contrato.proyecto))
        .filter(Contrato.id == contrato_id)
        .first()
    )
    if contrato is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contrato no encontrado")
    return contrato


def _to_out(contrato: Contrato) -> ContratoOut:
    data = ContratoOut.model_validate(contrato)
    data.proyecto_nombre = contrato.proyecto.nombre if contrato.proyecto else None
    data.duracion = duracion_contrato(contrato)
    data.vencido = contrato_vencido(contrato)
    return data


@router.get("/contratos", response_model=list[ContratoOut])
def listar_contratos(
    empleado_id: int | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = db.query(Contrato).options(
        joinedload(Contrato.modificaciones), joinedload(Contrato.proyecto)
    )
    if empleado_id:
        query = query.filter(Contrato.empleado_id == empleado_id)
    contratos = query.order_by(Contrato.fecha_inicio.desc()).all()
    return [_to_out(c) for c in contratos]


@router.post("/contratos", response_model=ContratoOut, status_code=status.HTTP_201_CREATED)
def crear_contrato(
    payload: ContratoCreate, db: Session = Depends(get_db), current_user=Depends(require_write)
):
    empleado = db.query(Empleado).filter(Empleado.id == payload.empleado_id).first()
    if empleado is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empleado no encontrado")

    contrato = Contrato(**payload.model_dump())
    db.add(contrato)
    db.commit()
    db.refresh(contrato)
    return _to_out(contrato)


@router.put("/contratos/{contrato_id}", response_model=ContratoOut)
def actualizar_contrato(
    contrato_id: int,
    payload: ContratoUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_write),
):
    contrato = _contrato_con_relaciones(db, contrato_id)
    for key, value in payload.model_dump().items():
        setattr(contrato, key, value)
    db.commit()
    db.refresh(contrato)
    return _to_out(contrato)


@router.delete("/contratos/{contrato_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_contrato(
    contrato_id: int, db: Session = Depends(get_db), current_user=Depends(require_write)
):
    contrato = _contrato_con_relaciones(db, contrato_id)
    db.delete(contrato)
    db.commit()


# ---------------------------------------------------------------------------
# Prórrogas y otrosí
# ---------------------------------------------------------------------------

@router.post(
    "/contratos/{contrato_id}/modificaciones",
    response_model=ModificacionContratoOut,
    status_code=status.HTTP_201_CREATED,
)
def agregar_modificacion(
    contrato_id: int,
    payload: ModificacionContratoCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_write),
):
    """Registra una prórroga o un otrosí. Una prórroga trae su propia nueva
    fecha de finalización, que se aplica de una vez al contrato: así el
    historial contractual explica por qué cambió la fecha_fin en vez de que
    quede como un cambio silencioso."""
    contrato = _contrato_con_relaciones(db, contrato_id)
    modificacion = ModificacionContrato(contrato_id=contrato_id, **payload.model_dump())
    db.add(modificacion)
    if modificacion.tipo == TipoModificacionContrato.prorroga and modificacion.nueva_fecha_fin:
        contrato.fecha_fin = modificacion.nueva_fecha_fin
    db.commit()
    db.refresh(modificacion)
    return modificacion


@router.delete("/modificaciones/{modificacion_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_modificacion(
    modificacion_id: int, db: Session = Depends(get_db), current_user=Depends(require_write)
):
    modificacion = (
        db.query(ModificacionContrato).filter(ModificacionContrato.id == modificacion_id).first()
    )
    if modificacion is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Modificación no encontrada")
    db.delete(modificacion)
    db.commit()
