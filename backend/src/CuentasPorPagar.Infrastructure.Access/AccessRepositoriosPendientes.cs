using CuentasPorPagar.Application.Abstractions.Repositories;
using CuentasPorPagar.Domain.Entities;
using CuentasPorPagar.Domain.Enums;

namespace CuentasPorPagar.Infrastructure.Access;

/// <summary>
/// Repositorios Access pendientes de implementar en la siguiente iteración de la
/// Fase 2, siguiendo exactamente el mismo patrón ya probado en
/// <see cref="AccessSolicitudPagoRepository"/>, <see cref="AccessSecuenciaRadicadoRepository"/>,
/// <see cref="AccessAuditoriaRepository"/> y <see cref="AccessUsuarioRepository"/>:
/// SQL parametrizado sobre <see cref="AccessConnectionFactory"/>, concurrencia
/// optimista por RowVersion en escrituras, transacciones cortas.
///
/// Se registran igualmente en DI (ver ServiceCollectionExtensions) para que
/// DataProvider=Access sea seleccionable de punta a punta sin excepciones de
/// resolución de dependencias; cada método lanza NotImplementedException hasta
/// completarse, en vez de fingir una implementación que no existe.
/// </summary>
public class AccessRolRepository : IRolRepository
{
    private readonly AccessConnectionFactory _connectionFactory;
    public AccessRolRepository(AccessConnectionFactory connectionFactory) => _connectionFactory = connectionFactory;

