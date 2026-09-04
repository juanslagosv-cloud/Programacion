using System.Security.Claims;
using CuentasPorPagar.Api.Auth;
using CuentasPorPagar.Application.Abstractions.Repositories;
using CuentasPorPagar.Application.Common;
using CuentasPorPagar.Application.Services;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace CuentasPorPagar.Api.Controllers;

/// <summary>
/// Login (sección 4). POST /login recibe el token externo (id_token de Google en
/// producción; "mock:correo:nombre" cuando IntegrationMode=mock, ver
/// MockAuthProvider) y devuelve el JWT propio de la aplicación + el perfil del
/// usuario. La autenticación queda desacoplada: este controlador no sabe si
/// detrás hay Google real o el simulador.
/// </summary>
[ApiController]
[Route("api/auth")]
public class AuthController : ControllerBase
{
    private readonly IAutenticacionService _autenticacion;
    private readonly IJwtTokenService _jwt;
    private readonly IUsuarioRepository _usuarios;

    public AuthController(IAutenticacionService autenticacion, IJwtTokenService jwt, IUsuarioRepository usuarios)
    {
        _autenticacion = autenticacion;
        _jwt = jwt;
        _usuarios = usuarios;
    }

    public record LoginRequest(string Token);

    public record PerfilResponse(int Id, string Nombre, string Correo, string[] Roles, string[] Permisos);

    [HttpPost("login")]
    [AllowAnonymous]
    public async Task<IActionResult> Login([FromBody] LoginRequest request, CancellationToken ct)
    {
        try
        {
            var resultado = await _autenticacion.AutenticarAsync(request.Token, ct);
            var jwt = _jwt.EmitirToken(resultado.Usuario, resultado.Permisos, resultado.Roles);

            return Ok(new
            {
                token = jwt,
                perfil = new PerfilResponse(
                    resultado.Usuario.Id,
                    resultado.Usuario.Nombre,
                    resultado.Usuario.Correo,
                    resultado.Roles.Select(r => r.NombreRol).Distinct().ToArray(),
                    resultado.Permisos.ToArray())
            });
        }
        catch (AutenticacionInvalidaException ex)
        {
            // 401 y no 403: todavía no sabemos "quién" es para hablar de permisos,
            // el login mismo fue rechazado (sección 4).
            return Unauthorized(new { error = ex.Message });
        }
    }

    [HttpGet("me")]
    [Authorize]
    public async Task<IActionResult> Perfil(CancellationToken ct)
    {
        var usuarioId = int.Parse(User.FindFirstValue(ClaimTypes.NameIdentifier)
            ?? User.FindFirstValue("sub")!);

        var usuario = await _usuarios.ObtenerPorIdAsync(usuarioId, ct);
        if (usuario is null || !usuario.Activo) return Unauthorized();

        // Se re-consulta en vivo (no solo se leen los claims del JWT) para que el
        // perfil mostrado en pantalla refleje cambios de rol recientes, aunque la
        // AUTORIZACIÓN de cada endpoint sí siga usando los claims del token
        // vigente hasta que este expire (sección 19).
        var roles = await _usuarios.ObtenerRolesAsync(usuario.Id, ct);
        var permisos = await _usuarios.ObtenerPermisosAsync(usuario.Id, ct);

        return Ok(new PerfilResponse(
            usuario.Id, usuario.Nombre, usuario.Correo,
            roles.Select(r => r.NombreRol).Distinct().ToArray(), permisos.ToArray()));
    }
}
