# Cómo obtener una URL pública real (sin instalar nada)

Esta guía despliega el proyecto en [Render](https://render.com) para que quede
accesible por una URL de internet, usando solo el navegador — no requiere
instalar ningún software ni compartir credenciales con nadie. Solo inicias
sesión en Render con tu cuenta de GitHub (OAuth), igual que cuando entras a
cualquier sitio con "Continuar con GitHub".

**Importante — alcance de esta instancia:**
- Corre en modo `DataProvider=Mock` / `IntegrationMode=mock`: usa datos de
  demostración en memoria (sección 88 del documento técnico), **no** Microsoft
  Access real ni Google real. Sirve para que el equipo vea y pruebe la
  aplicación funcionando de verdad (login, JWT, permisos), no para operar con
  información real de la empresa.
- El plan gratuito de Render "duerme" el servicio tras ~15 min sin uso; la
  primera petición después de eso tarda unos segundos en responder mientras
  despierta. Es normal.

## Pasos

1. **Entra a [render.com](https://render.com) e inicia sesión con GitHub.**
   Render pedirá autorización para leer tus repositorios — puedes limitarlo
   solo al repositorio `Programacion` si tu organización lo exige.

2. **"New" → "Blueprint".** Selecciona el repositorio `Programacion` y la
   rama `claude/sistema-documental-cuentas-pagar-ew65ic`. Render detecta
   automáticamente el archivo `render.yaml` en la raíz del repositorio y
   propone crear dos servicios: `cxp-api` (backend) y `cxp-frontend`
   (frontend). Confirma con "Apply".

3. **Espera a que ambos terminen de desplegar** (unos minutos la primera vez,
   Render construye la imagen Docker del backend y compila el frontend).
   Cuando terminen, cada servicio muestra su propia URL, algo como:
   - `https://cxp-api-xxxx.onrender.com`
   - `https://cxp-frontend-xxxx.onrender.com`

4. **Conecta los dos servicios entre sí** (un único paso manual, una sola vez):
   - Entra al servicio `cxp-frontend` → pestaña "Environment" → edita
     `NEXT_PUBLIC_API_URL` con la URL real de `cxp-api` (paso 3) → guarda →
     Render vuelve a desplegar el frontend automáticamente.
   - Entra al servicio `cxp-api` → pestaña "Environment" → edita
     `Cors__AllowedOrigins__0` con la URL real de `cxp-frontend` → guarda.

5. **Abre la URL de `cxp-frontend`.** Ahí está el sistema real: login con los
   7 usuarios de demostración, JWT emitido por el backend real, permisos
   verificados en el servidor — no una vista previa.

## Si la empresa exige un proveedor específico (Azure, AWS, etc.)

La arquitectura no depende de Render — es un backend Docker estándar (ASP.NET
Core) y un frontend Node estándar (Next.js), desplegables en cualquier
plataforma que soporte contenedores/Node (Azure App Service, AWS App Runner,
Google Cloud Run, etc.). El `render.yaml` sirve como referencia de qué
variables de entorno necesita cada servicio (`backend/Dockerfile` +
`DataProvider`, `IntegrationMode`, `Jwt__SigningKey`, `Cors__AllowedOrigins__0`
para el backend; `NEXT_PUBLIC_API_URL` para el frontend). Dime qué proveedor
usa la empresa y preparo la configuración equivalente.

## Recordatorio de seguridad

Esta URL queda accesible para cualquiera que la conozca (no tiene usuarios de
producción reales ni datos sensibles porque corre en modo Mock, pero sí es
pública). Cuando termines de mostrarla, puedes suspender o borrar el servicio
desde el dashboard de Render sin afectar el repositorio ni el resto del
trabajo.
