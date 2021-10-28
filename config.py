import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent

if os.environ.get('ENV') == 'test':
    LOGGING_LEVEL = "DEBUG"
    filepath = os.path.join(BASE_DIR, ".env.test")
else:
    LOGGING_LEVEL = "INFO"
    filepath = os.path.join(BASE_DIR, ".env")

load_dotenv(filepath)

API_KEY = os.environ.get('API_KEY')
API_SECRET = os.environ.get('API_SECRET')
API_PASSPHRASE = os.environ.get('API_PASSPHRASE')

REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')

MAIL_ADDRESS = os.environ.get('MAIL_ADDRESS')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
