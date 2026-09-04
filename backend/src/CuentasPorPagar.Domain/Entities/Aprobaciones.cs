using CuentasPorPagar.Domain.Common;
using CuentasPorPagar.Domain.Enums;

namespace CuentasPorPagar.Domain.Entities;

/// <summary>Definición parametrizable de una ruta de aprobación (sección 18/19).</summary>
public class FlujoAprobacion : EntidadBase
{
    public int? EmpresaId { get; set; }
    public string Nombre { get; set; } = string.Empty;

    /// <summary>
    /// Reglas de aplicabilidad (empresa, proyecto, centro de costo, tipo de solicitud,
    /// rango de monto, proveedor, categoría de gasto) serializadas en JSON.
    /// Evaluadas por WorkflowEngine.ResolverFlujoAplicable; la más específica gana.
    /// </summary>
    public string CondicionJson { get; set; } = "{}";
    public bool Activo { get; set; } = true;
}

public class PasoFlujo : EntidadBase
{
    public int FlujoId { get; set; }
    public int Orden { get; set; }
    public TipoPasoFlujo Tipo { get; set; }
    public ReglaAprobacion ReglaAprobacion { get; set; } = ReglaAprobacion.Todos;

    /// <summary>Para reglas CantidadMinima/PorcentajeMinimo.</summary>
    public int? CantidadMinima { get; set; }
    public decimal? PorcentajeMinimo { get; set; }

    public int? RolRequeridoId { get; set; }
    public int? UsuarioEspecificoId { get; set; }
}

/// <summary>
/// Instancia "congelada" del flujo aplicado a una solicitud concreta (sección 10):
/// cambios posteriores a la configuración de FlujosAprobacion no deben afectar
/// solicitudes ya en curso.
/// </summary>
public class InstanciaAprobacion : EntidadBase
{
    public int SolicitudId { get; set; }
    public int FlujoId { get; set; }
    public int PasoActualId { get; set; }
    public EstadoInstanciaAprobacion Estado { get; set; } = EstadoInstanciaAprobacion.EnCurso;
    public DateTime FechaInicio { get; set; } = DateTime.UtcNow;
    public DateTime? FechaFin { get; set; }
}

public class Aprobacion : EntidadBase
{
    public int InstanciaId { get; set; }
    public int PasoId { get; set; }
    public int AprobadorId { get; set; }

    /// <summary>Si el aprobador actuó como suplente, referencia al titular (sección 25).</summary>
    public int? ActuaComoSuplenteDeId { get; set; }

    public DecisionAprobacion Decision { get; set; }
    public string? Comentario { get; set; }
    public int? MotivoDevolucionId { get; set; }
    public DateTime Fecha { get; set; } = DateTime.UtcNow;
}
