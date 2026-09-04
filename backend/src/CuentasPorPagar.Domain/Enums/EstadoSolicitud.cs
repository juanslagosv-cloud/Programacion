namespace CuentasPorPagar.Domain.Enums;

/// <summary>
/// Estados de la máquina de estados de una SolicitudPago (sección 9 de la propuesta técnica).
/// El valor numérico es estable: se persiste en Access y nunca debe reordenarse.
/// </summary>
public enum EstadoSolicitud
{
    Borrador = 0,
    Radicado = 1,
    PendienteDeRevision = 2,
    PendienteDeAprobacion = 3,
    DevueltoParaCorreccion = 4,
    Rechazado = 5,
    Aprobado = 6,
    PendienteDeCausacion = 7,
    DevueltoPorContabilidad = 8,
    Causado = 9,
    PagoProgramado = 10,
    PagoParcial = 11,
    Pagado = 12,
    Cerrado = 13,
    Anulado = 14
}
