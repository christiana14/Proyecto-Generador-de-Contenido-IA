# WSGI entry point para Render
from app.main import app

# Configuración para inicio rápido
app.config['PROPAGATE_EXCEPTIONS'] = True

if __name__ == "__main__":
    app.run() 