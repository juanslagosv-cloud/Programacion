import re
import unicodedata
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.certificados import generar_certificado_laboral
from app.deps import get_current_user, require_write
from app.models import Empleado, EstadoEmpleado, Estudio, Experiencia, TipoCargo
from app.schemas import (
    CumpleañosOut,
    EmpleadoCreate,
    EmpleadoListOut,
    EmpleadoOut,
    EmpleadoUpdate,
    EstudioCreate,
    EstudioOut,
    ExperienciaCreate,
    ExperienciaOut,
)
from app.utils import antiguedad_meses, porcentaje_total_empleado

router = APIRouter(prefix="/empleados", tags=["Empleados"])


def _empleado_con_relaciones(db: Session, empleado_id: int) -> Empleado:
    empleado = (
        db.query(Empleado)
        .options(
            joinedload(Empleado.estudios),
            joinedload(Empleado.experiencias),
            joinedload(Empleado.participaciones),
        )
        .filter(Empleado.id == empleado_id)
        .first()
    )
    if empleado is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empleado no encontrado")
    return empleado


def _to_list_out(empleado: Empleado) -> EmpleadoListOut:
    data = EmpleadoListOut.model_validate(empleado)
    data.antiguedad_meses = antiguedad_meses(empleado)
    data.porcentaje_total = porcentaje_total_empleado(empleado)
    data.proyectos = [p.proyecto.nombre for p in empleado.participaciones]
    return data


def _to_out(empleado: Empleado) -> EmpleadoOut:
    data = EmpleadoOut.model_validate(empleado)
    data.antiguedad_meses = antiguedad_meses(empleado)
    data.porcentaje_total = porcentaje_total_empleado(empleado)
    for part_out, part in zip(data.participaciones, empleado.participaciones):
        part_out.empleado_nombre = empleado.nombre_completo
        part_out.proyecto_nombre = part.proyecto.nombre
    return data


@router.get("", response_model=list[EmpleadoListOut])
def listar_empleados(
    estado: EstadoEmpleado | None = None,
    proyecto_id: int | None = None,
    tipo_cargo: TipoCargo | None = None,
    q: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = db.query(Empleado).options(
        joinedload(Empleado.participaciones), joinedload(Empleado.estudios), joinedload(Empleado.experiencias)
    )
    if estado:
        query = query.filter(Empleado.estado == estado)
    if tipo_cargo:
        query = query.filter(Empleado.tipo_cargo == tipo_cargo)
    if q:
        query = query.filter(Empleado.nombre_completo.ilike(f"%{q}%"))

    empleados = query.order_by(Empleado.nombre_completo).all()

    if proyecto_id:
        empleados = [e for e in empleados if any(p.proyecto_id == proyecto_id for p in e.participaciones)]

    return [_to_list_out(e) for e in empleados]


@router.get("/cumpleanos", response_model=list[CumpleañosOut])
def proximos_cumpleanos(
    dias: int = 45,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    hoy = date.today()
    empleados = db.query(Empleado).filter(Empleado.estado == EstadoEmpleado.activo).all()
    resultado = []
    for e in empleados:
        try:
            proxima = e.fecha_nacimiento.replace(year=hoy.year)
        except ValueError:  # 29 de febrero
            proxima = e.fecha_nacimiento.replace(year=hoy.year, day=28, month=2)
        if proxima < hoy:
            try:
                proxima = proxima.replace(year=hoy.year + 1)
            except ValueError:
                proxima = proxima.replace(year=hoy.year + 1, day=28)

        dias_restantes = (proxima - hoy).days
        if dias_restantes > dias:
            continue

        etiqueta = None
        if dias_restantes == 0:
            etiqueta = "Hoy"
        elif dias_restantes == 1:
            etiqueta = "Mañana"

        resultado.append(
            CumpleañosOut(
                empleado_id=e.id,
                nombre_completo=e.nombre_completo,
                foto_url=e.foto_url,
                nombre_cargo=e.nombre_cargo,
                fecha_nacimiento=e.fecha_nacimiento,
                proxima_fecha=proxima,
                dias_restantes=dias_restantes,
                etiqueta=etiqueta,
            )
        )

    resultado.sort(key=lambda c: c.dias_restantes)
    return resultado


@router.get("/{empleado_id}", response_model=EmpleadoOut)
def obtener_empleado(
    empleado_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    empleado = _empleado_con_relaciones(db, empleado_id)
    return _to_out(empleado)


@router.post("", response_model=EmpleadoOut, status_code=status.HTTP_201_CREATED)
def crear_empleado(
    payload: EmpleadoCreate, db: Session = Depends(get_db), current_user=Depends(require_write)
):
    data = payload.model_dump(exclude={"estudios", "experiencias"})
    empleado = Empleado(**data)
    empleado.estudios = [Estudio(**e.model_dump()) for e in payload.estudios]
    empleado.experiencias = [Experiencia(**e.model_dump()) for e in payload.experiencias]
    db.add(empleado)
    db.commit()
    db.refresh(empleado)
    return _to_out(empleado)


@router.put("/{empleado_id}", response_model=EmpleadoOut)
def actualizar_empleado(
    empleado_id: int,
    payload: EmpleadoUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_write),
):
    empleado = _empleado_con_relaciones(db, empleado_id)
    for key, value in payload.model_dump().items():
        setattr(empleado, key, value)
    db.commit()
    db.refresh(empleado)
    return _to_out(empleado)


@router.delete("/{empleado_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_empleado(
    empleado_id: int, db: Session = Depends(get_db), current_user=Depends(require_write)
):
    empleado = _empleado_con_relaciones(db, empleado_id)
    db.delete(empleado)
    db.commit()


# ---------------------------------------------------------------------------
# Formación académica
# ---------------------------------------------------------------------------

@router.post("/{empleado_id}/estudios", response_model=EstudioOut, status_code=status.HTTP_201_CREATED)
def agregar_estudio(
    empleado_id: int,
    payload: EstudioCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_write),
):
    _empleado_con_relaciones(db, empleado_id)
    estudio = Estudio(empleado_id=empleado_id, **payload.model_dump())
    db.add(estudio)
    db.commit()
    db.refresh(estudio)
    return estudio


@router.delete("/{empleado_id}/estudios/{estudio_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_estudio(
    empleado_id: int,
    estudio_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_write),
):
    estudio = (
        db.query(Estudio).filter(Estudio.id == estudio_id, Estudio.empleado_id == empleado_id).first()
    )
    if estudio is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estudio no encontrado")
    db.delete(estudio)
    db.commit()


