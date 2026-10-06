from io import BytesIO

import pandas as pd
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import (
    Area,
    Capacitacion,
    Cargo,
    Certificacion,
    Contrato,
    Documento,
    Empleado,
    Empresa,
    Estudio,
    Evaluacion,
    ExamenMedico,
    Experiencia,
    ModificacionContrato,
    Nomina,
    Novedad,
    ParametroLegal,
    Participacion,
    Proyecto,
    Solicitud,
    Vacante,
)
from app.utils import contar_empleados_area, dias_solicitados, duracion_contrato, estado_general_solicitud

router = APIRouter(prefix="/exportar", tags=["Exportar"])


@router.get("/excel")
def exportar_excel(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    empleados = db.query(Empleado).all()
    df_empleados = pd.DataFrame(
        [
            {
                "id": e.id,
                "empresa_id": e.empresa_id,
                "empresa_nombre": e.empresa.nombre if e.empresa else None,
                "nombre_completo": e.nombre_completo,
                "tipo_documento": e.tipo_documento.value,
                "numero_documento": e.numero_documento,
                "genero": e.genero.value,
                "fecha_nacimiento": e.fecha_nacimiento,
                "direccion": e.direccion,
                "ciudad": e.ciudad,
                "estado_civil": e.estado_civil.value if e.estado_civil else None,
                "contacto_emergencia_nombre": e.contacto_emergencia_nombre,
                "contacto_emergencia_telefono": e.contacto_emergencia_telefono,
                "contacto_emergencia_parentesco": e.contacto_emergencia_parentesco,
                "area": e.area,
                "jefe_inmediato_id": e.jefe_inmediato_id,
                "jefe_inmediato_nombre": e.jefe_inmediato.nombre_completo if e.jefe_inmediato else None,
                "nivel_educativo": e.nivel_educativo.value,
                "nombre_cargo": e.nombre_cargo,
                "tipo_cargo": e.tipo_cargo.value,
                "fecha_ingreso": e.fecha_ingreso,
                "estado": e.estado.value,
                "periodicidad_pago": e.periodicidad_pago.value,
                "vacaciones_ultima_toma": e.vacaciones_ultima_toma,
                "vacaciones_dias_pendientes": e.vacaciones_dias_pendientes,
                "banco": e.banco,
                "tipo_cuenta": e.tipo_cuenta.value if e.tipo_cuenta else None,
                "numero_cuenta": e.numero_cuenta,
                "eps": e.eps,
                "afp": e.afp,
                "arl": e.arl,
                "nivel_riesgo_arl": e.nivel_riesgo_arl.value if e.nivel_riesgo_arl else None,
                "caja_compensacion": e.caja_compensacion,
                "fondo_cesantias": e.fondo_cesantias,
            }
            for e in empleados
        ]
    )

    estudios = db.query(Estudio).all()
    df_estudios = pd.DataFrame(
        [
            {
                "id": s.id,
                "empleado_id": s.empleado_id,
                "titulo": s.titulo,
                "institucion": s.institucion,
                "anio": s.anio,
            }
            for s in estudios
        ]
    )

    experiencias = db.query(Experiencia).all()
    df_experiencia = pd.DataFrame(
        [
            {
                "id": x.id,
                "empleado_id": x.empleado_id,
                "empresa": x.empresa,
                "cargo": x.cargo,
                "periodo": x.periodo,
            }
            for x in experiencias
        ]
    )

    proyectos = db.query(Proyecto).all()
    df_proyectos = pd.DataFrame(
        [
            {
                "id": p.id,
                "empresa_id": p.empresa_id,
                "empresa_nombre": p.empresa.nombre if p.empresa else None,
                "nombre": p.nombre,
                "contratante": p.contratante,
                "fecha_inicio": p.fecha_inicio,
                "fecha_fin": p.fecha_fin,
                "presupuesto": float(p.presupuesto),
                "estado": p.estado.value,
            }
            for p in proyectos
        ]
    )

    participaciones = db.query(Participacion).all()
    df_participaciones = pd.DataFrame(
        [
            {
                "id": pa.id,
                "empleado_id": pa.empleado_id,
                "proyecto_id": pa.proyecto_id,
                "porcentaje": float(pa.porcentaje),
                "fecha_asignacion": pa.fecha_asignacion,
            }
            for pa in participaciones
        ]
    )

    nominas = db.query(Nomina).all()
    df_nomina = pd.DataFrame(
        [
            {
                "id": n.id,
                "empleado_id": n.empleado_id,
                "periodo": n.periodo,
                "quincena": n.quincena,
                "fecha_pago": n.fecha_pago,
                "dias_liquidados": n.dias_liquidados,
                "salario_base": float(n.salario_base),
                "salario_devengado": float(n.salario_devengado),
                "auxilio_transporte": float(n.auxilio_transporte),
                "auxilio_movilidad": float(n.auxilio_movilidad),
                "salud_empleado": float(n.salud_empleado),
                "pension_empleado": float(n.pension_empleado),
                "otros_descuentos": float(n.descuentos),
                "total_descuentos": float(n.total_descuentos),
                "neto_pagado": float(n.total),
                "prima": float(n.prima),
                "cesantias": float(n.cesantias),
                "intereses_cesantias": float(n.intereses_cesantias),
                "provision_vacaciones": float(n.provision_vacaciones),
                "pension_empleador": float(n.pension_empleador),
                "arl": float(n.arl),
                "otros_aportes": float(n.otros_aportes),
                "total_prestaciones": float(n.total_prestaciones),
                "costo_empleador": float(n.costo_empleador),
                "pagada": n.pagada,
            }
            for n in nominas
        ]
    )

    contratos = db.query(Contrato).all()
    df_contratos = pd.DataFrame(
        [
            {
                "id": c.id,
                "empleado_id": c.empleado_id,
                "empleado_nombre": c.empleado.nombre_completo,
                "tipo_contrato": c.tipo_contrato.value,
                "fecha_inicio": c.fecha_inicio,
                "fecha_fin": c.fecha_fin,
                "duracion": duracion_contrato(c),
                "periodo_prueba_dias": c.periodo_prueba_dias,
                "cargo_contractual": c.cargo_contractual,
                "salario": float(c.salario),
                "proyecto_id": c.proyecto_id,
                "proyecto_nombre": c.proyecto.nombre if c.proyecto else None,
                "centro_costos": c.centro_costos,
                "modalidad": c.modalidad.value,
                "estado": c.estado.value,
            }
            for c in contratos
        ]
    )

    modificaciones = db.query(ModificacionContrato).all()
    df_modificaciones = pd.DataFrame(
        [
            {
                "id": m.id,
                "contrato_id": m.contrato_id,
                "empleado_id": m.contrato.empleado_id,
                "tipo": m.tipo.value,
                "fecha": m.fecha,
                "detalle": m.detalle,
                "nueva_fecha_fin": m.nueva_fecha_fin,
            }
            for m in modificaciones
        ]
    )

    novedades = db.query(Novedad).all()
    df_novedades = pd.DataFrame(
        [
            {
                "id": nv.id,
                "empleado_id": nv.empleado_id,
                "proyecto_id": nv.proyecto_id,
                "tipo": nv.tipo.value,
                "fecha": nv.fecha,
                "detalle": nv.detalle,
                "procesada": nv.procesada,
            }
            for nv in novedades
        ]
    )

    solicitudes = db.query(Solicitud).all()
    df_solicitudes = pd.DataFrame(
        [
            {
                "id": s.id,
                "empleado_id": s.empleado_id,
                "empleado_nombre": s.empleado.nombre_completo,
                "tipo": s.tipo.value,
                "fecha_solicitud": s.fecha_solicitud,
                "fecha_inicio": s.fecha_inicio,
                "fecha_fin": s.fecha_fin,
                "dias_solicitados": dias_solicitados(s),
                "horas": float(s.horas) if s.horas is not None else None,
                "motivo": s.motivo,
                "valor_propuesto": s.valor_propuesto,
                "proyecto_propuesto_id": s.proyecto_propuesto_id,
                "proyecto_propuesto_nombre": s.proyecto_propuesto.nombre if s.proyecto_propuesto else None,
                "jefe_inmediato_nombre": s.empleado.jefe_inmediato.nombre_completo if s.empleado.jefe_inmediato else None,
                "estado_jefe": s.estado_jefe.value,
                "jefe_comentario": s.jefe_comentario,
                "jefe_fecha_respuesta": s.jefe_fecha_respuesta,
                "estado_th": s.estado_th.value,
                "th_comentario": s.th_comentario,
                "th_fecha_respuesta": s.th_fecha_respuesta,
                "estado_general": estado_general_solicitud(s),
            }
            for s in solicitudes
        ]
    )

    areas = db.query(Area).all()
    df_areas = pd.DataFrame(
        [
            {
                "id": a.id,
                "empresa_id": a.empresa_id,
                "nombre": a.nombre,
                "area_padre_id": a.area_padre_id,
                "area_padre_nombre": a.area_padre.nombre if a.area_padre else None,
                "responsable_id": a.responsable_id,
                "responsable_nombre": a.responsable.nombre_completo if a.responsable else None,
                "total_empleados": contar_empleados_area(a),
            }
            for a in areas
        ]
    )

    cargos = db.query(Cargo).all()
    df_cargos = pd.DataFrame(
        [
            {
                "id": c.id,
                "empresa_id": c.empresa_id,
                "area_id": c.area_id,
                "area_nombre": c.area.nombre if c.area else None,
                "nombre": c.nombre,
                "cargo_superior_id": c.cargo_superior_id,
                "cargo_superior_nombre": c.cargo_superior.nombre if c.cargo_superior else None,
            }
            for c in cargos
        ]
    )

    vacantes = db.query(Vacante).all()
    df_vacantes = pd.DataFrame(
        [
            {
                "id": v.id,
                "empresa_id": v.empresa_id,
                "area_id": v.area_id,
                "area_nombre": v.area.nombre if v.area else None,
                "cargo_id": v.cargo_id,
                "cargo_nombre": v.cargo.nombre if v.cargo else None,
                "titulo": v.titulo,
                "motivo": v.motivo,
                "salario_ofrecido": float(v.salario_ofrecido) if v.salario_ofrecido is not None else None,
                "fecha_apertura": v.fecha_apertura,
                "fecha_cierre_esperada": v.fecha_cierre_esperada,
                "fecha_cierre_real": v.fecha_cierre_real,
                "estado": v.estado.value,
                "notas": v.notas,
            }
            for v in vacantes
        ]
    )

    certificaciones = db.query(Certificacion).all()
    df_certificaciones = pd.DataFrame(
        [
            {
                "id": c.id,
                "empleado_id": c.empleado_id,
                "empleado_nombre": c.empleado.nombre_completo,
                "nombre": c.nombre,
                "entidad": c.entidad,
                "fecha_obtencion": c.fecha_obtencion,
                "fecha_vencimiento": c.fecha_vencimiento,
            }
            for c in certificaciones
        ]
    )

    documentos = db.query(Documento).all()
    df_documentos = pd.DataFrame(
        [
            {
                "id": d.id,
                "empleado_id": d.empleado_id,
                "empleado_nombre": d.empleado.nombre_completo,
                "tipo": d.tipo.value,
                "nombre_archivo": d.nombre_archivo,
                "fecha_cargue": d.fecha_cargue,
            }
            for d in documentos
        ]
    )

    evaluaciones = db.query(Evaluacion).all()
    df_evaluaciones = pd.DataFrame(
        [
            {
                "id": ev.id,
                "empleado_id": ev.empleado_id,
                "empleado_nombre": ev.empleado.nombre_completo,
                "periodo": ev.periodo,
                "fecha_programada": ev.fecha_programada,
                "fecha_realizada": ev.fecha_realizada,
                "resultado": ev.resultado,
                "comentario": ev.comentario,
            }
            for ev in evaluaciones
        ]
    )

    capacitaciones = db.query(Capacitacion).all()
    df_capacitaciones = pd.DataFrame(
        [
            {
                "id": cap.id,
                "empleado_id": cap.empleado_id,
                "empleado_nombre": cap.empleado.nombre_completo,
                "nombre": cap.nombre,
                "fecha_programada": cap.fecha_programada,
                "fecha_realizada": cap.fecha_realizada,
                "horas": cap.horas,
            }
            for cap in capacitaciones
        ]
    )

    examenes_medicos = db.query(ExamenMedico).all()
    df_examenes_medicos = pd.DataFrame(
        [
            {
                "id": ex.id,
                "empleado_id": ex.empleado_id,
                "empleado_nombre": ex.empleado.nombre_completo,
                "tipo": ex.tipo.value,
                "fecha_realizado": ex.fecha_realizado,
                "fecha_proximo": ex.fecha_proximo,
                "concepto": ex.concepto,
            }
            for ex in examenes_medicos
        ]
    )

    parametros_legales = db.query(ParametroLegal).all()
    df_parametros_legales = pd.DataFrame(
        [
            {
                "id": p.id,
                "codigo": p.codigo,
                "nombre": p.nombre,
                "descripcion": p.descripcion,
                "valor": float(p.valor),
                "unidad": p.unidad.value,
                "fecha_inicio_vigencia": p.fecha_inicio_vigencia,
                "fecha_fin_vigencia": p.fecha_fin_vigencia,
                "anio": p.anio,
                "norma": p.norma,
                "observaciones": p.observaciones,
                "activo": p.activo,
                "pendiente_verificacion": p.pendiente_verificacion,
                "usuario_cambio": p.usuario_cambio.nombre if p.usuario_cambio else None,
                "fecha_cambio": p.fecha_cambio,
            }
            for p in parametros_legales
        ]
    )

    empresas = db.query(Empresa).all()
    df_empresas = pd.DataFrame(
        [
            {
                "id": emp.id,
                "nombre": emp.nombre,
                "nit": emp.nit,
                "ciudad": emp.ciudad,
                "activa": emp.activa,
                "total_empleados": len(emp.empleados),
                "total_proyectos": len(emp.proyectos),
            }
            for emp in empresas
        ]
    )

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_empresas.to_excel(writer, sheet_name="empresas", index=False)
        df_empleados.to_excel(writer, sheet_name="empleados", index=False)
        df_estudios.to_excel(writer, sheet_name="estudios", index=False)
        df_experiencia.to_excel(writer, sheet_name="experiencia", index=False)
        df_proyectos.to_excel(writer, sheet_name="proyectos", index=False)
        df_participaciones.to_excel(writer, sheet_name="participaciones", index=False)
        df_contratos.to_excel(writer, sheet_name="contratos", index=False)
        df_modificaciones.to_excel(writer, sheet_name="modificaciones_contrato", index=False)
        df_nomina.to_excel(writer, sheet_name="nomina", index=False)
        df_novedades.to_excel(writer, sheet_name="novedades", index=False)
        df_solicitudes.to_excel(writer, sheet_name="solicitudes", index=False)
        df_areas.to_excel(writer, sheet_name="areas", index=False)
        df_cargos.to_excel(writer, sheet_name="cargos", index=False)
        df_vacantes.to_excel(writer, sheet_name="vacantes", index=False)
        df_certificaciones.to_excel(writer, sheet_name="certificaciones", index=False)
        df_documentos.to_excel(writer, sheet_name="documentos", index=False)
        df_evaluaciones.to_excel(writer, sheet_name="evaluaciones", index=False)
        df_capacitaciones.to_excel(writer, sheet_name="capacitaciones", index=False)
        df_examenes_medicos.to_excel(writer, sheet_name="examenes_medicos", index=False)
        df_parametros_legales.to_excel(writer, sheet_name="parametros_legales", index=False)

    buffer.seek(0)
    headers = {"Content-Disposition": "attachment; filename=ecodes_talento_humano.xlsx"}
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )
