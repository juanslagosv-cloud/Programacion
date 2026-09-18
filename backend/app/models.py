import enum
from datetime import date, datetime

from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# ---------------------------------------------------------------------------
# Enumeraciones
# ---------------------------------------------------------------------------

class RolUsuario(str, enum.Enum):
    talento_humano = "talento_humano"
    administrativo = "administrativo"


class Genero(str, enum.Enum):
    femenino = "Femenino"
    masculino = "Masculino"
    otro = "Otro"


class NivelEducativo(str, enum.Enum):
    bachiller = "Bachiller"
    tecnico = "Técnico"
    tecnologo = "Tecnólogo"
    profesional = "Profesional"
    especializacion = "Especialización"
    maestria = "Maestría"


class TipoCargo(str, enum.Enum):
    profesional = "Profesional"
    tecnico = "Técnico"
    operario = "Operario"
    administrativo = "Administrativo"


class EstadoEmpleado(str, enum.Enum):
    activo = "Activo"
    inactivo = "Inactivo"


class PeriodicidadPago(str, enum.Enum):
    mensual = "Mensual"  # se paga el último día del mes
    quincenal = "Quincenal"  # se paga el 15 y el último día del mes


class EstadoProyecto(str, enum.Enum):
    activo = "Activo"
    cierre = "Cierre"
    continuo = "Continuo"


class TipoNovedad(str, enum.Enum):
    ingreso = "Ingreso"
    salida = "Salida"
    cambio_proyecto = "Cambio de proyecto"
    incapacidad = "Incapacidad"
    otro = "Otro"


# ---------------------------------------------------------------------------
# Usuarios (autenticación)
# ---------------------------------------------------------------------------

