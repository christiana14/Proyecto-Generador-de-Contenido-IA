from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Generation(Base):
    __tablename__ = "generations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Tipo de contenido generado
    content_type = Column(String, nullable=False)  # post_social, email, description, etc.
    
    # Parámetros de entrada
    topic = Column(String, nullable=False)
    tone = Column(String, nullable=False)
    length = Column(String, nullable=False)
    additional_prompt = Column(Text, nullable=True)
    
    # Contenido generado
    generated_content = Column(Text, nullable=False)
    
    # Metadatos
    tokens_used = Column(Integer, nullable=True)
    processing_time = Column(Integer, nullable=True)  # en milisegundos
    model_used = Column(String, nullable=True)
    
    # Configuración adicional
    settings = Column(JSON, nullable=True)  # Configuración adicional
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relaciones
    user = relationship("User", back_populates="generations")
    
    def to_dict(self):
        """Convertir a diccionario para API"""
        return {
            "id": self.id,
            "content_type": self.content_type,
            "topic": self.topic,
            "tone": self.tone,
            "length": self.length,
            "generated_content": self.generated_content,
            "tokens_used": self.tokens_used,
            "processing_time": self.processing_time,
            "created_at": self.created_at.isoformat() if self.created_at else None
        } 