from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
import logging
import os
from datetime import datetime, timedelta
from app.core.config import settings
from app.services.openai_service import OpenAIService
from app.models.user import User, UserRole
from app.models.generation import Generation
from app.core.database import engine, SessionLocal
from app.models import user, generation as generation_model, api_key

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Crear aplicación Flask
app = Flask(__name__)

# Configuración
app.config['SECRET_KEY'] = settings.secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = settings.database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = settings.jwt_secret_key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=settings.access_token_expire_minutes)

# Inicializar extensiones
db = SQLAlchemy(app)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

# Configurar CORS
CORS(app, origins=settings.cors_origins)

# Crear tablas solo si no existen (optimización)
def init_db():
    try:
        with app.app_context():
            user.Base.metadata.create_all(bind=engine)
            generation_model.Base.metadata.create_all(bind=engine)
            api_key.Base.metadata.create_all(bind=engine)
            print("✅ Base de datos inicializada")
    except Exception as e:
        print(f"⚠️ Error inicializando DB: {e}")

# Inicializar DB de forma asíncrona
init_db()

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Verificar estado de la aplicación"""
    return jsonify({
        "status": "healthy",
        "app_name": settings.app_name,
        "version": "1.0.0"
    })

@app.route('/api/v1/plans')
def get_plans():
    """Obtener información de planes disponibles"""
    return jsonify({
        "plans": [
            {
                "id": "free",
                "name": "Plan Gratuito",
                "price": 0,
                "monthly_generations": settings.free_plan_limit,
                "features": [
                    "10 generaciones por mes",
                    "Contenido básico",
                    "Soporte por email"
                ]
            },
            {
                "id": "pro",
                "name": "Plan Pro",
                "price": settings.pro_plan_price / 100,
                "monthly_generations": settings.pro_plan_limit,
                "features": [
                    "1000 generaciones por mes",
                    "Todos los tipos de contenido",
                    "API access",
                    "Analytics avanzados",
                    "Soporte prioritario"
                ]
            },
            {
                "id": "enterprise",
                "name": "Plan Enterprise",
                "price": settings.enterprise_plan_price / 100,
                "monthly_generations": settings.enterprise_plan_limit,
                "features": [
                    "Generaciones ilimitadas",
                    "Prioridad en cola",
                    "Soporte dedicado",
                    "White-label disponible",
                    "Integración personalizada"
                ]
            }
        ]
    })

@app.route('/api/v1/auth/register', methods=['POST'])
def register():
    """Registrar nuevo usuario"""
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        if not all(key in data for key in ['email', 'username', 'password']):
            return jsonify({"error": "Faltan campos requeridos"}), 400
        
        # Validar email
        import re
        if not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
            return jsonify({"error": "Email inválido"}), 400
        
        db_session = SessionLocal()
        
        # Verificar si el email ya existe
        existing_user = db_session.query(User).filter(User.email == data['email']).first()
        if existing_user:
            return jsonify({"error": "El email ya está registrado"}), 400
        
        # Verificar si el username ya existe
        existing_username = db_session.query(User).filter(User.username == data['username']).first()
        if existing_username:
            return jsonify({"error": "El nombre de usuario ya está en uso"}), 400
        
        # Crear usuario
        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        user = User(
            email=data['email'],
            username=data['username'],
            hashed_password=hashed_password,
            full_name=data.get('full_name'),
            role=UserRole.FREE
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Generar token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "role": user.role.value
            }
        }), 201
        
    except Exception as e:
        logging.error(f"Error registrando usuario: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500
    finally:
        db_session.close()

@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    """Iniciar sesión"""
    try:
        data = request.get_json()
        
        if not all(key in data for key in ['email', 'password']):
            return jsonify({"error": "Email y contraseña son requeridos"}), 400
        
        db_session = SessionLocal()
        user = db_session.query(User).filter(User.email == data['email']).first()
        
        if not user or not bcrypt.check_password_hash(user.hashed_password, data['password']):
            return jsonify({"error": "Email o contraseña incorrectos"}), 401
        
        if not user.is_active:
            return jsonify({"error": "Usuario inactivo"}), 400
        
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "role": user.role.value
            }
        })
        
    except Exception as e:
        logging.error(f"Error en login: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500
    finally:
        db_session.close()

@app.route('/api/v1/auth/me')
@jwt_required()
def get_current_user_info():
    """Obtener información del usuario actual"""
    try:
        user_id = get_jwt_identity()
        db_session = SessionLocal()
        user = db_session.query(User).filter(User.id == user_id).first()
        
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        return jsonify({
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "role": user.role.value,
            "monthly_generations_used": user.monthly_generations_used,
            "monthly_generations_limit": user.monthly_generations_limit
        })
        
    except Exception as e:
        logging.error(f"Error obteniendo usuario: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500
    finally:
        db_session.close()

@app.route('/api/v1/generate', methods=['POST'])
@jwt_required()
def generate_content():
    """Generar contenido usando IA"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        db_session = SessionLocal()
        user = db_session.query(User).filter(User.id == user_id).first()
        
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
        
        # Verificar límites del usuario
        if not user.can_generate():
            return jsonify({
                "error": "Has alcanzado tu límite mensual de generaciones. Actualiza tu plan para continuar."
            }), 402
        
        # Validar datos requeridos
        required_fields = ['content_type', 'topic', 'tone', 'length']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Faltan campos requeridos"}), 400
        
        # Validar tipo de contenido
        valid_types = ["post_social", "email", "description", "title", "blog_post"]
        if data['content_type'] not in valid_types:
            return jsonify({"error": f"Tipo de contenido no válido. Opciones: {', '.join(valid_types)}"}), 400
        
        # Validar tono
        valid_tones = ["profesional", "casual", "amigable", "formal", "creativo", "persuasivo"]
        if data['tone'] not in valid_tones:
            return jsonify({"error": f"Tono no válido. Opciones: {', '.join(valid_tones)}"}), 400
        
        # Validar longitud
        valid_lengths = ["corta", "media", "larga"]
        if data['length'] not in valid_lengths:
            return jsonify({"error": f"Longitud no válida. Opciones: {', '.join(valid_lengths)}"}), 400
        
        # Generar contenido
        openai_service = OpenAIService()
        result = openai_service.generate_content(
            content_type=data['content_type'],
            topic=data['topic'],
            tone=data['tone'],
            length=data['length'],
            additional_prompt=data.get('additional_prompt')
        )
        
        # Guardar en base de datos
        generation = Generation(
            user_id=user.id,
            content_type=data['content_type'],
            topic=data['topic'],
            tone=data['tone'],
            length=data['length'],
            additional_prompt=data.get('additional_prompt'),
            generated_content=result["content"],
            tokens_used=result["tokens_used"],
            processing_time=result["processing_time"],
            model_used=result["model_used"]
        )
        
        db_session.add(generation)
        
        # Incrementar contador de uso del usuario
        user.increment_usage()
        
        db_session.commit()
        db_session.refresh(generation)
        
        return jsonify({
            "id": generation.id,
            "content_type": generation.content_type,
            "topic": generation.topic,
            "tone": generation.tone,
            "length": generation.length,
            "generated_content": generation.generated_content,
            "tokens_used": generation.tokens_used,
            "processing_time": generation.processing_time,
            "created_at": generation.created_at.isoformat() if generation.created_at else None
        })
        
    except Exception as e:
        logging.error(f"Error generando contenido: {str(e)}")
        return jsonify({"error": "Error interno del servidor al generar contenido"}), 500
    finally:
        db_session.close()

@app.route('/api/v1/generations')
@jwt_required()
def get_user_generations():
    """Obtener historial de generaciones del usuario"""
    try:
        user_id = get_jwt_identity()
        skip = request.args.get('skip', 0, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        db_session = SessionLocal()
        generations = db_session.query(Generation).filter(
            Generation.user_id == user_id
        ).order_by(
            Generation.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        return jsonify([
            {
                "id": g.id,
                "content_type": g.content_type,
                "topic": g.topic,
                "tone": g.tone,
                "length": g.length,
                "generated_content": g.generated_content,
                "tokens_used": g.tokens_used,
                "processing_time": g.processing_time,
                "created_at": g.created_at.isoformat() if g.created_at else None
            }
            for g in generations
        ])
        
    except Exception as e:
        logging.error(f"Error obteniendo generaciones: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500
    finally:
        db_session.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=settings.debug) 