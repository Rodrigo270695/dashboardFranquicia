from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    secret_key: str = "cambiar_en_produccion"
    auth_username: str = "admin"
    auth_password: str = "Dashboard2026!"
    jwt_expire_hours: int = 24
    # Orígenes CORS separados por coma (producción)
    cors_origins: str = "http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:3003"

    model_config = {"env_file": ".env", "extra": "ignore"}

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
