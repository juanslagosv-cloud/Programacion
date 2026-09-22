# Ecodes · Sistema de Talento Humano

Sistema web de gestión de Talento Humano para **Ecodes**, empresa de consultoría y
gestión ambiental con operación en Colombia, Perú y Argentina (restauración
ecológica, compensación forestal, monitoreo de biodiversidad y gestión ambiental
corporativa).

El sistema **no construye dashboards ni gráficos**: administra la información
operativa (empleados, proyectos, participaciones, novedades y nómina) y permite
**exportarla a Excel** para que los indicadores de talento humano (rotación,
costos laborales prorrateados por proyecto, ausentismo) se analicen en **Power BI**.

---

## 1. Arquitectura

```
Programacion/
├── backend/                 # API REST — FastAPI + SQLAlchemy + PostgreSQL
│   ├── app/
│   │   ├── main.py          # Punto de entrada de la app FastAPI
│   │   ├── config.py        # Variables de entorno (pydantic-settings)
│   │   ├── database.py      # Motor SQLAlchemy y sesión
│   │   ├── models.py        # Modelos ORM (Empleado, Proyecto, Participación...)
│   │   ├── schemas.py       # Esquemas Pydantic (entrada/salida)
│   │   ├── security.py      # Hash de contraseñas y JWT
│   │   ├── deps.py          # Dependencias de autenticación y autorización
│   │   ├── utils.py         # Cálculos derivados (antigüedad, prorrateo, rotación)
│   │   ├── seed.py          # Script de datos de ejemplo para demo
│   │   └── routers/         # Endpoints agrupados por dominio
│   └── requirements.txt
├── frontend/                 # SPA ligera en HTML/CSS/JS puro (sin build step)
│   ├── index.html            # Login
│   ├── empleados.html / proyectos.html / novedades.html / nomina.html / alertas.html
│   ├── css/styles.css        # Sistema de diseño (claro/oscuro, marca Ecodes)
│   ├── js/                   # api.js, common.js y lógica de cada pantalla
│   └── assets/               # Logo e ilustración de campo (SVG)
├── docker-compose.yml         # PostgreSQL local
└── .env.example
```

**Roles:**

| Rol              | Acceso                                                            |
|------------------|--------------------------------------------------------------------|
| Talento Humano   | Lectura y escritura completa (crear, editar, eliminar)             |
| Administrativo   | Solo lectura — el backend bloquea cualquier escritura con `403`, y el frontend oculta los controles de edición |

---

## 2. Requisitos

- Python 3.11+
- Docker y Docker Compose (para PostgreSQL local) — o una instancia de PostgreSQL existente
- Un navegador moderno (no requiere Node.js ni build step para el frontend)

---

## 3. Puesta en marcha — Backend

### 3.1. Levantar PostgreSQL

```bash
docker compose up -d
```

Esto crea una base de datos `ecodes_th` en `localhost:5432` con usuario/clave
`ecodes` / `ecodes` (ver `docker-compose.yml`).

### 3.2. Configurar variables de entorno

```bash
cp .env.example backend/.env
```

Ajusta `backend/.env` si cambiaste las credenciales de la base de datos o quieres
usar una clave JWT propia. Variables disponibles:

| Variable                        | Descripción                                              |
|----------------------------------|-----------------------------------------------------------|
| `DATABASE_URL`                  | Cadena de conexión SQLAlchemy a PostgreSQL                |
| `JWT_SECRET_KEY`                | Clave secreta para firmar los tokens JWT                  |
| `JWT_ALGORITHM`                 | Algoritmo de firma (por defecto `HS256`)                   |
| `ACCESS_TOKEN_EXPIRE_MINUTES`   | Minutos de validez del token (por defecto 480 = 8h)        |
| `CORS_ORIGINS`                  | Orígenes permitidos, separados por coma                    |

### 3.3. Instalar dependencias y crear el entorno virtual

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3.4. Poblar la base de datos con datos de ejemplo

