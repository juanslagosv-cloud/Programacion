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
CuentasPorPagar.Infrastructure.Google  Pendiente (Fases 3/12/13): Drive, Gmail, Google OAuth
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
pagar, pagos parciales, versionamiento documental, detección de duplicados y
concurrencia optimista.
