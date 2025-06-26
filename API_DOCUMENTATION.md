# 📚 Documentación de la API - Generador de Contenido IA

## 🌐 Base URL
```
http://localhost:8000/api/v1
```

## 🔐 Autenticación

La API utiliza autenticación JWT Bearer Token. Incluye el token en el header de todas las peticiones:

```
Authorization: Bearer <tu-token-jwt>
```

## 📋 Endpoints

### 🔑 Autenticación

#### POST /auth/register
Registrar un nuevo usuario.

**Request Body:**
```json
{
  "email": "usuario@ejemplo.com",
  "username": "usuario123",
  "password": "contraseña123",
  "full_name": "Nombre Completo"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "usuario@ejemplo.com",
    "username": "usuario123",
    "full_name": "Nombre Completo",
    "role": "free"
  }
}
```

#### POST /auth/login
Iniciar sesión.

**Request Body (Form Data):**
```
username: usuario@ejemplo.com
password: contraseña123
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "usuario@ejemplo.com",
    "username": "usuario123",
    "full_name": "Nombre Completo",
    "role": "free"
  }
}
```

#### GET /auth/me
Obtener información del usuario actual.

**Response:**
```json
{
  "id": 1,
  "email": "usuario@ejemplo.com",
  "username": "usuario123",
  "full_name": "Nombre Completo",
  "is_active": true,
  "role": "free",
  "monthly_generations_used": 5,
  "monthly_generations_limit": 10
}
```

### 🤖 Generación de Contenido

#### POST /generate
Generar contenido usando IA.

**Request Body:**
```json
{
  "content_type": "post_social",
  "topic": "Inteligencia Artificial en el Marketing",
  "tone": "profesional",
  "length": "media",
  "additional_prompt": "Incluye estadísticas recientes"
}
```

**Tipos de contenido disponibles:**
- `post_social` - Posts para redes sociales
- `email` - Emails de marketing
- `description` - Descripciones de productos
- `title` - Títulos SEO
- `blog_post` - Artículos de blog

**Tonos disponibles:**
- `profesional`
- `casual`
- `amigable`
- `formal`
- `creativo`
- `persuasivo`

**Longitudes disponibles:**
- `corta`
- `media`
- `larga`

