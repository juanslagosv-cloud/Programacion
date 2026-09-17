from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routers import alertas, auth, empleados, exportar, nomina, novedades, participaciones, proyectos

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Ecodes · Talento Humano",
    description="API del sistema de gestión de Talento Humano de Ecodes (Colombia · Perú · Argentina).",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(empleados.router)
app.include_router(proyectos.router)
app.include_router(participaciones.router)
app.include_router(novedades.router)
app.include_router(nomina.router)
app.include_router(alertas.router)
app.include_router(exportar.router)


@app.get("/", tags=["Estado"])
def raiz():
    return {"servicio": "Ecodes Talento Humano API", "estado": "operativo"}


@app.get("/salud", tags=["Estado"])
def salud():
    return {"status": "ok"}
