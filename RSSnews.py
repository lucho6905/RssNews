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
from urllib.parse import urlparse, urlunparse, urljoin
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from newspaper import Article
import json
import hashlib
from datetime import datetime, timedelta
from rss_urls import RSS_FEEDS
from config import *
import random
from news_sender import NewsSender
import logging

import nltk

def setup_nltk():
    """Configura y descarga los recursos necesarios de NLTK"""
    resources = [
        'punkt',
        'punkt_tab',
        'averaged_perceptron_tagger',
        'maxent_ne_chunker',
        'words',
        'stopwords'
    ]
    
    for resource in resources:
        try:
            nltk.data.find(f'tokenizers/{resource}')
        except LookupError:
            try:
                print(f"Descargando recurso NLTK: {resource}")
                nltk.download(resource, quiet=True)
            except Exception as e:
                print(f"Error descargando {resource}: {e}")

# Configurar NLTK antes de cualquier otra operación
setup_nltk()

# Opciones del navegador
brave_options = Options()
brave_options.binary_location = BRAVE_PATH
brave_options.add_argument('--headless=new')  # Nueva sintaxis para modo headless
brave_options.add_argument('--disable-gpu')  # Deshabilitar aceleración GPU
brave_options.add_argument('--no-sandbox')  # Mejorar estabilidad
brave_options.add_argument('--disable-dev-shm-usage')  # Evitar errores de memoria
brave_options.add_argument('--log-level=3')  # Minimizar logs
brave_options.add_argument('--silent')  # Reducir salida de mensajes
brave_options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Deshabilitar logs de DevTools

service = Service(DRIVER_PATH)
service.log_path = os.devnull  # Deshabilitar logs del servicio
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

# Función para verificar si un elemento contiene palabras clave no deseadas
def contains_unwanted_keywords(text):
    unwanted_keywords = ["cookies", "banner"]  # Palabras clave no deseadas
    for keyword in unwanted_keywords:
        if keyword in text.lower().split():  # Verificar si la palabra está en el texto
            return True
    return False


# Crear un diccionario para almacenar el texto extraído de cada URL
extracted_text_dict = defaultdict(str)

# Crear un conjunto para almacenar las URLs ya procesadas
processed_urls = set()
processed_count = 0

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
]

def accept_cookies(driver, url):
    try:
        driver.get(url)
        # Botones comunes de cookies
        cookie_buttons = [
            "//button[contains(text(), 'Aceptar')]",
            "//button[contains(text(), 'Entendido')]",
            "//button[contains(@class, 'cookie')]",
            "//a[contains(text(), 'Aceptar')]",
            "//button[contains(text(), 'Accept')]"
        ]
        
        for button in cookie_buttons:
            try:
                cookie_button = driver.find_element("xpath", button)
                cookie_button.click()
                break
            except:
                continue
                
        return True
    except Exception as e:
        print(f"Error aceptando cookies: {e}")
        return False

def extract_full_text(url):
    try:
        # Primero intentar con Selenium
        accept_cookies(driver, url)
        time.sleep(2)  # Esperar a que cargue
        
        # Luego extraer con newspaper3k
        article = Article(url, language='es')
        article.config.browser_user_agent = random.choice(USER_AGENTS)
        article.download()
        article.parse()
        
        # Si el texto está vacío o contiene palabras de paywall/cookies, usar Selenium
        if not article.text or contains_unwanted_keywords(article.text):
            text = driver.find_element("tag name", "body").text
            return text
            
        return article.text
    except Exception as e:
        print(f'Error procesando {url}: {str(e)}')
        return ""

def process_feed_entry(entry):
    # Convertir FeedParserDict a diccionario
    if hasattr(entry, 'title'):
        title = str(entry.title)
    else:
        title = ""
    
    if hasattr(entry, 'link'):
        link = str(entry.link)
    else:
        link = ""
        
    return {
        'title': title,
        'link': link,
        'published': str(entry.get('published', ''))
    }

