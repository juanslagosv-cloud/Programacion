from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import text

from app.api.routes.alerts import router as alerts_router
from app.api.routes.auth import router as auth_router
from app.api.routes.employees import router as employees_router
from app.api.routes.events import router as events_router
from app.api.routes.export import router as export_router
from app.api.routes.participations import router as participations_router
from app.api.routes.payroll import router as payroll_router
from app.api.routes.projects import router as projects_router
from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app import crud

settings = get_settings()
app = FastAPI(title="Ecodes HR", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(auth_router)
app.include_router(employees_router)
app.include_router(projects_router)
app.include_router(participations_router)
app.include_router(events_router)
app.include_router(payroll_router)
app.include_router(alerts_router)
app.include_router(export_router)


def ensure_user_email_column() -> None:
    with engine.begin() as conn:
        try:
            result = conn.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result.fetchall()]
            if "email" not in columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN email VARCHAR(255)"))
                conn.execute(text("UPDATE users SET email = username || '@ecodes.com' WHERE email IS NULL OR email = ''"))
                conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users (email)"))
        except Exception:
            pass


@app.on_event("startup")
def startup_event() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_user_email_column()
    db = SessionLocal()
    try:
        crud.create_seed_users(db)
        crud.create_seed_data(db)
    finally:
        db.close()


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse(url="/ecodesTH/login")


@app.get("/ecodesTH", include_in_schema=False)
def ecodes_th_root() -> RedirectResponse:
    return RedirectResponse(url="/ecodesTH/login")


@app.get("/login", include_in_schema=False)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/ecodesTH/login", include_in_schema=False)
def ecodes_th_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/app", include_in_schema=False)
def app_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/ecodesTH/app", include_in_schema=False)
def ecodes_th_app_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
