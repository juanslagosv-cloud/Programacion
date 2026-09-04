using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;

namespace CuentasPorPagar.Api.Auth;

/// <summary>
/// Exige que el JWT del usuario autenticado incluya el claim "permiso" con el
/// código dado (sección 8/54/81: "no basta con ocultar botones visualmente";
/// "cada endpoint del backend vuelve a validar el permiso"). Implica [Authorize]:
/// un request sin token válido recibe 401 antes de llegar a este filtro.
/// </summary>
[AttributeUsage(AttributeTargets.Class | AttributeTargets.Method)]
public class PermisoRequeridoAttribute : TypeFilterAttribute
{
    public PermisoRequeridoAttribute(string codigoPermiso) : base(typeof(PermisoRequeridoFilter))
    {
        Arguments = new object[] { codigoPermiso };
    }
}

public class PermisoRequeridoFilter : IAsyncAuthorizationFilter
{
    private readonly string _codigoPermiso;

    public PermisoRequeridoFilter(string codigoPermiso)
    {
        _codigoPermiso = codigoPermiso;
    }

    public Task OnAuthorizationAsync(AuthorizationFilterContext context)
    {
        var usuario = context.HttpContext.User;

        if (usuario.Identity?.IsAuthenticated != true)
        {
            context.Result = new UnauthorizedResult();
            return Task.CompletedTask;
        }

        var tienePermiso = usuario.Claims.Any(c => c.Type == "permiso" && c.Value == _codigoPermiso);
        if (!tienePermiso)
        {
            context.Result = new ObjectResult(new { error = $"No tiene el permiso requerido: {_codigoPermiso}" })
            {
                StatusCode = StatusCodes.Status403Forbidden
            };
        }

        return Task.CompletedTask;
    }
}
