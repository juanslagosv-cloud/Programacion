from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import get_current_user, require_write
from app.models import Area, Cargo, Empleado, Empresa, Vacante
from app.schemas import (
    AreaCreate,
    AreaOut,
    AreaUpdate,
    CargoCreate,
    CargoOut,
    CargoUpdate,
    NodoArea,
    NodoJefatura,
    VacanteCreate,
    VacanteOut,
    VacanteUpdate,
)
from app.utils import construir_arbol_areas, construir_arbol_jefaturas, contar_empleados_area

router = APIRouter(tags=["Organigrama"])


# ---------------------------------------------------------------------------
# Áreas
# ---------------------------------------------------------------------------

def _area_a_salida(area: Area) -> AreaOut:
    data = AreaOut.model_validate(area)
    data.area_padre_nombre = area.area_padre.nombre if area.area_padre else None
    data.responsable_nombre = area.responsable.nombre_completo if area.responsable else None
    data.total_empleados = contar_empleados_area(area)
    return data


def _area_con_relaciones(db: Session, area_id: int) -> Area:
    area = (
        db.query(Area)
        .options(joinedload(Area.area_padre), joinedload(Area.responsable), joinedload(Area.empresa))
        .filter(Area.id == area_id)
        .first()
    )
    if area is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Área no encontrada")
    return area


