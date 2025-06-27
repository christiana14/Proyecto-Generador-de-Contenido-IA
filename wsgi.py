# WSGI entry point para Render
from app.main import app

# Configuración para producción
app.config['PROPAGATE_EXCEPTIONS'] = True

# Asegurar que la aplicación esté disponible para gunicorn
application = app

import os

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 