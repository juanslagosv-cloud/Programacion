using System.Data;
using System.Data.OleDb;
using CuentasPorPagar.Application.Abstractions.Repositories;

namespace CuentasPorPagar.Infrastructure.Access;

/// <summary>
/// Implementación de referencia del mecanismo de radicado seguro (sección 9/20).
///
/// La tabla SecuenciasRadicado tiene PK en Clave. Esta operación:
///  1. Abre una transacción OLE DB corta.
///  2. Lee UltimoValor con el registro efectivamente bloqueado por la transacción.
///  3. Si no existe la clave, la inserta en 0 dentro de la misma transacción.
///  4. Escribe UltimoValor + 1 y confirma.
///
/// Esto por sí solo NO basta bajo alta concurrencia con Access (el motor Jet/ACE
/// no ofrece un verdadero "SELECT ... FOR UPDATE"): por eso
/// Application.Services.SecuenciaRadicadoService añade un semáforo por clave a
/// nivel de proceso ANTES de llamar a este método, y SolicitudesPago.Radicado
/// tiene un índice único como última barrera (ver AccessSolicitudPagoRepository).
/// </summary>
public class AccessSecuenciaRadicadoRepository : ISecuenciaRadicadoRepository
{
    private readonly AccessConnectionFactory _connectionFactory;

    public AccessSecuenciaRadicadoRepository(AccessConnectionFactory connectionFactory)
    {
        _connectionFactory = connectionFactory;
    }

    public async Task<long> ObtenerSiguienteValorAsync(string clave, CancellationToken ct = default)
    {
        using var conexion = await _connectionFactory.AbrirAsync(ct);
        using var transaccion = conexion.BeginTransaction(IsolationLevel.Serializable);

        try
        {
            long ultimoValor;

            using (var lectura = new OleDbCommand("SELECT UltimoValor FROM SecuenciasRadicado WHERE Clave = ?", conexion, transaccion))
            {
                lectura.Parameters.AddWithValue("@Clave", clave);
                var resultado = await lectura.ExecuteScalarAsync(ct);

                if (resultado is null)
                {
                    using var insertar = new OleDbCommand(
                        "INSERT INTO SecuenciasRadicado (Clave, UltimoValor, RowVersion) VALUES (?, 0, 1)", conexion, transaccion);
                    insertar.Parameters.AddWithValue("@Clave", clave);
                    await insertar.ExecuteNonQueryAsync(ct);
                    ultimoValor = 0;
                }
                else
                {
                    ultimoValor = Convert.ToInt64(resultado);
                }
            }

            var nuevoValor = ultimoValor + 1;

            using (var actualizar = new OleDbCommand(
                "UPDATE SecuenciasRadicado SET UltimoValor = ?, RowVersion = RowVersion + 1 WHERE Clave = ?", conexion, transaccion))
            {
                actualizar.Parameters.AddWithValue("@UltimoValor", nuevoValor);
                actualizar.Parameters.AddWithValue("@Clave", clave);
                await actualizar.ExecuteNonQueryAsync(ct);
            }

            transaccion.Commit();
            return nuevoValor;
        }
        catch
        {
            transaccion.Rollback();
            throw;
        }
    }
}
