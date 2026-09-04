using CuentasPorPagar.Application.Abstractions.Repositories;
using CuentasPorPagar.Domain.Entities;

namespace CuentasPorPagar.Infrastructure.Mock;

public class MockEmpresaRepository : IEmpresaRepository
{
    private readonly InMemoryDataStore _store;
    public MockEmpresaRepository(InMemoryDataStore store) => _store = store;

    public Task<IReadOnlyList<Empresa>> ListarAsync(bool soloActivas = true, CancellationToken ct = default)
        => Task.FromResult<IReadOnlyList<Empresa>>(_store.Empresas.Values.Where(e => !soloActivas || e.Activa).ToList());

    public Task<Empresa?> ObtenerPorIdAsync(int id, CancellationToken ct = default)
        => Task.FromResult(_store.Empresas.GetValueOrDefault(id));

    public Task<Empresa?> ObtenerPorNitAsync(string nit, CancellationToken ct = default)
        => Task.FromResult(_store.Empresas.Values.FirstOrDefault(e => e.Nit == nit));

    public Task<Empresa> CrearAsync(Empresa empresa, CancellationToken ct = default)
    {
        empresa.Id = _store.SiguienteId();
        empresa.RowVersion = 1;
        _store.Empresas[empresa.Id] = empresa;
        return Task.FromResult(empresa);
    }

    public Task ActualizarAsync(Empresa empresa, CancellationToken ct = default)
    {
        empresa.RowVersion++;
        _store.Empresas[empresa.Id] = empresa;
        return Task.CompletedTask;
    }
}

public class MockProveedorRepository : IProveedorRepository
{
    private readonly InMemoryDataStore _store;
    public MockProveedorRepository(InMemoryDataStore store) => _store = store;

    public Task<IReadOnlyList<Proveedor>> ListarAsync(int? empresaId = null, CancellationToken ct = default)
        => Task.FromResult<IReadOnlyList<Proveedor>>(_store.Proveedores.Values
            .Where(p => !p.EliminadoLogico && (empresaId == null || p.EmpresaId == empresaId)).ToList());

    public Task<Proveedor?> ObtenerPorIdAsync(int id, CancellationToken ct = default)
        => Task.FromResult(_store.Proveedores.GetValueOrDefault(id));

    public Task<Proveedor?> ObtenerPorNitAsync(int empresaId, string nit, CancellationToken ct = default)
        => Task.FromResult(_store.Proveedores.Values.FirstOrDefault(p => p.EmpresaId == empresaId && p.Nit == nit));

    public Task<Proveedor> CrearAsync(Proveedor proveedor, CancellationToken ct = default)
    {
        proveedor.Id = _store.SiguienteId();
        proveedor.RowVersion = 1;
        _store.Proveedores[proveedor.Id] = proveedor;
        return Task.FromResult(proveedor);
    }

    public Task ActualizarAsync(Proveedor proveedor, CancellationToken ct = default)
    {
        proveedor.RowVersion++;
        _store.Proveedores[proveedor.Id] = proveedor;
        return Task.CompletedTask;
    }

    public Task<IReadOnlyList<ProveedorCuentaBancaria>> ObtenerCuentasBancariasAsync(int proveedorId, CancellationToken ct = default)
        => Task.FromResult<IReadOnlyList<ProveedorCuentaBancaria>>(
            _store.CuentasBancariasProveedor.Values.Where(c => c.ProveedorId == proveedorId && c.Vigente).ToList());

    public Task<ProveedorCuentaBancaria> AgregarCuentaBancariaAsync(ProveedorCuentaBancaria cuenta, CancellationToken ct = default)
    {
        cuenta.Id = _store.SiguienteId();
        _store.CuentasBancariasProveedor[cuenta.Id] = cuenta;
        return Task.FromResult(cuenta);
    }
}

public class MockProyectoRepository : IProyectoRepository
{
    private readonly InMemoryDataStore _store;
    public MockProyectoRepository(InMemoryDataStore store) => _store = store;

    public Task<IReadOnlyList<Proyecto>> ListarAsync(int? empresaId = null, CancellationToken ct = default)
        => Task.FromResult<IReadOnlyList<Proyecto>>(_store.Proyectos.Values
            .Where(p => empresaId == null || p.EmpresaId == empresaId).ToList());

    public Task<Proyecto?> ObtenerPorIdAsync(int id, CancellationToken ct = default)
        => Task.FromResult(_store.Proyectos.GetValueOrDefault(id));

