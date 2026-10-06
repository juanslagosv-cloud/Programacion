#!/usr/bin/env bash
# Respaldo de la base de datos de Talento Humano - Ecodes.
# Crea un archivo .sql con la fecha en el nombre, dentro de "respaldos".
#
# Para que corra solo todos los días a las 7 p.m., agregar a crontab:
#   0 19 * * * /ruta/al/proyecto/respaldar.sh
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p respaldos

ARCHIVO="respaldos/ecodes_th_$(date +%Y-%m-%d_%H%M).sql"

echo "Generando respaldo..."
docker compose exec -T db pg_dump -U ecodes ecodes_th > "$ARCHIVO"

echo "Respaldo creado: $ARCHIVO"
echo "Copia esa carpeta a donde guardan los respaldos de la empresa."
