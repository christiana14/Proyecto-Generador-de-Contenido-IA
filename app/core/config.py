from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Configuración básica
    app_name: str = "Generador de Contenido IA"
    debug: bool = True
    secret_key: str = "tu-secret-key-super-segura-aqui"
    allowed_hosts: List[str] = ["localhost", "127.0.0.1"]
    
    # Base de datos
    database_url: str = "postgresql://usuario:password@localhost/generador_contenido"
    database_test_url: str = "postgresql://usuario:password@localhost/generador_contenido_test"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # OpenAI
    openai_api_key: str = "tu-openai-api-key-aqui"
    openai_model: str = "gpt-3.5-turbo"
    openai_max_tokens: int = 1000
    
    # Wompi (El Salvador)
    wompi_app_id: str = "prueba-app-id"
    wompi_api_secret: str = "prueba-api-secret"
    wompi_env: str = "staging"  # staging para pruebas, production para real
    
    # Email
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    
    # Planes y límites
    free_plan_limit: int = 10
    pro_plan_limit: int = 1000
    enterprise_plan_limit: int = 999999
    
    # Precios (en centavos)
    pro_plan_price: int = 2900  # $29.00
    enterprise_plan_price: int = 9900  # $99.00
    
    # JWT
    jwt_secret_key: str = "tu-jwt-secret-key-aqui"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Logs
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False
    }

settings = Settings() 