Las tablas se crean automáticamente al iniciar la app, pero para tener datos de
demo (empleados, proyectos, participaciones, novedades y nómina de ejemplo):

```bash
python -m app.seed
```

Esto crea dos usuarios de prueba:

- **Talento Humano** → usuario `th` / contraseña `th12345`
- **Administrativo** → usuario `admin` / contraseña `admin12345`

> El script de seed **borra y vuelve a crear todas las tablas** (`drop_all` +
> `create_all`) — solo debe usarse en ambientes de desarrollo/demo.

### 3.5. Iniciar la API

```bash
uvicorn app.main:app --reload --port 8000
```

La API queda disponible en `http://localhost:8000` y la documentación
interactiva (Swagger) en `http://localhost:8000/docs`.

---

## 4. Puesta en marcha — Frontend

El frontend es HTML/CSS/JS puro, sin dependencias ni build step. Solo necesita
servirse como archivos estáticos (no se puede abrir con `file://` porque el
navegador bloquea `fetch` entre orígenes distintos):

```bash
cd frontend
python3 -m http.server 8080
```

Abre `http://localhost:8080/index.html` en el navegador.

Si el backend corre en una URL distinta a `http://localhost:8000`, defínelo antes
de cargar los scripts agregando en cada HTML (o en un archivo `config.js` propio):

```html
<script>window.ECODES_API_BASE = "https://mi-api.dominio.com";</script>
```

Por defecto, añade `http://localhost:8080` a `CORS_ORIGINS` en `backend/.env`
para que el navegador pueda llamar a la API.

---

## 5. Flujo de uso

1. Inicia sesión en `index.html` seleccionando el rol (Talento Humano o
   Administrativo) e ingresando usuario/contraseña.
2. La pantalla de entrada es **Empleados**, con el widget de próximos
   cumpleaños (siguientes ~45 días) y la tabla filtrable de personal.
3. Haz clic en una fila para abrir la ficha completa del empleado (panel
   lateral): información general, formación académica, experiencia laboral,
   proyectos asignados (con su % de dedicación), vacaciones e historial de
   movimientos.
4. En **Proyectos** puedes crear proyectos y gestionar el equipo asignado con
   su % de dedicación — la suma de participación de una persona en todos sus
   proyectos nunca puede superar el 100% (validado en frontend y backend).
5. **Novedades** registra ingresos, salidas, cambios de proyecto e
   incapacidades. Una novedad de tipo "Salida" marca automáticamente al
   empleado como Inactivo.
6. **Nómina** muestra el resumen del mes (total, próximo pago, novedades sin
   procesar) y el detalle por empleado con los auxilios calculados
   automáticamente (ver "Reglas de auxilios" más abajo).
7. **Alertas** agrupa vacaciones por vencer, sobre-asignación de personal,
   nómina/pagos próximos y novedades sin procesar.
8. El botón **"Exportar a Excel"** (visible en todas las pantallas) descarga un
   libro con una hoja por tabla (`empleados`, `estudios`, `experiencia`,
   `proyectos`, `participaciones`, `nomina`, `novedades`), con columnas en
   `snake_case` y los mismos `id` como llaves, listo para conectar en Power BI
   y construir las relaciones e indicadores de rotación, costos laborales
   prorrateados y ausentismo.

---

## 6. Reglas de liquidación de nómina

Todas las tasas y valores viven en un solo lugar (`backend/app/utils.py`,
función `liquidar_nomina`) y los usan tanto el endpoint de nómina como el
script de seed, así que nunca se desincronizan.

### 6.1. Devengado

| Concepto | Valor 2026 | Regla |
|----------|-----------:|-------|
| Salario mínimo (SMLMV) | $1.750.905 | Referencia legal |
| Tope auxilio de transporte | $3.501.810 | 2 SMLMV |
| **Auxilio de transporte** | **$249.095** | Obligatorio por ley **solo** para quien devengue hasta 2 SMLMV. No depende del tipo de cargo. Si se deja en `0` al registrar la nómina, el sistema lo aplica automáticamente. |
| **Auxilio de movilidad** | lo define Ecodes | Auxilio interno para roles de campo. **No es salarial ni prestacional**: no entra en ninguna base, solo suma al costo. Al ser una decisión de la empresa, **se registra persona a persona** y el sistema nunca lo calcula ni lo asume. |

