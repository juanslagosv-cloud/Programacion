using CuentasPorPagar.Application.Abstractions.Repositories;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

namespace CuentasPorPagar.Infrastructure.Access;

/// <summary>
/// Registra las implementaciones sobre Microsoft Access (DataProvider=Access,
/// sección 4/61-70). Solo funciona en un host Windows con el Access Database
/// Engine Redistributable instalado y ACCESS_DATABASE_PATH configurado.
/// </summary>
public static class ServiceCollectionExtensions
{
    public static IServiceCollection AddAccessInfrastructure(this IServiceCollection services, IConfiguration configuration)
    {
        services.Configure<AccessOptions>(configuration.GetSection(AccessOptions.SeccionConfiguracion));

        // Sin estado propio (solo abre conexiones bajo demanda): singleton para poder
        // ser inyectado también en ISecuenciaRadicadoRepository, que es singleton
        // porque el semáforo de exclusión mutua de SecuenciaRadicadoService debe
        // compartirse entre todas las peticiones concurrentes del proceso.
        services.AddSingleton<AccessConnectionFactory>();

        services.AddScoped<IUsuarioRepository, AccessUsuarioRepository>();
        services.AddScoped<IRolRepository, AccessRolRepository>();
        services.AddScoped<IPermisoRepository, AccessPermisoRepository>();
        services.AddScoped<IDelegacionRepository, AccessDelegacionRepository>();

        services.AddScoped<IEmpresaRepository, AccessEmpresaRepository>();
        services.AddScoped<IProveedorRepository, AccessProveedorRepository>();
        services.AddScoped<IProyectoRepository, AccessProyectoRepository>();
        services.AddScoped<ICentroCostoRepository, AccessCentroCostoRepository>();
        services.AddScoped<IBancoRepository, AccessBancoRepository>();
        services.AddScoped<ITipoSolicitudRepository, AccessTipoSolicitudRepository>();
        services.AddScoped<ITipoDocumentoRepository, AccessTipoDocumentoRepository>();
        services.AddScoped<IDocumentoObligatorioConfigRepository, AccessDocumentoObligatorioConfigRepository>();
        services.AddScoped<IMotivoRepository, AccessMotivoRepository>();
        services.AddScoped<IPlantillaCorreoRepository, AccessPlantillaCorreoRepository>();
        services.AddScoped<IConfiguracionSistemaRepository, AccessConfiguracionSistemaRepository>();

        services.AddScoped<ISolicitudPagoRepository, AccessSolicitudPagoRepository>();
        services.AddScoped<IDocumentoSolicitudRepository, AccessDocumentoSolicitudRepository>();
        services.AddScoped<IFlujoAprobacionRepository, AccessFlujoAprobacionRepository>();
        services.AddScoped<IAprobacionRepository, AccessAprobacionRepository>();
        services.AddScoped<ICausacionRepository, AccessCausacionRepository>();
        services.AddScoped<IPagoRepository, AccessPagoRepository>();
        services.AddScoped<INotificacionRepository, AccessNotificacionRepository>();
        services.AddScoped<IAuditoriaRepository, AccessAuditoriaRepository>();

        // Consecutivo de radicado: una única instancia por proceso, porque el semáforo
        // de exclusión mutua por clave (sección 20) vive en Application.Services.SecuenciaRadicadoService
        // sobre este mismo repositorio y debe ser compartido entre todas las peticiones concurrentes.
        services.AddSingleton<ISecuenciaRadicadoRepository, AccessSecuenciaRadicadoRepository>();

        services.AddScoped<IColaSincronizacionRepository, AccessColaSincronizacionRepository>();

        return services;
    }
}
