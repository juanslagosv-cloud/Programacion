using CuentasPorPagar.Domain.Entities;
using CuentasPorPagar.Domain.Enums;

namespace CuentasPorPagar.Application.Abstractions.Repositories;

/// <summary>Filtros usados por las distintas bandejas (Solicitante, Aprobador, Contabilidad, Tesorería, buscador).</summary>
public class FiltroSolicitudes
{
    public int? EmpresaId { get; set; }
    public int? ProveedorId { get; set; }
    public int? SolicitanteId { get; set; }
    public int? ProyectoId { get; set; }
    public int? CentroCostoId { get; set; }
    public string? Radicado { get; set; }
    public string? NumeroFactura { get; set; }
    public EstadoSolicitud[]? Estados { get; set; }
    public DateTime? FechaDesde { get; set; }
    public DateTime? FechaHasta { get; set; }
    public int Pagina { get; set; } = 1;
    public int TamanoPagina { get; set; } = 25;
}

public class ResultadoPaginado<T>
{
    public IReadOnlyList<T> Items { get; init; } = Array.Empty<T>();
    public int Total { get; init; }
    public int Pagina { get; init; }
    public int TamanoPagina { get; init; }
}

public interface ISolicitudPagoRepository
{
    Task<SolicitudPago?> ObtenerPorIdAsync(int id, CancellationToken ct = default);
    Task<SolicitudPago?> ObtenerPorRadicadoAsync(string radicado, CancellationToken ct = default);
    Task<ResultadoPaginado<SolicitudPago>> BuscarAsync(FiltroSolicitudes filtro, CancellationToken ct = default);

    /// <summary>Soporte para la detección de posibles facturas duplicadas (sección 17).</summary>
    Task<IReadOnlyList<SolicitudPago>> BuscarPosiblesDuplicadosAsync(
        int empresaId, int proveedorId, string numeroFactura, DateTime fechaEmision, decimal valorBruto, CancellationToken ct = default);

    Task<SolicitudPago> CrearAsync(SolicitudPago solicitud, CancellationToken ct = default);

    /// <summary>
    /// Actualiza datos generales de la solicitud (no el estado). Debe validar
    /// RowVersion para concurrencia optimista (sección 20.2); si no afecta filas,
    /// implementaciones deben lanzar ConcurrenciaException.
    /// </summary>
    Task ActualizarAsync(SolicitudPago solicitud, CancellationToken ct = default);

    /// <summary>
    /// Único método autorizado para persistir un cambio de estado. Debe ser invocado
    /// solo desde Application.Services.WorkflowEngineService, nunca directamente
    /// desde un controlador (regla del punto 99).
    /// </summary>
    Task CambiarEstadoAsync(int solicitudId, EstadoSolicitud nuevoEstado, long rowVersionEsperada, CancellationToken ct = default);
}

public interface IDocumentoSolicitudRepository
{
    Task<IReadOnlyList<DocumentoSolicitud>> ListarPorSolicitudAsync(int solicitudId, CancellationToken ct = default);
    Task<DocumentoSolicitud?> ObtenerPorIdAsync(int id, CancellationToken ct = default);
    Task<DocumentoSolicitud> CrearAsync(DocumentoSolicitud documento, CancellationToken ct = default);
    Task<IReadOnlyList<VersionDocumento>> ObtenerVersionesAsync(int documentoId, CancellationToken ct = default);

    /// <summary>Crea una nueva versión, marca la anterior EsVigente=false (sección 16). No borra nada.</summary>
    Task<VersionDocumento> AgregarVersionAsync(int documentoId, VersionDocumento nuevaVersion, CancellationToken ct = default);
}

public interface IFlujoAprobacionRepository
{
    Task<IReadOnlyList<FlujoAprobacion>> ListarActivosAsync(int? empresaId, CancellationToken ct = default);
    Task<FlujoAprobacion?> ObtenerPorIdAsync(int id, CancellationToken ct = default);
    Task<IReadOnlyList<PasoFlujo>> ObtenerPasosAsync(int flujoId, CancellationToken ct = default);
    Task<FlujoAprobacion> CrearAsync(FlujoAprobacion flujo, CancellationToken ct = default);
    Task<PasoFlujo> AgregarPasoAsync(PasoFlujo paso, CancellationToken ct = default);
}