### 6.2. Deducciones al trabajador

| Concepto | Tasa | Base |
|----------|-----:|------|
| Salud | 4% | Salario base |
| Pensión | 4% | Salario base |

El campo `descuentos` queda libre para descuentos adicionales (préstamos,
embargos, etc.); salud y pensión se calculan aparte.

### 6.3. Costo adicional que asume el empleador

| Concepto | Tasa mensual | Base | Equivalente anual |
|----------|-------------:|------|-------------------|
| Prima de servicios | 8,33% | Salario + auxilio de transporte | 1 salario al año |
| Cesantías | 8,33% | Salario + auxilio de transporte | 1 salario al año |
| Intereses de cesantías | 1,00% | Salario + auxilio de transporte | 12% anual sobre cesantías |
| Provisión de vacaciones | 4,17% | Salario base | 15 días hábiles al año |
| Pensión (empleador) | 12% | Salario base | — |
| ARL (la paga 100% el empleador) | 0,522% oficina / 6,960% campo | Salario base | Según clase de riesgo |

**Bases de cálculo** (es donde se equivocan la mayoría de las hojas de Excel):

- El auxilio de transporte **sí** es base para prima, cesantías e intereses,
  pero **no** para vacaciones ni para seguridad social.
- El auxilio de movilidad no entra en ninguna base.

> **Dos supuestos que conviene confirmar con contabilidad:**
> 1. **Clase de riesgo de la ARL**: se asume riesgo V para cargos de campo y
>    riesgo I para oficina. Se ajusta en `TASA_ARL_RIESGO_*`.
> 2. **Exoneración de la Ley 1607 de 2012**: salud del empleador (8,5%), caja de
>    compensación (4%), SENA (2%) e ICBF (3%) están en `0.0`. Si Ecodes no está
>    exonerada, basta con poner las tasas reales en esas constantes y el cálculo
>    las incluye automáticamente.

### 6.4. Periodicidad de pago: mensual y quincenal

No todo el mundo cobra el mismo día. Cada empleado tiene un campo
`periodicidad_pago`:

| Periodicidad | Quiénes | Cuándo se paga | Registros de nómina por mes |
|--------------|---------|----------------|------------------------------|
| **Mensual** | Profesionales y administrativos | El último día del mes (los "30 de cada mes") | 1 registro, `quincena = null`, 30 días |
| **Quincenal** | Operarios y técnicos de campo | El 15 y el último día del mes | 2 registros, `quincena = 1` y `quincena = 2`, 15 días cada uno |

Al registrar una nómina, **el salario base que se digita siempre es el salario
mensual del contrato**, aunque el pago sea quincenal: el sistema parte el mes
internamente. Si no se indica la quincena, se asume la primera para quien cobra
quincenalmente y el mes completo para quien cobra mensual.

**Cómo se parte el mes.** Primero se liquida el mes completo y después se divide:
la primera quincena se lleva `round(valor / 2)` y la segunda el resto
(`valor - round(valor / 2)`). Así **las dos quincenas suman exactamente el mes**,
sin diferencias de un peso que después no cuadren en el Excel. Por eso es normal
que las dos quincenas de una misma persona difieran en unos pocos pesos: la
segunda absorbe el ajuste del redondeo.

El endpoint `GET /nomina/resumen` devuelve además la **fecha del próximo pago** y
a quiénes cubre (`proximo_pago_concepto`), contando cuántas personas cobran
mensual y cuántas quincenal. Las columnas `quincena`, `fecha_pago`,
`dias_liquidados` y `salario_devengado` se exportan en la hoja `nomina` del Excel
para poder analizar el flujo de caja por fecha de desembolso en Power BI.

