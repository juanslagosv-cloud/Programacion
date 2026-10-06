from pydantic_settings import BaseSettings, SettingsConfigDict


def _normalizar_url(url: str) -> str:
    """Deja la cadena de conexión en el formato que espera SQLAlchemy.

    Render, Heroku y varios proveedores entregan la URL como
    ``postgres://usuario:clave@host/base``, pero SQLAlchemy 2.0 ya no
    reconoce ese esquema y falla con "Can't load plugin: sqlalchemy.dialects:postgres".
    Aquí se traduce al driver que realmente usamos (psycopg2).
    """
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg2://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://ecodes:ecodes@localhost:5432/ecodes_th"
    jwt_secret_key: str = "cambia-esta-clave-por-una-secreta-y-larga"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 480
    cors_origins: str = "http://localhost:5500,http://127.0.0.1:5500,http://localhost:8080,http://localhost:3000"
    # Permite aceptar dominios variables, como las URLs de vista previa que
    # Vercel genera en cada despliegue. Ej: https://.*\.vercel\.app
    cors_origin_regex: str = ""

    # ------------------------------------------------------------------
    # Datos de la primera empresa (Ecodes) que el seed carga al arrancar
    # con la base vacía. Después de esa primera vez, la información de las
    # empresas (Ecodes, Envsol, o las que hagan falta) se administra desde
    # la propia aplicación — pantalla Empleados > Empresas — y ya NO se lee
    # de aquí: el sistema atiende a más de una empresa a la vez, así que no
    # puede haber un solo NIT fijo en la configuración.
    # Se conservan estas variables solo por continuidad con instalaciones
    # que ya las tenían configuradas (por ejemplo, en Render).
    # ------------------------------------------------------------------
    empresa_nombre: str = "ECODES INGENIERÍA S.A.S."
    empresa_nit: str = "[NIT POR CONFIGURAR]"
    empresa_ciudad: str = "Bogotá D.C."
    empresa_direccion: str = ""
    empresa_telefono: str = ""
    empresa_correo: str = ""
    firmante_nombre: str = "[NOMBRE DE QUIEN FIRMA]"
    firmante_cargo: str = "Directora de Talento Humano"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def sqlalchemy_url(self) -> str:
        return _normalizar_url(self.database_url)

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
