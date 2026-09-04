using CuentasPorPagar.Application.Abstractions.Repositories;
using CuentasPorPagar.Application.Common;
using CuentasPorPagar.Domain.Entities;
using CuentasPorPagar.Domain.Enums;
using CuentasPorPagar.Domain.Workflow;

namespace CuentasPorPagar.Application.Services;

/// <summary>
/// Único punto autorizado para cambiar el estado de una SolicitudPago (punto 99:
/// "toda transición debe estar controlada por el motor de workflow"). Valida contra
/// <see cref="TransicionesEstado"/> y delega la escritura, con concurrencia
/// optimista, al repositorio.
/// </summary>
public class WorkflowEngineService
{
    private readonly ISolicitudPagoRepository _solicitudes;
    private readonly IAuditService _auditoria;

    public WorkflowEngineService(ISolicitudPagoRepository solicitudes, IAuditService auditoria)
    {
        _solicitudes = solicitudes;
        _auditoria = auditoria;
    }

    public async Task TransicionarAsync(
        SolicitudPago solicitud, EstadoSolicitud nuevoEstado, int usuarioId, string modulo, string? comentario = null, CancellationToken ct = default)
    {
        if (!TransicionesEstado.EsTransicionValida(solicitud.Estado, nuevoEstado))
        {
            throw new TransicionInvalidaException(solicitud.Estado.ToString(), nuevoEstado.ToString());
        }

        var estadoAnterior = solicitud.Estado;

        try
        {
            await _solicitudes.CambiarEstadoAsync(solicitud.Id, nuevoEstado, solicitud.RowVersion, ct);
        }
        catch (ConcurrenciaException)
        {
            await _auditoria.RegistrarAsync(usuarioId, "CambioEstado", modulo, nameof(SolicitudPago), solicitud.Id,
                valorAnterior: estadoAnterior.ToString(), valorNuevo: nuevoEstado.ToString(), comentario, resultado: "ConflictoConcurrencia", ct);
            throw;
        }

        solicitud.Estado = nuevoEstado;

        await _auditoria.RegistrarAsync(usuarioId, "CambioEstado", modulo, nameof(SolicitudPago), solicitud.Id,
            valorAnterior: estadoAnterior.ToString(), valorNuevo: nuevoEstado.ToString(), comentario, resultado: "Exitoso", ct);
    }
}