> Para el prorrateo por proyecto se toma el **último período** de cada persona y
> se suman sus registros, de modo que un empleado quincenal aporta sus dos
> quincenas y no se subestima su costo.

### 6.5. Por qué importa para los indicadores

El **costo por proyecto se prorratea sobre el costo real del empleador**, no
sobre el salario: una persona cuesta entre 1,34× y 1,62× su salario según su
nivel salarial y su clase de riesgo. Con los datos de ejemplo, la carga
prestacional total es de **+47,7%** sobre el neto pagado — esa es la diferencia
entre lo que un proyecto *parece* costar y lo que realmente cuesta.

La hoja `nomina` del Excel exporta el desglose completo (`salud_empleado`,
`pension_empleado`, `prima`, `cesantias`, `intereses_cesantias`,
`provision_vacaciones`, `pension_empleador`, `arl`, `total_prestaciones`,
`costo_empleador`) para poder analizarlo en Power BI.

> Los valores cambian cada año con el decreto de salario mínimo: para
> actualizarlos basta editar las constantes al inicio de `backend/app/utils.py`.

---

## 7. Certificado laboral en PDF

Desde la ficha de cada empleado (panel lateral, sección **Documentos**) se
genera un certificado laboral en PDF con el logo de Ecodes, listo para firmar
y entregar. Hay dos botones, porque es lo que suele pedirse:

- **Sin salario** — para trámites donde solo hace falta acreditar el vínculo.
- **Con salario** — toma el salario base del último período de nómina
  registrado y lo imprime en números y en letras, como se acostumbra.

El documento incluye nombre completo, tipo y número de documento, cargo y
fecha de ingreso. Si la persona ya no está activa, el texto pasa a tiempo
pasado y agrega la fecha de retiro, que se toma de la novedad de tipo
**Salida**. Lo pueden emitir los dos roles: es una consulta, no modifica nada.

### 7.1. Datos de la empresa y de quien firma

El sistema **no se inventa** el NIT ni el nombre de quien firma. Esos datos se
configuran por variables de entorno (en Render, pestaña *Environment*; en
local, el archivo `.env`):

| Variable | Para qué sirve |
|----------|----------------|
| `EMPRESA_NOMBRE` | Razón social que encabeza el certificado |
| `EMPRESA_NIT` | NIT de la empresa |
| `EMPRESA_CIUDAD` | Ciudad de expedición |
| `EMPRESA_DIRECCION`, `EMPRESA_TELEFONO`, `EMPRESA_CORREO` | Membrete (opcionales) |
| `FIRMANTE_NOMBRE` | Quien firma el certificado |
| `FIRMANTE_CARGO` | Su cargo |

Mientras no se configuren, el PDF sale con textos como `[NIT POR CONFIGURAR]`
bien visibles, para que nadie lo entregue a medio llenar.

### 7.2. Si pides el certificado con salario y no hay nómina

El sistema responde con un mensaje explicando que esa persona no tiene nómina
registrada, en vez de emitir un certificado que no dice nada del salario.
Registra la nómina del período o genera el certificado sin salario.

---

## 8. Endpoints principales

| Método | Ruta                                          | Descripción                                   |
|--------|------------------------------------------------|------------------------------------------------|
| POST   | `/auth/login`                                  | Autenticación (usuario, contraseña, rol) → JWT |
| GET/POST/PUT/DELETE | `/empleados[/{id}]`               | CRUD de empleados                              |
| POST/DELETE | `/empleados/{id}/estudios[/{id}]`          | Formación académica                            |
| POST/DELETE | `/empleados/{id}/experiencia[/{id}]`       | Experiencia laboral                            |
| GET    | `/empleados/{id}/certificado-laboral`          | Certificado laboral en PDF (`?incluir_salario=`)|
| GET    | `/empleados/cumpleanos`                        | Próximos cumpleaños (parámetro `dias`)         |
| GET/POST/PUT/DELETE | `/proyectos[/{id}]`               | CRUD de proyectos                              |
| GET/POST/PUT/DELETE | `/participaciones[/{id}]`         | Asignación empleado-proyecto (valida ≤ 100%)   |
| GET/POST/PUT/DELETE | `/novedades[/{id}]`               | Ingresos, salidas, incapacidades, etc.         |
| GET/POST/DELETE | `/nomina[/{id}]` · `/nomina/resumen`  | Registros de nómina y resumen del mes          |
| GET    | `/alertas` · `/alertas/vacaciones` · `/alertas/sobreasignacion` | Alertas calculadas |
| GET    | `/exportar/excel`                              | Descarga el libro de Excel para Power BI       |

