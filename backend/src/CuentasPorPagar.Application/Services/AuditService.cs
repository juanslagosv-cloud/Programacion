using CuentasPorPagar.Application.Abstractions.Repositories;
using CuentasPorPagar.Domain.Entities;

namespace CuentasPorPagar.Application.Services;

/// <summary>
/// Fachada de auditoría (sección 18/53). Todo Service de caso de uso que escriba
/// datos financieros o de workflow debe llamar a este servicio; nunca se escribe
/// en IAuditoriaRepository directamente desde un controlador.
/// </summary>
public interface IAuditService
{
    Task RegistrarAsync(
        int usuarioId, string accion, string modulo, string entidadTipo, int entidadId,
        string? valorAnterior, string? valorNuevo, string? comentario, string resultado = "Exitoso", CancellationToken ct = default);
}

public class AuditService : IAuditService
{
    private readonly IAuditoriaRepository _repositorio;

    public AuditService(IAuditoriaRepository repositorio)
    {
        _repositorio = repositorio;
    }

    public Task RegistrarAsync(
        int usuarioId, string accion, string modulo, string entidadTipo, int entidadId,
        string? valorAnterior, string? valorNuevo, string? comentario, string resultado = "Exitoso", CancellationToken ct = default)
    {
        var registro = new RegistroAuditoria
        {
            UsuarioId = usuarioId,
            Fecha = DateTime.UtcNow,
            Accion = accion,
            Modulo = modulo,
            EntidadTipo = entidadTipo,
            EntidadId = entidadId,
            ValorAnteriorJson = valorAnterior,
            ValorNuevoJson = valorNuevo,
            Comentario = comentario,
            Resultado = resultado
        };

        return _repositorio.RegistrarAsync(registro, ct);
    }
}
