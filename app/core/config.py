import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la aplicación
APP_NAME = os.getenv("APP_NAME", "Newsletter Inteligente")
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")
API_PREFIX = os.getenv("API_PREFIX", "/api/v1")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Configuración de Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Configuración de OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configuración de NewsAPI
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Configuración de Email
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_FROM = os.getenv("EMAIL_FROM")

# Validar configuración crítica
def validate_config():
    """Validar que las configuraciones críticas estén presentes."""
    missing_vars = []
    
    if not SUPABASE_URL:
        missing_vars.append("SUPABASE_URL")
    if not SUPABASE_KEY:
        missing_vars.append("SUPABASE_KEY")
    if not OPENAI_API_KEY:
        missing_vars.append("OPENAI_API_KEY")
    if not NEWS_API_KEY:
        missing_vars.append("NEWS_API_KEY")
    
    if missing_vars:
        raise ValueError(
            f"Faltan variables de entorno críticas: {', '.join(missing_vars)}. "
            "Por favor, configura estas variables en el archivo .env"
        ) 