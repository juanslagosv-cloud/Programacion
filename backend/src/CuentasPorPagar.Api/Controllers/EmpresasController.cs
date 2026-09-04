using CuentasPorPagar.Application.Abstractions.Repositories;
using CuentasPorPagar.Domain.Entities;
using Microsoft.AspNetCore.Mvc;

namespace CuentasPorPagar.Api.Controllers;

/// <summary>
/// Maestro de Empresas (sección 57). Sin [Authorize] todavía: la autenticación/RBAC
/// se conecta en la Fase 3; hasta entonces estos endpoints son solo para validar
/// que el pipeline Controller -> Application -> Repository (Mock/Access) funciona.
/// </summary>
[ApiController]
[Route("api/[controller]")]
public class EmpresasController : ControllerBase
{
    private readonly IEmpresaRepository _empresas;

    public EmpresasController(IEmpresaRepository empresas)
    {
        _empresas = empresas;
    }

    [HttpGet]
    public async Task<IActionResult> Listar(CancellationToken ct)
        => Ok(await _empresas.ListarAsync(ct: ct));

    [HttpGet("{id:int}")]
    public async Task<IActionResult> ObtenerPorId(int id, CancellationToken ct)
    {
        var empresa = await _empresas.ObtenerPorIdAsync(id, ct);
        return empresa is null ? NotFound() : Ok(empresa);
    }

    public record CrearEmpresaRequest(string RazonSocial, string Nit, string NombreCorto);

    [HttpPost]
    public async Task<IActionResult> Crear([FromBody] CrearEmpresaRequest request, CancellationToken ct)
    {
        if (await _empresas.ObtenerPorNitAsync(request.Nit, ct) is not null)
        {
            return Conflict($"Ya existe una empresa con NIT {request.Nit}.");
        }

        var empresa = await _empresas.CrearAsync(new Empresa
        {
            RazonSocial = request.RazonSocial,
            Nit = request.Nit,
            NombreCorto = request.NombreCorto,
            Activa = true
        }, ct);

        return CreatedAtAction(nameof(ObtenerPorId), new { id = empresa.Id }, empresa);
    }
}
