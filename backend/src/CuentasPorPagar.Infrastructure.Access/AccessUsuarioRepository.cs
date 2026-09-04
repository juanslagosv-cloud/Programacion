using System.Data.Common;
using System.Data.OleDb;
using CuentasPorPagar.Application.Abstractions.Repositories;
using CuentasPorPagar.Domain.Entities;

namespace CuentasPorPagar.Infrastructure.Access;

/// <summary>
/// Implementación de referencia para autenticación (sección 4): tras validar el
/// id_token de Google (IAuthProvider), el login exige que el correo exista y
/// esté Activo en esta tabla — el login de Google por sí solo no basta.
/// </summary>
public class AccessUsuarioRepository : IUsuarioRepository
{
    private readonly AccessConnectionFactory _connectionFactory;

    public AccessUsuarioRepository(AccessConnectionFactory connectionFactory)
    {
        _connectionFactory = connectionFactory;
    }

    private const string ColumnasSelect = "Id, GoogleSub, Correo, Nombre, Activo, UltimoLogin, FechaCreacion, RowVersion, EliminadoLogico";

    private static Usuario Mapear(DbDataReader lector) => new()
    {
        Id = lector.GetInt32(0),
        GoogleSub = lector.IsDBNull(1) ? string.Empty : lector.GetString(1),
        Correo = lector.GetString(2),
        Nombre = lector.GetString(3),
        Activo = lector.GetBoolean(4),
        UltimoLogin = lector.IsDBNull(5) ? null : lector.GetDateTime(5),
        FechaCreacion = lector.GetDateTime(6),
        RowVersion = Convert.ToInt64(lector.GetValue(7)),
        EliminadoLogico = lector.GetBoolean(8)
    };

    public async Task<Usuario?> ObtenerPorIdAsync(int id, CancellationToken ct = default)
    {
        using var conexion = await _connectionFactory.AbrirAsync(ct);
        using var comando = new OleDbCommand($"SELECT {ColumnasSelect} FROM Usuarios WHERE Id = ?", conexion);
        comando.Parameters.AddWithValue("@Id", id);
        using var lector = await comando.ExecuteReaderAsync(ct);
        return await lector.ReadAsync(ct) ? Mapear(lector) : null;
    }

    public async Task<Usuario?> ObtenerPorCorreoAsync(string correo, CancellationToken ct = default)
    {
        using var conexion = await _connectionFactory.AbrirAsync(ct);
        using var comando = new OleDbCommand($"SELECT {ColumnasSelect} FROM Usuarios WHERE Correo = ?", conexion);
        comando.Parameters.AddWithValue("@Correo", correo);
        using var lector = await comando.ExecuteReaderAsync(ct);
        return await lector.ReadAsync(ct) ? Mapear(lector) : null;
    }

    public async Task<Usuario?> ObtenerPorGoogleSubAsync(string googleSub, CancellationToken ct = default)
    {
        using var conexion = await _connectionFactory.AbrirAsync(ct);
        using var comando = new OleDbCommand($"SELECT {ColumnasSelect} FROM Usuarios WHERE GoogleSub = ?", conexion);
        comando.Parameters.AddWithValue("@GoogleSub", googleSub);
        using var lector = await comando.ExecuteReaderAsync(ct);
        return await lector.ReadAsync(ct) ? Mapear(lector) : null;
    }

    public async Task<IReadOnlyList<Usuario>> ListarAsync(CancellationToken ct = default)
    {
        using var conexion = await _connectionFactory.AbrirAsync(ct);
        using var comando = new OleDbCommand($"SELECT {ColumnasSelect} FROM Usuarios WHERE EliminadoLogico = False", conexion);
        using var lector = await comando.ExecuteReaderAsync(ct);
        var resultado = new List<Usuario>();
        while (await lector.ReadAsync(ct)) resultado.Add(Mapear(lector));
        return resultado;
    }

