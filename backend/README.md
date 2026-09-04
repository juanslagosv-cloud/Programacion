# Backend — CuentasPorPagar

API en ASP.NET Core 8 (Web API), siguiendo la arquitectura por capas descrita en
[docs/00-propuesta-tecnica-funcional.md](../docs/00-propuesta-tecnica-funcional.md)
(sección 3, 61-64):

```
CuentasPorPagar.Api                    Controllers, Program.cs (composición/DI)
CuentasPorPagar.Application            Interfaces de repositorio, servicios de negocio (workflow, radicado, auditoría, neto a pagar)
CuentasPorPagar.Domain                 Entidades, enums, máquina de estados (sin dependencias externas)
CuentasPorPagar.Infrastructure.Access  Implementación sobre Microsoft Access (OLE DB) — requiere Windows
CuentasPorPagar.Infrastructure.Mock    Implementación en memoria (desarrollo/demo, INTEGRATION_MODE=mock)
CuentasPorPagar.Infrastructure.Google  Login real con Google (Fase 3, GoogleAuthProvider); Drive/Gmail reales pendientes (Fases 12/13)
```

## Ejecutar en modo Mock (sin Access ni Google reales)

```bash
cd src/CuentasPorPagar.Api
DataProvider=Mock IntegrationMode=mock dotnet run
```

La API queda disponible en la URL que imprima la consola (por defecto algo como
`http://localhost:5238`). Verificar con:

```bash
curl http://localhost:5238/api/sistema/estado
```

## Autenticación y RBAC (Fase 3)

En `DataProvider=Mock`, al arrancar se siembran automáticamente los roles,
permisos (sección 8) y usuarios de ejemplo de la sección 88 — uno por rol, todos
`Activo=true` — para poder iniciar sesión sin depender de credenciales de
Google reales:

| Correo | Rol |
|---|---|
| laura.gomez@empresa.com | Solicitante |
| andres.ruiz@empresa.com | Revisor |
| carlos.perez@empresa.com | Aprobador |
| andrea.rojas@empresa.com | Contabilidad |
| diego.sanchez@empresa.com | Tesorería |
| marta.londono@empresa.com | Auditor |
| admin@empresa.com | Administrador |

Con `IntegrationMode=mock`, `POST /api/auth/login` acepta un token con formato
`mock:{correo}:{nombre}` (ver `MockAuthProvider`) en vez de un id_token real de
Google — así el resto del flujo (JWT propio, permisos, `[PermisoRequerido]`)
puede probarse de punta a punta sin credenciales de Google Workspace:

```bash
curl -X POST http://localhost:5238/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"token":"mock:carlos.perez@empresa.com:Carlos Pérez"}'
# -> { "token": "<jwt>", "perfil": { "roles": ["Aprobador"], "permisos": [...] } }

curl http://localhost:5238/api/auth/me -H "Authorization: Bearer <jwt>"
```

Con `IntegrationMode=google`, el mismo endpoint exige un id_token real emitido
por Google (validado por `GoogleAuthProvider` contra los certificados públicos
de Google) y requiere `Google__ClientId` configurado; el resto del flujo
(búsqueda en `Usuarios`, verificación `Activo`, emisión del JWT propio,
`[PermisoRequerido]` en los controladores) es idéntico — la autenticación está
desacoplada del resto de la aplicación (sección 4).

**En `DataProvider=Access` no existe seeder automático:** el primer usuario
Administrador debe insertarse manualmente en la tabla `Usuarios` (y su fila en
`UsuariosRoles`) antes de la puesta en producción — es exactamente el mismo
problema del "huevo y la gallina" que describe la sección 4 ("el usuario debe
existir y estar activo... antes de poder entrar").

## Ejecutar contra Microsoft Access real

Requiere un host **Windows** con el "Access Database Engine Redistributable"
(64 bits) instalado — ver sección 4 de la propuesta técnica. Configurar:

```bash
DataProvider=Access
Access__DatabasePath=C:\CuentasPorPagar\Data\CuentasPorPagar.accdb
```

**Importante:** varios repositorios Access (`Access*Repository` en
`CuentasPorPagar.Infrastructure.Access/AccessRepositoriosPendientes.cs`) todavía
lanzan `NotImplementedException` — ver ese archivo para la lista completa y el
patrón de referencia ya implementado (`AccessSolicitudPagoRepository`,
`AccessSecuenciaRadicadoRepository`, `AccessAuditoriaRepository`,
`AccessUsuarioRepository`).

## Pruebas

```bash
dotnet test tests/CuentasPorPagar.Tests
```

Cubren, entre otros, los casos mínimos pedidos en la sección 86: máquina de
estados, generación segura del radicado bajo concurrencia, cálculo del neto a
pagar, pagos parciales, versionamiento documental, detección de duplicados,
concurrencia optimista, y — mediante pruebas de integración HTTP reales con
`WebApplicationFactory` (`AutenticacionYRbacTests`) — que un usuario sin el
permiso requerido recibe 403 del backend, no solo un botón oculto en la UI.
