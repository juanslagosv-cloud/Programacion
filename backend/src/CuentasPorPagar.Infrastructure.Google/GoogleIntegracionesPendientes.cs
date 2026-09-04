using CuentasPorPagar.Application.Abstractions.Integrations;

namespace CuentasPorPagar.Infrastructure.Google;

/// <summary>
/// Google Drive real (Fase 12) y Gmail real (Fase 13) todavía no están
/// implementados — solo la autenticación (Fase 3, <see cref="GoogleAuthProvider"/>).
/// Se registran igualmente en DI para que IntegrationMode=google sea seleccionable
/// de punta a punta (el login real ya funciona); usar estas dos integraciones
/// lanza NotImplementedException en vez de fallar silenciosamente o fingir éxito.
/// Mientras tanto, puede combinarse GOOGLE_CLIENT_ID real para el login con
/// Drive/Gmail simulados (ver Program.cs).
/// </summary>
public class GoogleDocumentStorageProviderPendiente : IDocumentStorageProvider
{
    public Task<CarpetaDrive> ObtenerOCrearCarpetaExpedienteAsync(string empresaNombre, int anio, int mes, string radicado, string proveedorNombre, CancellationToken ct = default)
        => throw new NotImplementedException("Google Drive real es Fase 12. Use IntegrationMode=mock mientras tanto.");

    public Task<ArchivoDrive> SubirArchivoAsync(string carpetaId, string nombreNormalizado, string mimeType, Stream contenido, CancellationToken ct = default)
        => throw new NotImplementedException("Google Drive real es Fase 12. Use IntegrationMode=mock mientras tanto.");

    public Task<ArchivoDrive> ObtenerArchivoAsync(string archivoId, CancellationToken ct = default)
        => throw new NotImplementedException("Google Drive real es Fase 12. Use IntegrationMode=mock mientras tanto.");
}

public class GmailEmailSenderPendiente : IEmailSender
{
    public Task EnviarAsync(string destinatario, IReadOnlyList<string> copias, string asunto, string cuerpoHtml, CancellationToken ct = default)
        => throw new NotImplementedException("Gmail real es Fase 13. Use IntegrationMode=mock mientras tanto.");
}
