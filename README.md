# RSS News Processor

Sistema automatizado de recopilación, procesamiento y distribución de noticias RSS en español.

## Descripción

Este proyecto es un sistema integral que:

1. Recopila noticias de múltiples fuentes RSS
2. Procesa y extrae información relevante de cada artículo
3. Almacena el contenido de forma organizada
4. Distribuye las noticias a través de diferentes canales

## Características Principales

- 🔄 Monitoreo continuo de feeds RSS
- 📝 Extracción de texto completo de artículos
- 🏷️ Generación automática de palabras clave
- 📂 Organización jerárquica por dominio
- 🤖 Manejo inteligente de cookies y paywalls
- 📱 Distribución multiplataforma (Telegram, Email, WhatsApp)
- 🔍 Detección de duplicados
- 📊 Logging detallado
- ⚡ Rate limiting para APIs

## Componentes Técnicos

- Selenium WebDriver con Brave Browser para manejo de JavaScript
- NLTK para procesamiento de lenguaje natural
- newspaper3k para extracción de artículos
- Feedparser para procesamiento RSS
- Sistema de caché para URLs procesadas
- Manejo de errores y reintentos
- Rotación de User-Agents

## Estructura de Archivos

```
└── RssNewS/
    ├── RSSnews.py        # Script principal
    ├── config.py         # Configuraciones
    ├── news_sender.py    # Sistema de distribución
    └── rss_urls.py       # URLs de feeds RSS
```

## Configuración

El sistema es altamente configurable a través de 

config.py

, permitiendo ajustar:

- Rutas de almacenamiento
- Intervalos de ejecución
- Credenciales de APIs
- Límites de rate
- Parámetros de logging

## Requisitos del Sistema

- Python 3.x
- Brave Browser
- Chromedriver
- Bibliotecas Python (requirements.txt)
