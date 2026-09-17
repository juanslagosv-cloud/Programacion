from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import get_current_user, require_write
from app.models import Empleado, Nomina, Novedad
from app.schemas import NominaCreate, NominaOut, NominaResumen
from app.utils import liquidar_nomina, novedades_del_mes

router = APIRouter(prefix="/nomina", tags=["Nómina"])


def _to_out(nomina: Nomina, db: Session) -> NominaOut:
    data = NominaOut.model_validate(nomina)
    data.empleado_nombre = nomina.empleado.nombre_completo
    data.novedades_mes = novedades_del_mes(nomina.empleado, nomina.periodo)
    return data


@router.get("", response_model=list[NominaOut])
def listar_nomina(
    periodo: str | None = None,
    empleado_id: int | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = db.query(Nomina).options(joinedload(Nomina.empleado))
    if periodo:
        query = query.filter(Nomina.periodo == periodo)
    if empleado_id:
        query = query.filter(Nomina.empleado_id == empleado_id)
    registros = query.order_by(Nomina.periodo.desc()).all()
    return [_to_out(n, db) for n in registros]


@router.get("/resumen", response_model=NominaResumen)
def resumen_nomina(
    periodo: str | None = None, db: Session = Depends(get_db), current_user=Depends(get_current_user)
):
    periodo = periodo or date.today().strftime("%Y-%m")
    registros = db.query(Nomina).filter(Nomina.periodo == periodo).all()
    total = sum(float(n.total) for n in registros)
    costo_empleador = sum(float(n.costo_empleador) for n in registros)
    sin_procesar = db.query(Novedad).filter(Novedad.procesada.is_(False)).count()

    hoy = date.today()
    if hoy.month == 12:
        siguiente = date(hoy.year + 1, 1, 5)
    else:
        siguiente = date(hoy.year, hoy.month + 1, 5)

    return NominaResumen(
        nomina_total_mes=round(total, 2),
        costo_total_empleador=round(costo_empleador, 2),
        carga_prestacional=round((costo_empleador / total - 1) * 100, 1) if total else 0,
        proximo_pago=siguiente.isoformat(),
        novedades_sin_procesar=sin_procesar,
    )


@router.post("", response_model=NominaOut, status_code=status.HTTP_201_CREATED)
def crear_nomina(
    payload: NominaCreate, db: Session = Depends(get_db), current_user=Depends(require_write)
):
    empleado = db.query(Empleado).filter(Empleado.id == payload.empleado_id).first()
    if empleado is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empleado no encontrado")

    liq = liquidar_nomina(
        empleado,
        payload.salario_base,
        payload.auxilio_transporte,
        payload.auxilio_movilidad,
        payload.descuentos,
    )

    nomina = Nomina(
        empleado_id=payload.empleado_id,
        periodo=payload.periodo,
        salario_base=liq.salario_base,
        auxilio_transporte=liq.auxilio_transporte,
        auxilio_movilidad=liq.auxilio_movilidad,
        salud_empleado=liq.salud_empleado,
        pension_empleado=liq.pension_empleado,
        descuentos=liq.otros_descuentos,
        total_descuentos=liq.total_descuentos,
        total=liq.neto_pagado,
        prima=liq.prima,
        cesantias=liq.cesantias,
        intereses_cesantias=liq.intereses_cesantias,
        provision_vacaciones=liq.provision_vacaciones,
        pension_empleador=liq.pension_empleador,
        arl=liq.arl,
        otros_aportes=liq.otros_aportes,
        total_prestaciones=liq.total_prestaciones,
        costo_empleador=liq.costo_empleador,
        pagada=payload.pagada,
    )
    db.add(nomina)
    db.commit()
    db.refresh(nomina)
    return _to_out(nomina, db)


@router.delete("/{nomina_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_nomina(
    nomina_id: int, db: Session = Depends(get_db), current_user=Depends(require_write)
):
    nomina = db.query(Nomina).filter(Nomina.id == nomina_id).first()
    if nomina is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro de nómina no encontrado")
    db.delete(nomina)
    db.commit()
