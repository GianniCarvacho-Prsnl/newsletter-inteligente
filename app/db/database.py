from supabase import create_client
from app.core.config import SUPABASE_URL, SUPABASE_KEY, validate_config
from fastapi import Depends, HTTPException, status
from typing import Optional, Dict, Any

# Validar la configuración crítica
validate_config()

# Cliente Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Tabla de usuarios
users_table = "users"
# Tabla de tópicos
topics_table = "topics"
# Tabla de relación usuarios-tópicos
user_topics_table = "user_topics"
# Tabla de newsletters enviados
newsletters_table = "newsletters"

async def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Obtener un usuario por su ID desde Supabase.
    
    Args:
        user_id: ID del usuario a buscar
        
    Returns:
        Diccionario con la información del usuario o None si no existe
    """
    try:
        response = supabase.table(users_table).select("*").eq("id", user_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error al obtener usuario: {e}")
        return None

async def get_user_topics(user_id: str) -> list:
    """
    Obtener los tópicos de un usuario.
    
    Args:
        user_id: ID del usuario
        
    Returns:
        Lista de tópicos del usuario
    """
    try:
        # Consulta para obtener los tópicos del usuario desde la tabla de relación
        response = supabase.table(user_topics_table) \
            .select("topic_id, topics(name, description)") \
            .eq("user_id", user_id) \
            .execute()
        
        if response.data:
            # Extraer los tópicos de la respuesta
            topics = [
                {
                    "id": item["topic_id"],
                    "name": item["topics"]["name"],
                    "description": item["topics"]["description"]
                }
                for item in response.data
            ]
            return topics
        return []
    except Exception as e:
        print(f"Error al obtener tópicos del usuario: {e}")
        return []

async def save_newsletter(
    user_id: str, 
    content: str, 
    topics: list, 
    channel: str = "email"
) -> Dict[str, Any]:
    """
    Guardar un registro de newsletter enviado.
    
    Args:
        user_id: ID del usuario
        content: Contenido del newsletter
        topics: Lista de tópicos incluidos
        channel: Canal de envío (email, whatsapp, telegram)
        
    Returns:
        Diccionario con la información del newsletter guardado
    """
    try:
        # Datos a insertar
        newsletter_data = {
            "user_id": user_id,
            "content": content,
            "topics": topics,
            "channel": channel,
            "sent_at": "now()"  # Función de PostgreSQL para fecha actual
        }
        
        # Insertar en la tabla de newsletters
        response = supabase.table(newsletters_table).insert(newsletter_data).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        return {}
    except Exception as e:
        print(f"Error al guardar newsletter: {e}")
        return {} 