    public Task<Proyecto> CrearAsync(Proyecto proyecto, CancellationToken ct = default)
    {
        proyecto.Id = _store.SiguienteId();
        _store.Proyectos[proyecto.Id] = proyecto;
        return Task.FromResult(proyecto);
    }

    public Task ActualizarAsync(Proyecto proyecto, CancellationToken ct = default)
    {
        _store.Proyectos[proyecto.Id] = proyecto;
        return Task.CompletedTask;
    }
}

public class MockCentroCostoRepository : ICentroCostoRepository
{
    private readonly InMemoryDataStore _store;
    public MockCentroCostoRepository(InMemoryDataStore store) => _store = store;

    public Task<IReadOnlyList<CentroCosto>> ListarAsync(int? empresaId = null, int? proyectoId = null, CancellationToken ct = default)
        => Task.FromResult<IReadOnlyList<CentroCosto>>(_store.CentrosCosto.Values
            .Where(c => (empresaId == null || c.EmpresaId == empresaId) && (proyectoId == null || c.ProyectoId == proyectoId))
            .ToList());

    public Task<CentroCosto?> ObtenerPorIdAsync(int id, CancellationToken ct = default)
        => Task.FromResult(_store.CentrosCosto.GetValueOrDefault(id));

    public Task<CentroCosto> CrearAsync(CentroCosto centroCosto, CancellationToken ct = default)
    {
        centroCosto.Id = _store.SiguienteId();
        _store.CentrosCosto[centroCosto.Id] = centroCosto;
        return Task.FromResult(centroCosto);
    }

    public Task ActualizarAsync(CentroCosto centroCosto, CancellationToken ct = default)
    {
        _store.CentrosCosto[centroCosto.Id] = centroCosto;
        return Task.CompletedTask;
    }
}

public class MockBancoRepository : IBancoRepository
{
    private readonly InMemoryDataStore _store;
    public MockBancoRepository(InMemoryDataStore store) => _store = store;

    public Task<IReadOnlyList<Banco>> ListarAsync(int? empresaId = null, CancellationToken ct = default)
        => Task.FromResult<IReadOnlyList<Banco>>(_store.Bancos.Values
            .Where(b => empresaId == null || b.EmpresaId == empresaId).ToList());

    public Task<Banco?> ObtenerPorIdAsync(int id, CancellationToken ct = default)
        => Task.FromResult(_store.Bancos.GetValueOrDefault(id));

    public Task<Banco> CrearAsync(Banco banco, CancellationToken ct = default)
    {
        banco.Id = _store.SiguienteId();
        _store.Bancos[banco.Id] = banco;
        return Task.FromResult(banco);
    }

    public Task ActualizarAsync(Banco banco, CancellationToken ct = default)
    {
        _store.Bancos[banco.Id] = banco;
        return Task.CompletedTask;
    }
}

public class MockTipoSolicitudRepository : ITipoSolicitudRepository
{
    private readonly InMemoryDataStore _store;
    public MockTipoSolicitudRepository(InMemoryDataStore store) => _store = store;

    public Task<IReadOnlyList<TipoSolicitud>> ListarAsync(bool soloActivos = true, CancellationToken ct = default)
        => Task.FromResult<IReadOnlyList<TipoSolicitud>>(_store.TiposSolicitud.Values.Where(t => !soloActivos || t.Activo).ToList());

    public Task<TipoSolicitud> CrearAsync(TipoSolicitud tipo, CancellationToken ct = default)
    {
        tipo.Id = _store.SiguienteId();
        _store.TiposSolicitud[tipo.Id] = tipo;
        return Task.FromResult(tipo);
    }
}

public class MockTipoDocumentoRepository : ITipoDocumentoRepository
{
    private readonly InMemoryDataStore _store;
    public MockTipoDocumentoRepository(InMemoryDataStore store) => _store = store;

    public Task<IReadOnlyList<TipoDocumento>> ListarAsync(bool soloActivos = true, CancellationToken ct = default)
        => Task.FromResult<IReadOnlyList<TipoDocumento>>(_store.TiposDocumento.Values.Where(t => !soloActivos || t.Activo).ToList());

    public Task<TipoDocumento> CrearAsync(TipoDocumento tipo, CancellationToken ct = default)
    {
        tipo.Id = _store.SiguienteId();
        _store.TiposDocumento[tipo.Id] = tipo;
        return Task.FromResult(tipo);
    }
}

