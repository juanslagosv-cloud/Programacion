using CuentasPorPagar.Domain.Entities;

namespace CuentasPorPagar.Application.Services;

/// <summary>
/// Reglas configurables de segregación de funciones (sección 54). Se evalúan en
/// backend antes de ejecutar la acción; la UI puede además ocultar el botón, pero
/// eso nunca reemplaza esta validación.
/// </summary>
public interface ISegregacionDeFuncionesService
{
    /// <summary>Un solicitante no puede aprobar su propia solicitud, salvo excepción configurada por empresa.</summary>
    bool PuedeAprobarPropiaSolicitud(int empresaId);

    bool EsAutoAprobacion(SolicitudPago solicitud, int usuarioIdQueDecide);
}

public class SegregacionDeFuncionesService : ISegregacionDeFuncionesService
{
    // TODO (Fase 4): leer la excepción por empresa desde ConfiguracionSistema/Empresas.ConfiguracionJson.
    public bool PuedeAprobarPropiaSolicitud(int empresaId) => false;

    public bool EsAutoAprobacion(SolicitudPago solicitud, int usuarioIdQueDecide)
        => solicitud.SolicitanteId == usuarioIdQueDecide || solicitud.ResponsableId == usuarioIdQueDecide;
}
