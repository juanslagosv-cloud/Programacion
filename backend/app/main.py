import logging
from pathlib import Path

from fastapi import FastAPI
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import Base, engine
from app.routers import alertas, auth, empleados, empresas, exportar, nomina, novedades, participaciones, proyectos

logger = logging.getLogger(__name__)

# Crear las tablas si aún no existen. Si la base de datos no responde no se
# tumba el proceso: el servicio arranca igual y /salud permite diagnosticarlo.
# (En un arranque en frío la base puede tardar unos segundos en aceptar
# conexiones; la siguiente petición ya la encuentra disponible.)
try:
    Base.metadata.create_all(bind=engine)
except Exception:  # noqa: BLE001 - se registra y se sigue, a propósito
    logger.exception("No se pudieron crear las tablas al iniciar")

app = FastAPI(
    title="Ecodes · Talento Humano",
    description="API del sistema de gestión de Talento Humano de Ecodes (Colombia · Perú · Argentina).",
    version="1.0.0",
)

cors_kwargs = {
    "allow_origins": settings.cors_origins_list,
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
    # Sin esto el navegador no deja que el JavaScript lea el nombre del
    # archivo, y las descargas salen con un nombre genérico.
    "expose_headers": ["Content-Disposition"],
}
if settings.cors_origin_regex:
    cors_kwargs["allow_origin_regex"] = settings.cors_origin_regex

app.add_middleware(CORSMiddleware, **cors_kwargs)

app.include_router(auth.router)
app.include_router(empresas.router)
app.include_router(empleados.router)
app.include_router(proyectos.router)
app.include_router(participaciones.router)
app.include_router(novedades.router)
app.include_router(nomina.router)
app.include_router(alertas.router)
app.include_router(exportar.router)


@app.get("/api", tags=["Estado"])
def raiz():
    return {"servicio": "Ecodes Talento Humano API", "estado": "operativo"}


@app.get("/salud", tags=["Estado"])
def salud():
    """Estado del servicio y de la conexión a la base de datos."""
    try:
        with engine.connect() as conexion:
            conexion.execute(text("SELECT 1"))
        base_datos = "ok"
    except Exception as exc:  # noqa: BLE001 - se reporta el motivo al operador
        base_datos = f"error: {exc.__class__.__name__}"
    return {"status": "ok", "base_datos": base_datos}


# ---------------------------------------------------------------------------
# Servir el frontend desde el mismo servidor.
#
# En una instalación local esto es lo que hace que todo sea una sola cosa:
# se levanta un único programa, los computadores de la oficina entran a
# http://IP-DEL-SERVIDOR:8000 y ya. Al compartir origen con la API tampoco
# hay que configurar CORS.
#
# Va al final a propósito: las rutas de la API se registran primero y tienen
# prioridad sobre estos archivos.
# ---------------------------------------------------------------------------
FRONTEND = Path(__file__).resolve().parent.parent.parent / "frontend"

if FRONTEND.is_dir():
    app.mount("/", StaticFiles(directory=str(FRONTEND), html=True), name="frontend")
else:
    logger.warning("No se encontró la carpeta frontend en %s: solo se sirve la API", FRONTEND)
