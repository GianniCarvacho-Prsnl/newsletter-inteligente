from openai import OpenAI
from typing import Dict, Any, List
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os
from pathlib import Path
from app.core.config import OPENAI_API_KEY

# Inicializar cliente de OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Configurar Jinja2 para plantillas
templates_dir = Path(__file__).parents[2] / "templates"
env = Environment(
    loader=FileSystemLoader(templates_dir),
    autoescape=select_autoescape(['html', 'xml'])
)

class FormatterAgent:
    """
    Agente que formatea el contenido del newsletter para hacerlo atractivo y legible.
    
    Este agente utiliza OpenAI para personalizar introducciones y títulos,
    y Jinja2 para aplicar plantillas predefinidas al contenido resumido.
    """
    
    def __init__(self, template_name: str = "default_email.html"):
        """
        Inicializar el agente de formato.
        
        Args:
            template_name: Nombre de la plantilla a utilizar
        """
        self.template_name = template_name
        
        # Asegurarse de que exista la carpeta de plantillas
        os.makedirs(templates_dir, exist_ok=True)
        
        # Si no existe la plantilla, crear una predeterminada
        self._ensure_default_template_exists()
    
    async def format_newsletter(self, user_data: Dict[str, Any], summarized_news: Dict[str, Any]) -> Dict[str, Any]:
        """
        Formatear el newsletter completo para un usuario.
        
        Args:
            user_data: Información del usuario
            summarized_news: Noticias resumidas por tópico
            
        Returns:
            Diccionario con el newsletter formateado en HTML y texto plano
        """
        # Extraer datos del usuario
        user_name = user_data.get("name", "Usuario")
        user_topics = user_data.get("topics", [])
        
        # Generar un título personalizado para el newsletter
        newsletter_title = await self._generate_title(user_name, list(summarized_news.keys()))
        
        # Generar una introducción personalizada
        introduction = await self._generate_introduction(user_name, list(summarized_news.keys()))
        
        # Preparar los datos para la plantilla
        template_data = {
            "user_name": user_name,
            "newsletter_title": newsletter_title,
            "introduction": introduction,
            "topics": [],
            "date": self._get_formatted_date()
        }
        
        # Procesar cada tópico para la plantilla
        for topic, data in summarized_news.items():
            topic_data = {
                "name": topic,
                "summary": data.get("summary", ""),
                "articles": data.get("articles", [])
            }
            template_data["topics"].append(topic_data)
        
        # Renderizar el HTML usando la plantilla
        try:
            template = env.get_template(self.template_name)
            html_content = template.render(**template_data)
        except Exception as e:
            print(f"Error al renderizar la plantilla: {e}")
            # Fallback a una plantilla simple en caso de error
            html_content = self._generate_simple_html(template_data)
        
        # Generar también una versión en texto plano
        text_content = await self._generate_text_version(template_data)
        
        return {
            "html": html_content,
            "text": text_content,
            "title": newsletter_title,
            "subject": f"{newsletter_title} - {self._get_formatted_date()}"
        }
    
    async def _generate_title(self, user_name: str, topics: List[str]) -> str:
        """
        Generar un título personalizado para el newsletter.
        
        Args:
            user_name: Nombre del usuario
            topics: Lista de tópicos incluidos
            
        Returns:
            Título personalizado
        """
        topics_text = ", ".join(topics[:3])
        if len(topics) > 3:
            topics_text += " y más"
        
        prompt = f"""
        Genera un título atractivo y personal para un newsletter que va dirigido a {user_name},
        y que contiene noticias sobre los siguientes temas: {topics_text}.
        
        El título debe ser conciso (máximo 8 palabras) y captar la atención.
        No uses comillas ni signos de exclamación excesivos.
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un experto en marketing y titulares atractivos."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=30
            )
            
            title = response.choices[0].message.content.strip()
            # Eliminar comillas si las hay
            title = title.strip('"\'')
            return title
        except Exception as e:
            print(f"Error al generar título: {e}")
            return f"Tu Resumen de Noticias: {topics_text}"
    
    async def _generate_introduction(self, user_name: str, topics: List[str]) -> str:
        """
        Generar una introducción personalizada para el newsletter.
        
        Args:
            user_name: Nombre del usuario
            topics: Lista de tópicos incluidos
            
        Returns:
            Introducción personalizada
        """
        topics_text = ", ".join(topics[:3])
        if len(topics) > 3:
            topics_text += " y otros temas"
        
        prompt = f"""
        Escribe un párrafo introductorio personal y amigable para un newsletter 
        que va dirigido a {user_name}, y que contiene un resumen de noticias sobre: {topics_text}.
        
        La introducción debe ser cálida, directa y no exceder de 3 frases.
        Menciona que estas son las noticias más relevantes seleccionadas especialmente según sus intereses.
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un redactor amigable y persuasivo que conecta con los lectores."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error al generar introducción: {e}")
            return f"Hola {user_name}, aquí tienes tu resumen de noticias sobre {topics_text} para hoy."
    
    async def _generate_text_version(self, template_data: Dict[str, Any]) -> str:
        """
        Generar una versión en texto plano del newsletter.
        
        Args:
            template_data: Datos para la plantilla
            
        Returns:
            Versión en texto plano del newsletter
        """
        text = f"📰 {template_data['newsletter_title']}\n"
        text += f"📅 {template_data['date']}\n\n"
        text += f"Hola {template_data['user_name']},\n\n"
        text += f"{template_data['introduction']}\n\n"
        
        for topic in template_data["topics"]:
            text += f"🔷 {topic['name'].upper()}\n"
            text += f"{topic['summary']}\n\n"
            
            for i, article in enumerate(topic["articles"], 1):
                text += f"{i}. {article.get('title', 'Sin título')}\n"
                text += f"   {article.get('summary', 'Sin resumen')}\n"
                if "relevance" in article:
                    text += f"   Relevancia: {article['relevance']}\n"
                text += f"   Fuente: {article.get('source', 'Desconocida')} - {article.get('url', '')}\n\n"
            
            text += "\n"
        
        text += "¡Gracias por leer tu newsletter personalizado!\n"
        text += "Recibe este resumen diariamente según tus intereses.\n"
        
        return text
    
    def _get_formatted_date(self) -> str:
        """
        Obtener la fecha actual formateada.
        
        Returns:
            Fecha formateada
        """
        from datetime import datetime
        now = datetime.now()
        return now.strftime("%d de %B de %Y")
    
    def _ensure_default_template_exists(self):
        """
        Asegurarse de que existe una plantilla predeterminada.
        Si no existe, la crea.
        """
        template_path = templates_dir / self.template_name
        
        if not template_path.exists():
            # Crear una plantilla HTML básica
            default_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ newsletter_title }}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .date {
            color: #7f8c8d;
            font-size: 0.9em;
        }
        .introduction {
            font-size: 1.1em;
            margin-bottom: 30px;
            padding: 15px;
            background-color: #f8f9fa;
            border-left: 4px solid #3498db;
        }
        .topic {
            margin-bottom: 40px;
        }
        .topic-header {
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }
        .topic-title {
            color: #2980b9;
            font-size: 1.4em;
            margin: 0;
        }
        .topic-summary {
            font-style: italic;
            margin-bottom: 20px;
        }
        .article {
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 1px solid #eee;
        }
        .article-title {
            color: #34495e;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .article-summary {
            margin-bottom: 10px;
        }
        .article-relevance {
            font-size: 0.9em;
            color: #16a085;
            margin-bottom: 10px;
        }
        .article-source {
            font-size: 0.8em;
            color: #7f8c8d;
        }
        .article-source a {
            color: #3498db;
            text-decoration: none;
        }
        .article-source a:hover {
            text-decoration: underline;
        }
        .footer {
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            text-align: center;
            font-size: 0.9em;
            color: #7f8c8d;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ newsletter_title }}</h1>
        <div class="date">{{ date }}</div>
    </div>
    
    <div class="introduction">
        <p>Hola {{ user_name }},</p>
        <p>{{ introduction }}</p>
    </div>
    
    {% for topic in topics %}
    <div class="topic">
        <div class="topic-header">
            <h2 class="topic-title">{{ topic.name }}</h2>
        </div>
        
        <div class="topic-summary">
            <p>{{ topic.summary }}</p>
        </div>
        
        {% for article in topic.articles %}
        <div class="article">
            <div class="article-title">{{ article.title }}</div>
            <div class="article-summary">{{ article.summary }}</div>
            {% if article.relevance %}
            <div class="article-relevance">Relevancia: {{ article.relevance }}</div>
            {% endif %}
            <div class="article-source">
                Fuente: {{ article.source }} - 
                <a href="{{ article.url }}" target="_blank">Leer más</a>
            </div>
        </div>
        {% endfor %}
    </div>
    {% endfor %}
    
    <div class="footer">
        <p>¡Gracias por leer tu newsletter personalizado!</p>
        <p>Recibe este resumen diariamente según tus intereses.</p>
    </div>
</body>
</html>
            """
            
            # Crear el directorio si no existe
            os.makedirs(os.path.dirname(template_path), exist_ok=True)
            
            # Guardar la plantilla
            with open(template_path, "w", encoding="utf-8") as f:
                f.write(default_template.strip())
    
    def _generate_simple_html(self, data: Dict[str, Any]) -> str:
        """
        Generar HTML simple en caso de error con la plantilla.
        
        Args:
            data: Datos para la plantilla
            
        Returns:
            HTML simple
        """
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{data['newsletter_title']}</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
            <h1>{data['newsletter_title']}</h1>
            <p>{data['date']}</p>
            <p>Hola {data['user_name']},</p>
            <p>{data['introduction']}</p>
        """
        
        for topic in data["topics"]:
            html += f"""
            <h2>{topic['name']}</h2>
            <p><em>{topic['summary']}</em></p>
            """
            
            for article in topic["articles"]:
                html += f"""
                <div style="margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #eee;">
                    <h3>{article.get('title', 'Sin título')}</h3>
                    <p>{article.get('summary', 'Sin resumen')}</p>
                """
                
                if "relevance" in article:
                    html += f"<p><strong>Relevancia:</strong> {article['relevance']}</p>"
                
                html += f"""
                    <p>Fuente: {article.get('source', 'Desconocida')} - 
                    <a href="{article.get('url', '#')}" target="_blank">Leer más</a></p>
                </div>
                """
            
        html += """
            <p style="margin-top: 30px; padding-top: 10px; border-top: 1px solid #eee;">
                ¡Gracias por leer tu newsletter personalizado!<br>
                Recibe este resumen diariamente según tus intereses.
            </p>
        </body>
        </html>
        """
        
        return html

# Ejemplo de uso
"""
async def example():
    # Datos de ejemplo
    user_data = {
        "name": "Ana",
        "topics": ["Inteligencia Artificial", "Cambio Climático"]
    }
    
    summarized_news = {
        "Inteligencia Artificial": {
            "summary": "Importantes avances en IA generativa y nuevos modelos de lenguaje.",
            "articles": [
                {
                    "title": "OpenAI anuncia GPT-5",
                    "summary": "Nueva versión con mejoras en razonamiento.",
                    "relevance": "Es un avance significativo en NLP.",
                    "url": "https://example.com/1",
                    "source": "Tech News"
                }
            ]
        },
        "Cambio Climático": {
            "summary": "Nuevas políticas internacionales contra el cambio climático.",
            "articles": [
                {
                    "title": "ONU presenta nuevo acuerdo climático",
                    "summary": "Países se comprometen a reducir emisiones.",
                    "relevance": "Podría tener impacto global en políticas ambientales.",
                    "url": "https://example.com/2",
                    "source": "Climate Report"
                }
            ]
        }
    }
    
    formatter = FormatterAgent()
    result = await formatter.format_newsletter(user_data, summarized_news)
    print(result["title"])
    print("\nHTML:")
    print(result["html"][:200] + "...")
    print("\nText:")
    print(result["text"][:200] + "...")

# Para ejecutar el ejemplo
import asyncio
asyncio.run(example())
""" 