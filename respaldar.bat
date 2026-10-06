@echo off
REM ============================================================
REM  Respaldo de la base de datos de Talento Humano - Ecodes
REM
REM  Crea un archivo .sql en la carpeta "respaldos", con la fecha
REM  en el nombre. Esa carpeta se puede copiar como cualquier otra.
REM
REM  Para que corra solo todos los dias:
REM    Panel de control > Herramientas administrativas >
REM    Programador de tareas > Crear tarea basica
REM    y apuntar a este archivo.
REM ============================================================

cd /d "%~dp0"

for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set DT=%%I
set FECHA=%DT:~0,4%-%DT:~4,2%-%DT:~6,2%_%DT:~8,2%%DT:~10,2%

if not exist respaldos mkdir respaldos

echo Generando respaldo...
docker compose exec -T db pg_dump -U ecodes ecodes_th > "respaldos\ecodes_th_%FECHA%.sql"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo  Respaldo creado: respaldos\ecodes_th_%FECHA%.sql
    echo  Copia esa carpeta a donde guardan los respaldos de la empresa.
) else (
    echo.
    echo  ERROR: no se pudo crear el respaldo.
    echo  Revisa que el sistema este encendido con: docker compose ps
)
echo.
pause
