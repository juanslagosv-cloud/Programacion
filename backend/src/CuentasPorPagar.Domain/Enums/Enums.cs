namespace CuentasPorPagar.Domain.Enums;

public enum TipoPasoFlujo
{
    Secuencial = 0,
    Paralelo = 1
}

/// <summary>Regla de resolución de un paso paralelo de aprobación (punto 21 de la propuesta).</summary>
public enum ReglaAprobacion
{
    Todos = 0,
    UnoBasta = 1,
    CantidadMinima = 2,
    PorcentajeMinimo = 3
}

public enum DecisionAprobacion
{
    Aprobado = 0,
    Rechazado = 1,
    Devuelto = 2
}

public enum EstadoInstanciaAprobacion
{
    EnCurso = 0,
    Completada = 1,
    Rechazada = 2,
    Devuelta = 3
}

public enum EstadoPago
{
    Programado = 0,
    Parcial = 1,
    Completo = 2
}

/// <summary>Componentes del cálculo del neto a pagar (sección 12).</summary>
public enum TipoRetencion
{
    ReteFuente = 0,
    ReteIca = 1,
    ReteIva = 2,
    OtraRetencion = 3,
    Descuento = 4,
    OtroConcepto = 5
}

public enum EstadoEnvio
{
    Pendiente = 0,
    Enviado = 1,
    Fallido = 2
}

/// <summary>Tipo de trabajo encolado para reintento (punto 71/72 - fallas de Drive/correo).</summary>
public enum TipoOperacionSincronizacion
{
    DriveCrearCarpeta = 0,
    DriveSubirArchivo = 1,
    EnvioCorreo = 2
}

public enum EstadoTrabajoSincronizacion
{
    Pendiente = 0,
    Fallido = 1,
    Completado = 2
}

public enum TipoDocumentoVida
{
    Vigente = 0,
    NoVigente = 1
}
