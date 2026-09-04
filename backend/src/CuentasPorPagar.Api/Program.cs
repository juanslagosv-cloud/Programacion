using System.Text;
using CuentasPorPagar.Api.Auth;
using CuentasPorPagar.Api.Seed;
using CuentasPorPagar.Application.Services;
using CuentasPorPagar.Infrastructure.Access;
using CuentasPorPagar.Infrastructure.Google;
using CuentasPorPagar.Infrastructure.Mock;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;

var builder = WebApplication.CreateBuilder(args);

// DataProvider selecciona la implementación de persistencia (sección 61-64/87):
// "Mock" = en memoria, sin Access ni Google reales (desarrollo/demo);
// "Access" = Microsoft Access vía OLE DB (requiere host Windows, sección 4).
// Se lee de configuración/entorno para no acoplar el código a un valor fijo,
// preparando el reemplazo futuro por SqlServer/PostgreSQL (sección 23) sin
// tocar Application, Controllers ni Frontend.
var dataProvider = builder.Configuration["DataProvider"] ?? "Mock";
var esDataProviderMock = string.Equals(dataProvider, "Mock", StringComparison.OrdinalIgnoreCase);

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
    // Login real con Google ya está implementado (Fase 3, GoogleAuthProvider).
    // Drive/Gmail reales siguen pendientes (Fases 12/13): AddGoogleInfrastructure
    // los registra igual, pero lanzan NotImplementedException si se invocan.
    builder.Services.AddGoogleInfrastructure(builder.Configuration);
}
else if (string.Equals(dataProvider, "Access", StringComparison.OrdinalIgnoreCase))
{
    // DataProvider=Access + IntegrationMode=mock: Access real, Drive/Gmail/OAuth
    // simulados mientras no haya credenciales de Google Workspace configuradas.
    builder.Services.AddMockIntegrations();
}
// Si DataProvider=Mock, AddMockInfrastructure() ya registró también las integraciones mock.

builder.Services.AddScoped<WorkflowEngineService>();
builder.Services.AddScoped<SecuenciaRadicadoService>();
builder.Services.AddScoped<IAuditService, AuditService>();
builder.Services.AddScoped<ISegregacionDeFuncionesService, SegregacionDeFuncionesService>();
builder.Services.AddScoped<IAutenticacionService, AutenticacionService>();

// --- Autenticación (sección 4/19): JWT propio de la aplicación, emitido tras
// validar el login (Google real o Mock, según IntegrationMode). Desacoplado de
// CÓMO se validó la identidad externa: el resto de la app solo conoce este JWT.
builder.Services.Configure<JwtOptions>(builder.Configuration.GetSection(JwtOptions.SeccionConfiguracion));
builder.Services.AddSingleton<IJwtTokenService, JwtTokenService>();

var jwtOptions = builder.Configuration.GetSection(JwtOptions.SeccionConfiguracion).Get<JwtOptions>() ?? new JwtOptions();
if (string.IsNullOrWhiteSpace(jwtOptions.SigningKey))
{
    if (builder.Environment.IsDevelopment())
    {
        // Solo para desarrollo local: nunca usar una clave generada así en producción
        // (debe venir de JWT_SIGNING_KEY, ver .env.example).
        jwtOptions.SigningKey = "clave-de-desarrollo-NO-usar-en-produccion-min-32-caracteres";
    }
    else
    {
        throw new InvalidOperationException("Jwt:SigningKey (JWT_SIGNING_KEY) es obligatorio fuera de Development.");
    }
}

builder.Services
    .AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidIssuer = jwtOptions.Issuer,
            ValidateAudience = true,
            ValidAudience = jwtOptions.Audience,
            ValidateIssuerSigningKey = true,
            IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtOptions.SigningKey)),
            ValidateLifetime = true,
            ClockSkew = TimeSpan.FromSeconds(30)
        };
    });

builder.Services.AddAuthorization();

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
app.UseAuthentication();
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

// Datos de demostración (sección 88): solo en modo Mock, nunca contra Access real
// (ahí el primer Administrador se crea manualmente, ver backend/README.md).
if (esDataProviderMock)
{
    await DemoDataSeeder.SembrarAsync(app.Services);
}

app.Run();

public partial class Program { }
