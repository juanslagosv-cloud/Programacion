using System.Data.OleDb;
using CuentasPorPagar.Application.Abstractions.Repositories;
using CuentasPorPagar.Domain.Entities;

namespace CuentasPorPagar.Infrastructure.Access;

/// <summary>
/// Auditoria es append-only (sección 18/53): esta clase intencionalmente no expone
/// ningún método de UPDATE/DELETE, ni siquiera privado. El único método de
/// escritura es RegistrarAsync (INSERT puro).
/// </summary>
public class AccessAuditoriaRepository : IAuditoriaRepository
{
    private readonly AccessConnectionFactory _connectionFactory;

    public AccessAuditoriaRepository(AccessConnectionFactory connectionFactory)
    {
        _connectionFactory = connectionFactory;
    }

    public async Task RegistrarAsync(RegistroAuditoria registro, CancellationToken ct = default)
    {
        using var conexion = await _connectionFactory.AbrirAsync(ct);
        using var comando = new OleDbCommand(
            @"INSERT INTO Auditoria
                (UsuarioId, Fecha, Accion, Modulo, EntidadTipo, EntidadId, ValorAnteriorJson, ValorNuevoJson, Comentario, Resultado, IpOrigen)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", conexion);

        comando.Parameters.AddWithValue("@UsuarioId", registro.UsuarioId);
        comando.Parameters.AddWithValue("@Fecha", registro.Fecha);
        comando.Parameters.AddWithValue("@Accion", registro.Accion);
        comando.Parameters.AddWithValue("@Modulo", registro.Modulo);
        comando.Parameters.AddWithValue("@EntidadTipo", registro.EntidadTipo);
        comando.Parameters.AddWithValue("@EntidadId", registro.EntidadId);
        comando.Parameters.AddWithValue("@ValorAnteriorJson", (object?)registro.ValorAnteriorJson ?? DBNull.Value);
        comando.Parameters.AddWithValue("@ValorNuevoJson", (object?)registro.ValorNuevoJson ?? DBNull.Value);
        comando.Parameters.AddWithValue("@Comentario", (object?)registro.Comentario ?? DBNull.Value);
        comando.Parameters.AddWithValue("@Resultado", registro.Resultado);
        comando.Parameters.AddWithValue("@IpOrigen", (object?)registro.IpOrigen ?? DBNull.Value);

        await comando.ExecuteNonQueryAsync(ct);
    }

    public async Task<ResultadoPaginado<RegistroAuditoria>> BuscarAsync(
        int? usuarioId, string? modulo, string? entidadTipo, int? entidadId,
        DateTime? desde, DateTime? hasta, int pagina, int tamanoPagina, CancellationToken ct = default)
    {
        var condiciones = new List<string>();
        var parametros = new List<OleDbParameter>();

        void Agregar(string sql, string nombre, object valor)
        {
            condiciones.Add(sql);
            parametros.Add(new OleDbParameter(nombre, valor));
        }

        if (usuarioId is not null) Agregar("UsuarioId = ?", "@UsuarioId", usuarioId.Value);
        if (!string.IsNullOrWhiteSpace(modulo)) Agregar("Modulo = ?", "@Modulo", modulo);
        if (!string.IsNullOrWhiteSpace(entidadTipo)) Agregar("EntidadTipo = ?", "@EntidadTipo", entidadTipo);
        if (entidadId is not null) Agregar("EntidadId = ?", "@EntidadId", entidadId.Value);
        if (desde is not null) Agregar("Fecha >= ?", "@Desde", desde.Value);
        if (hasta is not null) Agregar("Fecha <= ?", "@Hasta", hasta.Value);

        var whereSql = condiciones.Count > 0 ? "WHERE " + string.Join(" AND ", condiciones) : "";

        using var conexion = await _connectionFactory.AbrirAsync(ct);

        var total = 0;
        using (var conteo = new OleDbCommand($"SELECT COUNT(*) FROM Auditoria {whereSql}", conexion))
        {
            foreach (var p in parametros) conteo.Parameters.Add(((ICloneable)p).Clone());
            total = Convert.ToInt32(await conteo.ExecuteScalarAsync(ct));
        }

        var items = new List<RegistroAuditoria>();
        // Access/Jet no soporta OFFSET/FETCH: se pagina leyendo secuencialmente y descartando filas
        // previas a la página solicitada (aceptable para el volumen esperado en Access, sección 21).
        using (var seleccion = new OleDbCommand(
            $"SELECT Id, UsuarioId, Fecha, Accion, Modulo, EntidadTipo, EntidadId, ValorAnteriorJson, ValorNuevoJson, Comentario, Resultado, IpOrigen " +
            $"FROM Auditoria {whereSql} ORDER BY Fecha DESC", conexion))
        {
            foreach (var p in parametros) seleccion.Parameters.Add(((ICloneable)p).Clone());
            using var lector = await seleccion.ExecuteReaderAsync(ct);

            var indice = 0;
            var inicio = (pagina - 1) * tamanoPagina;
            while (await lector.ReadAsync(ct) && items.Count < tamanoPagina)
            {
                if (indice++ < inicio) continue;

                items.Add(new RegistroAuditoria
                {
                    Id = lector.GetInt32(0),
                    UsuarioId = lector.GetInt32(1),
                    Fecha = lector.GetDateTime(2),
                    Accion = lector.GetString(3),
                    Modulo = lector.GetString(4),
                    EntidadTipo = lector.GetString(5),
                    EntidadId = lector.GetInt32(6),
                    ValorAnteriorJson = lector.IsDBNull(7) ? null : lector.GetString(7),
                    ValorNuevoJson = lector.IsDBNull(8) ? null : lector.GetString(8),
                    Comentario = lector.IsDBNull(9) ? null : lector.GetString(9),
                    Resultado = lector.GetString(10),
                    IpOrigen = lector.IsDBNull(11) ? null : lector.GetString(11)
                });
            }
        }

        return new ResultadoPaginado<RegistroAuditoria> { Items = items, Total = total, Pagina = pagina, TamanoPagina = tamanoPagina };
    }
}
