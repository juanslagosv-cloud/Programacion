# Ecodes HR

Sistema web de Talento Humano para Ecodes, construido con FastAPI, PostgreSQL, SQLAlchemy y una interfaz web en HTML/CSS/JS con diseño adaptado a la identidad visual de la empresa.

## Stack

- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- JWT
- Jinja2 + HTML/CSS/JS
- Pandas + Openpyxl para exportación Excel
- Docker Compose para PostgreSQL local

## Requisitos

- Python 3.11+
- Docker Desktop o Docker Engine
- Git

## Instalación

1. Clona el repositorio.
2. Crea un entorno virtual:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows PowerShell
```

3. Instala las dependencias:

```bash
pip install -r requirements.txt
```

4. Crea el archivo `.env` basado en `.env.example`:

```bash
cp .env.example .env
```

5. Levanta PostgreSQL con Docker:

```bash
docker compose up -d postgres
```

6. Ejecuta la aplicación:

```bash
uvicorn app.main:app --reload
```

La aplicación queda disponible en:

- http://localhost:8000/login
- http://localhost:8000/app

## Seed de demo

```bash
python scripts/seed_demo.py
```

## Usuarios demo

- Talento Humano
  - usuario: talento
  - contraseña: talento123
- Administrativo
  - usuario: admin
  - contraseña: admin123

## Endpoints principales

- `/auth/login`
- `/empleados`
- `/proyectos`
- `/participaciones`
- `/novedades`
- `/nomina`
- `/alertas/vacaciones`
- `/alertas/sobreasignacion`
- `/exportar/excel`

## Exportación Excel

El endpoint `/exportar/excel` genera un archivo `.xlsx` con hojas para Empleados, Estudios, Experiencia, Proyectos, Participaciones, Nómina y Novedades. Está orientado para conectarse desde Power BI.

## Notas de diseño

- Base blanca con acento verde/azul.
- Soporta modo oscuro del sistema por variables CSS.
- Panel lateral con prioridad visual más alta.
- sin dashboard gráfico embebido; todo se exporta a Excel para análisis en Power BI.

## Despliegue

Para despliegue en producción conviene usar:

- PostgreSQL en un servicio gestionado
- variables de entorno reales para JWT y CORS
- reverse proxy como Nginx o un servicio de hosting con Gunicorn/Uvicorn

Ejemplo:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
