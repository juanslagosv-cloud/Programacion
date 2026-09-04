# CuentasPorPagar.Infrastructure.Google

Pendiente de implementar en las Fases 12 (Google Drive real) y 13 (Gmail real) del
plan de desarrollo, y en la Fase 3 para el `IAuthProvider` real basado en Google
OAuth (validación de `id_token` contra los certificados públicos de Google).

Implementará, contra las APIs oficiales de Google Workspace:

- `GoogleDocumentStorageProvider : IDocumentStorageProvider` (Google Drive API v3).
- `GmailEmailSender : IEmailSender` (Gmail API, cuenta de servicio con
  domain-wide delegation — ver sección 17/69 de la propuesta técnica).
- `GoogleAuthProvider : IAuthProvider` (validación de `id_token` de Google Identity Services).

Mientras no se implemente, el sistema debe operar con
`CuentasPorPagar.Infrastructure.Mock` (`INTEGRATION_MODE=mock`).
