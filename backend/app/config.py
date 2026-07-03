from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    secret_key: str = "cambiar_en_produccion"
    auth_username: str = "admin"
    auth_password: str = "Dashboard2026!"
    jwt_expire_hours: int = 24

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