# ---------------------------------------------------------------------------
# Experiencia laboral
# ---------------------------------------------------------------------------

@router.post(
    "/{empleado_id}/experiencia", response_model=ExperienciaOut, status_code=status.HTTP_201_CREATED
)
def agregar_experiencia(
    empleado_id: int,
    payload: ExperienciaCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_write),
):
    _empleado_con_relaciones(db, empleado_id)
    experiencia = Experiencia(empleado_id=empleado_id, **payload.model_dump())
    db.add(experiencia)
    db.commit()
    db.refresh(experiencia)
    return experiencia


@router.delete("/{empleado_id}/experiencia/{experiencia_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_experiencia(
    empleado_id: int,
    experiencia_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_write),
):
    experiencia = (
        db.query(Experiencia)
        .filter(Experiencia.id == experiencia_id, Experiencia.empleado_id == empleado_id)
        .first()
    )
    if experiencia is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experiencia no encontrada")
    db.delete(experiencia)
    db.commit()


@router.get("/{empleado_id}/certificado-laboral")
def certificado_laboral(
    empleado_id: int,
    incluir_salario: bool = Query(
        default=False,
        description="Si es verdadero, el certificado indica el salario del último período de nómina registrado.",
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Genera el certificado laboral del empleado en PDF.

    Lo pueden emitir ambos roles: es un documento de consulta, no modifica nada.
    """
    empleado = _empleado_con_relaciones(db, empleado_id)

    if incluir_salario and not empleado.nominas:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"{empleado.nombre_completo} no tiene nómina registrada, así que no se "
                "puede certificar un salario. Registra la nómina del período o genera "
                "el certificado sin salario."
            ),
        )

    pdf = generar_certificado_laboral(empleado, incluir_salario=incluir_salario)

    # Nombre de archivo legible: "certificado_laboral_maria_lopez.pdf"
    base = unicodedata.normalize("NFKD", empleado.nombre_completo)
    base = base.encode("ascii", "ignore").decode("ascii").lower()
    base = re.sub(r"[^a-z0-9]+", "_", base).strip("_") or f"empleado_{empleado_id}"

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="certificado_laboral_{base}.pdf"'},
    )
