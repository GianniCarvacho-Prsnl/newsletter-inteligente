# 📚 Documentación - Newsletter Inteligente

Esta documentación proporciona información sobre cómo configurar, utilizar y extender el sistema de Newsletter Inteligente.

## 📋 Índice

1. [Introducción](#introducción)
2. [Instalación y Configuración](#instalación-y-configuración)
3. [Modelo de Datos](#modelo-de-datos)
4. [Agentes](#agentes)
5. [API REST](#api-rest)
6. [Guía de Uso](#guía-de-uso)
7. [Pruebas](#pruebas)
8. [Solución de Problemas](#solución-de-problemas)

## 📖 Introducción

Newsletter Inteligente es un sistema que utiliza inteligencia artificial para:

1. Buscar noticias relevantes según los intereses del usuario
2. Resumir y extraer lo más importante de cada noticia
3. Formatear el contenido en un newsletter atractivo
4. Enviar el newsletter al usuario por su canal preferido

El sistema está diseñado con una arquitectura basada en agentes, donde cada agente es responsable de una parte específica del proceso. Esta arquitectura permite:

- Modularidad y separación de responsabilidades
- Facilidad para extender o reemplazar componentes
- Mantenimiento simplificado

## 🔧 Instalación y Configuración

### Requisitos Previos

- Python 3.9+
- Cuenta en Supabase
- Cuenta en OpenAI
- (Opcional) Cuenta en NewsAPI

### Pasos de Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/GianniCarvacho-Prsnl/newsletter-inteligente.git
cd newsletter-inteligente
```

2. Crear un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus claves y configuración
```

5. Configurar Supabase:
   - Crear un proyecto en Supabase
   - Ejecutar el script para crear las tablas:
   ```bash
   python -m app.scripts.create_supabase_tables --org-id <tu_org_id> --project-id <tu_project_id>
   ```

## 🗃️ Modelo de Datos

El sistema utiliza las siguientes tablas en Supabase:

### Tabla `users`

Almacena información de los usuarios.

| Campo      | Tipo                 | Descripción                    |
|------------|----------------------|--------------------------------|
| id         | UUID                 | Identificador único (PK)       |
| name       | TEXT                 | Nombre del usuario             |
| email      | TEXT                 | Correo electrónico (UNIQUE)    |
| phone      | TEXT                 | Número de teléfono (opcional)  |
| telegram_id| TEXT                 | ID de Telegram (opcional)      |
| preferences| JSONB                | Preferencias adicionales       |
| created_at | TIMESTAMP WITH TZ    | Fecha de creación              |
| updated_at | TIMESTAMP WITH TZ    | Fecha de última actualización  |

### Tabla `topics`

Almacena los tópicos disponibles.

| Campo      | Tipo                 | Descripción                    |
|------------|----------------------|--------------------------------|
| id         | UUID                 | Identificador único (PK)       |
| name       | TEXT                 | Nombre del tópico (UNIQUE)     |
| description| TEXT                 | Descripción del tópico         |
| created_at | TIMESTAMP WITH TZ    | Fecha de creación              |
| updated_at | TIMESTAMP WITH TZ    | Fecha de última actualización  |

### Tabla `user_topics`

Relación entre usuarios y tópicos.

| Campo      | Tipo                 | Descripción                    |
|------------|----------------------|--------------------------------|
| id         | UUID                 | Identificador único (PK)       |
| user_id    | UUID                 | Referencia a users(id)         |
| topic_id   | UUID                 | Referencia a topics(id)        |
| created_at | TIMESTAMP WITH TZ    | Fecha de creación              |

### Tabla `newsletters`

Registro de newsletters enviados.

| Campo      | Tipo                 | Descripción                    |
|------------|----------------------|--------------------------------|
| id         | UUID                 | Identificador único (PK)       |
| user_id    | UUID                 | Referencia a users(id)         |
| content    | TEXT                 | Contenido o título del newsletter |
| topics     | TEXT[]               | Array de tópicos incluidos     |
| channel    | TEXT                 | Canal de envío                 |
| sent_at    | TIMESTAMP WITH TZ    | Fecha de envío                 |
| created_at | TIMESTAMP WITH TZ    | Fecha de creación              |

## 🤖 Agentes

El sistema utiliza cuatro agentes principales:

### 1. NewsFetcherAgent

**Responsabilidad**: Buscar noticias relevantes según los tópicos del usuario.

**Características**:
- Utiliza OpenAI para generar términos de búsqueda específicos
- Conecta con NewsAPI para obtener artículos recientes
- Filtrado por idioma y relevancia

**Uso**:
```python
from app.agents.news_fetcher import NewsFetcherAgent

# Crear instancia
fetcher = NewsFetcherAgent()

# Obtener noticias
topics = [
    {"id": "1", "name": "Inteligencia Artificial", "description": "Avances en IA"}
]
news_results = await fetcher.get_news_for_topics(topics, language="es")
```

### 2. SummarizerAgent

**Responsabilidad**: Resumir las noticias encontradas.

**Características**:
- Genera un resumen general por tópico
- Crea resúmenes concisos de cada artículo
- Opcionalmente incluye explicación de relevancia

**Uso**:
```python
from app.agents.summarizer import SummarizerAgent

# Crear instancia
summarizer = SummarizerAgent()

# Resumir noticias
summarized_news = await summarizer.summarize_news_by_topic(news_results)
```

### 3. FormatterAgent

**Responsabilidad**: Formatear el contenido para hacerlo atractivo.

**Características**:
- Genera títulos e introducciones personalizadas
- Aplica plantillas HTML para correo electrónico
- Crea versiones en texto plano

**Uso**:
```python
from app.agents.formatter import FormatterAgent

# Crear instancia
formatter = FormatterAgent()

# Formatear newsletter
user_data = {"name": "Ana", "email": "ana@example.com"}
formatted_newsletter = await formatter.format_newsletter(user_data, summarized_news)
```

### 4. SenderAgent

**Responsabilidad**: Enviar el newsletter al usuario.

**Características**:
- Envío por correo electrónico
- Implementaciones dummy para WhatsApp y Telegram
- Registro de envíos realizados

**Uso**:
```python
from app.agents.sender import SenderAgent

# Crear instancia
sender = SenderAgent()

# Enviar newsletter
send_result = await sender.send_newsletter(user_data, formatted_newsletter, channel="email")
```

## 🌐 API REST

El sistema expone los siguientes endpoints:

### Endpoints Principales

| Método | Ruta                           | Descripción                        |
|--------|--------------------------------|------------------------------------|
| GET    | /                              | Información básica de la API       |
| GET    | /health                        | Verificación de estado             |
| POST   | /api/newsletters/generate      | Generar y enviar newsletter        |
| POST   | /api/newsletters/generate/mock | Generar con datos mock (desarrollo)|
| GET    | /api/newsletters/status/{id}   | Consultar estado de generación     |

### Ejemplo de Uso (cURL)

```bash
# Generar newsletter para un usuario (modo mock)
curl -X POST http://localhost:8000/api/newsletters/generate/mock \
  -H "Content-Type: application/json" \
  -d '{"user_id": "usuario_ejemplo", "channel": "email", "language": "es"}'
```

## 📝 Guía de Uso

### Ejecución Manual desde CLI

Para generar y enviar un newsletter manualmente:

```bash
# Activar entorno virtual
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Enviar a usuario específico con datos reales
python -m app.scripts.generate_newsletter --user-id <id_usuario> --channel email

# Enviar con datos mock (para pruebas)
python -m app.scripts.generate_newsletter --mock
```

### Inicio del Servidor API

```bash
# Activar entorno virtual
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Iniciar el servidor
uvicorn app.main:app --reload
```

La documentación interactiva estará disponible en:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🧪 Pruebas

Para ejecutar las pruebas:

```bash
# Pruebas unitarias
pytest

# Pruebas con cobertura
pytest --cov=app
```

## 🔍 Solución de Problemas

### Problemas Comunes

1. **Error de autenticación con OpenAI**
   - Verificar que la clave API en `.env` es correcta
   - Comprobar que la cuenta tiene saldo disponible

2. **Error de conexión con Supabase**
   - Verificar URL y clave en `.env`
   - Comprobar que las tablas existen

3. **NewsAPI devuelve pocos resultados**
   - La API gratuita tiene limitaciones de uso
   - Considerar usar una clave API de pago

### Logs

Los logs se escriben en la consola y se pueden encontrar en:
- API: Logs del servidor uvicorn
- Script manual: En la consola al ejecutar

Para problemas adicionales, consulta el repositorio de GitHub o abre un issue. 