namespace CuentasPorPagar.Application.Abstractions.Integrations;

/// <summary>
/// Envío de correo (sección 17/27-29). La implementación real usa Gmail API con
/// cuenta de servicio + delegación de dominio; en modo mock se registra el envío
/// sin llamar a Google (punto 87). El llamador nunca debe bloquear el flujo
/// principal por una falla aquí: los Services capturan la excepción y encolan
/// el reintento vía IColaSincronizacionRepository (punto 72).
/// </summary>
public interface IEmailSender
{
    Task EnviarAsync(string destinatario, IReadOnlyList<string> copias, string asunto, string cuerpoHtml, CancellationToken ct = default);
}
