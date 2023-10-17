Descripción
Este repositorio contiene una colección de scripts en Python utilizados para diversas tareas relacionadas con la obtención, procesamiento y clasificación de contenido web, así como la generación de resúmenes de noticias. A continuación, se proporciona una descripción de cada script y su funcionalidad:

Script 1: web_scraping.py
Este script se encarga de realizar la extracción de información de sitios web y de feeds RSS. Realiza las siguientes tareas:

Descarga de archivos desde enlaces web.
Extracción de texto relevante de páginas web, excluyendo contenido no deseado.
Almacenamiento de información de noticias en archivos de texto.
Script 2: eliminar_lineas_repetidas.py
Este script se utiliza para eliminar líneas repetidas y cortas en archivos de texto. Su funcionalidad incluye:

Eliminación de líneas repetidas o similares en un archivo.
Exclusión de palabras o entidades específicas.
Procesamiento de archivos en una carpeta y eliminación de archivos originales.
Script 3: generar_resumenes.py
Este script genera resúmenes de noticias a partir del contenido de archivos de texto. Realiza las siguientes tareas:

Utiliza el modelo de lenguaje BART para generar resúmenes de noticias.
Combina el resumen generado con información de título, enlace, autor y fecha.
Guarda los resúmenes en archivos de texto en una estructura de directorios.
Script 4: clasificar_archivos.py
Este script se utiliza para clasificar archivos de texto en categorías predefinidas. Su funcionalidad incluye:

Utiliza un modelo de clasificación de texto para predecir la categoría de un archivo.
Mueve los archivos a carpetas correspondientes según la categoría predicha.
Proporciona una clasificación basada en la confianza del modelo.
Requisitos
Asegúrese de tener instaladas las siguientes bibliotecas y dependencias de Python para ejecutar estos scripts:

requests: Para realizar solicitudes web y descargas.
beautifulsoup4: Para analizar el contenido HTML de las páginas web.
feedparser: Para analizar feeds RSS.
selenium: Para la automatización de navegadores web.
transformers: Para utilizar modelos de lenguaje como BART.
langdetect: Para detectar el idioma del contenido.
torch: Para operaciones de aprendizaje profundo.
difflib: Para comparar texto y eliminar líneas repetidas.
Uso
Cada script puede ejecutarse de forma independiente según su funcionalidad. Asegúrese de proporcionar las rutas de directorio y configuraciones necesarias en los scripts antes de ejecutarlos. Para obtener más información sobre cómo utilizar cada script, consulte los comentarios en el código fuente.
