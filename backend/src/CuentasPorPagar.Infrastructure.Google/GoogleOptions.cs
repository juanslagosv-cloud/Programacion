namespace CuentasPorPagar.Infrastructure.Google;

/// <summary>Configuración de Google Workspace/OAuth (sección 4/69/89).</summary>
public class GoogleOptions
{
    public const string SeccionConfiguracion = "Google";

    public string ClientId { get; set; } = string.Empty;

    /// <summary>
    /// Si se configura, solo se aceptan logins cuyo id_token declare este dominio
    /// (claim "hd" de Google) — sección 4: "restringir acceso únicamente a
    /// usuarios autorizados del dominio". Vacío = no restringe por dominio.
    /// </summary>
    public string WorkspaceDomain { get; set; } = string.Empty;

    public string DriveRootFolderId { get; set; } = string.Empty;
}
