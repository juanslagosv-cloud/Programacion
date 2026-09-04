using CuentasPorPagar.Application.Common;
using CuentasPorPagar.Application.Services;
using CuentasPorPagar.Domain.Entities;
using CuentasPorPagar.Domain.Enums;
using CuentasPorPagar.Infrastructure.Mock;
using Xunit;

namespace CuentasPorPagar.Tests;

public class NetoAPagarCalculatorTests
{
    [Fact]
    public void Calcular_RestaRetencionesYSumaOtrosConceptos()
    {
        var retenciones = new List<RetencionCausacion>
        {
            new() { Tipo = TipoRetencion.ReteFuente, Valor = 400_000m },
            new() { Tipo = TipoRetencion.ReteIca, Valor = 100_000m },
            new() { Tipo = TipoRetencion.Descuento, Valor = 50_000m },
            new() { Tipo = TipoRetencion.OtroConcepto, Valor = 20_000m },
        };

        // VALOR BRUTO - RETEFUENTE - RETEICA - DESCUENTOS + OTROS CONCEPTOS (sección 12/34)
        var neto = NetoAPagarCalculator.Calcular(valorBase: 10_000_000m, iva: 1_900_000m, retenciones);

        Assert.Equal(10_000_000m + 1_900_000m - 400_000m - 100_000m - 50_000m + 20_000m, neto);
    }
}

/// <summary>Cubre el punto 86: "un pago parcial no cierra una solicitud; un pago completo sí puede cerrarla".</summary>
public class PagosParcialesTests
{
    [Fact]
    public async Task SaldoPendiente_DisminuyeConCadaAbono_YLlegaACeroSoloConElPagoCompleto()
    {
        var store = new InMemoryDataStore();
        var causaciones = new MockCausacionRepository(store);
        var pagos = new MockPagoRepository(store, causaciones);

        var causacion = await causaciones.RegistrarAsync(
            new Causacion { SolicitudId = 1, ValorBase = 100_000_000m, ValorNeto = 100_000_000m },
            retenciones: Array.Empty<RetencionCausacion>());

        Assert.Equal(100_000_000m, await pagos.ObtenerSaldoPendienteAsync(1));

        await pagos.RegistrarAsync(new Pago { SolicitudId = 1, CausacionId = causacion.Id, ValorPagado = 40_000_000m, EstadoPago = EstadoPago.Parcial });
        Assert.Equal(60_000_000m, await pagos.ObtenerSaldoPendienteAsync(1));

        await pagos.RegistrarAsync(new Pago { SolicitudId = 1, CausacionId = causacion.Id, ValorPagado = 60_000_000m, EstadoPago = EstadoPago.Completo });
        Assert.Equal(0m, await pagos.ObtenerSaldoPendienteAsync(1));
    }
}

/// <summary>Cubre el punto 86: "un documento reemplazado conserva versión anterior".</summary>
public class VersionamientoDocumentalTests
{
    [Fact]
    public async Task AgregarVersion_MarcaLaAnteriorNoVigente_PeroNoLaElimina()
    {
        var store = new InMemoryDataStore();
        var repositorio = new MockDocumentoSolicitudRepository(store);

        var documento = await repositorio.CrearAsync(new DocumentoSolicitud { SolicitudId = 1, TipoDocumentoId = 1 });

        var v1 = await repositorio.AgregarVersionAsync(documento.Id, new VersionDocumento { DriveFileId = "file-v1", NumeroVersion = 1 });
        var v2 = await repositorio.AgregarVersionAsync(documento.Id, new VersionDocumento { DriveFileId = "file-v2", NumeroVersion = 2, MotivoReemplazo = "Factura corregida" });

        var versiones = await repositorio.ObtenerVersionesAsync(documento.Id);

        Assert.Equal(2, versiones.Count);
        Assert.False(versiones.Single(v => v.Id == v1.Id).EsVigente);
        Assert.True(versiones.Single(v => v.Id == v2.Id).EsVigente);
    }
}

/// <summary>Cubre el punto 86: "una factura duplicada genera alerta".</summary>
public class DeteccionDeDuplicadosTests
{
    [Fact]
    public async Task BuscarPosiblesDuplicados_EncuentraCoincidenciaExacta()
    {
        var store = new InMemoryDataStore();
        var repositorio = new MockSolicitudPagoRepository(store);

        var existente = await repositorio.CrearAsync(new SolicitudPago
        {
            Radicado = "RAD-2026-000120",
            EmpresaId = 1,
            ProveedorId = 5,
            NumeroFactura = "FE-4589",
            FechaEmision = new DateTime(2026, 8, 20),
            ValorBruto = 11_900_000m
        });

        var duplicados = await repositorio.BuscarPosiblesDuplicadosAsync(
            empresaId: 1, proveedorId: 5, numeroFactura: "FE-4589", fechaEmision: new DateTime(2026, 8, 20), valorBruto: 11_900_000m);

        Assert.Single(duplicados);
        Assert.Equal(existente.Radicado, duplicados[0].Radicado);
    }
}

/// <summary>Cubre la sección 20.2: la actualización optimista rechaza escrituras con RowVersion desactualizada.</summary>
public class ConcurrenciaOptimistaTests
{
    [Fact]
    public async Task ActualizarAsync_ConRowVersionDesactualizada_LanzaConcurrenciaException()
    {
        var store = new InMemoryDataStore();
        var repositorio = new MockSolicitudPagoRepository(store);

        var solicitud = await repositorio.CrearAsync(new SolicitudPago { Concepto = "Original" });
        var copiaObsoleta = new SolicitudPago { Id = solicitud.Id, RowVersion = solicitud.RowVersion, Concepto = "Cambio A" };

        await repositorio.ActualizarAsync(solicitud); // primer usuario actualiza y avanza el RowVersion

        await Assert.ThrowsAsync<ConcurrenciaException>(() => repositorio.ActualizarAsync(copiaObsoleta));
    }
}
