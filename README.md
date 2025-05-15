# 🧠 Newsletter Inteligente

Sistema automatizado de generación y envío de newsletters personalizados utilizando agentes de OpenAI.

## 🎯 Descripción

Este proyecto implementa un sistema de backend basado en agentes inteligentes que genera newsletters personalizados según los tópicos de interés de cada usuario y los envía por correo electrónico.

## 🧩 Características

- **Agentes inteligentes**: Utiliza OpenAI Agents SDK para crear agentes especializados
- **Contenido personalizado**: Genera newsletters según los intereses del usuario
- **Base de datos**: Integración con Supabase para gestión de usuarios y preferencias
- **API REST**: Implementada con FastAPI para la gestión del sistema

## 👥 Estructura de Agentes

El sistema utiliza cuatro agentes principales:

1. **NewsFetcherAgent**: Busca noticias relevantes según los tópicos del usuario
2. **SummarizerAgent**: Resume las noticias encontradas
3. **FormatterAgent**: Da formato al contenido para hacerlo atractivo
4. **SenderAgent**: Envía el newsletter por el canal seleccionado

## 🛠️ Tecnologías

- [FastAPI](https://fastapi.tiangolo.com/) - Framework web
- [Supabase](https://supabase.com/) - Base de datos y autenticación
- [OpenAI](https://openai.com/) - Agentes inteligentes y LLMs
- [NewsAPI](https://newsapi.org/) - Fuente de noticias
- [Python 3.9+](https://www.python.org/) - Lenguaje de programación

## 🚀 Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/GianniCarvacho-Prsnl/newsletter-inteligente.git
cd newsletter-inteligente
```

2. Crear y activar entorno virtual:
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
# Editar .env con tus claves de API y configuración
```

## 🗃️ Estructura del Proyecto

```
newsletter-inteligente/
├── app/                      # Aplicación principal
│   ├── agents/               # Agentes inteligentes
│   │   ├── news_fetcher.py   # Agente de búsqueda de noticias
│   │   ├── summarizer.py     # Agente de resumen
│   │   ├── formatter.py      # Agente de formato
│   │   └── sender.py         # Agente de envío
│   ├── api/                  # Endpoints API
│   ├── core/                 # Configuración central
│   ├── db/                   # Modelos y conexión a DB
│   ├── utils/                # Utilidades
│   └── main.py               # Punto de entrada
├── templates/                # Plantillas para newsletters
├── tests/                    # Pruebas unitarias
├── docs/                     # Documentación
├── .env.example              # Ejemplo de variables de entorno
├── requirements.txt          # Dependencias
└── README.md                 # Este archivo
```

## 📝 Uso

Para ejecutar el sistema manualmente:

```bash
# Activar entorno virtual
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Ejecutar el script de generación manual
python -m app.scripts.generate_newsletter
```

Para iniciar el servidor API:

```bash
uvicorn app.main:app --reload
```

## 🔐 Configuración de Supabase

El proyecto requiere una instancia de Supabase con las siguientes tablas:
- `users`: Información de usuarios
- `topics`: Tópicos disponibles
- `user_topics`: Relación entre usuarios y tópicos
- `newsletters`: Registro de newsletters enviados

## 📚 Documentación

Para más detalles, consulta la [documentación completa](docs/README.md).

## 🤝 Contribución

Las contribuciones son bienvenidas. Por favor, abre un issue o pull request para sugerencias.

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles. 