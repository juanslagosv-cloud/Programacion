from __future__ import annotations

import io
from typing import Any

import pandas as pd
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AcademicFormation, Employee, EmployeeEvent, Participation, Payroll, Project, WorkExperience
from app.security import get_current_user

router = APIRouter(prefix="/exportar", tags=["Exportación"])


@router.get("/excel")
def export_excel(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    excel_buffer = io.BytesIO()

    frames = {
        "empleados": pd.DataFrame([
            {
                "id": e.id,
                "nombre_completo": e.nombre_completo,
                "genero": e.genero,
                "fecha_nacimiento": e.fecha_nacimiento,
                "direccion": e.direccion,
                "nivel_educativo": e.nivel_educativo,
                "nombre_cargo": e.nombre_cargo,
                "tipo_cargo": e.tipo_cargo,
                "fecha_ingreso": e.fecha_ingreso,
                "estado": e.estado,
            }
            for e in db.query(Employee).all()
        ]),
        "estudios": pd.DataFrame([
            {
                "id": s.id,
                "employee_id": s.employee_id,
                "titulo": s.titulo,
                "institucion": s.institucion,
                "anio": s.anio,
            }
            for s in db.query(AcademicFormation).all()
        ]),
        "experiencia": pd.DataFrame([
            {
                "id": w.id,
                "employee_id": w.employee_id,
                "empresa": w.empresa,
                "cargo": w.cargo,
                "periodo": w.periodo,
            }
            for w in db.query(WorkExperience).all()
        ]),
        "proyectos": pd.DataFrame([
            {
                "id": p.id,
                "nombre": p.nombre,
                "contratante": p.contratante,
                "fecha_inicio": p.fecha_inicio,
                "fecha_fin_estimada": p.fecha_fin_estimada,
                "presupuesto": p.presupuesto,
                "estado": p.estado,
            }
            for p in db.query(Project).all()
        ]),
        "participaciones": pd.DataFrame([
            {
                "id": p.id,
                "employee_id": p.employee_id,
                "project_id": p.project_id,
                "porcentaje": p.porcentaje,
            }
            for p in db.query(Participation).all()
        ]),
        "nomina": pd.DataFrame([
            {
                "id": n.id,
                "employee_id": n.employee_id,
                "periodo": n.periodo,
                "salario_base": n.salario_base,
                "auxilio_transporte": n.auxilio_transporte,
                "auxilio_movilidad": n.auxilio_movilidad,
                "descuentos": n.descuentos,
                "total": n.total,
            }
            for n in db.query(Payroll).all()
        ]),
        "novedades": pd.DataFrame([
            {
                "id": e.id,
                "employee_id": e.employee_id,
                "project_id": e.project_id,
                "tipo": e.tipo,
                "fecha": e.fecha,
                "detalle": e.detalle,
            }
            for e in db.query(EmployeeEvent).all()
        ]),
    }

    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        for name, df in frames.items():
            df.columns = [str(c).replace(" ", "_").lower() for c in df.columns]
            df.to_excel(writer, sheet_name=name[:31], index=False)

    excel_buffer.seek(0)
    return StreamingResponse(
        excel_buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=ecodes_hr_export.xlsx"},
    )
