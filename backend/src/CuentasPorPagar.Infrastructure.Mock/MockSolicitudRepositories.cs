using CuentasPorPagar.Application.Abstractions.Repositories;
using CuentasPorPagar.Application.Common;
using CuentasPorPagar.Domain.Entities;

namespace CuentasPorPagar.Infrastructure.Mock;

public class MockSolicitudPagoRepository : ISolicitudPagoRepository
{
    private readonly InMemoryDataStore _store;
    public MockSolicitudPagoRepository(InMemoryDataStore store) => _store = store;

    public Task<SolicitudPago?> ObtenerPorIdAsync(int id, CancellationToken ct = default)
        => Task.FromResult(_store.Solicitudes.GetValueOrDefault(id));

    public Task<SolicitudPago?> ObtenerPorRadicadoAsync(string radicado, CancellationToken ct = default)
        => Task.FromResult(_store.Solicitudes.Values.FirstOrDefault(s => s.Radicado == radicado));

    public Task<ResultadoPaginado<SolicitudPago>> BuscarAsync(FiltroSolicitudes filtro, CancellationToken ct = default)
    {
        var query = _store.Solicitudes.Values.Where(s => !s.EliminadoLogico).AsEnumerable();

        if (filtro.EmpresaId is not null) query = query.Where(s => s.EmpresaId == filtro.EmpresaId);
        if (filtro.ProveedorId is not null) query = query.Where(s => s.ProveedorId == filtro.ProveedorId);
        if (filtro.SolicitanteId is not null) query = query.Where(s => s.SolicitanteId == filtro.SolicitanteId);
        if (filtro.ProyectoId is not null) query = query.Where(s => s.ProyectoId == filtro.ProyectoId);
        if (filtro.CentroCostoId is not null) query = query.Where(s => s.CentroCostoId == filtro.CentroCostoId);
        if (!string.IsNullOrWhiteSpace(filtro.Radicado)) query = query.Where(s => s.Radicado.Contains(filtro.Radicado, StringComparison.OrdinalIgnoreCase));
        if (!string.IsNullOrWhiteSpace(filtro.NumeroFactura)) query = query.Where(s => (s.NumeroFactura ?? "").Contains(filtro.NumeroFactura, StringComparison.OrdinalIgnoreCase));
        if (filtro.Estados is { Length: > 0 }) query = query.Where(s => filtro.Estados.Contains(s.Estado));
        if (filtro.FechaDesde is not null) query = query.Where(s => s.FechaCreacion >= filtro.FechaDesde);
        if (filtro.FechaHasta is not null) query = query.Where(s => s.FechaCreacion <= filtro.FechaHasta);

        var total = query.Count();
        var items = query
            .OrderByDescending(s => s.FechaCreacion)
            .Skip((filtro.Pagina - 1) * filtro.TamanoPagina)
            .Take(filtro.TamanoPagina)
            .ToList();

        return Task.FromResult(new ResultadoPaginado<SolicitudPago>
        {
            Items = items,
            Total = total,
            Pagina = filtro.Pagina,
            TamanoPagina = filtro.TamanoPagina
        });
    }

    public Task<IReadOnlyList<SolicitudPago>> BuscarPosiblesDuplicadosAsync(
        int empresaId, int proveedorId, string numeroFactura, DateTime fechaEmision, decimal valorBruto, CancellationToken ct = default)
    {
        var resultado = _store.Solicitudes.Values.Where(s =>
            !s.EliminadoLogico &&
            s.EmpresaId == empresaId &&
            s.ProveedorId == proveedorId &&
            s.NumeroFactura == numeroFactura &&
            s.FechaEmision.Date == fechaEmision.Date &&
            s.ValorBruto == valorBruto)
            .ToList();

        return Task.FromResult<IReadOnlyList<SolicitudPago>>(resultado);
    }

    public Task<SolicitudPago> CrearAsync(SolicitudPago solicitud, CancellationToken ct = default)
    {
        solicitud.Id = _store.SiguienteId();
        solicitud.RowVersion = 1;
        _store.Solicitudes[solicitud.Id] = solicitud;
        return Task.FromResult(solicitud);
    }

    public Task ActualizarAsync(SolicitudPago solicitud, CancellationToken ct = default)
    {
        if (!_store.Solicitudes.TryGetValue(solicitud.Id, out var existente) || existente.RowVersion != solicitud.RowVersion)
        {
            throw new ConcurrenciaException(nameof(SolicitudPago), solicitud.Id);
        }

        solicitud.RowVersion++;
        _store.Solicitudes[solicitud.Id] = solicitud;
        return Task.CompletedTask;
    }

    public Task CambiarEstadoAsync(int solicitudId, Domain.Enums.EstadoSolicitud nuevoEstado, long rowVersionEsperada, CancellationToken ct = default)
    {
        if (!_store.Solicitudes.TryGetValue(solicitudId, out var existente) || existente.RowVersion != rowVersionEsperada)
        {
            throw new ConcurrenciaException(nameof(SolicitudPago), solicitudId);
        }

        existente.Estado = nuevoEstado;
        existente.RowVersion++;
        if (nuevoEstado == Domain.Enums.EstadoSolicitud.Radicado && existente.FechaRadicacion is null)
        {
            existente.FechaRadicacion = DateTime.UtcNow;
        }
        return Task.CompletedTask;
    }
}

public class MockDocumentoSolicitudRepository : IDocumentoSolicitudRepository
{
    private readonly InMemoryDataStore _store;
    public MockDocumentoSolicitudRepository(InMemoryDataStore store) => _store = store;

    public Task<IReadOnlyList<DocumentoSolicitud>> ListarPorSolicitudAsync(int solicitudId, CancellationToken ct = default)
        => Task.FromResult<IReadOnlyList<DocumentoSolicitud>>(
            _store.DocumentosSolicitud.Values.Where(d => d.SolicitudId == solicitudId).ToList());

    public Task<DocumentoSolicitud?> ObtenerPorIdAsync(int id, CancellationToken ct = default)
        => Task.FromResult(_store.DocumentosSolicitud.GetValueOrDefault(id));

    public Task<DocumentoSolicitud> CrearAsync(DocumentoSolicitud documento, CancellationToken ct = default)
    {
        documento.Id = _store.SiguienteId();
        _store.DocumentosSolicitud[documento.Id] = documento;
        return Task.FromResult(documento);
    }

    public Task<IReadOnlyList<VersionDocumento>> ObtenerVersionesAsync(int documentoId, CancellationToken ct = default)
        => Task.FromResult<IReadOnlyList<VersionDocumento>>(
            _store.VersionesDocumento.Values.Where(v => v.DocumentoId == documentoId).OrderBy(v => v.NumeroVersion).ToList());

    public Task<VersionDocumento> AgregarVersionAsync(int documentoId, VersionDocumento nuevaVersion, CancellationToken ct = default)
    {
        foreach (var anterior in _store.VersionesDocumento.Values.Where(v => v.DocumentoId == documentoId))
        {
            anterior.EsVigente = false;
        }

        nuevaVersion.Id = _store.SiguienteId();
        nuevaVersion.DocumentoId = documentoId;
        nuevaVersion.EsVigente = true;
        _store.VersionesDocumento[nuevaVersion.Id] = nuevaVersion;

        if (_store.DocumentosSolicitud.TryGetValue(documentoId, out var documento))
        {
            documento.VersionVigenteId = nuevaVersion.Id;
        }

        return Task.FromResult(nuevaVersion);
    }
}
