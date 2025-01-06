import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from config import *
import time
from collections import deque
from datetime import datetime, timedelta

class NewsSender:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.message_queue = deque()
        self.last_sent_time = datetime.now()
        self.sent_messages_count = 0
        self.message_timestamps = []

    def _reset_rate_limit(self):
        """Resetea el contador de mensajes cada minuto"""
        now = datetime.now()
        self.message_timestamps = [ts for ts in self.message_timestamps 
                                 if now - ts < timedelta(minutes=1)]
        
    def _can_send_message(self):
        """Verifica si podemos enviar un nuevo mensaje según el rate limit"""
        self._reset_rate_limit()
        return len(self.message_timestamps) < TELEGRAM_RATE_LIMIT

    def send_telegram(self, news):
        try:
            # Esperar si es necesario debido al rate limiting
            while not self._can_send_message():
                self.logger.info("Rate limit alcanzado, esperando...")
                time.sleep(TELEGRAM_DELAY)

            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            message = f"📰 {news['title']}\n\n{news.get('summary', '')}\n\n🔗 {news['url']}"
            data = {
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            # Registrar el envío del mensaje
            self.message_timestamps.append(datetime.now())
            time.sleep(TELEGRAM_DELAY)  # Esperar entre mensajes
            
            self.logger.info(f"Noticia enviada a Telegram: {news['title']}")
            
            # Si hemos enviado un lote completo, hacer una pausa más larga
            if len(self.message_timestamps) % MESSAGE_BATCH_SIZE == 0:
                self.logger.info(f"Pausa de lote, esperando {BATCH_DELAY} segundos...")
                time.sleep(BATCH_DELAY)
                
        except Exception as e:
            self.logger.error(f"Error enviando a Telegram: {e}")
            if "429" in str(e):  # Too Many Requests
                self.logger.warning("Rate limit excedido, esperando 5 minutos...")
                time.sleep(300)  # Esperar 5 minutos si se excede el rate limit

    def send_email(self, news):
        try:
            msg = MIMEMultipart()
            msg['From'] = EMAIL_SENDER
            msg['To'] = ", ".join(EMAIL_RECIPIENTS)
            msg['Subject'] = f"Nueva Noticia: {news['title']}"

            body = f"""
            <h2>{news['title']}</h2>
            <p>{news.get('summary', '')}</p>
            <p><a href="{news['url']}">Leer más</a></p>
            """
            msg.attach(MIMEText(body, 'html'))

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                server.send_message(msg)
            
            self.logger.info(f"Noticia enviada por email: {news['title']}")
        except Exception as e:
            self.logger.error(f"Error enviando email: {e}")

    def send_all(self, news):
        """Envía la noticia por todos los canales disponibles"""
        try:
            self.send_telegram(news)
            self.send_email(news)
        except Exception as e:
            self.logger.error(f"Error en send_all: {e}")
