from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import List

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import AcademicFormation, Employee, EmployeeEvent, Participation, Payroll, Project, User, Vacation, WorkExperience
from app.security import get_password_hash


def create_seed_users(db: Session) -> None:
    seeded_users = [
        {"username": "talento", "email": "talento@ecodes.com", "password": "talento123", "role": "Talento Humano"},
        {"username": "admin", "email": "admin@ecodes.com", "password": "admin123", "role": "Administrativo"},
        {"username": "juans.lagosv", "email": "juans.lagosv@gmail.com", "password": "ecodes123", "role": "Talento Humano"},
    ]

    for user_data in seeded_users:
        user = db.query(User).filter((User.email == user_data["email"]) | (User.username == user_data["username"])).first()
        if user:
            user.email = user_data["email"]
            user.username = user_data["username"]
            user.role = user_data["role"]
            user.password_hash = get_password_hash(user_data["password"])
        else:
            db.add(
                User(
                    username=user_data["username"],
                    email=user_data["email"],
                    password_hash=get_password_hash(user_data["password"]),
                    role=user_data["role"],
                )
            )

    db.commit()


def set_employee_state_from_event(db: Session, employee_id: int, event_type: str) -> None:
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        return
    if event_type == "Salida":
        employee.estado = "Inactivo"
        db.commit()


def calculate_antiguedad(fecha_ingreso: date | None) -> str:
    if not fecha_ingreso:
        return "Sin fecha"
    today = date.today()
    years = today.year - fecha_ingreso.year - ((today.month, today.day) < (fecha_ingreso.month, fecha_ingreso.day))
    months = (today.year - fecha_ingreso.year) * 12 + (today.month - fecha_ingreso.month)
    if years > 0:
        return f"{years} año(s)"
    return f"{months} mes(es)"


def get_employee_by_id(db: Session, employee_id: int) -> Employee:
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empleado no encontrado")
    return employee


def get_project_by_id(db: Session, project_id: int) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proyecto no encontrado")
    return project


def validate_participation_total(db: Session, employee_id: int, project_id: int, porcentaje: float) -> None:
    current = db.query(func.coalesce(func.sum(Participation.porcentaje), 0)).filter(Participation.employee_id == employee_id).scalar() or 0
    if project_id:
        current_project = db.query(Participation).filter(Participation.employee_id == employee_id, Participation.project_id == project_id).first()
        if current_project and current_project.porcentaje != porcentaje:
            current = current - current_project.porcentaje + porcentaje
        else:
            current = current + porcentaje
    else:
        current = current + porcentaje
    if current > 100:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La suma de participación no puede superar el 100%")


def build_employee_response(employee: Employee) -> dict:
    return {
        "id": employee.id,
        "nombre_completo": employee.nombre_completo,
        "foto": employee.foto,
        "genero": employee.genero,
        "fecha_nacimiento": employee.fecha_nacimiento.isoformat() if employee.fecha_nacimiento else None,
        "direccion": employee.direccion,
        "nivel_educativo": employee.nivel_educativo,
        "nombre_cargo": employee.nombre_cargo,
        "tipo_cargo": employee.tipo_cargo,
        "fecha_ingreso": employee.fecha_ingreso.isoformat() if employee.fecha_ingreso else None,
        "estado": employee.estado,
        "antiguedad": calculate_antiguedad(employee.fecha_ingreso),
        "formaciones": [
            {"id": f.id, "titulo": f.titulo, "institucion": f.institucion, "anio": f.anio}
            for f in employee.formaciones
        ],
        "experiencias": [
            {"id": e.id, "empresa": e.empresa, "cargo": e.cargo, "periodo": e.periodo}
            for e in employee.experiencias
        ],
        "participaciones": [
            {
                "id": p.id,
                "employee_id": p.employee_id,
                "project_id": p.project_id,
                "porcentaje": p.porcentaje,
            }
            for p in employee.participaciones
        ],
    }


def build_project_response(project: Project) -> dict:
    return {
        "id": project.id,
        "nombre": project.nombre,
        "contratante": project.contratante,
        "fecha_inicio": project.fecha_inicio.isoformat() if project.fecha_inicio else None,
        "fecha_fin_estimada": project.fecha_fin_estimada.isoformat() if project.fecha_fin_estimada else None,
        "presupuesto": str(project.presupuesto) if project.presupuesto is not None else "0",
        "estado": project.estado,
        "participaciones": [
            {
                "id": p.id,
                "employee_id": p.employee_id,
                "project_id": p.project_id,
                "porcentaje": p.porcentaje,
            }
            for p in project.participaciones
        ],
    }


