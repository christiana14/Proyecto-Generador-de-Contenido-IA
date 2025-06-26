from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class UserRole(str, enum.Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role = Column(Enum(UserRole), default=UserRole.FREE)
    
    # Stripe
    stripe_customer_id = Column(String, nullable=True)
    stripe_subscription_id = Column(String, nullable=True)
    
    # Límites de uso
    monthly_generations_used = Column(Integer, default=0)
    monthly_generations_limit = Column(Integer, default=10)  # Plan gratuito
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relaciones
    generations = relationship("Generation", back_populates="user")
    api_keys = relationship("APIKey", back_populates="user")
    
    def can_generate(self) -> bool:
        """Verificar si el usuario puede generar contenido"""
        return self.monthly_generations_used < self.monthly_generations_limit
    
    def increment_usage(self):
        """Incrementar contador de uso"""
        self.monthly_generations_used += 1
    
    def reset_monthly_usage(self):
        """Resetear uso mensual"""
        self.monthly_generations_used = 0 