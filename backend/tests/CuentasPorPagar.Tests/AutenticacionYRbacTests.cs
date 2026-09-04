using System.Net;
using System.Net.Http.Json;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Mvc.Testing;
using Xunit;

namespace CuentasPorPagar.Tests;

/// <summary>
/// Pruebas de integración sobre el pipeline HTTP real (login -> JWT -> autorización),
/// usando los datos de demostración sembrados por DemoDataSeeder en modo Mock.
/// Cubren directamente el punto 86: "un usuario sin permisos no puede acceder" a
/// una acción reservada a otro rol, verificado en el BACKEND (no solo oculto en
/// la UI, sección 3/81).
/// </summary>
public class AutenticacionYRbacTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly WebApplicationFactory<Program> _factory;

    public AutenticacionYRbacTests(WebApplicationFactory<Program> factory)
    {
        // Se fija explícitamente el ambiente y una clave de firma de prueba, en vez
        // de depender de la detección automática de "Development" del host de
        // pruebas (evita que el arranque falle si esa detección cambia de versión).
        _factory = factory.WithWebHostBuilder(builder =>
        {
            builder.UseEnvironment("Development");
            builder.UseSetting("Jwt:SigningKey", "clave-de-pruebas-min-32-caracteres-000000");
        });
    }

    private static string TokenMockPara(string correo, string nombre) => $"mock:{correo}:{nombre}";

    private async Task<string> IniciarSesionAsync(HttpClient cliente, string correo, string nombre)
    {
        var respuesta = await cliente.PostAsJsonAsync("/api/auth/login", new { token = TokenMockPara(correo, nombre) });
        respuesta.EnsureSuccessStatusCode();
        var cuerpo = await respuesta.Content.ReadFromJsonAsync<LoginResponse>();
        return cuerpo!.token;
    }

    private record LoginResponse(string token, PerfilResponse perfil);
    private record PerfilResponse(int id, string nombre, string correo, string[] roles, string[] permisos);

    [Fact]
    public async Task Login_ConUsuarioSembradoYActivo_DevuelveTokenYPermisosDeSuRol()
    {
        var cliente = _factory.CreateClient();

        var respuesta = await cliente.PostAsJsonAsync("/api/auth/login", new { token = TokenMockPara("laura.gomez@empresa.com", "Laura Gómez") });

        Assert.Equal(HttpStatusCode.OK, respuesta.StatusCode);
        var cuerpo = await respuesta.Content.ReadFromJsonAsync<LoginResponse>();
        Assert.Contains("Solicitante", cuerpo!.perfil.roles);
        Assert.Contains("solicitud.crear", cuerpo.perfil.permisos);
        Assert.DoesNotContain("admin.configurar", cuerpo.perfil.permisos);
    }

    [Fact]
    public async Task Login_ConCorreoQueNoExisteEnUsuarios_Devuelve401()
    {
        var cliente = _factory.CreateClient();

        var respuesta = await cliente.PostAsJsonAsync("/api/auth/login", new { token = TokenMockPara("no.existe@empresa.com", "Nadie") });

        Assert.Equal(HttpStatusCode.Unauthorized, respuesta.StatusCode);
    }

    [Fact]
    public async Task Endpoint_SinToken_Devuelve401()
    {
        var cliente = _factory.CreateClient();

        var respuesta = await cliente.GetAsync("/api/auth/me");

        Assert.Equal(HttpStatusCode.Unauthorized, respuesta.StatusCode);
    }

    [Fact]
    public async Task UsuarioSinPermisoSolicitudCrear_NoPuedeCrearSolicitud()
    {
        var cliente = _factory.CreateClient();
        // Diego Sánchez es Tesorería (sembrado por DemoDataSeeder): no tiene solicitud.crear.
        var token = await IniciarSesionAsync(cliente, "diego.sanchez@empresa.com", "Diego Sánchez");
        cliente.DefaultRequestHeaders.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", token);

        var respuesta = await cliente.PostAsJsonAsync("/api/solicitudes/borradores", new
        {
            empresaId = 1,
            tipoSolicitudId = 1,
            proveedorId = 1,
            tipoDocumento = "Factura",
            numeroFactura = (string?)null,
            fechaEmision = DateTime.UtcNow,
            fechaVencimiento = DateTime.UtcNow.AddDays(30),
            valorAntesImpuestos = 100m,
            iva = 19m,
            valorBruto = 119m,
            concepto = "Prueba",
            proyectoId = (int?)null,
            centroCostoId = (int?)null,
            responsableId = 1
        });

        Assert.Equal(HttpStatusCode.Forbidden, respuesta.StatusCode);
    }

    [Fact]
    public async Task UsuarioConPermisoSolicitudCrear_SiPuedeCrearSolicitud()
    {
        var cliente = _factory.CreateClient();
        var token = await IniciarSesionAsync(cliente, "laura.gomez@empresa.com", "Laura Gómez");
        cliente.DefaultRequestHeaders.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", token);

        var respuesta = await cliente.PostAsJsonAsync("/api/solicitudes/borradores", new
        {
            empresaId = 1,
            tipoSolicitudId = 1,
            proveedorId = 1,
            tipoDocumento = "Factura",
            numeroFactura = (string?)null,
            fechaEmision = DateTime.UtcNow,
            fechaVencimiento = DateTime.UtcNow.AddDays(30),
            valorAntesImpuestos = 100m,
            iva = 19m,
            valorBruto = 119m,
            concepto = "Prueba",
            proyectoId = (int?)null,
            centroCostoId = (int?)null,
            responsableId = 1
        });

        Assert.Equal(HttpStatusCode.OK, respuesta.StatusCode);
    }

    [Fact]
    public async Task SolicitanteSinAdminConfigurar_NoPuedeCrearEmpresa()
    {
        var cliente = _factory.CreateClient();
        var token = await IniciarSesionAsync(cliente, "laura.gomez@empresa.com", "Laura Gómez");
        cliente.DefaultRequestHeaders.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", token);

        var respuesta = await cliente.PostAsJsonAsync("/api/empresas", new { razonSocial = "X", nit = "999", nombreCorto = "X" });

        Assert.Equal(HttpStatusCode.Forbidden, respuesta.StatusCode);
    }

    [Fact]
    public async Task Administrador_SiPuedeCrearEmpresa()
    {
        var cliente = _factory.CreateClient();
        var token = await IniciarSesionAsync(cliente, "admin@empresa.com", "Admin Sistema");
        cliente.DefaultRequestHeaders.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", token);

        var respuesta = await cliente.PostAsJsonAsync("/api/empresas", new { razonSocial = "Empresa Demo", nit = $"NIT-{Guid.NewGuid():N}", nombreCorto = "Demo" });

        Assert.Equal(HttpStatusCode.Created, respuesta.StatusCode);
    }
}
