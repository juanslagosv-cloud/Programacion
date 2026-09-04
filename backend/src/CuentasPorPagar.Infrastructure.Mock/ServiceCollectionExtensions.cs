using CuentasPorPagar.Application.Abstractions.Integrations;
using CuentasPorPagar.Application.Abstractions.Repositories;
using Microsoft.Extensions.DependencyInjection;

namespace CuentasPorPagar.Infrastructure.Mock;

/// <summary>
/// Registra todas las implementaciones en memoria (INTEGRATION_MODE=mock / DataProvider=Mock,
/// punto 87). Usado en desarrollo y demo; nunca en producción real de la empresa.
/// </summary>
public static class ServiceCollectionExtensions
{
    public static IServiceCollection AddMockInfrastructure(this IServiceCollection services)
    {
        services.AddSingleton<InMemoryDataStore>();

        services.AddSingleton<IUsuarioRepository, MockUsuarioRepository>();
        services.AddSingleton<IRolRepository, MockRolRepository>();
        services.AddSingleton<IPermisoRepository, MockPermisoRepository>();
        services.AddSingleton<IDelegacionRepository, MockDelegacionRepository>();

        services.AddSingleton<IEmpresaRepository, MockEmpresaRepository>();
        services.AddSingleton<IProveedorRepository, MockProveedorRepository>();
        services.AddSingleton<IProyectoRepository, MockProyectoRepository>();
        services.AddSingleton<ICentroCostoRepository, MockCentroCostoRepository>();
        services.AddSingleton<IBancoRepository, MockBancoRepository>();
        services.AddSingleton<ITipoSolicitudRepository, MockTipoSolicitudRepository>();
        services.AddSingleton<ITipoDocumentoRepository, MockTipoDocumentoRepository>();
        services.AddSingleton<IDocumentoObligatorioConfigRepository, MockDocumentoObligatorioConfigRepository>();
        services.AddSingleton<IMotivoRepository, MockMotivoRepository>();
        services.AddSingleton<IPlantillaCorreoRepository, MockPlantillaCorreoRepository>();
        services.AddSingleton<IConfiguracionSistemaRepository, MockConfiguracionSistemaRepository>();

        services.AddSingleton<ISolicitudPagoRepository, MockSolicitudPagoRepository>();
        services.AddSingleton<IDocumentoSolicitudRepository, MockDocumentoSolicitudRepository>();
        services.AddSingleton<IFlujoAprobacionRepository, MockFlujoAprobacionRepository>();
        services.AddSingleton<IAprobacionRepository, MockAprobacionRepository>();
        services.AddSingleton<ICausacionRepository, MockCausacionRepository>();
        services.AddSingleton<IPagoRepository, MockPagoRepository>();
        services.AddSingleton<INotificacionRepository, MockNotificacionRepository>();
        services.AddSingleton<IAuditoriaRepository, MockAuditoriaRepository>();
        services.AddSingleton<ISecuenciaRadicadoRepository, MockSecuenciaRadicadoRepository>();
        services.AddSingleton<IColaSincronizacionRepository, MockColaSincronizacionRepository>();

        services.AddMockIntegrations();

        return services;
    }

    /// <summary>
    /// Registra únicamente las integraciones simuladas (Drive/Gmail/OAuth), sin los
    /// repositorios en memoria. Permite combinar DataProvider=Access (Microsoft
    /// Access real) con IntegrationMode=mock (Drive/Gmail simulados) mientras no
    /// haya credenciales de Google Workspace configuradas.
    /// </summary>
    public static IServiceCollection AddMockIntegrations(this IServiceCollection services)
    {
        services.AddSingleton<IDocumentStorageProvider, MockDocumentStorageProvider>();
        services.AddSingleton<IEmailSender, MockEmailSender>();
        services.AddSingleton<IAuthProvider, MockAuthProvider>();

        return services;
    }
}
