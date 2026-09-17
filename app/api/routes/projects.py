from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.crud import build_project_response, get_project_by_id
from app.database import get_db
from app.models import Project
from app.schemas import ProjectCreate, ProjectRead
from app.security import get_current_user, require_write_access

router = APIRouter(prefix="/proyectos", tags=["Proyectos"])


@router.get("", response_model=list[ProjectRead])
def list_proyectos(
    estado: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = db.query(Project)
    if estado:
        query = query.filter(Project.estado == estado)
    return [ProjectRead.model_validate(build_project_response(p)) for p in query.all()]


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_proyecto(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_write_access),
):
    project = Project(**payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return ProjectRead.model_validate(build_project_response(project))


@router.get("/{project_id}", response_model=ProjectRead)
def get_proyecto(project_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    project = get_project_by_id(db, project_id)
    return ProjectRead.model_validate(build_project_response(project))