@router.get("/areas", response_model=list[AreaOut])
def listar_areas(
    empresa_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = db.query(Area).options(
        joinedload(Area.area_padre), joinedload(Area.responsable), joinedload(Area.empresa)
    )
    if empresa_id is not None:
        query = query.filter(Area.empresa_id == empresa_id)
    areas = query.order_by(Area.nombre).all()
    return [_area_a_salida(a) for a in areas]


@router.post("/areas", response_model=AreaOut, status_code=status.HTTP_201_CREATED)
def crear_area(payload: AreaCreate, db: Session = Depends(get_db), current_user=Depends(require_write)):
    area = Area(**payload.model_dump())
    db.add(area)
    db.commit()
    db.refresh(area)
    return _area_a_salida(_area_con_relaciones(db, area.id))


@router.put("/areas/{area_id}", response_model=AreaOut)
def actualizar_area(
    area_id: int, payload: AreaUpdate, db: Session = Depends(get_db), current_user=Depends(require_write)
):
    area = _area_con_relaciones(db, area_id)
    if payload.area_padre_id == area_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Un área no puede depender de sí misma")
    for campo, valor in payload.model_dump().items():
        setattr(area, campo, valor)
    db.commit()
    db.refresh(area)
    return _area_a_salida(_area_con_relaciones(db, area.id))


@router.delete("/areas/{area_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_area(area_id: int, db: Session = Depends(get_db), current_user=Depends(require_write)):
    area = _area_con_relaciones(db, area_id)
    db.delete(area)
    db.commit()


# ---------------------------------------------------------------------------
# Cargos
# ---------------------------------------------------------------------------

def _cargo_a_salida(cargo: Cargo) -> CargoOut:
    data = CargoOut.model_validate(cargo)
    data.area_nombre = cargo.area.nombre if cargo.area else None
    data.cargo_superior_nombre = cargo.cargo_superior.nombre if cargo.cargo_superior else None
    return data


def _cargo_con_relaciones(db: Session, cargo_id: int) -> Cargo:
    cargo = (
        db.query(Cargo)
        .options(joinedload(Cargo.area), joinedload(Cargo.cargo_superior))
        .filter(Cargo.id == cargo_id)
        .first()
    )
    if cargo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cargo no encontrado")
    return cargo


@router.get("/cargos", response_model=list[CargoOut])
def listar_cargos(
    empresa_id: int | None = Query(default=None),
    area_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = db.query(Cargo).options(joinedload(Cargo.area), joinedload(Cargo.cargo_superior))
    if empresa_id is not None:
        query = query.filter(Cargo.empresa_id == empresa_id)
    if area_id is not None:
        query = query.filter(Cargo.area_id == area_id)
    cargos = query.order_by(Cargo.nombre).all()
    return [_cargo_a_salida(c) for c in cargos]


@router.post("/cargos", response_model=CargoOut, status_code=status.HTTP_201_CREATED)
def crear_cargo(payload: CargoCreate, db: Session = Depends(get_db), current_user=Depends(require_write)):
    cargo = Cargo(**payload.model_dump())
    db.add(cargo)
    db.commit()
    db.refresh(cargo)
    return _cargo_a_salida(_cargo_con_relaciones(db, cargo.id))


@router.put("/cargos/{cargo_id}", response_model=CargoOut)
def actualizar_cargo(
    cargo_id: int, payload: CargoUpdate, db: Session = Depends(get_db), current_user=Depends(require_write)
):
    cargo = _cargo_con_relaciones(db, cargo_id)
    if payload.cargo_superior_id == cargo_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Un cargo no puede depender de sí mismo")
    for campo, valor in payload.model_dump().items():
        setattr(cargo, campo, valor)
    db.commit()
    db.refresh(cargo)
    return _cargo_a_salida(_cargo_con_relaciones(db, cargo.id))


@router.delete("/cargos/{cargo_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_cargo(cargo_id: int, db: Session = Depends(get_db), current_user=Depends(require_write)):
    cargo = _cargo_con_relaciones(db, cargo_id)
    db.delete(cargo)
    db.commit()


# ---------------------------------------------------------------------------
# Vacantes
# ---------------------------------------------------------------------------

def _vacante_a_salida(vacante: Vacante) -> VacanteOut:
    data = VacanteOut.model_validate(vacante)
    data.area_nombre = vacante.area.nombre if vacante.area else None
    data.cargo_nombre = vacante.cargo.nombre if vacante.cargo else None
    fin = vacante.fecha_cierre_real or date.today()
    data.dias_abierta = (fin - vacante.fecha_apertura).days
    return data


def _vacante_con_relaciones(db: Session, vacante_id: int) -> Vacante:
    vacante = (
        db.query(Vacante)
        .options(joinedload(Vacante.area), joinedload(Vacante.cargo))
        .filter(Vacante.id == vacante_id)
        .first()
    )
    if vacante is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vacante no encontrada")
    return vacante


@router.get("/vacantes", response_model=list[VacanteOut])
def listar_vacantes(
    empresa_id: int | None = Query(default=None),
    estado: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = db.query(Vacante).options(joinedload(Vacante.area), joinedload(Vacante.cargo))
    if empresa_id is not None:
        query = query.filter(Vacante.empresa_id == empresa_id)
    if estado is not None:
        query = query.filter(Vacante.estado == estado)
    vacantes = query.order_by(Vacante.fecha_apertura.desc()).all()
    return [_vacante_a_salida(v) for v in vacantes]


@router.post("/vacantes", response_model=VacanteOut, status_code=status.HTTP_201_CREATED)
def crear_vacante(payload: VacanteCreate, db: Session = Depends(get_db), current_user=Depends(require_write)):
    datos = payload.model_dump()
    if datos.get("fecha_apertura") is None:
        datos["fecha_apertura"] = date.today()
    vacante = Vacante(**datos)
    db.add(vacante)
    db.commit()
    db.refresh(vacante)
    return _vacante_a_salida(_vacante_con_relaciones(db, vacante.id))


@router.put("/vacantes/{vacante_id}", response_model=VacanteOut)
def actualizar_vacante(
    vacante_id: int,
    payload: VacanteUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_write),
):
    vacante = _vacante_con_relaciones(db, vacante_id)
    datos = payload.model_dump()
    if datos.get("fecha_apertura") is None:
        datos["fecha_apertura"] = vacante.fecha_apertura
    for campo, valor in datos.items():
        setattr(vacante, campo, valor)
    db.commit()
    db.refresh(vacante)
    return _vacante_a_salida(_vacante_con_relaciones(db, vacante.id))


@router.delete("/vacantes/{vacante_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_vacante(vacante_id: int, db: Session = Depends(get_db), current_user=Depends(require_write)):
    vacante = _vacante_con_relaciones(db, vacante_id)
    db.delete(vacante)
    db.commit()


# ---------------------------------------------------------------------------
# Organigrama: jefaturas/equipos (árbol derivado de jefe_inmediato) y
# dependencias entre áreas (árbol derivado de area_padre)
# ---------------------------------------------------------------------------

@router.get("/organigrama/jefaturas", response_model=list[NodoJefatura])
def organigrama_jefaturas(
    empresa_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Árbol de jefaturas: cada empleado con quienes le reportan directamente
    (su "equipo"), recursivamente. No se filtran los empleados inactivos para
    no romper el árbol si uno de ellos sigue siendo jefe de alguien activo."""
    query = db.query(Empleado)
    if empresa_id is not None:
        query = query.filter(Empleado.empresa_id == empresa_id)
    empleados = query.all()
    return construir_arbol_jefaturas(empleados)


@router.get("/organigrama/dependencias", response_model=list[NodoArea])
def organigrama_dependencias(
    empresa_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Árbol de dependencias entre áreas, de la(s) raíz(ces) hacia las
    subáreas."""
    query = db.query(Area).options(
        joinedload(Area.responsable), joinedload(Area.empresa).joinedload(Empresa.empleados)
    )
    if empresa_id is not None:
        query = query.filter(Area.empresa_id == empresa_id)
    areas = query.all()
    return construir_arbol_areas(areas)
