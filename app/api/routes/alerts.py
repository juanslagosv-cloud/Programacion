from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Employee, EmployeeEvent, Participation, Vacation
from app.security import get_current_user

router = APIRouter(prefix="/alertas", tags=["Alertas"])


@router.get("/vacaciones")
def vacations_alerts(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    rows = []
    for vac in db.query(Vacation).all():
        if vac.dias_pendientes > 5:
            rows.append({
                "employee_id": vac.employee_id,
                "employee_name": vac.employee.nombre_completo if vac.employee else "",
                "dias_pendientes": vac.dias_pendientes,
                "mensaje": "Vacaciones por vencer"
            })
    return rows


@router.get("/sobreasignacion")
def over_assignment_alerts(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    rows = []
    for emp in db.query(Employee).all():
        total = sum(p.porcentaje for p in emp.participaciones)
        if total >= 90:
            rows.append({
                "employee_id": emp.id,
                "employee_name": emp.nombre_completo,
                "total_porcentaje": total,
                "mensaje": "Sobreasignación de personal"
            })
    return rows


@router.get("/resumen")
def alerts_summary(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    vacations = len(db.query(Vacation).filter(Vacation.dias_pendientes > 5).all())
    pending_events = db.query(EmployeeEvent).count()
    return {"vacaciones": vacations, "novedades_sin_procesar": pending_events, "sobreasignacion": len(db.query(Employee).all())}
