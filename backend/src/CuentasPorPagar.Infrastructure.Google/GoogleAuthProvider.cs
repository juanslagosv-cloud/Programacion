using CuentasPorPagar.Application.Abstractions.Integrations;
using Google.Apis.Auth;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;

namespace CuentasPorPagar.Infrastructure.Google;

/// <summary>
/// Validación real del id_token emitido por Google Identity Services (sección 4).
/// Verifica la firma y el emisor contra los certificados públicos de Google
/// (descargados y cacheados automáticamente por Google.Apis.Auth), que el
/// Audience coincida con GOOGLE_CLIENT_ID, y — si se configuró
/// GOOGLE_WORKSPACE_DOMAIN — que el claim "hd" del token coincida con ese
/// dominio corporativo.
///
/// Esta clase NO decide si el usuario puede entrar al sistema: solo certifica
/// "esta persona es quien dice ser, según Google". La decisión de autorización
/// (¿existe y está Activo en Usuarios?) vive en Application.AutenticacionService,
/// manteniendo la autenticación desacoplada del resto de la aplicación.
///
/// Requiere salida a internet hacia Google (para obtener sus claves públicas) y
/// un GOOGLE_CLIENT_ID real registrado en Google Cloud Console — no es
/// verificable end-to-end sin esas credenciales de la empresa (ver punto 27 de
/// la propuesta técnica).
/// </summary>
public class GoogleAuthProvider : IAuthProvider
{
    private readonly GoogleOptions _options;
    private readonly ILogger<GoogleAuthProvider> _logger;

    public GoogleAuthProvider(IOptions<GoogleOptions> options, ILogger<GoogleAuthProvider> logger)
    {
        _options = options.Value;
        _logger = logger;
    }

    public async Task<IdentidadExterna?> ValidarTokenAsync(string idToken, CancellationToken ct = default)
    {
        if (string.IsNullOrWhiteSpace(_options.ClientId))
        {
            throw new InvalidOperationException(
                "GOOGLE_CLIENT_ID no está configurado. Requerido para IntegrationMode=google (ver .env.example).");
        }

        GoogleJsonWebSignature.Payload payload;
        try
        {
            payload = await GoogleJsonWebSignature.ValidateAsync(idToken, new GoogleJsonWebSignature.ValidationSettings
            {
                Audience = new[] { _options.ClientId }
            });
        }
        catch (InvalidJwtException ex)
        {
            _logger.LogWarning(ex, "id_token de Google inválido o expirado.");
            return null;
        }

        if (!string.IsNullOrWhiteSpace(_options.WorkspaceDomain) &&
            !string.Equals(payload.HostedDomain, _options.WorkspaceDomain, StringComparison.OrdinalIgnoreCase))
        {
            _logger.LogWarning(
                "Login rechazado: dominio {DominioRecibido} no coincide con el dominio corporativo configurado.",
                payload.HostedDomain);
            return null;
        }

        return new IdentidadExterna(payload.Subject, payload.Email, payload.Name, payload.HostedDomain);
    }
}
