using System.Data.OleDb;
using Microsoft.Extensions.Options;

namespace CuentasPorPagar.Infrastructure.Access;

/// <summary>
/// Único punto de apertura de conexiones OLE DB hacia el archivo .accdb (sección 4/20).
/// Deliberadamente NO se registra como singleton de conexión abierta: cada operación
/// abre, ejecuta y cierra rápido (transacciones cortas) para minimizar el tiempo que
/// Access mantiene bloqueos de página (archivo .laccdb).
///
/// Solo funciona en Windows con el "Access Database Engine Redistributable" (ACE
/// OLEDB) instalado; en Linux/macOS System.Data.OleDb lanza PlatformNotSupportedException
/// en tiempo de ejecución (compila igual en cualquier SO, ver docs/database-access.md).
/// </summary>
public class AccessConnectionFactory
{
    private readonly AccessOptions _options;

    public AccessConnectionFactory(IOptions<AccessOptions> options)
    {
        _options = options.Value;
    }

    public OleDbConnection Crear()
    {
        if (string.IsNullOrWhiteSpace(_options.DatabasePath))
        {
            throw new InvalidOperationException(
                "ACCESS_DATABASE_PATH no está configurado. Defina la ruta local (Windows) al archivo .accdb.");
        }

        return new OleDbConnection(_options.ConnectionString);
    }

    public async Task<OleDbConnection> AbrirAsync(CancellationToken ct = default)
    {
        var conexion = Crear();
        await conexion.OpenAsync(ct);
        return conexion;
    }
}
