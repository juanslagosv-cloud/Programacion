using CuentasPorPagar.Domain.Common;

namespace CuentasPorPagar.Domain.Entities;

/// <summary>
/// Metadatos del documento (sección 13/14): el archivo físico vive en Google Drive,
/// Access/la base de datos solo guarda IDs, URL y metadatos.
/// </summary>
public class DocumentoSolicitud : EntidadBase
{
    public int SolicitudId { get; set; }
    public int TipoDocumentoId { get; set; }
    public string NombreOriginal { get; set; } = string.Empty;
    public string NombreNormalizado { get; set; } = string.Empty;
    public string? DriveFileId { get; set; }
    public string? DriveFolderId { get; set; }
    public string? UrlDrive { get; set; }
    public int? VersionVigenteId { get; set; }
    public bool EstadoVigente { get; set; } = true;
    public int SubidoPorId { get; set; }
    public DateTime FechaCarga { get; set; } = DateTime.UtcNow;
}

/// <summary>
/// Historial de versiones (sección 16): nunca se borra una versión anterior,
/// se marca <see cref="EsVigente"/> = false y se exige <see cref="MotivoReemplazo"/>.
/// </summary>
public class VersionDocumento : EntidadBase
{
    public int DocumentoId { get; set; }
    public int NumeroVersion { get; set; }
    public string DriveFileId { get; set; } = string.Empty;
    public long TamanoBytes { get; set; }
    public string MimeType { get; set; } = string.Empty;
    public int UsuarioId { get; set; }
    public DateTime Fecha { get; set; } = DateTime.UtcNow;
    public string? MotivoReemplazo { get; set; }
    public bool EsVigente { get; set; } = true;
}
