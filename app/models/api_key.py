from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import secrets

class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # API Key
    key_hash = Column(String, nullable=False, unique=True, index=True)
    key_prefix = Column(String, nullable=False)  # Primeros 8 caracteres para identificación
    
    # Metadatos
    name = Column(String, nullable=False)  # Nombre descriptivo
    is_active = Column(Boolean, default=True)
    last_used = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relaciones
    user = relationship("User", back_populates="api_keys")
    
    @staticmethod
    def generate_key() -> str:
        """Generar una nueva API key"""
        return f"gcai_{secrets.token_urlsafe(32)}"
    
    @staticmethod
    def get_key_prefix(key: str) -> str:
        """Obtener prefijo de la key para identificación"""
        return key[:8]
    
    def is_expired(self) -> bool:
        """Verificar si la key ha expirado"""
        if not self.expires_at:
            return False
        return func.now() > self.expires_at 