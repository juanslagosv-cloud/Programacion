namespace CuentasPorPagar.Api.Auth;

/// <summary>
/// Configuración del JWT de sesión de la aplicación (sección 19: "sesión corta,
/// 30-60 min"). Este JWT es propio del backend — no confundir con el id_token de
/// Google, que solo se usa una vez para el login (sección 4).
/// </summary>
public class JwtOptions
{
    public const string SeccionConfiguracion = "Jwt";

    public string Issuer { get; set; } = "CuentasPorPagar";
    public string Audience { get; set; } = "CuentasPorPagar.Frontend";

    /// <summary>Clave de firma simétrica. En producción debe venir de una variable de entorno/secret store, nunca hardcodeada.</summary>
    public string SigningKey { get; set; } = string.Empty;

    public int ExpiracionMinutos { get; set; } = 60;
}
