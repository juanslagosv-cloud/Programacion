using CuentasPorPagar.Domain.Entities;

namespace CuentasPorPagar.Application.Abstractions.Repositories;

public interface IEmpresaRepository
{
    Task<IReadOnlyList<Empresa>> ListarAsync(bool soloActivas = true, CancellationToken ct = default);
    Task<Empresa?> ObtenerPorIdAsync(int id, CancellationToken ct = default);
    Task<Empresa?> ObtenerPorNitAsync(string nit, CancellationToken ct = default);
    Task<Empresa> CrearAsync(Empresa empresa, CancellationToken ct = default);
    Task ActualizarAsync(Empresa empresa, CancellationToken ct = default);
}

public interface IProveedorRepository
{
    Task<IReadOnlyList<Proveedor>> ListarAsync(int? empresaId = null, CancellationToken ct = default);
    Task<Proveedor?> ObtenerPorIdAsync(int id, CancellationToken ct = default);

    /// <summary>Evita duplicados por NIT dentro de la misma empresa (sección 55).</summary>
    Task<Proveedor?> ObtenerPorNitAsync(int empresaId, string nit, CancellationToken ct = default);
    Task<Proveedor> CrearAsync(Proveedor proveedor, CancellationToken ct = default);
    Task ActualizarAsync(Proveedor proveedor, CancellationToken ct = default);

    Task<IReadOnlyList<ProveedorCuentaBancaria>> ObtenerCuentasBancariasAsync(int proveedorId, CancellationToken ct = default);
    Task<ProveedorCuentaBancaria> AgregarCuentaBancariaAsync(ProveedorCuentaBancaria cuenta, CancellationToken ct = default);
}

public interface IProyectoRepository
{
    Task<IReadOnlyList<Proyecto>> ListarAsync(int? empresaId = null, CancellationToken ct = default);
    Task<Proyecto?> ObtenerPorIdAsync(int id, CancellationToken ct = default);
    Task<Proyecto> CrearAsync(Proyecto proyecto, CancellationToken ct = default);
    Task ActualizarAsync(Proyecto proyecto, CancellationToken ct = default);
}

public interface ICentroCostoRepository
{
    Task<IReadOnlyList<CentroCosto>> ListarAsync(int? empresaId = null, int? proyectoId = null, CancellationToken ct = default);
    Task<CentroCosto?> ObtenerPorIdAsync(int id, CancellationToken ct = default);
    Task<CentroCosto> CrearAsync(CentroCosto centroCosto, CancellationToken ct = default);
    Task ActualizarAsync(CentroCosto centroCosto, CancellationToken ct = default);
}

public interface IBancoRepository
{
    Task<IReadOnlyList<Banco>> ListarAsync(int? empresaId = null, CancellationToken ct = default);
    Task<Banco?> ObtenerPorIdAsync(int id, CancellationToken ct = default);
    Task<Banco> CrearAsync(Banco banco, CancellationToken ct = default);
    Task ActualizarAsync(Banco banco, CancellationToken ct = default);
}

public interface ITipoSolicitudRepository
{
    Task<IReadOnlyList<TipoSolicitud>> ListarAsync(bool soloActivos = true, CancellationToken ct = default);
    Task<TipoSolicitud> CrearAsync(TipoSolicitud tipo, CancellationToken ct = default);
}

public interface ITipoDocumentoRepository
{
    Task<IReadOnlyList<TipoDocumento>> ListarAsync(bool soloActivos = true, CancellationToken ct = default);
    Task<TipoDocumento> CrearAsync(TipoDocumento tipo, CancellationToken ct = default);
}

public interface IDocumentoObligatorioConfigRepository
{
    /// <summary>Resuelve qué tipos de documento son obligatorios para el contexto dado (sección 12).</summary>
    Task<IReadOnlyList<DocumentoObligatorioConfig>> ResolverAplicablesAsync(
        int tipoSolicitudId, int empresaId, string? tipoProveedor, decimal valorBruto, CancellationToken ct = default);
    Task<DocumentoObligatorioConfig> CrearAsync(DocumentoObligatorioConfig config, CancellationToken ct = default);
}

public interface IMotivoRepository
{
    Task<IReadOnlyList<MotivoDevolucion>> ListarMotivosDevolucionAsync(CancellationToken ct = default);
    Task<IReadOnlyList<MotivoRechazo>> ListarMotivosRechazoAsync(CancellationToken ct = default);
    Task<IReadOnlyList<MotivoDiferenciaPago>> ListarMotivosDiferenciaPagoAsync(CancellationToken ct = default);
}

public interface IPlantillaCorreoRepository
{
    Task<PlantillaCorreo?> ObtenerPorCodigoAsync(string codigo, CancellationToken ct = default);
    Task<IReadOnlyList<PlantillaCorreo>> ListarAsync(CancellationToken ct = default);
    Task ActualizarAsync(PlantillaCorreo plantilla, CancellationToken ct = default);
}

public interface IConfiguracionSistemaRepository
{
    Task<string?> ObtenerValorAsync(string clave, CancellationToken ct = default);
    Task EstablecerValorAsync(string clave, string valor, CancellationToken ct = default);
    Task<IReadOnlyList<ConfiguracionSistema>> ListarAsync(CancellationToken ct = default);
}
