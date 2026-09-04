using System.Collections.Concurrent;
using CuentasPorPagar.Application.Abstractions.Integrations;
using Microsoft.Extensions.Logging;

namespace CuentasPorPagar.Infrastructure.Mock;

/// <summary>
/// Simula Google Drive (punto 87, INTEGRATION_MODE=mock): genera IDs/URLs falsos,
/// sin llamar a Google. Útil para desarrollo y demo sin credenciales reales.
/// </summary>
public class MockDocumentStorageProvider : IDocumentStorageProvider
{
    private readonly ConcurrentDictionary<string, CarpetaDrive> _carpetas = new();
    private int _contador;

    public Task<CarpetaDrive> ObtenerOCrearCarpetaExpedienteAsync(
        string empresaNombre, int anio, int mes, string radicado, string proveedorNombre, CancellationToken ct = default)
    {
        var clave = $"{empresaNombre}/{anio}/{mes:D2}/{radicado}-{proveedorNombre}";
        var carpeta = _carpetas.GetOrAdd(clave, _ =>
        {
            var id = $"mock-folder-{Interlocked.Increment(ref _contador)}";
            return new CarpetaDrive(id, $"https://drive.mock.local/folders/{id}");
        });

        return Task.FromResult(carpeta);
    }

    public Task<ArchivoDrive> SubirArchivoAsync(string carpetaId, string nombreNormalizado, string mimeType, Stream contenido, CancellationToken ct = default)
    {
        var id = $"mock-file-{Interlocked.Increment(ref _contador)}";
        var archivo = new ArchivoDrive(id, $"https://drive.mock.local/files/{id}/{Uri.EscapeDataString(nombreNormalizado)}", contenido.Length, mimeType);
        return Task.FromResult(archivo);
    }

    public Task<ArchivoDrive> ObtenerArchivoAsync(string archivoId, CancellationToken ct = default)
        => Task.FromResult(new ArchivoDrive(archivoId, $"https://drive.mock.local/files/{archivoId}", 0, "application/octet-stream"));
}

/// <summary>Simula el envío de Gmail (punto 87): registra el correo en el log en vez de enviarlo.</summary>
public class MockEmailSender : IEmailSender
{
    private readonly ILogger<MockEmailSender> _logger;
    public MockEmailSender(ILogger<MockEmailSender> logger) => _logger = logger;

    public Task EnviarAsync(string destinatario, IReadOnlyList<string> copias, string asunto, string cuerpoHtml, CancellationToken ct = default)
    {
        _logger.LogInformation(
            "[MOCK EMAIL] Para={Destinatario} CC={Copias} Asunto={Asunto}",
            destinatario, string.Join(",", copias), asunto);
        return Task.CompletedTask;
    }
}

/// <summary>
/// Simula la validación de un token de Google (punto 87): acepta cualquier
/// "id_token" con formato "mock:{correo}:{nombre}" para pruebas locales sin
/// depender de credenciales OAuth reales. Nunca debe registrarse en producción.
/// </summary>
public class MockAuthProvider : IAuthProvider
{
    public Task<IdentidadExterna?> ValidarTokenAsync(string idToken, CancellationToken ct = default)
    {
        if (!idToken.StartsWith("mock:", StringComparison.Ordinal))
        {
            return Task.FromResult<IdentidadExterna?>(null);
        }

        var partes = idToken.Split(':', 3);
        if (partes.Length < 3) return Task.FromResult<IdentidadExterna?>(null);

        var correo = partes[1];
        var nombre = partes[2];
        var dominio = correo.Contains('@') ? correo.Split('@')[1] : null;

        return Task.FromResult<IdentidadExterna?>(new IdentidadExterna($"mock-sub-{correo}", correo, nombre, dominio));
    }
}
