import os
import re
import time
import feedparser
import requests
import string
import unicodedata
import urllib.parse
from pathlib import Path
from collections import defaultdict
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse, urljoin
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


# Opciones
brave_options = Options()
brave_options.binary_location = 'C:/Program Files/BraveSoftware/Brave-Browser/Application/Brave.exe'
driver_path = 'C:/Program Files/BraveSoftware/Brave-Browser/Application/chromedriver.exe'
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=brave_options)
output_directory: str = 'C:/Users/lucho/Downloads/NOTICIAS/Rss'


def get_output_directory(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.strip()
    domain_directory = os.path.join(output_directory, domain)
    os.makedirs(domain_directory, exist_ok=True)
    return domain_directory


def clean_filename(filename):
    valid_chars = f"-_.() {string.ascii_letters}{string.digits}"
    cleaned_filename = ''.join(c for c in filename if c in valid_chars)
    cleaned_filename = unicodedata.normalize('NFKD', cleaned_filename).encode('ASCII', 'ignore').decode()
    cleaned_filename = cleaned_filename.replace('/', '_')  # Reemplazar barras diagonales por guiones bajos
    cleaned_filename = cleaned_filename.strip()  # Eliminar espacios adicionales al inicio y final

    # Acortar el nombre del archivo si es demasiado largo (máximo 200 caracteres)
    max_filename_length = 50
    if len(cleaned_filename) > max_filename_length:
        cleaned_filename = cleaned_filename[:max_filename_length]

    return cleaned_filename


# Función para descargar archivos
def download_file(url, output_folder):
    try:
        response = requests.get(url)
        response.raise_for_status()

        # Verificar si el archivo ya existe en el directorio de salida
        filename = re.findall("filename=(.+)", response.headers.get("content-disposition", ""))
        if filename:
            parsed_url = urllib.parse.urlparse(url)
            filename = Path(parsed_url.path).name
            filename = urllib.parse.unquote(filename)  # Decodificar el nombre del archivo
            filename = clean_filename(filename)
        else:
            # Si no se encuentra el nombre del archivo, extraerlo del final de la URL
            filename = os.path.basename(urlparse(url).path)
            filename = urllib.parse.unquote(filename)  # Decodificar el nombre del archivo
            filename = clean_filename(filename)

        output_path = os.path.join(output_folder, filename)

        # Verificar si el archivo ya existe en el directorio de salida
        if os.path.exists(output_path):
            print(f"El archivo ya existe en el directorio de salida: {filename}")
            return filename
        else:
            with open(output_path, "wb") as file:
                file.write(response.content)

            return filename

    except requests.exceptions.MissingSchema as e:
        print(f'Error al descargar el archivo {url}: URL no válida')
        return None

    except (requests.exceptions.ConnectionError, ConnectionResetError) as e:
        print(f'Error de conexión al descargar el archivo {url}')
        return None

    except requests.exceptions.HTTPError as e:
        print(f'Error al descargar el archivo {url}: {e}')
        return None

# URLs del feed RSS
rss_urls = rss_urls = [
    
    "https://trends.google.com/trends/trendingsearches/daily/rss?geo=ES",
    "https://www.coruna.gal/web/es/rss/noticias",
    "https://www.laopinioncoruna.es/rss/section/1244710",
    "https://www.laopinioncoruna.es/rss/section/1612270",
    "https://www.laopinioncoruna.es/rss/section/1612271",
    "https://www.laopinioncoruna.es/rss/section/13576",
    "https://www.laopinioncoruna.es/rss/section/13501",
    "https://www.laopinioncoruna.es/rss/section/13563",
    "https://www.laopinioncoruna.es/rss/section/13509",
    "https://www.laopinioncoruna.es/rss/section/13571",
    "https://www.laopinioncoruna.es/rss/section/1527708",
    "https://www.laopinioncoruna.es/rss/section/13668",
    "https://www.laopinioncoruna.es/rss/section/13659",
    "https://www.lavozdegalicia.es/coruna/index.xml",
    "https://www.lavozdegalicia.es/carballo/index.xml",
    "https://ep00.epimg.net/rss/ccaa/galicia.xml",
    "https://feeds2.feedburner.com/libertaddigital/nacional",
    "https://e00-elmundo.uecdn.es/elmundo/rss/espana.xml",
    "https://thedefiant.io/feed/",
    "https://www.coindesk.com/arc/outboundfeeds/rss/?outputType=xml",
    "https://cointelegraph.com/rss",
    "https://cryptopotato.com/feed/",
    "https://cryptoslate.com/feed/",
    "https://cryptonews.com/news/feed/",
    "https://smartliquidity.info/feed/",
    "https://finance.yahoo.com/news/rssindex",
    "https://www.cnbc.com/id/10000664/device/rss/rss.html",
    "https://time.com/nextadvisor/feed/",
    "https://benjaminion.xyz/newineth2/rss_feed.xml",
    "https://www.boe.es/rss/canal.php?c=prestamos",
    "https://www.aemet.es/es/noticias.rss",
    "https://www.aemet.es/documentos_d/eltiempo/prediccion/avisos/rss/CAP_AFAZ711504_RSS.xml",
    "https://www.aemet.es/documentos_d/eltiempo/prediccion/avisos/rss/CAP_AFAZ711503_RSS.xml",
    "https://www.aemet.es/documentos_d/eltiempo/prediccion/avisos/rss/CAP_AFAZ711502_RSS.xml",
    "https://www.aemet.es/documentos_d/eltiempo/prediccion/avisos/rss/CAP_AFAZ711501_RSS.xml",
    "https://www.boe.es/rss/canal.php?c=imp_amb",
    "https://xxicoruna.sergas.gal/_layouts/agoracentros/rss.aspx?seccion=SalaComunicacion",
    "https://xxicoruna.sergas.gal/_layouts/agoracentros/rss.aspx?seccion=Novidades",
    "https://www.boe.es/rss/canal.php?c=ccolaboracion",
    "https://www.coruna.gal/web/es/rss/ociocultura",
    "https://www.coruna.gal/web/es/rss/contenidos",
    "https://www.coruna.gal/web/es/rss/entidades",
    "https://www.coruna.gal/web/es/rss/eventos",
    "https://www.poderjudicial.es/cgpj/es/Poder-Judicial/Tribunal-Supremo/ch.Noticias-Judiciales.formato1/",
    "https://www.poderjudicial.es/cgpj/es/Poder-Judicial/Audiencia-Nacional/ch.Noticias-Judiciales.formato1/",
    "https://www.boe.es/rss/canal.php?c=tc",
    "https://www.boe.es/rss/canal.php?c=fundaciones",
    "https://www.boe.es/rss/canal.php?c=notariado",
    "https://www.boe.es/rss/canal.php?c=premios",
    "https://www.boe.es/rss/canal.php?c=ccolectivos",
    "https://www.boe.es/rss/canal.php?c=becas",
    "https://www.boe.es/rss/canal.php?c=ayudas"

]
# Función para verificar si un elemento contiene palabras clave no deseadas
def contains_unwanted_keywords(text):
    unwanted_keywords = ["cookies", "banner"]  # Palabras clave no deseadas
    for keyword in unwanted_keywords:
        if keyword in text.lower().split():  # Verificar si la palabra está en el texto
            return True
    return False


# Lista de clases no deseadas y etiquetas no deseadas
unwanted_classes = ["cookies-policy", "ad-banner", "unwanted-class"]
unwanted_tags = ["script", "style", "css"]

elements_to_extract = ['main', 'div', 'ul', 'ol', 'li', 'table', 'tr', 'td', 'a', 'form', 'article', 'p', 'textarea',
                       'pre', 'h1', 'h2', 'h3', 'title', 'iframe', 'section', 'body', '.entradilla, .parrafo']
# Crear un diccionario para almacenar el texto extraído de cada URL
extracted_text_dict = defaultdict(str)

# Crear un conjunto para almacenar las URLs ya procesadas
processed_urls = set()
processed_count = 0

# Bucle para procesar las URLs del feed RSS
for rss_url in rss_urls:
    # Analizar el feed RSS
    feed = feedparser.parse(rss_url)
    # Obtener las entradas del feed RSS
    for entry in feed.entries:
        # Obtener los enlaces
        urls = []
        possible_link_fields = ['ht_news_item_url', 'guid', 'link']
        for field in possible_link_fields:
            if field in entry and entry[field]:
                urls.append(entry[field])

        # Procesar cada enlace si no se ha procesado antes
        for url in urls:
            if url and url not in processed_urls:
                # Verificar si es una URL válida
                if not re.match(r'^https?://', url):
                    print(f'URL no válida: {url}')
                    continue
                # Obtener el título de la noticia
                news_title = entry.get('ht_news_item_title', entry.get('title', entry.get('link', '')))
                news_resumen = entry.get('ht_news_item_snippet', entry.get('description', ''))
                news_date = entry.get('published', entry.get('pubDate', ''))
                news_creator = entry.get('author', entry.get('dc_creator', entry.get('itunes_author', '')))
                news_source = []
                possible_news_source = ['media_description', 'ht_news_item_source', 'keywords',
                                        'media_keywords', 'category', 'description']
                for field in possible_news_source:
                    if field in entry and entry[field]:
                        news_source.extend(entry[field].split(','))
                news_source_str = ', '.join(news_source)
                news_keywords = []
                possible_keyword_fields = ['media_description', 'ht_news_item_source', 'itunes_keywords',
                                           'media_keywords', 'category', 'description']
                for field in possible_keyword_fields:
                    if field in entry and entry[field]:
                        news_keywords.extend(entry[field].split(','))
                news_keywords = [keyword.strip(', ') for keyword in news_keywords]

                # Procesar el enlace
                if url:
                    parsed_url = urlparse(url)
                    url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
                    if not re.match(r'^https?://', url):
                        print(f'URL no válida: {url}')
                        continue
                    print("Procesando URL:", url)
                    try:
                        if url.endswith('.pdf') or url.endswith('.tar.gz') or url.endswith('.csv'):
                            output_folder = get_output_directory(url)
                            filename = download_file(url, output_directory)
                            if filename:
                                print(f"Archivo descargado: {filename}")
                        else:
                            # Obtener el contenido de la página web solo si no es un archivo descargable
                            print('Obteniendo contenido de la página...')
                            processed_urls.add(url)
                            processed_count += 1
                            driver.get(url)
                            page_load_timeout = 180
                            start_time = time.time()
                            while time.time() - start_time < page_load_timeout:
                                if driver.execute_script('return document.readyState') == 'complete':
                                    break
                                time.sleep(3)
                            time.sleep(1)
                            html = driver.page_source
                            soup = BeautifulSoup(html, 'html.parser')
                            parsed_url = urlparse(url)
                            domain = parsed_url.netloc.strip()
                            domain_directory = os.path.join(output_directory, domain)
                            os.makedirs(domain_directory, exist_ok=True)
                            elements = soup.find_all(elements_to_extract)
                            combined_text = ''
                            for element in elements:
                                if any(unwanted_class in element.get('class', []) for unwanted_class in
                                       unwanted_classes):
                                    continue
                                if element.name in unwanted_tags:
                                    continue
                                text = element.get_text()
                                if text and not contains_unwanted_keywords(text):
                                    combined_text += text + '\n'
                            combined_text = f'Título: {news_title}\n' \
                                            f'Resumen: {news_resumen}\n\n' \
                                            f'Noticia Raspada: {combined_text}\n\n' \
                                            f'Enlace: {url}\n' \
                                            f'Palabra clave: {news_source}\n' \
                                            f'Autor: {news_creator}\n' \
                                            f'Fecha: {news_date}\n'

                            # Obtener el identificador único para el archivo de texto
                            unique_identifier = f"{news_title}"
                            unique_filename = clean_filename(unique_identifier) + ".txt"
                            text_file_path = os.path.join(domain_directory, unique_filename)

                            # Leer el contenido actual del archivo (si existe)
                            existing_text = ''
                            if os.path.exists(text_file_path):
                                with open(text_file_path, 'r', encoding='utf-8') as existing_file:
                                    existing_text = existing_file.read()

                            # Comparar el contenido existente con el nuevo texto y agregar solo el contenido no duplicado
                            if combined_text not in existing_text:
                                with open(text_file_path, 'w', encoding='utf-8') as text_file:
                                    text_file.write(combined_text)

                                # Guardar las palabras clave en un archivo separado
                                #keywords_filename = f'{clean_filename(unique_identifier)}_keywords.txt'
                                #keywords_file_path = os.path.join(domain_directory, keywords_filename)
                                #with open(keywords_file_path, 'w', encoding='utf-8') as keywords_file:
                                    #if news_source_str:
                                        #keywords_file.write(news_source_str + '\n')

                                #print(f'Detalles y palabras clave guardados en: {text_file_path}, {keywords_file_path}')

                            # Descargar archivos si existen en el enlace
                            links = soup.find_all('a', href=True)
                            for link in links:
                                file_url = link['href']
                                if not file_url.startswith('http://') and not file_url.startswith('https://'):
                                    file_url = urljoin(url, file_url)
                                try:
                                    # Descargar el archivo solo si es descargable
                                    if file_url.endswith('.pdf') or file_url.endswith('.tar.gz') or file_url.endswith(
                                            '.txt') or file_url.endswith('.xlsx') or file_url.endswith(
                                                '.doc') or file_url.endswith('.csv'):
                                        filename = download_file(file_url, domain_directory)
                                        if filename:
                                            print(f"Archivo descargado: {filename}")
                                except Exception as e:
                                    print(f'Error al descargar el archivo {file_url}: {e}')

                    except WebDriverException as e:
                        print(f'Error al acceder a la URL: {url}')
                        print(f'Error: {e}')

                else:
                    print("No se encontró URL en esta entrada.")
                time.sleep(1)

driver.quit()