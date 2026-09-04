using System.Data.Common;
using System.Data.OleDb;
using CuentasPorPagar.Application.Abstractions.Repositories;
using CuentasPorPagar.Application.Common;
using CuentasPorPagar.Domain.Entities;
using CuentasPorPagar.Domain.Enums;

namespace CuentasPorPagar.Infrastructure.Access;

/// <summary>
/// Implementación de referencia sobre Access para el agregado raíz del proceso.
/// Ilustra los dos mecanismos de concurrencia descritos en la sección 20:
///  - Concurrencia optimista (RowVersion) en <see cref="ActualizarAsync"/> y
///    <see cref="CambiarEstadoAsync"/>: el UPDATE incluye "WHERE Id=? AND RowVersion=?";
///    si no afecta filas, se lanza ConcurrenciaException en vez de sobrescribir.
///  - Índice único sobre Radicado (creado en el esquema de Access) como barrera
///    final ante una colisión de radicado no prevista por el semáforo de aplicación.
/// </summary>
public class AccessSolicitudPagoRepository : ISolicitudPagoRepository
{
    private readonly AccessConnectionFactory _connectionFactory;

    public AccessSolicitudPagoRepository(AccessConnectionFactory connectionFactory)
    {
        _connectionFactory = connectionFactory;
    }

    private const string ColumnasSelect =
        "Id, Radicado, EmpresaId, TipoSolicitudId, ProveedorId, TipoDocumento, NumeroFactura, NumeroCuentaCobro, " +
        "FechaEmision, FechaVencimiento, Moneda, ValorAntesImpuestos, Iva, ValorBruto, Concepto, ProyectoId, " +
        "CentroCostoId, OrdenCompra, Contrato, ResponsableId, Observaciones, Estado, SolicitanteId, DriveFolderId, " +
        "FechaCreacion, FechaRadicacion, RowVersion, EliminadoLogico";

    private static SolicitudPago Mapear(DbDataReader lector) => new()
    {
        Id = lector.GetInt32(0),
        Radicado = lector.GetString(1),
        EmpresaId = lector.GetInt32(2),
        TipoSolicitudId = lector.GetInt32(3),
        ProveedorId = lector.GetInt32(4),
        TipoDocumento = lector.GetString(5),
        NumeroFactura = lector.IsDBNull(6) ? null : lector.GetString(6),
        NumeroCuentaCobro = lector.IsDBNull(7) ? null : lector.GetString(7),
        FechaEmision = lector.GetDateTime(8),
        FechaVencimiento = lector.GetDateTime(9),
        Moneda = lector.GetString(10),
        ValorAntesImpuestos = lector.GetDecimal(11),
        Iva = lector.GetDecimal(12),
        ValorBruto = lector.GetDecimal(13),
        Concepto = lector.GetString(14),
        ProyectoId = lector.IsDBNull(15) ? null : lector.GetInt32(15),
        CentroCostoId = lector.IsDBNull(16) ? null : lector.GetInt32(16),
        OrdenCompra = lector.IsDBNull(17) ? null : lector.GetString(17),
        Contrato = lector.IsDBNull(18) ? null : lector.GetString(18),
        ResponsableId = lector.GetInt32(19),
        Observaciones = lector.IsDBNull(20) ? null : lector.GetString(20),
        Estado = (EstadoSolicitud)lector.GetInt32(21),
        SolicitanteId = lector.GetInt32(22),
        DriveFolderId = lector.IsDBNull(23) ? null : lector.GetString(23),
        FechaCreacion = lector.GetDateTime(24),
        FechaRadicacion = lector.IsDBNull(25) ? null : lector.GetDateTime(25),
        RowVersion = Convert.ToInt64(lector.GetValue(26)),
        EliminadoLogico = lector.GetBoolean(27)
    };

    public async Task<SolicitudPago?> ObtenerPorIdAsync(int id, CancellationToken ct = default)
    {
        using var conexion = await _connectionFactory.AbrirAsync(ct);
        using var comando = new OleDbCommand($"SELECT {ColumnasSelect} FROM SolicitudesPago WHERE Id = ?", conexion);
        comando.Parameters.AddWithValue("@Id", id);
        using var lector = await comando.ExecuteReaderAsync(ct);
        return await lector.ReadAsync(ct) ? Mapear(lector) : null;
    }

