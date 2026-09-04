using System.Collections.Concurrent;
using CuentasPorPagar.Application.Abstractions.Repositories;

namespace CuentasPorPagar.Application.Services;

/// <summary>
/// Genera el radicado único (sección 9/20). Implementa el mecanismo descrito en la
/// propuesta técnica: un semáforo por clave a nivel de proceso (el backend es la
/// única instancia que habla con Access) serializa la lectura+incremento del
/// consecutivo, delegando la operación atómica de bajo nivel al repositorio
/// (que además se apoya en el índice único de SolicitudesPago.Radicado como
/// última barrera ante cualquier condición de carrera no prevista).
///
/// NUNCA usar "SELECT MAX(...) + 1" sin este mecanismo: dos radicaciones
/// simultáneas generarían el mismo consecutivo.
/// </summary>
public class SecuenciaRadicadoService
{
    private readonly ISecuenciaRadicadoRepository _repositorio;
    private static readonly ConcurrentDictionary<string, SemaphoreSlim> Semaforos = new();

    public SecuenciaRadicadoService(ISecuenciaRadicadoRepository repositorio)
    {
        _repositorio = repositorio;
    }

    /// <summary>Formato parametrizable: por defecto "RAD-{anio}-{consecutivo:D6}" (ej. RAD-2026-000001).</summary>
    public async Task<string> GenerarRadicadoAsync(int anio, string formato = "RAD-{0}-{1:D6}", CancellationToken ct = default)
    {
        var clave = $"RAD-{anio}";
        var semaforo = Semaforos.GetOrAdd(clave, _ => new SemaphoreSlim(1, 1));

        await semaforo.WaitAsync(ct);
        try
        {
            var siguiente = await _repositorio.ObtenerSiguienteValorAsync(clave, ct);
            return string.Format(formato, anio, siguiente);
        }
        finally
        {
            semaforo.Release();
        }
    }
}
