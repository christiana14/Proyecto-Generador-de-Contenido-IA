from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from app.core.database import get_db
from app.services.openai_service import OpenAIService
from app.models.user import User
from app.models.generation import Generation
from app.core.auth import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class GenerationRequest(BaseModel):
    content_type: str
    topic: str
    tone: str
    length: str
    additional_prompt: Optional[str] = None

class GenerationResponse(BaseModel):
    id: int
    content_type: str
    topic: str
    tone: str
    length: str
    generated_content: str
    tokens_used: Optional[int]
    processing_time: Optional[int]
    created_at: str

@router.post("/generate", response_model=GenerationResponse)
async def generate_content(
    request: GenerationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generar contenido usando IA
    """
    # Verificar límites del usuario
    if not current_user.can_generate():
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Has alcanzado tu límite mensual de generaciones. Actualiza tu plan para continuar."
        )
    
    # Validar tipo de contenido
    valid_types = ["post_social", "email", "description", "title", "blog_post"]
    if request.content_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de contenido no válido. Opciones: {', '.join(valid_types)}"
        )
    
    # Validar tono
    valid_tones = ["profesional", "casual", "amigable", "formal", "creativo", "persuasivo"]
    if request.tone not in valid_tones:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tono no válido. Opciones: {', '.join(valid_tones)}"
        )
    
    # Validar longitud
    valid_lengths = ["corta", "media", "larga"]
    if request.length not in valid_lengths:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Longitud no válida. Opciones: {', '.join(valid_lengths)}"
        )
    
    try:
        # Generar contenido
        openai_service = OpenAIService()
        result = openai_service.generate_content(
            content_type=request.content_type,
            topic=request.topic,
            tone=request.tone,
            length=request.length,
            additional_prompt=request.additional_prompt
        )
        
        # Guardar en base de datos
        generation = Generation(
            user_id=current_user.id,
            content_type=request.content_type,
            topic=request.topic,
            tone=request.tone,
            length=request.length,
            additional_prompt=request.additional_prompt,
            generated_content=result["content"],
            tokens_used=result["tokens_used"],
            processing_time=result["processing_time"],
            model_used=result["model_used"]
        )
        
        db.add(generation)
        
        # Incrementar contador de uso del usuario
        current_user.increment_usage()
        
        db.commit()
        db.refresh(generation)
        
        logger.info(f"Contenido generado para usuario {current_user.id}: {generation.id}")
        
        return GenerationResponse(
            id=generation.id,
            content_type=generation.content_type,
            topic=generation.topic,
            tone=generation.tone,
            length=generation.length,
            generated_content=generation.generated_content,
            tokens_used=generation.tokens_used,
            processing_time=generation.processing_time,
            created_at=generation.created_at.isoformat() if generation.created_at else None
        )
        
    except Exception as e:
        logger.error(f"Error generando contenido: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor al generar contenido"
        )

@router.get("/generations", response_model=list[GenerationResponse])
async def get_user_generations(
    skip: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener historial de generaciones del usuario
    """
    generations = db.query(Generation).filter(
        Generation.user_id == current_user.id
    ).order_by(
        Generation.created_at.desc()
    ).offset(skip).limit(limit).all()
    
    return [
        GenerationResponse(
            id=g.id,
            content_type=g.content_type,
            topic=g.topic,
            tone=g.tone,
            length=g.length,
            generated_content=g.generated_content,
            tokens_used=g.tokens_used,
            processing_time=g.processing_time,
            created_at=g.created_at.isoformat() if g.created_at else None
        )
        for g in generations
    ]

@router.get("/generations/{generation_id}", response_model=GenerationResponse)
async def get_generation(
    generation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener una generación específica
    """
    generation = db.query(Generation).filter(
        Generation.id == generation_id,
        Generation.user_id == current_user.id
    ).first()
    
    if not generation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generación no encontrada"
        )
    
    return GenerationResponse(
        id=generation.id,
        content_type=generation.content_type,
        topic=generation.topic,
        tone=generation.tone,
        length=generation.length,
        generated_content=generation.generated_content,
        tokens_used=generation.tokens_used,
        processing_time=generation.processing_time,
        created_at=generation.created_at.isoformat() if generation.created_at else None
    )

@router.delete("/generations/{generation_id}")
async def delete_generation(
    generation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Eliminar una generación
    """
    generation = db.query(Generation).filter(
        Generation.id == generation_id,
        Generation.user_id == current_user.id
    ).first()
    
    if not generation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Generación no encontrada"
        )
    
    db.delete(generation)
    db.commit()
    
    return {"message": "Generación eliminada exitosamente"}

@router.get("/usage")
async def get_usage_stats(
    current_user: User = Depends(get_current_user)
):
    """
    Obtener estadísticas de uso del usuario
    """
    return {
        "monthly_generations_used": current_user.monthly_generations_used,
        "monthly_generations_limit": current_user.monthly_generations_limit,
        "remaining_generations": current_user.monthly_generations_limit - current_user.monthly_generations_used,
        "plan": current_user.role.value
    } 