    public async Task<SolicitudPago?> ObtenerPorRadicadoAsync(string radicado, CancellationToken ct = default)
    {
        using var conexion = await _connectionFactory.AbrirAsync(ct);
        using var comando = new OleDbCommand($"SELECT {ColumnasSelect} FROM SolicitudesPago WHERE Radicado = ?", conexion);
        comando.Parameters.AddWithValue("@Radicado", radicado);
        using var lector = await comando.ExecuteReaderAsync(ct);
        return await lector.ReadAsync(ct) ? Mapear(lector) : null;
    }

    public async Task<IReadOnlyList<SolicitudPago>> BuscarPosiblesDuplicadosAsync(
        int empresaId, int proveedorId, string numeroFactura, DateTime fechaEmision, decimal valorBruto, CancellationToken ct = default)
    {
        using var conexion = await _connectionFactory.AbrirAsync(ct);
        using var comando = new OleDbCommand(
            $"SELECT {ColumnasSelect} FROM SolicitudesPago " +
            "WHERE EliminadoLogico = False AND EmpresaId = ? AND ProveedorId = ? AND NumeroFactura = ? " +
            "AND FechaEmision = ? AND ValorBruto = ?", conexion);
        comando.Parameters.AddWithValue("@EmpresaId", empresaId);
        comando.Parameters.AddWithValue("@ProveedorId", proveedorId);
        comando.Parameters.AddWithValue("@NumeroFactura", numeroFactura);
        comando.Parameters.AddWithValue("@FechaEmision", fechaEmision.Date);
        comando.Parameters.AddWithValue("@ValorBruto", valorBruto);

        using var lector = await comando.ExecuteReaderAsync(ct);
        var resultado = new List<SolicitudPago>();
        while (await lector.ReadAsync(ct)) resultado.Add(Mapear(lector));
        return resultado;
    }

    public async Task<ResultadoPaginado<SolicitudPago>> BuscarAsync(FiltroSolicitudes filtro, CancellationToken ct = default)
    {
        var condiciones = new List<string> { "EliminadoLogico = False" };
        var parametros = new List<OleDbParameter>();

        void Agregar(string sql, string nombre, object valor)
        {
            condiciones.Add(sql);
            parametros.Add(new OleDbParameter(nombre, valor));
        }

        if (filtro.EmpresaId is not null) Agregar("EmpresaId = ?", "@EmpresaId", filtro.EmpresaId.Value);
        if (filtro.ProveedorId is not null) Agregar("ProveedorId = ?", "@ProveedorId", filtro.ProveedorId.Value);
        if (filtro.SolicitanteId is not null) Agregar("SolicitanteId = ?", "@SolicitanteId", filtro.SolicitanteId.Value);
        if (filtro.ProyectoId is not null) Agregar("ProyectoId = ?", "@ProyectoId", filtro.ProyectoId.Value);
        if (filtro.CentroCostoId is not null) Agregar("CentroCostoId = ?", "@CentroCostoId", filtro.CentroCostoId.Value);
        if (!string.IsNullOrWhiteSpace(filtro.Radicado)) Agregar("Radicado LIKE ?", "@Radicado", $"%{filtro.Radicado}%");
        if (!string.IsNullOrWhiteSpace(filtro.NumeroFactura)) Agregar("NumeroFactura LIKE ?", "@NumeroFactura", $"%{filtro.NumeroFactura}%");
        if (filtro.FechaDesde is not null) Agregar("FechaCreacion >= ?", "@FechaDesde", filtro.FechaDesde.Value);
        if (filtro.FechaHasta is not null) Agregar("FechaCreacion <= ?", "@FechaHasta", filtro.FechaHasta.Value);

        if (filtro.Estados is { Length: > 0 })
        {
            var enteros = filtro.Estados.Select(e => (int)e).ToArray();
            condiciones.Add($"Estado IN ({string.Join(",", enteros)})"); // valores enteros propios, no entrada de usuario: seguro sin parametrizar
        }

        var whereSql = "WHERE " + string.Join(" AND ", condiciones);

        using var conexion = await _connectionFactory.AbrirAsync(ct);

        int total;
        using (var conteo = new OleDbCommand($"SELECT COUNT(*) FROM SolicitudesPago {whereSql}", conexion))
        {
            foreach (var p in parametros) conteo.Parameters.Add(((ICloneable)p).Clone());
            total = Convert.ToInt32(await conteo.ExecuteScalarAsync(ct));
        }

        var items = new List<SolicitudPago>();
        using (var seleccion = new OleDbCommand(
            $"SELECT {ColumnasSelect} FROM SolicitudesPago {whereSql} ORDER BY FechaCreacion DESC", conexion))
        {
            foreach (var p in parametros) seleccion.Parameters.Add(((ICloneable)p).Clone());
            using var lector = await seleccion.ExecuteReaderAsync(ct);

            var indice = 0;
            var inicio = (filtro.Pagina - 1) * filtro.TamanoPagina;
            while (await lector.ReadAsync(ct) && items.Count < filtro.TamanoPagina)
            {
                if (indice++ < inicio) continue;
                items.Add(Mapear(lector));
            }
        }

        return new ResultadoPaginado<SolicitudPago> { Items = items, Total = total, Pagina = filtro.Pagina, TamanoPagina = filtro.TamanoPagina };
    }

