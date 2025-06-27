from decouple import config
from typing import List, Optional
import os

class Settings:
    # Configuración básica
    app_name: str = config("APP_NAME", default="Generador de Contenido IA")
    debug: bool = config("DEBUG", default=True, cast=bool)
    secret_key: str = config("SECRET_KEY", default="tu-secret-key-super-segura-aqui")
    allowed_hosts: List[str] = config("ALLOWED_HOSTS", default="localhost,127.0.0.1").split(",")
    
    # Base de datos
    database_url: str = config("DATABASE_URL", default="postgresql://usuario:password@localhost/generador_contenido")
    database_test_url: str = config("DATABASE_TEST_URL", default="postgresql://usuario:password@localhost/generador_contenido_test")
    
    # Redis
    redis_url: str = config("REDIS_URL", default="redis://localhost:6379/0")
    
    # OpenAI
    openai_api_key: str = config("OPENAI_API_KEY", default="tu-openai-api-key-aqui")
    openai_model: str = config("OPENAI_MODEL", default="gpt-3.5-turbo")
    openai_max_tokens: int = config("OPENAI_MAX_TOKENS", default=1000, cast=int)
    
    # Wompi (El Salvador)
    wompi_app_id: str = config("WOMPI_APP_ID", default="prueba-app-id")
    wompi_api_secret: str = config("WOMPI_API_SECRET", default="prueba-api-secret")
    wompi_env: str = config("WOMPI_ENV", default="staging")
    
    # Email
    smtp_host: Optional[str] = config("SMTP_HOST", default=None)
    smtp_port: int = config("SMTP_PORT", default=587, cast=int)
    smtp_user: Optional[str] = config("SMTP_USER", default=None)
    smtp_password: Optional[str] = config("SMTP_PASSWORD", default=None)
    
    # Planes y límites
    free_plan_limit: int = config("FREE_PLAN_LIMIT", default=10, cast=int)
    pro_plan_limit: int = config("PRO_PLAN_LIMIT", default=1000, cast=int)
    enterprise_plan_limit: int = config("ENTERPRISE_PLAN_LIMIT", default=999999, cast=int)
    
    # Precios (en centavos)
    pro_plan_price: int = config("PRO_PLAN_PRICE", default=2900, cast=int)
    enterprise_plan_price: int = config("ENTERPRISE_PLAN_PRICE", default=9900, cast=int)
    
    # JWT
    jwt_secret_key: str = config("JWT_SECRET_KEY", default="tu-jwt-secret-key-aqui")
    jwt_algorithm: str = config("JWT_ALGORITHM", default="HS256")
    access_token_expire_minutes: int = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30, cast=int)
    
    # CORS
    cors_origins: List[str] = config("CORS_ORIGINS", default="http://localhost:3000,http://localhost:8000").split(",")
    
    # Logs
    log_level: str = config("LOG_LEVEL", default="INFO")
    log_file: str = config("LOG_FILE", default="logs/app.log")

settings = Settings() 