    public async Task<Usuario> CrearAsync(Usuario usuario, CancellationToken ct = default)
    {
        using var conexion = await _connectionFactory.AbrirAsync(ct);
        using var comando = new OleDbCommand(
            "INSERT INTO Usuarios (GoogleSub, Correo, Nombre, Activo, FechaCreacion, RowVersion, EliminadoLogico) " +
            "VALUES (?, ?, ?, ?, ?, 1, False)", conexion);
        comando.Parameters.AddWithValue("@GoogleSub", usuario.GoogleSub);
        comando.Parameters.AddWithValue("@Correo", usuario.Correo);
        comando.Parameters.AddWithValue("@Nombre", usuario.Nombre);
        comando.Parameters.AddWithValue("@Activo", usuario.Activo);
        comando.Parameters.AddWithValue("@FechaCreacion", usuario.FechaCreacion);
        await comando.ExecuteNonQueryAsync(ct);

        using var idComando = new OleDbCommand("SELECT @@IDENTITY", conexion);
        usuario.Id = Convert.ToInt32(await idComando.ExecuteScalarAsync(ct));
        usuario.RowVersion = 1;
        return usuario;
    }

    public async Task ActualizarAsync(Usuario usuario, CancellationToken ct = default)
    {
        using var conexion = await _connectionFactory.AbrirAsync(ct);
        using var comando = new OleDbCommand(
            "UPDATE Usuarios SET Nombre = ?, Activo = ?, RowVersion = RowVersion + 1 WHERE Id = ? AND RowVersion = ?", conexion);
        comando.Parameters.AddWithValue("@Nombre", usuario.Nombre);
        comando.Parameters.AddWithValue("@Activo", usuario.Activo);
        comando.Parameters.AddWithValue("@Id", usuario.Id);
        comando.Parameters.AddWithValue("@RowVersion", usuario.RowVersion);

        var filas = await comando.ExecuteNonQueryAsync(ct);
        if (filas == 0)
        {
            throw new Application.Common.ConcurrenciaException(nameof(Usuario), usuario.Id);
        }
    }

    public async Task RegistrarLoginAsync(int usuarioId, DateTime fechaHora, CancellationToken ct = default)
    {
        using var conexion = await _connectionFactory.AbrirAsync(ct);
        using var comando = new OleDbCommand("UPDATE Usuarios SET UltimoLogin = ? WHERE Id = ?", conexion);
        comando.Parameters.AddWithValue("@UltimoLogin", fechaHora);
        comando.Parameters.AddWithValue("@Id", usuarioId);
        await comando.ExecuteNonQueryAsync(ct);
    }

    public async Task<IReadOnlyList<(int RolId, string NombreRol, int? EmpresaId)>> ObtenerRolesAsync(int usuarioId, CancellationToken ct = default)
    {
        using var conexion = await _connectionFactory.AbrirAsync(ct);
        using var comando = new OleDbCommand(
            @"SELECT ur.RolId, r.Nombre, ur.EmpresaId
              FROM UsuariosRoles ur INNER JOIN Roles r ON r.Id = ur.RolId
              WHERE ur.UsuarioId = ?", conexion);
        comando.Parameters.AddWithValue("@UsuarioId", usuarioId);

        using var lector = await comando.ExecuteReaderAsync(ct);
        var resultado = new List<(int, string, int?)>();
        while (await lector.ReadAsync(ct))
        {
            resultado.Add((lector.GetInt32(0), lector.GetString(1), lector.IsDBNull(2) ? null : lector.GetInt32(2)));
        }
        return resultado;
    }

    public async Task<IReadOnlyList<string>> ObtenerPermisosAsync(int usuarioId, CancellationToken ct = default)
    {
        using var conexion = await _connectionFactory.AbrirAsync(ct);
        using var comando = new OleDbCommand(
            @"SELECT DISTINCT p.Codigo
              FROM UsuariosRoles ur
              INNER JOIN RolesPermisos rp ON rp.RolId = ur.RolId
              INNER JOIN Permisos p ON p.Id = rp.PermisoId
              WHERE ur.UsuarioId = ?", conexion);
        comando.Parameters.AddWithValue("@UsuarioId", usuarioId);

        using var lector = await comando.ExecuteReaderAsync(ct);
        var resultado = new List<string>();
        while (await lector.ReadAsync(ct)) resultado.Add(lector.GetString(0));
        return resultado;
    }
}