Todas las rutas (excepto `/auth/login`) requieren el header
`Authorization: Bearer <token>`. Las operaciones de escritura devuelven `403`
si el usuario autenticado tiene rol Administrativo.

---

## 9. Notas de diseño

- Paleta derivada del logo de Ecodes: verde hoja y azul acento sobre fondo
  blanco dominante, con soporte completo de modo oscuro (variables CSS para
  fondos, bordes, inputs y estados hover).
- Tipografía Space Grotesk (encabezados) + Inter (interfaz y datos), cargadas
  desde Google Fonts — si no hay conexión a internet, el navegador usa la
  fuente del sistema como respaldo.
- La ilustración de campo del login (`frontend/assets/login-scene.svg`) es un
  **placeholder ilustrado** que representa trabajo de restauración forestal;
  se recomienda reemplazarla por una fotografía real de campo de Ecodes antes
  de un despliegue productivo.
- El panel lateral (ficha de empleado/proyecto) tiene siempre la prioridad
  visual más alta; el menú lateral y la barra superior permanecen clicables
  mientras el panel está abierto, y este se cierra automáticamente al navegar.

---

## 10. Publicar el sistema (Render + Vercel)

El backend y el frontend se publican por separado, porque son cosas distintas:
el backend es un servidor que necesita base de datos, y el frontend son
archivos estáticos.

> **Por qué el backend no va en Vercel.** Vercel ejecuta funciones *serverless*
> (arrancan y mueren en cada petición) y no incluye PostgreSQL. Este backend es
> un servidor de larga vida con base de datos, así que va en Render, que tiene
> ambas cosas en su plan gratuito. Si lo intentas desplegar en Vercel tal cual,
> falla con `FUNCTION_INVOCATION_FAILED` porque no encuentra la base de datos.

### 10.1. Backend en Render

El archivo `render.yaml` en la raíz ya describe el servicio y la base de datos,
así que no hay que configurar nada a mano.