    public Task<IReadOnlyList<Rol>> ListarAsync(CancellationToken ct = default) => throw new NotImplementedException();
    public Task<Rol?> ObtenerPorIdAsync(int id, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<Rol> CrearAsync(Rol rol, CancellationToken ct = default) => throw new NotImplementedException();
    public Task ActualizarAsync(Rol rol, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<IReadOnlyList<Permiso>> ObtenerPermisosDelRolAsync(int rolId, CancellationToken ct = default) => throw new NotImplementedException();
    public Task AsignarPermisoAsync(int rolId, int permisoId, CancellationToken ct = default) => throw new NotImplementedException();
    public Task RevocarPermisoAsync(int rolId, int permisoId, CancellationToken ct = default) => throw new NotImplementedException();
    public Task AsignarRolAUsuarioAsync(int usuarioId, int rolId, int? empresaId, CancellationToken ct = default) => throw new NotImplementedException();
    public Task RevocarRolDeUsuarioAsync(int usuarioId, int rolId, int? empresaId, CancellationToken ct = default) => throw new NotImplementedException();
}

public class AccessPermisoRepository : IPermisoRepository
{
    private readonly AccessConnectionFactory _connectionFactory;
    public AccessPermisoRepository(AccessConnectionFactory connectionFactory) => _connectionFactory = connectionFactory;

    public Task<IReadOnlyList<Permiso>> ListarAsync(CancellationToken ct = default) => throw new NotImplementedException();
    public Task<Permiso> CrearAsync(Permiso permiso, CancellationToken ct = default) => throw new NotImplementedException();
}

public class AccessDelegacionRepository : IDelegacionRepository
{
    private readonly AccessConnectionFactory _connectionFactory;
    public AccessDelegacionRepository(AccessConnectionFactory connectionFactory) => _connectionFactory = connectionFactory;

    public Task<IReadOnlyList<Delegacion>> ListarVigentesAsync(DateTime fecha, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<Delegacion?> ObtenerSuplenciaVigenteAsync(int titularId, int rolId, DateTime fecha, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<Delegacion> CrearAsync(Delegacion delegacion, CancellationToken ct = default) => throw new NotImplementedException();
}

public class AccessEmpresaRepository : IEmpresaRepository
{
    private readonly AccessConnectionFactory _connectionFactory;
    public AccessEmpresaRepository(AccessConnectionFactory connectionFactory) => _connectionFactory = connectionFactory;

    public Task<IReadOnlyList<Empresa>> ListarAsync(bool soloActivas = true, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<Empresa?> ObtenerPorIdAsync(int id, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<Empresa?> ObtenerPorNitAsync(string nit, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<Empresa> CrearAsync(Empresa empresa, CancellationToken ct = default) => throw new NotImplementedException();
    public Task ActualizarAsync(Empresa empresa, CancellationToken ct = default) => throw new NotImplementedException();
}

public class AccessProveedorRepository : IProveedorRepository
{
    private readonly AccessConnectionFactory _connectionFactory;
    public AccessProveedorRepository(AccessConnectionFactory connectionFactory) => _connectionFactory = connectionFactory;

    public Task<IReadOnlyList<Proveedor>> ListarAsync(int? empresaId = null, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<Proveedor?> ObtenerPorIdAsync(int id, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<Proveedor?> ObtenerPorNitAsync(int empresaId, string nit, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<Proveedor> CrearAsync(Proveedor proveedor, CancellationToken ct = default) => throw new NotImplementedException();
    public Task ActualizarAsync(Proveedor proveedor, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<IReadOnlyList<ProveedorCuentaBancaria>> ObtenerCuentasBancariasAsync(int proveedorId, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<ProveedorCuentaBancaria> AgregarCuentaBancariaAsync(ProveedorCuentaBancaria cuenta, CancellationToken ct = default) => throw new NotImplementedException();
}

public class AccessProyectoRepository : IProyectoRepository
{
    private readonly AccessConnectionFactory _connectionFactory;
    public AccessProyectoRepository(AccessConnectionFactory connectionFactory) => _connectionFactory = connectionFactory;

    public Task<IReadOnlyList<Proyecto>> ListarAsync(int? empresaId = null, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<Proyecto?> ObtenerPorIdAsync(int id, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<Proyecto> CrearAsync(Proyecto proyecto, CancellationToken ct = default) => throw new NotImplementedException();
    public Task ActualizarAsync(Proyecto proyecto, CancellationToken ct = default) => throw new NotImplementedException();
}

public class AccessCentroCostoRepository : ICentroCostoRepository
{
    private readonly AccessConnectionFactory _connectionFactory;
    public AccessCentroCostoRepository(AccessConnectionFactory connectionFactory) => _connectionFactory = connectionFactory;

    public Task<IReadOnlyList<CentroCosto>> ListarAsync(int? empresaId = null, int? proyectoId = null, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<CentroCosto?> ObtenerPorIdAsync(int id, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<CentroCosto> CrearAsync(CentroCosto centroCosto, CancellationToken ct = default) => throw new NotImplementedException();
    public Task ActualizarAsync(CentroCosto centroCosto, CancellationToken ct = default) => throw new NotImplementedException();
}

public class AccessBancoRepository : IBancoRepository
{
    private readonly AccessConnectionFactory _connectionFactory;
    public AccessBancoRepository(AccessConnectionFactory connectionFactory) => _connectionFactory = connectionFactory;

    public Task<IReadOnlyList<Banco>> ListarAsync(int? empresaId = null, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<Banco?> ObtenerPorIdAsync(int id, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<Banco> CrearAsync(Banco banco, CancellationToken ct = default) => throw new NotImplementedException();
    public Task ActualizarAsync(Banco banco, CancellationToken ct = default) => throw new NotImplementedException();
}

public class AccessTipoSolicitudRepository : ITipoSolicitudRepository
{
    private readonly AccessConnectionFactory _connectionFactory;
    public AccessTipoSolicitudRepository(AccessConnectionFactory connectionFactory) => _connectionFactory = connectionFactory;

    public Task<IReadOnlyList<TipoSolicitud>> ListarAsync(bool soloActivos = true, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<TipoSolicitud> CrearAsync(TipoSolicitud tipo, CancellationToken ct = default) => throw new NotImplementedException();
}

public class AccessTipoDocumentoRepository : ITipoDocumentoRepository
{
    private readonly AccessConnectionFactory _connectionFactory;
    public AccessTipoDocumentoRepository(AccessConnectionFactory connectionFactory) => _connectionFactory = connectionFactory;

    public Task<IReadOnlyList<TipoDocumento>> ListarAsync(bool soloActivos = true, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<TipoDocumento> CrearAsync(TipoDocumento tipo, CancellationToken ct = default) => throw new NotImplementedException();
}

public class AccessDocumentoObligatorioConfigRepository : IDocumentoObligatorioConfigRepository
{
    private readonly AccessConnectionFactory _connectionFactory;
    public AccessDocumentoObligatorioConfigRepository(AccessConnectionFactory connectionFactory) => _connectionFactory = connectionFactory;

    public Task<IReadOnlyList<DocumentoObligatorioConfig>> ResolverAplicablesAsync(int tipoSolicitudId, int empresaId, string? tipoProveedor, decimal valorBruto, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<DocumentoObligatorioConfig> CrearAsync(DocumentoObligatorioConfig config, CancellationToken ct = default) => throw new NotImplementedException();
}

public class AccessMotivoRepository : IMotivoRepository
{
    private readonly AccessConnectionFactory _connectionFactory;
    public AccessMotivoRepository(AccessConnectionFactory connectionFactory) => _connectionFactory = connectionFactory;

    public Task<IReadOnlyList<MotivoDevolucion>> ListarMotivosDevolucionAsync(CancellationToken ct = default) => throw new NotImplementedException();
    public Task<IReadOnlyList<MotivoRechazo>> ListarMotivosRechazoAsync(CancellationToken ct = default) => throw new NotImplementedException();
    public Task<IReadOnlyList<MotivoDiferenciaPago>> ListarMotivosDiferenciaPagoAsync(CancellationToken ct = default) => throw new NotImplementedException();
}

public class AccessPlantillaCorreoRepository : IPlantillaCorreoRepository
{
    private readonly AccessConnectionFactory _connectionFactory;
    public AccessPlantillaCorreoRepository(AccessConnectionFactory connectionFactory) => _connectionFactory = connectionFactory;

    public Task<PlantillaCorreo?> ObtenerPorCodigoAsync(string codigo, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<IReadOnlyList<PlantillaCorreo>> ListarAsync(CancellationToken ct = default) => throw new NotImplementedException();
    public Task ActualizarAsync(PlantillaCorreo plantilla, CancellationToken ct = default) => throw new NotImplementedException();
}

public class AccessConfiguracionSistemaRepository : IConfiguracionSistemaRepository
{
    private readonly AccessConnectionFactory _connectionFactory;
    public AccessConfiguracionSistemaRepository(AccessConnectionFactory connectionFactory) => _connectionFactory = connectionFactory;

    public Task<string?> ObtenerValorAsync(string clave, CancellationToken ct = default) => throw new NotImplementedException();
    public Task EstablecerValorAsync(string clave, string valor, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<IReadOnlyList<ConfiguracionSistema>> ListarAsync(CancellationToken ct = default) => throw new NotImplementedException();
}

public class AccessDocumentoSolicitudRepository : IDocumentoSolicitudRepository
{
    private readonly AccessConnectionFactory _connectionFactory;
    public AccessDocumentoSolicitudRepository(AccessConnectionFactory connectionFactory) => _connectionFactory = connectionFactory;

    public Task<IReadOnlyList<DocumentoSolicitud>> ListarPorSolicitudAsync(int solicitudId, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<DocumentoSolicitud?> ObtenerPorIdAsync(int id, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<DocumentoSolicitud> CrearAsync(DocumentoSolicitud documento, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<IReadOnlyList<VersionDocumento>> ObtenerVersionesAsync(int documentoId, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<VersionDocumento> AgregarVersionAsync(int documentoId, VersionDocumento nuevaVersion, CancellationToken ct = default) => throw new NotImplementedException();
}

public class AccessFlujoAprobacionRepository : IFlujoAprobacionRepository
{
    private readonly AccessConnectionFactory _connectionFactory;
    public AccessFlujoAprobacionRepository(AccessConnectionFactory connectionFactory) => _connectionFactory = connectionFactory;

    public Task<IReadOnlyList<FlujoAprobacion>> ListarActivosAsync(int? empresaId, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<FlujoAprobacion?> ObtenerPorIdAsync(int id, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<IReadOnlyList<PasoFlujo>> ObtenerPasosAsync(int flujoId, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<FlujoAprobacion> CrearAsync(FlujoAprobacion flujo, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<PasoFlujo> AgregarPasoAsync(PasoFlujo paso, CancellationToken ct = default) => throw new NotImplementedException();
}

public class AccessAprobacionRepository : IAprobacionRepository
{
    private readonly AccessConnectionFactory _connectionFactory;
    public AccessAprobacionRepository(AccessConnectionFactory connectionFactory) => _connectionFactory = connectionFactory;

    public Task<InstanciaAprobacion?> ObtenerInstanciaVigenteAsync(int solicitudId, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<InstanciaAprobacion> CrearInstanciaAsync(InstanciaAprobacion instancia, CancellationToken ct = default) => throw new NotImplementedException();
    public Task ActualizarInstanciaAsync(InstanciaAprobacion instancia, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<IReadOnlyList<Aprobacion>> ObtenerDecisionesAsync(int instanciaId, int? pasoId = null, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<Aprobacion> RegistrarDecisionAsync(Aprobacion aprobacion, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<ResultadoPaginado<SolicitudPago>> ObtenerPendientesDeAprobadorAsync(int usuarioId, int pagina, int tamanoPagina, CancellationToken ct = default) => throw new NotImplementedException();
}

public class AccessCausacionRepository : ICausacionRepository
{
    private readonly AccessConnectionFactory _connectionFactory;
    public AccessCausacionRepository(AccessConnectionFactory connectionFactory) => _connectionFactory = connectionFactory;

    public Task<Causacion?> ObtenerVigentePorSolicitudAsync(int solicitudId, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<IReadOnlyList<Causacion>> ObtenerHistorialAsync(int solicitudId, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<IReadOnlyList<RetencionCausacion>> ObtenerRetencionesAsync(int causacionId, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<Causacion> RegistrarAsync(Causacion causacion, IReadOnlyList<RetencionCausacion> retenciones, CancellationToken ct = default) => throw new NotImplementedException();
}

public class AccessPagoRepository : IPagoRepository
{
    private readonly AccessConnectionFactory _connectionFactory;
    public AccessPagoRepository(AccessConnectionFactory connectionFactory) => _connectionFactory = connectionFactory;

    public Task<IReadOnlyList<Pago>> ObtenerPorSolicitudAsync(int solicitudId, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<decimal> ObtenerSaldoPendienteAsync(int solicitudId, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<Pago> RegistrarAsync(Pago pago, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<DocumentoPago> AgregarSoporteAsync(DocumentoPago documentoPago, CancellationToken ct = default) => throw new NotImplementedException();
}

public class AccessNotificacionRepository : INotificacionRepository
{
    private readonly AccessConnectionFactory _connectionFactory;
    public AccessNotificacionRepository(AccessConnectionFactory connectionFactory) => _connectionFactory = connectionFactory;

    public Task<Notificacion> CrearAsync(Notificacion notificacion, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<IReadOnlyList<Notificacion>> ListarPorUsuarioAsync(int usuarioId, bool soloNoLeidas, CancellationToken ct = default) => throw new NotImplementedException();
    public Task MarcarLeidaAsync(int notificacionId, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<IReadOnlyList<Notificacion>> ObtenerPendientesDeCorreoAsync(int maxIntentos, CancellationToken ct = default) => throw new NotImplementedException();
    public Task MarcarEnvioCorreoAsync(int notificacionId, EstadoEnvio estado, CancellationToken ct = default) => throw new NotImplementedException();
}

public class AccessColaSincronizacionRepository : IColaSincronizacionRepository
{
    private readonly AccessConnectionFactory _connectionFactory;
    public AccessColaSincronizacionRepository(AccessConnectionFactory connectionFactory) => _connectionFactory = connectionFactory;

    public Task<TrabajoSincronizacion> EncolarAsync(TrabajoSincronizacion trabajo, CancellationToken ct = default) => throw new NotImplementedException();
    public Task<IReadOnlyList<TrabajoSincronizacion>> ObtenerPendientesAsync(int maxIntentos, CancellationToken ct = default) => throw new NotImplementedException();
    public Task MarcarResultadoAsync(int trabajoId, EstadoTrabajoSincronizacion estado, string? error, CancellationToken ct = default) => throw new NotImplementedException();
}
