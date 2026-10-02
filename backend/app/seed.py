"""Script de siembra de datos de ejemplo para demos del sistema.

Uso:
    cd backend
    python -m app.seed                  # BORRA las tablas y las recrea desde cero
    python -m app.seed --solo-si-vacia  # siembra solo si la base está vacía
"""

from datetime import date, timedelta

from app.config import settings
from app.database import Base, SessionLocal, engine
from app.models import (
    Area,
    Capacitacion,
    Cargo,
    Certificacion,
    Contrato,
    Documento,
    Empleado,
    Empresa,
    EstadoAprobacion,
    EstadoCivil,
    EstadoContrato,
    EstadoEmpleado,
    EstadoProyecto,
    EstadoVacante,
    Estudio,
    Evaluacion,
    ExamenMedico,
    Experiencia,
    Genero,
    ModalidadTrabajo,
    ModificacionContrato,
    Nomina,
    NivelEducativo,
    NivelRiesgoArl,
    Novedad,
    Participacion,
    PeriodicidadPago,
    Proyecto,
    RolUsuario,
    Solicitud,
    TipoCargo,
    TipoContrato,
    TipoCuenta,
    TipoDocumento,
    TipoDocumentoExpediente,
    TipoExamenMedico,
    TipoModificacionContrato,
    TipoNovedad,
    TipoSolicitud,
    Usuario,
    Vacante,
)
from app.security import hash_password
from app.utils import fecha_de_pago, liquidar_nomina, periodos_de_pago

HOY = date.today()


def dias_desde_hoy(dias: int) -> date:
    return HOY + timedelta(days=dias)


def meses_despues(f: date, meses: int) -> date:
    total = f.month - 1 + meses
    anio = f.year + total // 12
    mes = total % 12 + 1
    return date(anio, mes, f.day)


def anios_atras(anios: int, dia: int, mes: int) -> date:
    return date(HOY.year - anios, mes, dia)


