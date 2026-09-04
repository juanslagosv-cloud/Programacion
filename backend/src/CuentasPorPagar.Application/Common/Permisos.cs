namespace CuentasPorPagar.Application.Common;

/// <summary>
/// Catálogo de códigos de permiso (sección 8, matriz de roles y permisos). Estas
/// constantes son la única fuente de verdad usada tanto para sembrar
/// Roles/Permisos en modo demostración como para decorar endpoints con
/// [PermisoRequerido] — evita que el código y los datos de permisos diverjan.
/// </summary>
public static class Permisos
{
    public const string SolicitudCrear = "solicitud.crear";
    public const string SolicitudRadicar = "solicitud.radicar";
    public const string SolicitudVerPropia = "solicitud.ver.propia";
    public const string SolicitudVerTodas = "solicitud.ver.todas";

    public const string AprobacionDecidir = "aprobacion.decidir";

    public const string CausacionRegistrar = "causacion.registrar";
    public const string CausacionDevolver = "causacion.devolver";

    public const string TesoreriaProgramarPago = "tesoreria.programar_pago";
    public const string TesoreriaRegistrarPago = "tesoreria.registrar_pago";
    public const string TesoreriaDevolverContabilidad = "tesoreria.devolver_contabilidad";

    public const string ProveedorVerDatosBancarios = "proveedor.ver_datos_bancarios";
    public const string ProveedorEditar = "proveedor.editar";

    public const string AuditoriaVer = "auditoria.ver";

    public const string AdminConfigurar = "admin.configurar";

    /// <summary>Todos los códigos declarados (usado por el seeder de demostración).</summary>
    public static readonly string[] Todos =
    {
        SolicitudCrear, SolicitudRadicar, SolicitudVerPropia, SolicitudVerTodas,
        AprobacionDecidir,
        CausacionRegistrar, CausacionDevolver,
        TesoreriaProgramarPago, TesoreriaRegistrarPago, TesoreriaDevolverContabilidad,
        ProveedorVerDatosBancarios, ProveedorEditar,
        AuditoriaVer,
        AdminConfigurar
    };
}
