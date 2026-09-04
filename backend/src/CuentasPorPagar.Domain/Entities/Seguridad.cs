using CuentasPorPagar.Domain.Common;

namespace CuentasPorPagar.Domain.Entities;

/// <summary>Usuario del sistema (sección 4/6). La autenticación real vive en Application/IAuthProvider.</summary>
public class Usuario : EntidadBase
{
    public string GoogleSub { get; set; } = string.Empty;
    public string Correo { get; set; } = string.Empty;
    public string Nombre { get; set; } = string.Empty;
    public bool Activo { get; set; } = true;
    public DateTime? UltimoLogin { get; set; }
    public DateTime FechaCreacion { get; set; } = DateTime.UtcNow;
}

public class Rol : EntidadBase
{
    public string Nombre { get; set; } = string.Empty;
    public string? Descripcion { get; set; }
}

public class Permiso : EntidadBase
{
    public string Codigo { get; set; } = string.Empty;
    public string? Descripcion { get; set; }
    public string Modulo { get; set; } = string.Empty;
}

public class RolPermiso
{
    public int RolId { get; set; }
    public int PermisoId { get; set; }
}

/// <summary>
/// Asignación de rol a usuario, opcionalmente restringida a una empresa
/// (una persona puede tener roles distintos por empresa, punto 3).
/// </summary>
public class UsuarioRol
{
    public int UsuarioId { get; set; }
    public int RolId { get; set; }
    public int? EmpresaId { get; set; }
}

/// <summary>Suplencia temporal de un aprobador (sección 25).</summary>
public class Delegacion : EntidadBase
{
    public int TitularId { get; set; }
    public int SuplenteId { get; set; }
    public int RolId { get; set; }
    public DateTime FechaInicio { get; set; }
    public DateTime FechaFin { get; set; }
    public string Motivo { get; set; } = string.Empty;
    public int CreadoPorId { get; set; }

    public bool EstaVigente(DateTime fecha) => fecha.Date >= FechaInicio.Date && fecha.Date <= FechaFin.Date;
}
