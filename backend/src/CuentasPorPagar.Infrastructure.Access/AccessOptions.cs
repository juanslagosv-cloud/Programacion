namespace CuentasPorPagar.Infrastructure.Access;

/// <summary>
/// Configuración de conexión a Microsoft Access (sección 4/61). El archivo .accdb
/// debe residir en disco LOCAL del servidor Windows donde corre este backend —
/// nunca en una ruta de red (UNC/SMB), causa documentada de corrupción del motor
/// Jet/ACE. Se puebla desde la variable de entorno ACCESS_DATABASE_PATH (ver .env.example).
/// </summary>
public class AccessOptions
{
    public const string SeccionConfiguracion = "Access";

    public string DatabasePath { get; set; } = string.Empty;

    /// <summary>Requiere el "Access Database Engine Redistributable" (64 bits) instalado en el servidor.</summary>
    public string ProviderName { get; set; } = "Microsoft.ACE.OLEDB.16.0";

    public string ConnectionString => $"Provider={ProviderName};Data Source={DatabasePath};Persist Security Info=False;";
}
