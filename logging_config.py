import logging, os
from logging.handlers import RotatingFileHandler

def configure_logging():
    os.makedirs('logs', exist_ok=True)
    logging.basicConfig(level=os.getenv('LOG_LEVEL','INFO').upper(),
      format='%(asctime)s %(levelname)s %(name)s: %(message)s',
      handlers=[logging.StreamHandler(),RotatingFileHandler('logs/stm.log',maxBytes=2_000_000,backupCount=3,encoding='utf-8')])
