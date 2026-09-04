using CuentasPorPagar.Domain.Enums;

namespace CuentasPorPagar.Domain.Entities;

public class Notificacion
{
    public int Id { get; set; }
    public int UsuarioId { get; set; }
    public string Tipo { get; set; } = string.Empty;
    public string Titulo { get; set; } = string.Empty;
    public string Mensaje { get; set; } = string.Empty;
    public int? SolicitudId { get; set; }
    public bool Leida { get; set; }
    public DateTime FechaCreacion { get; set; } = DateTime.UtcNow;
    public DateTime? FechaLectura { get; set; }
    public EstadoEnvio EstadoEnvioCorreo { get; set; } = EstadoEnvio.Pendiente;
}

/// <summary>
/// Registro de auditoría append-only (sección 18/53): no existe operación de
/// actualización ni borrado expuesta por la aplicación sobre esta entidad.
/// </summary>
public class RegistroAuditoria
{
    public int Id { get; set; }
    public int UsuarioId { get; set; }
    public DateTime Fecha { get; set; } = DateTime.UtcNow;
    public string Accion { get; set; } = string.Empty;
    public string Modulo { get; set; } = string.Empty;
    public string EntidadTipo { get; set; } = string.Empty;
    public int EntidadId { get; set; }
    public string? ValorAnteriorJson { get; set; }
    public string? ValorNuevoJson { get; set; }
    public string? Comentario { get; set; }
    public string Resultado { get; set; } = "Exitoso";
    public string? IpOrigen { get; set; }
}

/// <summary>
/// Consecutivo de radicado por año (sección 9/20). El acceso concurrente se
/// serializa en Application.Services.SecuenciaRadicadoService; esta entidad
/// solo representa el estado persistido.
/// </summary>
public class SecuenciaRadicado
{
    public string Clave { get; set; } = string.Empty;
    public long UltimoValor { get; set; }
    public long RowVersion { get; set; }
}

/// <summary>
/// Cola de reintentos para operaciones de integración que no deben bloquear
/// el flujo principal si Drive o Gmail fallan temporalmente (sección 71/72).
/// </summary>
public class TrabajoSincronizacion
{
    public int Id { get; set; }
    public TipoOperacionSincronizacion TipoOperacion { get; set; }
    public string PayloadJson { get; set; } = string.Empty;
    public int Intentos { get; set; }
    public EstadoTrabajoSincronizacion Estado { get; set; } = EstadoTrabajoSincronizacion.Pendiente;
    public string? UltimoError { get; set; }
    public DateTime FechaCreacion { get; set; } = DateTime.UtcNow;
    public DateTime? FechaUltimoIntento { get; set; }
}