public class MockDocumentoObligatorioConfigRepository : IDocumentoObligatorioConfigRepository
{
    private readonly InMemoryDataStore _store;
    public MockDocumentoObligatorioConfigRepository(InMemoryDataStore store) => _store = store;

    public Task<IReadOnlyList<DocumentoObligatorioConfig>> ResolverAplicablesAsync(
        int tipoSolicitudId, int empresaId, string? tipoProveedor, decimal valorBruto, CancellationToken ct = default)
    {
        var resultado = _store.DocumentosObligatorios.Values.Where(c =>
            c.TipoSolicitudId == tipoSolicitudId &&
            (c.EmpresaId == null || c.EmpresaId == empresaId) &&
            (c.TipoProveedor == null || c.TipoProveedor == tipoProveedor) &&
            (c.MontoDesde == null || valorBruto >= c.MontoDesde) &&
            (c.MontoHasta == null || valorBruto <= c.MontoHasta))
            .ToList();

        return Task.FromResult<IReadOnlyList<DocumentoObligatorioConfig>>(resultado);
    }

    public Task<DocumentoObligatorioConfig> CrearAsync(DocumentoObligatorioConfig config, CancellationToken ct = default)
    {
        config.Id = _store.SiguienteId();
        _store.DocumentosObligatorios[config.Id] = config;
        return Task.FromResult(config);
    }
}

public class MockMotivoRepository : IMotivoRepository
{
    private readonly InMemoryDataStore _store;
    public MockMotivoRepository(InMemoryDataStore store) => _store = store;

    public Task<IReadOnlyList<MotivoDevolucion>> ListarMotivosDevolucionAsync(CancellationToken ct = default)
        => Task.FromResult<IReadOnlyList<MotivoDevolucion>>(_store.MotivosDevolucion.Values.Where(m => m.Activo).ToList());

    public Task<IReadOnlyList<MotivoRechazo>> ListarMotivosRechazoAsync(CancellationToken ct = default)
        => Task.FromResult<IReadOnlyList<MotivoRechazo>>(_store.MotivosRechazo.Values.Where(m => m.Activo).ToList());

    public Task<IReadOnlyList<MotivoDiferenciaPago>> ListarMotivosDiferenciaPagoAsync(CancellationToken ct = default)
        => Task.FromResult<IReadOnlyList<MotivoDiferenciaPago>>(_store.MotivosDiferenciaPago.Values.Where(m => m.Activo).ToList());
}

public class MockPlantillaCorreoRepository : IPlantillaCorreoRepository
{
    private readonly InMemoryDataStore _store;
    public MockPlantillaCorreoRepository(InMemoryDataStore store) => _store = store;

    public Task<PlantillaCorreo?> ObtenerPorCodigoAsync(string codigo, CancellationToken ct = default)
        => Task.FromResult(_store.PlantillasCorreo.Values.FirstOrDefault(p => p.Codigo == codigo));

    public Task<IReadOnlyList<PlantillaCorreo>> ListarAsync(CancellationToken ct = default)
        => Task.FromResult<IReadOnlyList<PlantillaCorreo>>(_store.PlantillasCorreo.Values.ToList());

    public Task ActualizarAsync(PlantillaCorreo plantilla, CancellationToken ct = default)
    {
        _store.PlantillasCorreo[plantilla.Id] = plantilla;
        return Task.CompletedTask;
    }
}

public class MockConfiguracionSistemaRepository : IConfiguracionSistemaRepository
{
    private readonly InMemoryDataStore _store;
    public MockConfiguracionSistemaRepository(InMemoryDataStore store) => _store = store;

    public Task<string?> ObtenerValorAsync(string clave, CancellationToken ct = default)
        => Task.FromResult(_store.ConfiguracionSistema.GetValueOrDefault(clave)?.Valor);

    public Task EstablecerValorAsync(string clave, string valor, CancellationToken ct = default)
    {
        _store.ConfiguracionSistema[clave] = new ConfiguracionSistema { Clave = clave, Valor = valor };
        return Task.CompletedTask;
    }

    public Task<IReadOnlyList<ConfiguracionSistema>> ListarAsync(CancellationToken ct = default)
        => Task.FromResult<IReadOnlyList<ConfiguracionSistema>>(_store.ConfiguracionSistema.Values.ToList());
}
