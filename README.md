# Programacion

Sistema web empresarial de gestión documental, aprobaciones, contabilidad y tesorería (cuentas por pagar).

Documento base del proyecto (análisis, arquitectura, modelo de datos, fases): [docs/00-propuesta-tecnica-funcional.md](docs/00-propuesta-tecnica-funcional.md).

## ¿Cómo lo veo?

- **URL pública, sin instalar nada:** [docs/desplegar-url-publica.md](docs/desplegar-url-publica.md) — despliega el proyecto real (backend + frontend) en unos minutos usando solo el navegador.
- **En tu máquina:** ver [backend/README.md](backend/README.md) y [frontend/README.md](frontend/README.md).

## Estado del proyecto

- **Fase 0 (Análisis):** completa — ver el documento de propuesta técnica.
- **Fase 1-2 (Arquitectura base + Access/Repository):** completas. Backend funcional en modo `Mock` (sin Access ni Google reales) para desarrollo.
- **Fase 3 (Autenticación Google OAuth + RBAC):** completa. Login real (Google o simulado según `IntegrationMode`), JWT propio, permisos verificados en cada endpoint del backend.
- **Frontend:** login y dashboards por rol conectados de verdad al backend (JWT + permisos reales, no simulados en el navegador).
- **Siguiente:** Fase 4 (maestros: Empresas, Proveedores, Proyectos, Centros de costo) en adelante.

## Estructura del repositorio

```
/docs         Documentación técnica y funcional
/backend      API en ASP.NET Core (Domain, Application, Infrastructure.Access, Infrastructure.Mock, Infrastructure.Google, Api, Tests)
/frontend     Aplicación web en Next.js
render.yaml   Blueprint de despliegue (ver docs/desplegar-url-publica.md)
```