class NewsProcessor:
    def __init__(self):
        self.processed_news = self.load_processed_news()
        self.news_sender = NewsSender()
        self.logger = logging.getLogger(__name__)

    def load_processed_news(self):
        try:
            with open(PROCESSED_NEWS_FILE, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_processed_news(self):
        with open(PROCESSED_NEWS_FILE, 'w') as f:
            json.dump(self.processed_news, f, indent=2)

    def generate_news_id(self, url, title, date):
        """Genera un ID único para cada noticia"""
        content = f"{url}{title}{date}".encode('utf-8')
        return hashlib.md5(content).hexdigest()

    def extract_keywords(self, article, entry):
        """Extrae palabras clave de la noticia"""
        keywords = set()
        
        # Extraer keywords del feed RSS
        possible_keyword_fields = ['category', 'tags', 'keywords']
        for field in possible_keyword_fields:
            if hasattr(entry, field):
                kw = getattr(entry, field)
                if isinstance(kw, list):
                    keywords.update(kw)
                elif isinstance(kw, str):
                    keywords.update(kw.split(','))

        # Extraer keywords del artículo usando newspaper3k
        if article.keywords:
            keywords.update(article.keywords)

        return list(keywords)

    def process_news(self, url, entry):
        news_id = self.generate_news_id(url, entry['title'], entry.get('published', ''))
        
        if news_id in self.processed_news:
            print(f"Noticia ya procesada: {entry['title']}")
            return False

        try:
            article = Article(url, language='es')
            article.download()
            article.parse()
            article.nlp()  # Esto extrae keywords y resumen

            # Generar nombre corto para el archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            short_name = f"{timestamp}_{news_id[:8]}"
            
            # Guardar contenido
            domain_directory = get_output_directory(url)
            text_path = os.path.join(domain_directory, f"{short_name}.txt")
            keywords_path = os.path.join(domain_directory, f"{short_name}_keywords.txt")

            # Extraer keywords
            keywords = self.extract_keywords(article, entry)

            # Guardar contenido principal
            content = f"""Título: {entry['title']}
Fecha: {entry.get('published', '')}
URL: {url}
Autor: {entry.get('author', '')}

Resumen:
{article.summary}

Contenido:
{article.text}
"""                
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # Guardar keywords
            with open(keywords_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(keywords))

            # Registrar como procesada
            self.processed_news[news_id] = {
                'title': entry['title'],
                'url': url,
                'date': entry.get('published', ''),
                'processed_date': datetime.now().isoformat(),
                'file_path': text_path
            }
            
            processed_successfully = True

            if processed_successfully:
                # Enviar la noticia por todos los canales configurados
                news_data = {
                    'title': entry['title'],
                    'url': url,
                    'summary': article.summary,
                    'content': article.text,
                    'keywords': keywords
                }
                self.news_sender.send_all(news_data)
                
            return processed_successfully

        except Exception as e:
            self.logger.error(f"Error procesando noticia: {e}")
            return False

def main_loop():
    processor = NewsProcessor()
    logger = logging.getLogger(__name__)
    
    while True:
        try:
            start_time = datetime.now()
            logger.info("Iniciando ciclo de revisión de feeds...")
            
            for rss_url in RSS_FEEDS:
                try:
                    feed = feedparser.parse(rss_url)
                    for entry in feed.entries:
                        processed_entry = process_feed_entry(entry)
                        processor.process_news(processed_entry['link'], processed_entry)
                except Exception as e:
                    logger.error(f"Error procesando feed {rss_url}: {e}")
                    continue
            
            processor.save_processed_news()
            
            # Calcular tiempo hasta próxima ejecución
            elapsed_time = (datetime.now() - start_time).seconds
            sleep_time = max(CHECK_INTERVAL - elapsed_time, 0)
            logger.info(f"Ciclo completado. Esperando {sleep_time} segundos...")
            time.sleep(sleep_time)
            
        except Exception as e:
            logger.error(f"Error en el ciclo principal: {e}")
            time.sleep(RETRY_INTERVAL)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        logger.info("Programa terminado por el usuario")
    finally:
        driver.quit()
