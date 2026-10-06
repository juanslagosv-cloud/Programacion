#!/usr/bin/env bash
# Restaura un respaldo sobre la base de datos.
#
#   ./restaurar.sh respaldos/ecodes_th_2026-09-22_1900.sql
#
# ATENCIÓN: reemplaza TODO lo que haya en la base por el contenido del
# archivo. Lo que esté cargado ahora se pierde.
set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Uso: $0 <archivo-de-respaldo.sql>"
  exit 1
fi

ARCHIVO="$1"
[ -f "$ARCHIVO" ] || { echo "No existe el archivo: $ARCHIVO"; exit 1; }

cd "$(dirname "$0")"

echo "Esto reemplaza TODOS los datos actuales por los de $ARCHIVO."
read -r -p "¿Continuar? (escribe SI): " respuesta
[ "$respuesta" = "SI" ] || { echo "Cancelado."; exit 0; }

docker compose exec -T db psql -U ecodes -d postgres -c "DROP DATABASE IF EXISTS ecodes_th;"
docker compose exec -T db psql -U ecodes -d postgres -c "CREATE DATABASE ecodes_th;"
docker compose exec -T db psql -U ecodes -d ecodes_th < "$ARCHIVO"

echo "Base restaurada desde $ARCHIVO"
