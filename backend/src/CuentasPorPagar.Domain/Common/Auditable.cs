namespace CuentasPorPagar.Domain.Common;

/// <summary>
/// Campos de control de concurrencia optimista y eliminación lógica compartidos
/// por las entidades financieras críticas (sección 18 y 20 de la propuesta técnica).
/// </summary>
public abstract class EntidadBase
{
    public int Id { get; set; }

    /// <summary>
    /// Token de concurrencia optimista (equivalente a un timestamp/rowversion).
    /// Toda actualización debe incluir "WHERE Id = @id AND RowVersion = @version";
    /// si no afecta filas se asume conflicto de concurrencia (sección 20.2).
    /// </summary>
    public long RowVersion { get; set; }

    public bool EliminadoLogico { get; set; }
}
