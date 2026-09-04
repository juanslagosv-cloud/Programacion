namespace CuentasPorPagar.Application.Abstractions.Integrations;

public record IdentidadExterna(string Sub, string Correo, string Nombre, string? DominioHd);

/// <summary>
/// Valida el token de identidad recibido del frontend tras "Continuar con Google"
/// (sección 4/69). Desacoplada del resto de la aplicación para permitir otros
/// métodos de autenticación en el futuro sin tocar Services ni Controllers.
/// </summary>
public interface IAuthProvider
{
    Task<IdentidadExterna?> ValidarTokenAsync(string idToken, CancellationToken ct = default);
}
