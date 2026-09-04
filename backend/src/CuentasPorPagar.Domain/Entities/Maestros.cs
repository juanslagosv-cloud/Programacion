using CuentasPorPagar.Domain.Common;

namespace CuentasPorPagar.Domain.Entities;

public class Empresa : EntidadBase
{
    public string RazonSocial { get; set; } = string.Empty;
    public string Nit { get; set; } = string.Empty;
    public string NombreCorto { get; set; } = string.Empty;
    public bool Activa { get; set; } = true;
    public string? DriveFolderId { get; set; }
    public string? ConfiguracionJson { get; set; }
}

public class Proveedor : EntidadBase
{
    public int EmpresaId { get; set; }
    public string Nit { get; set; } = string.Empty;
    public string RazonSocial { get; set; } = string.Empty;
    public string? NombreComercial { get; set; }
    public string TipoProveedor { get; set; } = string.Empty;
    public bool Activo { get; set; } = true;
    public string? Correo { get; set; }
    public string? Telefono { get; set; }
    public string? InfoTributariaJson { get; set; }
    public DateTime FechaActualizacion { get; set; } = DateTime.UtcNow;
}

/// <summary>
/// Dato sensible (sección 56/82): el número de cuenta se guarda cifrado
/// (<see cref="NumeroCuentaCifrado"/>) y solo se expone enmascarado
/// ("********4582") a usuarios sin el permiso proveedor.ver_datos_bancarios.
/// </summary>
public class ProveedorCuentaBancaria : EntidadBase
{
    public int ProveedorId { get; set; }
    public string Banco { get; set; } = string.Empty;
    public string TipoCuenta { get; set; } = string.Empty;
    public string NumeroCuentaCifrado { get; set; } = string.Empty;
    public string Titular { get; set; } = string.Empty;
    public string? CertificacionDriveFileId { get; set; }
    public DateTime FechaActualizacion { get; set; } = DateTime.UtcNow;
    public bool Vigente { get; set; } = true;
}

public class Proyecto : EntidadBase
{
    public int EmpresaId { get; set; }
    public string Codigo { get; set; } = string.Empty;
    public string Nombre { get; set; } = string.Empty;
    public int? ResponsableId { get; set; }
    public int? DirectorId { get; set; }
    public bool Activo { get; set; } = true;
}

public class CentroCosto : EntidadBase
{
    public string Codigo { get; set; } = string.Empty;
    public string Nombre { get; set; } = string.Empty;
    public int EmpresaId { get; set; }
    public int? ProyectoId { get; set; }
    public bool Activo { get; set; } = true;
}

public class Banco : EntidadBase
{
    public int EmpresaId { get; set; }
    public string Nombre { get; set; } = string.Empty;
    public string TipoCuenta { get; set; } = string.Empty;
    public string NumeroCuentaCifrado { get; set; } = string.Empty;
    public string NombreInterno { get; set; } = string.Empty;
    public bool Activo { get; set; } = true;
    public string Moneda { get; set; } = "COP";
}

public class TipoSolicitud : EntidadBase
{
    public string Codigo { get; set; } = string.Empty;
    public string Nombre { get; set; } = string.Empty;
    public bool Activo { get; set; } = true;
}

public class TipoDocumento : EntidadBase
{
    public string Codigo { get; set; } = string.Empty;
    public string Nombre { get; set; } = string.Empty;
    public bool Activo { get; set; } = true;
}

/// <summary>
/// Regla de documento obligatorio dinámico (sección 12 del requerimiento):
/// depende de tipo de solicitud, opcionalmente de empresa, tipo de proveedor y rango de monto.
/// </summary>
public class DocumentoObligatorioConfig : EntidadBase
{
    public int TipoSolicitudId { get; set; }
    public int TipoDocumentoId { get; set; }
    public int? EmpresaId { get; set; }
    public string? TipoProveedor { get; set; }
    public decimal? MontoDesde { get; set; }
    public decimal? MontoHasta { get; set; }
    public bool Obligatorio { get; set; } = true;
}

public class MotivoDevolucion : EntidadBase
{
    public string Codigo { get; set; } = string.Empty;
    public string Texto { get; set; } = string.Empty;
    public bool Activo { get; set; } = true;
}

public class MotivoRechazo : EntidadBase
{
    public string Codigo { get; set; } = string.Empty;
    public string Texto { get; set; } = string.Empty;
    public bool Activo { get; set; } = true;
}

public class MotivoDiferenciaPago : EntidadBase
{
    public string Codigo { get; set; } = string.Empty;
    public string Texto { get; set; } = string.Empty;
    public bool Activo { get; set; } = true;
}

public class PlantillaCorreo : EntidadBase
{
    public string Codigo { get; set; } = string.Empty;
    public string Asunto { get; set; } = string.Empty;
    public string CuerpoHtml { get; set; } = string.Empty;
    public string? VariablesJson { get; set; }
    public bool Activo { get; set; } = true;
}

/// <summary>Parámetros administrables sin tocar código (formato de radicado, días "próximo a vencer", etc.).</summary>
public class ConfiguracionSistema
{
    public string Clave { get; set; } = string.Empty;
    public string Valor { get; set; } = string.Empty;
    public string? Descripcion { get; set; }
}
