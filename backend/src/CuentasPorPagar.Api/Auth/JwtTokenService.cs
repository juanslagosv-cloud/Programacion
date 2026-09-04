using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using CuentasPorPagar.Domain.Entities;
using Microsoft.Extensions.Options;
using Microsoft.IdentityModel.Tokens;

namespace CuentasPorPagar.Api.Auth;

public interface IJwtTokenService
{
    /// <summary>
    /// Emite el JWT de sesión. Los permisos se incluyen como claims para que la
    /// autorización (PermisoRequeridoAttribute) no dependa de una consulta a base
    /// de datos en cada request; el costo es que una revocación de permiso no
    /// tiene efecto hasta que el token expira o se vuelve a iniciar sesión — por
    /// eso la expiración se mantiene corta (sección 19).
    /// </summary>
    string EmitirToken(Usuario usuario, IReadOnlyList<string> permisos, IReadOnlyList<(int RolId, string NombreRol, int? EmpresaId)> roles);
}

public class JwtTokenService : IJwtTokenService
{
    private readonly JwtOptions _options;

    public JwtTokenService(IOptions<JwtOptions> options)
    {
        _options = options.Value;
        if (string.IsNullOrWhiteSpace(_options.SigningKey))
        {
            throw new InvalidOperationException(
                "Jwt:SigningKey no está configurado. Defina una clave de firma (ver .env.example, JWT_SIGNING_KEY).");
        }
    }

    public string EmitirToken(Usuario usuario, IReadOnlyList<string> permisos, IReadOnlyList<(int RolId, string NombreRol, int? EmpresaId)> roles)
    {
        var claims = new List<Claim>
        {
            new(JwtRegisteredClaimNames.Sub, usuario.Id.ToString()),
            new(JwtRegisteredClaimNames.Email, usuario.Correo),
            new("nombre", usuario.Nombre),
            new(JwtRegisteredClaimNames.Jti, Guid.NewGuid().ToString())
        };

        claims.AddRange(permisos.Distinct().Select(p => new Claim("permiso", p)));
        claims.AddRange(roles.Select(r => r.EmpresaId is null
            ? new Claim("rol", r.NombreRol)
            : new Claim("rol", $"{r.NombreRol}:{r.EmpresaId}")));

        var credenciales = new SigningCredentials(
            new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_options.SigningKey)), SecurityAlgorithms.HmacSha256);

        var token = new JwtSecurityToken(
            issuer: _options.Issuer,
            audience: _options.Audience,
            claims: claims,
            expires: DateTime.UtcNow.AddMinutes(_options.ExpiracionMinutos),
            signingCredentials: credenciales);

        return new JwtSecurityTokenHandler().WriteToken(token);
    }
}
