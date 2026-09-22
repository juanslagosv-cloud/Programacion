from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, require_write
from app.models import Empleado, Empresa, Proyecto
from app.schemas import EmpresaCreate, EmpresaOut, EmpresaUpdate

router = APIRouter(prefix="/empresas", tags=["Empresas"])


def _to_out(db: Session, empresa: Empresa) -> EmpresaOut:
    data = EmpresaOut.model_validate(empresa)
    data.total_empleados = db.query(Empleado).filter(Empleado.empresa_id == empresa.id).count()
    data.total_proyectos = db.query(Proyecto).filter(Proyecto.empresa_id == empresa.id).count()
    return data


@router.get("", response_model=list[EmpresaOut])
def listar_empresas(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Todas las empresas, activas e inactivas.

    Se necesitan ambos roles para poder llenar el filtro y el selector del
    formulario de empleados/proyectos, que es de solo lectura para el rol
    Administrativo igual que el resto del sistema.
    """
    empresas = db.query(Empresa).order_by(Empresa.nombre).all()
    return [_to_out(db, e) for e in empresas]


@router.post("", response_model=EmpresaOut, status_code=status.HTTP_201_CREATED)
def crear_empresa(
    payload: EmpresaCreate, db: Session = Depends(get_db), current_user=Depends(require_write)
):
    if db.query(Empresa).filter(Empresa.nombre == payload.nombre).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una empresa registrada como «{payload.nombre}»",
        )
    empresa = Empresa(**payload.model_dump())
    db.add(empresa)
    db.commit()
    db.refresh(empresa)
    return _to_out(db, empresa)


@router.put("/{empresa_id}", response_model=EmpresaOut)
def actualizar_empresa(
    empresa_id: int,
    payload: EmpresaUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_write),
):
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if empresa is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa no encontrada")

    duplicada = (
        db.query(Empresa)
        .filter(Empresa.nombre == payload.nombre, Empresa.id != empresa_id)
        .first()
    )
    if duplicada:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una empresa registrada como «{payload.nombre}»",
        )

    for campo, valor in payload.model_dump().items():
        setattr(empresa, campo, valor)
    db.commit()
    db.refresh(empresa)
    return _to_out(db, empresa)


@router.delete("/{empresa_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_empresa(
    empresa_id: int, db: Session = Depends(get_db), current_user=Depends(require_write)
):
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id).first()
    if empresa is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa no encontrada")

    en_uso = db.query(Empleado).filter(Empleado.empresa_id == empresa_id).count()
    en_uso += db.query(Proyecto).filter(Proyecto.empresa_id == empresa_id).count()
    if en_uso:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"No se puede eliminar «{empresa.nombre}»: tiene {en_uso} registro(s) "
                "de empleados o proyectos asociados. Reasígnalos primero, o desactiva "
                "la empresa en vez de eliminarla."
            ),
        )
    db.delete(empresa)
    db.commit()
