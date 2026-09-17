from __future__ import annotations

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Payroll
from app.schemas import PayrollCreate, PayrollRead, PayrollUpdate
from app.security import get_current_user, require_write_access

router = APIRouter(prefix="/nomina", tags=["Nómina"])

SMMLV = Decimal("1_300_000")


def _validate_colombian_payroll(payload: PayrollCreate | PayrollUpdate) -> None:
    if payload.salario_base < SMMLV:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El salario base no puede ser inferior al salario mínimo legal vigente en Colombia.",
        )
    if payload.auxilio_transporte > payload.salario_base:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El auxilio de transporte no puede ser mayor al salario base.",
        )
    if payload.descuentos > payload.salario_base + payload.auxilio_transporte + payload.auxilio_movilidad:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Los descuentos no pueden superar la base liquidable del empleado.",
        )


@router.get("", response_model=list[PayrollRead])
def list_payroll(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    rows = db.query(Payroll).all()
    response = []
    for item in rows:
        response.append(
            {
                "id": item.id,
                "employee_id": item.employee_id,
                "periodo": item.periodo,
                "salario_base": item.salario_base,
                "auxilio_transporte": item.auxilio_transporte,
                "auxilio_movilidad": item.auxilio_movilidad,
                "descuentos": item.descuentos,
                "total": item.total,
                "novedad_tipo": "Normal",
                "novedad_detalle": None,
            }
        )
    return response


@router.post("", response_model=PayrollRead, status_code=status.HTTP_201_CREATED)
def create_payroll(
    payload: PayrollCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_write_access),
):
    _validate_colombian_payroll(payload)
    total = payload.salario_base + payload.auxilio_transporte + payload.auxilio_movilidad - payload.descuentos
    item = Payroll(**payload.model_dump(), total=total)
    db.add(item)
    db.commit()
    db.refresh(item)
    return PayrollRead.model_validate({
        "id": item.id,
        "employee_id": item.employee_id,
        "periodo": item.periodo,
        "salario_base": item.salario_base,
        "auxilio_transporte": item.auxilio_transporte,
        "auxilio_movilidad": item.auxilio_movilidad,
        "descuentos": item.descuentos,
        "total": item.total,
        "novedad_tipo": item.novedad_tipo if hasattr(item, "novedad_tipo") else "Normal",
        "novedad_detalle": item.novedad_detalle if hasattr(item, "novedad_detalle") else None,
    })


@router.put("/{payroll_id}", response_model=PayrollRead)
def update_payroll(
    payroll_id: int,
    payload: PayrollUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(require_write_access),
):
    item = db.query(Payroll).filter(Payroll.id == payroll_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registro de nómina no encontrado")

    _validate_colombian_payroll(payload)
    item.employee_id = payload.employee_id
    item.periodo = payload.periodo
    item.salario_base = payload.salario_base
    item.auxilio_transporte = payload.auxilio_transporte
    item.auxilio_movilidad = payload.auxilio_movilidad
    item.descuentos = payload.descuentos
    item.total = payload.salario_base + payload.auxilio_transporte + payload.auxilio_movilidad - payload.descuentos
    item.novedad_tipo = payload.novedad_tipo or "Normal"
    item.novedad_detalle = payload.novedad_detalle
    db.commit()
    db.refresh(item)
    return PayrollRead.model_validate({
        "id": item.id,
        "employee_id": item.employee_id,
        "periodo": item.periodo,
        "salario_base": item.salario_base,
        "auxilio_transporte": item.auxilio_transporte,
        "auxilio_movilidad": item.auxilio_movilidad,
        "descuentos": item.descuentos,
        "total": item.total,
        "novedad_tipo": item.novedad_tipo,
        "novedad_detalle": item.novedad_detalle,
    })
