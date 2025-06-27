import httpx
import logging
from typing import Dict, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class WompiService:
    def __init__(self):
        self.base_url = "https://sandbox.wompi.co/v1" if settings.wompi_env == "staging" else "https://production.wompi.co/v1"
        self.app_id = settings.wompi_app_id
        self.api_secret = settings.wompi_api_secret
    
    async def create_payment_link(self, amount: int, description: str, user_email: str) -> Optional[Dict]:
        """
        Crear enlace de pago en Wompi
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/payment_links",
                    headers={
                        "Authorization": f"Bearer {self.api_secret}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "name": description,
                        "description": description,
                        "amount_in_cents": amount,
                        "currency": "COP",
                        "accept_partial": False,
                        "expires_at": None,
                        "collect_shipping": False,
                        "customer_email": user_email
                    }
                )
                
                if response.status_code == 201:
                    return response.json()
                else:
                    logger.error(f"Error creando enlace de pago: {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error en Wompi service: {str(e)}")
            return None
    
    async def verify_payment(self, payment_id: str) -> Optional[Dict]:
        """
        Verificar estado de un pago
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/transactions/{payment_id}",
                    headers={
                        "Authorization": f"Bearer {self.api_secret}"
                    }
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Error verificando pago: {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error verificando pago en Wompi: {str(e)}")
            return None

wompi_service = WompiService() 