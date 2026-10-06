from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models import (
    EstadoAprobacion,
    EstadoCivil,
    EstadoContrato,
    EstadoEmpleado,
    EstadoProyecto,
    EstadoVacante,
    Genero,
    ModalidadTrabajo,
    NivelEducativo,
    NivelRiesgoArl,
    PeriodicidadPago,
    RolUsuario,
    TipoCargo,
    TipoContrato,
    TipoCuenta,
    TipoDocumento,
    TipoDocumentoExpediente,
    TipoExamenMedico,
    TipoModificacionContrato,
    TipoNovedad,
    TipoSolicitud,
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
# Expediente del empleado (certificaciones, documentos, evaluaciones,
# capacitaciones y exámenes médicos — soportan las alertas correspondientes)
# ---------------------------------------------------------------------------

class CertificacionBase(BaseModel):
    nombre: str
    entidad: Optional[str] = None
    fecha_obtencion: Optional[date] = None
    fecha_vencimiento: Optional[date] = None


class CertificacionCreate(CertificacionBase):
    pass


class CertificacionOut(CertificacionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    empleado_id: int


class DocumentoBase(BaseModel):
    tipo: TipoDocumentoExpediente
    nombre_archivo: Optional[str] = Field(default=None, max_length=300)


class DocumentoCreate(DocumentoBase):
    pass


class DocumentoOut(DocumentoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    empleado_id: int
    fecha_cargue: date


class EvaluacionBase(BaseModel):
    periodo: str
    fecha_programada: date
    fecha_realizada: Optional[date] = None
    resultado: Optional[str] = Field(default=None, max_length=200)
    comentario: Optional[str] = None


class EvaluacionCreate(EvaluacionBase):
    pass


class EvaluacionOut(EvaluacionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    empleado_id: int


class CapacitacionBase(BaseModel):
    nombre: str
    fecha_programada: date
    fecha_realizada: Optional[date] = None
    horas: Optional[int] = Field(default=None, ge=0)


class CapacitacionCreate(CapacitacionBase):
    pass


class CapacitacionOut(CapacitacionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    empleado_id: int


class ExamenMedicoBase(BaseModel):
    tipo: TipoExamenMedico
    fecha_realizado: date
    fecha_proximo: Optional[date] = None
    concepto: Optional[str] = Field(default=None, max_length=200)


class ExamenMedicoCreate(ExamenMedicoBase):
    pass


class ExamenMedicoOut(ExamenMedicoBase):
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
# Empresas
# ---------------------------------------------------------------------------

class EmpresaBase(BaseModel):
    nombre: str
    nit: str
    ciudad: str = "Bogotá D.C."
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None
    firmante_nombre: str
    firmante_cargo: str = "Directora de Talento Humano"
    activa: bool = True


class EmpresaCreate(EmpresaBase):
    pass


class EmpresaUpdate(EmpresaBase):
    pass


class EmpresaOut(EmpresaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    total_empleados: int = 0
    total_proyectos: int = 0


# ---------------------------------------------------------------------------
# Empleados
# ---------------------------------------------------------------------------

class EmpleadoBase(BaseModel):
    nombre_completo: str
    tipo_documento: TipoDocumento = TipoDocumento.cedula_ciudadania
    numero_documento: Optional[str] = Field(default=None, max_length=30)
    empresa_id: Optional[int] = None
    foto_url: Optional[str] = None
    genero: Genero
    fecha_nacimiento: date
    direccion: Optional[str] = None
    ciudad: Optional[str] = Field(default=None, max_length=120)
    estado_civil: Optional[EstadoCivil] = None
    contacto_emergencia_nombre: Optional[str] = Field(default=None, max_length=150)
    contacto_emergencia_telefono: Optional[str] = Field(default=None, max_length=40)
    contacto_emergencia_parentesco: Optional[str] = Field(default=None, max_length=80)
    area: Optional[str] = Field(default=None, max_length=120)
    jefe_inmediato_id: Optional[int] = None
    nivel_educativo: NivelEducativo
    nombre_cargo: str
    tipo_cargo: TipoCargo
    fecha_ingreso: date
    estado: EstadoEmpleado = EstadoEmpleado.activo
    periodicidad_pago: PeriodicidadPago = PeriodicidadPago.mensual
    vacaciones_ultima_toma: Optional[date] = None
    vacaciones_dias_pendientes: int = 0
    banco: Optional[str] = Field(default=None, max_length=120)
    tipo_cuenta: Optional[TipoCuenta] = None
    numero_cuenta: Optional[str] = Field(default=None, max_length=40)
    eps: Optional[str] = Field(default=None, max_length=120)
    afp: Optional[str] = Field(default=None, max_length=120)
    arl: Optional[str] = Field(default=None, max_length=120)
    caja_compensacion: Optional[str] = Field(default=None, max_length=120)
    fondo_cesantias: Optional[str] = Field(default=None, max_length=120)
    nivel_riesgo_arl: Optional[NivelRiesgoArl] = None


class EmpleadoCreate(EmpleadoBase):
    estudios: list[EstudioCreate] = []
    experiencias: list[ExperienciaCreate] = []


class EmpleadoUpdate(EmpleadoBase):
    pass


# ---------------------------------------------------------------------------
# Contratos (historial contractual del empleado)
# ---------------------------------------------------------------------------

class ModificacionContratoBase(BaseModel):
    tipo: TipoModificacionContrato
    fecha: date
    detalle: str
    # Solo tiene sentido cuando tipo es "Prórroga": al crearla, se aplica
    # automáticamente como la nueva fecha_fin del contrato (ver routers/contratos.py).
    nueva_fecha_fin: Optional[date] = None


class ModificacionContratoCreate(ModificacionContratoBase):
    pass


class ModificacionContratoOut(ModificacionContratoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    contrato_id: int


class ContratoBase(BaseModel):
    tipo_contrato: TipoContrato
    fecha_inicio: date
    fecha_fin: Optional[date] = None
    periodo_prueba_dias: Optional[int] = Field(default=None, ge=0)
    cargo_contractual: str
    salario: float = Field(ge=0)
    proyecto_id: Optional[int] = None
    centro_costos: Optional[str] = Field(default=None, max_length=80)
    modalidad: ModalidadTrabajo = ModalidadTrabajo.presencial
    estado: EstadoContrato = EstadoContrato.activo


class ContratoCreate(ContratoBase):
    empleado_id: int


class ContratoUpdate(ContratoBase):
    pass


class ContratoOut(ContratoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    empleado_id: int
    proyecto_nombre: Optional[str] = None
    # "12 meses" o "Indefinido" — se calcula a partir de fecha_inicio/fecha_fin
    # en vez de guardarse, para que nunca quede desincronizado de las fechas.
    duracion: Optional[str] = None
    vencido: bool = False
    modificaciones: list[ModificacionContratoOut] = []


class EmpleadoListOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nombre_completo: str
    tipo_documento: TipoDocumento
    numero_documento: Optional[str] = None
    empresa_id: Optional[int] = None
    empresa_nombre: Optional[str] = None
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
    empresa_nombre: Optional[str] = None
    jefe_inmediato_nombre: Optional[str] = None
    antiguedad_meses: int = 0
    estudios: list[EstudioOut] = []
    experiencias: list[ExperienciaOut] = []
    participaciones: list[ParticipacionOut] = []
    contratos: list[ContratoOut] = []
    certificaciones: list[CertificacionOut] = []
    documentos: list[DocumentoOut] = []
    evaluaciones: list[EvaluacionOut] = []
    capacitaciones: list[CapacitacionOut] = []
    examenes_medicos: list[ExamenMedicoOut] = []
    porcentaje_total: float = 0


# ---------------------------------------------------------------------------
# Proyectos
# ---------------------------------------------------------------------------

class ProyectoBase(BaseModel):
    nombre: str
    contratante: str
    empresa_id: Optional[int] = None
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
    empresa_nombre: Optional[str] = None
    tamano_equipo: int = 0
    costo_nomina_mes: float = 0
    porcentaje_rotacion: float = 0


class ProyectoOut(ProyectoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    empresa_nombre: Optional[str] = None
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
# Solicitudes (flujo empleado → jefe → Talento Humano)
# ---------------------------------------------------------------------------

class SolicitudBase(BaseModel):
    tipo: TipoSolicitud
    fecha_inicio: date
    fecha_fin: Optional[date] = None
    horas: Optional[float] = Field(default=None, ge=0)
    motivo: str
    valor_propuesto: Optional[str] = Field(default=None, max_length=200)
    proyecto_propuesto_id: Optional[int] = None


class SolicitudCreate(SolicitudBase):
    empleado_id: int


class SolicitudDecision(BaseModel):
    aprobar: bool
    comentario: Optional[str] = None


class SolicitudOut(SolicitudBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    empleado_id: int
    empleado_nombre: Optional[str] = None
    jefe_inmediato_nombre: Optional[str] = None
    proyecto_propuesto_nombre: Optional[str] = None
    fecha_solicitud: date
    estado_jefe: EstadoAprobacion
    jefe_comentario: Optional[str] = None
    jefe_fecha_respuesta: Optional[date] = None
    estado_th: EstadoAprobacion
    th_comentario: Optional[str] = None
    th_fecha_respuesta: Optional[date] = None
    # Resumen de una sola palabra para pintar en la tabla, calculado a partir
    # de estado_jefe/estado_th (ver utils.estado_general_solicitud).
    estado_general: str = "Pendiente del jefe"
    dias_solicitados: Optional[int] = None


# ---------------------------------------------------------------------------
# Organigrama: áreas, cargos y vacantes
# ---------------------------------------------------------------------------

class AreaBase(BaseModel):
    empresa_id: int
    nombre: str
    area_padre_id: Optional[int] = None
    responsable_id: Optional[int] = None


class AreaCreate(AreaBase):
    pass


class AreaUpdate(AreaBase):
    pass


class AreaOut(AreaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    area_padre_nombre: Optional[str] = None
    responsable_nombre: Optional[str] = None
    total_empleados: int = 0


class CargoBase(BaseModel):
    empresa_id: int
    area_id: Optional[int] = None
    nombre: str
    cargo_superior_id: Optional[int] = None


class CargoCreate(CargoBase):
    pass


class CargoUpdate(CargoBase):
    pass


class CargoOut(CargoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    area_nombre: Optional[str] = None
    cargo_superior_nombre: Optional[str] = None


class VacanteBase(BaseModel):
    empresa_id: int
    area_id: Optional[int] = None
    cargo_id: Optional[int] = None
    titulo: str
    motivo: Optional[str] = None
    salario_ofrecido: Optional[float] = Field(default=None, ge=0)
    fecha_apertura: Optional[date] = None
    fecha_cierre_esperada: Optional[date] = None
    fecha_cierre_real: Optional[date] = None
    estado: EstadoVacante = EstadoVacante.abierta
    notas: Optional[str] = None


class VacanteCreate(VacanteBase):
    pass


class VacanteUpdate(VacanteBase):
    pass


class VacanteOut(VacanteBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    fecha_apertura: date
    area_nombre: Optional[str] = None
    cargo_nombre: Optional[str] = None
    dias_abierta: Optional[int] = None


class NodoJefatura(BaseModel):
    """Un nodo del árbol de jefaturas/equipos: un empleado y, recursivamente,
    las personas que le reportan directamente."""

    empleado_id: int
    nombre: str
    nombre_cargo: str
    foto_url: Optional[str] = None
    reportes: list["NodoJefatura"] = []


class NodoArea(BaseModel):
    """Un nodo del árbol de dependencias entre áreas: un área y,
    recursivamente, las subáreas que dependen de ella."""

    area_id: int
    nombre: str
    responsable_nombre: Optional[str] = None
    total_empleados: int = 0
    subareas: list["NodoArea"] = []


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


class AlertaGenerica(BaseModel):
    """Forma común para las alertas del expediente: contrato por vencer,
    período de prueba, certificación por vencer, documento faltante,
    evaluación pendiente, capacitación pendiente, examen médico próximo e
    incapacidad activa. `tipo` identifica de cuál de esas se trata."""

    tipo: str
    empleado_id: int
    empleado_nombre: str
    foto_url: Optional[str] = None
    descripcion: str
    fecha: Optional[date] = None
    nivel: str


class AlertasResumen(BaseModel):
    vacaciones: list[AlertaVacaciones]
    sobreasignacion: list[AlertaSobreasignacion]
    nomina: list[AlertaNomina]
    novedades_sin_procesar: list[NovedadOut]
    expediente: list[AlertaGenerica] = []
    aniversarios: list[AlertaGenerica] = []


class CumpleañosOut(BaseModel):
    empleado_id: int
    nombre_completo: str
    foto_url: Optional[str] = None
    nombre_cargo: str
    fecha_nacimiento: date
    proxima_fecha: date
    dias_restantes: int
    etiqueta: Optional[str] = None
