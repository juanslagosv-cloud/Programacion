using CuentasPorPagar.Application.Services;
using CuentasPorPagar.Infrastructure.Access;
using CuentasPorPagar.Infrastructure.Mock;

var builder = WebApplication.CreateBuilder(args);

// DataProvider selecciona la implementación de persistencia (sección 61-64/87):
// "Mock" = en memoria, sin Access ni Google reales (desarrollo/demo);
// "Access" = Microsoft Access vía OLE DB (requiere host Windows, sección 4).
// Se lee de configuración/entorno para no acoplar el código a un valor fijo,
// preparando el reemplazo futuro por SqlServer/PostgreSQL (sección 23) sin
// tocar Application, Controllers ni Frontend.
var dataProvider = builder.Configuration["DataProvider"] ?? "Mock";

if (string.Equals(dataProvider, "Access", StringComparison.OrdinalIgnoreCase))
{
    builder.Services.AddAccessInfrastructure(builder.Configuration);
}
else
{
    builder.Services.AddMockInfrastructure();
}

// INTEGRATION_MODE gobierna las integraciones externas (Drive/Gmail/OAuth, punto 87)
// de forma independiente del proveedor de datos: se puede correr con Access real
// y aun así simular Drive/Gmail mientras no haya credenciales de Google listas.
var integrationMode = builder.Configuration["IntegrationMode"] ?? "mock";
if (string.Equals(integrationMode, "google", StringComparison.OrdinalIgnoreCase))
{
    // TODO (Fase 3/12/13): builder.Services.AddGoogleInfrastructure(builder.Configuration);
    throw new NotImplementedException(
        "IntegrationMode=google aún no está implementado (Infrastructure.Google pendiente, ver Fases 3/12/13). Use IntegrationMode=mock.");
}
else if (string.Equals(dataProvider, "Access", StringComparison.OrdinalIgnoreCase))
{
    // DataProvider=Access + IntegrationMode=mock: Access real, Drive/Gmail simulados
    // mientras no haya credenciales de Google Workspace configuradas.
    builder.Services.AddMockIntegrations();
}
// Si DataProvider=Mock, AddMockInfrastructure() ya registró también las integraciones mock.

builder.Services.AddScoped<WorkflowEngineService>();
builder.Services.AddScoped<SecuenciaRadicadoService>();
builder.Services.AddScoped<IAuditService, AuditService>();
builder.Services.AddScoped<ISegregacionDeFuncionesService, SegregacionDeFuncionesService>();

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

builder.Services.AddCors(options =>
{
    // Origen del frontend Next.js (sección 3/83): el navegador nunca habla con
    // Access/Drive/Gmail directamente, solo con esta API.
    options.AddPolicy("Frontend", policy =>
    {
        var origenes = builder.Configuration.GetSection("Cors:AllowedOrigins").Get<string[]>()
            ?? new[] { "http://localhost:3000" };
        policy.WithOrigins(origenes).AllowAnyHeader().AllowAnyMethod().AllowCredentials();
    });
});

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();
app.UseCors("Frontend");
app.UseAuthorization();
app.MapControllers();

// Endpoint de diagnóstico: confirma qué DataProvider/IntegrationMode está activo
// sin exponer secretos (sección 93 - logging estructurado, nada sensible).
app.MapGet("/api/sistema/estado", (IConfiguration config) => Results.Ok(new
{
    dataProvider = config["DataProvider"] ?? "Mock",
    integrationMode = config["IntegrationMode"] ?? "mock",
    ambiente = app.Environment.EnvironmentName
}));

app.Run();

public partial class Program { }
