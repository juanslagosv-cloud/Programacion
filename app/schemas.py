from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserLogin(BaseModel):
    email: EmailStr
    role: str
    password: Optional[str] = None
    code: Optional[str] = None


class EmailCodeRequest(BaseModel):
    email: EmailStr
    role: str


class TokenPayload(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class AcademicFormationCreate(BaseModel):
    titulo: str
    institucion: str
    anio: int


class AcademicFormationRead(AcademicFormationCreate):
    id: int


class WorkExperienceCreate(BaseModel):
    empresa: str
    cargo: str
    periodo: str


class WorkExperienceRead(WorkExperienceCreate):
    id: int


class EmployeeBase(BaseModel):
    nombre_completo: str
    foto: Optional[str] = None
    genero: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    direccion: Optional[str] = None
    nivel_educativo: Optional[str] = None
    nombre_cargo: Optional[str] = None
    tipo_cargo: Optional[str] = None
    fecha_ingreso: Optional[date] = None
    estado: str = "Activo"


class EmployeeParticipationCreate(BaseModel):
    project_id: int
    porcentaje: float = Field(..., ge=1, le=100)


class EmployeeCreate(EmployeeBase):
    formaciones: List[AcademicFormationCreate] = []
    experiencias: List[WorkExperienceCreate] = []
    participaciones: List[EmployeeParticipationCreate] = []


class EmployeeRead(EmployeeBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    antiguedad: Optional[str] = None
    formaciones: List[AcademicFormationRead] = []
    experiencias: List[WorkExperienceRead] = []
    participaciones: List["ParticipationRead"] = []


class ProjectBase(BaseModel):
    nombre: str
    contratante: str
    fecha_inicio: date
    fecha_fin_estimada: Optional[date] = None
    presupuesto: Optional[Decimal] = Decimal("0")
    estado: str = "Activo"


class ProjectCreate(ProjectBase):
    pass


class ProjectRead(ProjectBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    participaciones: List["ParticipationRead"] = []


class ParticipationCreate(BaseModel):
    employee_id: int
    project_id: int
    porcentaje: float = Field(..., ge=0, le=100)

    @field_validator("porcentaje")
    @classmethod
    def validate_percentage(cls, value):
        if value <= 0:
            raise ValueError("El porcentaje debe ser mayor a 0")
        return value


class ParticipationRead(ParticipationCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class EventCreate(BaseModel):
    employee_id: int
    project_id: Optional[int] = None
    tipo: str
    fecha: date
    detalle: Optional[str] = None


class EventRead(EventCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int


class PayrollCreate(BaseModel):
    employee_id: int
    periodo: str
    salario_base: Decimal = Decimal("0")
    auxilio_transporte: Decimal = Decimal("0")
    auxilio_movilidad: Decimal = Decimal("0")
    descuentos: Decimal = Decimal("0")
    novedad_tipo: Optional[str] = "Normal"
    novedad_detalle: Optional[str] = None


class PayrollUpdate(PayrollCreate):
    pass


class PayrollRead(PayrollCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    total: Decimal


class AlertVacation(BaseModel):
    employee_id: int
    employee_name: str
    dias_pendientes: int
    mensaje: str


class AlertOverAssignment(BaseModel):
    employee_id: int
    employee_name: str
    total_porcentaje: float
    mensaje: str


class ExportSheet(BaseModel):
    name: str
    rows: List[dict]
