import re
import unicodedata
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.certificados import generar_certificado_laboral
from app.deps import get_current_user, require_write
from app.models import (
    Capacitacion,
    Certificacion,
    Contrato,
    Documento,
    Empleado,
    EstadoEmpleado,
    Estudio,
    Evaluacion,
    ExamenMedico,
    Experiencia,
    TipoCargo,
)
from app.schemas import (
    CapacitacionCreate,
    CapacitacionOut,
    CertificacionCreate,
    CertificacionOut,
    CumpleañosOut,
    DocumentoCreate,
    DocumentoOut,
    EmpleadoCreate,
    EmpleadoListOut,
    EmpleadoOut,
    EmpleadoUpdate,
    EstudioCreate,
    EstudioOut,
    EvaluacionCreate,
    EvaluacionOut,
    ExamenMedicoCreate,
    ExamenMedicoOut,
    ExperienciaCreate,
    ExperienciaOut,
)
from app.utils import antiguedad_meses, contrato_vencido, duracion_contrato, porcentaje_total_empleado

router = APIRouter(prefix="/empleados", tags=["Empleados"])


def _empleado_con_relaciones(db: Session, empleado_id: int) -> Empleado:
    empleado = (
        db.query(Empleado)
        .options(
            joinedload(Empleado.estudios),
            joinedload(Empleado.experiencias),
            joinedload(Empleado.participaciones),
            joinedload(Empleado.empresa),
            joinedload(Empleado.jefe_inmediato),
            joinedload(Empleado.contratos).joinedload(Contrato.modificaciones),
            joinedload(Empleado.contratos).joinedload(Contrato.proyecto),
            joinedload(Empleado.certificaciones),
            joinedload(Empleado.documentos),
            joinedload(Empleado.evaluaciones),
            joinedload(Empleado.capacitaciones),
            joinedload(Empleado.examenes_medicos),
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
    data.empresa_nombre = empleado.empresa.nombre if empleado.empresa else None
    return data


def _to_out(empleado: Empleado) -> EmpleadoOut:
    data = EmpleadoOut.model_validate(empleado)
    data.antiguedad_meses = antiguedad_meses(empleado)
    data.porcentaje_total = porcentaje_total_empleado(empleado)
    data.empresa_nombre = empleado.empresa.nombre if empleado.empresa else None
    data.jefe_inmediato_nombre = empleado.jefe_inmediato.nombre_completo if empleado.jefe_inmediato else None
    for part_out, part in zip(data.participaciones, empleado.participaciones):
        part_out.empleado_nombre = empleado.nombre_completo
        part_out.proyecto_nombre = part.proyecto.nombre
    for contrato_out, contrato in zip(data.contratos, empleado.contratos):
        contrato_out.proyecto_nombre = contrato.proyecto.nombre if contrato.proyecto else None
        contrato_out.duracion = duracion_contrato(contrato)
        contrato_out.vencido = contrato_vencido(contrato)
    return data


@router.get("", response_model=list[EmpleadoListOut])
def listar_empleados(
    estado: EstadoEmpleado | None = None,
    proyecto_id: int | None = None,
    tipo_cargo: TipoCargo | None = None,
    empresa_id: int | None = None,
    q: str | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = db.query(Empleado).options(
        joinedload(Empleado.participaciones),
        joinedload(Empleado.estudios),
        joinedload(Empleado.experiencias),
        joinedload(Empleado.empresa),
    )
    if estado:
        query = query.filter(Empleado.estado == estado)
    if tipo_cargo:
        query = query.filter(Empleado.tipo_cargo == tipo_cargo)
    if empresa_id:
        query = query.filter(Empleado.empresa_id == empresa_id)
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


# ---------------------------------------------------------------------------
# Certificaciones
# ---------------------------------------------------------------------------

@router.post(
    "/{empleado_id}/certificaciones", response_model=CertificacionOut, status_code=status.HTTP_201_CREATED
)
def agregar_certificacion(
    empleado_id: int,
    payload: CertificacionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_write),
):
    _empleado_con_relaciones(db, empleado_id)
    certificacion = Certificacion(empleado_id=empleado_id, **payload.model_dump())
    db.add(certificacion)
    db.commit()
    db.refresh(certificacion)
    return certificacion


@router.delete("/{empleado_id}/certificaciones/{certificacion_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_certificacion(
    empleado_id: int,
    certificacion_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_write),
):
    certificacion = (
        db.query(Certificacion)
        .filter(Certificacion.id == certificacion_id, Certificacion.empleado_id == empleado_id)
        .first()
    )
    if certificacion is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificación no encontrada")
    db.delete(certificacion)
    db.commit()


# ---------------------------------------------------------------------------
# Documentos del expediente
# ---------------------------------------------------------------------------

@router.post("/{empleado_id}/documentos", response_model=DocumentoOut, status_code=status.HTTP_201_CREATED)
def agregar_documento(
    empleado_id: int,
    payload: DocumentoCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_write),
):
    _empleado_con_relaciones(db, empleado_id)
    documento = Documento(empleado_id=empleado_id, **payload.model_dump())
    db.add(documento)
    db.commit()
    db.refresh(documento)
    return documento


