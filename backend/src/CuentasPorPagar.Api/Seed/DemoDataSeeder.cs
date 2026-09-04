using CuentasPorPagar.Application.Abstractions.Repositories;
using CuentasPorPagar.Application.Common;
using CuentasPorPagar.Domain.Entities;

namespace CuentasPorPagar.Api.Seed;

/// <summary>
/// Datos de demostración (sección 88), sembrados SOLO cuando DataProvider=Mock.
/// Resuelve el problema del "huevo y la gallina" del login (sección 4: el
/// usuario debe existir y estar Activo en Usuarios antes de poder entrar): en
/// Access real, el primer Administrador se inserta manualmente en la base antes
/// de la puesta en producción (ver backend/README.md); en Mock, este seeder lo
/// hace automáticamente al arrancar.
/// </summary>
public static class DemoDataSeeder
{
    public static async Task SembrarAsync(IServiceProvider servicios)
    {
        using var scope = servicios.CreateScope();
        var sp = scope.ServiceProvider;

        var roles = sp.GetRequiredService<IRolRepository>();
        var permisosRepo = sp.GetRequiredService<IPermisoRepository>();
        var usuarios = sp.GetRequiredService<IUsuarioRepository>();

        // 1. Permisos (catálogo completo de la sección 8).
        var permisosCreados = new Dictionary<string, int>();
        foreach (var codigo in Permisos.Todos)
        {
            var permiso = await permisosRepo.CrearAsync(new Permiso { Codigo = codigo, Modulo = codigo.Split('.')[0] });
            permisosCreados[codigo] = permiso.Id;
        }

        // 2. Roles y su matriz de permisos (sección 8). El Administrador funcional
        // recibe todos los permisos operativos; en un sistema real, un
        // administrador TÉCNICO no debería recibir por defecto permisos de
        // decisión financiera (sección 54) — aquí se simplifica para la demo.
        var matriz = new Dictionary<string, string[]>
        {
            ["Solicitante"] = new[] { Permisos.SolicitudCrear, Permisos.SolicitudRadicar, Permisos.SolicitudVerPropia },
            ["Revisor"] = new[] { Permisos.SolicitudVerTodas },
            ["Aprobador"] = new[] { Permisos.AprobacionDecidir, Permisos.SolicitudVerTodas },
            ["Contabilidad"] = new[] { Permisos.CausacionRegistrar, Permisos.CausacionDevolver, Permisos.SolicitudVerTodas, Permisos.ProveedorVerDatosBancarios },
            ["Tesoreria"] = new[] { Permisos.TesoreriaProgramarPago, Permisos.TesoreriaRegistrarPago, Permisos.TesoreriaDevolverContabilidad, Permisos.SolicitudVerTodas, Permisos.ProveedorVerDatosBancarios },
            ["Auditor"] = new[] { Permisos.AuditoriaVer, Permisos.SolicitudVerTodas },
            ["Administrador"] = Permisos.Todos,
        };

        var rolesCreados = new Dictionary<string, int>();
        foreach (var (nombreRol, codigosPermiso) in matriz)
        {
            var rol = await roles.CrearAsync(new Rol { Nombre = nombreRol });
            rolesCreados[nombreRol] = rol.Id;
            foreach (var codigo in codigosPermiso)
            {
                await roles.AsignarPermisoAsync(rol.Id, permisosCreados[codigo]);
            }
        }

        // 3. Usuarios de ejemplo (sección 88), uno por rol, todos Activos.
        var usuariosDemo = new (string Nombre, string Correo, string Rol)[]
        {
            ("Laura Gómez", "laura.gomez@empresa.com", "Solicitante"),
            ("Andrés Ruiz", "andres.ruiz@empresa.com", "Revisor"),
            ("Carlos Pérez", "carlos.perez@empresa.com", "Aprobador"),
            ("Andrea Rojas", "andrea.rojas@empresa.com", "Contabilidad"),
            ("Diego Sánchez", "diego.sanchez@empresa.com", "Tesoreria"),
            ("Marta Londoño", "marta.londono@empresa.com", "Auditor"),
            ("Admin Sistema", "admin@empresa.com", "Administrador"),
        };

        foreach (var (nombre, correo, rol) in usuariosDemo)
        {
            var usuario = await usuarios.CrearAsync(new Usuario { Nombre = nombre, Correo = correo, Activo = true });
            await roles.AsignarRolAUsuarioAsync(usuario.Id, rolesCreados[rol], empresaId: null);
        }
    }
}