    public async Task<SolicitudPago> CrearAsync(SolicitudPago solicitud, CancellationToken ct = default)
    {
        using var conexion = await _connectionFactory.AbrirAsync(ct);
        using var comando = new OleDbCommand(
            @"INSERT INTO SolicitudesPago
                (Radicado, EmpresaId, TipoSolicitudId, ProveedorId, TipoDocumento, NumeroFactura, NumeroCuentaCobro,
                 FechaEmision, FechaVencimiento, Moneda, ValorAntesImpuestos, Iva, ValorBruto, Concepto, ProyectoId,
                 CentroCostoId, OrdenCompra, Contrato, ResponsableId, Observaciones, Estado, SolicitanteId,
                 FechaCreacion, RowVersion, EliminadoLogico)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, False)", conexion);

        // El índice único de Access sobre Radicado es la barrera final: si dos
        // radicaciones colisionan pese al semáforo de aplicación, este INSERT
        // fallará con una excepción de violación de índice y el llamador
        // (SecuenciaRadicadoService) debe reintentar con un nuevo consecutivo.
        comando.Parameters.AddWithValue("@Radicado", solicitud.Radicado);
        comando.Parameters.AddWithValue("@EmpresaId", solicitud.EmpresaId);
        comando.Parameters.AddWithValue("@TipoSolicitudId", solicitud.TipoSolicitudId);
        comando.Parameters.AddWithValue("@ProveedorId", solicitud.ProveedorId);
        comando.Parameters.AddWithValue("@TipoDocumento", solicitud.TipoDocumento);
        comando.Parameters.AddWithValue("@NumeroFactura", (object?)solicitud.NumeroFactura ?? DBNull.Value);
        comando.Parameters.AddWithValue("@NumeroCuentaCobro", (object?)solicitud.NumeroCuentaCobro ?? DBNull.Value);
        comando.Parameters.AddWithValue("@FechaEmision", solicitud.FechaEmision);
        comando.Parameters.AddWithValue("@FechaVencimiento", solicitud.FechaVencimiento);
        comando.Parameters.AddWithValue("@Moneda", solicitud.Moneda);
        comando.Parameters.AddWithValue("@ValorAntesImpuestos", solicitud.ValorAntesImpuestos);
        comando.Parameters.AddWithValue("@Iva", solicitud.Iva);
        comando.Parameters.AddWithValue("@ValorBruto", solicitud.ValorBruto);
        comando.Parameters.AddWithValue("@Concepto", solicitud.Concepto);
        comando.Parameters.AddWithValue("@ProyectoId", (object?)solicitud.ProyectoId ?? DBNull.Value);
        comando.Parameters.AddWithValue("@CentroCostoId", (object?)solicitud.CentroCostoId ?? DBNull.Value);
        comando.Parameters.AddWithValue("@OrdenCompra", (object?)solicitud.OrdenCompra ?? DBNull.Value);
        comando.Parameters.AddWithValue("@Contrato", (object?)solicitud.Contrato ?? DBNull.Value);
        comando.Parameters.AddWithValue("@ResponsableId", solicitud.ResponsableId);
        comando.Parameters.AddWithValue("@Observaciones", (object?)solicitud.Observaciones ?? DBNull.Value);
        comando.Parameters.AddWithValue("@Estado", (int)solicitud.Estado);
        comando.Parameters.AddWithValue("@SolicitanteId", solicitud.SolicitanteId);
        comando.Parameters.AddWithValue("@FechaCreacion", solicitud.FechaCreacion);

        await comando.ExecuteNonQueryAsync(ct);

        using var idComando = new OleDbCommand("SELECT @@IDENTITY", conexion);
        solicitud.Id = Convert.ToInt32(await idComando.ExecuteScalarAsync(ct));
        solicitud.RowVersion = 1;
        return solicitud;
    }

