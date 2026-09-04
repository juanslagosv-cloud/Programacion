using System.Security.Claims;
using CuentasPorPagar.Api.Auth;
using CuentasPorPagar.Application.Abstractions.Repositories;
using CuentasPorPagar.Application.Common;
using CuentasPorPagar.Application.Services;
using CuentasPorPagar.Domain.Entities;
using CuentasPorPagar.Domain.Enums;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace CuentasPorPagar.Api.Controllers;

/// <summary>
/// Checkpoint de las Fases 2/3: demuestra que crear un borrador y radicarlo pasa
/// realmente por SecuenciaRadicadoService (consecutivo seguro, sección 20),
/// WorkflowEngineService (transición validada + auditoría, sección 9/18/99), y
/// que ambas acciones exigen el permiso correspondiente (sección 8) verificado
/// en el JWT del usuario autenticado — nunca un UsuarioId enviado por el cliente.
///
/// Deliberadamente NO incluye todavía documentos obligatorios ni motor de
/// aprobación (Fases 5-7).
/// </summary>
[ApiController]
[Route("api/[controller]")]
[Authorize]
public class SolicitudesController : ControllerBase
{
    private readonly ISolicitudPagoRepository _solicitudes;
    private readonly SecuenciaRadicadoService _secuenciaRadicado;
    private readonly WorkflowEngineService _workflow;
    private readonly IAuditService _auditoria;

    public SolicitudesController(
        ISolicitudPagoRepository solicitudes,
        SecuenciaRadicadoService secuenciaRadicado,
        WorkflowEngineService workflow,
        IAuditService auditoria)
    {
        _solicitudes = solicitudes;
        _secuenciaRadicado = secuenciaRadicado;
        _workflow = workflow;
        _auditoria = auditoria;
    }

    /// <summary>Id del usuario autenticado, tomado del JWT — nunca confiar en un valor enviado por el cliente.</summary>
    private int UsuarioIdActual => int.Parse(User.FindFirstValue(ClaimTypes.NameIdentifier) ?? User.FindFirstValue("sub")!);

    [HttpGet("{id:int}")]
    public async Task<IActionResult> ObtenerPorId(int id, CancellationToken ct)
    {
        var solicitud = await _solicitudes.ObtenerPorIdAsync(id, ct);
        return solicitud is null ? NotFound() : Ok(solicitud);
    }

    [HttpGet]
    public async Task<IActionResult> Buscar([FromQuery] FiltroSolicitudes filtro, CancellationToken ct)
        => Ok(await _solicitudes.BuscarAsync(filtro, ct));

    public record CrearBorradorRequest(
        int EmpresaId, int TipoSolicitudId, int ProveedorId, string TipoDocumento,
        string? NumeroFactura, DateTime FechaEmision, DateTime FechaVencimiento,
        decimal ValorAntesImpuestos, decimal Iva, decimal ValorBruto, string Concepto,
        int? ProyectoId, int? CentroCostoId, int ResponsableId);

    [HttpPost("borradores")]
    [PermisoRequerido(Permisos.SolicitudCrear)]
    public async Task<IActionResult> CrearBorrador([FromBody] CrearBorradorRequest request, CancellationToken ct)
    {
        // Detección de posibles facturas duplicadas (sección 17): informativa, no bloqueante.
        var duplicados = !string.IsNullOrWhiteSpace(request.NumeroFactura)
            ? await _solicitudes.BuscarPosiblesDuplicadosAsync(
                request.EmpresaId, request.ProveedorId, request.NumeroFactura, request.FechaEmision, request.ValorBruto, ct)
            : Array.Empty<SolicitudPago>();

        var solicitanteId = UsuarioIdActual;

        var solicitud = await _solicitudes.CrearAsync(new SolicitudPago
        {
            Radicado = string.Empty, // se asigna únicamente al radicar (sección 9)
            EmpresaId = request.EmpresaId,
            TipoSolicitudId = request.TipoSolicitudId,
            ProveedorId = request.ProveedorId,
            TipoDocumento = request.TipoDocumento,
            NumeroFactura = request.NumeroFactura,
            FechaEmision = request.FechaEmision,
            FechaVencimiento = request.FechaVencimiento,
            ValorAntesImpuestos = request.ValorAntesImpuestos,
            Iva = request.Iva,
            ValorBruto = request.ValorBruto,
            Concepto = request.Concepto,
            ProyectoId = request.ProyectoId,
            CentroCostoId = request.CentroCostoId,
            ResponsableId = request.ResponsableId,
            SolicitanteId = solicitanteId,
            Estado = EstadoSolicitud.Borrador
        }, ct);

        await _auditoria.RegistrarAsync(
            solicitanteId, "Crear", "Solicitudes", nameof(SolicitudPago), solicitud.Id,
            valorAnterior: null, valorNuevo: "Borrador", comentario: null, ct: ct);

        return Ok(new
        {
            solicitud,
            posiblesDuplicados = duplicados.Select(d => new { d.Id, d.Radicado }).ToArray()
        });
    }

    [HttpPost("{id:int}/radicar")]
    [PermisoRequerido(Permisos.SolicitudRadicar)]
    public async Task<IActionResult> Radicar(int id, CancellationToken ct)
    {
        var solicitud = await _solicitudes.ObtenerPorIdAsync(id, ct);
        if (solicitud is null) return NotFound();

        if (solicitud.Estado is not (EstadoSolicitud.Borrador or EstadoSolicitud.DevueltoParaCorreccion))
        {
            return Conflict($"No se puede radicar una solicitud en estado {solicitud.Estado}.");
        }

        if (string.IsNullOrEmpty(solicitud.Radicado))
        {
            solicitud.Radicado = await _secuenciaRadicado.GenerarRadicadoAsync(DateTime.UtcNow.Year, ct: ct);
            await _solicitudes.ActualizarAsync(solicitud, ct);
        }

        // TODO (Fase 5/6): validar documentos obligatorios dinámicos antes de permitir
        // el paso a PendienteDeAprobacion (sección 12). Por ahora transiciona directo.
        await _workflow.TransicionarAsync(solicitud, EstadoSolicitud.Radicado, UsuarioIdActual, "Solicitudes", ct: ct);

        return Ok(solicitud);
    }
}
