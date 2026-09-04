using CuentasPorPagar.Application.Abstractions.Repositories;
using CuentasPorPagar.Domain.Entities;

namespace CuentasPorPagar.Infrastructure.Mock;

public class MockCausacionRepository : ICausacionRepository
{
    private readonly InMemoryDataStore _store;
    public MockCausacionRepository(InMemoryDataStore store) => _store = store;

    public Task<Causacion?> ObtenerVigentePorSolicitudAsync(int solicitudId, CancellationToken ct = default)
        => Task.FromResult(_store.Causaciones.Values.FirstOrDefault(c => c.SolicitudId == solicitudId && c.Vigente));

    public Task<IReadOnlyList<Causacion>> ObtenerHistorialAsync(int solicitudId, CancellationToken ct = default)
        => Task.FromResult<IReadOnlyList<Causacion>>(
            _store.Causaciones.Values.Where(c => c.SolicitudId == solicitudId).OrderBy(c => c.FechaCausacion).ToList());

    public Task<IReadOnlyList<RetencionCausacion>> ObtenerRetencionesAsync(int causacionId, CancellationToken ct = default)
        => Task.FromResult<IReadOnlyList<RetencionCausacion>>(
            _store.RetencionesCausacion.Values.Where(r => r.CausacionId == causacionId).ToList());

    public Task<Causacion> RegistrarAsync(Causacion causacion, IReadOnlyList<RetencionCausacion> retenciones, CancellationToken ct = default)
    {
        // Si se re-causa tras una devolución de Tesorería, la causación anterior queda
        // en el historial (Vigente=false) en vez de sobrescribirse (sección 12/35/36).
        foreach (var anterior in _store.Causaciones.Values.Where(c => c.SolicitudId == causacion.SolicitudId && c.Vigente))
        {
            anterior.Vigente = false;
        }

        causacion.Id = _store.SiguienteId();
        causacion.Vigente = true;
        _store.Causaciones[causacion.Id] = causacion;

        foreach (var retencion in retenciones)
        {
            retencion.Id = _store.SiguienteId();
            retencion.CausacionId = causacion.Id;
            _store.RetencionesCausacion[retencion.Id] = retencion;
        }

        return Task.FromResult(causacion);
    }
}

public class MockPagoRepository : IPagoRepository
{
    private readonly InMemoryDataStore _store;
    private readonly ICausacionRepository _causaciones;

    public MockPagoRepository(InMemoryDataStore store, ICausacionRepository causaciones)
    {
        _store = store;
        _causaciones = causaciones;
    }

    public Task<IReadOnlyList<Pago>> ObtenerPorSolicitudAsync(int solicitudId, CancellationToken ct = default)
        => Task.FromResult<IReadOnlyList<Pago>>(
            _store.Pagos.Values.Where(p => p.SolicitudId == solicitudId).OrderBy(p => p.FechaPago).ToList());

    public async Task<decimal> ObtenerSaldoPendienteAsync(int solicitudId, CancellationToken ct = default)
    {
        var causacion = await _causaciones.ObtenerVigentePorSolicitudAsync(solicitudId, ct);
        if (causacion is null) return 0m;

        var pagado = _store.Pagos.Values.Where(p => p.SolicitudId == solicitudId).Sum(p => p.ValorPagado);
        return causacion.ValorNeto - pagado;
    }

    public Task<Pago> RegistrarAsync(Pago pago, CancellationToken ct = default)
    {
        pago.Id = _store.SiguienteId();
        _store.Pagos[pago.Id] = pago;
        return Task.FromResult(pago);
    }

    public Task<DocumentoPago> AgregarSoporteAsync(DocumentoPago documentoPago, CancellationToken ct = default)
    {
        documentoPago.Id = _store.SiguienteId();
        _store.DocumentosPago[documentoPago.Id] = documentoPago;
        return Task.FromResult(documentoPago);
    }
}
