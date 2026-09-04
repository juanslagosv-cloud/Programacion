using CuentasPorPagar.Domain.Common;
using CuentasPorPagar.Domain.Enums;

namespace CuentasPorPagar.Domain.Entities;

/// <summary>
/// Agregado raíz del proceso (sección 6/7). El campo <see cref="Estado"/> nunca se
/// asigna directamente desde un endpoint genérico: solo el WorkflowEngine
/// (Application) puede cambiarlo, a través de una acción de negocio válida (punto 10/99).
/// </summary>
public class SolicitudPago : EntidadBase
{
    /// <summary>Consecutivo único, formato parametrizable (ej. RAD-2026-000001). Ver ISecuenciaRadicadoRepository.</summary>
    public string Radicado { get; set; } = string.Empty;

    public int EmpresaId { get; set; }
    public int TipoSolicitudId { get; set; }
    public int ProveedorId { get; set; }
    public string TipoDocumento { get; set; } = string.Empty;
    public string? NumeroFactura { get; set; }
    public string? NumeroCuentaCobro { get; set; }
    public DateTime FechaEmision { get; set; }
    public DateTime FechaVencimiento { get; set; }
    public string Moneda { get; set; } = "COP";
    public decimal ValorAntesImpuestos { get; set; }
    public decimal Iva { get; set; }
    public decimal ValorBruto { get; set; }
    public string Concepto { get; set; } = string.Empty;
    public int? ProyectoId { get; set; }
    public int? CentroCostoId { get; set; }
    public string? OrdenCompra { get; set; }
    public string? Contrato { get; set; }
    public int ResponsableId { get; set; }
    public string? Observaciones { get; set; }

    public EstadoSolicitud Estado { get; set; } = EstadoSolicitud.Borrador;

    public int SolicitanteId { get; set; }
    public string? DriveFolderId { get; set; }

    public DateTime FechaCreacion { get; set; } = DateTime.UtcNow;
    public DateTime? FechaRadicacion { get; set; }
}
