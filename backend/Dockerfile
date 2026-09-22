# Imagen del sistema de Talento Humano de Ecodes.
# Sirve la API y también las pantallas, así que es lo único que hay que
# levantar en el servidor de la empresa.
FROM python:3.11-slim

# psycopg2-binary trae sus propias librerías, pero pandas y reportlab
# agradecen estas herramientas básicas.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY frontend /frontend

# main.py busca el frontend en ../../frontend respecto de app/, que dentro
# del contenedor es /frontend.
RUN mkdir -p /frontend

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
