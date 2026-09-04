using CuentasPorPagar.Domain.Common;
using CuentasPorPagar.Domain.Enums;

namespace CuentasPorPagar.Domain.Entities;

/// <summary>
/// Causación registrada por Contabilidad (sección 11/12/33). El <see cref="ValorNeto"/>
/// se persiste (no solo se calcula al vuelo) para quedar congelado como el valor
/// oficial que recibe Tesorería; Tesorería nunca puede escribir sobre esta entidad
/// (regla de segregación de funciones, sección 35, aplicada en la capa de autorización).
/// </summary>
public class Causacion : EntidadBase
{
    public int SolicitudId { get; set; }
    public string? NumeroComprobante { get; set; }
    public string? NumeroDocumentoContable { get; set; }
    public decimal ValorBase { get; set; }
    public decimal Iva { get; set; }

    /// <summary>NETO A PAGAR = ValorBase + Iva - Σ retenciones/descuentos + Σ otros conceptos.</summary>
    public decimal ValorNeto { get; set; }

    public DateTime FechaCausacion { get; set; } = DateTime.UtcNow;
    public DateTime FechaVencimientoDefinitiva { get; set; }
    public string? Observaciones { get; set; }
    public int UsuarioId { get; set; }
    public int? DevueltaPorId { get; set; }

    /// <summary>Solo la causación vigente de la solicitud participa en el saldo de Tesorería.</summary>
    public bool Vigente { get; set; } = true;
}

public class RetencionCausacion : EntidadBase
{
    public int CausacionId { get; set; }
    public TipoRetencion Tipo { get; set; }
    public decimal Base { get; set; }
    public decimal Porcentaje { get; set; }
    public decimal Valor { get; set; }
}

/// <summary>
/// Un abono de pago. Relación 1—N con SolicitudPago (vía Causacion) para soportar
/// pagos parciales (sección 14/45): nunca se asume 1 factura = 1 transferencia.
/// </summary>
public class Pago : EntidadBase
{
    public int SolicitudId { get; set; }
    public int CausacionId { get; set; }
    public DateTime FechaPago { get; set; }
    public int BancoId { get; set; }
    public int CuentaBancariaId { get; set; }
    public string MedioPago { get; set; } = string.Empty;
    public decimal ValorPagado { get; set; }
    public string ReferenciaBancaria { get; set; } = string.Empty;
    public string? Observaciones { get; set; }
    public EstadoPago EstadoPago { get; set; }
    public int? MotivoDiferenciaPagoId { get; set; }
    public int UsuarioId { get; set; }
    public DateTime Fecha { get; set; } = DateTime.UtcNow;
}

public class DocumentoPago : EntidadBase
{
    public int PagoId { get; set; }
    public string DriveFileId { get; set; } = string.Empty;
    public string UrlDrive { get; set; } = string.Empty;
    public string NombreArchivo { get; set; } = string.Empty;
    public int UsuarioId { get; set; }
    public DateTime Fecha { get; set; } = DateTime.UtcNow;
}
