from io import BytesIO

import pandas as pd
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Empleado, Estudio, Experiencia, Nomina, Novedad, Participacion, Proyecto

router = APIRouter(prefix="/exportar", tags=["Exportar"])


@router.get("/excel")
def exportar_excel(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    empleados = db.query(Empleado).all()
    df_empleados = pd.DataFrame(
        [
            {
                "id": e.id,
                "nombre_completo": e.nombre_completo,
                "genero": e.genero.value,
                "fecha_nacimiento": e.fecha_nacimiento,
                "direccion": e.direccion,
                "nivel_educativo": e.nivel_educativo.value,
                "nombre_cargo": e.nombre_cargo,
                "tipo_cargo": e.tipo_cargo.value,
                "fecha_ingreso": e.fecha_ingreso,
                "estado": e.estado.value,
                "periodicidad_pago": e.periodicidad_pago.value,
                "vacaciones_ultima_toma": e.vacaciones_ultima_toma,
                "vacaciones_dias_pendientes": e.vacaciones_dias_pendientes,
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

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df_empleados.to_excel(writer, sheet_name="empleados", index=False)
        df_estudios.to_excel(writer, sheet_name="estudios", index=False)
        df_experiencia.to_excel(writer, sheet_name="experiencia", index=False)
        df_proyectos.to_excel(writer, sheet_name="proyectos", index=False)
        df_participaciones.to_excel(writer, sheet_name="participaciones", index=False)
        df_nomina.to_excel(writer, sheet_name="nomina", index=False)
        df_novedades.to_excel(writer, sheet_name="novedades", index=False)

    buffer.seek(0)
    headers = {"Content-Disposition": "attachment; filename=ecodes_talento_humano.xlsx"}
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )
