# Ecodes · Sistema de Talento Humano

Sistema web de gestión de Talento Humano para **Ecodes**, empresa de consultoría y
gestión ambiental con operación en Colombia, Perú y Argentina (restauración
ecológica, compensación forestal, monitoreo de biodiversidad y gestión ambiental
corporativa). El mismo sistema atiende también a **Envsol**, la otra empresa
del grupo: es una sola instalación para las dos (ver sección 2).

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
│   │   ├── models.py        # Modelos ORM (Empresa, Empleado, Contrato, Proyecto, Participación...)
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

## 2. Varias empresas en un mismo sistema

Ecodes y Envsol comparten esta misma instalación: un solo servidor, una sola
base de datos, un solo sitio al que entra todo el equipo. Lo que cambia por
empresa es un solo dato — a cuál pertenece cada empleado y cada proyecto —,
no el sistema completo.

- **Cada empleado y cada proyecto tiene una empresa asignada.** Se elige en
  su formulario, en un campo obligatorio.
- **El filtro "Todas las empresas"** en Empleados y Proyectos deja ver todo
  junto o separar por empresa, según haga falta.
- **El certificado laboral usa los datos de la empresa del empleado**, no
  una configuración fija: el de alguien de Envsol sale con el NIT y la firma
  de Envsol, no con los de Ecodes.
- **Las empresas se administran desde la propia aplicación**, en
  Empleados → **Empresas** (arriba de la tabla). Ahí se agregan, editan o
  desactivan, sin tocar el servidor ni ninguna variable de entorno. Solo el
  rol Talento Humano puede crear o editar; el rol Administrativo puede
  verlas.
- **Cada participación, cada proyecto, cada registro de nómina** sigue
  perteneciendo a una sola persona o a un solo proyecto — la empresa no
  cambia esas reglas, solo agrupa. Una persona de Envsol puede trabajar en
  un proyecto de Ecodes si así se le asigna: el sistema no lo impide, porque
  en la práctica el equipo sí colabora entre las dos empresas.

**Logo por empresa en el certificado.** El sistema busca un archivo
`backend/app/assets/logo_<nombre-en-minusculas-y-guiones-bajos>.jpg` (por
ejemplo, para "Envsol S.A.S." sería `logo_envsol_s_a_s.jpg`); si no lo
encuentra, usa el logo de Ecodes como respaldo. No hay que escribir código
para agregarlo: basta con dejar el archivo en esa carpeta.

**Para la hoja de indicadores en Power BI**: el Excel exportado (`Exportar a
Excel` en cualquier pantalla) trae una hoja `empresas` y una columna
`empresa_id` / `empresa_nombre` en `empleados` y en `proyectos`, así que los
tres indicadores (rotación, costos laborales, ausentismo) se pueden filtrar
o agrupar por empresa sin tocar nada más.

---

## 3. Ficha del empleado: datos personales e historial contractual

La ficha de cada empleado (panel lateral de la pantalla **Empleados**) tiene,
además de lo descrito arriba, dos secciones más:

### 3.1. Información personal y organizacional

Ciudad, estado civil, contacto de emergencia (nombre, parentesco y teléfono),
área y jefe inmediato. El jefe inmediato se elige entre los demás empleados
del sistema (es la misma tabla `empleados`, con una referencia a sí misma),
así que con este campo se arma un organigrama sin necesidad de otra pantalla.
Todos estos campos son opcionales.

### 3.2. Historial contractual

Cada empleado puede tener varios contratos a lo largo del tiempo — por
ejemplo, uno a término fijo que termina y otro indefinido que lo reemplaza
cuando lo ascienden. El historial contractual es, sencillamente, la lista de
esos contratos, del más reciente al más antiguo. Cada uno guarda:

| Campo | Notas |
|-------|-------|
| Tipo de contrato | Término fijo, término indefinido, obra o labor, prestación de servicios o aprendizaje |
| Fecha inicial / final | La fecha final queda vacía en los contratos a término indefinido |
| Duración | **No se guarda**: se calcula a partir de las dos fechas de arriba, para que nunca quede desincronizada de ellas |
| Período de prueba | En días |
| Cargo contractual | El cargo que dice el contrato — puede no coincidir con el cargo actual de la persona si hubo un ascenso que todavía no se formaliza |
| Salario | El que estipula ese contrato en particular |
| Proyecto y centro de costos | A qué proyecto y centro de costos se imputa |
| Modalidad | Presencial, híbrido o remoto |
| Estado | Activo, vencido, suspendido o terminado |

**Prórrogas y otrosí.** No son contratos nuevos, son modificaciones de uno
existente, y quedan anidadas bajo el contrato que modifican. Una **prórroga**
trae su propia fecha final, que se aplica de una vez al contrato: así el
historial explica por qué cambió esa fecha, en vez de que el cambio quede
silencioso. Un **otrosí** es cualquier otro cambio formal (un ascenso, un
ajuste salarial) que se deja anotado sin modificar las fechas.

> Un contrato con fecha final vencida que nadie ha marcado como "Vencido"
> aparece con una insignia de aviso en la interfaz (campo `vencido` de la
> API) — es solo un aviso, no cambia el estado guardado por su cuenta.

## 4. Solicitudes: flujo de aprobación

La pantalla **Solicitudes** registra 13 tipos de trámites del empleado:
vacaciones, incapacidades, permisos, licencias remuneradas y no remuneradas,
calamidad doméstica, trabajo remoto, horas extras, ausencias, suspensiones,
cambios salariales, cambios de cargo y cambios de proyecto.

Toda solicitud sigue el mismo flujo de dos pasos:

**Empleado → Jefe inmediato → Talento Humano → aprobada / rechazada**

El sistema no tiene cuentas de usuario por empleado — igual que el resto de
la aplicación, es Talento Humano quien registra lo que ocurrió en cada
etapa, no un portal de autoservicio. Primero se deja la decisión del jefe
inmediato del empleado (el mismo campo `jefe_inmediato` usado en la ficha
del empleado, ver sección 3.1); solo si la aprueba, la solicitud pasa a
Talento Humano para la decisión final. Si el jefe la **rechaza, ahí
termina**: la API devuelve `409` si se intenta registrar la decisión de
Talento Humano sobre una solicitud que el jefe todavía no aprobó o que ya
rechazó.

| Campo | Notas |
|-------|-------|
| Tipo | Uno de los 13 tipos listados arriba |
| Fecha de la solicitud | Se asigna automáticamente al crearla |
| Fecha inicial / final | La fecha final queda vacía en tipos sin rango (p. ej. horas extras de un solo día) |
| Días solicitados | **No se guarda**: se calcula a partir de las dos fechas, igual que la duración de un contrato |
| Horas | Solo aplica a "Horas extras" |
| Valor propuesto | Texto libre para "Cambio salarial" y "Cambio de cargo" (p. ej. "De $4.200.000 a $4.800.000") |
| Proyecto propuesto | Solo aplica a "Cambio de proyecto" |
| Motivo | Obligatorio |
| Decisión del jefe / de Talento Humano | Estado (pendiente, aprobado, rechazado), comentario opcional y fecha de respuesta, por separado para cada etapa |

**Si el empleado no tiene jefe inmediato asignado** (por ejemplo, la persona
en la cima del organigrama), la pantalla lo indica como "sin jefe asignado"
pero no bloquea el flujo: Talento Humano igual puede registrar esa etapa.

**Único efecto automático.** Aprobar unas **vacaciones** en la etapa de
Talento Humano descuenta los días solicitados del saldo pendiente del
empleado y actualiza su fecha de última toma. Los demás 12 tipos —
permisos, licencias, cambios de cargo o de salario, cambio de proyecto,
etc. — quedan solo como el registro de la decisión; aplicar el cambio real
en el contrato, el salario o la asignación de proyecto sigue siendo una
acción aparte de Talento Humano en las pantallas correspondientes. Esto es
intencional: evita que una solicitud modifique datos de nómina o del
contrato de forma silenciosa.

## 5. Organigrama y alertas del expediente

### 5.1. Organigrama: áreas, cargos, jefaturas, dependencias, equipos y vacantes

La pantalla **Organigrama** tiene cinco vistas:

- **Áreas**: catálogo formal de las áreas de la empresa, con jerarquía entre
  ellas (`área padre`, lo que arma las **Dependencias**) y un responsable
  opcional (el jefe del área). Es un catálogo aparte del campo de texto libre
  `área` que ya tiene cada empleado en su ficha (sección 3.1): no se migra a
  nadie automáticamente, a propósito, para no obligar a reasignar empleados
  ya existentes. El número de empleados que muestra cada área se calcula por
  coincidencia de nombre contra ese campo de texto, no por una relación
  guardada.
- **Cargos**: catálogo formal de cargos, también con jerarquía
  (`cargo superior`) e independiente del texto libre `nombre_cargo` de cada
  empleado, por la misma razón que las áreas. Sirve sobre todo para definir
  **Vacantes**.
- **Vacantes**: posiciones abiertas, con área, cargo, motivo, salario
  ofrecido, fechas de apertura/cierre y estado (Abierta, En proceso,
  Cerrada). Llenar una vacante no crea el empleado automáticamente: Talento
  Humano lo registra como siempre en la pantalla de Empleados y simplemente
  cierra la vacante aquí.
- **Jefaturas y equipos**: árbol de solo lectura armado a partir del jefe
  inmediato que ya tiene cada empleado (el mismo campo de la sección 3.1) —
  cada persona con quienes le reportan directamente, de forma recursiva. No
  es una pantalla aparte de datos: es la misma información de siempre, vista
  como árbol.
- **Dependencias**: igual que Jefaturas pero para la jerarquía de Áreas, de
  la(s) raíz(ces) hacia las subáreas.

### 5.2. Alertas del expediente del empleado

Son ocho alertas nuevas, agrupadas bajo "Expediente del empleado" en la
pantalla de Alertas, que se suman a las que ya existían (vacaciones por
vencer, sobre-asignación, nómina y novedades sin procesar):

| Alerta | De dónde sale |
|--------|----------------|
| Contrato próximo a vencer | `fecha_fin` del contrato activo, dentro de 30 días |
| Período de prueba por finalizar | `fecha_inicio + periodo_prueba_dias` del contrato, dentro de 10 días |
| Certificación próxima a vencer | `fecha_vencimiento` de una certificación del empleado, dentro de 30 días |
| Documento faltante | Compara los documentos cargados contra los tipos obligatorios (hoja de vida, cédula, certificado EPS, certificado bancario, antecedentes judiciales) |
| Evaluación pendiente | Evaluación de desempeño sin `fecha_realizada` |
| Capacitación pendiente | Capacitación sin `fecha_realizada` |
| Examen médico próximo | `fecha_proximo` de un examen médico, dentro de 30 días |
| Incapacidad activa | Una solicitud de tipo Incapacidad ya aprobada por Talento Humano, vigente hoy (ver sección 4) |

Certificaciones, documentos, evaluaciones, capacitaciones y exámenes médicos
se registran desde la propia ficha del empleado (igual que Formación
académica o Experiencia laboral): son sub-listas de la ficha, no pantallas
aparte, y cada una se agrega o se elimina ahí mismo.

### 5.3. Aniversarios laborales

Al crear un empleado, la **fecha de ingreso** es un campo obligatorio del
formulario (`fecha_ingreso`, ver sección 3) — de ahí sale tanto la
antigüedad que se muestra en su ficha como esta alerta. Treinta días antes
de que el empleado cumpla 1 año, 2 años, 3 años, etc. con la empresa
(contados desde esa fecha), aparece una alerta "Aniversario laboral" en la
pantalla de Alertas, con cuántos años cumple y en qué fecha exacta. Se
calcula igual que los cumpleaños de la pantalla Inicio (mismo manejo del
29 de febrero), pero sobre `fecha_ingreso` en vez de `fecha_nacimiento`, y
sin alertar antes de que se cumpla el primer año.

### 5.4. Inicio: tablero con KPIs, cumpleaños y alertas urgentes

**Inicio** es la pantalla de entrada tras el login (reemplaza a Empleados
como pantalla por defecto) y reúne en un solo lugar lo que antes estaba
repartido:

- **KPIs básicos**: empleados activos (sobre el total), proyectos activos,
  alertas pendientes (la suma de todas las categorías de la pantalla
  Alertas) y vacantes abiertas o en proceso (sección 5.1).
- **Próximos cumpleaños**: el mismo widget que antes vivía en Empleados,
  calculado sobre `fecha_nacimiento` para los próximos ~45 días (empleados
  activos únicamente), con la etiqueta "Hoy"/"Mañana" cuando corresponde.
- **Alertas próximas a atender**: una vista previa de hasta seis alertas,
  tomadas de todas las categorías (vacaciones, sobre-asignación, nómina,
  novedades sin procesar, expediente del empleado y aniversarios) y
  ordenadas por nivel de severidad (crítico, alerta, info), con un enlace
  "Ver todas las alertas" que lleva a la pantalla completa de Alertas
  (sección 5.2).

La pantalla de **Empleados** conserva solo la tabla filtrable de personal;
los KPIs y el widget de cumpleaños que antes mostraba se trasladaron a
Inicio para que Empleados vuelva a ser una pantalla enfocada en buscar y
filtrar personal, no un dashboard.

## 6. Parámetros laborales y legales (motor de nómina colombiana)

> **⚠️ Advertencia importante.** Este módulo es la primera fase de un motor
> de nómina colombiano completo (cálculo de incapacidades, vacaciones,
> prestaciones sociales, liquidación de contrato, indemnización, seguridad
> social y PILA vienen en fases posteriores). Lo que existe hoy es el
> **motor de configuración legal** — la base de la que dependerán esas
> fases — ya sembrado con un catálogo inicial de parámetros. **Ninguno de
> esos valores debe usarse para una nómina real todavía**: todos se cargan
> con `pendiente_verificacion = true` a propósito, porque son la mejor
> estimación disponible al construir este módulo (citando la norma que se
> cree aplicable) pero no se pudieron confirmar contra una fuente oficial
> en ese momento — en particular el SMLMV y la UVT de 2026 (dependen de
> decretos de diciembre de 2025) y varias fechas exactas de la Ley 2466 de
> 2025 (reforma laboral). Un profesional de nómina/legal colombiano debe
> revisar y confirmar (o corregir) cada parámetro desde esta pantalla antes
> de que cualquier cálculo futuro se apoye en ellos.

### 6.1. Por qué un motor de parámetros, y no constantes en el código

Todo el resto del sistema de nómina colombiana que se construya en fases
siguientes (incapacidades, vacaciones, prestaciones, liquidación,
indemnización, seguridad social) debe leer sus porcentajes, topes y
fórmulas de aquí — nunca escribirlos directamente en Python. La razón es
que la legislación laboral colombiana cambia por tramos de vigencia: por
ejemplo, el recargo dominical/festivo subió de 75% a 80%, luego a 90% y
llegará a 100%, cada tramo en una fecha distinta (Ley 2466 de 2025). Una
nómina de 2026 debe seguir mostrando el 90% con el que se calculó, aunque
en 2027 la norma ya diga 100%. Por eso cada parámetro se guarda como una o
varias **vigencias** con su propio rango de fechas, y nunca se sobrescribe
una vigencia ya cerrada — si una norma cambia, se cierra la vigencia
abierta y se crea una nueva (automáticamente, al registrar la siguiente).

### 6.2. Pantalla: Configuración > Parámetros laborales y legales

Cada parámetro tiene: nombre, código (identificador único, ej.
`recargo_dominical_festivo`), descripción, valor, unidad (porcentaje,
pesos, días, horas, semanas, meses, número, u "hora del día" para los
horarios de jornada nocturna), fecha inicial y final de vigencia, año,
norma relacionada, observaciones, estado activo/inactivo, si está
pendiente de verificación legal, y quién hizo el último cambio y cuándo.

La pantalla filtra por código, año y estado de verificación, y muestra un
aviso con cuántos parámetros siguen pendientes de confirmar. Cada fila
indica si su vigencia está **Vigente**, **Histórica** (ya cerrada) o
**Futura** (todavía no empieza).

- **Nueva vigencia**: crea una fila nueva. Si ya existe una vigencia
  abierta (sin fecha final) para el mismo código que empieza antes, el
  sistema la cierra automáticamente el día anterior al inicio de la
  nueva — así nunca compiten dos vigencias por la misma fecha, y la
  anterior queda intacta como historia. Si la nueva vigencia se cruza con
  una vigencia **ya cerrada** (histórica), la operación se rechaza
  (`409`): no se permite alterar cómo se calculó algo en el pasado.
- **Editar**: solo cambia metadatos (nombre, descripción, norma,
  observaciones, estado, verificación) — nunca el valor ni las fechas. Si
  el valor realmente cambió, se crea una vigencia nueva en vez de editar
  la existente.
- **Eliminar**: solo se puede borrar la vigencia más reciente de su
  código (equivale a deshacer la última creación), y si al crearla se
  había cerrado automáticamente la vigencia anterior, esa se reabre. Esto
  evita dejar huecos en mitad del historial normativo.

### 6.3. Cómo lo usan los cálculos (`utils.obtener_parametro`)

Internamente, cualquier función de cálculo que necesite un valor legal
llama a `obtener_parametro(db, "codigo", fecha)`, que filtra por código,
`activo = true`, y la vigencia cuyo rango de fechas incluya `fecha` —
nunca toma "la fila más reciente" a secas. Si no existe ninguna vigencia
configurada para ese código en esa fecha, lanza un error explícito
(`ParametroLegalNoEncontrado`) en vez de asumir un valor por defecto: un
cálculo salarial no debe adivinar un porcentaje que nadie configuró.

### 6.4. Catálogo inicial sembrado

El script de seed carga ~59 vigencias repartidas en estos códigos (todas
`pendiente_verificacion = true`):

| Grupo | Códigos |
|-------|---------|
| Salario y jornada | `salario_minimo`, `auxilio_transporte`, `jornada_semanal_maxima`, `horas_mensuales_calculo` |
| Seguridad social | `porcentaje_salud_empleado/empleador`, `porcentaje_pension_empleado/empleador`, `fondo_solidaridad_*_smlmv` (tabla por tramos de IBC), `caja_compensacion`, `sena`, `icbf`, `exoneracion_parafiscales_umbral_smlmv`, `arl_riesgo_i` a `arl_riesgo_v` |
| Jornada nocturna y recargos | `hora_inicio_jornada_nocturna`, `hora_fin_jornada_nocturna`, `recargo_nocturno`, `recargo_hora_extra_diurna/nocturna`, `recargo_dominical_festivo` (con sus 4 tramos históricos/vigentes/futuros), `recargo_hora_extra_dominical_diurna/nocturna` |
| Prestaciones sociales | `porcentaje_cesantias`, `porcentaje_intereses_cesantias`, `porcentaje_prima_servicios`, `dias_vacaciones_anuales` |
| Licencias | `licencia_maternidad_semanas`, `licencia_paternidad_dias`, `licencia_luto_dias`, `calamidad_domestica_dias_referencia` |
| Incapacidades | `incapacidad_general_dias_empresa`, `incapacidad_general_porcentaje`, `incapacidad_general_porcentaje_dias91_180`, `incapacidad_laboral_porcentaje` |
| Tributario y topes | `uvt_valor`, `tope_ibc_salud_pension_smlmv` |
| Indemnización | `indemnizacion_salario_bajo/alto_primer_anio_dias`, `indemnizacion_salario_bajo/alto_adicional_anio_dias`, `indemnizacion_umbral_salario_alto_smlmv` |

La tabla de retención en la fuente (progresiva en UVT) y las reglas
completas de indemnización por tipo de contrato/causal se dejan para la
fase de Nómina e Indemnización, respectivamente — aquí solo vive el
parámetro base (`uvt_valor`) del que dependerán.

## 7. Requisitos

- Python 3.11+
- Docker y Docker Compose (para PostgreSQL local) — o una instancia de PostgreSQL existente
- Un navegador moderno (no requiere Node.js ni build step para el frontend)

---

## 8. Puesta en marcha — Backend

### 8.1. Levantar PostgreSQL

```bash
docker compose up -d
```

Esto crea una base de datos `ecodes_th` en `localhost:5432` con usuario/clave
`ecodes` / `ecodes` (ver `docker-compose.yml`).

### 8.2. Configurar variables de entorno

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

### 8.3. Instalar dependencias y crear el entorno virtual

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 8.4. Poblar la base de datos con datos de ejemplo

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

### 8.5. Iniciar la API

```bash
uvicorn app.main:app --reload --port 8000
```

La API queda disponible en `http://localhost:8000` y la documentación
interactiva (Swagger) en `http://localhost:8000/docs`.

---

## 9. Puesta en marcha — Frontend

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

## 10. Flujo de uso

1. Inicia sesión en `index.html` seleccionando el rol (Talento Humano o
   Administrativo) e ingresando usuario/contraseña.
2. La pantalla de entrada es **Inicio**, un dashboard con KPIs básicos
   (empleados activos, proyectos activos, alertas pendientes y vacantes
   abiertas), el widget de próximos cumpleaños (siguientes ~45 días) y una
   vista previa de las alertas más urgentes con un enlace directo a la
   pantalla completa de Alertas (ver sección 5.4).
3. En **Empleados** se filtra y busca el personal; haz clic en una fila para
   abrir la ficha completa del empleado (panel lateral): información
   general, información personal y organizacional (ciudad, estado civil,
   contacto de emergencia, área, jefe inmediato), afiliaciones y datos
   bancarios (banco, EPS, AFP, ARL y su nivel de riesgo, caja de
   compensación, fondo de cesantías, tipo y número de cuenta), historial
   contractual (ver sección 3), formación académica, experiencia laboral,
   proyectos asignados (con su % de dedicación), vacaciones e historial de
   movimientos.
4. En **Proyectos** puedes crear proyectos y gestionar el equipo asignado con
   su % de dedicación — la suma de participación de una persona en todos sus
   proyectos nunca puede superar el 100% (validado en frontend y backend).
5. **Novedades** registra ingresos, salidas, cambios de proyecto e
   incapacidades. Una novedad de tipo "Salida" marca automáticamente al
   empleado como Inactivo.
6. **Solicitudes** registra vacaciones, permisos, licencias, calamidades,
   trabajo remoto, horas extras, ausencias, suspensiones y cambios
   salariales/de cargo/de proyecto, con el flujo de aprobación
   Empleado → Jefe inmediato → Talento Humano (ver sección 4).
7. **Organigrama** administra áreas, cargos y vacantes, y muestra las
   jefaturas/equipos y las dependencias entre áreas como árboles de solo
   lectura (ver sección 5.1).
8. **Nómina** muestra el resumen del mes (total, próximo pago, novedades sin
   procesar) y el detalle por empleado con los auxilios calculados
   automáticamente (ver "Reglas de auxilios" más abajo).
9. **Alertas** agrupa vacaciones por vencer, sobre-asignación de personal,
   nómina/pagos próximos, novedades sin procesar y las ocho alertas del
   expediente del empleado (contrato por vencer, período de prueba,
   certificaciones, documentos, evaluaciones, capacitaciones, exámenes
   médicos e incapacidad activa — ver sección 5.2).
10. **Configuración** administra los parámetros laborales y legales del
    motor de nómina colombiana (ver sección 6) — por ahora solo visible
    como pantalla independiente, todavía no conectada a un cálculo de
    nómina real.
11. El botón **"Exportar a Excel"** (visible en todas las pantallas) descarga
    un libro con una hoja por tabla (`empleados`, `estudios`, `experiencia`,
    `proyectos`, `participaciones`, `nomina`, `novedades`, `solicitudes`,
    `areas`, `cargos`, `vacantes`, `certificaciones`, `documentos`,
    `evaluaciones`, `capacitaciones`, `examenes_medicos`,
    `parametros_legales`), con columnas en `snake_case` y los mismos `id`
    como llaves, listo para conectar en Power BI y construir las
    relaciones e indicadores de rotación, costos laborales prorrateados y
    ausentismo.

---

## 11. Reglas de liquidación de nómina

Todas las tasas y valores viven en un solo lugar (`backend/app/utils.py`,
función `liquidar_nomina`) y los usan tanto el endpoint de nómina como el
script de seed, así que nunca se desincronizan.

### 11.1. Devengado

| Concepto | Valor 2026 | Regla |
|----------|-----------:|-------|
| Salario mínimo (SMLMV) | $1.750.905 | Referencia legal |
| Tope auxilio de transporte | $3.501.810 | 2 SMLMV |
| **Auxilio de transporte** | **$249.095** | Obligatorio por ley **solo** para quien devengue hasta 2 SMLMV. No depende del tipo de cargo. Si se deja en `0` al registrar la nómina, el sistema lo aplica automáticamente. |
| **Auxilio de movilidad** | lo define Ecodes | Auxilio interno para roles de campo. **No es salarial ni prestacional**: no entra en ninguna base, solo suma al costo. Al ser una decisión de la empresa, **se registra persona a persona** y el sistema nunca lo calcula ni lo asume. |

### 11.2. Deducciones al trabajador

| Concepto | Tasa | Base |
|----------|-----:|------|
| Salud | 4% | Salario base |
| Pensión | 4% | Salario base |

El campo `descuentos` queda libre para descuentos adicionales (préstamos,
embargos, etc.); salud y pensión se calculan aparte.

### 11.3. Costo adicional que asume el empleador

| Concepto | Tasa mensual | Base | Equivalente anual |
|----------|-------------:|------|-------------------|
| Prima de servicios | 8,33% | Salario + auxilio de transporte | 1 salario al año |
| Cesantías | 8,33% | Salario + auxilio de transporte | 1 salario al año |
| Intereses de cesantías | 1,00% | Salario + auxilio de transporte | 12% anual sobre cesantías |
| Provisión de vacaciones | 4,17% | Salario base | 15 días hábiles al año |
| Pensión (empleador) | 12% | Salario base | — |
| ARL (la paga 100% el empleador) | Según clase de riesgo (ver tabla) | Salario base | Campo `nivel_riesgo_arl` del empleado |

**Clase de riesgo de la ARL.** Se registra en la ficha de cada empleado (sección
"Afiliaciones y datos bancarios"), no se adivina por el cargo:

| Nivel | Tasa | Ejemplos típicos |
|-------|-----:|-------------------|
| I | 0,522% | Trabajo de oficina |
| II | 1,044% | Riesgo bajo |
| III | 2,436% | Riesgo medio |
| IV | 4,350% | Riesgo alto |
| V | 6,960% | Trabajo de campo, forestal |

Si una persona no tiene el nivel registrado (bases creadas antes de este
campo), el cálculo cae de vuelta a clasificarla por palabras clave del cargo
("campo", "forestal", "restauración", "monitoreo" → riesgo V; el resto →
riesgo I), para no dejar de calcular algo razonable.

**Bases de cálculo** (es donde se equivocan la mayoría de las hojas de Excel):

- El auxilio de transporte **sí** es base para prima, cesantías e intereses,
  pero **no** para vacaciones ni para seguridad social.
- El auxilio de movilidad no entra en ninguna base.

> **Exoneración de la Ley 1607 de 2012**: salud del empleador (8,5%), caja de
> compensación (4%), SENA (2%) e ICBF (3%) están en `0.0`. Si Ecodes no está
> exonerada, basta con poner las tasas reales en esas constantes
> (`TASA_SALUD_EMPLEADOR`, etc. en `backend/app/utils.py`) y el cálculo las
> incluye automáticamente.

### 11.3.1. Afiliaciones y datos bancarios

Además de lo que entra en el cálculo de nómina, la ficha del empleado guarda
los datos que Contabilidad necesita para pagarle y afiliarlo: EPS, AFP,
ARL (aseguradora), caja de compensación, fondo de cesantías, tipo y número de
cuenta. Son campos de texto libre (no hay una lista cerrada de entidades,
porque cambian y varían según el país), opcionales para no bloquear el
registro de alguien mientras se termina de recolectar su información.

### 11.4. Periodicidad de pago: mensual y quincenal

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

### 11.5. Por qué importa para los indicadores

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

## 12. Certificado laboral en PDF

Desde la ficha de cada empleado (panel lateral, sección **Documentos**) se
genera un certificado laboral en PDF con el logo y los datos de SU empresa
(Ecodes, Envsol, u otra — ver sección 2), listo para firmar y entregar. Antes
de generarlo se elige:

- **Fecha de expedición** — la fecha que queda impresa en "se expide en...".
  Por defecto es hoy, pero se puede cambiar a una fecha anterior (por ejemplo,
  para que coincida con la fecha de una solicitud ya radicada). No puede ser
  futura ni anterior a la fecha de ingreso de la persona.
- **Sin salario** — para trámites donde solo hace falta acreditar el vínculo.
- **Con salario** — toma el salario base del último período de nómina
  registrado y lo imprime en números y en letras, como se acostumbra.

El documento incluye nombre completo, tipo y número de documento, cargo y
fecha de ingreso. Si la persona ya no está activa, el texto pasa a tiempo
pasado y agrega la fecha de retiro, que se toma de la novedad de tipo
**Salida**. Lo pueden emitir los dos roles: es una consulta, no modifica nada.

### 12.1. Datos de la empresa y de quien firma

El sistema **no se inventa** el NIT ni el nombre de quien firma: esos datos
salen de la empresa asignada al empleado, administrada desde Empleados >
Empresas (ver sección 2), no de variables de entorno. Si la persona no tiene
una empresa asignada, el sistema avisa y no genera el certificado hasta que
se le asigne una.

Las variables `EMPRESA_*` y `FIRMANTE_*` del `.env` solo importan para la
primera empresa que se crea al sembrar la base vacía (ver `.env.example`).

### 12.2. Si pides el certificado con salario y no hay nómina

El sistema responde con un mensaje explicando que esa persona no tiene nómina
registrada, en vez de emitir un certificado que no dice nada del salario.
Registra la nómina del período o genera el certificado sin salario.

---

## 13. Endpoints principales

| Método | Ruta                                          | Descripción                                   |
|--------|------------------------------------------------|------------------------------------------------|
| POST   | `/auth/login`                                  | Autenticación (usuario, contraseña, rol) → JWT |
| GET/POST/PUT/DELETE | `/empresas[/{id}]`                | CRUD de empresas (Ecodes, Envsol, etc.)        |
| GET/POST/PUT/DELETE | `/empleados[/{id}]`               | CRUD de empleados                              |
| POST/DELETE | `/empleados/{id}/estudios[/{id}]`          | Formación académica                            |
| POST/DELETE | `/empleados/{id}/experiencia[/{id}]`       | Experiencia laboral                            |
| GET/POST/PUT/DELETE | `/contratos[/{id}]`               | Historial contractual (`?empleado_id=` para filtrar) |
| POST    | `/contratos/{id}/modificaciones`               | Agregar una prórroga o un otrosí               |
| DELETE  | `/modificaciones/{id}`                         | Eliminar una prórroga o un otrosí              |
| GET    | `/empleados/{id}/certificado-laboral`          | Certificado laboral en PDF (`?incluir_salario=&fecha_expedicion=`)|
| GET    | `/empleados/cumpleanos`                        | Próximos cumpleaños (parámetro `dias`)         |
| GET/POST/PUT/DELETE | `/proyectos[/{id}]`               | CRUD de proyectos                              |
| GET/POST/PUT/DELETE | `/participaciones[/{id}]`         | Asignación empleado-proyecto (valida ≤ 100%)   |
| GET/POST/PUT/DELETE | `/novedades[/{id}]`               | Ingresos, salidas, incapacidades, etc.         |
| GET/POST/DELETE | `/solicitudes[/{id}]`             | Solicitudes de los 13 tipos (`?empleado_id=&tipo=&estado_jefe=&estado_th=` para filtrar) |
| POST   | `/solicitudes/{id}/decision-jefe`              | Registra la decisión del jefe inmediato (`409` si ya decidió) |
| POST   | `/solicitudes/{id}/decision-th`                | Registra la decisión de Talento Humano (`409` si el jefe no la aprobó aún, o si ya decidió) |
| GET/POST/PUT/DELETE | `/areas[/{id}]`                   | Catálogo de áreas (`?empresa_id=` para filtrar) |
| GET/POST/PUT/DELETE | `/cargos[/{id}]`                  | Catálogo de cargos (`?empresa_id=&area_id=` para filtrar) |
| GET/POST/PUT/DELETE | `/vacantes[/{id}]`                | Vacantes abiertas (`?empresa_id=&estado=` para filtrar) |
| GET    | `/organigrama/jefaturas`                       | Árbol de jefaturas/equipos, derivado del jefe inmediato de cada empleado |
| GET    | `/organigrama/dependencias`                    | Árbol de dependencias entre áreas              |
| POST/DELETE | `/empleados/{id}/certificaciones[/{id}]`   | Certificaciones del empleado                   |
| POST/DELETE | `/empleados/{id}/documentos[/{id}]`        | Documentos del expediente                      |
| POST/DELETE | `/empleados/{id}/evaluaciones[/{id}]`      | Evaluaciones de desempeño                      |
| POST/DELETE | `/empleados/{id}/capacitaciones[/{id}]`    | Capacitaciones                                 |
| POST/DELETE | `/empleados/{id}/examenes-medicos[/{id}]`  | Exámenes médicos ocupacionales                 |
| GET/POST/PUT/DELETE | `/parametros-legales[/{id}]`      | Vigencias de parámetros legales (`?codigo=&anio=&activo=&pendiente_verificacion=` para filtrar) |
| GET    | `/parametros-legales/codigos`                  | Catálogo de códigos ya usados (para selectores) |
| GET    | `/parametros-legales/{codigo}/vigente`         | La vigencia que aplica en una fecha (`?fecha=`, por defecto hoy) |
| GET/POST/DELETE | `/nomina[/{id}]` · `/nomina/resumen`  | Registros de nómina y resumen del mes          |
| GET    | `/alertas` · `/alertas/vacaciones` · `/alertas/sobreasignacion` · `/alertas/expediente` · `/alertas/aniversarios` | Alertas calculadas |
| GET    | `/exportar/excel`                              | Descarga el libro de Excel para Power BI       |

Todas las rutas (excepto `/auth/login`) requieren el header
`Authorization: Bearer <token>`. Las operaciones de escritura devuelven `403`
si el usuario autenticado tiene rol Administrativo.

---

## 14. Notas de diseño

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

## 15. Instalación en el servidor de Ecodes (recomendada)

Esta es la forma en que el sistema queda funcionando **dentro de la empresa**:
en el servidor local, sin nube, y accesible desde los computadores de la
oficina por el navegador. Los datos de los empleados nunca salen de Ecodes.

### 15.1. Cómo queda montado

```
    Servidor de la oficina                    Computadores del equipo
  ┌────────────────────────────┐
  │  PostgreSQL  (los datos)   │            Talento Humano  ─┐
  │  Aplicación  (puerto 8000) │ ←── red ── Administración  ─┼→ el navegador
  │  Carpeta "respaldos"       │            Gerencia        ─┘
  └────────────────────────────┘
```

Un solo programa sirve la API **y** las pantallas, así que no hay nada que
instalar en los computadores del equipo: entran a
`http://IP-DEL-SERVIDOR:8000` desde Chrome o Edge y listo.

### 15.2. Instalación

En el servidor hace falta **Docker Desktop** (Windows) o **Docker Engine**
(Linux). Es lo único que se instala a mano.

1. Copia la carpeta del proyecto al servidor.
2. Duplica `.env.servidor.example` y renómbralo como `.env`. Ábrelo con el
   Bloc de notas y llénalo: contraseña de la base, clave de sesiones, NIT de
   la empresa y nombre de quien firma los certificados.
3. Abre una terminal en esa carpeta y ejecuta:

   ```bash
   docker compose up -d
   ```

   La primera vez tarda unos minutos. Levanta la base de datos, crea las
   tablas y carga los datos de ejemplo.
4. Averigua la IP del servidor (`ipconfig` en Windows, `ip a` en Linux) y
   entra desde otro computador a `http://ESA-IP:8000`.

Para que arranque solo cuando se prenda el servidor no hay que hacer nada
más: `restart: unless-stopped` en `docker-compose.yml` se encarga.

| Qué necesitas | Comando |
|---------------|---------|
| Apagar el sistema | `docker compose down` (los datos se conservan) |
| Volver a encenderlo | `docker compose up -d` |
| Ver si está funcionando | `docker compose ps` |
| Ver qué está pasando | `docker compose logs -f app` |
| Actualizar a una versión nueva | `docker compose up -d --build` |

### 15.3. Respaldos

Los datos viven dentro de Docker, no en una carpeta suelta, así que
copiar archivos no alcanza: hay que generar el respaldo.

- **Windows**: doble clic en `respaldar.bat`
- **Linux**: `./respaldar.sh`

Cada respaldo queda como un archivo `.sql` con la fecha en el nombre, dentro
de la carpeta **`respaldos`**. Esa carpeta sí se puede copiar como cualquier
otra, al mismo sitio donde la empresa guarda sus respaldos.

**Para que corra solo todos los días** (Windows): Programador de tareas →
Crear tarea básica → Diariamente → apuntar a `respaldar.bat`.

Para volver atrás: `./restaurar.sh respaldos/ecodes_th_2026-09-22_1900.sql`.
Ojo, reemplaza **todo** lo que haya en la base.

> **Prueba el respaldo antes de confiar en él.** Un respaldo que nunca se
> restauró no es un respaldo. Haz uno, restáuralo y verifica que los datos
> estén completos.

### 15.4. Seguridad en la red de la empresa

- **El sistema no va expuesto a internet.** Solo debe verse dentro de la red
  de la oficina. Si alguien necesita entrar desde afuera, que sea por la VPN
  de la empresa, no abriendo el puerto 8000 en el router.
- **Cambia las contraseñas de ejemplo.** Los usuarios `th` y `admin` del seed
  son públicos porque están en este repositorio. Antes de cargar datos reales,
  cámbialas.
- **La base no se expone a la red.** En `docker-compose.yml` el servicio de
  PostgreSQL no publica el puerto 5432 a propósito: solo la aplicación la ve.
- **Datos personales.** El sistema guarda nombres, documentos, fechas de
  nacimiento y salarios de personas reales. En Colombia eso lo cubre la Ley
  1581 de 2012: conviene tener la autorización de tratamiento de datos de cada
  empleado y restringir quién entra al servidor.

---

## 16. Publicar el sistema en internet (Render + Vercel)

> Esto es para **mostrar el sistema por fuera de la empresa** — la
> sustentación de la tesis, por ejemplo. Para el uso real de Ecodes sirve la
> instalación en el servidor local de la sección 12, que además evita que los
> datos de los empleados salgan de la empresa.



El backend y el frontend se publican por separado, porque son cosas distintas:
el backend es un servidor que necesita base de datos, y el frontend son
archivos estáticos.

> **Por qué el backend no va en Vercel.** Vercel ejecuta funciones *serverless*
> (arrancan y mueren en cada petición) y no incluye PostgreSQL. Este backend es
> un servidor de larga vida con base de datos, así que va en Render, que tiene
> ambas cosas en su plan gratuito. Si lo intentas desplegar en Vercel tal cual,
> falla con `FUNCTION_INVOCATION_FAILED` porque no encuentra la base de datos.

### 16.1. Backend en Render

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

### 16.2. Frontend en Vercel

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

### 16.3. Cosas que conviene saber del plan gratuito

| | |
|---|---|
| **El backend se duerme** | Render apaga los servicios gratuitos tras 15 minutos sin uso. La primera petición después de eso tarda **30–60 segundos** en responder mientras vuelve a arrancar. No está dañado; es el plan gratis. Si vas a mostrar el sistema en una sustentación, ábrelo unos minutos antes. |
| **La base de datos caduca** | Las bases PostgreSQL gratuitas de Render expiran a los 30 días. Para un proyecto de tesis alcanza, pero anótalo. |
| **Las contraseñas del seed son públicas** | `th / th12345` y `admin / admin12345` están en el repositorio. Sirven para la demo; si el sistema llegara a manejar datos reales de empleados, cámbialas antes. |

### 16.4. Otras opciones

- **Backend**: cualquier host compatible con ASGI (Uvicorn/Gunicorn) —
  Railway, Fly.io, un VPS con Docker, etc. Solo hay que configurar
  `DATABASE_URL` apuntando a PostgreSQL y una `JWT_SECRET_KEY` robusta.
- **Frontend**: al ser archivos estáticos, también funciona en Netlify,
  GitHub Pages, S3 + CloudFront o detrás del mismo proxy del backend. En
  cualquier caso, define la URL de la API en `frontend/js/config.js` e incluye
  el dominio del frontend en `CORS_ORIGINS`.