@router.delete("/{empleado_id}/documentos/{documento_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_documento(
    empleado_id: int,
    documento_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_write),
):
    documento = (
        db.query(Documento)
        .filter(Documento.id == documento_id, Documento.empleado_id == empleado_id)
        .first()
    )
    if documento is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Documento no encontrado")
    db.delete(documento)
    db.commit()


# ---------------------------------------------------------------------------
# Evaluaciones de desempeño
# ---------------------------------------------------------------------------

@router.post("/{empleado_id}/evaluaciones", response_model=EvaluacionOut, status_code=status.HTTP_201_CREATED)
def agregar_evaluacion(
    empleado_id: int,
    payload: EvaluacionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_write),
):
    _empleado_con_relaciones(db, empleado_id)
    evaluacion = Evaluacion(empleado_id=empleado_id, **payload.model_dump())
    db.add(evaluacion)
    db.commit()
    db.refresh(evaluacion)
    return evaluacion


@router.delete("/{empleado_id}/evaluaciones/{evaluacion_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_evaluacion(
    empleado_id: int,
    evaluacion_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_write),
):
    evaluacion = (
        db.query(Evaluacion)
        .filter(Evaluacion.id == evaluacion_id, Evaluacion.empleado_id == empleado_id)
        .first()
    )
    if evaluacion is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evaluación no encontrada")
    db.delete(evaluacion)
    db.commit()


# ---------------------------------------------------------------------------
# Capacitaciones
# ---------------------------------------------------------------------------

@router.post(
    "/{empleado_id}/capacitaciones", response_model=CapacitacionOut, status_code=status.HTTP_201_CREATED
)
def agregar_capacitacion(
    empleado_id: int,
    payload: CapacitacionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_write),
):
    _empleado_con_relaciones(db, empleado_id)
    capacitacion = Capacitacion(empleado_id=empleado_id, **payload.model_dump())
    db.add(capacitacion)
    db.commit()
    db.refresh(capacitacion)
    return capacitacion


@router.delete("/{empleado_id}/capacitaciones/{capacitacion_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_capacitacion(
    empleado_id: int,
    capacitacion_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_write),
):
    capacitacion = (
        db.query(Capacitacion)
        .filter(Capacitacion.id == capacitacion_id, Capacitacion.empleado_id == empleado_id)
        .first()
    )
    if capacitacion is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Capacitación no encontrada")
    db.delete(capacitacion)
    db.commit()


# ---------------------------------------------------------------------------
# Exámenes médicos
# ---------------------------------------------------------------------------

@router.post(
    "/{empleado_id}/examenes-medicos", response_model=ExamenMedicoOut, status_code=status.HTTP_201_CREATED
)
def agregar_examen_medico(
    empleado_id: int,
    payload: ExamenMedicoCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_write),
):
    _empleado_con_relaciones(db, empleado_id)
    examen = ExamenMedico(empleado_id=empleado_id, **payload.model_dump())
    db.add(examen)
    db.commit()
    db.refresh(examen)
    return examen


@router.delete("/{empleado_id}/examenes-medicos/{examen_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_examen_medico(
    empleado_id: int,
    examen_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_write),
):
    examen = (
        db.query(ExamenMedico)
        .filter(ExamenMedico.id == examen_id, ExamenMedico.empleado_id == empleado_id)
        .first()
    )
    if examen is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Examen médico no encontrado")
    db.delete(examen)
    db.commit()


@router.get("/{empleado_id}/certificado-laboral")
def certificado_laboral(
    empleado_id: int,
    incluir_salario: bool = Query(
        default=False,
        description="Si es verdadero, el certificado indica el salario del último período de nómina registrado.",
    ),
    fecha_expedicion: date | None = Query(
        default=None,
        description="Fecha que se imprime como fecha de expedición. Por defecto, hoy.",
    ),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Genera el certificado laboral del empleado en PDF.

    Lo pueden emitir ambos roles: es un documento de consulta, no modifica nada.
    """
    empleado = _empleado_con_relaciones(db, empleado_id)

    if empleado.empresa is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"{empleado.nombre_completo} no tiene una empresa asignada (Ecodes, Envsol, u otra), "
                "así que no se puede saber qué razón social y NIT imprimir en el certificado. "
                "Asígnale una empresa desde su ficha y vuelve a intentarlo."
            ),
        )

    if incluir_salario and not empleado.nominas:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"{empleado.nombre_completo} no tiene nómina registrada, así que no se "
                "puede certificar un salario. Registra la nómina del período o genera "
                "el certificado sin salario."
            ),
        )

    if fecha_expedicion is not None:
        if fecha_expedicion > date.today():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="La fecha de expedición no puede ser futura.",
            )
        if fecha_expedicion < empleado.fecha_ingreso:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"La fecha de expedición no puede ser anterior al ingreso de "
                    f"{empleado.nombre_completo} ({empleado.fecha_ingreso.isoformat()})."
                ),
            )

    pdf = generar_certificado_laboral(
        empleado, incluir_salario=incluir_salario, fecha_expedicion=fecha_expedicion
    )

    # Nombre de archivo legible: "certificado_laboral_maria_lopez.pdf"
    base = unicodedata.normalize("NFKD", empleado.nombre_completo)
    base = base.encode("ascii", "ignore").decode("ascii").lower()
    base = re.sub(r"[^a-z0-9]+", "_", base).strip("_") or f"empleado_{empleado_id}"

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="certificado_laboral_{base}.pdf"'},
    )
