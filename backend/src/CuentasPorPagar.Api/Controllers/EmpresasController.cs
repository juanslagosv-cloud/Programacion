using CuentasPorPagar.Api.Auth;
using CuentasPorPagar.Application.Abstractions.Repositories;
using CuentasPorPagar.Application.Common;
using CuentasPorPagar.Domain.Entities;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace CuentasPorPagar.Api.Controllers;

/// <summary>Maestro de Empresas (sección 57). Requiere sesión; crear/editar requiere admin.configurar.</summary>
[ApiController]
[Route("api/[controller]")]
[Authorize]
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
    [PermisoRequerido(Permisos.AdminConfigurar)]
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