1. Entra a [render.com](https://render.com) y crea una cuenta (sirve la de GitHub).
2. **New > Blueprint** y selecciona este repositorio.
3. Render lee `render.yaml` y crea dos cosas: el servicio web `ecodes-th-api`
   y la base de datos PostgreSQL `ecodes-th-db`, ya conectadas entre sí.
   La `JWT_SECRET_KEY` se genera sola.
4. Espera a que el despliegue termine (la primera vez tarda unos minutos
   instalando pandas y las demás dependencias).
5. **Los datos de ejemplo se cargan solos.** El `buildCommand` ejecuta
   `python -m app.seed --solo-si-vacia`, que siembra la base únicamente si
   está vacía. En los despliegues siguientes detecta que ya hay información y
   no toca nada, así que lo que cargues de Ecodes no se pierde. No hace falta
   la pestaña **Shell** — que el plan gratuito de Render no incluye.
6. Comprueba que quedó bien abriendo `https://TU-SERVICIO.onrender.com/salud`.
   Debe responder:

   ```json
   {"status": "ok", "base_datos": "ok"}
   ```

   Si `base_datos` trae un error, el servicio está vivo pero no alcanza la base:
   revisa `DATABASE_URL` en la pestaña Environment.

> **Si el modelo cambia y la base ya existe.** SQLAlchemy crea las tablas que
> falten, pero **no agrega columnas nuevas a tablas que ya existen**. Cuando una
> versión trae campos nuevos (como el número de documento), la base desplegada
> se queda sin ellos y la aplicación falla al consultarlos. Para recrearla:
> agrega la variable `SEED_RESET=1` en la pestaña *Environment* de Render,
> redespliega, y **quítala apenas termine** — si se queda puesta, cada
> despliegue borrará los datos. Esto destruye lo que haya en la base, así que
> úsalo mientras sean datos de ejemplo.

> **Si alguna vez quieres volver al estado inicial**, ejecuta el seed sin el
> parámetro: `python -m app.seed`. Esa forma hace `drop_all()` — **borra todas
> las tablas** y las recrea con los datos de ejemplo. Úsala solo a propósito y
> nunca sobre datos reales.

La documentación interactiva de la API queda en `https://TU-SERVICIO.onrender.com/docs`.

### 10.2. Frontend en Vercel

1. Abre `frontend/js/config.js` y pega la URL que te dio Render:

   ```js
   const API_EN_PRODUCCION = "https://ecodes-th-api.onrender.com";
   ```

   Guarda y sube el cambio a GitHub.
2. En [vercel.com](https://vercel.com): **Add New > Project**, elige este
   repositorio y —esto es lo importante— en **Root Directory** selecciona la
   carpeta **`frontend`**, no la raíz del repositorio.
3. Framework Preset: **Other**. No hay que poner comandos de build.
4. Deploy.

> **Si ya tenías un proyecto de Vercel apuntando a `backend`**, no crees uno
> nuevo: entra a ese proyecto y ve a **Settings > General > Root Directory**,
> cámbialo de `backend` a `frontend` y guarda. Después, en **Deployments**, usa
> el menú **⋯ > Redeploy** del último despliegue. Mientras el Root Directory
> siga en `backend`, Vercel intentará ejecutar la API de Python como función
> serverless y cada despliegue fallará con
> `could not import "app/main.py"` / `FUNCTION_INVOCATION_FAILED`, sin importar
> los cambios que hagas en el código. En esa misma pantalla puedes renombrar el
> proyecto para que la URL no siga diciendo "backend".

**El orden importa.** Publica primero el backend en Render (9.1), luego pega su
URL en `frontend/js/config.js` y sube el cambio, y solo entonces despliega el
frontend. Si lo haces al revés verás la pantalla de login, pero no podrás
entrar porque no hay API a la cual conectarse.

El `CORS` ya está resuelto: `render.yaml` define
`CORS_ORIGIN_REGEX=https://.*\.vercel\.app`, que acepta tanto el dominio
definitivo como las URLs de vista previa que Vercel genera en cada despliegue.
Si más adelante usas un dominio propio, agrégalo a `CORS_ORIGINS` en Render.

### 10.3. Cosas que conviene saber del plan gratuito

| | |
|---|---|
| **El backend se duerme** | Render apaga los servicios gratuitos tras 15 minutos sin uso. La primera petición después de eso tarda **30–60 segundos** en responder mientras vuelve a arrancar. No está dañado; es el plan gratis. Si vas a mostrar el sistema en una sustentación, ábrelo unos minutos antes. |
| **La base de datos caduca** | Las bases PostgreSQL gratuitas de Render expiran a los 30 días. Para un proyecto de tesis alcanza, pero anótalo. |
| **Las contraseñas del seed son públicas** | `th / th12345` y `admin / admin12345` están en el repositorio. Sirven para la demo; si el sistema llegara a manejar datos reales de empleados, cámbialas antes. |

### 10.4. Otras opciones

- **Backend**: cualquier host compatible con ASGI (Uvicorn/Gunicorn) —
  Railway, Fly.io, un VPS con Docker, etc. Solo hay que configurar
  `DATABASE_URL` apuntando a PostgreSQL y una `JWT_SECRET_KEY` robusta.
- **Frontend**: al ser archivos estáticos, también funciona en Netlify,
  GitHub Pages, S3 + CloudFront o detrás del mismo proxy del backend. En
  cualquier caso, define la URL de la API en `frontend/js/config.js` e incluye
  el dominio del frontend en `CORS_ORIGINS`.
