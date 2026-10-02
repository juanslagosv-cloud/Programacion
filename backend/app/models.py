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


class TipoDocumento(str, enum.Enum):
    cedula_ciudadania = "CC"
    cedula_extranjeria = "CE"
    pasaporte = "PA"
    permiso_especial = "PEP"


class EstadoEmpleado(str, enum.Enum):
    activo = "Activo"
    inactivo = "Inactivo"


class PeriodicidadPago(str, enum.Enum):
    mensual = "Mensual"  # se paga el último día del mes
    quincenal = "Quincenal"  # se paga el 15 y el último día del mes


class TipoCuenta(str, enum.Enum):
    ahorros = "Ahorros"
    corriente = "Corriente"


class NivelRiesgoArl(str, enum.Enum):
    """Clase de riesgo de la ARL (Decreto 1607 de 2002), de la que depende la
    tasa que paga el empleador. Ver TASAS_RIESGO_ARL en utils.py."""

    i = "I"
    ii = "II"
    iii = "III"
    iv = "IV"
    v = "V"


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


class EstadoCivil(str, enum.Enum):
    soltero = "Soltero(a)"
    casado = "Casado(a)"
    union_libre = "Unión libre"
    separado = "Separado(a)"
    viudo = "Viudo(a)"


# ---------------------------------------------------------------------------
# Contratos
# ---------------------------------------------------------------------------

class TipoContrato(str, enum.Enum):
    termino_fijo = "Término fijo"
    termino_indefinido = "Término indefinido"
    obra_labor = "Obra o labor"
    prestacion_servicios = "Prestación de servicios"
    aprendizaje = "Aprendizaje"


class ModalidadTrabajo(str, enum.Enum):
    presencial = "Presencial"
    hibrido = "Híbrido"
    remoto = "Remoto"


class EstadoContrato(str, enum.Enum):
    activo = "Activo"
    vencido = "Vencido"
    suspendido = "Suspendido"
    terminado = "Terminado"


class TipoModificacionContrato(str, enum.Enum):
    prorroga = "Prórroga"
    otrosi = "Otrosí"


# ---------------------------------------------------------------------------
# Solicitudes (flujo de aprobación empleado → jefe → Talento Humano)
# ---------------------------------------------------------------------------

class TipoSolicitud(str, enum.Enum):
    vacaciones = "Vacaciones"
    incapacidad = "Incapacidad"
    permiso = "Permiso"
    licencia_remunerada = "Licencia remunerada"
    licencia_no_remunerada = "Licencia no remunerada"
    calamidad = "Calamidad doméstica"
    trabajo_remoto = "Trabajo remoto"
    horas_extras = "Horas extras"
    ausencia = "Ausencia"
    suspension = "Suspensión"
    cambio_salarial = "Cambio salarial"
    cambio_cargo = "Cambio de cargo"
    cambio_proyecto = "Cambio de proyecto"


class EstadoAprobacion(str, enum.Enum):
    pendiente = "Pendiente"
    aprobado = "Aprobado"
    rechazado = "Rechazado"


# ---------------------------------------------------------------------------
# Organigrama (áreas, cargos y vacantes)
# ---------------------------------------------------------------------------

class EstadoVacante(str, enum.Enum):
    abierta = "Abierta"
    en_proceso = "En proceso"
    cerrada = "Cerrada"


# ---------------------------------------------------------------------------
# Expediente del empleado (alertas: certificaciones, documentos,
# evaluaciones, capacitaciones y exámenes médicos)
# ---------------------------------------------------------------------------

class TipoDocumentoExpediente(str, enum.Enum):
    hoja_de_vida = "Hoja de vida"
    cedula = "Cédula"
    certificado_eps = "Certificado EPS"
    certificado_bancario = "Certificado bancario"
    antecedentes_judiciales = "Antecedentes judiciales"
    otro = "Otro"


class TipoExamenMedico(str, enum.Enum):
    ingreso = "Ingreso"
    periodico = "Periódico"
    retiro = "Retiro"


# ---------------------------------------------------------------------------
# Usuarios (autenticación)
# ---------------------------------------------------------------------------

