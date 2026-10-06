from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import CurrentUser, get_current_user, require_write
from app.models import ParametroLegal
from app.schemas import ParametroLegalCreate, ParametroLegalOut, ParametroLegalUpdate
from app.utils import ParametroLegalNoEncontrado, obtener_parametro

router = APIRouter(prefix="/parametros-legales", tags=["Parámetros legales"])


def _to_out(p: ParametroLegal) -> ParametroLegalOut:
    data = ParametroLegalOut.model_validate(p)
    data.usuario_cambio_nombre = p.usuario_cambio.nombre if p.usuario_cambio else None
    hoy = date.today()
    data.vigente_actualmente = (
        p.activo and p.fecha_inicio_vigencia <= hoy and (p.fecha_fin_vigencia is None or p.fecha_fin_vigencia >= hoy)
    )
    return data


@router.get("", response_model=list[ParametroLegalOut])
def listar_parametros(
    codigo: str | None = Query(default=None),
    anio: int | None = Query(default=None),
    activo: bool | None = Query(default=None),
    pendiente_verificacion: bool | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Todas las vigencias registradas (no solo la actual): esta misma lista,
    agrupada por código, es el histórico normativo."""
    query = db.query(ParametroLegal).options(joinedload(ParametroLegal.usuario_cambio))
    if codigo:
        query = query.filter(ParametroLegal.codigo == codigo)
    if anio is not None:
        query = query.filter(ParametroLegal.anio == anio)
    if activo is not None:
        query = query.filter(ParametroLegal.activo == activo)
    if pendiente_verificacion is not None:
        query = query.filter(ParametroLegal.pendiente_verificacion == pendiente_verificacion)
    parametros = query.order_by(ParametroLegal.codigo, ParametroLegal.fecha_inicio_vigencia.desc()).all()
    return [_to_out(p) for p in parametros]


@router.get("/codigos")
def listar_codigos(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Catálogo de códigos ya usados, con su nombre y unidad más recientes —
    para poblar selectores en el frontend sin tener que repetir el catálogo
    ahí también."""
    parametros = (
        db.query(ParametroLegal)
        .order_by(ParametroLegal.codigo, ParametroLegal.fecha_inicio_vigencia.desc())
        .all()
    )
    vistos = {}
    for p in parametros:
        if p.codigo not in vistos:
            vistos[p.codigo] = {"codigo": p.codigo, "nombre": p.nombre, "unidad": p.unidad.value}
    return sorted(vistos.values(), key=lambda x: x["nombre"])


@router.get("/{codigo}/vigente", response_model=ParametroLegalOut)
def parametro_vigente(
    codigo: str,
    fecha: date | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """La vigencia que aplica para `codigo` en `fecha` (por defecto, hoy).
    Es el mismo mecanismo que usan internamente los motores de cálculo."""
    try:
        parametro = obtener_parametro(db, codigo, fecha)
    except ParametroLegalNoEncontrado as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return _to_out(parametro)


@router.post("", response_model=ParametroLegalOut, status_code=status.HTTP_201_CREATED)
def crear_vigencia(
    payload: ParametroLegalCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_write),
):
    """Crea una nueva vigencia de un código. Si existe una vigencia abierta
    (sin fecha_fin_vigencia) para el mismo código que empieza antes de esta,
    se cierra automáticamente el día anterior al inicio de la nueva — así
    nunca quedan dos vigencias abiertas "compitiendo" por la misma fecha, y
    la anterior queda intacta como historia. No se permite crear una
    vigencia que se cruce con otra ya cerrada (esa sí se considera
    histórica y protegida)."""
    if payload.fecha_fin_vigencia and payload.fecha_fin_vigencia < payload.fecha_inicio_vigencia:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha final de vigencia no puede ser anterior a la inicial",
        )

    cerradas = (
        db.query(ParametroLegal)
        .filter(
            ParametroLegal.codigo == payload.codigo,
            ParametroLegal.fecha_fin_vigencia.isnot(None),
            ParametroLegal.fecha_inicio_vigencia <= (payload.fecha_fin_vigencia or date(9999, 12, 31)),
            ParametroLegal.fecha_fin_vigencia >= payload.fecha_inicio_vigencia,
        )
        .first()
    )
    if cerradas:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"La nueva vigencia se cruza con una vigencia histórica ya cerrada de «{payload.codigo}» "
                f"({cerradas.fecha_inicio_vigencia} a {cerradas.fecha_fin_vigencia}). "
                "No se pueden modificar parámetros históricos; corrige las fechas de la nueva vigencia."
            ),
        )

    abierta = (
        db.query(ParametroLegal)
        .filter(
            ParametroLegal.codigo == payload.codigo,
            ParametroLegal.fecha_fin_vigencia.is_(None),
            ParametroLegal.fecha_inicio_vigencia < payload.fecha_inicio_vigencia,
        )
        .order_by(ParametroLegal.fecha_inicio_vigencia.desc())
        .first()
    )
    if abierta:
        abierta.fecha_fin_vigencia = payload.fecha_inicio_vigencia - timedelta(days=1)
        abierta.usuario_cambio_id = current_user.id

    parametro = ParametroLegal(**payload.model_dump(), usuario_cambio_id=current_user.id)
    db.add(parametro)
    db.commit()
    db.refresh(parametro)
    return _to_out(parametro)


@router.put("/{parametro_id}", response_model=ParametroLegalOut)
def actualizar_metadatos(
    parametro_id: int,
    payload: ParametroLegalUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_write),
):
    """Solo corrige metadatos (nombre, descripción, norma, observaciones,
    estado, verificación) — nunca el valor ni las fechas de vigencia. Si el
    valor cambió, crea una vigencia nueva (POST) en vez de editar esta."""
    parametro = db.query(ParametroLegal).filter(ParametroLegal.id == parametro_id).first()
    if parametro is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parámetro no encontrado")
    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(parametro, campo, valor)
    parametro.usuario_cambio_id = current_user.id
    db.commit()
    db.refresh(parametro)
    return _to_out(parametro)


@router.delete("/{parametro_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_vigencia(
    parametro_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(require_write),
):
    """Solo se puede eliminar la vigencia más reciente de su código (es
    decir, deshacer la última creación) — para no abrir huecos en medio del
    historial. Si al crearla se cerró automáticamente la vigencia anterior,
    esa reabre."""
    parametro = db.query(ParametroLegal).filter(ParametroLegal.id == parametro_id).first()
    if parametro is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parámetro no encontrado")

    mas_reciente = (
        db.query(ParametroLegal)
        .filter(ParametroLegal.codigo == parametro.codigo)
        .order_by(ParametroLegal.fecha_inicio_vigencia.desc())
        .first()
    )
    if mas_reciente.id != parametro.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Solo se puede eliminar la vigencia más reciente de un código, para no dejar "
                "huecos en el historial normativo."
            ),
        )

    anterior = (
        db.query(ParametroLegal)
        .filter(
            ParametroLegal.codigo == parametro.codigo,
            ParametroLegal.id != parametro.id,
            ParametroLegal.fecha_fin_vigencia == parametro.fecha_inicio_vigencia - timedelta(days=1),
        )
        .first()
    )
    if anterior:
        anterior.fecha_fin_vigencia = None

    db.delete(parametro)
    db.commit()
