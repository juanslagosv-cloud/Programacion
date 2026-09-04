using CuentasPorPagar.Application.Abstractions.Integrations;
using CuentasPorPagar.Application.Abstractions.Repositories;
using CuentasPorPagar.Application.Common;
using CuentasPorPagar.Domain.Entities;

namespace CuentasPorPagar.Application.Services;

public record ResultadoAutenticacion(
    Usuario Usuario,
    IReadOnlyList<string> Permisos,
    IReadOnlyList<(int RolId, string NombreRol, int? EmpresaId)> Roles);

/// <summary>
/// Orquesta el login (sección 4): valida el token externo (Google real o Mock,
/// según IAuthProvider registrado), exige que el usuario exista y esté Activo en
/// la tabla Usuarios, registra el inicio de sesión y audita el evento. La emisión
/// del JWT de sesión de la aplicación queda fuera de este servicio (vive en la
/// API, que es quien conoce la clave de firma) — esto es justamente lo que
/// mantiene la autenticación desacoplada del resto de la aplicación.
/// </summary>
public interface IAutenticacionService
{
    Task<ResultadoAutenticacion> AutenticarAsync(string tokenExterno, CancellationToken ct = default);
}

public class AutenticacionService : IAutenticacionService
{
    private readonly IAuthProvider _authProvider;
    private readonly IUsuarioRepository _usuarios;
    private readonly IAuditService _auditoria;

    public AutenticacionService(IAuthProvider authProvider, IUsuarioRepository usuarios, IAuditService auditoria)
    {
        _authProvider = authProvider;
        _usuarios = usuarios;
        _auditoria = auditoria;
    }

    public async Task<ResultadoAutenticacion> AutenticarAsync(string tokenExterno, CancellationToken ct = default)
    {
        var identidad = await _authProvider.ValidarTokenAsync(tokenExterno, ct);
        if (identidad is null)
        {
            throw new AutenticacionInvalidaException("El token de identidad no pudo validarse.");
        }

        var usuario = await _usuarios.ObtenerPorCorreoAsync(identidad.Correo, ct);
        if (usuario is null || !usuario.Activo)
        {
            // Auditamos el intento fallido con UsuarioId=0 (usuario desconocido/no autorizado
            // para el sistema) — nunca se crea una cuenta automáticamente desde el login.
            await _auditoria.RegistrarAsync(
                usuarioId: 0, accion: "LoginRechazado", modulo: "Autenticacion", entidadTipo: "Correo",
                entidadId: 0, valorAnterior: null, valorNuevo: identidad.Correo,
                comentario: "El correo no existe o no está activo en Usuarios.", resultado: "Rechazado", ct: ct);

            throw new AutenticacionInvalidaException(
                $"El usuario {identidad.Correo} no existe o no está activo en el sistema. Contacte al administrador.");
        }

        if (string.IsNullOrEmpty(usuario.GoogleSub) && !string.IsNullOrEmpty(identidad.Sub))
        {
            usuario.GoogleSub = identidad.Sub;
            await _usuarios.ActualizarAsync(usuario, ct);
        }

        await _usuarios.RegistrarLoginAsync(usuario.Id, DateTime.UtcNow, ct);

        var roles = await _usuarios.ObtenerRolesAsync(usuario.Id, ct);
        var permisos = await _usuarios.ObtenerPermisosAsync(usuario.Id, ct);

        await _auditoria.RegistrarAsync(
            usuario.Id, "Login", "Autenticacion", nameof(Usuario), usuario.Id,
            valorAnterior: null, valorNuevo: null, comentario: null, resultado: "Exitoso", ct: ct);

        return new ResultadoAutenticacion(usuario, permisos, roles);
    }
}
