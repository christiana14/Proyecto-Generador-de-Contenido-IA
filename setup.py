#!/usr/bin/env python3
"""
Script de configuración inicial para el Generador de Contenido IA
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Ejecutar comando y mostrar resultado"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}: {e}")
        print(f"Error: {e.stderr}")
        return False

def create_directories():
    """Crear directorios necesarios"""
    directories = [
        "app/static",
        "app/templates",
        "logs",
        "uploads"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Directorio creado: {directory}")

def setup_database():
    """Configurar base de datos"""
    print("🗄️  Configurando base de datos...")
    
    # Crear archivo de migración inicial
    alembic_ini = """
[alembic]
script_location = alembic
sqlalchemy.url = postgresql://usuario:password@localhost/generador_contenido

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""
    
    with open("alembic.ini", "w") as f:
        f.write(alembic_ini)
    
    # Crear directorio alembic
    Path("alembic").mkdir(exist_ok=True)
    Path("alembic/versions").mkdir(exist_ok=True)
    
    # Crear env.py para alembic
    env_py = '''
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from app.core.database import Base
from app.models import user, generation, api_key

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''
    
    with open("alembic/env.py", "w") as f:
        f.write(env_py)
    
    print("✅ Configuración de base de datos completada")

def setup_environment():
    """Configurar entorno de desarrollo"""
    print("🔧 Configurando entorno de desarrollo...")
    
    # Crear .env si no existe
    if not os.path.exists('.env'):
        if os.path.exists('env.example'):
            shutil.copy('env.example', '.env')
            print("✅ Archivo .env creado desde env.example")
        else:
            print("⚠️  Archivo env.example no encontrado")
    
    # Crear .gitignore
    gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# Environment variables
.env
.env.local
.env.production

# Database
*.db
*.sqlite3

# Logs
logs/
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Uploads
uploads/

# Temporary files
*.tmp
*.temp
"""
    
    with open(".gitignore", "w") as f:
        f.write(gitignore_content)
    
    print("✅ Archivos de configuración creados")

def main():
    """Función principal de configuración"""
    print("🚀 Configurando Generador de Contenido IA...")
    print("=" * 50)
    
    # Crear directorios
    create_directories()
    
    # Configurar entorno
    setup_environment()
    
    # Configurar base de datos
    setup_database()
    
    # Instalar dependencias
    if not run_command("pip install -r requirements.txt", "Instalando dependencias"):
        print("❌ Error instalando dependencias")
        return
    
    print("\n" + "=" * 50)
    print("✅ Configuración completada exitosamente!")
    print("\n📋 Próximos pasos:")
    print("1. Configura las variables en el archivo .env")
    print("2. Configura tu base de datos PostgreSQL")
    print("3. Obtén una API key de OpenAI")
    print("4. Configura Stripe para pagos (opcional)")
    print("5. Ejecuta: python run.py")
    print("\n🌐 La aplicación estará disponible en: http://localhost:8000")
    print("📚 Documentación API: http://localhost:8000/docs")

if __name__ == "__main__":
    main() 