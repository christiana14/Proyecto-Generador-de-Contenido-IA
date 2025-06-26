import stripe
from typing import Dict, Any, Optional
from app.core.config import settings
from app.models.user import User, UserRole
import logging

logger = logging.getLogger(__name__)

stripe.api_key = settings.stripe_secret_key

class StripeService:
    def __init__(self):
        self.pro_plan_price = settings.pro_plan_price
        self.enterprise_plan_price = settings.enterprise_plan_price
    
    def create_customer(self, user: User) -> str:
        """
        Crear cliente en Stripe
        """
        try:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.full_name or user.username,
                metadata={
                    "user_id": user.id,
                    "username": user.username
                }
            )
            return customer.id
        except Exception as e:
            logger.error(f"Error creando cliente en Stripe: {str(e)}")
            raise Exception(f"Error creando cliente: {str(e)}")
    
    def create_subscription(self, user: User, plan: str) -> Dict[str, Any]:
        """
        Crear suscripción en Stripe
        """
        try:
            # Obtener price ID según el plan
            price_id = self._get_price_id(plan)
            
            # Crear suscripción
            subscription = stripe.Subscription.create(
                customer=user.stripe_customer_id,
                items=[{"price": price_id}],
                payment_behavior="default_incomplete",
                payment_settings={"save_default_payment_method": "on_subscription"},
                expand=["latest_invoice.payment_intent"],
                metadata={
                    "user_id": user.id,
                    "plan": plan
                }
            )
            
            return {
                "subscription_id": subscription.id,
                "client_secret": subscription.latest_invoice.payment_intent.client_secret,
                "status": subscription.status
            }
            
        except Exception as e:
            logger.error(f"Error creando suscripción: {str(e)}")
            raise Exception(f"Error creando suscripción: {str(e)}")
    
    def cancel_subscription(self, subscription_id: str) -> bool:
        """
        Cancelar suscripción
        """
        try:
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
            return True
        except Exception as e:
            logger.error(f"Error cancelando suscripción: {str(e)}")
            return False
    
    def get_subscription(self, subscription_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtener información de suscripción
        """
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            return {
                "id": subscription.id,
                "status": subscription.status,
                "current_period_end": subscription.current_period_end,
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "plan": subscription.items.data[0].price.lookup_key if subscription.items.data else None
            }
        except Exception as e:
            logger.error(f"Error obteniendo suscripción: {str(e)}")
            return None
    
    def create_checkout_session(self, user: User, plan: str, success_url: str, cancel_url: str) -> str:
        """
        Crear sesión de checkout
        """
        try:
            price_id = self._get_price_id(plan)
            
            session = stripe.checkout.Session.create(
                customer=user.stripe_customer_id,
                payment_method_types=["card"],
                line_items=[{"price": price_id, "quantity": 1}],
                mode="subscription",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    "user_id": user.id,
                    "plan": plan
                }
            )
            
            return session.url
            
        except Exception as e:
            logger.error(f"Error creando checkout session: {str(e)}")
            raise Exception(f"Error creando checkout: {str(e)}")
    
    def handle_webhook(self, payload: bytes, sig_header: str) -> Dict[str, Any]:
        """
        Manejar webhooks de Stripe
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.stripe_webhook_secret
            )
            
            # Manejar diferentes tipos de eventos
            if event["type"] == "customer.subscription.created":
                return self._handle_subscription_created(event["data"]["object"])
            elif event["type"] == "customer.subscription.updated":
                return self._handle_subscription_updated(event["data"]["object"])
            elif event["type"] == "customer.subscription.deleted":
                return self._handle_subscription_deleted(event["data"]["object"])
            elif event["type"] == "invoice.payment_succeeded":
                return self._handle_payment_succeeded(event["data"]["object"])
            elif event["type"] == "invoice.payment_failed":
                return self._handle_payment_failed(event["data"]["object"])
            
            return {"status": "ignored", "event_type": event["type"]}
            
        except Exception as e:
            logger.error(f"Error procesando webhook: {str(e)}")
            raise Exception(f"Error en webhook: {str(e)}")
    
    def _get_price_id(self, plan: str) -> str:
        """
        Obtener price ID según el plan
        """
        # En producción, estos IDs vendrían de la base de datos o configuración
        price_ids = {
            "pro": "price_pro_plan_id",  # Reemplazar con ID real
            "enterprise": "price_enterprise_plan_id"  # Reemplazar con ID real
        }
        
        if plan not in price_ids:
            raise ValueError(f"Plan no válido: {plan}")
        
        return price_ids[plan]
    
    def _handle_subscription_created(self, subscription: Dict[str, Any]) -> Dict[str, Any]:
        """Manejar suscripción creada"""
        return {
            "status": "subscription_created",
            "subscription_id": subscription["id"],
            "customer_id": subscription["customer"]
        }
    
    def _handle_subscription_updated(self, subscription: Dict[str, Any]) -> Dict[str, Any]:
        """Manejar suscripción actualizada"""
        return {
            "status": "subscription_updated",
            "subscription_id": subscription["id"],
            "status": subscription["status"]
        }
    
    def _handle_subscription_deleted(self, subscription: Dict[str, Any]) -> Dict[str, Any]:
        """Manejar suscripción eliminada"""
        return {
            "status": "subscription_deleted",
            "subscription_id": subscription["id"]
        }
    
    def _handle_payment_succeeded(self, invoice: Dict[str, Any]) -> Dict[str, Any]:
        """Manejar pago exitoso"""
        return {
            "status": "payment_succeeded",
            "invoice_id": invoice["id"],
            "subscription_id": invoice["subscription"]
        }
    
    def _handle_payment_failed(self, invoice: Dict[str, Any]) -> Dict[str, Any]:
        """Manejar pago fallido"""
        return {
            "status": "payment_failed",
            "invoice_id": invoice["id"],
            "subscription_id": invoice["subscription"]
        } 