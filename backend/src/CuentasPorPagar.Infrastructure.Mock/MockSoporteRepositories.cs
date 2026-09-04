using CuentasPorPagar.Application.Abstractions.Repositories;
using CuentasPorPagar.Domain.Entities;
using CuentasPorPagar.Domain.Enums;

namespace CuentasPorPagar.Infrastructure.Mock;

public class MockNotificacionRepository : INotificacionRepository
{
    private readonly InMemoryDataStore _store;
    public MockNotificacionRepository(InMemoryDataStore store) => _store = store;

    public Task<Notificacion> CrearAsync(Notificacion notificacion, CancellationToken ct = default)
    {
        notificacion.Id = _store.SiguienteId();
        _store.Notificaciones[notificacion.Id] = notificacion;
        return Task.FromResult(notificacion);
    }

    public Task<IReadOnlyList<Notificacion>> ListarPorUsuarioAsync(int usuarioId, bool soloNoLeidas, CancellationToken ct = default)
        => Task.FromResult<IReadOnlyList<Notificacion>>(_store.Notificaciones.Values
            .Where(n => n.UsuarioId == usuarioId && (!soloNoLeidas || !n.Leida))
            .OrderByDescending(n => n.FechaCreacion)
            .ToList());

    public Task MarcarLeidaAsync(int notificacionId, CancellationToken ct = default)
    {
        if (_store.Notificaciones.TryGetValue(notificacionId, out var n))
        {
            n.Leida = true;
            n.FechaLectura = DateTime.UtcNow;
        }
        return Task.CompletedTask;
    }

    public Task<IReadOnlyList<Notificacion>> ObtenerPendientesDeCorreoAsync(int maxIntentos, CancellationToken ct = default)
        => Task.FromResult<IReadOnlyList<Notificacion>>(_store.Notificaciones.Values
            .Where(n => n.EstadoEnvioCorreo != EstadoEnvio.Enviado)
            .ToList());

    public Task MarcarEnvioCorreoAsync(int notificacionId, EstadoEnvio estado, CancellationToken ct = default)
    {
        if (_store.Notificaciones.TryGetValue(notificacionId, out var n))
        {
            n.EstadoEnvioCorreo = estado;
        }
        return Task.CompletedTask;
    }
}

public class MockAuditoriaRepository : IAuditoriaRepository
{
    private readonly InMemoryDataStore _store;
    public MockAuditoriaRepository(InMemoryDataStore store) => _store = store;

    public Task RegistrarAsync(RegistroAuditoria registro, CancellationToken ct = default)
    {
        registro.Id = _store.SiguienteId();
        _store.Auditoria.Add(registro);
        return Task.CompletedTask;
    }

    public Task<ResultadoPaginado<RegistroAuditoria>> BuscarAsync(
        int? usuarioId, string? modulo, string? entidadTipo, int? entidadId,
        DateTime? desde, DateTime? hasta, int pagina, int tamanoPagina, CancellationToken ct = default)
    {
        var query = _store.Auditoria.AsEnumerable();
        if (usuarioId is not null) query = query.Where(a => a.UsuarioId == usuarioId);
        if (!string.IsNullOrWhiteSpace(modulo)) query = query.Where(a => a.Modulo == modulo);
        if (!string.IsNullOrWhiteSpace(entidadTipo)) query = query.Where(a => a.EntidadTipo == entidadTipo);
        if (entidadId is not null) query = query.Where(a => a.EntidadId == entidadId);
        if (desde is not null) query = query.Where(a => a.Fecha >= desde);
        if (hasta is not null) query = query.Where(a => a.Fecha <= hasta);

        var lista = query.OrderByDescending(a => a.Fecha).ToList();
        var items = lista.Skip((pagina - 1) * tamanoPagina).Take(tamanoPagina).ToList();

        return Task.FromResult(new ResultadoPaginado<RegistroAuditoria>
        {
            Items = items,
            Total = lista.Count,
            Pagina = pagina,
            TamanoPagina = tamanoPagina
        });
    }
}

/// <summary>
/// Implementación en memoria del consecutivo de radicado. Reproduce la semántica
/// de "incremento atómico" que en Access se logra con una transacción corta
/// (Interlocked.Increment es equivalente de un solo proceso); el servicio de
/// aplicación (SecuenciaRadicadoService) añade el semáforo por clave descrito
/// en la sección 20 encima de este repositorio.
/// </summary>
public class MockSecuenciaRadicadoRepository : ISecuenciaRadicadoRepository
{
    private readonly InMemoryDataStore _store;
    public MockSecuenciaRadicadoRepository(InMemoryDataStore store) => _store = store;

    public Task<long> ObtenerSiguienteValorAsync(string clave, CancellationToken ct = default)
    {
        var secuencia = _store.Secuencias.GetOrAdd(clave, _ => new SecuenciaRadicado { Clave = clave, UltimoValor = 0 });

        lock (secuencia)
        {
            secuencia.UltimoValor++;
            secuencia.RowVersion++;
            return Task.FromResult(secuencia.UltimoValor);
        }
    }
}

public class MockColaSincronizacionRepository : IColaSincronizacionRepository
{
    private readonly InMemoryDataStore _store;
    public MockColaSincronizacionRepository(InMemoryDataStore store) => _store = store;

    public Task<TrabajoSincronizacion> EncolarAsync(TrabajoSincronizacion trabajo, CancellationToken ct = default)
    {
        trabajo.Id = _store.SiguienteId();
        _store.ColaSincronizacion[trabajo.Id] = trabajo;
        return Task.FromResult(trabajo);
    }

    public Task<IReadOnlyList<TrabajoSincronizacion>> ObtenerPendientesAsync(int maxIntentos, CancellationToken ct = default)
        => Task.FromResult<IReadOnlyList<TrabajoSincronizacion>>(_store.ColaSincronizacion.Values
            .Where(t => t.Estado != EstadoTrabajoSincronizacion.Completado && t.Intentos < maxIntentos)
            .ToList());

    public Task MarcarResultadoAsync(int trabajoId, EstadoTrabajoSincronizacion estado, string? error, CancellationToken ct = default)
    {
        if (_store.ColaSincronizacion.TryGetValue(trabajoId, out var trabajo))
        {
            trabajo.Estado = estado;
            trabajo.UltimoError = error;
            trabajo.Intentos++;
            trabajo.FechaUltimoIntento = DateTime.UtcNow;
        }
        return Task.CompletedTask;
    }
}
