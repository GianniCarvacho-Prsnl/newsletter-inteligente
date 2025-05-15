#!/usr/bin/env python3
"""
Script para generar y enviar un newsletter manualmente.

Este script orquesta la ejecución secuencial de los agentes:
1. NewsFetcherAgent - Busca noticias relevantes
2. SummarizerAgent - Resume las noticias
3. FormatterAgent - Da formato al contenido
4. SenderAgent - Envía el newsletter
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import argparse

# Asegurar que podemos importar desde app
parent_dir = Path(__file__).parents[2]
sys.path.append(str(parent_dir))

from app.agents.news_fetcher import NewsFetcherAgent
from app.agents.summarizer import SummarizerAgent
from app.agents.formatter import FormatterAgent
from app.agents.sender import SenderAgent
from app.db.database import get_user_by_id, get_user_topics, save_newsletter

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def generate_and_send_newsletter(
    user_id: str,
    channel: str = "email",
    language: str = "es",
    mock_data: bool = False
) -> Dict[str, Any]:
    """
    Generar y enviar un newsletter para un usuario específico.
    
    Args:
        user_id: ID del usuario
        channel: Canal de envío (email, whatsapp, telegram)
        language: Idioma de las noticias
        mock_data: Si se deben usar datos mock
        
    Returns:
        Diccionario con el resultado del proceso
    """
    # Inicializar los agentes
    news_fetcher = NewsFetcherAgent()
    summarizer = SummarizerAgent()
    formatter = FormatterAgent()
    sender = SenderAgent()
    
    logger.info(f"Generando newsletter para usuario {user_id}")
    
    if mock_data:
        # Usar datos mock para pruebas
        user_data = {
            "id": user_id,
            "name": "Usuario de Prueba",
            "email": "test@example.com",
            "phone": "+1234567890",
            "telegram_id": "12345678"
        }
        topics = [
            {"id": "1", "name": "Inteligencia Artificial", "description": "Avances en IA y machine learning"},
            {"id": "2", "name": "Cambio Climático", "description": "Noticias sobre el medio ambiente y cambio climático"}
        ]
    else:
        # Obtener datos reales del usuario desde Supabase
        user_data = await get_user_by_id(user_id)
        if not user_data:
            return {"success": False, "message": f"Usuario no encontrado: {user_id}"}
        
        # Obtener tópicos del usuario
        topics = await get_user_topics(user_id)
        if not topics:
            return {"success": False, "message": "El usuario no tiene tópicos configurados"}
    
    # 1. NewsFetcherAgent - Buscar noticias
    logger.info("Paso 1: Buscando noticias relevantes...")
    news_results = await news_fetcher.get_news_for_topics(topics, language)
    logger.info(f"Encontradas noticias para {len(news_results)} tópicos")
    
    # 2. SummarizerAgent - Resumir noticias
    logger.info("Paso 2: Resumiendo noticias...")
    summarized_news = await summarizer.summarize_news_by_topic(news_results)
    
    # 3. FormatterAgent - Formatear contenido
    logger.info("Paso 3: Formateando newsletter...")
    formatted_newsletter = await formatter.format_newsletter(user_data, summarized_news)
    
    # 4. SenderAgent - Enviar newsletter
    logger.info(f"Paso 4: Enviando por {channel}...")
    send_result = await sender.send_newsletter(user_data, formatted_newsletter, channel)
    
    # Guardar registro en la base de datos (solo si no es mock y el envío fue exitoso)
    if not mock_data and send_result.get("success", False):
        # Extraer tópicos para guardar
        topics_names = list(summarized_news.keys())
        
        await save_newsletter(
            user_id=user_id,
            content=formatted_newsletter.get("title", "Newsletter"),
            topics=topics_names,
            channel=channel
        )
        logger.info("Guardado registro de envío en la base de datos")
    
    return {
        "success": send_result.get("success", False),
        "message": send_result.get("message", ""),
        "user_id": user_id,
        "channel": channel,
        "topics": [t["name"] for t in topics],
        "newsletter_title": formatted_newsletter.get("title", "")
    }

async def process_all_users(mock_data: bool = False):
    """
    Procesar todos los usuarios con newsletter activo.
    En modo mock, crea un usuario de prueba.
    """
    if mock_data:
        # Usuario mock
        user_ids = ["mock_user_1"]
    else:
        # Aquí iría la lógica para obtener todos los usuarios activos
        # Por ahora, usamos un usuario de ejemplo
        user_ids = ["usuario_de_ejemplo"]
    
    for user_id in user_ids:
        try:
            result = await generate_and_send_newsletter(user_id, mock_data=mock_data)
            if result["success"]:
                logger.info(f"Éxito para usuario {user_id}: {result['message']}")
            else:
                logger.error(f"Error para usuario {user_id}: {result['message']}")
        except Exception as e:
            logger.exception(f"Error al procesar usuario {user_id}: {e}")

def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(description="Generar y enviar newsletter")
    parser.add_argument("--user-id", help="ID del usuario específico (opcional)")
    parser.add_argument("--channel", choices=["email", "whatsapp", "telegram"], 
                        default="email", help="Canal de envío")
    parser.add_argument("--language", default="es", help="Idioma de las noticias")
    parser.add_argument("--mock", action="store_true", help="Usar datos mock")
    
    args = parser.parse_args()
    
    # Ejecutar la función asíncrona
    if args.user_id:
        # Procesar un usuario específico
        asyncio.run(generate_and_send_newsletter(
            args.user_id, 
            args.channel, 
            args.language, 
            args.mock
        ))
    else:
        # Procesar todos los usuarios
        asyncio.run(process_all_users(args.mock))

if __name__ == "__main__":
    main() 