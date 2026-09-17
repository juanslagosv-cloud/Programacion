from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(30), nullable=False, default="Talento Humano")

    def __repr__(self) -> str:
        return f"User(username={self.username!r}, email={self.email!r}, role={self.role!r})"


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String(200), nullable=False)
    foto = Column(String(255), nullable=True)
    genero = Column(String(20), nullable=True)
    fecha_nacimiento = Column(Date, nullable=True)
    direccion = Column(String(255), nullable=True)
    nivel_educativo = Column(String(50), nullable=True)
    nombre_cargo = Column(String(120), nullable=True)
    tipo_cargo = Column(String(50), nullable=True)
    fecha_ingreso = Column(Date, nullable=True)
    estado = Column(String(30), default="Activo")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    formaciones = relationship("AcademicFormation", back_populates="employee", cascade="all, delete-orphan")
    experiencias = relationship("WorkExperience", back_populates="employee", cascade="all, delete-orphan")
    participaciones = relationship("Participation", back_populates="employee", cascade="all, delete-orphan")
    novedades = relationship("EmployeeEvent", back_populates="employee", cascade="all, delete-orphan")
    nominas = relationship("Payroll", back_populates="employee", cascade="all, delete-orphan")


class AcademicFormation(Base):
    __tablename__ = "academic_formations"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    titulo = Column(String(200), nullable=False)
    institucion = Column(String(200), nullable=False)
    anio = Column(Integer, nullable=False)
    employee = relationship("Employee", back_populates="formaciones")


class WorkExperience(Base):
    __tablename__ = "work_experiences"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    empresa = Column(String(200), nullable=False)
    cargo = Column(String(200), nullable=False)
    periodo = Column(String(80), nullable=False)
    employee = relationship("Employee", back_populates="experiencias")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    contratante = Column(String(200), nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin_estimada = Column(Date, nullable=True)
    presupuesto = Column(Numeric(12, 2), nullable=True, default=0)
    estado = Column(String(30), default="Activo")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    participaciones = relationship("Participation", back_populates="project", cascade="all, delete-orphan")
    novedades = relationship("EmployeeEvent", back_populates="project", cascade="all, delete-orphan")


class Participation(Base):
    __tablename__ = "participations"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    porcentaje = Column(Float, nullable=False, default=0)
    employee = relationship("Employee", back_populates="participaciones")
    project = relationship("Project", back_populates="participaciones")


class EmployeeEvent(Base):
    __tablename__ = "employee_events"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    tipo = Column(String(50), nullable=False)
    fecha = Column(Date, nullable=False)
    detalle = Column(Text, nullable=True)
    employee = relationship("Employee", back_populates="novedades")
    project = relationship("Project", back_populates="novedades")


class Payroll(Base):
    __tablename__ = "payrolls"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    periodo = Column(String(20), nullable=False)
    salario_base = Column(Numeric(12, 2), nullable=False, default=0)
    auxilio_transporte = Column(Numeric(12, 2), nullable=False, default=0)
    auxilio_movilidad = Column(Numeric(12, 2), nullable=False, default=0)
    descuentos = Column(Numeric(12, 2), nullable=False, default=0)
    total = Column(Numeric(12, 2), nullable=False, default=0)
    novedad_tipo = Column(String(80), nullable=True, default="Normal")
    novedad_detalle = Column(Text, nullable=True)
    employee = relationship("Employee", back_populates="nominas")


class Vacation(Base):
    __tablename__ = "vacations"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    ultima_toma = Column(Date, nullable=True)
    dias_pendientes = Column(Integer, default=0)
    employee = relationship("Employee")
