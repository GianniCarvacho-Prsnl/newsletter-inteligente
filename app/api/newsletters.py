from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, status
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from app.scripts.generate_newsletter import generate_and_send_newsletter
from app.db.database import get_user_by_id
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Crear router
router = APIRouter()

# Modelos Pydantic
class GenerateNewsletterRequest(BaseModel):
    user_id: str = Field(..., description="ID del usuario")
    channel: str = Field("email", description="Canal de envío (email, whatsapp, telegram)")
    language: str = Field("es", description="Idioma de las noticias")

class NewsletterResponse(BaseModel):
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None

@router.post("/generate", response_model=NewsletterResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_newsletter(
    request: GenerateNewsletterRequest,
    background_tasks: BackgroundTasks
):
    """
    Endpoint para generar y enviar un newsletter a un usuario específico.
    
    Esta tarea se ejecuta en segundo plano para no bloquear la respuesta.
    """
    # Verificar que el usuario existe
    user = await get_user_by_id(request.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario no encontrado: {request.user_id}"
        )
    
    # Programar la tarea en segundo plano
    background_tasks.add_task(
        process_newsletter_generation,
        request.user_id,
        request.channel,
        request.language
    )
    
    return {
        "success": True,
        "message": f"Generación de newsletter iniciada para el usuario {request.user_id}",
        "details": {
            "user_id": request.user_id,
            "channel": request.channel,
            "language": request.language,
            "status": "processing"
        }
    }

@router.post("/generate/mock", response_model=NewsletterResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_mock_newsletter(
    request: GenerateNewsletterRequest,
    background_tasks: BackgroundTasks
):
    """
    Endpoint para generar y enviar un newsletter usando datos mock.
    Útil para pruebas y desarrollo.
    """
    # Programar la tarea en segundo plano
    background_tasks.add_task(
        process_newsletter_generation,
        request.user_id,
        request.channel,
        request.language,
        True  # mock_data = True
    )
    
    return {
        "success": True,
        "message": f"Generación de newsletter mock iniciada para el usuario {request.user_id}",
        "details": {
            "user_id": request.user_id,
            "channel": request.channel,
            "language": request.language,
            "status": "processing",
            "mock": True
        }
    }

@router.get("/status/{user_id}", response_model=NewsletterResponse)
async def get_newsletter_status(user_id: str):
    """
    Endpoint para verificar el estado de generación de newsletter de un usuario.
    
    En una implementación completa, consultaría una cola de tareas o base de datos.
    En esta versión simplificada, responde que no hay información de estado.
    """
    # Verificar que el usuario existe
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario no encontrado: {user_id}"
        )
    
    # En una implementación real, consultaría el estado en la base de datos
    return {
        "success": True,
        "message": "En esta versión simplificada no se almacena el estado de las tareas",
        "details": {
            "user_id": user_id,
            "status": "unknown"
        }
    }

# Función de procesamiento en segundo plano
async def process_newsletter_generation(
    user_id: str,
    channel: str = "email",
    language: str = "es",
    mock_data: bool = False
):
    """
    Función para procesar la generación de newsletter en segundo plano.
    
    Args:
        user_id: ID del usuario
        channel: Canal de envío
        language: Idioma de las noticias
        mock_data: Si se deben usar datos mock
    """
    try:
        result = await generate_and_send_newsletter(
            user_id=user_id,
            channel=channel,
            language=language,
            mock_data=mock_data
        )
        
        if result.get("success", False):
            logger.info(f"Newsletter generado y enviado exitosamente para {user_id}")
        else:
            logger.error(f"Error al generar newsletter para {user_id}: {result.get('message', '')}")
    
    except Exception as e:
        logger.exception(f"Error no controlado al generar newsletter para {user_id}: {str(e)}") 