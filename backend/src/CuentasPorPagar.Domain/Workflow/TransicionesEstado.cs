using CuentasPorPagar.Domain.Enums;

namespace CuentasPorPagar.Domain.Workflow;

/// <summary>
/// Tabla única de transiciones válidas de la máquina de estados (sección 9 y regla
/// fundamental del punto 99: "nadie debe poder saltarse etapas manualmente").
///
/// Esta tabla es la única fuente de verdad sobre qué transición es legal. Ningún
/// controlador ni repositorio debe escribir <see cref="SolicitudPago.Estado"/>
/// directamente: siempre a través de WorkflowEngineService.Transicionar, que
/// consulta <see cref="EsTransicionValida"/> antes de aplicar el cambio.
/// </summary>
public static class TransicionesEstado
{
    private static readonly Dictionary<EstadoSolicitud, EstadoSolicitud[]> Transiciones = new()
    {
        [EstadoSolicitud.Borrador] = new[] { EstadoSolicitud.Radicado },
        [EstadoSolicitud.Radicado] = new[] { EstadoSolicitud.PendienteDeRevision, EstadoSolicitud.PendienteDeAprobacion },
        [EstadoSolicitud.PendienteDeRevision] = new[] { EstadoSolicitud.PendienteDeAprobacion, EstadoSolicitud.DevueltoParaCorreccion },
        [EstadoSolicitud.PendienteDeAprobacion] = new[] { EstadoSolicitud.PendienteDeAprobacion, EstadoSolicitud.Aprobado, EstadoSolicitud.DevueltoParaCorreccion, EstadoSolicitud.Rechazado },
        [EstadoSolicitud.DevueltoParaCorreccion] = new[] { EstadoSolicitud.Radicado },
        [EstadoSolicitud.Rechazado] = Array.Empty<EstadoSolicitud>(),
        [EstadoSolicitud.Aprobado] = new[] { EstadoSolicitud.PendienteDeCausacion },
        [EstadoSolicitud.PendienteDeCausacion] = new[] { EstadoSolicitud.Causado, EstadoSolicitud.DevueltoPorContabilidad },
        [EstadoSolicitud.DevueltoPorContabilidad] = new[] { EstadoSolicitud.Radicado, EstadoSolicitud.PendienteDeAprobacion },
        [EstadoSolicitud.Causado] = new[] { EstadoSolicitud.PagoProgramado, EstadoSolicitud.DevueltoPorContabilidad },
        [EstadoSolicitud.PagoProgramado] = new[] { EstadoSolicitud.PagoParcial, EstadoSolicitud.Pagado, EstadoSolicitud.DevueltoPorContabilidad },
        [EstadoSolicitud.PagoParcial] = new[] { EstadoSolicitud.PagoParcial, EstadoSolicitud.Pagado },
        [EstadoSolicitud.Pagado] = new[] { EstadoSolicitud.Cerrado },
        [EstadoSolicitud.Cerrado] = Array.Empty<EstadoSolicitud>(),
        [EstadoSolicitud.Anulado] = Array.Empty<EstadoSolicitud>(),
    };

    /// <summary>
    /// Estados desde los cuales un Administrador puede anular una solicitud
    /// (nunca después de Pagado, sección 27 del requerimiento).
    /// </summary>
    public static readonly EstadoSolicitud[] EstadosAnulables =
    {
        EstadoSolicitud.Borrador, EstadoSolicitud.Radicado, EstadoSolicitud.PendienteDeRevision,
        EstadoSolicitud.PendienteDeAprobacion, EstadoSolicitud.DevueltoParaCorreccion,
        EstadoSolicitud.Aprobado, EstadoSolicitud.PendienteDeCausacion,
        EstadoSolicitud.DevueltoPorContabilidad, EstadoSolicitud.Causado
    };

    public static bool EsTransicionValida(EstadoSolicitud origen, EstadoSolicitud destino)
    {
        if (destino == EstadoSolicitud.Anulado)
        {
            return EstadosAnulables.Contains(origen);
        }

        return Transiciones.TryGetValue(origen, out var permitidos) && permitidos.Contains(destino);
    }
}
