import openai
import time
from typing import Dict, Any, Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        openai.api_key = settings.openai_api_key
        self.model = settings.openai_model
        self.max_tokens = settings.openai_max_tokens
    
    def generate_content(self, content_type: str, topic: str, tone: str, 
                        length: str, additional_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Generar contenido usando OpenAI
        """
        start_time = time.time()
        
        # Construir prompt según el tipo de contenido
        prompt = self._build_prompt(content_type, topic, tone, length, additional_prompt)
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt(content_type)},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.7,
                top_p=0.9,
                frequency_penalty=0.1,
                presence_penalty=0.1
            )
            
            processing_time = int((time.time() - start_time) * 1000)  # en milisegundos
            
            return {
                "content": response.choices[0].message.content.strip(),
                "tokens_used": response.usage.total_tokens,
                "processing_time": processing_time,
                "model_used": self.model
            }
            
        except Exception as e:
            logger.error(f"Error generando contenido: {str(e)}")
            raise Exception(f"Error al generar contenido: {str(e)}")
    
    def _build_prompt(self, content_type: str, topic: str, tone: str, 
                     length: str, additional_prompt: Optional[str] = None) -> str:
        """
        Construir prompt específico según el tipo de contenido
        """
        base_prompt = f"Genera contenido sobre: {topic}\n"
        base_prompt += f"Tono: {tone}\n"
        base_prompt += f"Longitud: {length}\n"
        
        if additional_prompt:
            base_prompt += f"Instrucciones adicionales: {additional_prompt}\n"
        
        # Agregar instrucciones específicas según el tipo
        if content_type == "post_social":
            base_prompt += "Crea un post atractivo para redes sociales con hashtags relevantes."
        elif content_type == "email":
            base_prompt += "Escribe un email profesional y persuasivo."
        elif content_type == "description":
            base_prompt += "Crea una descripción detallada y atractiva."
        elif content_type == "title":
            base_prompt += "Genera títulos llamativos y optimizados para SEO."
        elif content_type == "blog_post":
            base_prompt += "Escribe un artículo de blog completo y bien estructurado."
        else:
            base_prompt += "Genera contenido creativo y de calidad."
        
        return base_prompt
    
    def _get_system_prompt(self, content_type: str) -> str:
        """
        Obtener prompt del sistema según el tipo de contenido
        """
        system_prompts = {
            "post_social": """Eres un experto en marketing digital y redes sociales. 
            Crea contenido viral, atractivo y que genere engagement. 
            Incluye hashtags relevantes y emojis apropiados.""",
            
            "email": """Eres un copywriter experto en email marketing. 
            Crea emails persuasivos, profesionales y que generen conversiones. 
            Usa técnicas de copywriting probadas.""",
            
            "description": """Eres un experto en descripciones de productos y servicios. 
            Crea descripciones atractivas, detalladas y que conviertan. 
            Enfócate en beneficios y características clave.""",
            
            "title": """Eres un experto en SEO y copywriting. 
            Crea títulos llamativos, optimizados para SEO y que generen clicks. 
            Usa palabras de poder y técnicas de persuasión.""",
            
            "blog_post": """Eres un blogger experto y escritor profesional. 
            Crea artículos informativos, bien estructurados y que aporten valor. 
            Usa un lenguaje claro y accesible."""
        }
        
        return system_prompts.get(content_type, 
            "Eres un asistente de IA experto en crear contenido de alta calidad.")
    
    def test_connection(self) -> bool:
        """
        Probar conexión con OpenAI
        """
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hola"}],
                max_tokens=10
            )
            return True
        except Exception as e:
            logger.error(f"Error conectando con OpenAI: {str(e)}")
            return False 