from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.crud import build_employee_response, get_employee_by_id
from app.database import get_db
from app.models import AcademicFormation, Employee, Participation, WorkExperience
from app.schemas import EmployeeCreate, EmployeeRead
from app.security import get_current_user, require_write_access

router = APIRouter(prefix="/empleados", tags=["Empleados"])


@router.get("", response_model=list[EmployeeRead])
def list_empleados(
    estado: Optional[str] = Query(default=None),
    project_id: Optional[int] = Query(default=None),
    tipo_cargo: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = db.query(Employee)
    if estado:
        query = query.filter(Employee.estado == estado)
    if tipo_cargo:
        query = query.filter(Employee.tipo_cargo == tipo_cargo)
    empleados = query.all()

    if project_id is not None:
        empleados = [e for e in empleados if any(p.project_id == project_id for p in e.participaciones)]

    return [EmployeeRead.model_validate(build_employee_response(e)) for e in empleados]


@router.post("", response_model=EmployeeRead, status_code=status.HTTP_201_CREATED)
def create_empleado(
    payload: EmployeeCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_write_access),
):
    employee = Employee(**payload.model_dump(exclude={"formaciones", "experiencias", "participaciones"}))
    db.add(employee)
    db.commit()
    db.refresh(employee)

    for item in payload.formaciones:
        db.add(AcademicFormation(employee_id=employee.id, **item.model_dump()))

    for item in payload.experiencias:
        db.add(WorkExperience(employee_id=employee.id, **item.model_dump()))

    for item in payload.participaciones:
        db.add(Participation(employee_id=employee.id, project_id=item.project_id, porcentaje=item.porcentaje))

    db.commit()
    return EmployeeRead.model_validate(build_employee_response(employee))


@router.get("/{employee_id}", response_model=EmployeeRead)
def get_empleado(employee_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    employee = get_employee_by_id(db, employee_id)
    return EmployeeRead.model_validate(build_employee_response(employee))


@router.post("/{employee_id}/estudios")
def add_estudio(employee_id: int, payload: dict, db: Session = Depends(get_db), _: object = Depends(require_write_access)):
    employee = get_employee_by_id(db, employee_id)
    item = AcademicFormation(employee_id=employee.id, **payload)
    db.add(item)
    db.commit()
    return {"id": item.id, "message": "Estudio agregado"}


@router.post("/{employee_id}/experiencia")
def add_experiencia(employee_id: int, payload: dict, db: Session = Depends(get_db), _: object = Depends(require_write_access)):
    employee = get_employee_by_id(db, employee_id)
    item = WorkExperience(employee_id=employee.id, **payload)
    db.add(item)
    db.commit()
    return {"id": item.id, "message": "Experiencia agregada"}
