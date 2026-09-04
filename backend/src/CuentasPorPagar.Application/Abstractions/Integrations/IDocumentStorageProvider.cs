namespace CuentasPorPagar.Application.Abstractions.Integrations;

public record CarpetaDrive(string Id, string Url);
public record ArchivoDrive(string Id, string Url, long TamanoBytes, string MimeType);

/// <summary>
/// Abstracción del repositorio documental (sección 13-16, 61-71). La implementación
/// real habla con Google Drive API; en INTEGRATION_MODE=mock se usa una
/// implementación en memoria que no llama a Google (punto 87).
///
/// Todas las operaciones deben ser idempotentes (punto 70): antes de crear una
/// carpeta o archivo, el llamador ya conoce el Id esperado (guardado en Access) y
/// esta interfaz nunca debe crear un duplicado si el Id ya existe.
/// </summary>
public interface IDocumentStorageProvider
{
    /// <summary>Crea (o reutiliza si ya existe) la carpeta del expediente: Empresa/Año/Mes/Radicado-Proveedor.</summary>
    Task<CarpetaDrive> ObtenerOCrearCarpetaExpedienteAsync(
        string empresaNombre, int anio, int mes, string radicado, string proveedorNombre, CancellationToken ct = default);

    /// <summary>Sube un archivo con nombre normalizado (sección 15) dentro de la carpeta del expediente.</summary>
    Task<ArchivoDrive> SubirArchivoAsync(
        string carpetaId, string nombreNormalizado, string mimeType, Stream contenido, CancellationToken ct = default);

    Task<ArchivoDrive> ObtenerArchivoAsync(string archivoId, CancellationToken ct = default);
}
