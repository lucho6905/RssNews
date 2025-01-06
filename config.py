import os
import logging

# Rutas
BASE_DIR = 'C:/Users/lucho/Downloads/NOTICIAS/Rss'
PROCESSED_NEWS_FILE = os.path.join(BASE_DIR, 'processed_news.json')
BRAVE_PATH = 'C:/Program Files/BraveSoftware/Brave-Browser/Application/Brave.exe'
DRIVER_PATH = 'C:/Program Files/BraveSoftware/Brave-Browser/Application/chromedriver.exe'

# Configuración NLTK
NLTK_DATA_PATH = os.path.join(os.path.expanduser('~'), 'nltk_data')
if not os.path.exists(NLTK_DATA_PATH):
    os.makedirs(NLTK_DATA_PATH)

# Configuración de logging
LOG_FILE = os.path.join(BASE_DIR, 'rss_news.log')

# Crear el directorio para logs si no existe
log_dir = os.path.dirname(LOG_FILE)
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Configurar el logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Crear los handlers
file_handler = logging.FileHandler(LOG_FILE)
console_handler = logging.StreamHandler()

# Crear el formato
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Agregar los handlers al logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Configuración de extracción
MAX_FILENAME_LENGTH = 50
SLEEP_TIME = 1

# Configuración del navegador
BROWSER_TIMEOUT = 30
BROWSER_PAGE_LOAD_TIMEOUT = 30
BROWSER_IMPLICIT_WAIT = 10

# Intervalos de ejecución
CHECK_INTERVAL = 300  # 5 minutos
RETRY_INTERVAL = 60  # 1 minuto en caso de error

# Configuración de notificaciones
TELEGRAM_TOKEN = 'your telegram token'
TELEGRAM_CHAT_ID = 'your chat ID'
EMAIL_SENDER = 'your_email@example.com'
EMAIL_PASSWORD = 'your_app_password'
EMAIL_RECIPIENTS = ['recipient1@example.com', 'recipient2@example.com']
WHATSAPP_NUMBER = 'your_whatsapp_number'

# Configuración de rate limiting
TELEGRAM_RATE_LIMIT = 30  # Máximo número de mensajes por minuto
TELEGRAM_DELAY = 2  # Segundos entre mensajes
MESSAGE_BATCH_SIZE = 5  # Número de mensajes a enviar en cada lote
BATCH_DELAY = 60  # Segundos de espera entre lotes