class Empresa(Base):
    """Cada una de las empresas que operan en este mismo sistema.

    El sistema no está pensado para una sola empresa: Ecodes y Envsol
    comparten la misma instalación, y cada empleado y cada proyecto
    pertenece a una de las dos. Los datos de aquí son los que salen
    impresos en el certificado laboral (NIT, firmante, etc.), así que ya
    no viven en variables de entorno sino que se administran desde la
    propia aplicación.
    """

    __tablename__ = "empresas"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(200), unique=True)
    nit: Mapped[str] = mapped_column(String(30))
    ciudad: Mapped[str] = mapped_column(String(120), default="Bogotá D.C.")
    direccion: Mapped[str | None] = mapped_column(String(300), nullable=True)
    telefono: Mapped[str | None] = mapped_column(String(60), nullable=True)
    correo: Mapped[str | None] = mapped_column(String(150), nullable=True)
    # Quien firma el certificado laboral de esta empresa.
    firmante_nombre: Mapped[str] = mapped_column(String(150))
    firmante_cargo: Mapped[str] = mapped_column(String(150), default="Directora de Talento Humano")
    activa: Mapped[bool] = mapped_column(default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    empleados: Mapped[list["Empleado"]] = relationship(back_populates="empresa")
    proyectos: Mapped[list["Proyecto"]] = relationship(back_populates="empresa")


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
    tipo_documento: Mapped[TipoDocumento] = mapped_column(
        Enum(TipoDocumento, name="tipo_documento"), default=TipoDocumento.cedula_ciudadania
    )
    # Único: no puede haber dos personas con el mismo documento. Es nullable
    # porque en bases ya existentes hay registros previos sin el dato.
    numero_documento: Mapped[str | None] = mapped_column(String(30), unique=True, index=True, nullable=True)
    empresa_id: Mapped[int | None] = mapped_column(
        ForeignKey("empresas.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    foto_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    genero: Mapped[Genero] = mapped_column(Enum(Genero, name="genero"))
    fecha_nacimiento: Mapped[date] = mapped_column(Date)
    direccion: Mapped[str | None] = mapped_column(String(300), nullable=True)
    ciudad: Mapped[str | None] = mapped_column(String(120), nullable=True)
    estado_civil: Mapped[EstadoCivil | None] = mapped_column(Enum(EstadoCivil, name="estado_civil"), nullable=True)
    contacto_emergencia_nombre: Mapped[str | None] = mapped_column(String(150), nullable=True)
    contacto_emergencia_telefono: Mapped[str | None] = mapped_column(String(40), nullable=True)
    contacto_emergencia_parentesco: Mapped[str | None] = mapped_column(String(80), nullable=True)
    area: Mapped[str | None] = mapped_column(String(120), nullable=True)
    # Quién es el jefe directo de esta persona, para el organigrama. Se
    # referencia a sí misma la tabla porque el jefe también es un empleado.
    jefe_inmediato_id: Mapped[int | None] = mapped_column(
        ForeignKey("empleados.id", ondelete="SET NULL"), nullable=True
    )
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

    # Datos bancarios y de afiliación al sistema de seguridad social. Son
    # nullable por el mismo motivo que numero_documento: en una base que ya
    # tenía empleados antes de este cambio, esos registros no traen el dato.
    banco: Mapped[str | None] = mapped_column(String(120), nullable=True)
    tipo_cuenta: Mapped[TipoCuenta | None] = mapped_column(Enum(TipoCuenta, name="tipo_cuenta"), nullable=True)
    numero_cuenta: Mapped[str | None] = mapped_column(String(40), nullable=True)
    eps: Mapped[str | None] = mapped_column(String(120), nullable=True)
    afp: Mapped[str | None] = mapped_column(String(120), nullable=True)
    arl: Mapped[str | None] = mapped_column(String(120), nullable=True)
    caja_compensacion: Mapped[str | None] = mapped_column(String(120), nullable=True)
    fondo_cesantias: Mapped[str | None] = mapped_column(String(120), nullable=True)
    # De esto depende la tasa de ARL que paga el empleador (ver utils.py). Si
    # no se registra, el cálculo cae de vuelta a la clasificación por cargo.
    nivel_riesgo_arl: Mapped[NivelRiesgoArl | None] = mapped_column(
        Enum(NivelRiesgoArl, name="nivel_riesgo_arl"), nullable=True
    )

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
    contratos: Mapped[list["Contrato"]] = relationship(
        back_populates="empleado",
        cascade="all, delete-orphan",
        order_by="Contrato.fecha_inicio.desc()",
        foreign_keys="Contrato.empleado_id",
    )
    solicitudes: Mapped[list["Solicitud"]] = relationship(
        back_populates="empleado",
        cascade="all, delete-orphan",
        order_by="Solicitud.fecha_solicitud.desc()",
        foreign_keys="Solicitud.empleado_id",
    )
    certificaciones: Mapped[list["Certificacion"]] = relationship(
        back_populates="empleado", cascade="all, delete-orphan", order_by="Certificacion.fecha_vencimiento"
    )
    documentos: Mapped[list["Documento"]] = relationship(
        back_populates="empleado", cascade="all, delete-orphan", order_by="Documento.fecha_cargue.desc()"
    )
    evaluaciones: Mapped[list["Evaluacion"]] = relationship(
        back_populates="empleado", cascade="all, delete-orphan", order_by="Evaluacion.fecha_programada.desc()"
    )
    capacitaciones: Mapped[list["Capacitacion"]] = relationship(
        back_populates="empleado", cascade="all, delete-orphan", order_by="Capacitacion.fecha_programada.desc()"
    )
    examenes_medicos: Mapped[list["ExamenMedico"]] = relationship(
        back_populates="empleado", cascade="all, delete-orphan", order_by="ExamenMedico.fecha_realizado.desc()"
    )
    empresa: Mapped["Empresa | None"] = relationship(back_populates="empleados")
    jefe_inmediato: Mapped["Empleado | None"] = relationship(
        remote_side=[id], foreign_keys=[jefe_inmediato_id]
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


class Certificacion(Base):
    """Una certificación o licencia del empleado (p. ej. trabajo en alturas,
    manejo de sustancias químicas) que puede vencerse — de ahí la alerta de
    certificación próxima a vencer."""

    __tablename__ = "certificaciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    empleado_id: Mapped[int] = mapped_column(ForeignKey("empleados.id", ondelete="CASCADE"))
    nombre: Mapped[str] = mapped_column(String(200))
    entidad: Mapped[str | None] = mapped_column(String(200), nullable=True)
    fecha_obtencion: Mapped[date | None] = mapped_column(Date, nullable=True)
    fecha_vencimiento: Mapped[date | None] = mapped_column(Date, nullable=True)

    empleado: Mapped["Empleado"] = relationship(back_populates="certificaciones")


class Documento(Base):
    """Un documento del expediente del empleado. La alerta de "documento
    faltante" compara, por cada empleado, los tipos de DOCUMENTOS_REQUERIDOS
    (ver utils.py) contra los tipos que ya tienen un registro aquí."""

    __tablename__ = "documentos"

    id: Mapped[int] = mapped_column(primary_key=True)
    empleado_id: Mapped[int] = mapped_column(ForeignKey("empleados.id", ondelete="CASCADE"))
    tipo: Mapped[TipoDocumentoExpediente] = mapped_column(Enum(TipoDocumentoExpediente, name="tipo_documento_expediente"))
    nombre_archivo: Mapped[str | None] = mapped_column(String(300), nullable=True)
    fecha_cargue: Mapped[date] = mapped_column(Date, server_default=func.current_date())

    empleado: Mapped["Empleado"] = relationship(back_populates="documentos")


class Evaluacion(Base):
    """Evaluación de desempeño de un período. `fecha_realizada` nula significa
    que todavía está pendiente — de ahí sale la alerta correspondiente."""

    __tablename__ = "evaluaciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    empleado_id: Mapped[int] = mapped_column(ForeignKey("empleados.id", ondelete="CASCADE"))
    periodo: Mapped[str] = mapped_column(String(50))
    fecha_programada: Mapped[date] = mapped_column(Date)
    fecha_realizada: Mapped[date | None] = mapped_column(Date, nullable=True)
    resultado: Mapped[str | None] = mapped_column(String(200), nullable=True)
    comentario: Mapped[str | None] = mapped_column(Text, nullable=True)

    empleado: Mapped["Empleado"] = relationship(back_populates="evaluaciones")


class Capacitacion(Base):
    """Una capacitación programada para el empleado. `fecha_realizada` nula
    significa que todavía está pendiente."""

    __tablename__ = "capacitaciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    empleado_id: Mapped[int] = mapped_column(ForeignKey("empleados.id", ondelete="CASCADE"))
    nombre: Mapped[str] = mapped_column(String(200))
    fecha_programada: Mapped[date] = mapped_column(Date)
    fecha_realizada: Mapped[date | None] = mapped_column(Date, nullable=True)
    horas: Mapped[int | None] = mapped_column(nullable=True)

    empleado: Mapped["Empleado"] = relationship(back_populates="capacitaciones")


class ExamenMedico(Base):
    """Examen médico ocupacional (ingreso, periódico o retiro). La alerta de
    examen médico próximo se calcula sobre `fecha_proximo`."""

    __tablename__ = "examenes_medicos"

    id: Mapped[int] = mapped_column(primary_key=True)
    empleado_id: Mapped[int] = mapped_column(ForeignKey("empleados.id", ondelete="CASCADE"))
    tipo: Mapped[TipoExamenMedico] = mapped_column(Enum(TipoExamenMedico, name="tipo_examen_medico"))
    fecha_realizado: Mapped[date] = mapped_column(Date)
    fecha_proximo: Mapped[date | None] = mapped_column(Date, nullable=True)
    concepto: Mapped[str | None] = mapped_column(String(200), nullable=True)

    empleado: Mapped["Empleado"] = relationship(back_populates="examenes_medicos")


# ---------------------------------------------------------------------------
# Historial contractual
# ---------------------------------------------------------------------------

class Contrato(Base):
    """Un período contractual de un empleado. El historial contractual de la
    persona es, sencillamente, la lista de sus contratos (los más antiguos
    normalmente "Terminado" y el último "Activo"). Las prórrogas y otrosí no
    son contratos nuevos: son modificaciones de uno existente, por eso viven
    en ModificacionContrato en lugar de crear otro registro de Contrato."""

    __tablename__ = "contratos"

    id: Mapped[int] = mapped_column(primary_key=True)
    empleado_id: Mapped[int] = mapped_column(ForeignKey("empleados.id", ondelete="CASCADE"), index=True)
    tipo_contrato: Mapped[TipoContrato] = mapped_column(Enum(TipoContrato, name="tipo_contrato"))
    fecha_inicio: Mapped[date] = mapped_column(Date)
    # Nulo para término indefinido, que no tiene fecha de finalización.
    fecha_fin: Mapped[date | None] = mapped_column(Date, nullable=True)
    # En días; no se valida contra los topes legales (2 meses general, o 1/5
    # del plazo si el contrato a término fijo dura menos de un año) porque
    # eso depende de acuerdos particulares que Talento Humano conoce mejor.
    periodo_prueba_dias: Mapped[int | None] = mapped_column(nullable=True)
    # El cargo y el salario quedan fijados en el texto del contrato: pueden
    # no coincidir con el cargo actual del empleado si hubo un ascenso que
    # todavía no se formaliza en un otrosí, o con la nómina ya liquidada.
    cargo_contractual: Mapped[str] = mapped_column(String(150))
    salario: Mapped[float] = mapped_column(Numeric(12, 2))
    proyecto_id: Mapped[int | None] = mapped_column(
        ForeignKey("proyectos.id", ondelete="SET NULL"), nullable=True
    )
    centro_costos: Mapped[str | None] = mapped_column(String(80), nullable=True)
    modalidad: Mapped[ModalidadTrabajo] = mapped_column(
        Enum(ModalidadTrabajo, name="modalidad_trabajo"), default=ModalidadTrabajo.presencial
    )
    estado: Mapped[EstadoContrato] = mapped_column(
        Enum(EstadoContrato, name="estado_contrato"), default=EstadoContrato.activo
    )
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    empleado: Mapped["Empleado"] = relationship(back_populates="contratos", foreign_keys=[empleado_id])
    proyecto: Mapped["Proyecto | None"] = relationship()
    modificaciones: Mapped[list["ModificacionContrato"]] = relationship(
        back_populates="contrato", cascade="all, delete-orphan", order_by="ModificacionContrato.fecha.desc()"
    )


class ModificacionContrato(Base):
    """Una prórroga o un otrosí sobre un contrato existente. Una prórroga
    trae una nueva fecha de finalización, que se aplica automáticamente al
    contrato al crearla (ver routers/contratos.py)."""

    __tablename__ = "modificaciones_contrato"

    id: Mapped[int] = mapped_column(primary_key=True)
    contrato_id: Mapped[int] = mapped_column(ForeignKey("contratos.id", ondelete="CASCADE"), index=True)
    tipo: Mapped[TipoModificacionContrato] = mapped_column(
        Enum(TipoModificacionContrato, name="tipo_modificacion_contrato")
    )
    fecha: Mapped[date] = mapped_column(Date)
    detalle: Mapped[str] = mapped_column(Text)
    # Solo aplica a las prórrogas: la nueva fecha de finalización del contrato.
    nueva_fecha_fin: Mapped[date | None] = mapped_column(Date, nullable=True)

    contrato: Mapped["Contrato"] = relationship(back_populates="modificaciones")


class Solicitud(Base):
    """Una solicitud del empleado (vacaciones, permisos, cambios, etc.) con un
    flujo de dos pasos: primero la revisa el jefe inmediato, y solo si la
    aprueba pasa a Talento Humano para la decisión final. Si el jefe la
    rechaza, ahí termina — Talento Humano nunca llega a verla.

    El sistema no tiene cuentas de usuario por empleado (todo lo registra
    Talento Humano, igual que las demás pantallas), así que esto es el
    registro de las dos decisiones, no un portal de autoservicio.
    """

    __tablename__ = "solicitudes"

    id: Mapped[int] = mapped_column(primary_key=True)
    empleado_id: Mapped[int] = mapped_column(ForeignKey("empleados.id", ondelete="CASCADE"), index=True)
    tipo: Mapped[TipoSolicitud] = mapped_column(Enum(TipoSolicitud, name="tipo_solicitud"))
    fecha_solicitud: Mapped[date] = mapped_column(Date, server_default=func.current_date())
    fecha_inicio: Mapped[date] = mapped_column(Date)
    # Nula para tipos de un solo día (horas extras, ausencia puntual).
    fecha_fin: Mapped[date | None] = mapped_column(Date, nullable=True)
    # Solo aplica al tipo "Horas extras".
    horas: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    motivo: Mapped[str] = mapped_column(Text)
    # Texto libre con el valor propuesto: el nuevo salario o el nuevo cargo,
    # según el tipo. No se valida contra un formato fijo porque el salario
    # puede venir acompañado de una nota ("de $X a $Y").
    valor_propuesto: Mapped[str | None] = mapped_column(String(200), nullable=True)
    # Solo aplica a "Cambio de proyecto".
    proyecto_propuesto_id: Mapped[int | None] = mapped_column(
        ForeignKey("proyectos.id", ondelete="SET NULL"), nullable=True
    )

    estado_jefe: Mapped[EstadoAprobacion] = mapped_column(
        Enum(EstadoAprobacion, name="estado_aprobacion_jefe"), default=EstadoAprobacion.pendiente
    )
    jefe_comentario: Mapped[str | None] = mapped_column(Text, nullable=True)
    jefe_fecha_respuesta: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Talento Humano solo puede decidir después de que el jefe aprueba.
    estado_th: Mapped[EstadoAprobacion] = mapped_column(
        Enum(EstadoAprobacion, name="estado_aprobacion_th"), default=EstadoAprobacion.pendiente
    )
    th_comentario: Mapped[str | None] = mapped_column(Text, nullable=True)
    th_fecha_respuesta: Mapped[date | None] = mapped_column(Date, nullable=True)

    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    empleado: Mapped["Empleado"] = relationship(back_populates="solicitudes")
    proyecto_propuesto: Mapped["Proyecto | None"] = relationship()


# ---------------------------------------------------------------------------
# Organigrama: áreas, cargos y vacantes
# ---------------------------------------------------------------------------

class Area(Base):
    """Un área de la empresa. `area_padre_id` arma la jerarquía de
    dependencias entre áreas (una subárea depende de otra), y `responsable_id`
    es quién tiene la jefatura del área — ambos opcionales porque no toda
    área tiene todavía un responsable o una matriz de la que depender."""

    __tablename__ = "areas"

    id: Mapped[int] = mapped_column(primary_key=True)
    empresa_id: Mapped[int] = mapped_column(ForeignKey("empresas.id", ondelete="CASCADE"), index=True)
    nombre: Mapped[str] = mapped_column(String(150))
    area_padre_id: Mapped[int | None] = mapped_column(ForeignKey("areas.id", ondelete="SET NULL"), nullable=True)
    responsable_id: Mapped[int | None] = mapped_column(
        ForeignKey("empleados.id", ondelete="SET NULL"), nullable=True
    )

    empresa: Mapped["Empresa"] = relationship()
    area_padre: Mapped["Area | None"] = relationship(remote_side=[id])
    responsable: Mapped["Empleado | None"] = relationship()


class Cargo(Base):
    """Catálogo formal de cargos de la empresa, independiente del texto libre
    `Empleado.nombre_cargo`: sirve para definir vacantes y la jerarquía de
    cargos (`cargo_superior_id`) sin forzar a que cada empleado ya existente
    quede amarrado a un cargo del catálogo."""

    __tablename__ = "cargos"

    id: Mapped[int] = mapped_column(primary_key=True)
    empresa_id: Mapped[int] = mapped_column(ForeignKey("empresas.id", ondelete="CASCADE"), index=True)
    area_id: Mapped[int | None] = mapped_column(ForeignKey("areas.id", ondelete="SET NULL"), nullable=True)
    nombre: Mapped[str] = mapped_column(String(150))
    cargo_superior_id: Mapped[int | None] = mapped_column(ForeignKey("cargos.id", ondelete="SET NULL"), nullable=True)

    empresa: Mapped["Empresa"] = relationship()
    area: Mapped["Area | None"] = relationship()
    cargo_superior: Mapped["Cargo | None"] = relationship(remote_side=[id])


class Vacante(Base):
    """Una vacante abierta. No crea un Empleado por sí sola: cuando se llena,
    Talento Humano registra al nuevo empleado por la pantalla de Empleados
    como siempre, y simplemente cierra la vacante aquí."""

    __tablename__ = "vacantes"

    id: Mapped[int] = mapped_column(primary_key=True)
    empresa_id: Mapped[int] = mapped_column(ForeignKey("empresas.id", ondelete="CASCADE"), index=True)
    area_id: Mapped[int | None] = mapped_column(ForeignKey("areas.id", ondelete="SET NULL"), nullable=True)
    cargo_id: Mapped[int | None] = mapped_column(ForeignKey("cargos.id", ondelete="SET NULL"), nullable=True)
    titulo: Mapped[str] = mapped_column(String(150))
    motivo: Mapped[str | None] = mapped_column(Text, nullable=True)
    salario_ofrecido: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    fecha_apertura: Mapped[date] = mapped_column(Date, server_default=func.current_date())
    fecha_cierre_esperada: Mapped[date | None] = mapped_column(Date, nullable=True)
    fecha_cierre_real: Mapped[date | None] = mapped_column(Date, nullable=True)
    estado: Mapped[EstadoVacante] = mapped_column(Enum(EstadoVacante, name="estado_vacante"), default=EstadoVacante.abierta)
    notas: Mapped[str | None] = mapped_column(Text, nullable=True)

    empresa: Mapped["Empresa"] = relationship()
    area: Mapped["Area | None"] = relationship()
    cargo: Mapped["Cargo | None"] = relationship()


# ---------------------------------------------------------------------------
# Proyectos
# ---------------------------------------------------------------------------

class Proyecto(Base):
    __tablename__ = "proyectos"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(200), index=True)
    # A quién contrató Ecodes o Envsol para este proyecto (el cliente), no
    # confundir con empresa_id, que es cuál de las dos opera el proyecto.
    contratante: Mapped[str] = mapped_column(String(200))
    empresa_id: Mapped[int | None] = mapped_column(
        ForeignKey("empresas.id", ondelete="RESTRICT"), nullable=True, index=True
    )
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
    empresa: Mapped["Empresa | None"] = relationship(back_populates="proyectos")


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
