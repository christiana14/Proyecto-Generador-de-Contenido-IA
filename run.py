#!/usr/bin/env python3
"""
Script principal para ejecutar el Generador de Contenido IA
"""

import uvicorn
import os
import sys
from pathlib import Path

def main():
    """Función principal"""
    print("🚀 Iniciando Generador de Contenido IA...")
    
    # Verificar si existe el archivo .env
    if not os.path.exists('.env'):
        print("⚠️  Archivo .env no encontrado. Copiando .env.example...")
        if os.path.exists('env.example'):
            import shutil
            shutil.copy('env.example', '.env')
            print("✅ Archivo .env creado. Por favor configura tus variables de entorno.")
        else:
            print("❌ Archivo env.example no encontrado.")
            return
    
    # Verificar dependencias
    try:
        import fastapi
        import openai
        import stripe
        print("✅ Dependencias verificadas")
    except ImportError as e:
        print(f"❌ Dependencia faltante: {e}")
        print("💡 Ejecuta: pip install -r requirements.txt")
        return
    
    # Configurar variables de entorno
    from dotenv import load_dotenv
    load_dotenv()
    
    # Verificar configuración crítica
    required_vars = [
        'OPENAI_API_KEY',
        'SECRET_KEY',
        'DATABASE_URL'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Variables de entorno faltantes: {', '.join(missing_vars)}")
        print("💡 Configura estas variables en el archivo .env")
        return
    
    print("✅ Configuración verificada")
    
    # Iniciar servidor
    print("🌐 Iniciando servidor en http://localhost:8000")
    print("📚 Documentación API: http://localhost:8000/docs")
    print("🔴 Para detener: Ctrl+C")
    
    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido")
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")

if __name__ == "__main__":
    main() 