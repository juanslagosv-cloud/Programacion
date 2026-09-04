using CuentasPorPagar.Application.Common;
using CuentasPorPagar.Application.Services;
using CuentasPorPagar.Domain.Entities;
using CuentasPorPagar.Domain.Enums;
using CuentasPorPagar.Domain.Workflow;
using CuentasPorPagar.Infrastructure.Mock;
using Xunit;

namespace CuentasPorPagar.Tests;

/// <summary>
/// Cubre la regla del punto 99 ("nadie debe poder saltarse etapas manualmente")
/// y varios de los casos de prueba mínimos pedidos en la sección 86.
/// </summary>
public class WorkflowTests
{
    [Theory]
    [InlineData(EstadoSolicitud.Borrador, EstadoSolicitud.Radicado, true)]
    [InlineData(EstadoSolicitud.Radicado, EstadoSolicitud.PendienteDeAprobacion, true)]
    // "No permitir: SOLICITUD -> TESORERÍA sin aprobaciones" (punto 99)
    [InlineData(EstadoSolicitud.Radicado, EstadoSolicitud.PagoProgramado, false)]
    // "No permitir: APROBACIÓN -> TESORERÍA sin Contabilidad" (punto 99)
    [InlineData(EstadoSolicitud.Aprobado, EstadoSolicitud.PagoProgramado, false)]
    // "No permitir: CAUSACIÓN -> CERRADO sin pago" (punto 99)
    [InlineData(EstadoSolicitud.Causado, EstadoSolicitud.Cerrado, false)]
    // Una solicitud sin causación no llega a Tesorería: Aprobado solo puede ir a PendienteDeCausacion.
    [InlineData(EstadoSolicitud.Aprobado, EstadoSolicitud.PendienteDeCausacion, true)]
    [InlineData(EstadoSolicitud.PagoParcial, EstadoSolicitud.Pagado, true)]
    [InlineData(EstadoSolicitud.Pagado, EstadoSolicitud.Cerrado, true)]
    [InlineData(EstadoSolicitud.Cerrado, EstadoSolicitud.Radicado, false)]
    public void ValidaTransicionesSegunLaTablaDeLaSeccion9(EstadoSolicitud origen, EstadoSolicitud destino, bool esperado)
    {
        Assert.Equal(esperado, TransicionesEstado.EsTransicionValida(origen, destino));
    }

    [Fact]
    public async Task WorkflowEngine_RechazaTransicionInvalida()
    {
        var store = new InMemoryDataStore();
        var solicitudes = new MockSolicitudPagoRepository(store);
        var auditoria = new AuditService(new MockAuditoriaRepository(store));
        var motor = new WorkflowEngineService(solicitudes, auditoria);

        var solicitud = await solicitudes.CrearAsync(new SolicitudPago { Estado = EstadoSolicitud.Radicado });

        await Assert.ThrowsAsync<TransicionInvalidaException>(() =>
            motor.TransicionarAsync(solicitud, EstadoSolicitud.Pagado, usuarioId: 1, modulo: "Test"));
    }

    [Fact]
    public async Task WorkflowEngine_AplicaTransicionValidaYRegistraAuditoria()
    {
        var store = new InMemoryDataStore();
        var solicitudes = new MockSolicitudPagoRepository(store);
        var auditoria = new AuditService(new MockAuditoriaRepository(store));
        var motor = new WorkflowEngineService(solicitudes, auditoria);

        var solicitud = await solicitudes.CrearAsync(new SolicitudPago { Estado = EstadoSolicitud.Borrador });

        await motor.TransicionarAsync(solicitud, EstadoSolicitud.Radicado, usuarioId: 7, modulo: "Solicitudes");

        Assert.Equal(EstadoSolicitud.Radicado, solicitud.Estado);
        Assert.Contains(store.Auditoria, a => a.EntidadId == solicitud.Id && a.Accion == "CambioEstado" && a.UsuarioId == 7);
    }
}