public interface IAprobacionRepository
{
    Task<InstanciaAprobacion?> ObtenerInstanciaVigenteAsync(int solicitudId, CancellationToken ct = default);
    Task<InstanciaAprobacion> CrearInstanciaAsync(InstanciaAprobacion instancia, CancellationToken ct = default);
    Task ActualizarInstanciaAsync(InstanciaAprobacion instancia, CancellationToken ct = default);

    Task<IReadOnlyList<Aprobacion>> ObtenerDecisionesAsync(int instanciaId, int? pasoId = null, CancellationToken ct = default);
    Task<Aprobacion> RegistrarDecisionAsync(Aprobacion aprobacion, CancellationToken ct = default);

    /// <summary>Bandeja "Mis aprobaciones" (sección 22): solicitudes esperando decisión del usuario (o de quien lo suplanta).</summary>
    Task<ResultadoPaginado<SolicitudPago>> ObtenerPendientesDeAprobadorAsync(int usuarioId, int pagina, int tamanoPagina, CancellationToken ct = default);
}

public interface ICausacionRepository
{
    Task<Causacion?> ObtenerVigentePorSolicitudAsync(int solicitudId, CancellationToken ct = default);
    Task<IReadOnlyList<Causacion>> ObtenerHistorialAsync(int solicitudId, CancellationToken ct = default);
    Task<IReadOnlyList<RetencionCausacion>> ObtenerRetencionesAsync(int causacionId, CancellationToken ct = default);

    /// <summary>Inserta la causación + sus retenciones como una única unidad de trabajo (sección 33/38).</summary>
    Task<Causacion> RegistrarAsync(Causacion causacion, IReadOnlyList<RetencionCausacion> retenciones, CancellationToken ct = default);
}

public interface IPagoRepository
{
    Task<IReadOnlyList<Pago>> ObtenerPorSolicitudAsync(int solicitudId, CancellationToken ct = default);
    Task<decimal> ObtenerSaldoPendienteAsync(int solicitudId, CancellationToken ct = default);
    Task<Pago> RegistrarAsync(Pago pago, CancellationToken ct = default);
    Task<DocumentoPago> AgregarSoporteAsync(DocumentoPago documentoPago, CancellationToken ct = default);
}

public interface INotificacionRepository
{
    Task<Notificacion> CrearAsync(Notificacion notificacion, CancellationToken ct = default);
    Task<IReadOnlyList<Notificacion>> ListarPorUsuarioAsync(int usuarioId, bool soloNoLeidas, CancellationToken ct = default);
    Task MarcarLeidaAsync(int notificacionId, CancellationToken ct = default);
    Task<IReadOnlyList<Notificacion>> ObtenerPendientesDeCorreoAsync(int maxIntentos, CancellationToken ct = default);
    Task MarcarEnvioCorreoAsync(int notificacionId, EstadoEnvio estado, CancellationToken ct = default);
}

public interface IAuditoriaRepository
{
    /// <summary>Único método de escritura: no existe actualización ni borrado (append-only, sección 18).</summary>
    Task RegistrarAsync(RegistroAuditoria registro, CancellationToken ct = default);

    Task<ResultadoPaginado<RegistroAuditoria>> BuscarAsync(
        int? usuarioId, string? modulo, string? entidadTipo, int? entidadId,
        DateTime? desde, DateTime? hasta, int pagina, int tamanoPagina, CancellationToken ct = default);
}

/// <summary>
/// Generación segura del consecutivo de radicado (sección 9/20). La implementación
/// debe combinar: (a) transacción corta a nivel de base de datos, y (b) un mecanismo
/// de exclusión mutua a nivel de aplicación (ver Application.Services.SecuenciaRadicadoService),
/// más un índice único sobre SolicitudesPago.Radicado como última barrera.
/// </summary>
public interface ISecuenciaRadicadoRepository
{
    /// <summary>Incrementa y devuelve el nuevo valor de forma atómica para la clave dada (ej. "RAD-2026").</summary>
    Task<long> ObtenerSiguienteValorAsync(string clave, CancellationToken ct = default);
}

public interface IColaSincronizacionRepository
{
    Task<TrabajoSincronizacion> EncolarAsync(TrabajoSincronizacion trabajo, CancellationToken ct = default);
    Task<IReadOnlyList<TrabajoSincronizacion>> ObtenerPendientesAsync(int maxIntentos, CancellationToken ct = default);
    Task MarcarResultadoAsync(int trabajoId, EstadoTrabajoSincronizacion estado, string? error, CancellationToken ct = default);
}
