using CuentasPorPagar.Application.Abstractions.Repositories;
using CuentasPorPagar.Domain.Entities;

namespace CuentasPorPagar.Infrastructure.Mock;

public class MockUsuarioRepository : IUsuarioRepository
{
    private readonly InMemoryDataStore _store;
    public MockUsuarioRepository(InMemoryDataStore store) => _store = store;

    public Task<Usuario?> ObtenerPorIdAsync(int id, CancellationToken ct = default)
        => Task.FromResult(_store.Usuarios.GetValueOrDefault(id));

    public Task<Usuario?> ObtenerPorCorreoAsync(string correo, CancellationToken ct = default)
        => Task.FromResult(_store.Usuarios.Values.FirstOrDefault(u =>
            string.Equals(u.Correo, correo, StringComparison.OrdinalIgnoreCase)));

    public Task<Usuario?> ObtenerPorGoogleSubAsync(string googleSub, CancellationToken ct = default)
        => Task.FromResult(_store.Usuarios.Values.FirstOrDefault(u => u.GoogleSub == googleSub));

    public Task<IReadOnlyList<Usuario>> ListarAsync(CancellationToken ct = default)
        => Task.FromResult<IReadOnlyList<Usuario>>(_store.Usuarios.Values.Where(u => !u.EliminadoLogico).ToList());

    public Task<Usuario> CrearAsync(Usuario usuario, CancellationToken ct = default)
    {
        usuario.Id = _store.SiguienteId();
        usuario.RowVersion = 1;
        _store.Usuarios[usuario.Id] = usuario;
        return Task.FromResult(usuario);
    }

    public Task ActualizarAsync(Usuario usuario, CancellationToken ct = default)
    {
        usuario.RowVersion++;
        _store.Usuarios[usuario.Id] = usuario;
        return Task.CompletedTask;
    }

    public Task RegistrarLoginAsync(int usuarioId, DateTime fechaHora, CancellationToken ct = default)
    {
        if (_store.Usuarios.TryGetValue(usuarioId, out var usuario))
        {
            usuario.UltimoLogin = fechaHora;
        }
        return Task.CompletedTask;
    }

    public Task<IReadOnlyList<(int RolId, string NombreRol, int? EmpresaId)>> ObtenerRolesAsync(int usuarioId, CancellationToken ct = default)
    {
        var roles = _store.UsuariosRoles
            .Where(ur => ur.UsuarioId == usuarioId)
            .Select(ur => (ur.RolId, _store.Roles.GetValueOrDefault(ur.RolId)?.Nombre ?? "", ur.EmpresaId))
            .ToList();
        return Task.FromResult<IReadOnlyList<(int, string, int?)>>(roles);
    }

    public Task<IReadOnlyList<string>> ObtenerPermisosAsync(int usuarioId, CancellationToken ct = default)
    {
        var rolIds = _store.UsuariosRoles.Where(ur => ur.UsuarioId == usuarioId).Select(ur => ur.RolId).ToHashSet();
        var permisoIds = _store.RolesPermisos.Where(rp => rolIds.Contains(rp.RolId)).Select(rp => rp.PermisoId).ToHashSet();
        var codigos = _store.Permisos.Values.Where(p => permisoIds.Contains(p.Id)).Select(p => p.Codigo).Distinct().ToList();
        return Task.FromResult<IReadOnlyList<string>>(codigos);
    }
}

public class MockRolRepository : IRolRepository
{
    private readonly InMemoryDataStore _store;
    public MockRolRepository(InMemoryDataStore store) => _store = store;

    public Task<IReadOnlyList<Rol>> ListarAsync(CancellationToken ct = default)
        => Task.FromResult<IReadOnlyList<Rol>>(_store.Roles.Values.ToList());

    public Task<Rol?> ObtenerPorIdAsync(int id, CancellationToken ct = default)
        => Task.FromResult(_store.Roles.GetValueOrDefault(id));

    public Task<Rol> CrearAsync(Rol rol, CancellationToken ct = default)
    {
        rol.Id = _store.SiguienteId();
        _store.Roles[rol.Id] = rol;
        return Task.FromResult(rol);
    }

    public Task ActualizarAsync(Rol rol, CancellationToken ct = default)
    {
        _store.Roles[rol.Id] = rol;
        return Task.CompletedTask;
    }

    public Task<IReadOnlyList<Permiso>> ObtenerPermisosDelRolAsync(int rolId, CancellationToken ct = default)
    {
        var permisoIds = _store.RolesPermisos.Where(rp => rp.RolId == rolId).Select(rp => rp.PermisoId).ToHashSet();
        return Task.FromResult<IReadOnlyList<Permiso>>(_store.Permisos.Values.Where(p => permisoIds.Contains(p.Id)).ToList());
    }

    public Task AsignarPermisoAsync(int rolId, int permisoId, CancellationToken ct = default)
    {
        _store.RolesPermisos.Add(new RolPermiso { RolId = rolId, PermisoId = permisoId });
        return Task.CompletedTask;
    }

    public Task RevocarPermisoAsync(int rolId, int permisoId, CancellationToken ct = default)
        => Task.CompletedTask; // ConcurrentBag no soporta remoción; aceptable para Mock (ver Access para semántica real)

    public Task AsignarRolAUsuarioAsync(int usuarioId, int rolId, int? empresaId, CancellationToken ct = default)
    {
        _store.UsuariosRoles.Add(new UsuarioRol { UsuarioId = usuarioId, RolId = rolId, EmpresaId = empresaId });
        return Task.CompletedTask;
    }

    public Task RevocarRolDeUsuarioAsync(int usuarioId, int rolId, int? empresaId, CancellationToken ct = default)
        => Task.CompletedTask;
}

public class MockPermisoRepository : IPermisoRepository
{
    private readonly InMemoryDataStore _store;
    public MockPermisoRepository(InMemoryDataStore store) => _store = store;

    public Task<IReadOnlyList<Permiso>> ListarAsync(CancellationToken ct = default)
        => Task.FromResult<IReadOnlyList<Permiso>>(_store.Permisos.Values.ToList());

    public Task<Permiso> CrearAsync(Permiso permiso, CancellationToken ct = default)
    {
        permiso.Id = _store.SiguienteId();
        _store.Permisos[permiso.Id] = permiso;
        return Task.FromResult(permiso);
    }
}

public class MockDelegacionRepository : IDelegacionRepository
{
    private readonly InMemoryDataStore _store;
    public MockDelegacionRepository(InMemoryDataStore store) => _store = store;

    public Task<IReadOnlyList<Delegacion>> ListarVigentesAsync(DateTime fecha, CancellationToken ct = default)
        => Task.FromResult<IReadOnlyList<Delegacion>>(_store.Delegaciones.Values.Where(d => d.EstaVigente(fecha)).ToList());

    public Task<Delegacion?> ObtenerSuplenciaVigenteAsync(int titularId, int rolId, DateTime fecha, CancellationToken ct = default)
        => Task.FromResult(_store.Delegaciones.Values.FirstOrDefault(d =>
            d.TitularId == titularId && d.RolId == rolId && d.EstaVigente(fecha)));

    public Task<Delegacion> CrearAsync(Delegacion delegacion, CancellationToken ct = default)
    {
        delegacion.Id = _store.SiguienteId();
        _store.Delegaciones[delegacion.Id] = delegacion;
        return Task.FromResult(delegacion);
    }
}
