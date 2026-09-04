# Imagen de despliegue del backend en modo Mock/Access-sobre-Linux-no-soportado
# (sección 61: Access solo funciona en Windows). Este contenedor sirve para
# desplegar la API con DataProvider=Mock — útil para que el equipo la pruebe
# en una URL pública real sin instalar nada localmente. El despliegue contra
# Microsoft Access real sigue requiriendo un host Windows (ver docs, sección 4).
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src

COPY CuentasPorPagar.sln .
COPY src/CuentasPorPagar.Domain/CuentasPorPagar.Domain.csproj src/CuentasPorPagar.Domain/
COPY src/CuentasPorPagar.Application/CuentasPorPagar.Application.csproj src/CuentasPorPagar.Application/
COPY src/CuentasPorPagar.Infrastructure.Access/CuentasPorPagar.Infrastructure.Access.csproj src/CuentasPorPagar.Infrastructure.Access/
COPY src/CuentasPorPagar.Infrastructure.Mock/CuentasPorPagar.Infrastructure.Mock.csproj src/CuentasPorPagar.Infrastructure.Mock/
COPY src/CuentasPorPagar.Infrastructure.Google/CuentasPorPagar.Infrastructure.Google.csproj src/CuentasPorPagar.Infrastructure.Google/
COPY src/CuentasPorPagar.Api/CuentasPorPagar.Api.csproj src/CuentasPorPagar.Api/
RUN dotnet restore src/CuentasPorPagar.Api/CuentasPorPagar.Api.csproj

COPY src/ src/
RUN dotnet publish src/CuentasPorPagar.Api/CuentasPorPagar.Api.csproj -c Release -o /app --no-restore

FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
COPY --from=build /app .

ENV ASPNETCORE_ENVIRONMENT=Production
ENV DataProvider=Mock
ENV IntegrationMode=mock

# Render/Railway/Fly.io inyectan el puerto real en $PORT; Kestrel debe escuchar
# ahí (forma shell del CMD para que la variable se expanda en tiempo de arranque).
CMD ASPNETCORE_URLS=http://+:${PORT:-8080} dotnet CuentasPorPagar.Api.dll