    public async Task ActualizarAsync(SolicitudPago solicitud, CancellationToken ct = default)
    {
        using var conexion = await _connectionFactory.AbrirAsync(ct);
        using var comando = new OleDbCommand(
            @"UPDATE SolicitudesPago SET
                NumeroFactura = ?, NumeroCuentaCobro = ?, FechaEmision = ?, FechaVencimiento = ?,
                ValorAntesImpuestos = ?, Iva = ?, ValorBruto = ?, Concepto = ?, ProyectoId = ?,
                CentroCostoId = ?, OrdenCompra = ?, Contrato = ?, Observaciones = ?, RowVersion = RowVersion + 1
              WHERE Id = ? AND RowVersion = ?", conexion);

        comando.Parameters.AddWithValue("@NumeroFactura", (object?)solicitud.NumeroFactura ?? DBNull.Value);
        comando.Parameters.AddWithValue("@NumeroCuentaCobro", (object?)solicitud.NumeroCuentaCobro ?? DBNull.Value);
        comando.Parameters.AddWithValue("@FechaEmision", solicitud.FechaEmision);
        comando.Parameters.AddWithValue("@FechaVencimiento", solicitud.FechaVencimiento);
        comando.Parameters.AddWithValue("@ValorAntesImpuestos", solicitud.ValorAntesImpuestos);
        comando.Parameters.AddWithValue("@Iva", solicitud.Iva);
        comando.Parameters.AddWithValue("@ValorBruto", solicitud.ValorBruto);
        comando.Parameters.AddWithValue("@Concepto", solicitud.Concepto);
        comando.Parameters.AddWithValue("@ProyectoId", (object?)solicitud.ProyectoId ?? DBNull.Value);
        comando.Parameters.AddWithValue("@CentroCostoId", (object?)solicitud.CentroCostoId ?? DBNull.Value);
        comando.Parameters.AddWithValue("@OrdenCompra", (object?)solicitud.OrdenCompra ?? DBNull.Value);
        comando.Parameters.AddWithValue("@Contrato", (object?)solicitud.Contrato ?? DBNull.Value);
        comando.Parameters.AddWithValue("@Observaciones", (object?)solicitud.Observaciones ?? DBNull.Value);
        comando.Parameters.AddWithValue("@Id", solicitud.Id);
        comando.Parameters.AddWithValue("@RowVersion", solicitud.RowVersion);

        var filasAfectadas = await comando.ExecuteNonQueryAsync(ct);
        if (filasAfectadas == 0)
        {
            throw new ConcurrenciaException(nameof(SolicitudPago), solicitud.Id);
        }
    }

    public async Task CambiarEstadoAsync(int solicitudId, EstadoSolicitud nuevoEstado, long rowVersionEsperada, CancellationToken ct = default)
    {
        using var conexion = await _connectionFactory.AbrirAsync(ct);
        using var comando = new OleDbCommand(
            @"UPDATE SolicitudesPago SET
                Estado = ?,
                FechaRadicacion = IIF(? = ? AND FechaRadicacion IS NULL, ?, FechaRadicacion),
                RowVersion = RowVersion + 1
              WHERE Id = ? AND RowVersion = ?", conexion);

        comando.Parameters.AddWithValue("@Estado", (int)nuevoEstado);
        comando.Parameters.AddWithValue("@EstadoComparacion1", (int)nuevoEstado);
        comando.Parameters.AddWithValue("@EstadoComparacion2", (int)EstadoSolicitud.Radicado);
        comando.Parameters.AddWithValue("@FechaRadicacion", DateTime.UtcNow);
        comando.Parameters.AddWithValue("@Id", solicitudId);
        comando.Parameters.AddWithValue("@RowVersion", rowVersionEsperada);

        var filasAfectadas = await comando.ExecuteNonQueryAsync(ct);
        if (filasAfectadas == 0)
        {
            throw new ConcurrenciaException(nameof(SolicitudPago), solicitudId);
        }
    }
}
