"""Script de siembra de datos de ejemplo para demos del sistema.

Uso:
    cd backend
    python -m app.seed
"""

from datetime import date, timedelta

from app.database import Base, SessionLocal, engine
from app.models import (
    Empleado,
    EstadoEmpleado,
    EstadoProyecto,
    Estudio,
    Experiencia,
    Genero,
    Nomina,
    NivelEducativo,
    Novedad,
    Participacion,
    PeriodicidadPago,
    Proyecto,
    RolUsuario,
    TipoCargo,
    TipoNovedad,
    Usuario,
)
from app.security import hash_password
from app.utils import fecha_de_pago, liquidar_nomina, periodos_de_pago

HOY = date.today()


def dias_desde_hoy(dias: int) -> date:
    return HOY + timedelta(days=dias)


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
        # Proyectos
        # -------------------------------------------------------------
        p1 = Proyecto(
            nombre="Restauración Ecológica Cuenca Alta del Chicamocha",
            contratante="Corporación Autónoma Regional de Boyacá",
            fecha_inicio=date(HOY.year - 1, 3, 1),
            fecha_fin=date(HOY.year + 1, 2, 28),
            presupuesto=980_000_000,
            estado=EstadoProyecto.activo,
        )
        p2 = Proyecto(
            nombre="Compensación Forestal Corredor Vial Pacífico",
            contratante="Concesión Vial del Pacífico S.A.S.",
            fecha_inicio=date(HOY.year - 1, 7, 15),
            fecha_fin=date(HOY.year, 12, 15),
            presupuesto=650_000_000,
            estado=EstadoProyecto.activo,
        )
        p3 = Proyecto(
            nombre="Monitoreo de Biodiversidad Selva Central",
            contratante="Ministerio del Ambiente - Perú",
            fecha_inicio=date(HOY.year - 2, 1, 10),
            fecha_fin=None,
            presupuesto=1_250_000_000,
            estado=EstadoProyecto.continuo,
        )
        p4 = Proyecto(
            nombre="Gestión Ambiental Corporativa Minera del Norte",
            contratante="Minera del Norte S.A.",
            fecha_inicio=date(HOY.year - 1, 9, 1),
            fecha_fin=date(HOY.year, 10, 30),
            presupuesto=410_000_000,
            estado=EstadoProyecto.cierre,
        )
        p5 = Proyecto(
            nombre="Restauración de Bosque Nativo Patagonia",
            contratante="Provincia de Río Negro - Argentina",
            fecha_inicio=date(HOY.year, 2, 1),
            fecha_fin=date(HOY.year + 1, 8, 30),
            presupuesto=560_000_000,
            estado=EstadoProyecto.activo,
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


if __name__ == "__main__":
    run()
