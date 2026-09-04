using CuentasPorPagar.Application.Abstractions.Repositories;
using CuentasPorPagar.Domain.Entities;
using CuentasPorPagar.Domain.Enums;

namespace CuentasPorPagar.Infrastructure.Mock;

public class MockFlujoAprobacionRepository : IFlujoAprobacionRepository
{
    private readonly InMemoryDataStore _store;
    public MockFlujoAprobacionRepository(InMemoryDataStore store) => _store = store;

    public Task<IReadOnlyList<FlujoAprobacion>> ListarActivosAsync(int? empresaId, CancellationToken ct = default)
        => Task.FromResult<IReadOnlyList<FlujoAprobacion>>(_store.FlujosAprobacion.Values
            .Where(f => f.Activo && (f.EmpresaId == null || f.EmpresaId == empresaId)).ToList());

    public Task<FlujoAprobacion?> ObtenerPorIdAsync(int id, CancellationToken ct = default)
        => Task.FromResult(_store.FlujosAprobacion.GetValueOrDefault(id));

    public Task<IReadOnlyList<PasoFlujo>> ObtenerPasosAsync(int flujoId, CancellationToken ct = default)
        => Task.FromResult<IReadOnlyList<PasoFlujo>>(
            _store.PasosFlujo.Values.Where(p => p.FlujoId == flujoId).OrderBy(p => p.Orden).ToList());

    public Task<FlujoAprobacion> CrearAsync(FlujoAprobacion flujo, CancellationToken ct = default)
    {
        flujo.Id = _store.SiguienteId();
        _store.FlujosAprobacion[flujo.Id] = flujo;
        return Task.FromResult(flujo);
    }

    public Task<PasoFlujo> AgregarPasoAsync(PasoFlujo paso, CancellationToken ct = default)
    {
        paso.Id = _store.SiguienteId();
        _store.PasosFlujo[paso.Id] = paso;
        return Task.FromResult(paso);
    }
}

public class MockAprobacionRepository : IAprobacionRepository
{
    private readonly InMemoryDataStore _store;
    public MockAprobacionRepository(InMemoryDataStore store) => _store = store;

    public Task<InstanciaAprobacion?> ObtenerInstanciaVigenteAsync(int solicitudId, CancellationToken ct = default)
        => Task.FromResult(_store.InstanciasAprobacion.Values
            .Where(i => i.SolicitudId == solicitudId)
            .OrderByDescending(i => i.FechaInicio)
            .FirstOrDefault(i => i.Estado == EstadoInstanciaAprobacion.EnCurso));

    public Task<InstanciaAprobacion> CrearInstanciaAsync(InstanciaAprobacion instancia, CancellationToken ct = default)
    {
        instancia.Id = _store.SiguienteId();
        instancia.RowVersion = 1;
        _store.InstanciasAprobacion[instancia.Id] = instancia;
        return Task.FromResult(instancia);
    }

    public Task ActualizarInstanciaAsync(InstanciaAprobacion instancia, CancellationToken ct = default)
    {
        instancia.RowVersion++;
        _store.InstanciasAprobacion[instancia.Id] = instancia;
        return Task.CompletedTask;
    }

    public Task<IReadOnlyList<Aprobacion>> ObtenerDecisionesAsync(int instanciaId, int? pasoId = null, CancellationToken ct = default)
        => Task.FromResult<IReadOnlyList<Aprobacion>>(_store.Aprobaciones.Values
            .Where(a => a.InstanciaId == instanciaId && (pasoId == null || a.PasoId == pasoId))
            .OrderBy(a => a.Fecha)
            .ToList());

    public Task<Aprobacion> RegistrarDecisionAsync(Aprobacion aprobacion, CancellationToken ct = default)
    {
        aprobacion.Id = _store.SiguienteId();
        _store.Aprobaciones[aprobacion.Id] = aprobacion;
        return Task.FromResult(aprobacion);
    }

    public Task<ResultadoPaginado<SolicitudPago>> ObtenerPendientesDeAprobadorAsync(int usuarioId, int pagina, int tamanoPagina, CancellationToken ct = default)
    {
        // Resuelve el paso actual de cada instancia en curso y filtra por rol/usuario requerido.
        var instanciasEnCurso = _store.InstanciasAprobacion.Values.Where(i => i.Estado == EstadoInstanciaAprobacion.EnCurso);

        var solicitudesPendientes = new List<SolicitudPago>();
        foreach (var instancia in instanciasEnCurso)
        {
            if (!_store.PasosFlujo.TryGetValue(instancia.PasoActualId, out var paso)) continue;

            var yaDecidio = _store.Aprobaciones.Values.Any(a => a.InstanciaId == instancia.Id && a.PasoId == paso.Id && a.AprobadorId == usuarioId);
            if (yaDecidio) continue;

            var esUsuarioAsignado = paso.UsuarioEspecificoId == usuarioId;
            var esRolAsignado = paso.RolRequeridoId is not null &&
                _store.UsuariosRoles.Any(ur => ur.UsuarioId == usuarioId && ur.RolId == paso.RolRequeridoId);

            if ((esUsuarioAsignado || esRolAsignado) && _store.Solicitudes.TryGetValue(instancia.SolicitudId, out var solicitud))
            {
                solicitudesPendientes.Add(solicitud);
            }
        }

        var total = solicitudesPendientes.Count;
        var items = solicitudesPendientes
            .OrderBy(s => s.FechaVencimiento)
            .Skip((pagina - 1) * tamanoPagina)
            .Take(tamanoPagina)
            .ToList();

        return Task.FromResult(new ResultadoPaginado<SolicitudPago> { Items = items, Total = total, Pagina = pagina, TamanoPagina = tamanoPagina });
    }
}
