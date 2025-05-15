import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Any, List, Optional
from app.core.config import (
    EMAIL_HOST, EMAIL_PORT, 
    EMAIL_USERNAME, EMAIL_PASSWORD, 
    EMAIL_FROM
)
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SenderAgent:
    """
    Agente que envía el newsletter al usuario por el canal preferido.
    
    En la primera versión, solo se implementa el envío por correo electrónico,
    con respuestas dummy para WhatsApp y Telegram.
    """
    
    def __init__(self):
        """
        Inicializar el agente de envío.
        """
        self.channels = {
            "email": self._send_by_email,
            "whatsapp": self._send_by_whatsapp_dummy,
            "telegram": self._send_by_telegram_dummy
        }
    
    async def send_newsletter(self, user_data: Dict[str, Any], newsletter_data: Dict[str, Any], channel: str = "email") -> Dict[str, Any]:
        """
        Enviar el newsletter al usuario por el canal especificado.
        
        Args:
            user_data: Información del usuario
            newsletter_data: Datos del newsletter formateado
            channel: Canal de envío (email, whatsapp, telegram)
            
        Returns:
            Diccionario con el resultado del envío
        """
        # Verificar que el canal es válido
        if channel not in self.channels:
            logger.error(f"Canal no válido: {channel}")
            return {
                "success": False,
                "message": f"Canal no soportado: {channel}",
                "channel": channel
            }
        
        # Enviar por el canal especificado
        try:
            # Ejecutar la función correspondiente al canal
            return await self.channels[channel](user_data, newsletter_data)
        except Exception as e:
            logger.error(f"Error al enviar por {channel}: {e}")
            return {
                "success": False,
                "message": f"Error al enviar: {str(e)}",
                "channel": channel
            }
    
    async def _send_by_email(self, user_data: Dict[str, Any], newsletter_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enviar el newsletter por correo electrónico.
        
        Args:
            user_data: Información del usuario
            newsletter_data: Datos del newsletter formateado
            
        Returns:
            Diccionario con el resultado del envío
        """
        # Extraer datos
        email = user_data.get("email")
        if not email:
            return {
                "success": False,
                "message": "No se proporcionó dirección de correo electrónico",
                "channel": "email"
            }
        
        # Crear el mensaje
        msg = MIMEMultipart('alternative')
        msg['Subject'] = newsletter_data.get("subject", "Tu Newsletter Personalizado")
        msg['From'] = EMAIL_FROM
        msg['To'] = email
        
        # Adjuntar versiones HTML y texto plano
        text_content = newsletter_data.get("text", "")
        html_content = newsletter_data.get("html", "")
        
        if text_content:
            msg.attach(MIMEText(text_content, 'plain'))
        if html_content:
            msg.attach(MIMEText(html_content, 'html'))
        
        # Enviar el correo
        try:
            # Validar que hay credenciales configuradas
            if not all([EMAIL_HOST, EMAIL_PORT, EMAIL_USERNAME, EMAIL_PASSWORD]):
                logger.warning("Configuración de correo incompleta. Simulando envío en modo desarrollo.")
                
                # Modo desarrollo - simular envío
                logger.info(f"Simulando envío a: {email}")
                logger.info(f"Asunto: {msg['Subject']}")
                logger.info(f"Texto: {text_content[:100]}...")
                
                return {
                    "success": True,
                    "message": "Simulación de envío exitosa (modo desarrollo)",
                    "channel": "email",
                    "recipient": email,
                    "subject": msg['Subject']
                }
            
            # Modo producción - envío real
            server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
            server.starttls()
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Correo enviado exitosamente a {email}")
            
            return {
                "success": True,
                "message": "Newsletter enviado exitosamente",
                "channel": "email",
                "recipient": email,
                "subject": msg['Subject']
            }
        except Exception as e:
            logger.error(f"Error al enviar correo: {e}")
            raise
    
    async def _send_by_whatsapp_dummy(self, user_data: Dict[str, Any], newsletter_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implementación dummy para envío por WhatsApp.
        
        Args:
            user_data: Información del usuario
            newsletter_data: Datos del newsletter formateado
            
        Returns:
            Diccionario con el resultado simulado
        """
        # Extraer datos
        phone = user_data.get("phone")
        if not phone:
            return {
                "success": False,
                "message": "No se proporcionó número de teléfono",
                "channel": "whatsapp"
            }
        
        # Simulación de envío
        logger.info(f"[DUMMY] Simulando envío de WhatsApp a: {phone}")
        logger.info(f"[DUMMY] Contenido: {newsletter_data.get('title', 'Newsletter')}")
        
        return {
            "success": True,
            "message": "Simulación de envío por WhatsApp exitosa",
            "channel": "whatsapp",
            "recipient": phone
        }
    
    async def _send_by_telegram_dummy(self, user_data: Dict[str, Any], newsletter_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implementación dummy para envío por Telegram.
        
        Args:
            user_data: Información del usuario
            newsletter_data: Datos del newsletter formateado
            
        Returns:
            Diccionario con el resultado simulado
        """
        # Extraer datos
        telegram_id = user_data.get("telegram_id")
        if not telegram_id:
            return {
                "success": False,
                "message": "No se proporcionó ID de Telegram",
                "channel": "telegram"
            }
        
        # Simulación de envío
        logger.info(f"[DUMMY] Simulando envío de Telegram a: {telegram_id}")
        logger.info(f"[DUMMY] Contenido: {newsletter_data.get('title', 'Newsletter')}")
        
        return {
            "success": True,
            "message": "Simulación de envío por Telegram exitosa",
            "channel": "telegram",
            "recipient": telegram_id
        }

# Ejemplo de uso
"""
async def example():
    # Datos de ejemplo
    user_data = {
        "name": "Ana García",
        "email": "ana@example.com",
        "phone": "+1234567890",
        "telegram_id": "12345678"
    }
    
    newsletter_data = {
        "title": "Resumen de Noticias Tecnológicas",
        "subject": "Tu Resumen Semanal de Tecnología",
        "html": "<html><body><h1>Hola Ana</h1><p>Aquí está tu newsletter...</p></body></html>",
        "text": "Hola Ana,\n\nAquí está tu newsletter...\n\nSaludos"
    }
    
    sender = SenderAgent()
    
    # Enviar por email
    result_email = await sender.send_newsletter(user_data, newsletter_data, "email")
    print("Email result:", result_email)
    
    # Enviar por WhatsApp (dummy)
    result_whatsapp = await sender.send_newsletter(user_data, newsletter_data, "whatsapp")
    print("WhatsApp result:", result_whatsapp)

# Para ejecutar el ejemplo
import asyncio
asyncio.run(example())
""" 