class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    nombre: Mapped[str] = mapped_column(String(150))
    password_hash: Mapped[str] = mapped_column(String(255))
    rol: Mapped[RolUsuario] = mapped_column(Enum(RolUsuario, name="rol_usuario"))
    activo: Mapped[bool] = mapped_column(default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# ---------------------------------------------------------------------------
# Empleados y sub-entidades
# ---------------------------------------------------------------------------

class Empleado(Base):
    __tablename__ = "empleados"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre_completo: Mapped[str] = mapped_column(String(200), index=True)
    foto_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    genero: Mapped[Genero] = mapped_column(Enum(Genero, name="genero"))
    fecha_nacimiento: Mapped[date] = mapped_column(Date)
    direccion: Mapped[str | None] = mapped_column(String(300), nullable=True)
    nivel_educativo: Mapped[NivelEducativo] = mapped_column(Enum(NivelEducativo, name="nivel_educativo"))
    nombre_cargo: Mapped[str] = mapped_column(String(150))
    tipo_cargo: Mapped[TipoCargo] = mapped_column(Enum(TipoCargo, name="tipo_cargo"))
    fecha_ingreso: Mapped[date] = mapped_column(Date)
    estado: Mapped[EstadoEmpleado] = mapped_column(
        Enum(EstadoEmpleado, name="estado_empleado"), default=EstadoEmpleado.activo
    )
    periodicidad_pago: Mapped[PeriodicidadPago] = mapped_column(
        Enum(PeriodicidadPago, name="periodicidad_pago"), default=PeriodicidadPago.mensual
    )
    vacaciones_ultima_toma: Mapped[date | None] = mapped_column(Date, nullable=True)
    vacaciones_dias_pendientes: Mapped[int] = mapped_column(default=0)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    estudios: Mapped[list["Estudio"]] = relationship(
        back_populates="empleado", cascade="all, delete-orphan", order_by="Estudio.anio.desc()"
    )
    experiencias: Mapped[list["Experiencia"]] = relationship(
        back_populates="empleado", cascade="all, delete-orphan"
    )
    participaciones: Mapped[list["Participacion"]] = relationship(
        back_populates="empleado", cascade="all, delete-orphan"
    )
    novedades: Mapped[list["Novedad"]] = relationship(
        back_populates="empleado", cascade="all, delete-orphan", order_by="Novedad.fecha.desc()"
    )
    nominas: Mapped[list["Nomina"]] = relationship(
        back_populates="empleado", cascade="all, delete-orphan"
    )


class Estudio(Base):
    __tablename__ = "estudios"

    id: Mapped[int] = mapped_column(primary_key=True)
    empleado_id: Mapped[int] = mapped_column(ForeignKey("empleados.id", ondelete="CASCADE"))
    titulo: Mapped[str] = mapped_column(String(200))
    institucion: Mapped[str] = mapped_column(String(200))
    anio: Mapped[int] = mapped_column()

    empleado: Mapped["Empleado"] = relationship(back_populates="estudios")


class Experiencia(Base):
    __tablename__ = "experiencias"

    id: Mapped[int] = mapped_column(primary_key=True)
    empleado_id: Mapped[int] = mapped_column(ForeignKey("empleados.id", ondelete="CASCADE"))
    empresa: Mapped[str] = mapped_column(String(200))
    cargo: Mapped[str] = mapped_column(String(200))
    periodo: Mapped[str] = mapped_column(String(100))

    empleado: Mapped["Empleado"] = relationship(back_populates="experiencias")


# ---------------------------------------------------------------------------
# Proyectos
# ---------------------------------------------------------------------------

class Proyecto(Base):
    __tablename__ = "proyectos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(200), index=True)
    contratante: Mapped[str] = mapped_column(String(200))
    fecha_inicio: Mapped[date] = mapped_column(Date)
    fecha_fin: Mapped[date | None] = mapped_column(Date, nullable=True)
    presupuesto: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    estado: Mapped[EstadoProyecto] = mapped_column(
        Enum(EstadoProyecto, name="estado_proyecto"), default=EstadoProyecto.activo
    )
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    participaciones: Mapped[list["Participacion"]] = relationship(
        back_populates="proyecto", cascade="all, delete-orphan"
    )
    novedades: Mapped[list["Novedad"]] = relationship(back_populates="proyecto")


# ---------------------------------------------------------------------------
# Participaciones (tabla puente empleado-proyecto)
# ---------------------------------------------------------------------------

class Participacion(Base):
    __tablename__ = "participaciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    empleado_id: Mapped[int] = mapped_column(ForeignKey("empleados.id", ondelete="CASCADE"))
    proyecto_id: Mapped[int] = mapped_column(ForeignKey("proyectos.id", ondelete="CASCADE"))
    porcentaje: Mapped[float] = mapped_column(Numeric(5, 2))
    fecha_asignacion: Mapped[date] = mapped_column(Date, server_default=func.current_date())

    empleado: Mapped["Empleado"] = relationship(back_populates="participaciones")
    proyecto: Mapped["Proyecto"] = relationship(back_populates="participaciones")


# ---------------------------------------------------------------------------
# Novedades
# ---------------------------------------------------------------------------

class Novedad(Base):
    __tablename__ = "novedades"

    id: Mapped[int] = mapped_column(primary_key=True)
    empleado_id: Mapped[int] = mapped_column(ForeignKey("empleados.id", ondelete="CASCADE"))
    proyecto_id: Mapped[int | None] = mapped_column(
        ForeignKey("proyectos.id", ondelete="SET NULL"), nullable=True
    )
    tipo: Mapped[TipoNovedad] = mapped_column(Enum(TipoNovedad, name="tipo_novedad"))
    fecha: Mapped[date] = mapped_column(Date)
    detalle: Mapped[str | None] = mapped_column(Text, nullable=True)
    procesada: Mapped[bool] = mapped_column(default=False)

    empleado: Mapped["Empleado"] = relationship(back_populates="novedades")
    proyecto: Mapped["Proyecto | None"] = relationship(back_populates="novedades")


# ---------------------------------------------------------------------------
# Nómina
# ---------------------------------------------------------------------------

class Nomina(Base):
    __tablename__ = "nominas"

    id: Mapped[int] = mapped_column(primary_key=True)
    empleado_id: Mapped[int] = mapped_column(ForeignKey("empleados.id", ondelete="CASCADE"))
    periodo: Mapped[str] = mapped_column(String(7))  # formato YYYY-MM

    # Período de pago: un registro por pago (mes completo o quincena)
    quincena: Mapped[int | None] = mapped_column(nullable=True)  # None = mes, 1 = 1-15, 2 = 16-fin
    fecha_pago: Mapped[date | None] = mapped_column(Date, nullable=True)
    dias_liquidados: Mapped[int] = mapped_column(default=30)

    # Devengado
    salario_base: Mapped[float] = mapped_column(Numeric(12, 2))  # salario mensual del contrato
    salario_devengado: Mapped[float] = mapped_column(Numeric(12, 2), default=0)  # causado en el período
    auxilio_transporte: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    auxilio_movilidad: Mapped[float] = mapped_column(Numeric(12, 2), default=0)

    # Deducciones al trabajador
    salud_empleado: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    pension_empleado: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    descuentos: Mapped[float] = mapped_column(Numeric(12, 2), default=0)  # otros descuentos
    total_descuentos: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    total: Mapped[float] = mapped_column(Numeric(12, 2), default=0)  # neto pagado

    # Prestaciones sociales y aportes que asume el empleador
    prima: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    cesantias: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    intereses_cesantias: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    provision_vacaciones: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    pension_empleador: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    arl: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    otros_aportes: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    total_prestaciones: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    costo_empleador: Mapped[float] = mapped_column(Numeric(12, 2), default=0)

    pagada: Mapped[bool] = mapped_column(default=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    empleado: Mapped["Empleado"] = relationship(back_populates="nominas")
