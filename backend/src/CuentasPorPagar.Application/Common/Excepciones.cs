namespace CuentasPorPagar.Application.Common;

/// <summary>Se lanza cuando una actualización optimista no encuentra la RowVersion esperada (sección 20.2).</summary>
public class ConcurrenciaException : Exception
{
    public ConcurrenciaException(string entidad, int id)
        : base($"{entidad} (Id={id}) fue modificado por otro usuario. Recargue e intente nuevamente.") { }
}

/// <summary>Se lanza cuando se intenta una transición de estado no permitida (regla del punto 99).</summary>
public class TransicionInvalidaException : Exception
{
    public TransicionInvalidaException(string origen, string destino)
        : base($"No se permite pasar de '{origen}' a '{destino}' fuera del flujo de workflow.") { }
}

/// <summary>Se lanza cuando una regla de segregación de funciones bloquea una acción (sección 54).</summary>
public class SegregacionDeFuncionesException : Exception
{
    public SegregacionDeFuncionesException(string mensaje) : base(mensaje) { }
}

public class PermisoDenegadoException : Exception
{
    public PermisoDenegadoException(string permiso) : base($"No tiene el permiso requerido: {permiso}") { }
}

public class ReglaDeNegocioException : Exception
{
    public ReglaDeNegocioException(string mensaje) : base(mensaje) { }
}