def employee_total_participation(db: Session, employee_id: int) -> float:
    total = db.query(func.coalesce(func.sum(Participation.porcentaje), 0.0)).filter(Participation.employee_id == employee_id).scalar() or 0.0
    return float(total)


def create_seed_data(db: Session) -> None:
    if db.query(Employee).count() > 0:
        return

    emp1 = Employee(
        nombre_completo="Ana María Pérez",
        foto="",
        genero="Femenino",
        fecha_nacimiento=date(1990, 6, 18),
        direccion="Bogotá",
        nivel_educativo="Profesional",
        nombre_cargo="Analista Ambiental",
        tipo_cargo="Profesional",
        fecha_ingreso=date(2021, 3, 10),
        estado="Activo",
    )
    emp2 = Employee(
        nombre_completo="Carlos Rojas",
        foto="",
        genero="Masculino",
        fecha_nacimiento=date(1988, 11, 2),
        direccion="Lima",
        nivel_educativo="Técnico",
        nombre_cargo="Monitoreo de Biodiversidad",
        tipo_cargo="Técnico",
        fecha_ingreso=date(2019, 4, 12),
        estado="Activo",
    )
    emp3 = Employee(
        nombre_completo="Lucía Gómez",
        foto="",
        genero="Femenino",
        fecha_nacimiento=date(1993, 9, 22),
        direccion="Buenos Aires",
        nivel_educativo="Tecnólogo",
        nombre_cargo="Coordinadora de Proyectos",
        tipo_cargo="Administrativo",
        fecha_ingreso=date(2022, 8, 20),
        estado="Activo",
    )
    db.add_all([emp1, emp2, emp3])
    db.commit()

    emp1.formaciones = [
        AcademicFormation(titulo="Ingeniería Ambiental", institucion="Universidad Nacional", anio=2014),
        AcademicFormation(titulo="Especialización en GIS", institucion="Universidad Javeriana", anio=2018),
    ]
    emp1.experiencias = [
        WorkExperience(empresa="Fundación Verde", cargo="Analista de campo", periodo="2015-2018"),
        WorkExperience(empresa="Ecodes", cargo="Analista Ambiental", periodo="2018-2021"),
    ]
    emp2.formaciones = [AcademicFormation(titulo="Tecnología Ambiental", institucion="UTP", anio=2011)]
    emp3.formaciones = [AcademicFormation(titulo="Administración de Empresas", institucion="UBA", anio=2010)]

    proj1 = Project(nombre="Restauración del río Bogotá", contratante="CAR", fecha_inicio=date(2024, 1, 15), fecha_fin_estimada=date(2025, 12, 30), presupuesto=Decimal("250000000"), estado="Activo")
    proj2 = Project(nombre="Monitoreo de fauna en Cusco", contratante="Municipio regional", fecha_inicio=date(2023, 6, 1), fecha_fin_estimada=date(2026, 5, 30), presupuesto=Decimal("180000000"), estado="Continuo")
    db.add_all([proj1, proj2])
    db.commit()

    db.add_all([
        Participation(employee_id=emp1.id, project_id=proj1.id, porcentaje=60),
        Participation(employee_id=emp1.id, project_id=proj2.id, porcentaje=30),
        Participation(employee_id=emp2.id, project_id=proj2.id, porcentaje=80),
        Participation(employee_id=emp3.id, project_id=proj1.id, porcentaje=40),
    ])
    db.commit()

    db.add_all([
        EmployeeEvent(employee_id=emp1.id, project_id=proj1.id, tipo="Cambio de proyecto", fecha=date(2024, 2, 5), detalle="Ajuste de participación por nuevo contrato"),
        EmployeeEvent(employee_id=emp2.id, project_id=proj2.id, tipo="Ingreso", fecha=date(2024, 1, 10), detalle="Ingreso a proyecto de monitoreo"),
    ])
    db.commit()

    db.add_all([
        Payroll(employee_id=emp1.id, periodo="2024-09", salario_base=Decimal("4500000"), auxilio_transporte=Decimal("140000"), auxilio_movilidad=Decimal("0"), descuentos=Decimal("120000"), total=Decimal("4400000")),
        Payroll(employee_id=emp2.id, periodo="2024-09", salario_base=Decimal("3600000"), auxilio_transporte=Decimal("0"), auxilio_movilidad=Decimal("260000"), descuentos=Decimal("90000"), total=Decimal("3600000")),
    ])
    db.commit()

    db.add_all([
        Vacation(employee_id=emp1.id, ultima_toma=date(2024, 3, 10), dias_pendientes=10),
        Vacation(employee_id=emp2.id, ultima_toma=date(2024, 1, 5), dias_pendientes=18),
    ])
    db.commit()
