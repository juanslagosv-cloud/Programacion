from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import (
    EstadoEmpleado,
    EstadoProyecto,
    Genero,
    NivelEducativo,
    PeriodicidadPago,
    RolUsuario,
    TipoCargo,
    TipoNovedad,
)


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    username: str
    password: str
    rol: RolUsuario


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    rol: RolUsuario
    nombre: str
    username: str


class UsuarioOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    nombre: str
    rol: RolUsuario
    activo: bool


# ---------------------------------------------------------------------------
# Estudios
# ---------------------------------------------------------------------------

class EstudioBase(BaseModel):
    titulo: str
    institucion: str
    anio: int = Field(ge=1950, le=2100)


class EstudioCreate(EstudioBase):
    pass


class EstudioOut(EstudioBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    empleado_id: int


# ---------------------------------------------------------------------------
# Experiencia
# ---------------------------------------------------------------------------

class ExperienciaBase(BaseModel):
    empresa: str
    cargo: str
    periodo: str


class ExperienciaCreate(ExperienciaBase):
    pass


class ExperienciaOut(ExperienciaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    empleado_id: int


# ---------------------------------------------------------------------------
# Participaciones
# ---------------------------------------------------------------------------

class ParticipacionBase(BaseModel):
    empleado_id: int
    proyecto_id: int
    porcentaje: float = Field(gt=0, le=100)


class ParticipacionCreate(ParticipacionBase):
    pass


class ParticipacionUpdate(BaseModel):
    porcentaje: float = Field(gt=0, le=100)


class ParticipacionOut(ParticipacionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    fecha_asignacion: date
    empleado_nombre: Optional[str] = None
    proyecto_nombre: Optional[str] = None


# ---------------------------------------------------------------------------
# Empleados
# ---------------------------------------------------------------------------

class EmpleadoBase(BaseModel):
    nombre_completo: str
    foto_url: Optional[str] = None
    genero: Genero
    fecha_nacimiento: date
    direccion: Optional[str] = None
    nivel_educativo: NivelEducativo
    nombre_cargo: str
    tipo_cargo: TipoCargo
    fecha_ingreso: date
    estado: EstadoEmpleado = EstadoEmpleado.activo
    periodicidad_pago: PeriodicidadPago = PeriodicidadPago.mensual
    vacaciones_ultima_toma: Optional[date] = None
    vacaciones_dias_pendientes: int = 0


class EmpleadoCreate(EmpleadoBase):
    estudios: list[EstudioCreate] = []
    experiencias: list[ExperienciaCreate] = []


class EmpleadoUpdate(EmpleadoBase):
    pass


class EmpleadoListOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre_completo: str
    foto_url: Optional[str] = None
    nombre_cargo: str
    tipo_cargo: TipoCargo
    estado: EstadoEmpleado
    periodicidad_pago: PeriodicidadPago
    fecha_ingreso: date
    antiguedad_meses: int = 0
    proyectos: list[str] = []
    porcentaje_total: float = 0


class EmpleadoOut(EmpleadoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    antiguedad_meses: int = 0
    estudios: list[EstudioOut] = []
    experiencias: list[ExperienciaOut] = []
    participaciones: list[ParticipacionOut] = []
    porcentaje_total: float = 0


# ---------------------------------------------------------------------------
# Proyectos
# ---------------------------------------------------------------------------

class ProyectoBase(BaseModel):
    nombre: str
    contratante: str
    fecha_inicio: date
    fecha_fin: Optional[date] = None
    presupuesto: float = 0
    estado: EstadoProyecto = EstadoProyecto.activo


class ProyectoCreate(ProyectoBase):
    pass


class ProyectoUpdate(ProyectoBase):
    pass


class ProyectoListOut(ProyectoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tamano_equipo: int = 0
    costo_nomina_mes: float = 0
    porcentaje_rotacion: float = 0


class ProyectoOut(ProyectoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    tamano_equipo: int = 0
    costo_nomina_mes: float = 0
    porcentaje_rotacion: float = 0
    participaciones: list[ParticipacionOut] = []


# ---------------------------------------------------------------------------
# Novedades
# ---------------------------------------------------------------------------

class NovedadBase(BaseModel):
    empleado_id: int
    proyecto_id: Optional[int] = None
    tipo: TipoNovedad
    fecha: date
    detalle: Optional[str] = None


class NovedadCreate(NovedadBase):
    pass


class NovedadOut(NovedadBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    procesada: bool
    empleado_nombre: Optional[str] = None
    proyecto_nombre: Optional[str] = None


# ---------------------------------------------------------------------------
# Nómina
# ---------------------------------------------------------------------------

class NominaBase(BaseModel):
    empleado_id: int
    periodo: str = Field(pattern=r"^\d{4}-\d{2}$")
    quincena: Optional[int] = Field(default=None, ge=1, le=2)  # None = mes completo
    salario_base: float = Field(ge=0)  # salario mensual del contrato
    auxilio_transporte: float = 0
    auxilio_movilidad: float = 0
    descuentos: float = 0
    pagada: bool = False


class NominaCreate(NominaBase):
    pass


class NominaOut(NominaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    fecha_pago: Optional[date] = None
    dias_liquidados: int = 30
    salario_devengado: float = 0
    # Deducciones al trabajador
    salud_empleado: float = 0
    pension_empleado: float = 0
    total_descuentos: float = 0
    total: float  # neto pagado al trabajador
    # Prestaciones sociales y aportes del empleador
    prima: float = 0
    cesantias: float = 0
    intereses_cesantias: float = 0
    provision_vacaciones: float = 0
    pension_empleador: float = 0
    arl: float = 0
    otros_aportes: float = 0
    total_prestaciones: float = 0
    costo_empleador: float = 0

    empleado_nombre: Optional[str] = None
    novedades_mes: int = 0


class NominaResumen(BaseModel):
    nomina_total_mes: float  # neto pagado a los trabajadores
    costo_total_empleador: float  # lo que realmente le cuesta a la empresa
    carga_prestacional: float  # % que las prestaciones suman sobre el neto pagado
    proximo_pago: Optional[str] = None
    proximo_pago_concepto: Optional[str] = None  # a quiénes cubre ese pago
    empleados_mensuales: int = 0
    empleados_quincenales: int = 0
    novedades_sin_procesar: int


# ---------------------------------------------------------------------------
# Alertas
# ---------------------------------------------------------------------------

class AlertaVacaciones(BaseModel):
    empleado_id: int
    empleado_nombre: str
    foto_url: Optional[str] = None
    dias_pendientes: int
    ultima_toma: Optional[date] = None
    meses_sin_tomar: Optional[int] = None
    nivel: str


class AlertaSobreasignacion(BaseModel):
    empleado_id: int
    empleado_nombre: str
    foto_url: Optional[str] = None
    porcentaje_total: float
    nivel: str


class AlertaNomina(BaseModel):
    tipo: str
    descripcion: str
    fecha: Optional[date] = None
    nivel: str


class AlertasResumen(BaseModel):
    vacaciones: list[AlertaVacaciones]
    sobreasignacion: list[AlertaSobreasignacion]
    nomina: list[AlertaNomina]
    novedades_sin_procesar: list[NovedadOut]


class CumpleañosOut(BaseModel):
    empleado_id: int
    nombre_completo: str
    foto_url: Optional[str] = None
    nombre_cargo: str
    fecha_nacimiento: date
    proxima_fecha: date
    dias_restantes: int
    etiqueta: Optional[str] = None
