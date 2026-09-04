using CuentasPorPagar.Application.Services;
using CuentasPorPagar.Infrastructure.Mock;
using Xunit;

namespace CuentasPorPagar.Tests;

/// <summary>
/// Cubre la sección 20 (concurrencia en Access) y el punto 86: la generación del
/// radicado debe ser segura ante radicaciones simultáneas. Lanza 50 generaciones
/// concurrentes y verifica que ninguna se repite.
/// </summary>
public class SecuenciaRadicadoConcurrenciaTests
{
    [Fact]
    public async Task GenerarRadicadoAsync_BajoConcurrencia_NuncaRepiteConsecutivo()
    {
        var repositorio = new MockSecuenciaRadicadoRepository(new InMemoryDataStore());
        var servicio = new SecuenciaRadicadoService(repositorio);

        var tareas = Enumerable.Range(0, 50).Select(_ => servicio.GenerarRadicadoAsync(2026));
        var radicados = await Task.WhenAll(tareas);

        Assert.Equal(50, radicados.Distinct().Count());
        Assert.Contains("RAD-2026-000001", radicados);
        Assert.Contains("RAD-2026-000050", radicados);
    }
}
