using CuentasPorPagar.Application.Abstractions.Repositories;
using CuentasPorPagar.Application.Services;
using CuentasPorPagar.Domain.Entities;
using CuentasPorPagar.Domain.Enums;
using Microsoft.AspNetCore.Mvc;

namespace CuentasPorPagar.Api.Controllers;

/// <summary>
/// Checkpoint de la Fase 2: demuestra que crear un borrador y radicarlo pasa
/// realmente por SecuenciaRadicadoService (consecutivo seguro, sección 20) y
/// WorkflowEngineService (transición validada + auditoría, sección 9/18/99).
///
/// Deliberadamente NO incluye todavía documentos obligatorios, motor de
/// aprobación, ni permisos (Fases 5-7); el usuario actuante se recibe por
/// query string como sustituto temporal del usuario autenticado (Fase 3).
/// </summary>
[ApiController]
[Route("api/[controller]")]
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
        int? ProyectoId, int? CentroCostoId, int ResponsableId, int SolicitanteId);

    [HttpPost("borradores")]
    public async Task<IActionResult> CrearBorrador([FromBody] CrearBorradorRequest request, CancellationToken ct)
    {
        // Detección de posibles facturas duplicadas (sección 17): informativa, no bloqueante.
        var duplicados = !string.IsNullOrWhiteSpace(request.NumeroFactura)
            ? await _solicitudes.BuscarPosiblesDuplicadosAsync(
                request.EmpresaId, request.ProveedorId, request.NumeroFactura, request.FechaEmision, request.ValorBruto, ct)
            : Array.Empty<SolicitudPago>();

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
            SolicitanteId = request.SolicitanteId,
            Estado = EstadoSolicitud.Borrador
        }, ct);

        await _auditoria.RegistrarAsync(
            request.SolicitanteId, "Crear", "Solicitudes", nameof(SolicitudPago), solicitud.Id,
            valorAnterior: null, valorNuevo: "Borrador", comentario: null, ct: ct);

        return Ok(new
        {
            solicitud,
            posiblesDuplicados = duplicados.Select(d => new { d.Id, d.Radicado }).ToArray()
        });
    }

    public record RadicarRequest(int UsuarioId);

    [HttpPost("{id:int}/radicar")]
    public async Task<IActionResult> Radicar(int id, [FromBody] RadicarRequest request, CancellationToken ct)
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
        await _workflow.TransicionarAsync(solicitud, EstadoSolicitud.Radicado, request.UsuarioId, "Solicitudes", ct: ct);

        return Ok(solicitud);
    }
}
