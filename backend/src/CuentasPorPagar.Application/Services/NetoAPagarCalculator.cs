using CuentasPorPagar.Domain.Entities;
using CuentasPorPagar.Domain.Enums;

namespace CuentasPorPagar.Application.Services;

/// <summary>
/// Cálculo del NETO A PAGAR (sección 12/34): recalculado siempre en backend, nunca
/// confiando en el valor enviado por el navegador. Cada componente (retención,
/// descuento, otro concepto) se guarda individualmente en RetencionCausacion.
/// </summary>
public static class NetoAPagarCalculator
{
    public static decimal Calcular(decimal valorBase, decimal iva, IReadOnlyList<RetencionCausacion> retenciones)
    {
        var deducciones = retenciones
            .Where(r => r.Tipo is TipoRetencion.ReteFuente or TipoRetencion.ReteIca or TipoRetencion.ReteIva
                     or TipoRetencion.OtraRetencion or TipoRetencion.Descuento)
            .Sum(r => r.Valor);

        var adiciones = retenciones
            .Where(r => r.Tipo == TipoRetencion.OtroConcepto)
            .Sum(r => r.Valor);

        return valorBase + iva - deducciones + adiciones;
    }

    /// <summary>Valida que el neto declarado coincida con el recalculado (tolerancia por redondeo).</summary>
    public static bool Coincide(decimal netoDeclarado, decimal netoCalculado, decimal tolerancia = 1m)
        => Math.Abs(netoDeclarado - netoCalculado) <= tolerancia;
}
