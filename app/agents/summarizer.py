from openai import OpenAI
from typing import List, Dict, Any
from app.core.config import OPENAI_API_KEY

# Inicializar cliente
client = OpenAI(api_key=OPENAI_API_KEY)

class SummarizerAgent:
    """
    Agente que resume las noticias encontradas.
    
    Este agente utiliza OpenAI para crear resúmenes concisos y coherentes
    de los artículos de noticias encontrados para cada tópico de interés.
    """
    
    def __init__(self, max_summary_length: int = 150, include_relevance: bool = True):
        """
        Inicializar el agente de resumen.
        
        Args:
            max_summary_length: Longitud máxima en palabras para cada resumen
            include_relevance: Si se debe incluir explicación de relevancia
        """
        self.max_summary_length = max_summary_length
        self.include_relevance = include_relevance
    
    async def summarize_news_by_topic(self, news_by_topic: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Resumir las noticias agrupadas por tópico.
        
        Args:
            news_by_topic: Diccionario con tópicos como claves y listas de noticias como valores
            
        Returns:
            Diccionario con resúmenes por tópico
        """
        summarized_results = {}
        
        for topic, news_items in news_by_topic.items():
            if not news_items:
                summarized_results[topic] = {
                    "summary": f"No se encontraron noticias para el tópico '{topic}'.",
                    "articles": []
                }
                continue
            
            # Obtener un resumen general del tópico
            topic_summary = await self._generate_topic_summary(topic, news_items)
            
            # Resumir cada artículo individualmente
            summarized_articles = []
            for article in news_items:
                article_summary = await self._summarize_article(
                    article, 
                    topic, 
                    self.include_relevance
                )
                summarized_articles.append(article_summary)
            
            # Guardar los resultados para este tópico
            summarized_results[topic] = {
                "summary": topic_summary,
                "articles": summarized_articles
            }
        
        return summarized_results
    
    async def _generate_topic_summary(self, topic: str, news_items: List[Dict[str, Any]]) -> str:
        """
        Generar un resumen general para un tópico basado en todas las noticias.
        
        Args:
            topic: Nombre del tópico
            news_items: Lista de artículos para el tópico
            
        Returns:
            Resumen general del tópico
        """
        # Extraer títulos y descripciones para el resumen
        titles = [item.get("title", "") for item in news_items]
        descriptions = [item.get("description", "") for item in news_items if item.get("description")]
        
        # Construir el contexto con los primeros 3 títulos y descripciones
        context = "\n\n".join([
            "Títulos:",
            "\n".join(titles[:3]),
            "\nDescripciones:",
            "\n".join(descriptions[:3])
        ])
        
        # Prompt para OpenAI
        prompt = f"""
        Basándote en las siguientes noticias sobre "{topic}", genera un resumen general 
        que capture las tendencias o temas principales en no más de 3 oraciones.
        
        {context}
        
        Resumen:
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un experto en sintetizar información de noticias de manera clara y objetiva."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error al generar resumen de tópico: {e}")
            return f"Resumen no disponible para '{topic}'."
    
    async def _summarize_article(self, article: Dict[str, Any], topic: str, include_relevance: bool) -> Dict[str, Any]:
        """
        Resumir un artículo individual.
        
        Args:
            article: Diccionario con información del artículo
            topic: Nombre del tópico
            include_relevance: Si se debe incluir explicación de relevancia
            
        Returns:
            Artículo con resumen añadido
        """
        # Extraer la información del artículo
        title = article.get("title", "")
        description = article.get("description", "")
        content = article.get("content", "")
        
        # Combinar el contenido disponible para el contexto
        context = f"Título: {title}\n"
        if description:
            context += f"Descripción: {description}\n"
        if content:
            context += f"Contenido: {content}\n"
        
        # Construir el prompt dependiendo de si se incluye relevancia
        if include_relevance:
            prompt = f"""
            Resume el siguiente artículo sobre "{topic}" en no más de {self.max_summary_length} palabras.
            
            {context}
            
            Proporciona:
            1. Un resumen conciso
            2. Una breve explicación de por qué este artículo es relevante para las personas interesadas en {topic}
            
            Formato:
            Resumen: [resumen conciso]
            Relevancia: [explicación breve]
            """
        else:
            prompt = f"""
            Resume el siguiente artículo sobre "{topic}" en no más de {self.max_summary_length} palabras.
            
            {context}
            
            Resumen:
            """
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un experto en resumir noticias de manera concisa y precisa."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=250
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Procesar la respuesta
            summary = ""
            relevance = ""
            
            if include_relevance:
                # Intentar extraer resumen y relevancia
                parts = response_text.split("Relevancia:", 1)
                if len(parts) > 1:
                    summary_part = parts[0]
                    relevance = parts[1].strip()
                    
                    # Extraer el resumen
                    if "Resumen:" in summary_part:
                        summary = summary_part.split("Resumen:", 1)[1].strip()
                    else:
                        summary = summary_part.strip()
                else:
                    summary = response_text
            else:
                summary = response_text
            
            # Crear el artículo resumido
            summarized_article = article.copy()
            summarized_article["summary"] = summary
            if relevance:
                summarized_article["relevance"] = relevance
            
            return summarized_article
        except Exception as e:
            print(f"Error al resumir artículo '{title}': {e}")
            
            # En caso de error, devolver el artículo original con un resumen básico
            summarized_article = article.copy()
            summarized_article["summary"] = description or "Resumen no disponible."
            if include_relevance:
                summarized_article["relevance"] = "Información no disponible."
            
            return summarized_article

# Ejemplo de uso
"""
async def example():
    # Ejemplo de datos de noticias por tópico
    news_by_topic = {
        "Inteligencia Artificial": [
            {
                "title": "OpenAI anuncia GPT-5 con capacidades mejoradas",
                "description": "La nueva versión promete mejoras en razonamiento y comprensión contextual",
                "content": "OpenAI ha anunciado hoy el lanzamiento de GPT-5, la nueva versión de su modelo de lenguaje...",
                "url": "https://example.com/news/1",
                "source": "Tech News"
            },
            {
                "title": "Google lanza nuevo modelo de IA para competir con GPT",
                "description": "El gigante tecnológico presenta su respuesta a los avances de OpenAI",
                "url": "https://example.com/news/2"
            }
        ]
    }
    
    summarizer = SummarizerAgent()
    results = await summarizer.summarize_news_by_topic(news_by_topic)
    print(results)

# Para ejecutar el ejemplo de forma asíncrona
import asyncio
asyncio.run(example())
""" 