using CuentasPorPagar.Domain.Entities;

namespace CuentasPorPagar.Application.Abstractions.Repositories;

public interface IUsuarioRepository
{
    Task<Usuario?> ObtenerPorIdAsync(int id, CancellationToken ct = default);
    Task<Usuario?> ObtenerPorCorreoAsync(string correo, CancellationToken ct = default);
    Task<Usuario?> ObtenerPorGoogleSubAsync(string googleSub, CancellationToken ct = default);
    Task<IReadOnlyList<Usuario>> ListarAsync(CancellationToken ct = default);
    Task<Usuario> CrearAsync(Usuario usuario, CancellationToken ct = default);
    Task ActualizarAsync(Usuario usuario, CancellationToken ct = default);
    Task RegistrarLoginAsync(int usuarioId, DateTime fechaHora, CancellationToken ct = default);

    /// <summary>Roles del usuario, opcionalmente acotados a una empresa (punto 3).</summary>
    Task<IReadOnlyList<(int RolId, string NombreRol, int? EmpresaId)>> ObtenerRolesAsync(int usuarioId, CancellationToken ct = default);

    /// <summary>Códigos de permiso efectivos del usuario (unión de todos sus roles).</summary>
    Task<IReadOnlyList<string>> ObtenerPermisosAsync(int usuarioId, CancellationToken ct = default);
}

public interface IRolRepository
{
    Task<IReadOnlyList<Rol>> ListarAsync(CancellationToken ct = default);
    Task<Rol?> ObtenerPorIdAsync(int id, CancellationToken ct = default);
    Task<Rol> CrearAsync(Rol rol, CancellationToken ct = default);
    Task ActualizarAsync(Rol rol, CancellationToken ct = default);
    Task<IReadOnlyList<Permiso>> ObtenerPermisosDelRolAsync(int rolId, CancellationToken ct = default);
    Task AsignarPermisoAsync(int rolId, int permisoId, CancellationToken ct = default);
    Task RevocarPermisoAsync(int rolId, int permisoId, CancellationToken ct = default);
    Task AsignarRolAUsuarioAsync(int usuarioId, int rolId, int? empresaId, CancellationToken ct = default);
    Task RevocarRolDeUsuarioAsync(int usuarioId, int rolId, int? empresaId, CancellationToken ct = default);
}

public interface IPermisoRepository
{
    Task<IReadOnlyList<Permiso>> ListarAsync(CancellationToken ct = default);
    Task<Permiso> CrearAsync(Permiso permiso, CancellationToken ct = default);
}

public interface IDelegacionRepository
{
    Task<IReadOnlyList<Delegacion>> ListarVigentesAsync(DateTime fecha, CancellationToken ct = default);
    Task<Delegacion?> ObtenerSuplenciaVigenteAsync(int titularId, int rolId, DateTime fecha, CancellationToken ct = default);
    Task<Delegacion> CrearAsync(Delegacion delegacion, CancellationToken ct = default);
}
