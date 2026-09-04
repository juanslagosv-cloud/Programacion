using System.Collections.Concurrent;
using CuentasPorPagar.Domain.Entities;

namespace CuentasPorPagar.Infrastructure.Mock;

/// <summary>
/// Almacén en memoria compartido por todos los repositorios Mock. Registrado como
/// Singleton en DI para que los datos sobrevivan entre llamadas HTTP durante la
/// vida del proceso (INTEGRATION_MODE=mock, punto 87). No usar en producción:
/// se pierde todo al reiniciar el proceso; su único propósito es desarrollo y demo
/// sin depender de Access ni de un servidor Windows.
/// </summary>
public class InMemoryDataStore
{
    private int _siguienteId;
    public int SiguienteId() => Interlocked.Increment(ref _siguienteId);

    public ConcurrentDictionary<int, Usuario> Usuarios { get; } = new();
    public ConcurrentDictionary<int, Rol> Roles { get; } = new();
    public ConcurrentDictionary<int, Permiso> Permisos { get; } = new();
    public ConcurrentBag<RolPermiso> RolesPermisos { get; } = new();
    public ConcurrentBag<UsuarioRol> UsuariosRoles { get; } = new();
    public ConcurrentDictionary<int, Delegacion> Delegaciones { get; } = new();

    public ConcurrentDictionary<int, Empresa> Empresas { get; } = new();
    public ConcurrentDictionary<int, Proveedor> Proveedores { get; } = new();
    public ConcurrentDictionary<int, ProveedorCuentaBancaria> CuentasBancariasProveedor { get; } = new();
    public ConcurrentDictionary<int, Proyecto> Proyectos { get; } = new();
    public ConcurrentDictionary<int, CentroCosto> CentrosCosto { get; } = new();
    public ConcurrentDictionary<int, Banco> Bancos { get; } = new();
    public ConcurrentDictionary<int, TipoSolicitud> TiposSolicitud { get; } = new();
    public ConcurrentDictionary<int, TipoDocumento> TiposDocumento { get; } = new();
    public ConcurrentDictionary<int, DocumentoObligatorioConfig> DocumentosObligatorios { get; } = new();
    public ConcurrentDictionary<int, MotivoDevolucion> MotivosDevolucion { get; } = new();
    public ConcurrentDictionary<int, MotivoRechazo> MotivosRechazo { get; } = new();
    public ConcurrentDictionary<int, MotivoDiferenciaPago> MotivosDiferenciaPago { get; } = new();
    public ConcurrentDictionary<int, PlantillaCorreo> PlantillasCorreo { get; } = new();
    public ConcurrentDictionary<string, ConfiguracionSistema> ConfiguracionSistema { get; } = new();

    public ConcurrentDictionary<int, SolicitudPago> Solicitudes { get; } = new();
    public ConcurrentDictionary<int, DocumentoSolicitud> DocumentosSolicitud { get; } = new();
    public ConcurrentDictionary<int, VersionDocumento> VersionesDocumento { get; } = new();

    public ConcurrentDictionary<int, FlujoAprobacion> FlujosAprobacion { get; } = new();
    public ConcurrentDictionary<int, PasoFlujo> PasosFlujo { get; } = new();
    public ConcurrentDictionary<int, InstanciaAprobacion> InstanciasAprobacion { get; } = new();
    public ConcurrentDictionary<int, Aprobacion> Aprobaciones { get; } = new();

    public ConcurrentDictionary<int, Causacion> Causaciones { get; } = new();
    public ConcurrentDictionary<int, RetencionCausacion> RetencionesCausacion { get; } = new();

    public ConcurrentDictionary<int, Pago> Pagos { get; } = new();
    public ConcurrentDictionary<int, DocumentoPago> DocumentosPago { get; } = new();

    public ConcurrentDictionary<int, Notificacion> Notificaciones { get; } = new();
    public ConcurrentBag<RegistroAuditoria> Auditoria { get; } = new();
    public ConcurrentDictionary<string, SecuenciaRadicado> Secuencias { get; } = new();
    public ConcurrentDictionary<int, TrabajoSincronizacion> ColaSincronizacion { get; } = new();
}
