from openai import OpenAI
import os
from typing import List, Dict, Any
from newsapi import NewsApiClient
from app.core.config import NEWS_API_KEY, OPENAI_API_KEY

# Inicializar clientes
client = OpenAI(api_key=OPENAI_API_KEY)
newsapi = NewsApiClient(api_key=NEWS_API_KEY)

class NewsFetcherAgent:
    """
    Agente que busca noticias relevantes según los tópicos del usuario.
    
    Este agente utiliza OpenAI para determinar cómo buscar noticias relevantes
    para cada tópico de interés del usuario, y luego ejecuta esas búsquedas
    utilizando NewsAPI.
    """
    
    def __init__(self, max_articles_per_topic: int = 3):
        """
        Inicializar el agente de búsqueda de noticias.
        
        Args:
            max_articles_per_topic: Máximo número de artículos por tópico
        """
        self.max_articles_per_topic = max_articles_per_topic
    
    async def get_news_for_topics(self, topics: List[Dict[str, Any]], language: str = "es") -> Dict[str, Any]:
        """
        Obtener noticias para los tópicos especificados.
        
        Args:
            topics: Lista de tópicos (cada uno con id, name, description)
            language: Idioma de las noticias (es, en, etc.)
            
        Returns:
            Diccionario con los resultados por tópico
        """
        results = {}
        
        for topic in topics:
            topic_name = topic["name"]
            topic_desc = topic.get("description", "")
            
            # Obtener los términos de búsqueda específicos para este tópico
            search_terms = await self._get_search_terms(topic_name, topic_desc)
            
            # Obtener las noticias usando los términos de búsqueda
            news_items = []
            for term in search_terms:
                try:
                    articles = self._fetch_from_news_api(term, language)
                    news_items.extend(articles)
                    
                    # Limitar el número de artículos
                    if len(news_items) >= self.max_articles_per_topic:
                        news_items = news_items[:self.max_articles_per_topic]
                        break
                except Exception as e:
                    print(f"Error al buscar noticias para '{term}': {e}")
            
            # Guardar los resultados para este tópico
            results[topic_name] = news_items
        
        return results
    
    async def _get_search_terms(self, topic_name: str, topic_description: str = "") -> List[str]:
        """
        Usar OpenAI para generar términos de búsqueda relevantes para un tópico.
        
        Args:
            topic_name: Nombre del tópico
            topic_description: Descripción del tópico (opcional)
            
        Returns:
            Lista de términos de búsqueda
        """
        # Prompt para OpenAI
        prompt = f"""
        Necesito buscar noticias relevantes sobre el tópico: "{topic_name}".
        {f'Descripción adicional: {topic_description}' if topic_description else ''}
        
        Por favor, proporciona 3 términos o frases de búsqueda que puedan usarse con NewsAPI
        para encontrar artículos recientes y relevantes sobre este tema.
        
        Responde solo con los términos separados por comas, sin numeración ni texto adicional.
        """
        
        # Llamada a OpenAI
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un asistente experto en encontrar noticias relevantes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=100
            )
            
            # Extraer y procesar los términos de búsqueda
            search_terms_text = response.choices[0].message.content.strip()
            search_terms = [term.strip() for term in search_terms_text.split(',')]
            
            return search_terms
        except Exception as e:
            print(f"Error al generar términos de búsqueda: {e}")
            # Fallback: usar el nombre del tópico directamente
            return [topic_name]
    
    def _fetch_from_news_api(self, query: str, language: str = "es") -> List[Dict[str, Any]]:
        """
        Buscar noticias en NewsAPI usando un término de búsqueda.
        
        Args:
            query: Término de búsqueda
            language: Idioma de las noticias
            
        Returns:
            Lista de artículos encontrados
        """
        try:
            # Realizar la búsqueda
            response = newsapi.get_everything(
                q=query,
                language=language,
                sort_by="relevancy",
                page_size=5  # Limitar a 5 resultados por término
            )
            
            # Procesar y estructurar los resultados
            articles = []
            for article in response.get("articles", []):
                processed_article = {
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "content": article.get("content", ""),
                    "url": article.get("url", ""),
                    "source": article.get("source", {}).get("name", ""),
                    "published_at": article.get("publishedAt", ""),
                    "search_term": query
                }
                articles.append(processed_article)
            
            return articles
        except Exception as e:
            print(f"Error al buscar en NewsAPI: {e}")
            return []

# Ejemplo de uso
"""
async def example():
    fetcher = NewsFetcherAgent()
    topics = [
        {"id": "1", "name": "Inteligencia Artificial", "description": "Avances en IA y machine learning"},
        {"id": "2", "name": "Cambio Climático", "description": "Noticias sobre el medio ambiente y cambio climático"}
    ]
    results = await fetcher.get_news_for_topics(topics)
    print(results)

# Para ejecutar el ejemplo de forma asíncrona
import asyncio
asyncio.run(example())
""" 