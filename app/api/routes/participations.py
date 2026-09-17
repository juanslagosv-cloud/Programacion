from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.crud import validate_participation_total
from app.database import get_db
from app.models import Participation
from app.schemas import ParticipationCreate, ParticipationRead
from app.security import get_current_user, require_write_access

router = APIRouter(prefix="/participaciones", tags=["Participaciones"])


@router.get("", response_model=list[ParticipationRead])
def list_participaciones(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return [
        ParticipationRead.model_validate({
            "id": p.id,
            "employee_id": p.employee_id,
            "project_id": p.project_id,
            "porcentaje": p.porcentaje,
        })
        for p in db.query(Participation).all()
    ]


@router.post("", response_model=ParticipationRead, status_code=status.HTTP_201_CREATED)
def create_participacion(
    payload: ParticipationCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_write_access),
):
    validate_participation_total(db, payload.employee_id, payload.project_id, payload.porcentaje)
    item = Participation(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return ParticipationRead.model_validate({
        "id": item.id,
        "employee_id": item.employee_id,
        "project_id": item.project_id,
        "porcentaje": item.porcentaje,
    })


@router.delete("/{participation_id}")
def delete_participacion(participation_id: int, db: Session = Depends(get_db), _: object = Depends(require_write_access)):
    item = db.query(Participation).filter(Participation.id == participation_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participación no encontrada")
    db.delete(item)
    db.commit()
    return {"message": "Participación eliminada"}