**Response:**
```json
{
  "id": 1,
  "content_type": "post_social",
  "topic": "Inteligencia Artificial en el Marketing",
  "tone": "profesional",
  "length": "media",
  "generated_content": "🚀 La IA está revolucionando el marketing digital...",
  "tokens_used": 150,
  "processing_time": 2500,
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### GET /generations
Obtener historial de generaciones del usuario.

**Query Parameters:**
- `skip` (int, opcional): Número de registros a saltar (default: 0)
- `limit` (int, opcional): Número máximo de registros (default: 10)

**Response:**
```json
[
  {
    "id": 1,
    "content_type": "post_social",
    "topic": "Inteligencia Artificial en el Marketing",
    "tone": "profesional",
    "length": "media",
    "generated_content": "🚀 La IA está revolucionando...",
    "tokens_used": 150,
    "processing_time": 2500,
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

#### GET /generations/{generation_id}
Obtener una generación específica.

**Response:**
```json
{
  "id": 1,
  "content_type": "post_social",
  "topic": "Inteligencia Artificial en el Marketing",
  "tone": "profesional",
  "length": "media",
  "generated_content": "🚀 La IA está revolucionando...",
  "tokens_used": 150,
  "processing_time": 2500,
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### DELETE /generations/{generation_id}
Eliminar una generación.

**Response:**
```json
{
  "message": "Generación eliminada exitosamente"
}
```

#### GET /usage
Obtener estadísticas de uso del usuario.

**Response:**
```json
{
  "monthly_generations_used": 5,
  "monthly_generations_limit": 10,
  "remaining_generations": 5,
  "plan": "free"
}
```

### 💰 Planes y Precios

#### GET /plans
Obtener información de planes disponibles.

**Response:**
```json
{
  "plans": [
    {
      "id": "free",
      "name": "Plan Gratuito",
      "price": 0,
      "monthly_generations": 10,
      "features": [
        "10 generaciones por mes",
        "Contenido básico",
        "Soporte por email"
      ]
    },
    {
      "id": "pro",
      "name": "Plan Pro",
      "price": 29,
      "monthly_generations": 1000,
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
      "price": 99,
      "monthly_generations": 999999,
      "features": [
        "Generaciones ilimitadas",
        "Prioridad en cola",
        "Soporte dedicado",
        "White-label disponible",
        "Integración personalizada"
      ]
    }
  ]
}
```

## 📊 Códigos de Estado HTTP

- `200` - OK - Petición exitosa
- `201` - Created - Recurso creado exitosamente
- `400` - Bad Request - Datos de entrada inválidos
- `401` - Unauthorized - Token inválido o faltante
- `402` - Payment Required - Límite de uso alcanzado
- `404` - Not Found - Recurso no encontrado
- `500` - Internal Server Error - Error interno del servidor

## 🔧 Ejemplos de Uso

### Ejemplo con cURL

#### Registrar usuario:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@ejemplo.com",
    "username": "usuario123",
    "password": "contraseña123",
    "full_name": "Nombre Completo"
  }'
```

#### Generar contenido:
```bash
curl -X POST "http://localhost:8000/api/v1/generate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer tu-token-jwt" \
  -d '{
    "content_type": "post_social",
    "topic": "Inteligencia Artificial",
    "tone": "profesional",
    "length": "media"
  }'
```

### Ejemplo con JavaScript

```javascript
// Registrar usuario
const registerUser = async () => {
  const response = await fetch('http://localhost:8000/api/v1/auth/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      email: 'usuario@ejemplo.com',
      username: 'usuario123',
      password: 'contraseña123',
      full_name: 'Nombre Completo'
    })
  });
  
  const data = await response.json();
  localStorage.setItem('token', data.access_token);
};

// Generar contenido
const generateContent = async () => {
  const token = localStorage.getItem('token');
  
  const response = await fetch('http://localhost:8000/api/v1/generate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      content_type: 'post_social',
      topic: 'Inteligencia Artificial',
      tone: 'profesional',
      length: 'media'
    })
  });
  
  const data = await response.json();
  console.log('Contenido generado:', data.generated_content);
};
```

### Ejemplo con Python

```python
import requests

# Configurar base URL
BASE_URL = "http://localhost:8000/api/v1"

# Registrar usuario
def register_user():
    response = requests.post(f"{BASE_URL}/auth/register", json={
        "email": "usuario@ejemplo.com",
        "username": "usuario123",
        "password": "contraseña123",
        "full_name": "Nombre Completo"
    })
    return response.json()

# Generar contenido
def generate_content(token):
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(f"{BASE_URL}/generate", 
                           headers=headers,
                           json={
                               "content_type": "post_social",
                               "topic": "Inteligencia Artificial",
                               "tone": "profesional",
                               "length": "media"
                           })
    return response.json()

# Uso
user_data = register_user()
token = user_data["access_token"]
content = generate_content(token)
print(content["generated_content"])
```

## 🚀 Integración con Stripe

Para habilitar pagos, configura las siguientes variables de entorno:

```env
STRIPE_SECRET_KEY=sk_test_tu-stripe-secret-key
STRIPE_PUBLISHABLE_KEY=pk_test_tu-stripe-publishable-key
STRIPE_WEBHOOK_SECRET=whsec_tu-webhook-secret
```

## 📈 Límites y Restricciones

### Plan Gratuito:
- 10 generaciones por mes
- Solo tipos básicos de contenido
- Sin acceso a API

### Plan Pro ($29/mes):
- 1000 generaciones por mes
- Todos los tipos de contenido
- Acceso completo a API
- Analytics avanzados

### Plan Enterprise ($99/mes):
- Generaciones ilimitadas
- Prioridad en cola de procesamiento
- Soporte dedicado
- White-label disponible

## 🔒 Seguridad

- Todas las contraseñas se hashean con bcrypt
- Los tokens JWT expiran en 30 minutos por defecto
- Las peticiones a la API requieren autenticación
- Los datos se validan en el servidor
- CORS configurado para seguridad

## 📞 Soporte

Para soporte técnico:
- 📧 Email: soporte@tuempresa.com
- 📖 Documentación: http://localhost:8000/docs
- 🐛 Issues: GitHub Issues 