def run():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # -------------------------------------------------------------
        # Usuarios
        # -------------------------------------------------------------
        db.add_all(
            [
                Usuario(
                    username="th",
                    nombre="Camila Rojas · Talento Humano",
                    password_hash=hash_password("th12345"),
                    rol=RolUsuario.talento_humano,
                ),
                Usuario(
                    username="admin",
                    nombre="Julián Vargas · Administrativo",
                    password_hash=hash_password("admin12345"),
                    rol=RolUsuario.administrativo,
                ),
            ]
        )

        # -------------------------------------------------------------
        # Empresas
        #
        # El sistema no es solo para Ecodes: Ecodes y Envsol comparten esta
        # misma instalación, y cada empleado y cada proyecto pertenece a una
        # de las dos. Estos son los datos de arranque; se editan luego desde
        # Empleados > Empresas sin tocar el servidor.
        # -------------------------------------------------------------
        empresa_ecodes = Empresa(
            nombre="Ecodes Ingeniería S.A.S.",
            nit=settings.empresa_nit if settings.empresa_nit != "[NIT POR CONFIGURAR]" else "900.123.456-7",
            ciudad=settings.empresa_ciudad,
            direccion=settings.empresa_direccion or None,
            telefono=settings.empresa_telefono or None,
            correo=settings.empresa_correo or None,
            firmante_nombre=(
                settings.firmante_nombre
                if settings.firmante_nombre != "[NOMBRE DE QUIEN FIRMA]"
                else "Camila Rojas Mejía"
            ),
            firmante_cargo=settings.firmante_cargo,
        )
        empresa_envsol = Empresa(
            nombre="Envsol S.A.S.",
            nit="901.987.654-3",
            ciudad="Bogotá D.C.",
            firmante_nombre="Camila Rojas Mejía",
            firmante_cargo="Directora de Talento Humano",
        )
        db.add_all([empresa_ecodes, empresa_envsol])
        db.flush()

        # -------------------------------------------------------------
        # Proyectos
        # -------------------------------------------------------------
        p1 = Proyecto(
            nombre="Restauración Ecológica Cuenca Alta del Chicamocha",
            contratante="Corporación Autónoma Regional de Boyacá",
            fecha_inicio=date(HOY.year - 1, 3, 1),
            fecha_fin=date(HOY.year + 1, 2, 28),
            presupuesto=980_000_000,
            estado=EstadoProyecto.activo,
            empresa=empresa_ecodes,
        )
        p2 = Proyecto(
            nombre="Compensación Forestal Corredor Vial Pacífico",
            contratante="Concesión Vial del Pacífico S.A.S.",
            fecha_inicio=date(HOY.year - 1, 7, 15),
            fecha_fin=date(HOY.year, 12, 15),
            presupuesto=650_000_000,
            estado=EstadoProyecto.activo,
            empresa=empresa_ecodes,
        )
        p3 = Proyecto(
            nombre="Monitoreo de Biodiversidad Selva Central",
            contratante="Ministerio del Ambiente - Perú",
            fecha_inicio=date(HOY.year - 2, 1, 10),
            fecha_fin=None,
            presupuesto=1_250_000_000,
            estado=EstadoProyecto.continuo,
            empresa=empresa_envsol,
        )
        p4 = Proyecto(
            nombre="Gestión Ambiental Corporativa Minera del Norte",
            contratante="Minera del Norte S.A.",
            fecha_inicio=date(HOY.year - 1, 9, 1),
            fecha_fin=date(HOY.year, 10, 30),
            presupuesto=410_000_000,
            estado=EstadoProyecto.cierre,
            empresa=empresa_envsol,
        )
        p5 = Proyecto(
            nombre="Restauración de Bosque Nativo Patagonia",
            contratante="Provincia de Río Negro - Argentina",
            fecha_inicio=date(HOY.year, 2, 1),
            fecha_fin=date(HOY.year + 1, 8, 30),
            presupuesto=560_000_000,
            estado=EstadoProyecto.activo,
            empresa=empresa_ecodes,
        )
        db.add_all([p1, p2, p3, p4, p5])
        db.flush()

        # -------------------------------------------------------------
        # Empleados
        # -------------------------------------------------------------
        empleados_data = [
            dict(
                nombre_completo="María Fernanda López Duarte",
                genero=Genero.femenino,
                fecha_nacimiento=anios_atras(34, dias_desde_hoy(3).day, dias_desde_hoy(3).month),
                direccion="Calle 93 # 15-20, Bogotá",
                nivel_educativo=NivelEducativo.maestria,
                nombre_cargo="Directora de Talento Humano",
                tipo_cargo=TipoCargo.administrativo,
                fecha_ingreso=date(HOY.year - 6, 2, 1),
                estado=EstadoEmpleado.activo,
                vacaciones_ultima_toma=dias_desde_hoy(-200),
                vacaciones_dias_pendientes=6,
            ),
            dict(
                nombre_completo="Andrés Felipe Torres Gómez",
                genero=Genero.masculino,
                fecha_nacimiento=anios_atras(41, dias_desde_hoy(1).day, dias_desde_hoy(1).month),
                direccion="Cra 45 # 22-10, Medellín",
                nivel_educativo=NivelEducativo.profesional,
                nombre_cargo="Gerente Financiero y Administrativo",
                tipo_cargo=TipoCargo.administrativo,
                fecha_ingreso=date(HOY.year - 9, 5, 15),
                estado=EstadoEmpleado.activo,
                vacaciones_ultima_toma=dias_desde_hoy(-380),
                vacaciones_dias_pendientes=22,
            ),
            dict(
                nombre_completo="Laura Camila Restrepo Ibáñez",
                genero=Genero.femenino,
                fecha_nacimiento=anios_atras(29, 12, 4),
                direccion="Av. Circunvalar # 8-45, Cali",
                nivel_educativo=NivelEducativo.profesional,
                nombre_cargo="Coordinadora de Restauración Ecológica",
                tipo_cargo=TipoCargo.profesional,
                fecha_ingreso=date(HOY.year - 3, 4, 3),
                estado=EstadoEmpleado.activo,
                vacaciones_ultima_toma=dias_desde_hoy(-90),
                vacaciones_dias_pendientes=8,
            ),
            dict(
                nombre_completo="Juan Sebastián Vargas Peña",
                genero=Genero.masculino,
                fecha_nacimiento=anios_atras(27, dias_desde_hoy(10).day, dias_desde_hoy(10).month),
                direccion="Calle 5 # 30-12, Bucaramanga",
                nivel_educativo=NivelEducativo.tecnologo,
                nombre_cargo="Técnico de Campo - Restauración",
                tipo_cargo=TipoCargo.tecnico,
                fecha_ingreso=date(HOY.year, 1, 15),
                estado=EstadoEmpleado.activo,
                periodicidad_pago=PeriodicidadPago.quincenal,
                vacaciones_ultima_toma=None,
                vacaciones_dias_pendientes=4,
            ),
            dict(
                nombre_completo="Diana Marcela Sánchez Ortiz",
                genero=Genero.femenino,
                fecha_nacimiento=anios_atras(31, 22, 8),
                direccion="Cra 7 # 60-33, Bogotá",
                nivel_educativo=NivelEducativo.especializacion,
                nombre_cargo="Especialista en Compensación Forestal",
                tipo_cargo=TipoCargo.profesional,
                fecha_ingreso=date(HOY.year - 2, 8, 20),
                estado=EstadoEmpleado.activo,
                vacaciones_ultima_toma=dias_desde_hoy(-60),
                vacaciones_dias_pendientes=3,
            ),
            dict(
                nombre_completo="Carlos Eduardo Ramírez Silva",
                genero=Genero.masculino,
                fecha_nacimiento=anios_atras(38, 30, 6),
                direccion="Jr. Amazonas 245, Lima",
                nivel_educativo=NivelEducativo.profesional,
                nombre_cargo="Biólogo de Monitoreo de Biodiversidad",
                tipo_cargo=TipoCargo.profesional,
                fecha_ingreso=date(HOY.year - 4, 11, 5),
                estado=EstadoEmpleado.activo,
                vacaciones_ultima_toma=dias_desde_hoy(-410),
                vacaciones_dias_pendientes=25,
            ),
            dict(
                nombre_completo="Valentina Herrera Cuesta",
                genero=Genero.femenino,
                fecha_nacimiento=anios_atras(25, dias_desde_hoy(20).day, dias_desde_hoy(20).month),
                direccion="Cll 14 # 9-08, Pasto",
                nivel_educativo=NivelEducativo.tecnico,
                nombre_cargo="Auxiliar de Campo - Monitoreo",
                tipo_cargo=TipoCargo.operario,
                fecha_ingreso=date(HOY.year, 3, 1),
                estado=EstadoEmpleado.activo,
                periodicidad_pago=PeriodicidadPago.quincenal,
                vacaciones_ultima_toma=None,
                vacaciones_dias_pendientes=2,
            ),
            dict(
                nombre_completo="Ricardo Antonio Molina Paz",
                genero=Genero.masculino,
                fecha_nacimiento=anios_atras(45, 3, 1),
                direccion="Av. Pellegrini 1200, San Carlos de Bariloche",
                nivel_educativo=NivelEducativo.maestria,
                nombre_cargo="Coordinador Regional Argentina",
                tipo_cargo=TipoCargo.profesional,
                fecha_ingreso=date(HOY.year - 5, 6, 1),
                estado=EstadoEmpleado.activo,
                vacaciones_ultima_toma=dias_desde_hoy(-120),
                vacaciones_dias_pendientes=10,
            ),
            dict(
                nombre_completo="Paula Andrea Gil Moreno",
                genero=Genero.femenino,
                fecha_nacimiento=anios_atras(33, 5, 5),
                direccion="Calle 100 # 19-61, Bogotá",
                nivel_educativo=NivelEducativo.profesional,
                nombre_cargo="Analista de Nómina y Compensación",
                tipo_cargo=TipoCargo.administrativo,
                fecha_ingreso=date(HOY.year - 2, 2, 10),
                estado=EstadoEmpleado.activo,
                vacaciones_ultima_toma=dias_desde_hoy(-45),
                vacaciones_dias_pendientes=5,
            ),
            dict(
                nombre_completo="Jorge Iván Castañeda Ruiz",
                genero=Genero.masculino,
                fecha_nacimiento=anios_atras(29, 18, 9),
                direccion="Cra 10 # 5-55, Neiva",
                nivel_educativo=NivelEducativo.tecnico,
                nombre_cargo="Operario Forestal",
                tipo_cargo=TipoCargo.operario,
                fecha_ingreso=date(HOY.year - 1, 10, 1),
                estado=EstadoEmpleado.activo,
                periodicidad_pago=PeriodicidadPago.quincenal,
                vacaciones_ultima_toma=dias_desde_hoy(-200),
                vacaciones_dias_pendientes=14,
            ),
            dict(
                nombre_completo="Natalia Andrea Peralta Fonseca",
                genero=Genero.femenino,
                fecha_nacimiento=anios_atras(27, dias_desde_hoy(40).day, dias_desde_hoy(40).month),
                direccion="Calle 63 # 11-30, Bogotá",
                nivel_educativo=NivelEducativo.profesional,
                nombre_cargo="Ingeniera Ambiental Junior",
                tipo_cargo=TipoCargo.profesional,
                fecha_ingreso=date(HOY.year, 5, 20),
                estado=EstadoEmpleado.activo,
                vacaciones_ultima_toma=None,
                vacaciones_dias_pendientes=1,
            ),
            dict(
                nombre_completo="Esteban Alejandro Ríos Bermúdez",
                genero=Genero.masculino,
                fecha_nacimiento=anios_atras(36, 8, 12),
                direccion="Av. La Marina 900, Lima",
                nivel_educativo=NivelEducativo.tecnologo,
                nombre_cargo="Técnico de Monitoreo Ambiental",
                tipo_cargo=TipoCargo.tecnico,
                fecha_ingreso=date(HOY.year - 3, 9, 12),
                estado=EstadoEmpleado.inactivo,
                periodicidad_pago=PeriodicidadPago.quincenal,
                vacaciones_ultima_toma=dias_desde_hoy(-500),
                vacaciones_dias_pendientes=0,
            ),
            dict(
                nombre_completo="Sofía Isabel Cárdenas León",
                genero=Genero.femenino,
                fecha_nacimiento=anios_atras(24, 15, 3),
                direccion="Cll 72 # 4-30, Bogotá",
                nivel_educativo=NivelEducativo.bachiller,
                nombre_cargo="Auxiliar Administrativa",
                tipo_cargo=TipoCargo.administrativo,
                fecha_ingreso=date(HOY.year - 1, 1, 20),
                estado=EstadoEmpleado.activo,
                vacaciones_ultima_toma=dias_desde_hoy(-30),
                vacaciones_dias_pendientes=2,
            ),
            dict(
                nombre_completo="Pedro Pablo Ospina Duque",
                genero=Genero.masculino,
                fecha_nacimiento=anios_atras(50, 25, 10),
                direccion="Cra 3 # 12-40, Pereira",
                nivel_educativo=NivelEducativo.especializacion,
                nombre_cargo="Gerente General",
                tipo_cargo=TipoCargo.administrativo,
                fecha_ingreso=date(HOY.year - 12, 1, 5),
                estado=EstadoEmpleado.activo,
                vacaciones_ultima_toma=dias_desde_hoy(-150),
                vacaciones_dias_pendientes=9,
            ),
        ]

        # Documentos de identidad de ejemplo: números ficticios, pero con la
        # forma de una cédula colombiana y asignados de manera estable para
        # que no cambien entre siembras.
        for indice, data in enumerate(empleados_data):
            data.setdefault("tipo_documento", TipoDocumento.cedula_ciudadania)
            data.setdefault("numero_documento", str(1_012_345_670 + indice * 137))

        # Quién trabaja para cuál de las dos empresas. Los cargos de
        # restauración y forestal quedan en Ecodes; los de monitoreo y
        # gestión ambiental corporativa, en Envsol. Los cargos directivos y
        # administrativos (dirección de talento humano, gerencia financiera)
        # quedan centralizados en Ecodes, como suele pasar en un grupo con
        # una empresa matriz.
        empresa_por_nombre = {
            "María Fernanda López Duarte": empresa_ecodes,
            "Andrés Felipe Torres Gómez": empresa_ecodes,
            "Laura Camila Restrepo Ibáñez": empresa_ecodes,
            "Juan Sebastián Vargas Peña": empresa_ecodes,
            "Diana Marcela Sánchez Ortiz": empresa_ecodes,
            "Ricardo Antonio Molina Paz": empresa_ecodes,
            "Jorge Iván Castañeda Ruiz": empresa_ecodes,
            "Pedro Pablo Ospina Duque": empresa_ecodes,
            "Carlos Eduardo Ramírez Silva": empresa_envsol,
            "Valentina Herrera Cuesta": empresa_envsol,
            "Paula Andrea Gil Moreno": empresa_envsol,
            "Natalia Andrea Peralta Fonseca": empresa_envsol,
            "Esteban Alejandro Ríos Bermúdez": empresa_envsol,
            "Sofía Isabel Cárdenas León": empresa_envsol,
        }
        for data in empleados_data:
            data["empresa"] = empresa_por_nombre[data["nombre_completo"]]

        # Afiliaciones al sistema de seguridad social, datos bancarios y
        # datos personales. El nivel de riesgo de la ARL sigue el mismo
        # criterio que antes separaba oficina de campo (ver
        # utils.es_rol_campo), pero ahora queda registrado explícitamente en
        # cada ficha en vez de inferirse del cargo cada vez que se liquida
        # una nómina. La ciudad sale de la misma dirección de cada quien,
        # arriba, para que no se contradigan.
        afiliaciones_por_nombre = {
            "María Fernanda López Duarte": dict(
                eps="EPS Sura", afp="Porvenir", arl="ARL Sura", caja_compensacion="Compensar",
                fondo_cesantias="Porvenir", nivel_riesgo_arl=NivelRiesgoArl.i,
                banco="Bancolombia", tipo_cuenta=TipoCuenta.ahorros, numero_cuenta="00912345671",
                ciudad="Bogotá D.C.", estado_civil=EstadoCivil.casado, area="Talento Humano",
                contacto_emergencia_nombre="Carlos López", contacto_emergencia_telefono="3001234501",
                contacto_emergencia_parentesco="Esposo",
            ),
            "Andrés Felipe Torres Gómez": dict(
                eps="Sanitas EPS", afp="Protección", arl="Positiva ARL", caja_compensacion="Colsubsidio",
                fondo_cesantias="Protección", nivel_riesgo_arl=NivelRiesgoArl.i,
                banco="Davivienda", tipo_cuenta=TipoCuenta.corriente, numero_cuenta="00912345672",
                ciudad="Medellín", estado_civil=EstadoCivil.casado, area="Financiera y Administrativa",
                contacto_emergencia_nombre="Marcela Gómez", contacto_emergencia_telefono="3001234502",
                contacto_emergencia_parentesco="Esposa",
            ),
            "Laura Camila Restrepo Ibáñez": dict(
                eps="Nueva EPS", afp="Colfondos", arl="Colmena Seguros", caja_compensacion="Comfama",
                fondo_cesantias="Colfondos", nivel_riesgo_arl=NivelRiesgoArl.iii,
                banco="Banco de Bogotá", tipo_cuenta=TipoCuenta.ahorros, numero_cuenta="00912345673",
                ciudad="Cali", estado_civil=EstadoCivil.soltero, area="Operaciones - Restauración",
                contacto_emergencia_nombre="Ana Restrepo", contacto_emergencia_telefono="3001234503",
                contacto_emergencia_parentesco="Madre",
            ),
            "Juan Sebastián Vargas Peña": dict(
                eps="Compensar EPS", afp="Porvenir", arl="ARL Sura", caja_compensacion="Comfenalco Valle",
                fondo_cesantias="Porvenir", nivel_riesgo_arl=NivelRiesgoArl.v,
                banco="Bancolombia", tipo_cuenta=TipoCuenta.ahorros, numero_cuenta="00912345674",
                ciudad="Bucaramanga", estado_civil=EstadoCivil.soltero, area="Operaciones - Restauración",
                contacto_emergencia_nombre="Luz Peña", contacto_emergencia_telefono="3001234504",
                contacto_emergencia_parentesco="Madre",
            ),
            "Diana Marcela Sánchez Ortiz": dict(
                eps="Salud Total EPS", afp="Protección", arl="Seguros Bolívar ARL", caja_compensacion="Compensar",
                fondo_cesantias="Protección", nivel_riesgo_arl=NivelRiesgoArl.iii,
                banco="BBVA Colombia", tipo_cuenta=TipoCuenta.ahorros, numero_cuenta="00912345675",
                ciudad="Bogotá D.C.", estado_civil=EstadoCivil.union_libre, area="Operaciones - Compensación Forestal",
                contacto_emergencia_nombre="Felipe Ortiz", contacto_emergencia_telefono="3001234505",
                contacto_emergencia_parentesco="Pareja",
            ),
            "Carlos Eduardo Ramírez Silva": dict(
                eps="EPS Sura", afp="Colfondos", arl="Colmena Seguros", caja_compensacion="Colsubsidio",
                fondo_cesantias="Colfondos", nivel_riesgo_arl=NivelRiesgoArl.iii,
                banco="Scotiabank Colpatria", tipo_cuenta=TipoCuenta.corriente, numero_cuenta="00912345676",
                ciudad="Lima", estado_civil=EstadoCivil.casado, area="Operaciones - Monitoreo",
                contacto_emergencia_nombre="Rosa Silva", contacto_emergencia_telefono="3001234506",
                contacto_emergencia_parentesco="Esposa",
            ),
            "Valentina Herrera Cuesta": dict(
                eps="Nueva EPS", afp="Porvenir", arl="ARL Sura", caja_compensacion="Comfama",
                fondo_cesantias="Porvenir", nivel_riesgo_arl=NivelRiesgoArl.v,
                banco="Davivienda", tipo_cuenta=TipoCuenta.ahorros, numero_cuenta="00912345677",
                ciudad="Pasto", estado_civil=EstadoCivil.soltero, area="Operaciones - Monitoreo",
                contacto_emergencia_nombre="Marta Cuesta", contacto_emergencia_telefono="3001234507",
                contacto_emergencia_parentesco="Madre",
            ),
            "Ricardo Antonio Molina Paz": dict(
                eps="Sanitas EPS", afp="Protección", arl="Positiva ARL", caja_compensacion="Compensar",
                fondo_cesantias="Protección", nivel_riesgo_arl=NivelRiesgoArl.i,
                banco="Banco de Bogotá", tipo_cuenta=TipoCuenta.corriente, numero_cuenta="00912345678",
                ciudad="San Carlos de Bariloche", estado_civil=EstadoCivil.casado, area="Dirección Regional Argentina",
                contacto_emergencia_nombre="Elena Paz", contacto_emergencia_telefono="3001234508",
                contacto_emergencia_parentesco="Esposa",
            ),
            "Paula Andrea Gil Moreno": dict(
                eps="Famisanar EPS", afp="Colfondos", arl="ARL Sura", caja_compensacion="Colsubsidio",
                fondo_cesantias="Colfondos", nivel_riesgo_arl=NivelRiesgoArl.i,
                banco="Bancolombia", tipo_cuenta=TipoCuenta.ahorros, numero_cuenta="00912345679",
                ciudad="Bogotá D.C.", estado_civil=EstadoCivil.soltero, area="Financiera y Administrativa",
                contacto_emergencia_nombre="Jorge Moreno", contacto_emergencia_telefono="3001234509",
                contacto_emergencia_parentesco="Hermano",
            ),
            "Jorge Iván Castañeda Ruiz": dict(
                eps="Compensar EPS", afp="Porvenir", arl="Colmena Seguros", caja_compensacion="Comfenalco Valle",
                fondo_cesantias="Porvenir", nivel_riesgo_arl=NivelRiesgoArl.v,
                banco="Banco Agrario", tipo_cuenta=TipoCuenta.ahorros, numero_cuenta="00912345680",
                ciudad="Neiva", estado_civil=EstadoCivil.union_libre, area="Operaciones - Restauración",
                contacto_emergencia_nombre="Diana Ruiz", contacto_emergencia_telefono="3001234510",
                contacto_emergencia_parentesco="Pareja",
            ),
            "Natalia Andrea Peralta Fonseca": dict(
                eps="Nueva EPS", afp="Protección", arl="Seguros Bolívar ARL", caja_compensacion="Compensar",
                fondo_cesantias="Protección", nivel_riesgo_arl=NivelRiesgoArl.iii,
                banco="BBVA Colombia", tipo_cuenta=TipoCuenta.ahorros, numero_cuenta="00912345681",
                ciudad="Bogotá D.C.", estado_civil=EstadoCivil.soltero, area="Operaciones Ambientales",
                contacto_emergencia_nombre="Carmen Fonseca", contacto_emergencia_telefono="3001234511",
                contacto_emergencia_parentesco="Madre",
            ),
            "Esteban Alejandro Ríos Bermúdez": dict(
                eps="EPS Sura", afp="Colfondos", arl="ARL Sura", caja_compensacion="Comfama",
                fondo_cesantias="Colfondos", nivel_riesgo_arl=NivelRiesgoArl.iii,
                banco="Scotiabank Colpatria", tipo_cuenta=TipoCuenta.corriente, numero_cuenta="00912345682",
                ciudad="Lima", estado_civil=EstadoCivil.separado, area="Operaciones - Monitoreo",
                contacto_emergencia_nombre="Pedro Bermúdez", contacto_emergencia_telefono="3001234512",
                contacto_emergencia_parentesco="Hermano",
            ),
            "Sofía Isabel Cárdenas León": dict(
                eps="Salud Total EPS", afp="Porvenir", arl="Positiva ARL", caja_compensacion="Colsubsidio",
                fondo_cesantias="Porvenir", nivel_riesgo_arl=NivelRiesgoArl.i,
                banco="Bancolombia", tipo_cuenta=TipoCuenta.ahorros, numero_cuenta="00912345683",
                ciudad="Bogotá D.C.", estado_civil=EstadoCivil.soltero, area="Administrativa",
                contacto_emergencia_nombre="Isabel León", contacto_emergencia_telefono="3001234513",
                contacto_emergencia_parentesco="Madre",
            ),
            "Pedro Pablo Ospina Duque": dict(
                eps="Sanitas EPS", afp="Protección", arl="ARL Sura", caja_compensacion="Compensar",
                fondo_cesantias="Protección", nivel_riesgo_arl=NivelRiesgoArl.i,
                banco="Davivienda", tipo_cuenta=TipoCuenta.corriente, numero_cuenta="00912345684",
                ciudad="Pereira", estado_civil=EstadoCivil.casado, area="Gerencia General",
                contacto_emergencia_nombre="Lucía Duque", contacto_emergencia_telefono="3001234514",
                contacto_emergencia_parentesco="Esposa",
            ),
        }
        for data in empleados_data:
            data.update(afiliaciones_por_nombre[data["nombre_completo"]])

        empleados = [Empleado(**data) for data in empleados_data]
        db.add_all(empleados)
        db.flush()

        (
            e_maria,
            e_andres,
            e_laura,
            e_juan,
            e_diana,
            e_carlos,
            e_valentina,
            e_ricardo,
            e_paula,
            e_jorge,
            e_natalia,
            e_esteban,
            e_sofia,
            e_pedro,
        ) = empleados

        # Organigrama: quién reporta a quién. Pedro (Gerente General) queda
        # en la raíz, sin jefe. Se asigna después del flush porque hace
        # falta que cada empleado ya tenga id.
        e_maria.jefe_inmediato = e_pedro
        e_andres.jefe_inmediato = e_pedro
        e_laura.jefe_inmediato = e_pedro
        e_juan.jefe_inmediato = e_laura
        e_jorge.jefe_inmediato = e_laura
        e_diana.jefe_inmediato = e_pedro
        e_carlos.jefe_inmediato = e_pedro
        e_valentina.jefe_inmediato = e_carlos
        e_ricardo.jefe_inmediato = e_pedro
        e_paula.jefe_inmediato = e_andres
        e_natalia.jefe_inmediato = e_diana
        e_esteban.jefe_inmediato = e_carlos
        e_sofia.jefe_inmediato = e_maria

        # -------------------------------------------------------------
        # Formación académica y experiencia
        # -------------------------------------------------------------
        db.add_all(
            [
                Estudio(empleado=e_maria, titulo="Maestría en Gestión Humana", institucion="Universidad de los Andes", anio=HOY.year - 8),
                Estudio(empleado=e_maria, titulo="Psicología", institucion="Universidad Javeriana", anio=HOY.year - 12),
                Estudio(empleado=e_laura, titulo="Ingeniería Forestal", institucion="Universidad Distrital", anio=HOY.year - 6),
                Estudio(empleado=e_carlos, titulo="Biología", institucion="Universidad Nacional Mayor de San Marcos", anio=HOY.year - 14),
                Estudio(empleado=e_diana, titulo="Especialización en Gestión Ambiental", institucion="Universidad del Rosario", anio=HOY.year - 5),
                Estudio(empleado=e_ricardo, titulo="Maestría en Ciencias Ambientales", institucion="Universidad de Buenos Aires", anio=HOY.year - 10),
                Estudio(empleado=e_juan, titulo="Tecnología en Gestión Ambiental", institucion="SENA", anio=HOY.year - 4),
            ]
        )
        db.add_all(
            [
                Experiencia(empleado=e_maria, empresa="Consultores Ambientales S.A.S.", cargo="Coordinadora de RRHH", periodo="2015 - 2019"),
                Experiencia(empleado=e_laura, empresa="Fundación Natura", cargo="Ingeniera de Proyectos", periodo="2018 - 2021"),
                Experiencia(empleado=e_carlos, empresa="SERNANP", cargo="Biólogo de Campo", periodo="2012 - 2019"),
                Experiencia(empleado=e_ricardo, empresa="Parques Nacionales Argentina", cargo="Coordinador de Conservación", periodo="2014 - 2020"),
            ]
        )

        # -------------------------------------------------------------
        # Participaciones (empleado, proyecto, %)
        # -------------------------------------------------------------
        participaciones = [
            Participacion(empleado=e_laura, proyecto=p1, porcentaje=60),
            Participacion(empleado=e_laura, proyecto=p5, porcentaje=30),
            Participacion(empleado=e_juan, proyecto=p1, porcentaje=100),
            Participacion(empleado=e_diana, proyecto=p2, porcentaje=80),
            Participacion(empleado=e_diana, proyecto=p4, porcentaje=20),
            Participacion(empleado=e_carlos, proyecto=p3, porcentaje=90),
            Participacion(empleado=e_valentina, proyecto=p3, porcentaje=100),
            Participacion(empleado=e_ricardo, proyecto=p5, porcentaje=70),
            Participacion(empleado=e_jorge, proyecto=p2, porcentaje=95),
            Participacion(empleado=e_natalia, proyecto=p1, porcentaje=40),
            Participacion(empleado=e_natalia, proyecto=p4, porcentaje=40),
        ]
        db.add_all(participaciones)

        # -------------------------------------------------------------
        # Novedades
        # -------------------------------------------------------------
        db.add_all(
            [
                Novedad(
                    empleado=e_juan,
                    proyecto=p1,
                    tipo=TipoNovedad.ingreso,
                    fecha=date(HOY.year, 1, 15),
                    detalle="Ingreso como técnico de campo para el proyecto de restauración.",
                    procesada=True,
                ),
                Novedad(
                    empleado=e_natalia,
                    proyecto=p1,
                    tipo=TipoNovedad.ingreso,
                    fecha=date(HOY.year, 5, 20),
                    detalle="Ingreso como ingeniera ambiental junior.",
                    procesada=True,
                ),
                Novedad(
                    empleado=e_valentina,
                    proyecto=p3,
                    tipo=TipoNovedad.cambio_proyecto,
                    fecha=dias_desde_hoy(-25),
                    detalle="Reasignada desde el proyecto de compensación forestal al de monitoreo.",
                    procesada=True,
                ),
                Novedad(
                    empleado=e_esteban,
                    proyecto=p3,
                    tipo=TipoNovedad.salida,
                    fecha=dias_desde_hoy(-15),
                    detalle="Finalización de contrato por cierre de fase de monitoreo.",
                    procesada=True,
                ),
                Novedad(
                    empleado=e_jorge,
                    proyecto=p2,
                    tipo=TipoNovedad.incapacidad,
                    fecha=dias_desde_hoy(-5),
                    detalle="Incapacidad médica de 3 días por accidente laboral leve en campo.",
                    procesada=False,
                ),
                Novedad(
                    empleado=e_sofia,
                    proyecto=None,
                    tipo=TipoNovedad.otro,
                    fecha=dias_desde_hoy(-2),
                    detalle="Cambio de horario administrativo temporal.",
                    procesada=False,
                ),
            ]
        )

        # -------------------------------------------------------------
        # Solicitudes (flujo empleado → jefe → Talento Humano)
        #
        # Una de cada tipo, repartidas en los tres estados posibles, para que
        # la pantalla de Solicitudes no se vea con una sola fila. Pedro no
        # tiene jefe inmediato (es el Gerente General), así que su solicitud
        # muestra cómo se ve ese caso: sin jefe asignado para la primera etapa.
        # -------------------------------------------------------------
        db.add_all(
            [
                Solicitud(
                    empleado=e_juan, tipo=TipoSolicitud.vacaciones,
                    fecha_solicitud=dias_desde_hoy(-3), fecha_inicio=dias_desde_hoy(15), fecha_fin=dias_desde_hoy(19),
                    motivo="Vacaciones familiares de fin de año.",
                ),
                Solicitud(
                    empleado=e_laura, tipo=TipoSolicitud.permiso,
                    fecha_solicitud=dias_desde_hoy(-6), fecha_inicio=dias_desde_hoy(-1), fecha_fin=dias_desde_hoy(-1),
                    motivo="Cita médica personal.",
                    estado_jefe=EstadoAprobacion.aprobado, jefe_comentario="Aprobado, sin inconveniente.",
                    jefe_fecha_respuesta=dias_desde_hoy(-5),
                ),
                Solicitud(
                    empleado=e_jorge, tipo=TipoSolicitud.incapacidad,
                    fecha_solicitud=dias_desde_hoy(-5), fecha_inicio=dias_desde_hoy(-5), fecha_fin=dias_desde_hoy(-3),
                    motivo="Incapacidad médica por accidente laboral leve en campo.",
                    estado_jefe=EstadoAprobacion.aprobado, jefe_comentario="Confirmado con el parte médico.",
                    jefe_fecha_respuesta=dias_desde_hoy(-4),
                    estado_th=EstadoAprobacion.aprobado, th_comentario="Incapacidad radicada ante la EPS.",
                    th_fecha_respuesta=dias_desde_hoy(-3),
                ),
                Solicitud(
                    empleado=e_diana, tipo=TipoSolicitud.horas_extras,
                    fecha_solicitud=dias_desde_hoy(-8), fecha_inicio=dias_desde_hoy(-7), horas=4,
                    motivo="Jornada adicional para la entrega del informe de compensación forestal.",
                    estado_jefe=EstadoAprobacion.aprobado, jefe_comentario="Aprobado, entrega urgente.",
                    jefe_fecha_respuesta=dias_desde_hoy(-7),
                    estado_th=EstadoAprobacion.aprobado, th_comentario="Se liquidan en la próxima nómina.",
                    th_fecha_respuesta=dias_desde_hoy(-6),
                ),
                Solicitud(
                    empleado=e_carlos, tipo=TipoSolicitud.trabajo_remoto,
                    fecha_solicitud=dias_desde_hoy(-10), fecha_inicio=dias_desde_hoy(5), fecha_fin=dias_desde_hoy(9),
                    motivo="Trabajo remoto mientras se tramitan los permisos de campo en Lima.",
                    estado_jefe=EstadoAprobacion.rechazado,
                    jefe_comentario="Se requiere presencia en campo para el monitoreo de esta semana.",
                    jefe_fecha_respuesta=dias_desde_hoy(-8),
                ),
                Solicitud(
                    empleado=e_valentina, tipo=TipoSolicitud.licencia_no_remunerada,
                    fecha_solicitud=dias_desde_hoy(-4), fecha_inicio=dias_desde_hoy(20), fecha_fin=dias_desde_hoy(34),
                    motivo="Viaje familiar por asuntos personales.",
                ),
                Solicitud(
                    empleado=e_natalia, tipo=TipoSolicitud.cambio_proyecto,
                    fecha_solicitud=dias_desde_hoy(-12), fecha_inicio=dias_desde_hoy(7), proyecto_propuesto=p3,
                    motivo="Interés en sumarse al equipo de monitoreo de biodiversidad.",
                    estado_jefe=EstadoAprobacion.aprobado, jefe_comentario="De acuerdo, le conviene a su desarrollo.",
                    jefe_fecha_respuesta=dias_desde_hoy(-10),
                ),
                Solicitud(
                    empleado=e_paula, tipo=TipoSolicitud.cambio_salarial,
                    fecha_solicitud=dias_desde_hoy(-20), fecha_inicio=dias_desde_hoy(-20),
                    valor_propuesto="De $4.200.000 a $4.800.000 mensuales",
                    motivo="Ajuste salarial por asunción de nuevas responsabilidades en nómina.",
                    estado_jefe=EstadoAprobacion.aprobado, jefe_comentario="Justificado por la carga adicional.",
                    jefe_fecha_respuesta=dias_desde_hoy(-18),
                    estado_th=EstadoAprobacion.rechazado,
                    th_comentario="Se revisará en el próximo ciclo de evaluación de desempeño.",
                    th_fecha_respuesta=dias_desde_hoy(-15),
                ),
                Solicitud(
                    empleado=e_sofia, tipo=TipoSolicitud.ausencia,
                    fecha_solicitud=dias_desde_hoy(-2), fecha_inicio=dias_desde_hoy(-1), fecha_fin=dias_desde_hoy(-1),
                    motivo="Ausencia por trámite personal urgente.",
                ),
                Solicitud(
                    empleado=e_ricardo, tipo=TipoSolicitud.suspension,
                    fecha_solicitud=dias_desde_hoy(-40), fecha_inicio=dias_desde_hoy(-35), fecha_fin=dias_desde_hoy(-33),
                    motivo="Suspensión disciplinaria por incumplimiento del protocolo de reporte.",
                    estado_jefe=EstadoAprobacion.aprobado, jefe_comentario="Procede según el reglamento interno.",
                    jefe_fecha_respuesta=dias_desde_hoy(-38),
                    estado_th=EstadoAprobacion.aprobado, th_comentario="Registrada en el expediente.",
                    th_fecha_respuesta=dias_desde_hoy(-36),
                ),
                Solicitud(
                    empleado=e_pedro, tipo=TipoSolicitud.cambio_cargo,
                    fecha_solicitud=dias_desde_hoy(-15), fecha_inicio=dias_desde_hoy(-15),
                    valor_propuesto="De Gerente General a Director Ejecutivo",
                    motivo="Formalización del cargo ante la junta directiva.",
                    # Pedro no tiene jefe inmediato: la solicitud queda a la espera
                    # de que alguien decida esa primera etapa (ver sección 4 del README).
                ),
                Solicitud(
                    empleado=e_esteban, tipo=TipoSolicitud.calamidad,
                    fecha_solicitud=dias_desde_hoy(-60), fecha_inicio=dias_desde_hoy(-58), fecha_fin=dias_desde_hoy(-56),
                    motivo="Calamidad doméstica por emergencia familiar.",
                    estado_jefe=EstadoAprobacion.aprobado, jefe_comentario="Aprobado, que atienda la emergencia.",
                    jefe_fecha_respuesta=dias_desde_hoy(-59),
                    estado_th=EstadoAprobacion.aprobado, th_comentario="Registrada la calamidad.",
                    th_fecha_respuesta=dias_desde_hoy(-57),
                ),
                Solicitud(
                    empleado=e_maria, tipo=TipoSolicitud.licencia_remunerada,
                    fecha_solicitud=dias_desde_hoy(-9), fecha_inicio=dias_desde_hoy(3), fecha_fin=dias_desde_hoy(5),
                    motivo="Licencia remunerada por capacitación externa en gestión humana.",
                    estado_jefe=EstadoAprobacion.aprobado, jefe_comentario="Aprobado, buena oportunidad de formación.",
                    jefe_fecha_respuesta=dias_desde_hoy(-7),
                ),
            ]
        )

        # -------------------------------------------------------------
        # Nómina (últimos 2 períodos)
        # -------------------------------------------------------------
        periodo_actual = HOY.strftime("%Y-%m")
        mes_anterior = (HOY.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")

        # salario base y auxilio de movilidad que la empresa asigna a cada persona
        # (el de movilidad es discrecional: solo lo reciben los roles de campo)
        salarios = {
            e_maria: (9_500_000, 0),
            e_andres: (10_200_000, 0),
            e_laura: (6_800_000, 100_000),
            e_juan: (2_600_000, 100_000),
            e_diana: (7_200_000, 100_000),
            e_carlos: (7_800_000, 100_000),
            e_valentina: (1_900_000, 100_000),
            e_ricardo: (8_500_000, 0),
            e_paula: (4_200_000, 0),
            e_jorge: (2_100_000, 100_000),
            e_natalia: (3_800_000, 0),
            e_sofia: (1_800_000, 0),
            e_pedro: (15_000_000, 0),
        }

        # -------------------------------------------------------------
        # Historial contractual
        #
        # La mayoría tiene un único contrato vigente. Laura, Juan, Diana y
        # Jorge traen algo de historia (un contrato anterior ya terminado,
        # una prórroga o un otrosí) para que el panel de "Historial
        # contractual" se vea con información real y no con una sola fila.
        # -------------------------------------------------------------
        c_maria = Contrato(
            empleado=e_maria, tipo_contrato=TipoContrato.termino_indefinido,
            fecha_inicio=e_maria.fecha_ingreso, cargo_contractual=e_maria.nombre_cargo,
            salario=9_500_000, centro_costos="TH-ADMIN", modalidad=ModalidadTrabajo.hibrido,
            estado=EstadoContrato.activo,
        )
        c_andres = Contrato(
            empleado=e_andres, tipo_contrato=TipoContrato.termino_indefinido,
            fecha_inicio=e_andres.fecha_ingreso, cargo_contractual=e_andres.nombre_cargo,
            salario=10_200_000, centro_costos="FIN-ADMIN", modalidad=ModalidadTrabajo.hibrido,
            estado=EstadoContrato.activo,
        )

        # Laura empezó a término fijo como profesional y, al año, la
        # ascendieron a coordinadora con contrato indefinido.
        laura_fin_fijo = date(e_laura.fecha_ingreso.year + 1, e_laura.fecha_ingreso.month, e_laura.fecha_ingreso.day)
        c_laura_1 = Contrato(
            empleado=e_laura, tipo_contrato=TipoContrato.termino_fijo,
            fecha_inicio=e_laura.fecha_ingreso, fecha_fin=laura_fin_fijo, periodo_prueba_dias=60,
            cargo_contractual="Profesional de Restauración Ecológica", salario=4_800_000,
            proyecto=p1, centro_costos="OPS-RESTAURACION", modalidad=ModalidadTrabajo.presencial,
            estado=EstadoContrato.terminado,
        )
        c_laura_2 = Contrato(
            empleado=e_laura, tipo_contrato=TipoContrato.termino_indefinido,
            fecha_inicio=date(laura_fin_fijo.year, laura_fin_fijo.month, laura_fin_fijo.day),
            cargo_contractual=e_laura.nombre_cargo, salario=6_800_000,
            proyecto=p1, centro_costos="OPS-RESTAURACION", modalidad=ModalidadTrabajo.presencial,
            estado=EstadoContrato.activo,
        )
        c_laura_2.modificaciones.append(
            ModificacionContrato(
                tipo=TipoModificacionContrato.otrosi,
                fecha=dias_desde_hoy(-360),
                detalle="Se formaliza el ascenso a Coordinadora de Restauración Ecológica y el ajuste salarial correspondiente.",
            )
        )

        c_diana = Contrato(
            empleado=e_diana, tipo_contrato=TipoContrato.termino_indefinido,
            fecha_inicio=e_diana.fecha_ingreso, cargo_contractual=e_diana.nombre_cargo,
            salario=7_200_000, proyecto=p2, centro_costos="OPS-COMPENSACION",
            modalidad=ModalidadTrabajo.hibrido, estado=EstadoContrato.activo,
        )
        c_diana.modificaciones.append(
            ModificacionContrato(
                tipo=TipoModificacionContrato.otrosi,
                fecha=dias_desde_hoy(-200),
                detalle="Ajuste salarial anual por desempeño: de $6.800.000 a $7.200.000 mensuales.",
            )
        )

        c_carlos = Contrato(
            empleado=e_carlos, tipo_contrato=TipoContrato.termino_indefinido,
            fecha_inicio=e_carlos.fecha_ingreso, cargo_contractual=e_carlos.nombre_cargo,
            salario=7_800_000, proyecto=p3, centro_costos="OPS-MONITOREO",
            modalidad=ModalidadTrabajo.presencial, estado=EstadoContrato.activo,
        )

        valentina_fin_fijo = date(e_valentina.fecha_ingreso.year + 1, e_valentina.fecha_ingreso.month, e_valentina.fecha_ingreso.day)
        c_valentina = Contrato(
            empleado=e_valentina, tipo_contrato=TipoContrato.termino_fijo,
            fecha_inicio=e_valentina.fecha_ingreso, fecha_fin=valentina_fin_fijo, periodo_prueba_dias=60,
            cargo_contractual=e_valentina.nombre_cargo, salario=1_900_000,
            proyecto=p3, centro_costos="OPS-MONITOREO", modalidad=ModalidadTrabajo.presencial,
            estado=EstadoContrato.activo,
        )

        c_ricardo = Contrato(
            empleado=e_ricardo, tipo_contrato=TipoContrato.termino_indefinido,
            fecha_inicio=e_ricardo.fecha_ingreso, cargo_contractual=e_ricardo.nombre_cargo,
            salario=8_500_000, proyecto=p5, centro_costos="DIR-REGIONAL-AR",
            modalidad=ModalidadTrabajo.hibrido, estado=EstadoContrato.activo,
        )
        c_paula = Contrato(
            empleado=e_paula, tipo_contrato=TipoContrato.termino_indefinido,
            fecha_inicio=e_paula.fecha_ingreso, cargo_contractual=e_paula.nombre_cargo,
            salario=4_200_000, centro_costos="FIN-ADMIN", modalidad=ModalidadTrabajo.hibrido,
            estado=EstadoContrato.activo,
        )

        # Jorge empezó por obra o labor para una fase puntual y, cuando esa
        # fase terminó, pasó a un contrato a término fijo.
        jorge_fin_obra = meses_despues(e_jorge.fecha_ingreso, 6)
        c_jorge_1 = Contrato(
            empleado=e_jorge, tipo_contrato=TipoContrato.obra_labor,
            fecha_inicio=e_jorge.fecha_ingreso, fecha_fin=jorge_fin_obra,
            cargo_contractual="Operario de Campo - Restauración", salario=1_950_000,
            proyecto=p2, centro_costos="OPS-RESTAURACION", modalidad=ModalidadTrabajo.presencial,
            estado=EstadoContrato.terminado,
        )
        jorge_fin_fijo = date(jorge_fin_obra.year + 1, jorge_fin_obra.month, jorge_fin_obra.day)
        c_jorge_2 = Contrato(
            empleado=e_jorge, tipo_contrato=TipoContrato.termino_fijo,
            fecha_inicio=jorge_fin_obra, fecha_fin=jorge_fin_fijo, periodo_prueba_dias=60,
            cargo_contractual=e_jorge.nombre_cargo, salario=2_100_000,
            proyecto=p2, centro_costos="OPS-RESTAURACION", modalidad=ModalidadTrabajo.presencial,
            estado=EstadoContrato.activo,
        )

        natalia_fin_fijo = date(e_natalia.fecha_ingreso.year + 1, e_natalia.fecha_ingreso.month, e_natalia.fecha_ingreso.day)
        c_natalia = Contrato(
            empleado=e_natalia, tipo_contrato=TipoContrato.termino_fijo,
            fecha_inicio=e_natalia.fecha_ingreso, fecha_fin=natalia_fin_fijo, periodo_prueba_dias=60,
            cargo_contractual=e_natalia.nombre_cargo, salario=3_800_000,
            proyecto=p4, centro_costos="OPS-AMBIENTAL", modalidad=ModalidadTrabajo.hibrido,
            estado=EstadoContrato.activo,
        )

        # Juan sigue a término fijo, pero ya se le prorrogó una vez.
        juan_fin_fijo = date(e_juan.fecha_ingreso.year + 1, e_juan.fecha_ingreso.month, e_juan.fecha_ingreso.day)
        c_juan = Contrato(
            empleado=e_juan, tipo_contrato=TipoContrato.termino_fijo,
            fecha_inicio=e_juan.fecha_ingreso, fecha_fin=juan_fin_fijo, periodo_prueba_dias=60,
            cargo_contractual=e_juan.nombre_cargo, salario=2_600_000,
            proyecto=p1, centro_costos="OPS-RESTAURACION", modalidad=ModalidadTrabajo.presencial,
            estado=EstadoContrato.activo,
        )
        juan_prorroga_fin = meses_despues(juan_fin_fijo, 6)
        c_juan.fecha_fin = juan_prorroga_fin
        c_juan.modificaciones.append(
            ModificacionContrato(
                tipo=TipoModificacionContrato.prorroga,
                fecha=dias_desde_hoy(-10),
                detalle="Se prorroga el contrato por 6 meses adicionales para continuar la fase de restauración.",
                nueva_fecha_fin=juan_prorroga_fin,
            )
        )

        c_esteban = Contrato(
            empleado=e_esteban, tipo_contrato=TipoContrato.obra_labor,
            fecha_inicio=e_esteban.fecha_ingreso, fecha_fin=dias_desde_hoy(-15), periodo_prueba_dias=60,
            cargo_contractual=e_esteban.nombre_cargo, salario=2_400_000,
            proyecto=p3, centro_costos="OPS-MONITOREO", modalidad=ModalidadTrabajo.presencial,
            estado=EstadoContrato.terminado,
        )
        c_sofia = Contrato(
            empleado=e_sofia, tipo_contrato=TipoContrato.termino_indefinido,
            fecha_inicio=e_sofia.fecha_ingreso, cargo_contractual=e_sofia.nombre_cargo,
            salario=1_800_000, centro_costos="ADMIN-GENERAL", modalidad=ModalidadTrabajo.presencial,
            estado=EstadoContrato.activo,
        )
        c_pedro = Contrato(
            empleado=e_pedro, tipo_contrato=TipoContrato.termino_indefinido,
            fecha_inicio=e_pedro.fecha_ingreso, cargo_contractual=e_pedro.nombre_cargo,
            salario=15_000_000, centro_costos="GERENCIA", modalidad=ModalidadTrabajo.presencial,
            estado=EstadoContrato.activo,
        )

        db.add_all([
            c_maria, c_andres, c_laura_1, c_laura_2, c_diana, c_carlos, c_valentina,
            c_ricardo, c_paula, c_jorge_1, c_jorge_2, c_natalia, c_juan, c_esteban, c_sofia, c_pedro,
        ])

        # -------------------------------------------------------------
        # Organigrama: áreas, cargos y vacantes
        #
        # Es un catálogo aparte del texto libre que cada empleado ya trae en
        # `area` y `nombre_cargo` (ver sección 4 del README): no se migra a
        # nadie, pero el conteo de personas por área se hace por coincidencia
        # de nombre para que ya se vea quién trabaja en cada una.
        # -------------------------------------------------------------
        a_ecodes_gerencia = Area(empresa=empresa_ecodes, nombre="Gerencia General", responsable=e_pedro)
        a_ecodes_operaciones = Area(empresa=empresa_ecodes, nombre="Operaciones", area_padre=a_ecodes_gerencia)
        a_ecodes_restauracion = Area(
            empresa=empresa_ecodes, nombre="Operaciones - Restauración",
            area_padre=a_ecodes_operaciones, responsable=e_laura,
        )
        a_ecodes_compensacion = Area(
            empresa=empresa_ecodes, nombre="Operaciones - Compensación Forestal",
            area_padre=a_ecodes_operaciones, responsable=e_diana,
        )
        a_ecodes_financiera = Area(
            empresa=empresa_ecodes, nombre="Financiera y Administrativa",
            area_padre=a_ecodes_gerencia, responsable=e_andres,
        )
        a_ecodes_th = Area(
            empresa=empresa_ecodes, nombre="Talento Humano",
            area_padre=a_ecodes_gerencia, responsable=e_maria,
        )
        a_ecodes_argentina = Area(
            empresa=empresa_ecodes, nombre="Dirección Regional Argentina",
            area_padre=a_ecodes_gerencia, responsable=e_ricardo,
        )

        a_envsol_direccion = Area(empresa=empresa_envsol, nombre="Dirección Envsol")
        a_envsol_monitoreo = Area(
            empresa=empresa_envsol, nombre="Operaciones - Monitoreo",
            area_padre=a_envsol_direccion, responsable=e_carlos,
        )
        a_envsol_ambiental = Area(
            empresa=empresa_envsol, nombre="Operaciones Ambientales",
            area_padre=a_envsol_direccion, responsable=e_natalia,
        )
        a_envsol_financiera = Area(
            empresa=empresa_envsol, nombre="Financiera y Administrativa",
            area_padre=a_envsol_direccion, responsable=e_paula,
        )
        a_envsol_administrativa = Area(
            empresa=empresa_envsol, nombre="Administrativa",
            area_padre=a_envsol_direccion, responsable=e_sofia,
        )
        db.add_all([
            a_ecodes_gerencia, a_ecodes_operaciones, a_ecodes_restauracion, a_ecodes_compensacion,
            a_ecodes_financiera, a_ecodes_th, a_ecodes_argentina,
            a_envsol_direccion, a_envsol_monitoreo, a_envsol_ambiental, a_envsol_financiera,
            a_envsol_administrativa,
        ])
        db.flush()

        cg_gerente_general = Cargo(empresa=empresa_ecodes, area=a_ecodes_gerencia, nombre="Gerente General")
        cg_directora_th = Cargo(
            empresa=empresa_ecodes, area=a_ecodes_th, nombre="Directora de Talento Humano",
            cargo_superior=cg_gerente_general,
        )
        cg_coordinador_financiero = Cargo(
            empresa=empresa_ecodes, area=a_ecodes_financiera, nombre="Coordinador Financiero y Administrativo",
            cargo_superior=cg_gerente_general,
        )
        cg_coordinadora_restauracion = Cargo(
            empresa=empresa_ecodes, area=a_ecodes_restauracion, nombre="Coordinadora de Restauración Ecológica",
            cargo_superior=cg_gerente_general,
        )
        cg_ingeniero_junior = Cargo(
            empresa=empresa_ecodes, area=a_ecodes_restauracion, nombre="Ingeniero Ambiental Junior",
            cargo_superior=cg_coordinadora_restauracion,
        )
        cg_director_envsol = Cargo(empresa=empresa_envsol, area=a_envsol_direccion, nombre="Director Envsol")
        cg_coordinador_monitoreo = Cargo(
            empresa=empresa_envsol, area=a_envsol_monitoreo, nombre="Coordinador de Monitoreo de Biodiversidad",
            cargo_superior=cg_director_envsol,
        )
        cg_biologa_campo = Cargo(
            empresa=empresa_envsol, area=a_envsol_monitoreo, nombre="Bióloga de Campo",
            cargo_superior=cg_coordinador_monitoreo,
        )
        db.add_all([
            cg_gerente_general, cg_directora_th, cg_coordinador_financiero, cg_coordinadora_restauracion,
            cg_ingeniero_junior, cg_director_envsol, cg_coordinador_monitoreo, cg_biologa_campo,
        ])
        db.flush()

        db.add_all([
            Vacante(
                empresa=empresa_ecodes, area=a_ecodes_restauracion, cargo=cg_ingeniero_junior,
                titulo="Ingeniero Ambiental Junior - Restauración",
                motivo="Crecimiento del proyecto de restauración en Boyacá.",
                salario_ofrecido=3_200_000,
                fecha_apertura=dias_desde_hoy(-20), fecha_cierre_esperada=dias_desde_hoy(15),
                estado=EstadoVacante.en_proceso, notas="Dos candidatos en entrevista final.",
            ),
            Vacante(
                empresa=empresa_envsol, area=a_envsol_monitoreo,
                titulo="Técnico de Campo - Monitoreo de Biodiversidad",
                motivo="Reemplazo por renuncia.",
                salario_ofrecido=2_800_000, fecha_apertura=dias_desde_hoy(-5),
                estado=EstadoVacante.abierta,
            ),
            Vacante(
                empresa=empresa_ecodes, area=a_ecodes_financiera,
                titulo="Analista Financiero",
                motivo="Nueva posición para apoyar el crecimiento de proyectos.",
                fecha_apertura=dias_desde_hoy(-60), fecha_cierre_esperada=dias_desde_hoy(-10),
                fecha_cierre_real=dias_desde_hoy(-8), estado=EstadoVacante.cerrada,
                notas="Vacante cerrada; se contrató internamente.",
            ),
        ])

        # -------------------------------------------------------------
        # Expediente del empleado: certificaciones, documentos,
        # evaluaciones, capacitaciones y exámenes médicos — soportan las
        # alertas correspondientes. Se ajustan un par de fechas de
        # contratos ya creados arriba para que las alertas de contrato por
        # vencer y período de prueba también tengan un caso real.
        # -------------------------------------------------------------
        c_valentina.fecha_fin = dias_desde_hoy(20)
        c_natalia.fecha_inicio = dias_desde_hoy(-55)

        db.add_all([
            Certificacion(
                empleado=e_laura, nombre="Trabajo seguro en alturas", entidad="SENA",
                fecha_obtencion=dias_desde_hoy(-300), fecha_vencimiento=dias_desde_hoy(20),
            ),
            Certificacion(
                empleado=e_juan, nombre="Manejo de sustancias químicas", entidad="ARL Sura",
                fecha_obtencion=dias_desde_hoy(-400), fecha_vencimiento=dias_desde_hoy(400),
            ),
            Certificacion(
                empleado=e_carlos, nombre="Primeros auxilios", entidad="Cruz Roja Colombiana",
                fecha_obtencion=dias_desde_hoy(-200), fecha_vencimiento=dias_desde_hoy(5),
            ),
        ])

        db.add_all([
            Documento(empleado=e_maria, tipo=TipoDocumentoExpediente.hoja_de_vida, nombre_archivo="hoja_vida_maria.pdf"),
            Documento(empleado=e_maria, tipo=TipoDocumentoExpediente.cedula, nombre_archivo="cedula_maria.pdf"),
            Documento(empleado=e_maria, tipo=TipoDocumentoExpediente.certificado_eps, nombre_archivo="eps_maria.pdf"),
            Documento(empleado=e_maria, tipo=TipoDocumentoExpediente.certificado_bancario, nombre_archivo="banco_maria.pdf"),
            Documento(empleado=e_maria, tipo=TipoDocumentoExpediente.antecedentes_judiciales, nombre_archivo="antecedentes_maria.pdf"),
            Documento(empleado=e_andres, tipo=TipoDocumentoExpediente.hoja_de_vida, nombre_archivo="hoja_vida_andres.pdf"),
            Documento(empleado=e_andres, tipo=TipoDocumentoExpediente.cedula, nombre_archivo="cedula_andres.pdf"),
            Documento(empleado=e_andres, tipo=TipoDocumentoExpediente.certificado_eps, nombre_archivo="eps_andres.pdf"),
            Documento(empleado=e_pedro, tipo=TipoDocumentoExpediente.hoja_de_vida, nombre_archivo="hoja_vida_pedro.pdf"),
            Documento(empleado=e_pedro, tipo=TipoDocumentoExpediente.cedula, nombre_archivo="cedula_pedro.pdf"),
            Documento(empleado=e_pedro, tipo=TipoDocumentoExpediente.certificado_eps, nombre_archivo="eps_pedro.pdf"),
            Documento(empleado=e_pedro, tipo=TipoDocumentoExpediente.certificado_bancario, nombre_archivo="banco_pedro.pdf"),
            Documento(empleado=e_pedro, tipo=TipoDocumentoExpediente.antecedentes_judiciales, nombre_archivo="antecedentes_pedro.pdf"),
            Documento(empleado=e_juan, tipo=TipoDocumentoExpediente.hoja_de_vida, nombre_archivo="hoja_vida_juan.pdf"),
            Documento(empleado=e_juan, tipo=TipoDocumentoExpediente.cedula, nombre_archivo="cedula_juan.pdf"),
        ])

        db.add_all([
            Evaluacion(
                empleado=e_juan, periodo=f"{HOY.year}-S1",
                fecha_programada=dias_desde_hoy(-10), fecha_realizada=dias_desde_hoy(-10),
                resultado="Sobresaliente", comentario="Buen desempeño en campo durante el semestre.",
            ),
            Evaluacion(empleado=e_valentina, periodo=f"{HOY.year}-S1", fecha_programada=dias_desde_hoy(5)),
            Evaluacion(empleado=e_esteban, periodo=f"{HOY.year}-S1", fecha_programada=dias_desde_hoy(-5)),
        ])

        db.add_all([
            Capacitacion(
                empleado=e_paula, nombre="Excel avanzado para nómina",
                fecha_programada=dias_desde_hoy(-30), fecha_realizada=dias_desde_hoy(-28), horas=16,
            ),
            Capacitacion(
                empleado=e_natalia, nombre="Inducción en seguridad y salud en el trabajo",
                fecha_programada=dias_desde_hoy(10),
            ),
            Capacitacion(
                empleado=e_jorge, nombre="Manejo de GPS y cartografía de campo",
                fecha_programada=dias_desde_hoy(-3),
            ),
        ])

        db.add_all([
            ExamenMedico(
                empleado=e_ricardo, tipo=TipoExamenMedico.ingreso,
                fecha_realizado=date(HOY.year - 1, 3, 1), fecha_proximo=dias_desde_hoy(25),
            ),
            ExamenMedico(
                empleado=e_sofia, tipo=TipoExamenMedico.periodico,
                fecha_realizado=dias_desde_hoy(-350), fecha_proximo=dias_desde_hoy(4),
            ),
            ExamenMedico(
                empleado=e_maria, tipo=TipoExamenMedico.periodico,
                fecha_realizado=dias_desde_hoy(-100), fecha_proximo=dias_desde_hoy(200),
            ),
        ])

        # Una incapacidad vigente hoy, para demostrar la alerta de
        # "incapacidad activa" (la de Jorge, más arriba, ya terminó).
        db.add(
            Solicitud(
                empleado=e_natalia, tipo=TipoSolicitud.incapacidad,
                fecha_solicitud=dias_desde_hoy(-3), fecha_inicio=dias_desde_hoy(-2), fecha_fin=dias_desde_hoy(3),
                motivo="Incapacidad médica por gripe.",
                estado_jefe=EstadoAprobacion.aprobado, jefe_comentario="Confirmado con el parte médico.",
                jefe_fecha_respuesta=dias_desde_hoy(-2),
                estado_th=EstadoAprobacion.aprobado, th_comentario="Incapacidad radicada ante la EPS.",
                th_fecha_respuesta=dias_desde_hoy(-1),
            )
        )

        for periodo in (mes_anterior, periodo_actual):
            for empleado, (salario, movilidad) in salarios.items():
                # Quien cobra quincenalmente tiene dos registros por mes; quien
                # cobra mensual, uno solo. Salud y pensión las calcula la
                # liquidación y aquí no se registran otros descuentos.
                for quincena in periodos_de_pago(empleado):
                    liq = liquidar_nomina(
                        empleado,
                        salario,
                        auxilio_movilidad=movilidad,
                        quincena=quincena,
                    )
                    db.add(
                        Nomina(
                            empleado=empleado,
                            periodo=periodo,
                            quincena=quincena,
                            fecha_pago=fecha_de_pago(periodo, quincena),
                            dias_liquidados=liq.dias_liquidados,
                            salario_base=liq.salario_base,
                            salario_devengado=liq.salario_devengado,
                            auxilio_transporte=liq.auxilio_transporte,
                            auxilio_movilidad=liq.auxilio_movilidad,
                            salud_empleado=liq.salud_empleado,
                            pension_empleado=liq.pension_empleado,
                            descuentos=liq.otros_descuentos,
                            total_descuentos=liq.total_descuentos,
                            total=liq.neto_pagado,
                            prima=liq.prima,
                            cesantias=liq.cesantias,
                            intereses_cesantias=liq.intereses_cesantias,
                            provision_vacaciones=liq.provision_vacaciones,
                            pension_empleador=liq.pension_empleador,
                            arl=liq.arl,
                            otros_aportes=liq.otros_aportes,
                            total_prestaciones=liq.total_prestaciones,
                            costo_empleador=liq.costo_empleador,
                            pagada=(periodo == mes_anterior),
                        )
                    )

        db.commit()
        print("Datos de ejemplo cargados correctamente.")
        print("Usuarios de prueba:")
        print("  Talento Humano  -> usuario: th     contraseña: th12345")
        print("  Administrativo  -> usuario: admin  contraseña: admin12345")
    finally:
        db.close()


def run_si_esta_vacia() -> None:
    """Siembra los datos de ejemplo solo si la base está vacía.

    Pensado para ejecutarse en cada despliegue sin riesgo: si ya hay
    información cargada no toca nada, así que la primera publicación queda
    con datos para la demo y las siguientes conservan lo que haya.

    Si la base no responde, no se interrumpe el despliegue: se avisa y se
    sigue, porque el servicio puede arrancar igual y reintentarlo después.
    """
    try:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        try:
            ya_hay_datos = db.query(Usuario).first() is not None
        finally:
            db.close()
    except Exception as exc:  # noqa: BLE001 - se informa y se continúa
        print(f"No se pudo consultar la base ({exc.__class__.__name__}): se omite la siembra.")
        return

    if ya_hay_datos:
        print("La base ya tiene datos: no se siembra nada y se conserva la información existente.")
        return

    print("Base vacía: se cargan los datos de ejemplo.")
    run()


if __name__ == "__main__":
    import os
    import sys

    # --solo-si-vacia: no destruye nada, es el modo que se usa al desplegar.
    # Sin argumentos: BORRA las tablas y las vuelve a crear desde cero.
    if "--solo-si-vacia" in sys.argv:
        # Válvula de escape para bases ya creadas: cuando el modelo cambia
        # (columnas nuevas), create_all() NO altera las tablas existentes.
        # Poniendo SEED_RESET=1 en las variables de entorno de Render y
        # redesplegando, la base se recrea desde cero. Hay que quitar la
        # variable después, o cada despliegue borrará los datos.
        if os.getenv("SEED_RESET", "").strip().lower() in {"1", "true", "si", "sí"}:
            print("SEED_RESET activo: se recrea la base desde cero y se pierden los datos actuales.")
            run()
        else:
            run_si_esta_vacia()
    else:
        run()
