using CuentasPorPagar.Application.Abstractions.Integrations;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

namespace CuentasPorPagar.Infrastructure.Google;

/// <summary>Registra las integraciones reales de Google (IntegrationMode=google).</summary>
public static class ServiceCollectionExtensions
{
    public static IServiceCollection AddGoogleInfrastructure(this IServiceCollection services, IConfiguration configuration)
    {
        services.Configure<GoogleOptions>(configuration.GetSection(GoogleOptions.SeccionConfiguracion));

        services.AddSingleton<IAuthProvider, GoogleAuthProvider>();
        services.AddSingleton<IDocumentStorageProvider, GoogleDocumentStorageProviderPendiente>();
        services.AddSingleton<IEmailSender, GmailEmailSenderPendiente>();

        return services;
    }
}
