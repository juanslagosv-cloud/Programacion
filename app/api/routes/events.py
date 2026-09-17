from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.crud import set_employee_state_from_event
from app.database import get_db
from app.models import EmployeeEvent
from app.schemas import EventCreate, EventRead
from app.security import get_current_user, require_write_access

router = APIRouter(prefix="/novedades", tags=["Novedades"])


@router.get("", response_model=list[EventRead])
def list_events(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return [
        EventRead.model_validate({
            "id": e.id,
            "employee_id": e.employee_id,
            "project_id": e.project_id,
            "tipo": e.tipo,
            "fecha": e.fecha,
            "detalle": e.detalle,
        })
        for e in db.query(EmployeeEvent).order_by(EmployeeEvent.fecha.desc()).all()
    ]


@router.post("", response_model=EventRead, status_code=status.HTTP_201_CREATED)
def create_event(
    payload: EventCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_write_access),
):
    event = EmployeeEvent(**payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    set_employee_state_from_event(db, payload.employee_id, payload.tipo)
    return EventRead.model_validate({
        "id": event.id,
        "employee_id": event.employee_id,
        "project_id": event.project_id,
        "tipo": event.tipo,
        "fecha": event.fecha,
        "detalle": event.detalle,
    })
